#!/usr/bin/python
from os        import *
from sys       import *
from time      import *
from socket    import *
from threading import *

path.append("..")

from utils.tools import *

class Host:
    def __init__(self, ip = 'localhost', server_port = 3155, client_port = 3156):
        self.ip   = ip

        self.server_connections = {}

        ''' server-side initialization '''
        self.server_port   = server_port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.server_port))
        self.server_socket.listen(5)
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.start()

        ''' client-side initialization '''
        self.client_port   = client_port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_thread = Thread(target = self.run_client)
        self.client_thread.start()

    # server-side methods

    def run_server(self):
        log(f'listening on {self.ip}:{self.server_port}...')
        while True:
            connection, address = self.server_socket.accept()
            self.server_connections[address] = connection
            client_thread = Thread(target = self.handle_client, args = (connection, address))
            client_thread.start()

    def handle_client(self, connection, address):
        while True:
            message = connection.recv(1024).decode('utf-8')
            if not message:
                del self.server_connections[address]
                break

            if message.startswith('RETR'):
                parts = message.split(" ")
                if len(parts) == 2:
                    filename = parts[1]
                    log(f'RETR command in-progress...')
                    self.send_message(connection, filename + SEND_MESSAGE_END)

                    self.read_file(connection, filename)

            elif message.startswith('QUIT'):
                log(f'removing {address} from host-server connections...')
                del self.server_connections[address]
                break
        connection.close()

    # client-side methods

    def run_client(self):
        log(f'running client on {self.ip}:{self.client_port}...')
        connection_set = False

        while True:
            command = input('> enter a client command: ')

            if command.startswith("CONNECT") and not connection_set:
                connection_set = True
                parts = command.split(" ")
                if len(parts) == 2:
                    host, port = parts[1].split(":")
                    self.client_socket.connect((host, int(port)))
                    log(f'connected to {host}:{port}')

            else:
                if connection_set:
                    self.send_message(self.client_socket, command + SEND_MESSAGE_END)

                    if command.startswith("RETR"):
                        message = self.read_message(self.client_socket)
                        log(f'received message from server: {message}')

                        self.write_file(self.client_socket, message)

                    elif command.startswith('QUIT'):
                        self.client_socket.close()
                        connection_set = False
                else:
                    log(f'error: no connections available!')

    # shared methods

    def send_message(self, connection, message):
        connection.sendall(message.encode('utf-8'))

    def read_message(self, connection):
        return connection.recv(1024).decode('utf-8')

    #! str cannot be interpreted as an integer error
    def write_file(self, connection, filename):
        with open('filename.txt', 'wb') as file:
            while True:
                data = self.read_message(connection)
                if not data:
                    break
                file.write(data)

    #! str cannot be interpreted as an integer error
    def read_file(self, connection, filename):
        with open('filename.txt', 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                self.send_message(connection, data)

def main():
    host1 = Host('127.0.0.1', 8000, 9000)

if __name__ == '__main__':
    main()
