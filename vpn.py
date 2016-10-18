#!/usr/bin/env python

import socket
import server
import client

def main():
    TCP_IP = '127.0.0.1'
    BUFFER_SIZE = 1024
    cliServ = 9999
    print "Please enter 0 if this is the server and 1 if this is the client"
    while 1:
        cliServ = input()
        if cliServ == 1 or cliServ == 0:
            break
        print "invalid input"
        print "Please enter 0 if this is the server and 1 if this is the client"

    print "Please specify the port to run on"
    # TCP_PORT = int(raw_input())
    TCP_PORT = 9045

    print "Please enter your shared secret"
    SHARED_SECRET = raw_input()
    # SHARED_SECRET = "foo"

    if cliServ == 0:
        server.run(TCP_IP, TCP_PORT, BUFFER_SIZE, SHARED_SECRET)
    else:
        client.run(TCP_IP, TCP_PORT, BUFFER_SIZE, SHARED_SECRET)

main()



