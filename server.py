import socket
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from time import sleep

def run(tcp_ip, tcp_port, buffer_size, verification_secret):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tcp_port))
    s.listen(1)

    conn, addr = s.accept()
    print 'Connection address:', addr

    #establish Shared key
    shared_base = random.getrandbits(8)
    shared_prime = number.getPrime(16)
    server_secret = random.getrandbits(17)
    print "generating secret..."
    public_server = (shared_base ** server_secret) % shared_prime

    print "base "+ str(shared_base)
    conn.send(str(shared_base))
    sleep(0.05)

    print "prime "+ str(shared_prime)
    conn.send(str(shared_prime))
    sleep(0.05)

    print "server DH public:  "+ str(public_server)

    conn.send(str(public_server))
    sleep(0.05)

    public_client = int(conn.recv(buffer_size))
    print "client DH public: " + str(public_client)

    print "server DH secret:  "+ str(server_secret)
    DH_key = (public_client ** server_secret) % shared_prime
    print "DH key: "+str(DH_key)

    #Authenticate client
    data = conn.recv(buffer_size)
    if data != verification_secret:
        print "THEYRE HACKIN US"
        print "abort abort abort"
        conn.close()
        return
    conn.send(verification_secret)

    #Send Messages
    while 1:
        data = conn.recv(buffer_size)
        if data == "q":
            conn.close()
            return
        print "received data:", data
