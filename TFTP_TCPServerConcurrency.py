#!/usr/bin/python3.7
import struct
import sys
import socket
import traceback
import io 
import _thread
import time
import threading
import os

                  
def read(child_sock,msg,client):
    
    block = 0

    rrq=unpack_RRQWRQ(msg)

    try:
       
        with open(f'TCP_SERVER/{rrq[1].decode()}','rb') as readfile:
                   
            message='File Has Found'      
            
            while True:                       
                
                sent_bytes=readfile.read(512)            
                
                packed_data=send_data(child_sock,block,sent_bytes)                
                 
                if(block == 65535):
                    block=1            
                else: 
                    block=block+1
                    
                if(len(sent_bytes)<512):
                    break 

                               
    except OSError:    
        message='File Not Found'
                       
        error_packet=struct.pack(f'!2H{len(message)}sB',5,1,str.encode(message),0)
        
        child_sock.send(error_packet)
            

def main(*args,**kwargs):
    if(sys.argv[1]!= '-p' ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPServer.py -p 'port number' ")
    
    try: 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port=int(sys.argv[2])
            sock.bind(('',port))
            sock.listen(5)
            
            i=1
            while True:     
                          
                child_socket, client= sock.accept()

                print("Client {} conected {}".format(i,client))

                msg =child_socket.recv(516)
                      
                code = unpack_packetcode(msg)
                
                if(code==1):
                                      
                    read(child_socket,msg,client)   
                
                i+=1     
    
    except socket.error:   
      print('Fail creating the socket')
      sys.exit(1)         

def unpack_RRQWRQ(packet,decode_mode='netascii'):
    request = struct.unpack(f"!H{len(packet)-12}sB{len(decode_mode)}sB",packet)
    return request

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]

def send_data(sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block , data)
    sock.send(packed_data)  
    return packed_data

def unpack_data(packet):
    unpacked_data = struct.unpack(f'!2H{len(packet)-4}s', packet)
    return unpacked_data 

  

if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
