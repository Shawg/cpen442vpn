import socket
import threading
import sys
import binascii
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from Crypto.Hash import SHA256
from Crypto.Hash import MD5
from time import sleep

exitFlag = 0
sendCounter = 0
recvCounter = 0

def run(tcp_ip, tcp_port, buffer_size, verification_secret):
    global exitFlag
    global sendCounter
    global recvCounter

    shared_prime = 32317006071311007300714876688669951960444102669715484032130345427524655138867890893197201411522913463688717960921898019494119559150490921095088152386448283120630877367300996091750197750389652106796057638384067568276792218642619756161838094338476170470581645852036305042887575891541065808607552399123930385521914333389668342420684974786564569494856176035326322058077805659331026192708460314150258592864177116725943603718461857357598351152301645904403697613233287231227125684710820209725157101726931323469678542580656697935045997268352998638215525166389437335543602135433594980054651204334503069401734924365973579369279
    shared_base = 147
    client_secret = random.getrandbits(1024)
    IV = Random.new().read(16)

    shared_key = SHA256.new(verification_secret)
    auth_suite = AES.new(shared_key.digest(), AES.MODE_CBC, IV)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((tcp_ip, tcp_port))

    #Authenticate server
    nonce = str(random.getrandbits(128))
    s.send("client$$"+nonce+"$$"+IV)

    resp = s.recv(buffer_size)
    server_nonce, encrypted, buff = resp.split('$$')
    encrypted = auth_suite.decrypt(encrypted)
    name, resp_nonce, public_server_dh, buff = encrypted.split('$$')
    if (name != "server") or (resp_nonce != nonce):
        print "THEYRE HACKIN US"
        print "abort abort abort"
        s.close()
        return

    public_client_dh = pow(shared_base, client_secret, shared_prime)

    message = "client$$"+server_nonce+'$$'+str(public_client_dh)+'$$'
    while len(message) % 16 != 0:
        message = message+'0'
    message = auth_suite.encrypt(message)
    message = message+'$$'
    while len(message) % 16 != 0:
        message = message+'0'
    s.send(message)

    print "Shared prime: "+str(shared_prime)
    print "Public server value: "+str(public_server_dh)
    print "Public client value: "+str(public_client_dh)
    print "Private client value: "+str(client_secret)

    print "Calculatin key, this may take a minute..."
    DH_key = pow(int(public_server_dh), client_secret, shared_prime)
    DH_key = SHA256.new(str(DH_key))
    print "DH key: "+DH_key.hexdigest()

    # set up encryption
    IV = Random.new().read(16)
    s.send(IV)
    encryption_suite = AES.new(DH_key.digest(), AES.MODE_CBC, IV)
    recvCounter = long(s.recv(buffer_size))
    sendCounter = long(s.recv(buffer_size))
    print "send counter: "+str(sendCounter)
    print "recv counter: "+str(recvCounter)

    # set up sending and receiving threads
    sender = myThread(1, "sendThread", encryption_suite, s, send, buffer_size)
    receiver = myThread(2, "recvThread", encryption_suite, s, recv, buffer_size)
    sender.deamon = 1
    receiver.deamon = 1
    sender.start()
    receiver.start()

    while not exitFlag:
        sleep(1)
        
    s.close()

def recv(name, encryption_suite, s, buffer_size):
    global exitFlag
    global recvCounter
    
    while not exitFlag:
        data = s.recv(buffer_size)
        original = data
        data = encryption_suite.decrypt(data)
        
	#INTEGRITY CHECK
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
            print "the server is off, press Enter to quit"
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
        self.stop = threading.Event()
        
    def run(self):
        #print "Starting " + self.name
        self.func(self, self.encryption_suite, self.s, self.buffer_size)
