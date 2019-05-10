
import unittest
import subprocess
import socket
import time
import TFTP_TCPClient as tftpclient
from random import choices
import string

class Reliability_tests(unittest.TestCase):

    def setUp(self):
        print("-------------------SETUP TEST-------------------")
        self.port = "53011"
        self.ip = "127.0.0.1"
        self.args = ["python3","TFTP_TCPServer.py","-p",f"{self.port}"]
        print("port=",self.port)
        print("ip=",self.ip)
        print("Server=",self.args)

        
        

    def test_nofile(self):
        print("\n")
        print("-------------------TEST NO FILE-------------------")

        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            file_name_read=''.join(choices(string.ascii_letters) for i in range(15))
            #This file must not exist in UDP_SERVER DIRECTORY
            print("file=",file_name_read)

            sock.connect((self.ip,int(self.port)))
            packet = tftpclient.sendRRQWRQ(1,self.file_name_read, sock)
            packed_data = sock.recv(516)
            code = tftpclient.unpack_packetcode(packed_data)
            errormessage = tftpclient.unpack_err(packed_data)
            self.assertEqual(code,5)

    def test_existingfile(self):
        print("\n")
        print("-------------------TEST EXISTING FILE-------------------")
        
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:

            self.file_name_write="filedoesntexists.txt" 
            #This file must exist in UDP_SERVER DIRECTORY
            print("file=",self.file_name_write)
    
            sock.connect((self.ip,int(self.port)))
            packet = tftpclient.sendRRQWRQ(2,self.file_name_write, sock)
            ack = sock.recv(516)
            code=tftpclient.unpack_packetcode(ack)
            errormessage=tftpclient.unpack_err(ack)   
            self.assertEqual(code,5)          

    
    def tearDown(self):
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())
