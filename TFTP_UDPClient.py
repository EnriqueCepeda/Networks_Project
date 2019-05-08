
import socket
import struct
import traceback 
import sys

def write(sock,*args,**kwargs):

    if(len(args)!=5):
        print("Please introduce the arguments in the correct format -> READ 'filename'")
    else:

        file_name=args[0]
        ip=args[2]
        port=args[4]

        file_content=''
        count=0
        continue_ack=0
        max_continue_ack=10
        file_iteration_block=1

        error=False
        recieved=False
        last_message=False

        try:
            
            with open(f'UDP_CLIENT/{file_name}','r') as writefile:
                file_content = writefile.read().encode()  

        except FileNotFoundError as filenotfounderror:
            print(filenotfounderror)
            error=True

        if error==False:

            try:

                last_packet= sendRRQWRQ(2,file_name,ip,port,sock)
                
                while continue_ack<max_continue_ack:
            
                    if not recieved:

                        try:
                            msg,cliente = sock.recvfrom(516)
                            continue_ack=0
                        except socket.error: 
                            recieved=True
                            continue_ack = continue_ack + 1
                            continue

                        if last_message: 
                            break

                        packet_code = unpack_packetcode(msg)

                        if(packet_code==4):

                            ack = unpack_ack(msg)

                            sent_bytes = file_content[count : (file_iteration_block)*512]

                            file_iteration_block = file_iteration_block + 1

                            count = count + len(sent_bytes)

                            last_packet = send_data(cliente,sock,ack[1],sent_bytes)

                            if( len ( sent_bytes ) < 512):
                                last_message=True
                        
                        elif(packet_code==5):
                            
                            unpack_err(msg)
                            break
                            
                            
                    else:
                        sock.sendto(last_packet,(ip,int(port)))
                        recieved=False
            
            except UnicodeDecodeError as decodeerror:
                print(decodeerror)

        
def read(sock,*args,**kwargs):

    if(len(args)!=5):
        print("Please introduce the arguments in the correct format -> READ 'filename'")
    else:

        try:

            file_name=args[0]
            ip=args[2]
            port=args[4]
            file_content=''
            continue_ack=0
            max_continue_ack=10

            acknowledgment=False

            last_packet = sendRRQWRQ(1,file_name,ip,port,sock)

            while continue_ack<max_continue_ack:
                            
                if not acknowledgment:
                    
                    try:
                        msg,cliente = sock.recvfrom(516)
                        continue_ack=0

                    except socket.error:  
                        continue_ack = continue_ack +1
                        acknowledgment=True
                        continue

                    packet_code = unpack_packetcode(msg)
                
                    if(packet_code == 3):

                        data = unpack_data(msg)

                        file_content = file_content + data[2].decode()

                        last_packet = send_ack(cliente, sock, data[1])

                        if ( len(msg) < 516 ):
                                
                            with open(f'UDP_CLIENT/{file_name}','w') as f:
                                f.write(file_content)
                                
                            break

                    
                    elif(packet_code==5):
                        
                        unpack_err(msg)
                        break

                else:
                    sock.sendto(last_packet, (ip,int(port)) )   
                    acknowledgment=False
        
        except UnicodeDecodeError as decodeerror:
            print(decodeerror)


        


def end_program(sock,*args,**kwargs):
    raise KeyboardInterrupt("Bye,good to see you")

functions={
    "quit":end_program,
    "read":read,
    "write":write
}

def main(*args,**kwargs):

    print(len(sys.argv))

    if(sys.argv[1]!='-s'or sys.argv[3]!='-p' or len(sys.argv) != 5):
        print("Introduce the arguments in the correct format -> python3 TFTP_UDPClient.py -s 'server direction' -p 'port number' ")
    else:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

            configure_socket(sock,999999)

            while True:
                
                command = input('TFTP@UDP> ')
                arguments = command.split() + sys.argv[1:]
                try:

                    functions[arguments[0].lower()](sock,*arguments[1:])
                except Exception as exception:
                    print(exception)

def configure_socket(sock,maxtimeout):
    timeval = struct.pack('LL',0,maxtimeout)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeval)

def unpack_packetcode(packet):
    code_message = struct.unpack(f'!H{len(packet)-2}s', packet)
    return code_message[0]
 
def unpack_data(packet):
    unpacked_data = struct.unpack(f'!2H{len(packet)-4}s', packet)
    return unpacked_data

def unpack_ack(packet):
    unpacked_ack = struct.unpack(f'!2H', packet)
    return unpacked_ack

def unpack_err(packet):
    unpacked_err = struct.unpack(f'!2H{len(packet)-5}sB', packet)
    print(f"Error number:{unpacked_err[1]} Message:{unpacked_err[2].decode()}")
    return unpacked_err[1],unpacked_err[2].decode()

def send_ack(destination, sock, block):
    packed_ack = struct.pack('!2H', 4 , block) 
    sock.sendto( packed_ack , destination )
    return packed_ack

def send_data(destination,sock,block,data):
    packed_data = struct.pack(f'!2H{len(data)}s', 3 , block+1 , data)
    sock.sendto(packed_data, destination)  
    return packed_data

def sendRRQWRQ(code,file_name,ip,port,sock,encode_mode='netascii'):
    last_packet=struct.pack(f"!H{len(file_name)}sB{len(encode_mode)}sB", code ,str.encode(file_name),0,str.encode(encode_mode),0)
    sock.sendto(last_packet, (ip ,int(port)))
    return last_packet

      

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)

