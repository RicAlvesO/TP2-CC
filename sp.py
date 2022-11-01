import socket
import threading

def handle_client(client_socket, address):
    print("New client connected from {}".format('HIDDEN'))
    full_msg = ""
    while True:
        msg = client_socket.recv(8)
        if len(msg) <= 0:
            break
        full_msg += msg.decode("utf-8")
    if len(full_msg) > 0:
        print(full_msg)

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress=socket.gethostname()
    port=7667
    s.bind((adress, port))
    s.listen()
    print("Server is listening on {}:{}".format(adress, port))

    while True:
        # now our endpoint knows about the OTHER endpoint.
        clientsocket, address = s.accept()
        threading.Thread(target=handle_client, args=(clientsocket, address)).start()
    s.close()
    

if __name__ == "__main__":
    main() 