#!/usr/bin/env python

import socket
import server
import client


TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE = "Hello, World!"

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
        server.run(TCP_IP, TCP_PORT, BUFFER_SIZE)
    else:
        client.run(TCP_IP, TCP_PORT, BUFFER_SIZE)
main()



