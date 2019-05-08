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


    def test_nonexistingFile(self):
        print("-------------------TEST EXISTING FILE-------------------")
        print("--------------------RELIABILITY TEST-------------------")
        packets=0

        file_name= ''.join(random.choice(string.ascii_letters) for i in range(15))

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)
            time_start_write=time.time()  
            tftpclient.read(sock,["-s",self.ip,"-p",self.port])
            print(time_start_write)
            self.assertTrue(time_start_write<100)

   

    def tearDown(self):
        self.server_proccess.terminate()
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())