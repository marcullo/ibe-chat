#!/usr/bin/python3.6
"""Usage:
`python database.py dump <type>` - read data selected by type,
`python database.py clean <type>` - clean data selected by type.
`python database.py gen_entry <type>` - generate entry selected by type.

<type>:
    `msg_db` - message database,
    `client_db` - client database.

E.g. `python database.py dump msg_db`"""
import tinydb
from tinydb import where
import message
import json
import threading
import sys
import time
import config


class Database:
    def __init__(self, database_path, msg_path, client_path):
        self._msg_db = tinydb.TinyDB('{}/{}'.format(database_path, msg_path))
        self._msg_lock = threading.Lock()
        self._client_db = tinydb.TinyDB('{}/{}'.format(database_path, client_path))
        self._client_lock = threading.Lock()

    def insert_message(self, msg):
        self._msg_lock.acquire()
        try:
            self._msg_db.insert(msg.content)
        finally:
            self._msg_lock.release()

    def select_messages(self, sender=None, recipient=None):
        self._msg_lock.acquire()
        try:
            if sender is None and recipient is None:
                entries = self._msg_db.all()
            elif sender is None:
                entries = self._msg_db.search(where('recipient') == recipient)
            elif recipient is None:
                entries = self._msg_db.search(where('sender') == sender)
            else:
                entries = self._msg_db.search((where('recipient') == recipient) &
                                              (where('sender') == sender))
        finally:
            self._msg_lock.release()

        return [message.Message.create(json.dumps(dict(e))) for e in entries]

    def clean_messages(self):
        self._msg_lock.acquire()
        self._msg_db.purge()
        self._msg_lock.release()

    def insert_client(self, identity, identity_hash):
        self._client_lock.acquire()
        try:
            self._client_db.insert({
                'client': str(identity),
                'privkey_file': '.{}'.format(identity_hash),
                'pubkey_file': '{}.pub'.format(identity_hash)
            })
        finally:
            self._client_lock.release()

    def select_client(self, identity=None):
        self._client_lock.acquire()
        try:
            if identity is None:
                entries = self._client_db.all()
            else:
                entries = self._client_db.search(where('client') == identity)
        finally:
            self._client_lock.release()

        if entries is None or len(entries) is 0:
            return []

        return [json.dumps(dict(e)) for e in entries]

    def clean_clients(self):
        self._client_lock.acquire()
        self._client_db.purge()
        self._client_lock.release()

    @staticmethod
    def create():
        conf = config.load()
        folder = conf['database']['folder']
        msg_file = conf['message']['database']
        client_file = conf['client']['database']
        return Database(folder, msg_file, client_file)


if __name__ == "__main__":
    if len(sys.argv) is not 3:
        print(__doc__)
        sys.exit(1)

    def dump_msg_db(db):
        for m in db.select_messages():
            print(m)

    def clean_msg_db(db):
        db.clean_messages()

    def gen_entry_msg_db(db):
        m = message.Message('Gen Sender<gsender@gs.com>',
                            'Gen Recipient<grecipient@gr.com>',
                            'Hello, World!',
                            time.time())
        db.insert_message(m)

    def dump_client_db(db):
        for m in db.select_client():
            print(m)

    def clean_client_db_stub(_):
        print('If you really want to clean a client database, try to use the `pkg.py`.')

    def gen_entry_client_db_stub(_):
        print('If you really want to generate a client entry, try to use the `pkg.py`.')

    commands = {
        'msg_db': {
            'dump': dump_msg_db,
            'clean': clean_msg_db,
            'gen_entry': gen_entry_msg_db
        },
        'client_db': {
            'dump': dump_client_db,
            'clean': clean_client_db_stub,
            'gen_entry': gen_entry_client_db_stub
        }
    }

    arg = sys.argv[2]
    if arg != 'msg_db' and arg != 'client_db':
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    if command not in commands[arg]:
        print(__doc__)
        sys.exit(1)

    ndb = Database.create()
    commands[arg][command](ndb)
