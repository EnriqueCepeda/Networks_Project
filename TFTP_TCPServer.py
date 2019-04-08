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


def read(sock,unpacked_code,client):
    block=0
    try:
        
        with open (unpacked_code[1].decode(),'r') as readfile: 
           #Abrimos el archivo que hemos indicado en el cliente     
            while True:    
                                    
                                       
                sent_bytes=readfile.read(512)  
                    #Leemos los archivo del fichero    
                #if not sent_bytes:
                #    break        
                        
                last_packet = struct.pack(f'!2H{len(sent_bytes)}s',3,block,str.encode(sent_bytes))
                    #Este paquete contiene el codigo, el bloque y los datos necesarios   
                block=block+1
                        
                sock.send(last_packet) #MANDAMOS LA ESTRUCTURA DEL LOS DATOS QUE LEEMOS DEL FICHERO
                        
                                             
            
            
    except OSError:
        message='File Not Found'
        
        error_packet=struct.pack(f'=2H{len(message)-5}sB',5,1,str.encode(message),0)
        
        sock.send(error_packet)

        sock.close()
    
                   

            

def write(sock,unpacked_code,client):
    block=0
    recieve=False
    try:
        with open(unpacked_code[1].decode(),'x') as writefile:
        
            while True:        
            
                if not recieve:
                    last_packet=struct.pack(f'!2H',4,block)
                    
                    block=block+1

                    sock.send(last_packet)
                    
                    msg = sock.recv(512)

                    write_message = struct.unpack(f'=2H{len(msg)-4}s',msg)
                    
                    print(write_message)

                    recieved_bytes=writefile.write(write_message[2])
                    
                else:
                    sock.send(last_packet)

                    msg=sock.recv(512)

                    write_message = struct.unpack(f'=2H{len(msg)-4}s',msg)

                    recieved_bytes=writefile.write(write_message[2])

                    recieve=False

    
    
    except IOError:
        message='File Already Exists'
        sock.send(struct.pack(f'=2H{len(message)}sH',5,2,str.encode(message),0))
        

def client_handle(child_sock,client,n):
    print("Client conected: ",n,client)
    msg =child_sock.recv(516) #RECIBIMOS EL PAQUETE QUE EL SERVIDOR MANDA, LA CANTIDAD DE DATOS TIENE QUE SER EL APROPIADO PARA QUE NO HAYA RESTRICCIONES
    unpacked_code = struct.unpack(f"!H{len(msg)-12}sB{len('netascii')}sB",msg)
    if not unpacked_code:
        pass
    
    if(unpacked_code[0]==1):
       read(child_sock,unpacked_code,client)
    if(unpacked_code[0]==2):
       write(child_sock,unpacked_code,client)
    else:
       pass

def main(*args,**kwargs):

    sock = socket(AF_INET, SOCK_STREAM)
    sock.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    port=int(sys.argv[1])
    sock.bind(('',port))
    Clients=int(input("Indicate the number of clients: "))
    sock.listen(Clients)
    n=0     
    while 1:
        
        child_socket, client= sock.accept()
        n=n+1
        start_new_thread(client_handle,(child_socket,client,n))
        
    
    


if __name__ == '__main__':
    try:
      sys.exit(main())
    except KeyboardInterrupt:
      pass
    
    except Exception:
        traceback.print_exc()
