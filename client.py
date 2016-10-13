import socket

def run(tcp_ip, tcp_port, buffer_size, verification_secret):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_ip, tcp_port))

    #establish shared key

    #Authenticate server
    s.send(verification_secret)
    data = s.recv(buffer_size)
    if data != verification_secret:
        print "THEYRE HACKIN US"
        print "abort abort abort"
        return

    #Send Messages
    print "what do you want to send?"
    message = raw_input()
    s.send(message)
    data = s.recv(buffer_size)
    s.close()

    print "received data:", data
