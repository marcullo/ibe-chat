#!/usr/bin/python3.6
"""Usage: python client.py <name> <email>"""
import socket
import config
import sys
import identity
import message
import request
from request import RequestType
import json
import time
import mcrypto


class Client:
    def __init__(self, cfg, identifier):
        conn = cfg['connection']
        self._address = (conn['address'], conn['port'])
        self._socket = None
        self._msg_size = cfg['message']['size']
        self._id = identifier
        self._privkey = None
        self._target_pubkey = None

    def send(self, text, target, wait_for_response=False):
        try:
            if self._target_pubkey is None:
                raise RuntimeError('Target public key not obtained before!')
            text = mcrypto.encrypt(text, self._target_pubkey)
            msg = message.Message(self._id, target, text)
            req = request.Request(RequestType.SEND_MSG, msg)
            self._open_socket()
            self._socket.connect(self._address)
            self._socket.send(str(req).encode())
            if wait_for_response:
                return self.get_response()
            else:
                return None
        except socket.error as err:
            print('Error {}: {}'.format(err.errno, err.strerror))
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self._close_socket()

    def get_response(self):
        return self._socket.recv(self._msg_size).decode()

    def get_conversation(self, target_id):
        try:
            self._open_socket()
            self._socket.connect(self._address)

            content = {
                'requester': str(self._id),
            }

            if self._privkey is None:
                req = request.Request(RequestType.RECEIVE_PRIVKEY, json.dumps(content))
                self._socket.send(str(req).encode())
                self._privkey = self.get_response()

            content['interlocutor'] = str(target_id)

            if self._target_pubkey is None:
                req = request.Request(RequestType.RECEIVE_PUBKEY, json.dumps(content))
                self._socket.send(str(req).encode())
                self._target_pubkey = self.get_response()

            req = request.Request(RequestType.RECEIVE_MSGS, json.dumps(content))
            self._socket.send(str(req).encode())
            return self.get_response()
        except socket.error as err:
            print('Error {}: {}'.format(err.errno, err.strerror))
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            self._close_socket()

    def _open_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def _close_socket(self):
        if self._socket:
            self._socket.close()

    @property
    def id(self):
        return self._id


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    def get_target_id(prompt):
        target_name = ''
        while target_name == '':
            sys.stdout.write('{} name: '.format(prompt))
            sys.stdout.flush()
            target_name = sys.stdin.readline().strip()

        target_email = ''
        while target_email == '':
            sys.stdout.write('{} email: '.format(prompt))
            sys.stdout.flush()
            target_email = sys.stdin.readline().strip()

        return identity.Identity(target_name, target_email)

    def get_message(prompt, forced=True):
        msg = ''
        while msg == '':
            sys.stdout.write('{}: '.format(prompt))
            sys.stdout.flush()
            msg = sys.stdin.readline().strip()
            if forced and msg == '':
                continue
            return msg

    def get_conversation(client, target_id):
        conversation_raw = client.get_conversation(target_id)
        if conversation_raw is None or conversation_raw == '':
            return
        conversation = sorted(json.loads(conversation_raw), key=lambda c: c['timestamp'], reverse=False)
        for m in conversation:
            current_time = time.ctime(m['timestamp'])
            sender = identity.Identity.create(m['sender'])
            content = m['message']
            print('{} {:>15}: {}'.format(current_time, sender.name if sender.name != client.id.name else 'Me', content))

    def chat(client):
        target_id = get_target_id('Interlocutor')
        while True:
            get_conversation(client, target_id)
            msg = get_message('$', False)
            if msg == '':
                continue
            client.send(msg, target_id, True)

    cid = identity.Identity(sys.argv[1], sys.argv[2])
    conf = config.load()
    c = Client(conf, cid)

    while True:
        try:
            chat(c)
        except (KeyboardInterrupt, SystemExit):
            break
