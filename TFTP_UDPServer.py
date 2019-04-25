#!/usr/bin/python3.7
import struct
import sys
import socket
import traceback
import time
import os

def read(sock,packet,client):

    block=0
    recieved=False
    file_content = ''
    count=0

    rrq=unpack_RRQWRQ(packet)

    try:

        with open(rrq[1],'r') as readfile:
            file_content = readfile.read().encode()

    except OSError:
        message='File Not Found'
        sock.sendto(struct.pack(f'!2H{len(message)}sB',5,1,message.encode(),0) , client)
        with open('log.txt','a') as logfile:    
            logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {rrq[1]} , status: {message}')
    
        
    while count < len(file_content) :

        if not recieved: 
            
            block=block+1 

            sent_bytes= file_content[count:512*block]
            
            count = count + len(sent_bytes)

            last_packet = send_data(client,sock,block,sent_bytes)

            try:

                msg, client =sock.recvfrom(512)

                if len(sent_bytes) < 512 :
                    with open('log.txt','a') as logfile:    
                        logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {rrq[1]} , status: succesfull')
                    break
            except socket.error:
                recieved=True
            
        else:

            sock.sendto(last_packet,client)
            
            try:
                msg, client =sock.recvfrom(512)
                recieved = False
                if len(sent_bytes) < 512 :
                    with open('log.txt','a') as logfile:    
                        logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {rrq[1]} , status: succesfull')
                    break
            except socket.error:
                recieved=True


def write(sock,packet,client):

    block=0
    recieved=False
    last_message = False
    file_content=''

    wrq=unpack_RRQWRQ(packet)

    try:

        with os.fdopen(os.open(wrq[1], os.O_CREAT | os.O_EXCL | os.O_WRONLY),'w') as writefile:

            while True:

                if not recieved: 

                    block = block + 1

                    last_packet=send_ack(client,sock,block)

                if last_message:
                    with open('log.txt','a') as logfile:    
                        logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: write {wrq[1]} , status: succesfull')
                    break

                try:
                    msg, client =sock.recvfrom(516)
                    if len(msg) < 516 :
                        last_message=True
                
                except socket.error:
                    recieved=True
                    continue

                data=unpack_data(msg)
                file_content= file_content + (data[2].decode())
                recieved=False

            writefile.write(file_content)

    except OSError:
        message='File already exists'
        sock.sendto(struct.pack(f'!2H{len(message)}sB',5,1,str.encode(message),0) , client)
        with open('log.txt','a') as logfile:    
            logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {wrq[1]} , status: {message}')
    



def main(*args,**kwargs):

    print (sys.argv)

    print (len(sys.argv))

    if(sys.argv[1]!= '-p' ):
            raise Exception("Introduce the arguments in the correct format -> python3 TFTP_UDPClient.py -s 'server direction' -p 'port number' ")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        
        configure_socket(sock,sys.argv[2],999999)

        while True:

            try:

                msg, client =sock.recvfrom(516)

                code = unpack_packetcode(msg)
                
                if(code==1):
                    read(sock,msg,client)
                if(code==2):
                    write(sock,msg,client)
            except IOError:
                pass


def configure_socket(sock,port,maxtimeout):
    timeval = struct.pack('LL',0,maxtimeout)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
    sock.bind(('',int(port)))

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]

def send_data(destination,sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block+1 , data)
    sock.sendto(packed_data, destination)  
    return packed_data

def send_ack(destination, sock, block):
    packed_ack = struct.pack('!2H', 4 , block) 
    sock.sendto( packed_ack , destination )
    return packed_ack
 
def unpack_data(packet):
    unpacked_data = struct.unpack(f'!2H{len(packet)-4}s', packet)
    return unpacked_data

def unpack_RRQWRQ(packet,decode_mode='netascii'):
    request = struct.unpack(f"!H{len(packet)-12}sB{len(decode_mode)}sB",packet)
    return request


if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
        
