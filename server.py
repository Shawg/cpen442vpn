import socket
from Crypto.Cipher import AES
from Crypto.Random import random
from Crypto.Util import number
from Crypto.Hash import SHA256
from Crypto import Random
from ModularExponentiation import fastPow
from time import sleep

def run(tcp_ip, tcp_port, buffer_size, verification_secret):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tcp_port))
    s.listen(1)

    conn, addr = s.accept()
    print 'Connection address:', addr

    #establish Shared key
    # shared_base = random.getrandbits(8)
    shared_base = 7
    # shared_prime = number.getPrime(128)
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

    print "IV: "+str(IV)
    conn.send(str(IV))
    sleep(0.05)

    public_client = int(conn.recv(buffer_size))
    print "client DH public: " + str(public_client)

    print "server DH secret:  "+ str(server_secret)
    print "Calculatin key, this may take a minute..."
    DH_key = pow(public_client, server_secret, shared_prime)
    DH_key = SHA256.new(str(DH_key))
    print "DH key: "+DH_key.hexdigest()

    encryption_suite = AES.new(DH_key.digest(), AES.MODE_ECB)
    #Authenticate client
    print "Verifying the client"
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
        data = encryption_suite.decrypt(data)
        if data == "q":
            conn.close()
            return
        print "received data:", data
