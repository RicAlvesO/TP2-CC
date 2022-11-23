#!/usr/bin/env python
import socket
import sys
import threading
import time

import parser


class Server:

    def __init__(self, adress, port, domain, log_file, top_servers, primary_server):
        self.address = adress
        self.port = port
        self.domain = domain
        self.clients = []
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

    def copy_cache(self, primary_server):
        self.tcp_socket.connect(primary_server)
        self.tcp_socket.sendall((primary_server[0]+':'+str(primary_server[1])).encode())
        size=int(self.tcp_socket.recv(1024).decode())
        if size==-1:
            socket.close()
            return
        self.tcp_socket.sendall("OK".encode())
        while size>0:
            message=self.tcp_socket.recv(1024).decode()
            self.cache.append(message)
            print (self.cache)
            size-=1
        self.tcp_socket.close()

    def handle_querys(self, msg, address):
        print("New client connected from {}".format(address))
        if len(msg) <= 0:
            print("Client disconnected")
            return
        elif msg.split(';')[1].split(',')[0] == self.domain:
            print(address,':',msg)
            now=time.time()
            passed_time=self.last_used-now
            self.last_used = now
            msg="3874,R+A,0,2,3,5;example.com.,MX;\nexample.com. MX mx1.example.com 86400 10,\nexample.com. MX mx2.example.com 86400 20;\nexample.com. NS ns1.example.com. 86400,\nexample.com. NS ns2.example.com. 86400,\nexample.com. NS ns3.example.com. 86400;\nmx1.example.com. A 193.136.130.200 86400,\nmx2.example.com. A 193.136.130.201 86400,\nns1.example.com. A 193.136.130.250 86400,\nns2.example.com. A 193.137.100.250 86400,\nns3.example.com. A 193.136.130.251 86400;"
            self.udp_socket.sendto(msg.encode(),address)
        else:
            print("Not this domain!")
        print("Client disconnected")

def main(config_file):
    server_info = parser.parse_config(config_file)
    print(server_info)
    if server_info is None:
        print("Error parsing config file")
        return
    server = Server("", server_info['PORT'], server_info['ADDRESS'],server_info['LG'], server_info['ST'], server_info['SP'])
    server.copy_cache(server.primary_server[0])
    if 'DD' in server_info:
        print('Accepting queries from:',server_info['DD'])
        server.accept_dd_only(server_info['DD'])
    else:
        print('Accepting queries from clients')
        server.accept_clients()

if __name__ == "__main__":
    main(sys.argv[1])