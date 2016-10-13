#!/usr/bin/env python

import socket


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

def client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()

    print "received data:", data

def server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((TCP_IP, TCP_PORT))
    s.listen(1)

    conn, addr = s.accept()
    print 'Connection address:', addr
    while 1:
        data = conn.recv(BUFFER_SIZE)
        if not data: break
        print "received data:", data
        conn.send(data)  # echo
    conn.close()

def main():
    cliServ = 9999
    print "Please enter 0 if this is the server and 1 if this is the client"
    while 1:
        cliServ = input()
        if cliServ == 1 or cliServ == 0:
            break
        print "invalid input"
        print "Please enter 0 if this is the server and 1 if this is the client"

    if cliServ == 0:
        server()
    else:
        client()
main()



