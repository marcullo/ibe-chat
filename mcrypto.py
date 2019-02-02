from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import pkg
import identity
import base64
import json


def encrypt(message, target_pubkey):
    target_pubkey = RSA.import_key(target_pubkey)
    session_key = get_random_bytes(16)

    cipher_rsa = PKCS1_OAEP.new(target_pubkey)
    enc_session_key = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(message.encode('utf-8'))
    nonce = cipher_aes.nonce

    return json.dumps({
        'enc_session_key': base64.b64encode(enc_session_key).decode('utf-8'),
        'nonce': base64.b64encode(nonce).decode('utf-8'),
        'tag': base64.b64encode(tag).decode('utf-8'),
        'ciphertext': base64.b64encode(ciphertext).decode('utf-8')
    })


def decrypt(content_raw, privkey):
    privkey = RSA.import_key(privkey)
    content = json.loads(content_raw)
    enc_session_key = base64.b64decode(content['enc_session_key'].encode('utf-8'))
    nonce = base64.b64decode(content['nonce'].encode('utf-8'))
    tag = base64.b64decode(content['tag'].encode('utf-8'))
    ciphertext = base64.b64decode(content['ciphertext'].encode('utf-8'))

    cipher_rsa = PKCS1_OAEP.new(privkey)
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    message = cipher_aes.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    return message


if __name__ == "__main__":
    keygen = pkg.PrivateKeyGenerator.create()
    idr = identity.Identity('Bob', 'bob@example.com')
    pubk = keygen.get_public_key(idr)
    privk = keygen._get_private_key(idr)
    msg = 'Hello, world!'
    print('***** Encrypting `{}` for {}:'.format(msg, idr))
    res = encrypt(msg, pubk)
    print(res)
    print('***** Decrypted: `{}`'.format(decrypt(res, privk)))
