#!/usr/bin/env python

import socket
import threading

class Client:
    def __init__(self, adress, port):
        self.port = port
        self.address = adress
        self.cl_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_connection(self):
        self.cl_socket.connect((self.address, self.port))
        print("Connected to {}:{}".format(self.address, self.port))

    def close_connection(self):
        self.cl_socket.close()
        self.cl_socket=None

    def receive_msg(self):
        
        msg = self.cl_socket.recv(1024).decode("utf-8")
        if len(msg) <= 0:
            return 0
        if msg == 'EXIT':
            return 1
        else:
            print(self.address+'['+str(self.port)+'] '+msg[:-1])
            msg = ''
        return 0

    def send_msg(self,msg=''):
        # if the function doesnt get a msg, it waits for input
        # this repeats until the user sends string 'EXIT'
        if msg=='EXIT':
            return 1
        # otherwise it sends the message from the argument
        else:
            self.cl_socket.sendall(msg.encode("utf-8"))
        return 0


def main():
    address = socket.gethostname()
    port = 53
    client=Client(address, port)
    client.start_connection()
    inout=0
    while inout==0:
        msg=input("#> ")
        inout+=client.send_msg(msg)
        inout+=client.receive_msg()
    client.close_connection()
    print("Connection closed")
        

if __name__ == "__main__":
    main()
