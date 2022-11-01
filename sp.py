import socket
import threading

def handle_client(client_socket, address):
    print("New client connected from {}".format(address))
    full_msg = ""
    while True:
        msg = client_socket.recv(8).decode("utf-8")
        if len(msg) <= 0:
            break
        full_msg += msg
        if msg[-1] == '\n':
            print(address,':',full_msg[:-1])
            full_msg=''
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
    s.close()
    

if __name__ == "__main__":
    main() 