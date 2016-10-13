import socket

def run(tcp_ip, tcp_port, buffer_size, verification_secret):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((tcp_ip, tcp_port))
    s.listen(1)

    conn, addr = s.accept()
    print 'Connection address:', addr
    data = conn.recv(buffer_size)
    if data != verification_secret:
        print "THEYRE HACKIN US"
    while 1:
        data = conn.recv(buffer_size)
        if not data: break
        print "received data:", data
        conn.send(data)  # echo
    conn.close()
