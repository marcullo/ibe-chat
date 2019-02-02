#!/usr/bin/python3.6
"""Usage:
`python database.py dump <type>` - read data selected by type,
`python database.py clean <type>` - clean data selected by type.
`python database.py gen_entry <type>` - generate entry selected by type.

<type>:
    `msg_db` - message database.

E.g. `python database.py dump msg_db`"""
import tinydb
from tinydb import where
import message
import json
import threading
import sys
import time


class Database:
    def __init__(self, msg_path):
        self._db = tinydb.TinyDB(msg_path)
        self._msg_lock = threading.Lock()

    def insert_message(self, msg):
        self._msg_lock.acquire()
        try:
            self._db.insert(msg.content)
        finally:
            self._msg_lock.release()

    def select_messages(self, sender=None, recipient=None):
        self._msg_lock.acquire()
        try:
            if sender is None and recipient is None:
                entries = self._db.all()
            elif sender is None:
                entries = self._db.search(where('recipient') == recipient)
            elif recipient is None:
                entries = self._db.search(where('sender') == sender)
            else:
                entries = self._db.search((where('recipient') == recipient) &
                                          (where('sender') == sender))
        finally:
            self._msg_lock.release()

        return [message.Message.create(json.dumps(dict(e))) for e in entries]

    def clean_messages(self):
        self._msg_lock.acquire()
        self._db.purge()
        self._msg_lock.release()


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

    db_paths = {
        'msg_db': '.db/messages.json'  # message database
    }

    commands = {
        'dump': dump_msg_db,
        'clean': clean_msg_db,
        'gen_entry': gen_entry_msg_db
    }

    command = sys.argv[1]
    arg = sys.argv[2]
    if command not in commands or arg not in db_paths:
        print(__doc__)
        sys.exit(1)

    path = db_paths[arg]
    ndb = Database(path)
    commands[command](ndb)
