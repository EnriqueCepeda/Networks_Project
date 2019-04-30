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
       
        with open (rrq[1].decode(),'rb') as readfile: 
                   
            message='File Has Found'
            
            confirm_packet=authentification_message(4,message,2)
            
            child_sock.send(confirm_packet)
            
            while True:                       
                
                sent_bytes=readfile.read(512)                      
                
                last_packet = send_data(child_sock,block,sent_bytes)
                   
                block=block+1
                    
                if(len(sent_bytes)<512):
                    break 
                               
            
    except FileNotFoundError: 
        
        message='File Not Found'
        
        confirm_packet=authentification_message(5,message,1)
            
        child_sock.send(confirm_packet)
            

def write(sock,msg,client):
    
    message=''        
    try:
        wrq=unpack_RRQWRQ(msg)
        
        with os.fdopen(os.open(wrq[1].decode(), os.O_CREAT | os.O_EXCL | os.O_WRONLY),'wb') as writefile:
        
            secure_message='File Not Exists'
            
            confirm_packet=authentification_message(4,secure_message,2)
            
            sock.send(confirm_packet)
            
            while True:        
                    
                msg = sock.recv(516)

                write_message = unpack_data(msg)

                if(write_message[0]==3):    
                    
                    
                    writefile.write( write_message[2])
                    
                    
                    if(len(write_message[2])<512):
                        
                        break
            
            
        

    except FileExistsError: 
        
        message='File Already Exists'
        
        confirm_packet=authentification_message(5,message,1)
        
        sock.send(confirm_packet)
        

        

def client_handle(child_sock,client,n):
    logfile_content=''

    with open('log.txt','a') as logfile:
        while True:
            
            try:
        
                msg =child_sock.recv(516) 
        
                code = unpack_packetcode(msg)
                
                if(code==1):
                    logfile.write(f'read request, time:{time.asctime()}\n')
                    read(child_sock,msg,client)
                if(code==2):
                    logfile.write(f'write request, time:{time.asctime()}\n')
                    write(child_sock,msg,client)            
            except Exception:
                print("Client {} disconnected".format(n))
                child_sock.close()
                break
                    
    
        logfile.write(logfile_content)
    logfile.close()    

def main(*args,**kwargs):
    if(sys.argv[1]!= '-p' ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPServer.py -p 'port number' ")
    
    try: 
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            port=int(sys.argv[2])
            sock.bind(('',port))
            sock.listen(5)
            n=0     
            while 1:
                
                child_socket, client= sock.accept()
                    
                n = n + 1
                    
                print("Client {} conected {}".format(n,client))
                
                client_connection = threading.Thread(target=client_handle,args=(child_socket,client,n))

                client_connection.start()
                
    
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

def authentification_message(code,message,code2):   
    authoritation=struct.pack(f'!2H{len(message)}sB',code,code2,str.encode(message),0)
    return authoritation
    

if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
