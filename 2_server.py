
# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_DGRAM
import pickle
import sys
import struct

def main():

    f=open('output','w')

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind(('', 12345))

    while True:
        msg, peer = sock.recvfrom(1024)
        f.writelines(struct.unpack('=2B2IH',msg)
        f.close()
        sock.close()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
