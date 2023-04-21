
import os
import sys

from socket import *

from tools.tools import *

class Client:

    def __init__(self, host = '127.0.0.1', port = 3155):
        self.host = host
        self.port = port
        self.control_socket = socket(AF_INET, SOCK_STREAM)
        self.data_socket    = None
        self.cwd = os.getcwd()
        self.connect()

    def connect(self):
        try:
            self.control_socket.connect((self.host, self.port))
            log(f'connection established')
        except Exception as e:
            error(f'connection error: {e}')

    def send_request(self, command):
        self.control_socket.sendall(f'{command}{SEND_MESSAGE_END}'.encode('utf-8'))

    def read_response(self) -> str:
        response = ''
        # self.control_socket.settimeout(5)  # set a timeout of 5 seconds
        while True:
            try:
                data = self.control_socket.recv(1024).decode('utf-8')
                response += data
                if response.endswith(READ_MESSAGE_END):
                    break
            except timeout:
                error('time out waiting for response from server')
                break
        return response.strip()

    def quit(self):
        self.send_request('QUIT')
        self.control_socket.close()

def main():
    client = Client()

    while True:
        command = input('Enter a command: ')

        client.send_request(command)

        if command.startswith('QUIT'):
            break
        # response = client.read_response()

        # log(response)


if __name__ == "__main__":
    main()