# -*- coding: utf-8 -*-

import socket
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
    
    block=1 

    

    with open(file_name,'r',) as f:

        autentication_packet=sock.recv(2)
        confirm_packet=struct.unpack(f'!H',autentication_packet)

        
        if (confirm_packet[0]==4):
            while True:         
                    
                sent_bytes=f.read(512)
                
                last_packet = struct.pack(f'!2H{len(sent_bytes)}s',3,block,str.encode(sent_bytes))
                                            
                sent = sock.send(last_packet)   

                block+=1
                
                if(len(last_packet)<512):
                    
                    break   
            
        
        else:
            
            
            error_message=sock.recv(516)
            
            error_packet=struct.unpack(f'!2H{len(error_message)-5}sB',error_message)
                                
            print(f"Error number:{error_packet[0]} Message:",error_packet[2].decode())
                 
            pass
    
        
def read(sock,*args,**kwargs):
    if(len(args)!=4):
        raise Exception("Please introduce the arguments in the correct format -> READ 'filename'")
    ip=args[2]
    port=args[3]
    file_name=args[0]
    
    
    last_packet=struct.pack(f"!H{len(file_name)}sB{len('netascii')}sB",1,str.encode(file_name),0,b'netascii',0)  
    
    sock.send(last_packet) 
    


    with open(file_name,'wb',) as f:

        while True:
            
                        
                msg = sock.recv(516)         
               
                
                code_message = struct.unpack(f'!H{len(msg)-2}s',msg)               
                if(code_message[0]==3):
                                    
                    
                    leftUnpackedMsg = struct.unpack(f'!H{len(code_message[1])-2}s', code_message[1]) 

                    f.write(leftUnpackedMsg[1])

                    if(len(leftUnpackedMsg[1])<512):
                        
                        break
                                        
                       
                
                else:

                    leftUnpackedMsg= struct.unpack(f'!H{len(code_message[1])-3}sB',code_message[1])
                    
                    print(f"Error number:{code_message[0]} Message:{leftUnpackedMsg[1].decode()}")

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
    if(sys.argv[1]!='-s'or sys.argv[3]!='-p' or len(sys.argv) != 5 ):
        raise Exception("Introduce the arguments in the correct format -> python3 TFTP_TCPClient.py -s 'server direction' -p 'port number' ")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    
        sock.connect((sys.argv[2],int(sys.argv[4])))
        while True:
            command = input('TFTP@TCP> ').lower()
            arguments = command.split() + sys.argv
            functions[arguments[0]](sock,*arguments[1:])
            
            

        

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(str(e))
