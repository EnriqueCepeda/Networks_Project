#!/usr/bin/python3.7
import struct
import pickle
import sys
from socket import *
import traceback
import io 
from _thread import *
import time
from threading import *
                  
def read(child_sock,unpacked_code,client):
    block=0
    try:
        with open (unpacked_code[1].decode(),'r') as readfile: 
             
            c
            
            while True:                       
                sent_bytes=readfile.read(512)                      
                
                last_packet = struct.pack(f'=2H{len(sent_bytes)}s',3,block,str.encode(sent_bytes))
                   
                block=block+1
                       
                child_sock.send(last_packet) 
                    
                if(len(sent_bytes)<512):
                    break 
                               
            
    except FileNotFoundError:
        
        
        message='File Not Found'
            
        error_packet=struct.pack(f'=2H{len(message)}sB',5,1,str.encode(message),0)
            
        child_sock.send(error_packet)

        

            

def write(sock,unpacked_code,client):
    try:
        
        with open(unpacked_code[1].decode(),'x') as writefile:
        
            confirm_packet=struct.pack(f'=H',4)
            print(confirm_packet[0])
            sock.send(confirm_packet)
            
            while True:        
                    
                msg = sock.recv(512)

                print(msg)
                write_message = struct.unpack(f'!2H{len(msg)-4}s',msg)

                if(write_message[0]==3):    

                    writefile.write(write_message[2].decode("utf-8"))

                    #podemos mandar una mensaje de seguimiento
                    if(len(write_message[2])<512):
                        break
    
    except FileExistsError:
        
        confirm_packet=struct.pack(f'=H',5)
        print(confirm_packet[0])    
        sock.send(confirm_packet)
        
        message='File Already Exists'
        
        error_packet=struct.pack(f'=2H{len(message)}sB',5,2,str.encode(message),0)
               
        sock.send(error_packet)

        

        

def client_handle(child_sock,client,n):
    logfile_content=''
    with open('log.txt','a') as logfile:
        while True:
            try:
            
                print("Client conected: ",n,client)
        
                msg =child_sock.recv(516) 
        
                unpacked_code = struct.unpack(f"!H{len(msg)-12}sB{len('netascii')}sB",msg)
                print(unpacked_code[0])
                if(unpacked_code[0]==1):
                    logfile.write(f'read file:{unpacked_code[1].decode()}, served-client:{client}, time:{time.asctime()}\n')
                    read(child_sock,unpacked_code,client)
                if(unpacked_code[0]==2):
                    logfile.write(f'write file:{unpacked_code[1].decode()}, served-client:{client}, time:{time.asctime()}\n')
                    write(child_sock,unpacked_code,client)
            except IOError:
                pass    
    logfile.write(logfile_content)

def main(*args,**kwargs):
    try: 
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        port=int(sys.argv[1])
        sock.bind(('',port))
        sock.listen(5)
        n=0     
        while 1:
        
            child_socket, client= sock.accept()
            
            n=n+1
            
            start_new_thread(client_handle,(child_socket,client,n))

    except socket.error:   
        print('Failed to create socket')
        sys.exit() 
    
if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
      pass
    
    except Exception:
        traceback.print_exc()
