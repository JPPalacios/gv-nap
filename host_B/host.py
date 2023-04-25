#!/usr/bin/python

import os
import sys
import time
from socket    import *
from threading import *

sys.path.append("..")

from utils.tools import *

class Host:
    def __init__(self, name = 'A', ip = 'localhost', server_port = 3155, client_port = 3156):
        self.name = name
        self.ip   = ip

        self.server_connections = {}

        ''' central-server socket initialization '''
        self.central_socket = socket(AF_INET, SOCK_STREAM)

        ''' server-side socket initialization '''
        self.server_port   = server_port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.server_port))
        self.server_socket.listen(5)
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.start()
        # self.server_thread.join()

        ''' client-side socket initialization '''
        self.client_port   = client_port
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_thread = Thread(target = self.run_client)
        self.client_thread.start()
        # self.client_thread.join()

    # server-side methods

    def run_server(self):
        log(f'host listening on {self.ip}:{self.server_port}...')
        while True:
            connection, address = self.server_socket.accept()
            self.server_connections[address] = connection
            connection_thread = Thread(target = self.handle_client, args = (connection, address))
            connection_thread.start()

    def handle_client(self, connection, address):
        while True:
            message = self.read_message(connection)
            if not message:
                del self.server_connections[address]
                break

            elif message.startswith('RETR'):
                parts = message.split(" ")
                if len(parts) == 2:
                    filename = parts[1]
                    log(f'RETR command in-progress...')
                    self.send_message(connection, filename)
                    self.send_file(connection, filename)

            elif message.startswith('QUIT'):
                log(f'removing {address} from host-server connections...')
                del self.server_connections[address]
                break
        connection.close()

    # client-side methods

    def run_client(self):
        log(f'running client on {self.ip}:{self.client_port}...')
        server_registration_set = False
        host_connection_set = False

        debug_command = 0
        central_server_connection = None

        while True:
            # command = self.get_command()

            if debug_command == 0:
                debug_command = 1
                command = 'CONNECT 127.0.0.0:3154'
            else:
                command = input('> enter a client command: ')

            if not server_registration_set:
                if command.startswith("CONNECT"):
                    parts = command.split(" ")
                    if len(parts) == 2:
                        host, port = parts[1].split(":")
                        self.central_socket.connect((host, int(port)))
                        central_server_connection = (host, int(port))
                        log(f'connected to central-server at {host}:{port}')
                        shared_files = 'host_' + self.name + '.txt'
                        registration_message = f'{self.ip}:{self.client_port} {shared_files}'
                        self.send_message(self.central_socket, registration_message)
                        server_registration_set = True

                elif command.startswith("QUIT"):
                    break
                else:
                    log('error: no connection to central server')
            else:
                if command.startswith("CONNECT") and not host_connection_set:
                    host_connection_set = True
                    parts = command.split(" ")
                    if len(parts) == 2:
                        host, port = parts[1].split(":")
                        self.client_socket.connect((host, int(port)))
                        log(f'connected to host at {host}:{port}')
                elif command.startswith("QUER"):
                    parts = command.split(" ")
                    if len(parts) == 2:
                        keyword = parts[1]
                    self.send_message(self.central_socket, command)

                    keyword_host = self.read_message(self.central_socket)

                    log(f'{keyword} found in {keyword_host}')

                elif command.startswith("RETR") and host_connection_set:
                    message = self.read_message(self.client_socket)
                    log(f'received message from host: {message}')
                    self.receive_file(self.client_socket, message)

                elif command.startswith('QUIT'):
                    parts = command.split(" ")
                    if len(parts) == 2:
                        host, port = parts[1].split(":")
                        if (host, int(port)) == central_server_connection:
                            self.send_message(self.central_socket, parts[0])
                            break
                        else:
                            self.send_message(self.client_socket, parts[0])
                            self.client_socket.close()
                            host_connection_set = False
                    break
        self.central_socket.close()

    def get_command(self):
        # if debug_command == 0:
        #     debug_command = 1
        #     return 'CONNECT 127.0.0.0:3154'
        # else:
        return input('> enter a client command: ')

    # shared methods

    def send_message(self, connection, message):
        connection.sendall(message.encode('utf-8'))

    def read_message(self, connection):
        return connection.recv(1024).decode('utf-8')

    def receive_file(self, connection, filename):
        with open(filename, 'wb') as file:
            while True:
                data = self.read_message(connection)
                if not data:
                    break
                file.write(data)

    def send_file(self, connection, filename):
        with open(filename, 'rb') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                self.send_message(connection, data)

def main():
    host1 = Host('B', '127.0.0.2', 8001, 9001)

if __name__ == '__main__':
    main()
