# -*- coding: utf-8 -*-

from socket import socket, AF_INET, SOCK_DGRAM
import pickle
import sys
import struct


def write(sock,*args,**kwargs):

    print(args)
    ip=args[0]
    port=args[1]
    file_name=args[2]


    if(len(args)!=1):
        raise Exception("The number of arguments is not correct")  
    
    sent=sock.send(struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",2,str.encode(file_name),0,b'netascii',0)) 
    #Enviamos el paquete para empezar a leer del servidor , args[0] es el nombre del archivo de texto que queremos leer
    #! es por el formato de la red
    #H es por un unsigned short de 2 Bytes
    #s es por una cadena de caracteres cuya longitud esta definida por la propia cadena en el formato
    #B es por un unsigned char que ocupa 1 Byte


    with open(args[0],'w',) as f:

        while True:

            try:
                    
                    #Podemos recibir una RRQ/ERR o normalmente un ACK de tamaño 4 que es el tamaño del acknowledgmente que serían 2 bytes del codigo y otros 2 del codigo
                msg = sock.recv(516)

                code_message = struct.unpack(f'=H{len(msg)-2}s', msg) #Extraemos todo el paquete del servidor dividiendolo en codigo de mensaje y lo demás para primero analizar el codigo

                    #En este caso el codigo sería el correcto, el codigo 4, que significa que hemos recibido el OK del server, un acknowledgment
                if(code_message[0]==4):

                    sent_bytes=f.read(512)

                    leftUnpackedMsg = struct.unpack('=H', code_message[1])
                        
                        #EL PRIMER MENSAJE DE ACK DEL SERVER AL CLIENTE TIENE QUE TENER BLOQUE 0
                    sent = sock.send(struct.pack(f'=2H{len(sent_bytes)}', 4 , leftUnpackedMsg[1]+1 ,sent_bytes))   



                      

                else:
                        #En este caso estamos recibiendo el codigo 5, que significa que ha habido un error en el servidor, tendríamos que mostrar un mensaje al usuario

                        #Lo dividimos en 2 bytes de error, el mensaje, y un byte que es un 0
                    leftUnpackedMsg= struct.unpack(f'=H{len(leftUnpackedMsg[1])-3}sB', code_message[1])
                    print(f"Error number:{leftUnpackedMsg[0]} Message:{leftUnpackedMsg[1]}")
                    break
                                             
                 
def read(sock,*args,**kwargs):

    ip=args[0]
    port=args[1]
    file_name=args[2]

    if(len(args)!=1):
        raise Exception("The number of arguments is not correct")

    
    estructura=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",1,str.encode(file_name),0,b'netascii',0)
    sock.send(estructura) 
    #Enviamos el paquete para empezar a leer del servidor , args[0] es el nombre del archivo de texto que queremos leer
    #! es por el formato de la red
    #H es por un unsigned short de 2 Bytes
    #s es por una cadena de caracteres cuya longitud esta definida por la propia cadena en el formato
    #B es por un unsigned char que ocupa 1 Byte


    with open(args[0],'w',) as f:

        while True:
            
                        
                    #516 es el tamaño de los 512 bytes de datos maximos mas los 2 bytes del codigo y los 2 bytes del bloque
            msg = sock.recv(516)
            code_message = struct.unpack(f'H{len(msg)-2}s',msg) #Extraemos todo el paquete del servidor dividiendolo en codigo de mensaje y lo demás para primero analizar el codigo

                    #En este caso el codigo sería el correcto, el codigo 3, que significa que recibimos datos del servidor tftp
            if(code_message[0]==3):

                leftUnpackedMsg = struct.unpack(f'H{len(code_message[1])-2}s', code_message[1]) #Extraemos todo el paquete del servidor dividiendolo en los campos indicados en el comentario de arriba

                        #Escribimos en un archivo que se llama igual que el archivo del server lo que recibimos de el
                f.write(leftUnpackedMsg[1].decode("utf-8"))
                        
                        #Enviamos codigo 4 de ACK y el numero de bloque al que corresponde el acknowledgment
                sock.send(struct.pack('!2H', 4 , leftUnpackedMsg[0]))   #ACK

            else:
                        #En este caso estamos recibiendo el codigo 5, que significa que ha habido un error en el servidor, tendríamos que mostrar un mensaje al usuario

                        #Lo dividimos en 2 bytes de error, el mensaje, y un byte que es un 0
                leftUnpackedMsg = struct.unpack(f'H{len(unpacked_code[1])-3}sB', code_message[1])
                print(f"Error number:{leftUnpackedMsg[0]} Message:{leftUnpackedMsg[1]}")
                        #depende de como lo haya hecho enrique lo tengo que mirar como lo ha hecho para el cliente proque teiene que ser concurrente
                if(struct.calcsize(msg) < 516 ):
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
    sock.accept(int(sys.argv[1]),int(sys.argv[2]))
    while True:
        try:
            command = input('TFTP@TCP> ').lower()
            arguments = command.split()
            print(sys.argv[1:])
            #sys.argv[0] es la ip // sys.argv[1] es el puerto //argumentos depende de la función que querramos invocar, cogemos apartir del 1 porque el 0 es el nombre del comando, READ, WRITE
            functions[arguments[0]](sock,sys.argv[1:],arguments[1])
        except Exception:
            traceback.print_exc()


        

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass