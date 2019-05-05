 #-*- coding: utf-8 -*-

import socket
import sys
import struct
import traceback
import io
import time
import os
import threading  
        
def read (port,ip,i, *args,**kwargs):
    
    print("Client {} reading".format(i+1))
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:   

        sock.connect((port,int(ip)))

        file_name="co.text"
       
        last_packet=sendRRQWRQ(1,file_name,sock)
                
        with open(f'TCP_CLIENT/{file_name}','wb',) as file_write:        
            while True:
                                        
                packet_data = sock.recv(516)                   
                                
                code=unpack_packetcode(packet_data)

                if(code==3):  

                    unpacked_data = unpack_data(packet_data)

                    file_write.write(unpacked_data[2])
                            
                    if(len(unpacked_data[2])<512):
                                        
                        break
                                                
                else:                 
                            
                    unpack_err(packet_data)
                        
                    break
        print("Client {} finishing reading".format(i+1))    
        sock.close()


def main(*args,**kwargs):
    if(sys.argv[1]!='-s'or sys.argv[3]!='-p' or len(sys.argv) != 6 ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPClient.py -s 'server direction' -p 'port number' 'number of clients' ")
    i=0
    n_client=int(sys.argv[5])
    for i in range(i,n_client):
       
        client = threading.Thread(target=read,args=(sys.argv[2],sys.argv[4],i))
        
        client.start()
   
    i=0
    for i in range(i,n_client):

        client.join()
        
            

def sendRRQWRQ(code,file_name,sock,encode_mode='netascii'):
    last_packet=struct.pack(f"!H{len(file_name)}sB{len(encode_mode)}sB", code ,str.encode(file_name),0,str.encode(encode_mode),0)
    sock.send(last_packet)
    return last_packet

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]

def unpack_data(packet):
    unpacked_data = struct.unpack(f'!2H{len(packet)-4}s', packet)
    return unpacked_data

def send_data(sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block , data)
    sock.send(packed_data)  
    return packed_data

def unpack_err(packet):
    unpacked_err = struct.unpack(f'!2H{len(packet)-5}sB', packet)
    print(f"Error number:{unpacked_err[1]} Message:{unpacked_err[2].decode()}")


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e))