#!/usr/bin/env python
import socket


class Client:
    def __init__(self, adress, port):
        self.port = port
        self.address = adress
        self.cl_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_buffer = 1024

    def receive_msg(self):
        bytes = self.cl_socket.recvfrom(self.udp_buffer)
        message = bytes[0].decode()
        address = bytes[1]
        print(self.address+'['+str(address)+'] '+message)

    def send_msg(self,msg=''):
        self.cl_socket.sendto(msg.encode(), (self.address, self.port))


def main():
    address = "10.2.2.2"
    port = 1234
    client=Client(address, port)
    msg="[TEST QUERY]"
    client.send_msg(msg)
    client.receive_msg()
    print("Connection closed")

if __name__ == "__main__":
    main()