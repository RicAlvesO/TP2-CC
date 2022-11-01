import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
adress=socket.gethostname()
port=7667
s.connect((adress, port))
s.sendall("ÇÁáô".encode("utf-8"))
s.close()


