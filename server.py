#!/usr/bin/python
import os
import sys
import time
from socket    import *
import threading

sys.path.append(".")

from utils.tools import *

class Server:
    def __init__(self, ip = '127.0.0.0', port = 3154):
        self.ip = ip
        self.port = port

        self.server_connections = {}

        ''' central server initialization '''
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.clean_metadata()
        self.run_server()

    def run_server(self):
        log(f'central server listening on {self.ip}:{self.port}...')
        while True:
            connection, address = self.server_socket.accept()
            self.server_connections[address] = connection
            host_thread = threading.Thread(target = self.handle_host, args = (connection, address))
            host_thread.start()

    def handle_host(self, connection, address):
        log(f'handling a host at {address}')
        registration_set = False
        metadata_copy = ''
        while True:
            message = self.read_message(connection)
            if not message:
                break

            if not registration_set:
                metadata_copy = message
                self.add_metadata(message)
                registration_set = True
                log(f'host registration complete.')

            else:
                if message.startswith('QUER'):
                    parts = message.split(" ")
                    if len(parts) == 2:
                        keyword = parts[1]
                        search_results = self.keyword_search(keyword)
                        log(f'sent {search_results} to host')
                        self.send_message(connection, search_results)

                elif message.startswith('QUIT'):
                    self.remove_metadata(metadata_copy)
                    del self.server_connections[address]
                    log(f'closing host connection {address}...')
                    break
        connection.close()

    def send_message(self, connection, message):
        connection.sendall(message.encode('utf-8'))

    def read_message(self, connection):
        return connection.recv(1024).decode('utf-8')

    def clean_metadata(self):
        with open('server.txt', 'w') as file:
            file.write('')

    def add_metadata(self, data):
        with open('server.txt', 'a') as file:
            file.write(data + '\n')

    def remove_metadata(self, metadata):
        with open('server.txt', "r") as file:
            lines = file.readlines()

        # Search for the line number to remove
        line_number = 0
        for i, line in enumerate(lines):
            if line == metadata:
                line_number = i
                break

        # Remove the line from the list
        if line_number is not None:
            del lines[line_number]

        # Open the same file in write mode and write all the remaining lines back to the file
        with open('server.txt', "w") as f:
            f.writelines(lines)

    def keyword_search(self, keyword):
        log(f'server searching for \'{keyword}\'...')

        result = ''

        search_filelist = []
        search_hosts = []
        with open('server.txt', 'r') as file:
            for line in file:
                host, filename = line.strip().split(" ")
                search_hosts.append(host)
                search_filelist.append(filename)

        # walk in our subdirectories and search every filename in our search_filelist
        # for our keyword, if we have a match, set that search_host value to our result
        # for root, dirs, files in os.walk('.'):
        #     for file in files:
        #         if file in search_filelist:
        #             with open(os.path.join(root, file), 'r') as f:
        #                 if keyword in f.read():
        #                     index = search_filelist.index(file)
        #                     result = search_hosts[index] + ' ' + search_filelist[index]
        #                     log(f'found keyword in {search_filelist[index]}!')
        #                     break
        #     if result:
                # break
        log(f'starting os walk')
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file in search_filelist:
                    log(f'searching {os.path.join(root, file)}...')
                    with open(os.path.join(root, file), 'r') as f:
                        contents = f.read()
                        log(f'{len(contents)} bytes read from {file}.')
                        if keyword in contents:
                            index = search_filelist.index(file)
                            result = search_hosts[index] + ' ' + search_filelist[index]
                            log(f'found keyword in {search_filelist[index]}!')
                            break
        log(f'completed os walk')

        return result

def main():
    server = Server()

if __name__ == "__main__":
    main()