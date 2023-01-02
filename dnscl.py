#!/usr/bin/env python

# Ficheiro principal dos clientes
#
# @Author: Ricardo Alves Oliveira (A96794)
# @Author: Rodrigo José Teixeira Freita (A96547)
#
# @Version: 02012023

import random
import socket
import sys


# Classe para representar um cliente
class Client:
    
    # Inicia o Client usando os dados adresse port
    # adress: Endereço IP
    # port: Porta utilizada pelo cliente
    def __init__(self, adress, port):
        self.port = port
        self.address = adress
        self.cl_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_buffer = 1024

    # Método realizado para o cliente receber uma mensagem
    def receive_msg(self):
        bytes = self.cl_socket.recvfrom(self.udp_buffer)
        message = bytes[0].decode()
        address = bytes[1]
        print('['+str(address)+']: '+message)

    # Método realizado para o cliente enviar uma mensagem
    # msg: Mensagem a ser enviada
    def send_msg(self,msg=''):
        self.cl_socket.sendto(msg.encode(), (self.address, self.port))

# Método principal para a execução do programa 
def main(args):
    if len(args[1].split(':')) == 2:
        address= args[1].split(':')[0]
        port = int(args[1].split(':')[1])
    else:
        address= args[1]
        port = 53
    client=Client(address, port)
    id = random.randint(0, 65535)
    query=str(id)+',Q'
    if len(args)==5:
        query+='+'+args[4]
    query+=',0,0,0,0;'+args[2]+','+args[3]+';'
    client.send_msg(query)
    client.receive_msg()

if __name__ == "__main__":
    main(sys.argv)