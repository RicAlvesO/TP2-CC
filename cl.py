import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
adress=socket.gethostname()
port=7667
s.connect((adress, port))
msg=''
while msg[:-1] != 'EXIT':
    msg=input("Message: ")+'\n'
    if len(msg)>1:s.sendall(msg.encode("utf-8"))
s.close()


