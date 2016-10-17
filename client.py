import socket
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from time import sleep

def run(tcp_ip, tcp_port, buffer_size, verification_secret):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_ip, tcp_port))

    #establish shared key
    client_secret = random.getrandbits(16)

    shared_base = int(s.recv(buffer_size))
    print "base "+ str(shared_base)

    shared_prime = int(s.recv(buffer_size))
    print "prime "+ str(shared_prime)

    public_server = int(s.recv(buffer_size))
    print "server DH public: " + str(public_server)

    public_client = (shared_base ** client_secret) % shared_prime
    print "client DH public: " + str(public_client)

    print "client DH secret: " + str(client_secret)

    #Authenticate server
    s.send(verification_secret)
    data = s.recv(buffer_size)
    if data != verification_secret:
        print "THEYRE HACKIN US"
        print "abort abort abort"
        s.close()
        return

    #Send Messages
    while 1:
        print "what do you want to send?"
        message = raw_input()
        if message == "q":
            s.send(message)
            s.close()
            return
        s.send(message)

    print "received data:", data
