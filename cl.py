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
        while True:
            msg = self.cl_socket.recv(1024).decode("utf-8")
            if len(msg) <= 0:
                break
            if msg == 'EXIT\0':
                self.close_connection()
                break
            elif msg[-1] == '\0':
                print(self.address+'['+str(self.port)+'] '+msg[:-1])
                msg = ''

    def send_msg(self,msg=''):
        # if the function doesnt get a msg, it waits for input
        # this repeats until the user sends string 'EXIT'
        if msg=='': 
            while msg!= 'EXIT':
                msg=input("#> ")+'\0'
                if len(msg)>1:self.cl_socket.sendall(msg.encode("utf-8"))
                msg=msg[:-1]
        # otherwise it sends the message from the argument
        else:
            self.cl_socket.sendall(msg.encode("utf-8"))


def main():
    client=Client(socket.gethostname(),7667)
    client.start_connection()
    threading.Thread(target=client.receive_msg).start()
    threading.Thread(target=client.send_msg).start()

if __name__ == "__main__":
    main()
