#-*- coding: utf-8 -*-

import socket
import sys
import struct
import traceback
import io
import time
import os
from pathlib import Path


def write(sock,*args,**kwargs):
    
    if(len(args)!=5):
        print(args)
        raise Exception("Please introduce the arguments in the correct format -> WRITE 'filename'")
    
    ip=args[2]
    port=args[3]
    file_name=args[0]
                 
    try:   
            
        with open(f'TCP_CLIENT/{file_name}','rb',) as file_read:
                
            last_packet=sendRRQWRQ(2,file_name,sock)
    
            block = 0          
                                    
            ack_packet = sock.recv(516)
                            
            code=unpack_packetcode(ack_packet)       
                    
            if(code==4):    
                                
                while True:                                
                                        
                    sent_bytes=file_read.read(512)
                                    
                    last_packet = send_data(sock,block,sent_bytes)

                    if(block == 65535):
                        block=1            
                    else: 
                        block=block+1   
                    
                    if(len(last_packet)<512):
                                        
                       break   
                                
                            
            else:             
                                
                unpack_err(ack_packet)
            
    except FileNotFoundError:
        
        print("This file doesn't exist")
        
def read(sock,*args,**kwargs):
    
    if(len(args)!=5):
        print(args)
        raise Exception("Please introduce the arguments in the correct format -> READ 'filename'")
    
    file_name=args[0]
    
    last_packet=sendRRQWRQ(1,file_name,sock)
    
    with open(f'TCP_CLIENT/{file_name}','wb',) as file_write:        
        while True:
                                    
            packet_data = sock.recv(516)                   
                            
            code=unpack_packetcode(packet_data)

            if(code==3):  


                unpacked_data = unpack_data(packet_data)

                file_write.write(unpacked_data[2])
                        
                if(len(unpacked_data[2])<512):

                   print("que pasó")                
                   break
                                            
            else:                 
                        
                unpack_err(packet_data)
                    
                break
                
                    

def end_program(sock,*args,**kwargs):
    raise KeyboardInterrupt("Bye,good to see you")

functions={
    "quit":end_program,
    "read":read,
    "write":write
}

def main(*args,**kwargs):
    
    if(sys.argv[1]!='-s'or sys.argv[3]!='-p' or len(sys.argv) != 5 ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPClient.py -s 'server direction' -p 'port number' ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.connect((sys.argv[2],int(sys.argv[4])))
            while True:
                command = input('TFTP@TCP> ')
                arguments = command.split() + sys.argv[1:]
                functions[arguments[0]](sock,*arguments[1:])
        except KeyboardInterrupt:
            sock.shutdown()
            print("\nBye, good to see you")
        except Exception as error:
            print(error)
        

            

def sendRRQWRQ(code,file_name,sock,encode_mode='netascii'):
    last_packet=struct.pack(f"!H{len(file_name)}sB{len(encode_mode)}sB", code ,str.encode(file_name),0,str.encode(encode_mode),0)
    sock.send(last_packet)
    return last_packet

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]

def unpack_data(packet):
    unpacked_data = struct.unpack(f'!2H{len(packet)-4}s', packet)
    return unpacked_data

def send_data(sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block , data)
    sock.send(packed_data)  
    return packed_data

def unpack_err(packet):
    unpacked_err = struct.unpack(f'!2H{len(packet)-5}sB', packet)
    print(f"Error number:{unpacked_err[1]} Message:{unpacked_err[2].decode()}")


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        (str(e))
