#!/usr/bin/env python
import parser
import socket
import sys
import threading
import time

import parser
import cache

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
    def __init__(self, stype, address, port, domain, log_file, top_servers, default_ttl, debug, database=None,primary_server=None, default_servers=None):
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
        self.last_used = time.time()
        self.default_ttl = default_ttl
        self.debug=True
        self.stype=stype


        if stype=='SP': 
            self.database = database
            self.cache = parser.parse_dataFile(database[0])
            self.tcp_socket.bind((address,port))
            self.tcp_socket.listen()

        elif stype=='SS':
            self.primary_server = primary_server
            self.cache = {}

        elif stype=='SR':
            self.cache = {}
            self.default_servers = default_servers

        if debug=='shy':
            self.debug=False
        self.cache = cache.Cache()
        self.cache.insert_DB(self.database[0])

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
        return self.cache.get_entries_for_domain(domain)

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


    # Método usado para copiar a cache de um servidor para um outro
    # primary_server: Servidor Primário que terá a cache copiada
    def receive_cache(self, primary_server):
        self.tcp_socket.connect(primary_server)
        self.tcp_socket.sendall(self.domain.encode())
        size=int(self.tcp_socket.recv(1024).decode())
        if size==-1:
            self.write_log(self.domain, 'EZ',primary_server, 'SP')
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
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
        self.write_log(self.domain, 'ZT',primary_server, 'SS')


    # Método usado para buscar as informações de um domínio e com um tipo especifico
    # domain: Domínio usado
    # type: Tipo do valor
    def fetch_db(self, domain, type):
        return self.cache.get_entry(domain, type)

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

        #PROCURA DA RESPOSTA NA CACHE

        get_cache = self.fetch_db(msg.split(';')[1].split(',')[0],msg.split(';')[1].split(',')[1])
        auto_cache =self.fetch_db(msg.split(';')[1].split(',')[0],'NS')
        extra_cache =self.fetch_db(msg.split(';')[1].split(',')[0],'A')
        resp=msg.split(',')[0]+',,0,'+str(len(get_cache))+','+str(len(auto_cache))+','+str(len(extra_cache))+';'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\n'
        
        
        if (get_cache+extra_cache)!=[]:

            # RESPOSTA ENCONTRADA NA CACHE

            for l in get_cache+auto_cache+extra_cache:
                resp+=l+',\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))
        
        elif self.stype=='SR':
        
            # RESPOSTA NAO ESTA NA CACHE E SERVIDOR É SR LOGO PERGUNTA AO SERVER DEFAULT
        
            udp_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.sendto(msg.encode(), self.default_server[0])
            self.write_log(self.domain, 'QE', self.default_server[0],msg[:-1])
            bytes = udp_sock.recvfrom(self.udp_buffer)
            msg = bytes[0].decode()
            self.write_log(self.domain, 'RR', self.default_server[0],msg.replace('\n','\\\\'))
            self.udp_socket.sendto(msg.encode(),address)
            self.write_log(self.domain, 'RE', address,msg.replace('\n','\\\\'))
            
        else:

            # RESPOSTA NAO ESTA NA CACHE E SERVIDOR É PRIMARIO/SECUNDARIO LOGO PERGUNTA AO SERVER DE TOPO

            udp_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.sendto(msg.encode(), self.top_servers[0])
            self.write_log(self.domain, 'QE', self.top_servers[0],msg[:-1])
            bytes = udp_sock.recvfrom(self.udp_buffer)
            msg = bytes[0].decode()
            self.write_log(self.domain, 'RR', self.top_servers[0],msg.replace('\n','\\\\'))
            self.udp_socket.sendto(msg.encode(),address)
            self.write_log(self.domain, 'RE', address,msg.replace('\n','\\\\'))

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
    if(server_info['Type']=='SP'):
        server = Server(server_info['Type'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, database=server_info['DB'])
        server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
        threading.Thread(target=server.accept_ss, args=(server_info['SS'],server_info['ADDRESS']), daemon=True).start()
    elif(server_info['Type']=='SS'):
        server = Server(server_info['Type'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, primary_server=server_info['SP'])
        server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
        server.receive_cache(server.primary_server[0])
    elif(server_info['Type']=='SR'):
        server = Server(server_info['Type'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, default_servers=server_info['SERVERS'])
        server.write_log('all', 'SR', ('127.0.01',0), str(port)+' '+str(default_ttl)+' '+debug)
    server.accept_clients()


if __name__ == "__main__":
    main(sys.argv)