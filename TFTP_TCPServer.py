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
       
        with open (rrq[1].decode(),'r') as readfile: 
                   
            
            while True:                       
                sent_bytes=readfile.read(512)                      
                
                last_packet = send_data(child_sock,block,sent_bytes)
                   
                block=block+1
                    
                if(len(sent_bytes)<512):
                    break 
                               
            
    except FileNotFoundError:
        
        
        message='File Not Found'
            
        send_err(child_sock,message)

        

            

def write(sock,msg,client):
    
    message=''
    
    try:
        wrq=unpack_RRQWRQ(msg)
        
        with os.fdopen(os.open(wrq[1], os.O_CREAT | os.O_EXCL | os.O_WRONLY),'w') as writefile:
        
            confirm_packet=authentification_message(4)
            
            sock.send(confirm_packet)
            
            while True:        
                    
                msg = sock.recv(512)

                write_message = unpack_data(msg)

                if(write_message[0]==3):    

                    #writefile.write(write_message[2].decode("utf-8"))
                    message = message + write_message[2].decode("utf-8")
                    
                    if(len(write_message[2])<512):
                        
                        break
            
            writefile.write(message)
        

    except FileExistsError:
        
        confirm_packet=authentification_message(5)
        sock.send(confirm_packet)
        
        message='File Already Exists'
        
        send_err(sock,message)

        

        

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
                #_thread.start_new_thread(client_handle,(child_socket,client,n))
    
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
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block , str.encode(data))
    sock.send(packed_data)  
    return packed_data

def send_err(child_sock,message):
    error_packet=struct.pack(f'!2H{len(message)}sB',5,1,str.encode(message),0)
    child_sock.send(error_packet)

def unpack_data(packet):
    unpacked_data = struct.unpack(f'!2H{len(packet)-4}s', packet)
    return unpacked_data 

def authentification_message(code):   
    authoritation=struct.pack(f'!H',code)
    return authoritation
    

if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
