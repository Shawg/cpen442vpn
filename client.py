import socket

def run(TCP_IP, TCP_PORT, BUFFER_SIZE):
    print "what do you want to send?"
    MESSAGE = raw_input()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print "received data:", data
