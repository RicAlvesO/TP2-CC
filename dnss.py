#!/usr/bin/env python
import socket
import sys
import threading
import time

import fparser
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
        self.default_ttl = default_ttl
        self.debug=True
        self.stype=stype
        self.cache = cache.Cache(default_ttl)


        if stype=='SP' or stype=='ST': 
            self.database = database
            self.cache.insert_DB(database[0])
            self.tcp_socket.bind((address,port))
            self.tcp_socket.listen()

        elif stype=='SS':
            self.last_update = -1
            self.primary_server = primary_server

        elif stype=='SR':
            self.default_servers = default_servers

        if debug=='shy':
            self.debug=False

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
        print("Server is running...")
        while True:
            bytes = self.udp_socket.recvfrom(self.udp_buffer)
            message=bytes[0].decode()
            address=bytes[1]
            print("Received message: " + message)
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
        serial = socket.recv(1024)
        if dom.decode()==self_domain[0] and int(serial.decode())!=self.cache.get_serial():
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
        elif dom.decode()==self_domain[0] and int(serial.decode())==self.cache.get_serial():
            self.write_log(self.domain, 'EZ',address, 'SP')
            socket.send("0".encode())
        else:
            self.write_log(self.domain, 'EZ',address, 'SP')
            socket.send("-1".encode())


    def cache_update(self, primary_server):
        self.receive_cache(primary_server)
        updated=True
        while True:
            time.sleep(self.cache.get_refesh())
            updated=False
            while not updated:
                i=self.receive_cache(primary_server)
                if i>=0:
                    self.last_update=time.time()
                    updated=True
                else:
                    time.sleep(self.cache.get_retry())
        
        
    # Método usado para copiar a cache de um servidor para um outro
    # primary_server: Servidor Primário que terá a cache copiada
    def receive_cache(self, primary_server):
        self.tcp_socket.connect(primary_server)
        self.tcp_socket.sendall(self.domain.encode())
        self.tcp_socket.sendall((str(self.cache.get_serial())).encode())
        size=int(self.tcp_socket.recv(1024).decode())
        if size==-1:
            self.write_log(self.domain, 'EZ',primary_server, 'SP')
            self.tcp_socket.shutdown(socket.SHUT_RDWR)
            self.tcp_socket.close()
            return
        self.tcp_socket.sendall("OK".encode())
        while size>0:
            message=self.tcp_socket.recv(1024).decode()
            self.cache.insert_cache(message)
            self.tcp_socket.sendall("OK".encode())
            size-=1
        self.tcp_socket.shutdown(socket.SHUT_RDWR)
        self.tcp_socket.close()
        self.write_log(self.domain, 'ZT',primary_server, 'SS')


    # Método usado para buscar as informações de um domínio e com um tipo especifico
    # domain: Domínio usado
    # type: Tipo do valor
    def fetch_db(self, domain, type):
        return self.cache.get_query(domain, type)

    # Método que executa as querys
    # msg: Mensagem da query
    # address: Endereço IP a ser usado
    def handle_querys(self, msg, address):
        self.write_log(self.domain, 'QR', address,msg[:-1])
        if len(msg) <= 0:
            return

        print(msg)

        if self.type == 'SS' and time.time()-self.last_update>=self.cache.get_expire():
            get_cache=[]
            auto_cache=[]
            extra_cache=[]
            val_amount=0
        else:
            #PROCURA DA RESPOSTA NA CACHE
            get_cache = self.fetch_db(msg.split(';')[1].split(',')[0],msg.split(';')[1].split(',')[1])
            auto_cache = get_cache[1]
            extra_cache = get_cache[2]
            get_cache = get_cache[0]
            val_amount = len(get_cache)
            
        flags = msg.split(',')[1]
        if 'A' not in flags:
            flags+='+A'
        
        if val_amount!=0:

            # RESPOSTA ENCONTRADA NA CACHE

            flags.replace("Q+","")
            resp=msg.split(',')[0]+','+flags+',0,'+str(len(get_cache))+','+str(len(auto_cache))+','+str(len(extra_cache))+';'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\n'
            if len(get_cache) > 0:
                for l in get_cache:
                    resp += l+',\n'
                resp = resp[:-2]
            resp += ';\n'
            if len(auto_cache) > 0:
                for l in auto_cache:
                    resp += l+',\n'
                resp = resp[:-2]
            resp += ';\n'
            if len(extra_cache) > 0:
                for l in extra_cache:
                    resp += l+',\n'
                resp = resp[:-2]
            resp += ';\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))
            return
        
        elif self.stype=='SR' and 'A' not in msg.split(',')[1]:
            
            print('sr no cache')

            # RESPOSTA NAO ESTA NA CACHE E SERVIDOR É SR LOGO PERGUNTA AO SERVER DEFAULT
        
            udp_sock=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server = 0
            while server < len(self.default_server):
                try:
                    udp_sock.sendto((','.join(msg.split(',')[0]+flags+msg.split(';')[0].split(',')[2:])+';'+msg.split(';')[1].split(',')[1]+';').encode(), self.default_server[server])
                    udp_sock.settimeout(5)
                    self.write_log(self.domain, 'QE', self.default_server[server], msg[:-1])
                    break
                except:
                    server+=1
            
            if server != len(self.default_server):
                bytes = udp_sock.recvfrom(self.udp_buffer)
                resp = bytes[0].decode()
                self.write_log(self.domain, 'RR', self.default_server[server],resp.replace('\n','\\\\'))
                val_amount=int(resp.split(',')[3])
                if val_amount > 0 :
                    self.cache.insert_cache(resp)
                    self.udp_socket.sendto(resp.encode(),address)
                    self.write_log(self.domain, 'RE', address,resp.replace('\n','\\\\'))
                    return

        print('no cache, no default')

        if 'A' in msg.split(',')[1]:
            print('not first server, returning error')
            flags.replace("Q+","")
            error=1
            if len(auto_cache)+len(extra_cache) == 0:
                error=2
            resp=msg.split(',')[0]+','+flags+','+error+','+str(len(get_cache))+','+str(len(auto_cache))+','+str(len(extra_cache))+';'+msg.split(';')[1]+';\n'
            for l in get_cache+auto_cache+extra_cache:
                resp+=l+',\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))
            return

        # RESPOSTA NAO ESTA NA CACHE E SERVIDOR É PRIMARIO/SECUNDARIO LOGO PERGUNTA AO SERVER DE TOPO
        
        doms = msg.split(';')[1].split(',')[0].split('.')[:-1]
        for i in range(len(doms)):
            doms[i]=('.'.join(doms[i:])+'.')
        doms.reverse()
        doms+=doms[-1]

        to_try = self.top_servers
        print(to_try)

        while len(doms)>0:
            dom = doms.pop(0)
            print('checking domain: '+dom)
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server = 0
            while server < len(to_try):
                try:
                    print('talkin to server: '+to_try[server][0]+':'+str(to_try[server][1]))
                    udp_sock.sendto((','.join(msg.split(',')[0]+flags+msg.split(';')[0].split(',')[2:])+';'+dom+','+msg.split(';')[1].split(',')[1]+';').encode(), (to_try[server][0], to_try[server][1]))
                    udp_sock.settimeout(10)
                    self.write_log(self.domain, 'QE', to_try[server], msg[:-1])
                    bytes = udp_sock.recvfrom(self.udp_buffer)
                    break
                except socket.timeout:
                    print('server not responding')
                    server += 1

            if server != len(to_try):
                res = bytes[0].decode()
                self.write_log(self.domain, 'RR', self.to_try[server], res.replace('\n', '\\\\'))
                auto_amount = int(res.split(',')[4])
                extra_amount = int(res.split(',')[5])
                if auto_amount+extra_amount > 0:
                    self.cache.insert_cache(res)
                    to_try = []
                    find=[]
                    for i in range(auto_amount):
                        if res.split(';')[3].split(',')[i].split(' ')[1] == 'NS':
                            find.append(res.split(';')[3].split(',')[i].split(' ')[2])
                    for i in range(extra_amount):
                        if res.split(';')[4].split(',')[i].split(' ')[0] in find:
                            to_try.append(res.split(';')[4].split(',')[i].split(' ')[2])
                    get_cache = res.split(';')[2].split(',')
                    auto_cache = res.split(';')[3].split(',')
                    extra_cache = res.split(';')[4].split(',')
                else:
                    doms=[]
                    

        if val_amount==0:
            flags.replace("Q+","")
            error=1
            if len(auto_cache)+len(extra_cache) == 0:
                error=2
            resp=msg.split(',')[0]+','+flags+','+str(error)+','+str(len(get_cache))+','+str(len(auto_cache))+','+str(len(extra_cache))+';'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\n'
            resp+= ';\n'
            if len(auto_cache)>0:
                for l in auto_cache:
                    resp += l+',\n'
                resp=resp[:-2]
            resp+= ';\n'
            if len(extra_cache)>0:
                for l in extra_cache:
                    resp += l+',\n'
                resp=resp[:-2]
            resp+= ';\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))
        else:
            flags.replace("Q+","")
            resp=msg.split(',')[0]+','+flags+',0,'+str(len(get_cache))+','+str(len(auto_cache))+','+str(len(extra_cache))+';'+msg.split(';')[1].split(',')[0]+','+msg.split(';')[1].split(',')[1]+';\n'
            if len(get_cache)>0:
                for l in get_cache:
                    resp += l+',\n'
                resp=resp[:-2]
            resp+= ';\n'
            if len(auto_cache)>0:
                for l in auto_cache:
                    resp += l+',\n'
                resp=resp[:-2]
            resp+= ';\n'
            if len(extra_cache)>0:
                for l in extra_cache:
                    resp += l+',\n'
                resp=resp[:-2]
            resp+= ';\n'
            self.udp_socket.sendto(resp[:-1].encode(),address)
            self.write_log(self.domain, 'RE', address, resp[:-2].replace('\n','\\\\'))

# Método principal para a execução do programa 
def main(args):
    server_info = fparser.parse_config(args[1])
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
    if(server_info['TYPE']=='SP'):
        server = Server(server_info['TYPE'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, database=server_info['DB'])
        server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
        threading.Thread(target=server.accept_ss, args=(server_info['SS'],server_info['ADDRESS']), daemon=True).start()
    elif(server_info['TYPE']=='SS'):
        server = Server(server_info['TYPE'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, primary_server=server_info['SP'])
        server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
        server.receive_cache(server.primary_server[0])
    elif(server_info['TYPE']=='SR'):
        server = Server(server_info['TYPE'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, default_servers=server_info['SERVERS'])
        server.write_log('all', 'SR', ('127.0.01',0), str(port)+' '+str(default_ttl)+' '+debug)
    if(server_info['TYPE']=='ST'):
        server = Server(server_info['TYPE'],server_info['DD'][0][0],port, server_info['ADDRESS'],server_info['LG'], server_info['ST'], default_ttl, debug, database=server_info['DB'])
        server.write_log('all', 'ST', ('127.0.0.1',0), str(port)+' '+str(default_ttl)+' '+debug)
    server.accept_clients()


if __name__ == "__main__":
    main(sys.argv)
