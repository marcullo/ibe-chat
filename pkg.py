#!/usr/bin/python3.6
"""Usage:
`python pkg.py register <name> <email>` - register client
`python pkg.py get_pubkey <name> <email>` - get public key assigned to client
`python pkg.py get_privkey <name> <email>` - get private key assigned to client (should be made by owner!)
`python pkg.py clean clients content` - clean the whole content related with clients

E.g. `python register Bob bob@example.com`"""
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA3_256
import os
import re
import sys
import database
import config
import identity
import json


class PrivateKeyGenerator:
    def __init__(self, db, k_folder, key_len):
        self._db = db
        self._key_folder = k_folder
        self._key_len = key_len

    def register(self, identifier):
        identifier_hash = self._hash(str(identifier))
        private_key_file = '{}/.{}'.format(self._key_folder, identifier_hash)
        public_key_file = '{}/{}.pub'.format(self._key_folder, identifier_hash)
        if os.path.exists(private_key_file) or os.path.exists(public_key_file):
            return

        print('Registering {}'.format(identifier))

        key = RSA.generate(self._key_len)
        private_key = key.export_key()
        with open(private_key_file, 'wb') as f:
            f.write(private_key)
        public_key = key.publickey().export_key()
        with open(public_key_file, 'wb') as f:
            f.write(public_key)

        self._db.insert_client(identifier, identifier_hash)

    def get_public_key(self, identifier):
        if identifier is None:
            raise ValueError
        self.register(identifier)
        pubkey_file = self._get_public_key_file(identifier)
        with open('{}/{}'.format(self._key_folder, pubkey_file)) as f:
            return f.read()

    """Caution: It should be implemented in other (local) way to provide secure operations.
Right now get_private_key reveals the whole secret of user without authenticating
(but it's not a part of IBE)!"""
    def _get_private_key(self, identifier):
        if identifier is None:
            raise ValueError
        self.register(identifier)
        privkey_file = self._get_private_key_file(identifier)
        with open('{}/{}'.format(self._key_folder, privkey_file)) as f:
            return f.read()

    def clean_keys(self):
        for f in os.listdir(self._key_folder):
            # private keys
            if re.search('^.[0-9a-fA-F]{64}$', f):
                os.remove(os.path.join(self._key_folder, f))
            # public keys
            if re.search('^[0-9a-fA-F]{64}.pub$', f):
                os.remove(os.path.join(self._key_folder, f))

    def _get_public_key_file(self, identifier):
        client_content = self._db.select_client(str(identifier))[0]
        return json.loads(client_content)['pubkey_file']

    def _get_private_key_file(self, identifier):
        client_content = self._db.select_client(str(identifier))[0]
        return json.loads(client_content)['privkey_file']

    @staticmethod
    def _hash(text):
        h = SHA3_256.new()
        h.update(text.encode())
        return h.hexdigest()

    @staticmethod
    def create():
        conf = config.load()
        folder = conf['database']['folder']
        key_len = conf['client']['key_len']
        ndb = database.Database.create()
        return PrivateKeyGenerator(ndb, folder, key_len)


if __name__ == "__main__":
    if len(sys.argv) is not 4:
        print(__doc__)
        sys.exit(1)

    def register_client(pkg, i):
        pkg.register(i)

    def get_public_key_user(pkg, i):
        print(pkg.get_public_key(i))

    def get_private_key_user(pkg, i):
        print(pkg._get_private_key(i))

    def clean_clients_content(pkg, _):
        pkg.clean_keys()
        pkg._db.clean_clients()

    commands = {
        'register': register_client,
        'get_pubkey': get_public_key_user,
        'get_privkey': get_private_key_user,
        'clean': clean_clients_content
    }

    command = sys.argv[1]
    if command not in commands:
        print(__doc__)
        sys.exit(1)
    if command == 'clean' and (sys.argv[2] != 'clients' or sys.argv[3] != 'content'):
        print(__doc__)
        sys.exit(1)

    identity = identity.Identity(sys.argv[2], sys.argv[3])
    keygen = PrivateKeyGenerator.create()
    commands[command](keygen, identity)
