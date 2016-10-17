import socket
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number

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
    print "prime "+ str(shared_prime)
    print "server DH secret:  "+ str(server_secret)

    conn.send(str(shared_base))
    conn.send(str(shared_prime))

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
