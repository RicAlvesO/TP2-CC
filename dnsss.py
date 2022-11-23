#!/usr/bin/env python
import socket
import sys
import threading
import time

import parser


class Server:

    def __init__(self, address, port, domain, log_file, top_servers, primary_server, default_ttl, debug):
        self.address = address
        self.port = port
        self.domain = domain
        self.clients = []
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((address,port))
        self.udp_buffer = 1024
        self.log_file = log_file
        self.top_servers = top_servers
        self.primary_server = primary_server
        self.last_used=time.time()
        self.cache = {}
        self.default_ttl= default_ttl
        self.debug = debug
        print("Server started: {}({})".format(self.address, self.port))

    def write_log(self, file, type, endereco, msg):
        message=type + ' ' + endereco[0] + str(endereco[1]) + ' ' + msg
        if self.debug: 
            print(message)
        with open(file, 'a+') as f:
            f.write(message)

    def accept_clients(self):
        while True:
            bytes = self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0].decode()
            address=bytes[1]
            threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()

    def fetch_db(self, domain, type):
        list=[]
        if type in self.cache:
            for entry in self.cache[type]:
                if entry[0] == domain:
                    list.append(entry[0]+' '+type+' '+entry[1])
        
        return list

    def copy_cache(self, primary_server):
        self.tcp_socket.connect(primary_server)
        self.tcp_socket.sendall(self.domain.encode())
        size=int(self.tcp_socket.recv(1024).decode())
        print(size)
        if size==-1:
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
            socket.close()
            return
        self.tcp_socket.sendall("OK".encode())
        while size>0:
            message=self.tcp_socket.recv(1024).decode()
            message=message.split(' ')
            if message[1] in self.cache:
                self.cache[message[1]].append((message[0],message[2]+' '+message[3]+' '+message[4]))
            else:
                self.cache[message[1]]=[(message[0],message[2]+' '+message[3]+' '+message[4])]
            self.tcp_socket.sendall("OK".encode())
            size-=1
        self.tcp_socket.shutdown(socket.SHUT_RDWR)
        self.tcp_socket.close()

    def handle_querys(self, msg, address):
        imp=msg.split(',')[0]+','+msg.split(',')[1]+','+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]
        #self.write_log(self.log_file[self.domain], 'QR', address[0]+':'+str(address[1]), imp)
        if len(msg) <= 0:
            print("Client disconnected")
            return
        elif msg.split(';')[1].split(',')[0] == self.domain:
            now=time.time()
            passed_time=self.last_used-now
            self.last_used = now
            get_cache = self.fetch_db(msg.split(';')[1].split(',')[0],msg.split(';')[1].split(',')[1])
            msg=msg.split(',')[0]+',,0,'+str(len(get_cache))+',0,5;example.com.,MX;\n'
            if get_cache!=[]:
                for l in get_cache:
                    msg+=l+',\n'
            else:
                udp_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                udp_sock.sendto(msg.encode(), self.primary_server[0])
                bytes = udp_sock.recvfrom(self.udp_buffer)
                msg = bytes[0].decode()
            self.udp_socket.sendto(msg[:-2].encode(),address)
        else:
            now=time.time()
            passed_time=self.last_used-now
            self.last_used = now
            udp_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.sendto(msg.encode(), self.primary_server[0])
            ###self.write_log(self.log_file[self.domain], 'QE', self.primary_server[0]+':'+str(self.primary_server[1]), imp)
            bytes = udp_sock.recvfrom(self.udp_buffer)
            message = bytes[0].decode()
            self.udp_socket.sendto(message.encode(), address)
        print("Client disconnected")

def main(args):
    server_info = parser.parse_config(args[1])
    print(server_info)
    if server_info is None:
        print("Error parsing config file")
        return
    port=server_info['PORT']
    default_ttl=86400
    debug=False
    if len(args)>2:
        port=int(args[2])
    if len(args)>3:
        default_ttl=int(args[3])
    if len(args)>4 and args[4]=="debug":
        debug=True
    server = Server(server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], server_info['SP'], default_ttl, debug)
    server.copy_cache(server.primary_server[0])
    
    print('Accepting queries from clients')
    server.accept_clients()

if __name__ == "__main__":
    main(sys.argv)