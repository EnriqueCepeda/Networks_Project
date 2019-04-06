#!/usr/bin/python3.7
import struct
import sys
import socket
import traceback
import time

def read(sock,unpacked_code,client):
    
    block=0
    recieved=False

    try:

        with open(unpacked_code[0],'r') as readfile:
        
            while True:
                
                try:

                    
                    
                    if not recieved: 


                        sent_bytes= readfile.read(512) 

                        last_packet = struct.pack(f'!2H{len(sent_bytes)}s',3,block,str.encode(sent_bytes))

                        block=block+1 #incrementamos el block number por cada mensaje que el servidor envía

                        sock.sendto(last_packet, client) #MANDAMOS LA ESTRUCTURA DEL LOS DATOS QUE LEEMOS DEL FICHERO

                        msg, client =sock.recvfrom(512) #EL SERVIDOR RESCIBE EL ACK DEL CLIENTE
                        
                        unpacked_ack=struct.unpack('=2H',msg)
                        
                        print(unpacked_ack)
                        
                    else:

                        sock.sendto(last_packet,client)
                        msg, client =sock.recvfrom(512)
                        recieved = False

                except socket.error as socketerror:
                    print(socketerror.strerror)
                    recieved=True
                
                else:
                    if(len(sent_bytes) < 512 ):
                        break

    except OSError:
        message='File Not Found'
        sock.sendto(struct.pack(f'=2H{len(message)}sH',5,1,str.encode(message),0) , client)


def write(sock,unpacked_code,client):

    block=0
    recieved=False

    try:

        with open(unpacked_code[0],'x') as writefile:
        
            while True:
                
                try:

                    
                    if not recieved: 

                        last_packet = struct.pack(f'!2H',4, block)

                        block = block + 1
                        
                        sock.sendto(last_packet, client) #MANDAMOS LA ESTRUCTURA DEL LOS DATOS QUE LEEMOS DEL FICHERO

                        msg, client =sock.recvfrom(512) #EL SERVIDOR RESCIBE EL ACK DEL CLIENTE

                        write_message=struct.unpack(f'2H{len(msg)-4}',msg)
                        print(write_message)
                        recieved_bytes=writefile.write(write_message[2])
                        
                        
                    else:

                        sock.sendto(last_packet,client)
                        msg, client =sock.recvfrom(512)
                        write_message=struct.unpack(f'2H{len(msg)-4}',msg)
                        recieved_bytes=writefile.write(write_message[2])
                        
                        recieved = False

                except socket.error as socketerror:
                    print(socketerror.strerror)
                    recieved=True
                
                else:
                    if(len(recieved_bytes) < 512 ):
                        break

    except OSError:
        message='File already exists'
        sock.sendto(struct.pack(f'=2H{len(message)}sH',5,1,str.encode(message),0) , client)


def main(*args,**kwargs):

    if(sys.argv[1]!= '-p' ):
            raise Exception("Introduce the arguments in the correct format -> python3 TFTP_UDPClient.py -s 'server direction' -p 'port number' ")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        
        timeval = struct.pack('LL',0,999999)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)
        port = sys.argv[2]
        sock.bind(('',int(port)))

    
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



if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
      pass
    except Exception:
        traceback.print_exc()
        
