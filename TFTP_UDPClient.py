# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_DGRAM
import pickle
import sys
import struct

# QUEDA PENDIENTE CERRAR EL SOCKET CUANDO TERMINAMOS CADA OPERACIÓN

def write(sock,*args,**kwargs):

    if(len(args)!=1):
        raise Exception("The number of arguments is not correct")
        
def read(sock,ip,port,*args,**kwargs):
    if(len(args)!=1):
        raise Exception("The number of arguments is not correct")

    acknowledgment=False
    
    sock.sendto(struct.pack(f"!H{len(sys.argv[1])}sB{len('netascii')}sB",1,args[0].encode(),0,b'netascii',0), (ip,port) ) 
    #Enviamos el paquete para empezar a leer del servidor , args[0] es el nombre del archivo de texto que queremos leer
    #! es por el formato de la red
    #H es por un unsigned short de 2 Bytes
    #s es por una cadena de caracteres cuya longitud esta definida por la propia cadena en el formato
    #B es por un unsigned char que ocupa 1 Byte




    while True:

        try:
                
            if not acknowledgment:

                #516 es el tamaño de los 512 bytes de datos maximos mas los 2 bytes del codigo y los 2 bytes del bloque
                msg,cliente = sock.recvfrom(516)

                unpacked_code = struct.unpack(f'H{len(msg)-2}', msg) #Extraemos todo el paquete del servidor dividiendolo en codigo de mensaje y lo demás para primero analizar el codigo

                #En este caso el codigo sería el correcto, el codigo 3, que significa que recibimos datos del servidor tftp
                if(unpacked_code[0]==3):

                    unpacked_data = struct.unpack(f'H{len(unpacked_code[1])-2}s', unpacked_code[1]) #Extraemos todo el paquete del servidor dividiendolo en los campos indicados en el comentario de arriba

                    #Enviamos codigo 4 de ACK y el numero de bloque al que corresponde el acknowledgment

                    sock.sendto(struct.pack('=2H', 4 , unpacked_data[1]) , cliente )   #ACK

                else:
                    #En este caso estamos recibiendo el codigo 5, que significa que ha habido un error en el servidor, tendríamos que mostrar un mensaje al usuario

                    #Lo dividimos en 2 bytes de error, el mensaje, y un byte que es un 0
                    unpacked_data = struct.unpack(f'H{len(unpacked_code[1])-3}sB', unpacked_code[1])

            else:
                sock.sendto(struct.pack('=2H', 4 , unpacked_data[1]), cliente )   #ACK
                    
            
        except sock.timeout: #pendiente que sea la excepción socket.timeout
            acknowledgment=True

        else:
            if(struct.calcsize(msg) < 516 ):
                break

    


def end_program(*args,**kwargs):
    raise SystemError("Bye,good to see you")

functions={
    "quit":end_program,
    "read":read,
    "write":write
}

def main(*args,**kwargs):

    sock = socket(AF_INET, SOCK_DGRAM)
    sock.settimeout(5)
    while True:
        try:
            command = input('TFTP@UDP> ').lower()
            arguments = command.split()
            #sys.argv[0] es la ip // sys.argv[1] es el puerto //argumentos depende de la función que querramos invocar, cogemos apartir del 1 porque el 0 es el nombre del comando, READ, WRITE
            functions[arguments[0]](sock,sys.argv[0],sys.argv[1],arguments[1:])
        except Exception:
            print ('error')
        finally:
            sock.close()


        

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass