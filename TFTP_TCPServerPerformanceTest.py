#!/usr/bin/python3.7
import struct
import sys
import socket
import traceback
import _thread
import time
import threading
import os

                  
def read(sock,msg,client):
    
    block = 0

    rrq=unpack_RRQWRQ(msg)

    try:
       
        with open(f'TCP_SERVER/{rrq[1].decode()}','rb') as readfile:
                   
            message='File Has Found'
            
            with open('TCP_SERVER/log.txt','a') as logfile:
        
                logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.asctime()} , request: READ {rrq[1].decode()} , status: {message} ")
        
                logfile.write("\n")
        
            
            while True:                 
                
                sent_bytes=readfile.read(512)       
                
                packed_data=send_data(sock,block,sent_bytes)                
            
                block= (block+1) % 65535 
                    
                if(len(sent_bytes)<512):
                    break 

                               
    except OSError:    
        message='File Not Found'

        with open('TCP_SERVER/log.txt','a') as logfile:

            logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.asctime()} , request: READ {rrq[1].decode()} , status: {message} ")
            logfile.write("\n")

        send_err(message,sock,1)

   
def write(sock,msg,client):
    
    block = 0
    
    try:
        
        wrq=unpack_RRQWRQ(msg)
              
        
        with os.fdopen(os.open(f'TCP_SERVER/{wrq[1].decode()}',os.O_CREAT | os.O_EXCL | os.O_WRONLY),'wb') as writefile:
            
                        
            secure_message='File Not Exists'

            with open('TCP_SERVER/log.txt','a') as logfile:
        
                
                logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.asctime()} , request: WRITE {wrq[1].decode()} , status: {secure_message} ")
            
                logfile.write("\n")
               
            ack=send_ack(sock,block)       
            
            while True:        
                    
                msg = sock.recv(516)     
                
                write_message = unpack_data(msg)
                         
                writefile.write(write_message[2])
                    
                if(len(write_message[2])<512):
                        
                    break 
       
    except OSError:
        
        message='File Already Exists'

        with open('TCP_SERVER/log.txt','a') as logfile:
        
            logfile.write(f"host: {client[0]} , port: {client[1]} , time: {time.asctime()} , request: WRITE {wrq[1].decode()} , status: {message} ")
        
            logfile.write("\n")

        send_err(message,sock,2)
        
        

        

def client_handle(child_sock,client,n):
               
    while True:
        
        msg =child_sock.recv(516) 

        if(len(msg)==0):
            break

        code = unpack_packetcode(msg)
        
        if(code==1):
            time_start_read=time.time()                                       
            read(child_sock,msg,client)
            time_end_read=time.time()
            print(f"Time taken by READ mode is : {round((time_end_read-time_start_read)*1000,3)} miliseconds")
            
        if(code==2):
            
            time_start_write=time.time()                                 
            write(child_sock,msg,client)            
            time_end_write=time.time()
            print(f"Time taken by WRITE mode is : {round((time_end_write-time_start_write)*1000,3)} miliseconds")
                
    print("Client {} disconnected".format(client))

    child_sock.close()


def main(*args,**kwargs):
    if(sys.argv[1]!= '-p' ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPServer.py -p 'port number' ")
    
    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            port=int(sys.argv[2])
            
            sock.bind(('',port))
            
            sock.listen(5)
            
            n_client = 0  

            socket_array=[]   

            try:
                    
                while 1:
                    
                    child_socket, client= sock.accept()
                        
                    n_client = n_client + 1
                        
                    print("Client {} conected {}".format(n_client,client))
                    
                    client_connection = threading.Thread(target=client_handle,args=(child_socket,client,n_client),daemon=True)
                    socket_array.append((child_socket))
                    client_connection.start()
                
            except KeyboardInterrupt:
                for sock in socket_array:
                    sock.close()
                
    except socket.error:   
      print('Fail creating the socket, there is something wrong')
      sys.exit(1)    
    
def send_err(message,sock,code):
    packed_err = struct.pack(f'!2H{len(message)}sB',5,code,message.encode(),0)
    sock.send(packed_err)
    return packed_err   
        
def send_data(sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block , data)
    sock.send(packed_data)  
    return packed_data        
     

def unpack_RRQWRQ(packet,decode_mode='netascii'):
    request = struct.unpack(f"!H{len(packet)-12}sB{len(decode_mode)}sB",packet)
    return request

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]

def send_ack(sock, block):
    packed_ack = struct.pack('!2H', 4 , block) 
    sock.send(packed_ack)
    return packed_ack

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
