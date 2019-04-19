# -*- coding: utf-8 -*-

import socket
import sys
import struct
import traceback
import io
import time

def write(sock,*args,**kwargs):
    
    if(len(args)!=5):
        print(args)
        raise Exception("Please introduce the arguments in the correct format -> WRITE 'filename'")
    
    ip=args[2]
    port=args[3]
    file_name=args[0]
         
    last_packet=sendRRQWRQ(2,file_name,sock)
    
    block = 1 

    

    with open(file_name,'r',) as f:

        autentication_packet=sock.recv(2)
        
        confirm_packet=autentication_message(autentication_packet)

        
        if (confirm_packet==4):
            
            while True:         
                    
                sent_bytes=f.read(512)
                
                last_packet = send_data(sock,block,sent_bytes)   

                block = block + 1
                
                if(len(last_packet)<512):
                    
                    break   
            
        
        else:
            
            
            error_message=sock.recv(516)
            
            unpack_err_write(error_message)

            pass
    
        
def read(sock,*args,**kwargs):
    if(len(args)!=5):
        print(args)
        raise Exception("Please introduce the arguments in the correct format -> READ 'filename'")
    
    file_name=args[0]
    
    last_packet=sendRRQWRQ(1,file_name,sock)
    
    with open(file_name,'wb',) as file_write:

        while True:
            
                        
                packet = sock.recv(516)         
               
                code = unpack_packetcode(packet)
                
                data_packed = unpack_data(packet)              
                
                if(code==3):
                                    
                    
                    leftUnpackedMsg = unpack_data(data_packed[1])

                    file_write.write(leftUnpackedMsg[1])

                    if(len(leftUnpackedMsg[1])<512):
                        
                        break
                else:
                    
                    unpack_err_read(data_packed[1],code)

                    break
                
    


def end_program(sock,*args,**kwargs):
    
    if(len(args)!=4):
        print(args)
        raise Exception("Please introduce the arguments in the correct format -> QUIT")

    raise KeyboardInterrupt("Bye,good to see you")
    

functions={
    "quit":end_program,
    "read":read,
    "write":write
}

def main(*args,**kwargs):
    if(sys.argv[1]!='-s'or sys.argv[3]!='-p' or len(sys.argv) != 5 ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPClient.py -s 'server direction' -p 'port number' ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    
        sock.connect((sys.argv[2],int(sys.argv[4])))
        while True:
            command = input('TFTP@TCP> ').lower()
            arguments = command.split() + sys.argv[1:]
            try:

                functions[arguments[0]](sock,*arguments[1:])
            except OSError as filenotfounderror:
                print(filenotfounderror.strerror)
            
            

def sendRRQWRQ(code,file_name,sock,encode_mode='netascii'):
    last_packet=struct.pack(f"!H{len(file_name)}sB{len(encode_mode)}sB", code ,str.encode(file_name),0,str.encode(encode_mode),0)
    sock.send(last_packet)
    return last_packet

def autentication_message(packet):        
    confirm_packet=struct.unpack(f'!H',packet)
    return confirm_packet[0]

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]

def unpack_data(packet):
    unpacked_data = struct.unpack(f'!H{len(packet)-2}s', packet)
    return unpacked_data

def unpack_err_read(packet,code):
    unpacked_err = struct.unpack(f'!H{len(packet)-3}sB', packet)
    print(f"Error number:{code} Message:{unpacked_err[1].decode()}")     

def send_data(sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block , str.encode(data))
    sock.send(packed_data)  
    return packed_data

def unpack_err_write(packet):
    unpacked_err = struct.unpack(f'!2H{len(packet)-5}sB', packet)
    print(f"Error number:{unpacked_err[0]} Message:{unpacked_err[2].decode()}")

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e))
