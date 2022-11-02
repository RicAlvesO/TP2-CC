import socket
import threading

def handle_client(client_socket, address):
    print("New client connected from {}".format(address))
    while True:
        msg = client_socket.recv(1024).decode("utf-8")
        if len(msg) <= 0:
            break
        if msg == 'EXIT\0':
            client_socket.send("Goodbye from server\0".encode("utf-8"))
            client_socket.send("EXIT\0".encode("utf-8"))
            break
        elif msg[-1] == '\0':
            print(address,':',msg[:-1])
            msg=''
    print("Client disconnected")

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress=socket.gethostname()
    port=7667
    s.bind((adress, port))
    s.listen()
    print("Server is listening on {}:{}".format(adress, port))
    
    
    while True:
        clientsocket, address = s.accept()
        threading.Thread(target=handle_client, args=(clientsocket, address)).start()
        clientsocket.send("Hello from server\0".encode("utf-8"))
    s.close()
    

if __name__ == "__main__":
    main() 