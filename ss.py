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
        self.tcp_socket.bind((self.address, self.port))
        self.tcp_socket.listen()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.address, port))
        self.udp_buffer = 1024
        self.log_file = log_file
        self.top_servers = top_servers
        self.primary_server = primary_server
        self.cache = []
        print("Server started: {}({})".format(self.address, self.port))

    def accept_dd_only(self, dd_address):
        while True:
            bytes = self.udp_socket.recvfrom()
            message=bytes[0].decode()
            address=bytes[1]
            if address==dd_address[0]:
                threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()

    def accept_clients(self):
        while True:
            bytes = self.udp_socket.recvfrom()
            message=bytes[0].decode()
            address=bytes[1]
            threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()

    def copy_cache(self, primary_server):
        self.tcp_socket.connect(primary_server)
        while True:
            message=self.tcp_socket.recvfrom(1020).decode()
            if message=='END':
                return
            print(message)
            self.cache.append(message)

    def handle_querys(self, msg, address):
        print("New client connected from {}".format(address))
        if len(msg) <= 0:
            print("Client disconnected")
            return
        else:
            print(address,':',msg)
            self.last_used = time.time()
            msg=''
        msg="[TEST RESPONSE]"
        self.udp_socket.send(msg.encode(),address)
        print("Client disconnected")
    

def main(config_file):
    server_info = parsing.parse_config(config_file)
    print(server_info)
    if server_info is None:
        print("Error parsing config file")
        return
    server = Server(server_info['ADDRESS'], server_info['PORT'], server_info['LG'], server_info['ST'], server_info['SP'])
    server.copy_cache(server.primary_server[0])
    if 'DD' in server_info:
        print('Accepting queries from:',server_info['DD'])
        server.accept_dd_only(server_info['DD'])
    else:
        print('Accepting queries from clients')
        server.accept_clients()
            
if __name__ == "__main__":
    main(sys.argv[1]) 