#!/usr/bin/python
import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 8765))
s.listen(5)

try:
    while True:
        client, addr = s.accept()
        print('{} connected.'.format(addr))
        client.send(time.ctime(time.time()))
        client.close()
except (KeyboardInterrupt, SystemExit):
    pass

s.shutdown(socket.SHUT_RDWR)
s.close()
