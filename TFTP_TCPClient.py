# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_STREAM
import pickle
import sys
import struct
import traceback
import io
import time

def write(sock,*args,**kwargs):
    if(len(args)!=4):
        raise Exception("The number of arguments is not correct")
    
    ip=args[2]
    port=args[3]
    file_name=args[0]
         
    last_packet=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",2,str.encode(file_name),0,b'netascii',0)
    sock.send(last_packet) 
    #Enviamos el paquete para empezar a leer del servidor , args[0] es el nombre del archivo de texto que queremos leer
    #! es por el formato de la red
    #H es por un unsigned short de 2 Bytes
    #s es por una cadena de caracteres cuya longitud esta definida por la propia cadena en el formato
    #B es por un unsigned char que ocupa 1 Byte


    with open(file_name,'w',) as f:

        while True:
                                
            msg = sock.recv(516) 

            code_message = struct.unpack(f'=H{len(msg)-2}s', msg) 
            
            print(code_message[0])
                   
            if(code_message[0]==4):

                sent_bytes=f.read(512)

                leftUnpackedMsg = struct.unpack('=H', code_message[1])
                        
                last_packet= struct.pack(f'!2H{len(sent_bytes)}s', 4 , leftUnpackedMsg[1]+1 ,sent_bytes)       #EL PRIMER MENSAJE DE ACK DEL SERVER AL CLIENTE TIENE QUE TENER BLOQUE 0
                
                sent = sock.send(last_packet)   



                      

            else:
                        #En este caso estamos recibiendo el codigo 5, que significa que ha habido un error en el servidor, tendríamos que mostrar un mensaje al usuario

                        #Lo dividimos en 2 bytes de error, el mensaje, y un byte que es un 0
                leftUnpackedMsg= struct.unpack(f'=H{len(code_message[1])-3}sB', code_message[1])
                print(f"Error number:{leftUnpackedMsg[0]} Message:{leftUnpackedMsg[1]}")
                break
                                             
                 
def read(sock,*args,**kwargs):
    if(len(args)!=4):
        raise Exception("The number of arguments is not correct")
    ip=args[2]
    port=args[3]
    file_name=args[0]
    
    
    last_packet=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",1,str.encode(file_name),0,b'netascii',0)  
    
    sock.send(last_packet) 
    #Enviamos el paquete para empezar a leer del servidor , args[0] es el nombre del archivo de texto que queremos leer
    #! es por el formato de la red
    #H es por un unsigned short de 2 Bytes
    #s es por una cadena de caracteres cuya longitud esta definida por la propia cadena en el formato
    #B es por un unsigned char que ocupa 1 Byte


    with open(file_name,'w',) as f:

        while True:
            
                        
                msg = sock.recv(516)         
                    #516 es el tamaño de los 512 bytes de datos maximos mas los 2 bytes del codigo y los 2 bytes del bloque
               
                
                code_message = struct.unpack(f'!H{len(msg)-2}s',msg) #Extraemos todo el paquete del servidor dividiendolo en codigo de mensaje y lo demás para primero analizar el codigo
                #En este caso el codigo sería el correcto, el codigo 3, que significa que recibimos datos del servidor tftp
                               
                if(code_message[0]==3):
                    print(code_message[1])
                    
                    
                    leftUnpackedMsg = struct.unpack(f'=H{len(code_message[1])-2}s', code_message[1]) #Extraemos todo el paquete del servidor dividiendolo en los campos indicados en el comentario de arriba
                        #print(leftUnpackedMsg[0])
                    print(leftUnpackedMsg[1])
                        #Escribimos en un archivo que se llama igual que el archivo del server lo que recibimos de el
                    f.write(leftUnpackedMsg[1].decode('cp437'))
                                        
                       
                
                else:
                        #En este caso estamos recibiendo el codigo 5, que significa que ha habido un error en el servidor, tendríamos que mostrar un mensaje al usuario

                        #Lo dividimos en 2 bytes de error, el mensaje, y un byte que es un 0
                    leftUnpackedMsg= struct.unpack(f'=H{len(code_message[1])-3}sB',code_message[1])
                    
                    print(f"Error number:{code_message[0]} Message:{leftUnpackedMsg[1].decode()}")
                        #depende de como lo haya hecho enrique lo tengo que mirar como lo ha hecho para el cliente proque teiene que ser concurrente
                    break

            





    


def end_program(sock,*args,**kwargs):
    sock.close()
    raise SystemError("Bye,good to see you")

functions={
    "quit":end_program,
    "read":read,
    "write":write
}

def main(*args,**kwargs):

    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((sys.argv[1],int(sys.argv[2])))
    while True:
        command = input('TFTP@TCP> ').lower()
        arguments = command.split() + sys.argv
        functions[arguments[0]](sock,*arguments[1:])
        
            


        

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        traceback.print_exc()
