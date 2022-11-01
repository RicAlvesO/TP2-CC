import socket
import threading

def send_msg(s,msg=''):
    # if the function doesnt get a msg, it waits for input
    # this repeats until the user sends string 'EXIT'
    if msg=='': 
        while msg!= 'EXIT':
            msg=input("#> ")+'\0'
            if len(msg)>1:s.sendall(msg.encode("utf-8"))
            msg=msg[:-1]
    # closes the socket
    elif msg=='EXIT':
        s.close()
    # otherwise it sends the message from the argument
    else:
        s.sendall(msg.encode("utf-8"))


def receive_msg(s,address):
    full_msg = ""
    while True:
        msg = s.recv(8).decode("utf-8")
        if len(msg) <= 0:
            break
        full_msg += msg
        if msg[-1] == '\0':
            print(address+'>', full_msg[:-1])
            full_msg = ''

def connect_to_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    adress = socket.gethostname()
    s.connect((adress, port))
    print("Connected to {}:{}".format(adress, port))
    return s

def main():
    port = 7667
    s=connect_to_port(port)
    threading.Thread(target=receive_msg, args=(s,socket.gethostname())).start()
    threading.Thread(target=send_msg, args=(s,'')).start()

if __name__ == "__main__":
    main()
