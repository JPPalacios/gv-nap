
import os
import sys

from threading import *
from socket import *

from tools.tools import *

class Server:

    def __init__(self, host = '127.0.0.1', port = 3155, buffer = 1024):
        self.host = host
        self.port = port
        self.buffer = buffer
        self.control_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket  = None

        self.client_address = None
        self.data_socket    = None

        self.cwd = os.getcwd()
        self.launch()

    def launch(self):
        self.control_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.control_socket.bind((self.host, self.port))
        self.control_socket.listen(5)
        log(f'server listening on {self.host}:{self.port}...')
        while True:
            self.client_socket, self.client_address = self.control_socket.accept()
            log(f'connection established')
            client_thread = Thread(target = self.handle_client)
            client_thread.start()

    def handle_client(self):
        log(f'handle_client thread running...')

        while True:
            request = self.read_request(self.client_socket)

            if not request:
                break
            log(f'received \'{request}\' from client...')

            if request.startswith('RETR'):
                log('checkpoint reached!')
            elif request.startswith('QUIT'):
                self.send_response(self.client_socket, 'closing down connection')
                break
            else:
                log('command not implemented')

        self.client_socket.close()

    def read_request(self, client_socket : socket) -> str:
        request = ''
        while True:
            data = client_socket.recv(self.buffer).decode('utf-8')
            request += data
            if request.endswith(SEND_MESSAGE_END):
                break
        return request.strip()

    def send_response(self, client_socket, message):
        client_socket.send(f'{message}{READ_MESSAGE_END}'.encode('utf-8'))

def main():
    server = Server()

if __name__ == "__main__":
    main()