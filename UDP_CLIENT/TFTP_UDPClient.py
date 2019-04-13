# -*- coding: utf-8 -*-

import socket
import struct
import traceback 
import sys
from os import remove
import pdb


def write(sock,*args,**kwargs):

    if(len(args)!=5):
        raise Exception("Please introduce the arguments in the correct format -> READ 'filename'")

    file_name=args[0]
    ip=args[2]
    port=args[4]

    recieved=False
    last_message=False
    last_packet=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",2,str.encode(file_name),0,b'netascii',0)

    #Enviamos el paquete para empezar a leer del servidor , args[0] es el nombre del archivo de texto que queremos leer
    #! es por el formato de la red
    #H es por un unsigned short de 2 Bytes
    #s es por una cadena de caracteres cuya longitud esta definida por la propia cadena en el formato
    #B es por un unsigned char que ocupa 1 Byte

    sock.sendto(last_packet, (ip,int(port)) ) 

    with open(file_name,'r',) as writefile:

        while True:

            try:
                    
                if not recieved:

                    msg,cliente = sock.recvfrom(516)

                    if last_message: break

                    code_message = struct.unpack(f'!H{len(msg)-2}s', msg) 

                    if(code_message[0]==4):

                        sent_bytes= writefile.read(512)

                        leftUnpackedMsg = struct.unpack('!H', code_message[1])
                        
                        #EL PRIMER MENSAJE DE ACK DEL SERVER AL CLIENTE TIENE QUE TENER BLOQUE 0
                        last_packet = struct.pack(f'!2H{len(sent_bytes)}s', 4 , leftUnpackedMsg[0]+1 ,str.encode(sent_bytes))

                        sock.sendto(last_packet, cliente)  
                    
                    else:

                        leftUnpackedMsg= struct.unpack(f'!H{len(code_message[1])-3}sB', code_message[1])

                        print(f"Error number:{leftUnpackedMsg[0]}  Message:{leftUnpackedMsg[1].decode()}")

                        break
                        
                        
                else:
                    sock.sendto(last_packet,(ip,int(port)))
                    recieved=False
                        
                
            except socket.error: 
                recieved=True
            
            except Exception:
                traceback.print_exc()
            
            else:
                if( len ( sent_bytes ) < 516):
                    last_message=True

                    

    
        
def read(sock,*args,**kwargs):


    if(len(args)!=5):
        raise Exception("Please introduce the arguments in the correct format -> READ 'filename'")

    file_name=args[0]
    ip=args[2]
    port=args[4]
   
    acknowledgment=False

    last_packet=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",1,str.encode(file_name),0,b'netascii',0)
    sock.sendto(last_packet, (ip ,int(port)))

    with open(file_name,'w',) as f:

        while True:

            try:
                    
                if not acknowledgment:

                    msg,cliente = sock.recvfrom(516)

                    code_message = struct.unpack(f'!H{len(msg)-2}s', msg) 

                    if(code_message[0]==3):

                        leftUnpackedMsg = struct.unpack(f'!H{len(code_message[1])-2}s', code_message[1]) 

                        f.write(leftUnpackedMsg[1].decode())
                        
                        last_packet = struct.pack('!2H', 4 , leftUnpackedMsg[0]) 

                        sock.sendto( last_packet , cliente )   #ACK

                    else:
                        
                        leftUnpackedMsg = struct.unpack(f'!H{len(code_message[1])-3}sB', code_message[1])

                        remove(file_name)
                        
                        print(f"Error number:{leftUnpackedMsg[0]} Message:{leftUnpackedMsg[1].decode()}")
                        break

                else:
                    sock.sendto(last_packet, (ip,int(port)) )   #ACK
                    acknowledgment=False
                        
                
            except socket.error: 
                acknowledgment=True

            except Exception:
                traceback.print_exc()
            else:
                if ( len(msg) < 516 ):
                    break


    


def end_program(sock,*args,**kwargs):
    raise KeyboardInterrupt("Bye,good to see you")

functions={
    "quit":end_program,
    "read":read,
    "write":write
}

def main(*args,**kwargs):

    if(sys.argv[1]!='-s'or sys.argv[3]!='-p'):
            raise Exception("Introduce the arguments in the correct format -> python3 TFTP_UDPClient.py -s 'server direction' -p 'port number' ")

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        timeval = struct.pack('LL',0,995000)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

        while True:
            
            command = input('TFTP@UDP> ').lower()
            arguments = command.split() + sys.argv[1:]
            functions[arguments[0]](sock,*arguments[1:])
      

if __name__ == '__main__':
    try:
        exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
            traceback.print_exc()
