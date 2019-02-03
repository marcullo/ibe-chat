# Identity-Based Encrypted Chat

> **Note**: The following solution is a description of context and cannot be used in a real secure application.

This is a simple hot-seat, client-server chat which provides the message encryption based on user identity (name and email). The server has a role of Key Authority. It also responds for clients requests which concerns messages and key generation. The communication is blocking, but a *server* provides multiple threads for processing requests made by *clients*.

- [Abstract](abstract/README.md)

## Requirements

- environment: Python 3.6
- libraries: [tinydb](https://tinydb.readthedocs.io/en/latest/), [PyCryptodome](https://pycryptodome.readthedocs.io/en/latest/src/introduction.html)

## Modules

### Config

In *config.json* you can set desired parameters of connection, message, clients and database.

### Database

Run *database.py* without arguments to check supported commands. This is the interface to database operations. For instance, to dump all messages you can simply do:

```python
$ python database.py dump msg_db
```

Database consists of two containers for:

- *messages* - stores information about timestamp, identities of parties and two versions of ciphertexts   based on original message (one encrypted for sender and the other for recipient) to encrypt.
- *clients* - stores identities of parties corresponding names of files which contains generated private and public keys.

### PKG

The hybrid encryption was implemented. RSAES-OAEP for asymmetric encryption of AES EAX (which provided detection of unauthorized modifications).

Key generation produces private and public key in separate files, which names correspond to the *SHA3-256* hash of an identity. Keys can be generated from console (*pkg.py*), but server automatically does that if any of parties of transmission doesn't own its keys.

## How to use

1. Run server: `python server.py`.
2. Run two clients from separate processes, calling like: `python client.py Bob bob@example.com`  for specifying the identity of client.
3. Provide an identity of interlocutor.
4. Chat.

**Note**: If you want to refresh messages list (it doesn't refresh automatically), type *ENTER* or simply send another message.
