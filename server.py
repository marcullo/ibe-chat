#!/usr/bin/python
import config
import socket
import threading
import message
import time
import request
from request import RequestType
import database


class Server:
    def __init__(self, cfg):
        self._address = ('', cfg['connection']['port'])
        self._backlog = 5
        self._socket = None
        self._message_size = cfg['message']['size']
        self._clients = []
        self._clients_timer = threading.Timer(0.1, self._inform_about_waiting_for_clients)
        self._db = database.Database(cfg['message']['database'])

    def run(self):
        try:
            self._open_socket()
            running = True
            while running:
                client, address = self._socket.accept()
                c = Client(client, address, self._message_size, self._db)
                c.start()
                self._clients.append(c)
        except socket.error as (val, msg):
            print('Error {}: {}'.format(val, msg))
        except (KeyboardInterrupt, SystemExit):
            pass

        self._close_socket()
        self._clients_timer.start()
        for c in self._clients:
            c.join()
        self._clients_timer.cancel()

    def _open_socket(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.bind(self._address)
        self._socket.listen(self._backlog)
        print('Listen on {}.'.format(self._address[1]))

    def _close_socket(self):
        if self._socket:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()

    def _inform_about_waiting_for_clients(self):
        print('Waiting for client(s)...')
        self._clients_timer.cancel()


class Client(threading.Thread):
    def __init__(self, client, address, msg_size, db):
        threading.Thread.__init__(self)
        self.client = client
        self._address = address
        self._message_size = msg_size
        self._db = db

    def run(self):
        running = True
        try:
            while running:
                req = self._receive_request()
                if req:
                    self._process_request(req)
                else:
                    self.client.close()
                    running = False
        except socket.error as (value, msg):
            if value is not 104:
                print('Error {}: {}'.format(value, msg))
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            if self.client:
                self.client.close()

    def _receive_request(self):
        return self.client.recv(self._message_size)

    def _process_request(self, data):
        req = request.Request.create(data)
        if req.type == RequestType.SEND_MSG:
            msg = message.Message.create(req.value, time.time())
            print('{} {} {} -> {}'.format(time.ctime(msg.timestamp), req.name, msg.sender, msg.recipient))
            self._db.insert_message(msg)
            self.client.send(data)
        else:
            raise NotImplementedError


if __name__ == "__main__":
    conf = config.load()
    server = Server(conf)
    server.run()
