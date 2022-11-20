#!/usr/bin/env python
import socket
import sys
import threading
import time

import parsing


class Server:

    def __init__(self, adress, port, log_file, database, top_servers):
        self.address = adress
        self.port = port
        self.clients = []
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.address, port))
        self.tcp_socket.listen()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.address, port))
        self.udp_buffer = 1024
        self.log_file = log_file
        self.database = database
        self.top_servers = top_servers
        self.cache = ["CACHE LINE 0","CACHE LINE 1"] # load database from file
        print("Server started: {}({})".format(self.address, self.port))

    def accept_dd_only(self, dd_address):
        while True:
            bytes = self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0].decode()
            address=bytes[1]
            if address==dd_address[0]:
                threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()

    def accept_clients(self):
        while True:
            bytes = self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0].decode()
            address=bytes[1]
            threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()

    def accept_ss(self, ss, phony):
        while True:
            socket,address = self.tcp_socket.accept()
            print (address,ss,address in ss)
            if address[0] in (x[0] for x in ss):
                threading.Thread(target=self.copy_cache, args=[socket], daemon=True).start()

    def copy_cache(self, socket):
        message = socket.recv(1024)
        print (message.decode())
        if message.decode() == 'COPY':
            print('ola')
            for str in self.cache:
                socket.send(str.encode())
            socket.send('END'.encode())

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
        self.udp_socket.sendto(msg.encode(),address)
        print("Client disconnected")

def main(config_file):
    server_info = parsing.parse_config(config_file)
    print(server_info)
    if server_info is None:
        print("Error parsing config file")
        return
    server = Server(server_info['ADDRESS'], server_info['PORT'], server_info['LG'], server_info['DB'], server_info['ST'])
    if 'DD' in server_info:
        print('Accepting queries from:',server_info['DD'])
        server.accept_dd_only(server_info['DD'])
    else:
        print('Accepting secondary servers from:',server_info['SS'])
        print('Accepting queries from clients')
        threading.Thread(target=server.accept_ss, args=(server_info['SS'],''), daemon=True).start()
        server.accept_clients()

if __name__ == "__main__":
    main(sys.argv[1])