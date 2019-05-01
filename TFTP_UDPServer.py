#!/usr/bin/python3.7
import struct
import sys
import socket
import traceback
import time
import os

def read(sock,packet,client):

    block=0
    received=False
    file_content = ''
    continueretransmissions=0
    count_bytes=0


    rrq=unpack_RRQWRQ(packet)

    print(rrq[1].decode())

    try:

        with open(f'UDP_SERVER/{rrq[1].decode()}','r') as readfile:
            file_content = readfile.read().encode()

    except OSError:
        message='File Not Found'
        sock.sendto(struct.pack(f'!2H{len(message)}sB',5,1,message.encode(),0) , client)
        with open('log.txt','a') as logfile:    
            logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {rrq[1]} , status: {message} ")
            logfile.write("\n")
    
        
    while count_bytes <= len(file_content) and continueretransmissions < 10 :

        if not received: 

            continueretransmissions = 0 

            sent_bytes= file_content[count_bytes:512*(block+1)]
            print(len(sent_bytes))
            
            count_bytes = count_bytes + len(sent_bytes)

            last_packet = send_data(client,sock,block,sent_bytes)

            block=block+1 

            try:

                msg, client =sock.recvfrom(512)
                if unpack_packetcode(msg) != 4:
                    received=True
                    continue

                if len(sent_bytes) < 512 :
                    with open('log.txt','a') as logfile:    
                        logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {rrq[1]} , status: succesfull \n")
                    break
            except socket.error:
                print("socket_error")
                received=True
                continueretransmissions= continueretransmissions + 1
            
        else:

            sock.sendto(last_packet,client)
            
            try:
                msg, client =sock.recvfrom(512)
                if unpack_packetcode(msg) != 4:
                    received=True
                    continue

                received = False

                if len(sent_bytes) < 512 :
                    with open('log.txt','a') as logfile:    
                        logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {rrq[1]} , status: succesfull \n')
                    break
            except socket.error:
                received=True
                continueretransmissions= continueretransmissions + 1


def write(sock,packet,client):

    block=0
    received=False
    last_message = False
    file_content=''
    continueretransmissions=0

    wrq=unpack_RRQWRQ(packet)
    print(f'UDP_SERVER/{wrq[1].decode()}')

    try:

        with os.fdopen(os.open(f'UDP_SERVER/{wrq[1].decode()}', os.O_CREAT | os.O_EXCL | os.O_WRONLY),'w') as writefile:

            while continueretransmissions<10:

                if not received: 

                    continueretransmissions=0

                    last_packet=send_ack(client,sock,block)

                    block = block + 1
                
                else:
                    sock.sendto(last_packet,client)

                if last_message:
                    with open('log.txt','a') as logfile:    
                        logfile.write(f'host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: write {wrq[1]} , status: succesfull \n')
                    break

                try:

                    msg, client =sock.recvfrom(516)
                    #if unpack_packetcode(msg) != 3:
                    #    received = True
                    #    continue

                    if len(msg) < 516 :
                        last_message=True
                
                except socket.error:
                    received=True
                    continueretransmissions = continueretransmissions + 1
                    continue

                data=unpack_data(msg)
                file_content= file_content + (data[2].decode())
                received=False

            writefile.write(file_content)

    except OSError as e:
        print(e.errno)
        message='File already exists'
        sock.sendto(struct.pack(f'!2H{len(message)}sB',5,1,str.encode(message),0) , client)
        with open('log.txt','a') as logfile:    
            logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.localtime()} , request: read {wrq[1]} , status: {message}\n")
    



def main(*args,**kwargs):

    if(sys.argv[1]!= '-p' ):
            raise Exception("Introduce the arguments in the correct format -> python3 TFTP_UDPClient.py -p 'port number' ")

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
        
