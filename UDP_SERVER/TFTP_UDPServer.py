#!/usr/bin/python3.7
import struct
import sys
import socket
import traceback
import time
import os

def read(sock,unpacked_code,client):

    block=0
    recieved=False
    file_content = ''
    count=0


    try:

        with open(unpacked_code[0],'r') as readfile:
            file_content = readfile.read().encode()

    except OSError:
        message='File Not Found'.encode()
        sock.sendto(struct.pack(f'!2H{len(message)}sB',5,1,message,0) , client)
    
        
    while count < len(file_content) :

        if not recieved: 
            
            block=block+1 

            sent_bytes= file_content[count:512*block]
            
            count = count + len(sent_bytes)

            last_packet = struct.pack(f'!2H{len(sent_bytes)}s',3,block,sent_bytes)

            sock.sendto(last_packet, client)

            try:

                msg, client =sock.recvfrom(512)
                if len(sent_bytes) < 512 :
                    break
            except socket.error:
                recieved=True
            
        else:

            sock.sendto(last_packet,client)
            
            try:
                msg, client =sock.recvfrom(512)
                recieved = False
                if len(sent_bytes) < 512 :
                    break
            except socket.error:
                recieved=True


def write(sock,unpacked_code,client):

    block=0
    recieved=False
    last_message = False
    file_content=''

    try:

        with os.fdopen(os.open(unpacked_code[0], os.O_CREAT | os.O_EXCL | os.O_WRONLY),'w') as writefile:

            while True:

                if not recieved: 

                    block = block + 1

                    last_packet = struct.pack(f'!2H',4, block)
                    
                    sock.sendto(last_packet, client) 

                if last_message:break

                try:
                    msg, client =sock.recvfrom(516)
                    if len(msg) < 516 :
                        last_message=True
                
                except socket.error:
                    recieved=True
                    continue

                write_message=struct.unpack(f'!2H{len(msg)-4}s',msg)
                file_content= file_content + (write_message[2].decode())
                recieved=False

            writefile.write(file_content)

    except OSError:
        message='File already exists'
        sock.sendto(struct.pack(f'!2H{len(message)}sB',5,1,str.encode(message),0) , client)
    



def main(*args,**kwargs):

    if(sys.argv[1]!= '-p' ):
            raise Exception("Introduce the arguments in the correct format -> python3 TFTP_UDPClient.py -s 'server direction' -p 'port number' ")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        
        timeval = struct.pack('LL',0,999999)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        port = sys.argv[2]
        sock.bind(('',int(port)))
        logfile_content=''


                
        with open('log.txt','a') as logfile:    
            
            while True:

                try:

                    msg, client =sock.recvfrom(516)

                    unpacked_code = struct.unpack(f"!H{len(msg)-12}sB{len('netascii')}sB",msg)
                    
                    if(unpacked_code[0]==1):
                        logfile.write(f'read file:{unpacked_code[1].decode()}, served-client:{client}, time:{time.asctime()}\n')
                        read(sock,unpacked_code[1:],client)
                    if(unpacked_code[0]==2):
                        logfile.write(f'write file:{unpacked_code[1].decode()}, served-client:{client}, time:{time.asctime()}\n')
                        write(sock,unpacked_code[1:],client)
                except IOError:
                    pass

        logfile.write(logfile_content)



if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        
