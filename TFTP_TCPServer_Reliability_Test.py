
import unittest
import os
import signal
import subprocess
import socket
import sys
import os
import time
import TFTP_TCPClient as tftpclient
from random import choices
import string

class Reliability_tests(unittest.TestCase):

    def setUp(self):
        print("-------------------SETUP TEST-------------------")
        self.port = "53011"
        self.ip = "127.0.0.1"
        self.args = ["python3.7","TFTP_TCPServer.py","-p",f"{self.port}"]
        self.file_name_read="rrq.txt"
        self.file_name_write="filedoesntexists.txt"
        self.server_proccess = subprocess.Popen(self.args)
        
        

    def test_nofile(self):
        print("\n")
        print("-------------------TEST NO FILE-------------------")
        print("port=",self.port)
        print("ip=",self.ip)
        print("Server=",self.args)
        print("file=",self.file_name_read)
        time.sleep(0.2)
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            sock.connect((self.ip,int(self.port)))
            packet = tftpclient.sendRRQWRQ(1,self.file_name_read, sock)
            while True:
                packed_data = sock.recv(516)
                code = tftpclient.unpack_packetcode(packed_data)
                errormessage = tftpclient.unpack_err(packed_data)
                if code!=3:
                    break
            self.assertEqual(code,5)

    def test_existingfile(self):
        print("\n")
        print("-------------------TEST EXISTING FILE-------------------")
        print("port=",self.port)
        print("ip=",self.ip)
        print("Server=",self.args)
        print("file=",self.file_name_write)
        time.sleep(0.2)
        
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
    
            sock.connect((self.ip,int(self.port)))
            packet = tftpclient.sendRRQWRQ(2,self.file_name_write, sock)
            ack = sock.recv(516)
            code=tftpclient.unpack_packetcode(ack)
            if code==4:
                pass
            errormessage=tftpclient.unpack_err(ack)   
            self.assertEqual(code,5)          

    
    def tearDown(self):
        self.server_proccess.terminate()
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())
