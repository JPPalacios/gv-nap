#!/usr/bin/python

import os
import sys
import time
import socket
from threading import *

sys.path.append("..")

from utils.tools import *

class Host:
    def __init__(self, name = 'a', ip = 'localhost', server_port = 3155, client_port = 3156):
        self.name = name
        self.ip   = ip

        self.server_connections = {}

        ''' central-server socket initialization '''
        self.central_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        ''' server-side socket initialization '''
        self.server_port   = server_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.server_port))
        self.server_socket.listen(5)
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.start()
        # self.server_thread.join()

        ''' client-side socket initialization '''
        self.client_port   = client_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        log(f'new host connection: {address}')
        while True:
            message = self.read_message(connection)
            if not message:
                del self.server_connections[address]
                break

            log(f'host message: {message}')
            if message.startswith('RETR'):
                parts = message.split(" ")
                if len(parts) == 2:
                    filename = parts[1]
                    log(f'RETR {filename} command in-progress...')
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
            # elif debug_command == 1:
                # command = 'QUER book'
            else:
                # debug_command = debug_command + 1
                command = input('> enter a client command: ')

            if not server_registration_set:
                if command.startswith("CONNECT"):
                    parts = command.split(" ")
                    if len(parts) == 2:
                        host, port = parts[1].split(":")
                        self.central_socket.connect((host, int(port)))
                        central_server_connection = (host, int(port))
                        log(f'connected to central-server at {host}:{port}')
                        shared_files =  self.name + '.txt'
                        registration_message = f'{self.ip}:{self.server_port} {shared_files}'
                        self.send_message(self.central_socket, registration_message)
                        server_registration_set = True

                elif command.startswith("QUIT"):
                    break
                else:
                    log('error: no connection to central server')
            else:
                if command.startswith("CONNECT") and not host_connection_set:
                    parts = command.split(" ")
                    if len(parts) == 2:
                        host, port = parts[1].split(":")
                        self.client_socket.connect((host, int(port)))
                        log(f'connected to host at {host}:{port}')
                        host_connection_set = True
                elif command.startswith("QUER"):
                    parts = command.split(" ")
                    if len(parts) == 2:
                        keyword = parts[1]
                    self.send_message(self.central_socket, command)

                    keyword_host = self.read_message(self.central_socket)

                    if keyword_host == ' ':
                        log(f'\'{keyword}\' not found in any host')
                    else:
                        log(f'\'{keyword}\' found in {keyword_host}')
                        new_parts = keyword_host.split(" ")
                        if len(new_parts) == 2:
                            host_filename = parts[1]

                elif command.startswith("RETR") and host_connection_set:
                    parts = command.split(" ")
                    if len(parts) == 2:
                        filename = parts[1]
                        log(f'waiting for file {filename}...')
                        self.send_message(self.client_socket, command)
                        self.receive_file(self.client_socket, filename)

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
        return input('> enter a client command: ')

    # shared methods

    def send_message(self, connection, message):
        connection.sendall(message.encode('utf-8'))

    def read_message(self, connection):
        return connection.recv(1024).decode('utf-8')

    def receive_file(self, connection, filename):
        with open(filename, 'w') as file:
            data = self.read_message(connection)
            file.write(data)
        log(f'file received.')

    def send_file(self, connection, filename):
        with open(filename, 'r') as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                self.send_message(connection, data)
        log(f'file sent.')

def main():
    host1 = Host('a', '127.0.0.1', 8000, 9000)

if __name__ == '__main__':
    main()
