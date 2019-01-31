#!/usr/bin/python
import socket
import config

cfg = config.load()
address = (cfg['connection']['address'], cfg['connection']['port'])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(address)
stime = s.recv(64)
s.close()
print('Server time: {}'.format(stime))
