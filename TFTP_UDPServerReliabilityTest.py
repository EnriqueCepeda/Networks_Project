import unittest
import signal
import subprocess
import socket
import time
import TFTP_UDPClient as tftpclient
import random
import string


class Reliability_tests(unittest.TestCase):

    def setUp(self):
        print("-------------------SETUP TEST-------------------")
        self.port = 53011
        self.ip = "127.0.0.1"
        self.args = ["python3","TFTP_UDPServer.py","-p", f"{self.port}"]
        self.server_proccess = subprocess.Popen(self.args)

                
    def test_existingFile(self):
        print("-------------------TEST EXISTING FILE-------------------")
        print("--------------------RELIABILITY TEST-------------------")
        packets=0

        file_name="log.txt" 
        max_packets=4

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)

            while packets < max_packets:

                last_packet=tftpclient.sendRRQWRQ(2,file_name,self.ip,self.port, sock)

                try:

                    message,client = sock.recvfrom(516)
                    errorcode , errormessage = tftpclient.unpack_err(message)
                    self.assertEqual(errormessage,"File already exists")  
                    break
                    
                except socket.error:
                    packets = packets +1
                    print("error")

    def test_nonexistingFile(self):
        print("-------------------TEST EXISTING FILE-------------------")
        print("--------------------RELIABILITY TEST-------------------")
        packets=0

        file_name="log1.txt" 
        max_packets=4

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)

            while packets < max_packets:

                last_packet=tftpclient.sendRRQWRQ(1,file_name,self.ip,self.port, sock)

                try:

                    message,client = sock.recvfrom(516)
                    errorcode , errormessage = tftpclient.unpack_err(message)
                    self.assertEqual(errormessage,"File Not Found")  
                    break
                    
                except socket.error:
                    packets = packets +1
                    print("error")

    def test_lostACK(self):
        print("-------------------TEST LOST ACKNOWLEDGMENT-------------------")
        print("-----------------------RELIABILITY TEST-----------------------")

        retransmited_packets=0
        maxpackets = 4
        timeout=0

        file_name="ack.txt" #This file must exist in UDP_SERVER directory and must be bigger than 512 bytes

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:

            tftpclient.configure_socket(sock,999999)

            while True:   

                try:

                    last_packet=tftpclient.sendRRQWRQ(1,file_name,self.ip,self.port, sock)
                    message,client = sock.recvfrom(516)
                    break

                except socket.error:
                    pass
                    
            while retransmited_packets < maxpackets :
                if timeout == 10:
                    break

                try:

                    message,client = sock.recvfrom(516)
                    retransmited_packets = retransmited_packets +1
                    print(f"{retransmited_packets} retransmited packets")

                except socket.error:
                    timeout = timeout +1

            self.assertEqual(retransmited_packets,maxpackets)

    def test_lostData(self):
        print("-------------------TEST LOST DATA-------------------")
        print("-------------------RELIABILITY TEST-----------------------")

        retransmited_acks=0
        maxacks = 4
        timeout=0

        file_name = ''.join(random.choice(string.ascii_letters) for i in range(15))
        #Generation of random name
        
        #This file must not exist in UDP_SERVER directory and must be bigger than 512 bytes

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:

            tftpclient.configure_socket(sock,999999)

            while True:   

                try:

                    last_packet=tftpclient.sendRRQWRQ(2,file_name,self.ip,self.port, sock)
                    message,client = sock.recvfrom(516)
                    break

                except socket.error:
                    pass
                    
            while retransmited_acks < maxacks :
                if timeout == 10:
                    break

                try:

                    message,client = sock.recvfrom(516)
                    retransmited_acks = retransmited_acks +1
                    print(f"{retransmited_acks} retransmited acks")

                except socket.error:
                    timeout = timeout +1

            self.assertEqual(retransmited_acks,maxacks)



    def tearDown(self):
        self.server_proccess.terminate()
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())