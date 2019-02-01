#!/usr/bin/python3.6
"""Usage: python client.py <name> <email>"""
import socket
import config
import time
import sys
import identity
import message
import request
from request import RequestType


class Client:
    def __init__(self, cfg, identifier):
        conn = cfg['connection']
        self._address = (conn['address'], conn['port'])
        self._socket = None
        self._msg_size = cfg['message']['size']
        self._id = identifier

    def run(self):
        try:
            self._open_socket()
            self._socket.connect(self._address)
            while True:
                response = self._request()
                self._process_response(response)
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

    def _request(self):
        curr_time = time.ctime(time.time())
        self.send('Hey! It\'s {}'.format(curr_time), self._id)
        return self.receive()

    def send(self, text, target):
        msg = message.Message(self._id, target, text)
        req = request.Request(RequestType.SEND_MSG, msg)
        print(req)
        self._socket.send(str(req).encode())

    def receive(self):
        return self._socket.recv(self._msg_size)

    @staticmethod
    def _process_response(response):
        response = response.decode()
        print(response)
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    client_id = identity.Identity(sys.argv[1], sys.argv[2])
    conf = config.load()
    client = Client(conf, client_id)
    client.run()
