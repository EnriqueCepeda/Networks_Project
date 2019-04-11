# -*- coding: utf-8 -*-

import socket
import sys
import struct
import traceback


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

    


    with open(file_name,'w',) as f:

        while True:

            try:
                    
                if not recieved:

                    msg,cliente = sock.recvfrom(516)

                    if last_message: break

                    code_message = struct.unpack(f'=H{len(msg)-2}s', msg) 

                    if(code_message[0]==4):

                        sent_bytes=f.read(512)

                        leftUnpackedMsg = struct.unpack('=H', code_message[1])
                        
                        #EL PRIMER MENSAJE DE ACK DEL SERVER AL CLIENTE TIENE QUE TENER BLOQUE 0
                        last_packet = struct.pack(f'!2H{len(sent_bytes)}s', 4 , leftUnpackedMsg[1]+1 ,sent_bytes)

                        sock.sendto(last_packet, cliente)   
                    
                    else:

                        print(code_message[0])

                        leftUnpackedMsg= struct.unpack(f'=H{len(code_message[1])-3}sB', code_message[1])

                        print(f"Error number:{leftUnpackedMsg[0]}  Message:{leftUnpackedMsg[1].decode()}")
                        break
                        
                        
                else:
                    sock.sendto(last_packet,(ip,int(port)))
                    recieved=False
                        
                
            except socket.error as socketerror: 
                recieved=True
            
            else:
                if( len(sent_bytes) < 512):
                    last_message=True

                    

    
        
def read(sock,*args,**kwargs):


    if(len(args)!=5):
        raise Exception("Please introduce the arguments in the correct format -> READ 'filename'")

    file_name=args[0]
    ip=args[2]
    port=args[4]
   
    acknowledgment=False
    last_message=False

    last_packet=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",1,str.encode(file_name),0,b'netascii',0)
    sock.sendto(last_packet, (ip ,int(port)))

    with open(file_name,'w',) as f:

        while True:

            try:
                    
                if not acknowledgment:

                    msg,cliente = sock.recvfrom(516)

                    if last_message: break

                    code_message = struct.unpack(f'!H{len(msg)-2}s', msg) 
                    if(code_message[0]==3):

                        leftUnpackedMsg = struct.unpack(f'=H{len(code_message[1])-2}s', code_message[1]) 

                        f.write(leftUnpackedMsg[1].decode('ascii'))
                        
                        last_packet = struct.pack('!2H', 4 , leftUnpackedMsg[0]) 

                        sock.sendto( last_packet , cliente )   #ACK

                    else:
                        
                        leftUnpackedMsg = struct.unpack(f'=H{len(code_message[1])-3}sB', code_message[1])
                        print(f"Error number:{leftUnpackedMsg[0]} Message:{leftUnpackedMsg[1].decode()}")
                        break

                else:
                    sock.sendto(last_packet, (ip,int(port)) )   #ACK
                    acknowledgment=False
                        
                
            except socket.error as socketerror: 
                acknowledgment=True

            else:
                if(len(msg) < 516 ):
                    last_message=True


    


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

        timeval = struct.pack('LL',0,999999)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

        while True:
            
            command = input('TFTP@UDP> ').lower()
            arguments = command.split() + sys.argv[1:]
            functions[arguments[0]](sock,*arguments[1:])



        

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception:
            traceback.print_exc()
