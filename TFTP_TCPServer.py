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
           #Abrimos el archivo que hemos indicado en el cliente     
            while True:                       
                sent_bytes=readfile.read(512)                      
                    #Leemos los paquetes que queremos del fichero en este caso de     
                last_packet = struct.pack(f'=2H{len(sent_bytes)}s',3,block,str.encode(sent_bytes))
                    #Este paquete contiene el codigo, el bloque y los datos necesarios   
                block=block+1
                    #Incrementamos el block number cada iteración    
                child_sock.send(last_packet) 
                    #Mandamos el paquete
                if(len(sent_bytes)<512):
                    break 
                    #En el caso de que el ultimo paquete sea menor que 512, la opción de lectura terminará                         
            
    except FileNotFoundError:
        
        message='File Not Found'
            
        error_packet=struct.pack(f'=2H{len(message)}sB',5,1,str.encode(message),0)
            
        child_sock.send(error_packet)

        

            

def write(sock,unpacked_code,client):
    try:
        with open(unpacked_code[1].decode(),'x') as writefile:
        
            while True:        
                    
                msg = sock.recv(512)

                if not msg:
                    break

                write_message = struct.unpack(f'!2H{len(msg)-4}s',msg)

                if(write_message[0]==3):    

                    writefile.write(write_message[2].decode("utf-8"))

                    if(len(write_message[2])<512):
                        break
    except IOError:
        
        message='File Already Exists'
        
        error_packet=struct.pack(f'=2H{len(message)}sB',5,2,str.encode(message),0)
               
        sock.send(error_packet)

        

        

def client_handle(child_sock,client,n):
    while True:
        print("Client conected: ",n,client)
        msg =child_sock.recv(516) #RECIBIMOS EL PAQUETE QUE EL SERVIDOR MANDA, LA CANTIDAD DE DATOS TIENE QUE SER EL APROPIADO PARA QUE NO HAYA RESTRICCIONES
        unpacked_code = struct.unpack(f"!H{len(msg)-12}sB{len('netascii')}sB",msg)
        print(unpacked_code[0])
        if(unpacked_code[0]==1):
            read(child_sock,unpacked_code,client)
        if(unpacked_code[0]==2):
            write(child_sock,unpacked_code,client)
        else:
            pass
    

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
