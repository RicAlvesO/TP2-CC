#!/usr/bin/env python
import socket
import sys
import threading
import time

import parsing


class Server:

    def __init__(self, adress, port, log_file, top_servers, primary_server):
        self.address = adress
        self.port = port
        self.clients = []
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.address, 1233))
        self.tcp_socket.listen()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.address, 1233))
        self.udp_buffer = 1024
        self.log_file = log_file
        self.top_servers = top_servers
        self.primary_server = primary_server
        self.cache = self.copy_cache(primary_server)
        print("Server started: {}({})".format(self.address, self.port))

    def accept_dd_only(self, dd_address):
        while True:
            socket, address = self.tcp_socket.accept()
            if address==dd_address[0]:
                threading.Thread(target=self.handle_querys, args=(socket, address), daemon=True).start()

    def accept_clients(self):
        while True:
            socket, address = self.tcp_socket.accept()
            threading.Thread(target=self.handle_querys, args=(socket, address), daemon=True).start()

    def copy_cache(self, primary_server):
        self.udp_socket.sendto('COPY'.encode(), primary_server)
        while True:
            bytes=self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0]
            address=bytes[1]
            if address == primary_server:
                self.cache.append(message)
            else:
                break

    def handle_querys(self, client_socket, address):
        print("New client connected from {}".format(address))
        self.clients.append(client_socket)
        while True:
            msg = client_socket.recv(1024).decode("utf-8")
            if len(msg) <= 0:
                break
            if msg == 'EXIT':
                client_socket.send("Goodbye from server".encode("utf-8"))
                self.last_used = time.time()
                self.clients.remove(client_socket)
                break
            else:
                print(address,':',msg)
                self.last_used = time.time()
                msg=''
        print("Client disconnected")
    

def main(config_file):
    server_info = parsing.parse_config(config_file)
    print(server_info)
    if server_info is None:
        print("Error parsing config file")
        return
    server = Server(server_info['ADDRESS'], server_info['PORT'], server_info['LG'], server_info['ST'], server_info['SP'])
    if 'DD' in server_info:
        print('Accepting queries from:',server_info['DD'])
        server.accept_dd_only(server_info['DD'])
    else:
        print('Accepting queries from clients')
        server.accept_clients()
            
if __name__ == "__main__":
    main(sys.argv[1]) 