
import struct
import pickle
import sys
from socket import *

def read(sock,unpacked_code,port):
    block=0 #THIS IS THE BLOCK NUMBER IN ORDER TO INDICATE THE PACKETS THAT HAS BEEN SENT
    while True:
        f=open(unpacked_code[1],'rb') #WE OPEN THE FILE THAT THE CLIENT SENT TO SERVER
        while True:
            try:
                acknowledgment=False
                record[block]=f.read(512) #ESTO ES UN ARRAY DE BYTES QUE VA LEYENDO EL SERVIDOR PARA MANDARSELO AL CLIENTE, EN EL QUE CASO DE QUE SE PRODUZCA UN ERROR EL SERVIDOR ENVIARA EL BLOCK DEL ANTERIOR EN VEZ DEL ACTUAL
                if not acknowledgment:
                    sock.sendto(struct.pack(f"!HH{len(record[block])}s",3,block+1,record[block].encode(), ('',port))) #EL SERVIDOR MANDA EL PAQUETE AL CLIENTE CON SU BLOCK NUMBER CORRESPONDIENTE
                    msg, client=sock.recvfrom(512) #EL SERVIDOR RESCIBE EL ACK DEL CLIENTE
                else:
                    sock.sendto(struct.pack(f"!HH{len(record[block-1])}s",3,block,record[block-1].encode(), ('',port))) #EN EL CASO DE QUE HAYA TIMEOUT SE TENDRÁ EN CUENTA DE QUE TIENE QUE MANDA EL MISMO PAQUETE CON LOS MISMOS BYTES DEL PAQUETE
            except sock.timeout:
                acknowledgment=True
            except IOError:
                sock.sendto(struct.pack('=HpH',5,1,'FILE NOT FOUND',0))
                sock.close()    ##en el caso de error se tendría que mandar un mensaje que contenga los siguiente y pot supuesto cerrar el SERVIDOR

            
                

def write(sock,unpacked_code,port):
    block=0
    f=open(unpacked_code[1],'wb')
    while True:
       sock.sendto(struct.pack('=HB',4,block ('',port)))
        while True:
            try:
                
                acknowledgment=False
                if not acknowledgment:
                    msg,client=sock.recvfrom(516)
                    unpacked_data = struct.unpack(f'H{len(msg)-2}s', msg) #Extraemos todo el paquete del servidor dividiendolo en los campos indicados en el comentario de arriba
                    f.write(unpacked_data[1])
                    sock.sendto(struct.pack('=2H', 4 , unpacked_data[1]) , ('',port) )   #ACK
                    
                else:
                   sock.sendto(struct.pack(f"!HH{len(f.read(512))}s",3,block+1,f.read(512).encode(), ('',port)))
            except sock.timeout:
                acknowledgment=True
            except IOError:
                sock.sendto(struct.pack('=HpH',5,1,'FILE NOT FOUND',0))
                sock.close()    ##en el caso de error se tendría que mandar un mensaje ya que ha habido un problema en cuanto al fichero y pot supuesto cerrar el SERVIDOR

            finally:
                sock.close()




def main(*args,**kwargs):
    try:

        sock = socket(AF_INET, SOCK_DGRAM)
        sock.settimeout(5)
        sock.bind(('',int(sys.argv[1])))
        msg, client =sock.recvfrom(516) #RECIBIMOS EL PAQUETE QUE EL SERVIDOR MANDA, LA CANTIDAD DE DATOS TIENE QUE SER EL APROPIADO PARA QUE NO HAYA RESTRICCIONES
        unpacked_code = struct.unpack(f"!H{len(msg)-12}sB{len('netascii')}sB",msg)
        if(unpacked_code[0]==1):
            read(sock,unpacked_code,int(sys.argv[1]))
        if(unpacked_code[0]==2):
            write(sock,unpacked_code,int(sys.argv[1]))
    except Exception:
        print ('error')
    finally:
        sock.close()

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
