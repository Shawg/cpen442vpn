import socket
import threading
import sys
import binascii
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from Crypto.Hash import SHA256
from Crypto import Random
from Crypto.Hash import MD5
from time import sleep

exitFlag = 0
sendCounter = 0
recvCounter = 0

def run(tcp_ip, tcp_port, buffer_size, verification_secret):
    global sendCounter
    global recvCounter
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tcp_port))
    s.listen(1)

    conn, addr = s.accept()
    print 'Connection address:', addr

    #getting authenticated
    client_nonce = conn.recv(buffer_size)
    conn.send(SHA256.new(verification_secret+client_nonce).hexdigest())
    sleep(0.05)
    #Authenticate client
    print "Verifying the client"
    nonce = str(random.getrandbits(128))
    conn.send(nonce)
    challenge = SHA256.new(verification_secret+nonce).hexdigest()
    resp = conn.recv(buffer_size)

    if resp != challenge:
        print "THEYRE HACKIN US"
        print "abort abort abort"
        s.close()
        return

    #establish Shared key
    shared_base = random.getrandbits(8)
    # shared_base = 7
    # shared_prime = number.getStrongPrime(2048)
    shared_prime = 32317006071311007300714876688669951960444102669715484032130345427524655138867890893197201411522913463688717960921898019494119559150490921095088152386448283120630877367300996091750197750389652106796057638384067568276792218642619756161838094338476170470581645852036305042887575891541065808607552399123930385521914333389668342420684974786564569494856176035326322058077805659331026192708460314150258592864177116725943603718461857357598351152301645904403697613233287231227125684710820209725157101726931323469678542580656697935045997268352998638215525166389437335543602135433594980054651204334503069401734924365973579369279
    server_secret = random.getrandbits(1024)
    IV = Random.get_random_bytes(16)
    print "generating secret..."
    public_server = pow(shared_base, server_secret, shared_prime)

    print "Establishing a shared key"
    print "base "+ str(shared_base)
    conn.send(str(shared_base))
    sleep(0.05)

    print "prime "+ str(shared_prime)
    conn.send(str(shared_prime))
    sleep(0.05)

    print "server DH public:  "+ str(public_server)
    conn.send(str(public_server))
    sleep(0.05)

    # print "IV: "+str(IV)
    conn.send(str(IV))
    sleep(0.05)

    public_client = int(conn.recv(buffer_size))
    print "client DH public: " + str(public_client)
    print "server DH secret:  "+ str(server_secret)

    print "Calculatin key, this may take a minute..."
    DH_key = pow(public_client, server_secret, shared_prime)
    DH_key = SHA256.new(str(DH_key))
    print "DH key: "+DH_key.hexdigest()

    #Setup AES
    encryption_suite = AES.new(DH_key.digest(), AES.MODE_ECB)
    sendCounter = random.getrandbits(128)
    recvCounter = random.getrandbits(128)
    conn.send(str(sendCounter))
    conn.send(str(recvCounter))
    print "send counter: "+str(sendCounter)
    print "recv counter: "+str(recvCounter)

    # Set up sending and receiving threads
    sender = myThread(1, "sendThread", encryption_suite, conn, send, buffer_size)
    receiver = myThread(2, "recvThread", encryption_suite, conn, recv, buffer_size)
    sender.deamon = 1
    receiver.deamon = 1
    sender.start()
    receiver.start()

    while not exitFlag:
        sleep(1)

    conn.close()
    s.close()

def recv(name, encryption_suite, s, buffer_size):
    global exitFlag
    global recvCounter
    
    while not exitFlag:
        data = s.recv(buffer_size)
        original = data
        data = encryption_suite.decrypt(data)

        #take checksum from end of data and compare to
	#generated checksum of message 
	messagehash = data[len(data)-32:len(data)]
        data = data[0:(len(data)-32)]
	generatedhash = MD5.new()
	generatedhash.update(data)
	if generatedhash.hexdigest() != messagehash and data != "":
            print "CHECKSUM FAILED!!!!"

	while data.endswith('0'):
            data = data[:-1]

        # Check counter
        if data != "":
            counter = long(data.split("$$")[1])
            data = data.split("$$")[0]
            if counter != recvCounter:
                print "replay attack detected"
                print "abort abort abort"
                exitFlag = 1
                return            
        
        if data == "q":
            exitFlag = 1
            print "======================================================"
            print "the client has left, press Enter to quit"
            return
        if data != "":
            print "======================================================"
            print "receiving counter: "+str(recvCounter)
            print "encrypted stuff: "+binascii.hexlify(original)
            print "generated hash: " + generatedhash.hexdigest()
	    print "message hash: " + messagehash
	    print "received data:", data
            print "======================================================"
            print "what do you want to send? (send q to close connection)"
            recvCounter += 1

def send(name, encryption_suite, s, buffer_size):
    global exitFlag
    global sendCounter
    
    while not exitFlag:
        print "======================================================"
        print "what do you want to send? (send q to close connection)"
        message = raw_input()
        quit_message = message
        message = message + "$$" + str(sendCounter) + "$$"
        while len(message) % 16 != 0:
            message = message+'0'

        #INTEGRITY CHECK
        #generate checksum and append to data being sent
        messagehash = MD5.new()
        messagehash.update(message)
        message = message + messagehash.hexdigest()
	message = encryption_suite.encrypt(message)
        
        if quit_message == "q":
            s.send(message)
            exitFlag = 1
            return

        if not exitFlag and quit_message != "":
            print "sending counter = "+str(sendCounter)
            sendCounter += 1
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
    def run(self):
        #print "Starting " + self.name
        self.func(self, self.encryption_suite, self.s, self.buffer_size)
