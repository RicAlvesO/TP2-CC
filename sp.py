import socket
import threading
import time

class Server:

    def __init__(self, adress, port, timeout=90):
        self.port = port
        self.address = adress
        self.clients = []
        self.last_used = time.time()
        self.timeout = timeout
        self.sv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sv_socket.bind((self.address, self.port))
        self.sv_socket.listen()
        print("Server started on {}:{}".format(self.address, self.port))

    def handle_client(self, client_socket, address):
        print("New client connected from {}".format(address))
        self.last_used = time.time()
        self.clients.append(client_socket)
        while True:
            msg = client_socket.recv(1024).decode("utf-8")
            if len(msg) <= 0:
                break
            if msg == 'EXIT':
                client_socket.send("Goodbye from server".encode("utf-8"))
                self.last_used = time.time()
                self.clients.remove(client_socket)
                break
            else:
                print(address,':',msg)
                self.last_used = time.time()
                msg=''
        print("Client disconnected")
    
    def timer(self):
        while True:
            time.sleep(5)
            if time.time() - self.last_used > self.timeout:
                self.sv_socket.close()
                self.sv_socket=None
                print("Server closed")
                break
    
    def accept_clients(self):
        while True:
            client_socket, address = self.sv_socket.accept()
            threading.Thread(target=self.handle_client, args=(client_socket, address), daemon=True).start()


def main():
    adress=socket.gethostname()
    port=7667
    server=Server(adress,port,60)
    threading.Thread(target=server.accept_clients, daemon=True).start()
    server.timer()
    

if __name__ == "__main__":
    main() 