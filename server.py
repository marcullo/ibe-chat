#!/usr/bin/python
import config
import socket
import threading


class Server:
    def __init__(self, connection):
        self._address = ('', connection['port'])
        self._backlog = 5
        self._socket = None
        self._clients = []
        self._clients_timer = threading.Timer(0.1, self._inform_about_waiting_for_clients)

    def run(self):
        try:
            self._open_socket()
            running = True
            while running:
                client, address = self._socket.accept()
                c = Client(client, address)
                c.start()
                self._clients.append(c)
        except socket.error as (value, message):
            print('Error {}: {}'.format(value, message))
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

    def _close_socket(self):
        if self._socket:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()

    def _inform_about_waiting_for_clients(self):
        print('Waiting for client(s)...')
        self._clients_timer.cancel()


class Client(threading.Thread):
    def __init__(self, client, address):
        threading.Thread.__init__(self)
        self.client = client
        self._address = address

    def run(self):
        running = True
        try:
            while running:
                request = self._receive_request()
                if request:
                    self._process_request(request)
                else:
                    self.client.close()
                    running = False
        except socket.error as (value, message):
            if value is not 104:
                print('Error {}: {}'.format(value, message))
        except (KeyboardInterrupt, SystemExit):
            pass
        finally:
            if self.client:
                self.client.close()

    def _receive_request(self):
        return self.client.recv(256)

    def _process_request(self, data):
        self.client.send(data)


if __name__ == "__main__":
    cfg = config.load()
    server = Server(cfg['connection'])
    server.run()
