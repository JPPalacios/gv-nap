''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from os        import *
from time      import *
from socket    import *
from threading import *

from tools.tools import *

''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

class Host:
    def __init__(self, ip = 'localhost', server_port = 3155, client_port = 3156):
        self.ip   = ip

        self.in_connections  = {}
        self.out_connections = {}

        ''' server-side initialization '''
        self.server_port   = server_port
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind((self.ip, self.server_port))
        self.server_socket.listen(5)
        self.server_thread = Thread(target=self.run_server)
        self.server_thread.start()

        ''' client-side initialization '''
        if client_port:
            self.client_port   = client_port
            self.client_socket = socket(AF_INET, SOCK_STREAM)
            self.client_thread = Thread(target = self.run_client)
            self.client_thread.start()

    ''' server-side methods '''

    def run_server(self):
        log(f'listening on {self.ip}:{self.server_port}...')

        while True:
            connection, address = self.server_socket.accept()
            self.in_connections[address] = connection
            client_thread = Thread(target = self.handle_client, args = (connection, address))
            client_thread.start()

    def handle_client(self, connection, address):
        log(f'handling client...')

        with connection:
            # Handle the connection here
            while True:
                data = connection.recv(1024)
                if not data:
                    del self.in_connections[(address)]
                    break
                message = data.decode('utf-8')
                log(f'Received message from {address}: {message}')

                if message.startswith('RETR') and len(self.in_connections) > 0:
                    parts = message.split(" ")
                    if len(parts) == 3:
                        filename = parts[1]
                        host, ip = parts[2].split(":")
                        print(f'filename: {filename}')
                        print(f'host, ip: {host}:{ip}')
                        self.send_file(host, ip, filename)

                elif message.startswith('QUIT'):
                    del self.in_connections[(address)]
                    break

    def send_file(self, host, ip, filename):

        if (host, ip) in self.in_connections:
            connection = self.in_connection[(host, ip)]

            with open(filename, 'rb') as f:
                chunk = f.read(1024)
                while chunk:
                    connection.sendall(chunk)
                    chunk = f.read(1024)
        else:
            log(f'no connection to {host}:{ip}')

    ''' client-side methods '''

    def run_client(self):
        log('running host\'s client...')

        while True:
            command = input('> enter a client command: ')
            # command = "CONNECT 127.0.0.1:8000"

            if command.startswith("CONNECT"):
                parts = command.split(" ")
                if len(parts) == 2:
                    host, port = parts[1].split(":")
                    print(f"Host: {host}")
                    print(f"Port: {port}")
                self.client_socket = socket(AF_INET, SOCK_STREAM)
                self.client_socket.connect((host, int(port)))
                self.out_connections[(host, int(port))] = self.client_socket
                log(f'connected to {host}:{port} on {self.client_socket}')

            # todo: this is where we need to interface with the gui-based inputs and not terminal-based inputs
            elif command.startswith("RETR"):
                parts = command.split(" ")
                if len(parts) == 3:
                    filename = parts[1]
                    host, ip = parts[2].split(":")
                    print(f'filename: {filename}')
                    print(f'host, ip: {host}:{ip}')
                    self.send_message(host, int(ip), parts[0] + ' '  + filename)
                    self.receive_file()
                else:
                    log(f'error: command-syntax')


            elif command.startswith('QUIT'):
                parts = command.split(" ")
                if len(parts) == 2:
                    host, ip = parts[1].split(":")
                self.send_message(host, int(ip), parts[0])
                del self.out_connections[(host, int(ip))]

    def send_message(self, host, ip, message):
        if (host, ip) in self.out_connections:
            connection = self.out_connections[(host, ip)]
            connection.sendall(message.encode('utf-8'))
            log(f'message sent to {connection}')
        else:
            log(f'error: no connection to {host}:{ip}')

    def receive_file(self):
        project_directory = getcwd()
        host_directory = '/host_A'
        chdir(host_directory)
        with open('received_file.txt', 'wb') as f:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    # End of file reached
                    break
                f.write(data)
        chdir(project_directory)

def main():
    host1 = Host('127.0.0.2', 8001, 9001)

if __name__ == '__main__':
    main()
