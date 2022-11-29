#!/usr/bin/env python
import socket
import sys
import threading
import time

import parser

# Classe para representar um Servidor Primário
class Server:

    # Inicia o Server usando os dados address, port, domain, log_file, database, top_servers, default_ttl e debug
    # address: Endereco
    # port: Porta utilizada pelo servidor
    # domain: Domínio do servidor
    # log_file: Ficheiro de log
    # database: Base de dados utilizada
    # top_servers: Lista dos Servidores de Topo
    # default_ttl: Tempo de validade, tempo máximo em segundos que os dados podem existir na cache do servidor
    # debug: Indica se o servidor se encontra em modo debug ou não
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
        self.debug=True
        if debug=='shy':
            self.debug=False
        self.cache = parser.parse_dataFile(database[0])
        for domain,log in self.log_file:
            f=open(log,'a+')
            f.close()
        
    # Método usado para escrever no ficheiro de log, que é utilizado para registar a atividade do servidor
    # file: Indica o domínio usado
    # type: Tipo de entrada
    # endereco: Endereço IP
    # msg: Mensagem a ser escrita
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

    # Método usado para aceitar os clientes e ser permitido a execução de queries
    def accept_clients(self):
        while True:
            bytes = self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0].decode()
            address=bytes[1]
            threading.Thread(target=self.handle_querys, args=(message, address), daemon=True).start()
            
    # Método usado para aceitar um Servidor Secundário
    # ss: Informações do Servidor Secundário
    # address: Endereço IP usado
    def accept_ss(self, ss, self_address):
        while True:
            socket,address = self.tcp_socket.accept()
            if address[0] in (x[0] for x in ss):
                threading.Thread(target=self.copy_cache, args=(socket,self_address, address), daemon=True).start()

    # Método usado para copiar de um domínio em especifico
    # domain: Domínio usado
    def copy_for_domain(self, domain):
        list=[]
        for type in self.cache:
            for ent in self.cache[type]:
                if type=='A':
                    list.append(ent[0]+' '+type+' '+ent[1])
                if ent[0] == domain:
                    list.append(ent[0]+' '+type+' '+ent[1])
        return list

    # Método usado para copiar a cache de um servidor para um outro
    # socket : Socket usado
    # self_domain: Domínio utilizado e a ter a cache copiada
    # address: Endereço IP usado
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

    # Método usado para buscar as informações de um domínio e com um tipo especifico
    # domain: Domínio usado
    # type: Tipo do valor
    def fetch_db(self, domain, type):
        list=[]
        if type in self.cache:
            for entry in self.cache[type]:
                if entry[0] == domain:
                    list.append(entry[0]+' '+type+' '+entry[1])
        
        return list

    # Método que executa as querys
    # msg: Mensagem da query
    # address: Endereço IP a ser usado
    def handle_querys(self, msg, address):
        self.write_log(self.domain, 'QR', address,msg[:-1])
        if len(msg) <= 0:
            return
        now=time.time()
        passed_time=self.last_used-now
        self.last_used = now
        get_cache = self.fetch_db(msg.split(';')[1].split(',')[0],msg.split(';')[1].split(',')[1])
        auto_cache =self.fetch_db(msg.split(';')[1].split(',')[0],'NS')
        extra_cache =self.fetch_db(msg.split(';')[1].split(',')[0],'A')
        resp=msg.split(',')[0]+',,0,'+str(len(get_cache))+','+str(len(auto_cache))+','+str(len(extra_cache))+';'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\n'
        if (get_cache+extra_cache)!=[]:
            for l in get_cache+auto_cache+extra_cache:
                resp+=l+',\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))
        else:
            resp=msg.split(',')[0]+',,1,0,0,0;'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\nNOT FOUND'
            self.udp_socket.sendto(resp.encode(),address)
            self.write_log(self.domain, 'RE', address, msg.replace('\n','\\\\'))

# Método principal para a execução do programa 
def main(args):
    server_info = parser.parse_config(args[1])
    if server_info is None:
        return
    port=server_info['PORT']
    default_ttl=86400
    debug='debug'
    if len(args)>2:
        port=int(args[2])
    if len(args)>3:
        default_ttl=int(args[3])
    if len(args)>4 and args[4]=="shy":
        debug='shy'
    server = Server(server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['DB'], server_info['ST'], default_ttl, debug)
    server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
    threading.Thread(target=server.accept_ss, args=(server_info['SS'],server_info['ADDRESS']), daemon=True).start()
    server.accept_clients()


if __name__ == "__main__":
    main(sys.argv)