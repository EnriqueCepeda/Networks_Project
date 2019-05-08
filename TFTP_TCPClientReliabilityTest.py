import unittest
import signal
import subprocess
import socket
import time
import TFTP_TCPClient as tftpclient
import random
import string
import pdb


class Reliability_tests(unittest.TestCase):

    def setUp(self):
        print("-------------------SETUP TEST-------------------")
        self.port = 53011
        self.ip = "127.0.0.1"

    def test_nonexistingFile(self):
        print("-------------------TEST NON EXISTING FILE-------------------")
        print("--------------------RELIABILITY TEST-------------------")

        file_name= ''.join(random.choice(string.ascii_letters) for i in range(15))

        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
            
            args=[file_name,"-s",self.ip,"-p",self.port] 
            time_start_write=time.time() 

            tftpclient.write(sock,*args)
            
            time_end_write=time.time() 

            self.assertTrue(time_start_write-time_end_write<0.1)

    def tearDown(self):
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())