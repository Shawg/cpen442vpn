import socket
import threading
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from Crypto.Hash import SHA256
from time import sleep

def run(tcp_ip, tcp_port, buffer_size, verification_secret):

    exitFlag = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_ip, tcp_port))

    #Authenticate server
    nonce = str(random.getrandbits(128))
    s.send(nonce)
    challenge = SHA256.new(verification_secret+nonce).hexdigest()
    resp = s.recv(buffer_size)

    if resp != challenge:
        print "THEYRE HACKIN US"
        print "abort abort abort"
        s.close()
        return

    #getting authenticated
    server_nonce = s.recv(buffer_size)
    s.send(SHA256.new(verification_secret+server_nonce).hexdigest())

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

    #Send Messages
    thread1 = sendThread(1, "sendThread", encryption_suite, s)
    thread1.start()

def send(name, encryption_suite, s):
    while 1:
        print "what do you want to send? (send q to close connection)"
        message = raw_input()
        quit_message = message
        while len(message) % 16 != 0:
            message = message+'0'
        message = encryption_suite.encrypt(message)
        if quit_message == "q":
            s.send(message)
            s.close()
            return
        s.send(message)

class sendThread (threading.Thread):
    def __init__(self, threadID, name, encryption_suite, s):
        threading.Thread.__init__(self)
        self.name = name
        self.threadID = threadID
        self.encryption_suite = encryption_suite
        self.s = s
    def run(self):
        print "Starting " + self.name
        send(self, self.encryption_suite, self.s)
