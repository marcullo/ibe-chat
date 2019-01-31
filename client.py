#!/usr/bin/python
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8765))
stime = s.recv(64)
s.close()
print('Server time: {}'.format(stime))
