import socket
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from Crypto.Hash import SHA256
from ModularExponentiation import fastPow
from time import sleep

def run(tcp_ip, tcp_port, buffer_size, verification_secret):

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_ip, tcp_port))

    #establish shared key
    print "Establishing a shared key"
    client_secret = random.getrandbits(1024)

    shared_base = int(s.recv(buffer_size))
    print "base "+ str(shared_base)

    shared_prime = int(s.recv(buffer_size))
    print "prime "+ str(shared_prime)

    public_server = int(s.recv(buffer_size))
    print "server DH public: " + str(public_server)

    IV = s.recv(buffer_size)

    public_client = pow(shared_base, client_secret, shared_prime)
    print "client DH public: " + str(public_client)
    sleep(0.05)
    s.send(str(public_client))

    print "client DH secret: " + str(client_secret)

    print "Calculatin key, this may take a minute..."
    DH_key = pow(public_server, client_secret, shared_prime)
    DH_key = SHA256.new(str(DH_key))
    print "DH key: "+DH_key.hexdigest()

    # set up encryption
    encryption_suite = AES.new(DH_key.digest(), AES.MODE_ECB)

    #Authenticate server
    print "Verifying the server"
    s.send(verification_secret)
    data = s.recv(buffer_size)
    if data != verification_secret:
        print "THEYRE HACKIN US"
        print "abort abort abort"
        s.close()
        return

    #Send Messages
    while 1:
        print "what do you want to send? (send q to close connection)"
        message = raw_input()
        while len(message) % 16 != 0:
            message = message+'0'
        message = encryption_suite.encrypt(message)
        if message == "q":
            s.send(message)
            s.close()
            return
        s.send(message)

    print "received data:", data
