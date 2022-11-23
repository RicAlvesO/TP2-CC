#!/usr/bin/env python
import socket
import sys
import threading
import time

import parser


class Server:

    def __init__(self, address, port, domain, log_file, database, top_servers, default_ttl, debug):
        self.address = address
        self.port = port
        self.domain = domain
        self.clients = []
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((address,port))
        self.tcp_socket.listen()
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((address,port))
        self.udp_buffer = 1024
        self.log_file = log_file
        self.database = database
        self.top_servers = top_servers
        self.last_used = time.time()
        self.default_ttl = default_ttl
        self.debug=False
        if debug=='debug':
            self.debug=True
        self.cache = parser.parse_dataFile(database[0])
        for domain,log in self.log_file:
            f=open(log,'a+')
            f.close()
        
    def write_log(self, file, type, endereco, msg):
        named_tuple = time.localtime() # get struct_time
        time_string = time.strftime("[%m/%d/%Y-%H:%M:%S]", named_tuple)
        port=str(endereco[1])
        if port=='0':port=''
        message=time_string +' ' + type + ' ' + endereco[0]+ ':' + str(endereco[1]) + ' ' + msg
        if self.debug:
            print(message)
        for domain,log in self.log_file:
            if domain == file:
                with open(log, 'a+') as f:
                    f.write(message+'\n')

    def accept_clients(self):
        while True:
            bytes = self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0].decode()
            address=bytes[1]
            threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()
            

    def accept_ss(self, ss, self_address):
        while True:
            socket,address = self.tcp_socket.accept()
            if address[0] in (x[0] for x in ss):
                threading.Thread(target=self.copy_cache, args=(socket,self_address, address), daemon=True).start()

    def copy_for_domain(self, domain):
        list=[]
        for type in self.cache:
            for ent in self.cache[type]:
                if ent[0] == domain:
                    list.append(ent[0]+' '+type+' '+ent[1])
        return list

    def copy_cache(self, socket, self_domain, address):
        dom = socket.recv(1024)
        if dom.decode().split(':')[0] == self.address or dom.decode()==self_domain:
            llist=self.copy_for_domain(dom.decode())
            socket.send(str(len(llist)).encode())
            ack=socket.recv(1024)
            if ack.decode() == "OK":
                for strs in llist:
                    i=0
                    while i<5:
                        socket.send(strs.encode())
                        ack=socket.recv(1024)
                        if ack.decode() == "OK":
                            i=5
                        i+=1
            self.write_log(self.domain, 'ZT',address, 'SP')
        else:
            self.write_log(self.domain, 'EZ',address, 'SP')
            socket.send("-1".encode())

    def fetch_db(self, domain, type):
        list=[]
        if type in self.cache:
            for entry in self.cache[type]:
                if entry[0] == domain:
                    list.append(entry[0]+' '+type+' '+entry[1])
        
        return list

    def handle_querys(self, msg, address):
        self.write_log(self.domain, 'QR', address,msg[:-1])
        if len(msg) <= 0:
            return
        now=time.time()
        passed_time=self.last_used-now
        self.last_used = now
        get_cache = self.fetch_db(msg.split(';')[1].split(',')[0],msg.split(';')[1].split(',')[1])
        resp=msg.split(',')[0]+',,0,'+str(len(get_cache))+',0,0;'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\n'
        if get_cache!=[]:
            for l in get_cache:
                resp+=l+',\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))
        else:
            resp=msg.split(',')[0]+',,1,0,0,0;'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\nNOT FOUND'
            self.udp_socket.sendto(resp.encode(),address)
            self.write_log(self.domain, 'RE', address, msg.replace('\n','\\\\'))

def main(args):
    server_info = parser.parse_config(args[1])
    if server_info is None:
        return
    port=server_info['PORT']
    default_ttl=86400
    debug='shy'
    if len(args)>2:
        port=int(args[2])
    if len(args)>3:
        default_ttl=int(args[3])
    if len(args)>4 and args[4]=="debug":
        debug='debug'
    server = Server(server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['DB'], server_info['ST'], default_ttl, debug)
    server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
    threading.Thread(target=server.accept_ss, args=(server_info['SS'],server_info['ADDRESS']), daemon=True).start()
    server.accept_clients()


if __name__ == "__main__":
    main(sys.argv)