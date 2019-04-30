import unittest
import signal
import subprocess
import socket
import time
import TFTP_UDPClient as tftpclient
from random import choices
import string

class Reliability_tests(unittest.TestCase):

    def setUp(self):
        print("-------------------SETUP TEST-------------------")
        self.port = 53010
        self.ip = "127.0.0.1"
        self.args = ["python3","TFTP_UDPServer.py","-p", f"{self.port}"]
        self.server_proccess = subprocess.Popen(self.args)


    def test_noFile(self):
        print("-------------------TEST NO FILE-------------------")
        packets=0
        
        file_name = "filedoesntexists.txt"


        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)
            tftpclient.sendRRQWRQ(1,file_name,self.ip,self.port, sock)
            while True:
                try:

                    message,client = sock.recvfrom(516)
                    errorcode , errormessage = tftpclient.unpack_err(message)
                    self.assertEqual(errormessage,"File Not Found")
                    break

                    
                except socket.error:
                    print("error")

                
    def test_existingFile(self):
        print("-------------------TEST EXISTING FILE-------------------")
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

    def test_lostACK(self):
        print("-------------------TEST LOST ACKNOWLEDGMENT-------------------")

        packets=0
        timeout=0
        maxpackets = 4
        maxtimeout = 4

        file_name="ack.txt" #This file must exist

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:

            tftpclient.configure_socket(sock,999999)

            while True:   

                try:

                    last_packet=tftpclient.sendRRQWRQ(1,file_name,self.ip,self.port, sock)
                    message,client = sock.recvfrom(516)
                    break

                except socket.error:
                    pass
                    
            while packets < maxpackets or timeout < maxtimeout :

                try:

                    message,client = sock.recvfrom(516)
                    packets=packets+1
                    print(packets)

                except socket.error:
                    print("error")
                    timeout = timeout +1

            self.assertNotEqual(packets,15)


    def test_lostData(self):
        print("-------------------TEST LOST DATA-------------------")

        packets=0
        timeout=0
        maxpackets = 4
        maxtimeout = 4

        file_name="data.txt" 

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:

            tftpclient.configure_socket(sock,999999)

            while True:   

                try:

                    last_packet=tftpclient.sendRRQWRQ(2,file_name,self.ip,self.port, sock)
                    message,client = sock.recvfrom(516)
                    break

                except socket.error:
                    print("error")
                    pass
                    
            while packets < maxpackets or timeout < maxtimeout :

                try:

                    message,client = sock.recvfrom(516)
                    packets=packets+1
                    print(packets)

                except socket.error:
                    print("error")
                    timeout = timeout +1

            self.assertNotEqual(packets,15)
    


    def tearDown(self):
        self.server_proccess.terminate()
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())