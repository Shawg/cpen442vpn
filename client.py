import socket
import threading
import sys
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from Crypto.Hash import SHA256
from time import sleep

exitFlag = 0

def run(tcp_ip, tcp_port, buffer_size, verification_secret):

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

    # set up sending and receiving threads
    sender = myThread(1, "sendThread", encryption_suite, s, send, buffer_size)
    receiver = myThread(2, "recvThread", encryption_suite, s, recv, buffer_size)
    sender.deamon = 1
    receiver.deamon = 1
    sender.start()
    receiver.start()

    while not exitFlag:
        pass
        
    s.close()

def recv(name, encryption_suite, s, buffer_size):
    global exitFlag
    while not exitFlag:
        data = s.recv(buffer_size)
        original = data
        data = encryption_suite.decrypt(data)
        while data.endswith('0'):
            data = data[:-1]
        if data == "q":
            exitFlag = 1
            return
        if data != "":
            print "======================================================"
            print "encrypted stuff: "+original
            print "received data:", data
            print "======================================================"
            print "what do you want to send? (send q to close connection)"

def send(name, encryption_suite, s, buffer_size):
    global exitFlag
    while not exitFlag:
        print "======================================================"
        print "what do you want to send? (send q to close connection)"
        message = raw_input()
        quit_message = message
        while len(message) % 16 != 0:
            message = message+'0'
        message = encryption_suite.encrypt(message)
        if quit_message == "q":
            s.send(message)
            exitFlag = 1
            return
        if not exitFlag:
            s.send(message)

class myThread (threading.Thread):
    def __init__(self, threadID, name, encryption_suite, s, func, buffer_size):
        threading.Thread.__init__(self)
        self.name = name
        self.threadID = threadID
        self.encryption_suite = encryption_suite
        self.s = s
        self.func = func
        self.buffer_size = buffer_size
        self.stop = threading.Event()
        
    def run(self):
        #print "Starting " + self.name
        self.func(self, self.encryption_suite, self.s, self.buffer_size)
