#!/usr/bin/python
"""Usage: python client.py <name> <email>"""
import socket
import config
import time
import sys
import os


class Client:
    def __init__(self, cfg):
        conn = cfg['connection']
        self._address = (conn['address'], conn['port'])
        self._socket = None
        self._message_size = cfg['message']['size']

    def run(self):
        try:
            self._open_socket()
            self._socket.connect(self._address)
            while True:
                response = self._request()
                self._process_response(response)
        except socket.error as (value, message):
            print('Error {}: {}'.format(value, message))
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
        line = '[{}] {}\n'.format(os.getpid(), time.ctime(time.time()))
        self._socket.send(line)
        return self._socket.recv(self._message_size)

    @staticmethod
    def _process_response(response):
        sys.stdout.write(response)
        time.sleep(1)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    conf = config.load()
    client = Client(conf)
    client.run()
