import unittest
import os
import signal
import subprocess
import socket
import sys
import os
import time
import TFTP_UDPClient as tftpclient

class Reliability_tests(unittest.TestCase):

    def setUp(self):
        self.port = "53002"
        self.ip = "127.0.0.1"
        self.args = ["python3","TFTP_UDPServer.py","-p", f"{self.port}"]
        self.file_name="filedoesntexists.txt"


    def test_nofile(self):
        server_proccess = subprocess.Popen(self.args)
        time.sleep(0.2)

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:

            tftpclient.sendRRQWRQ(1,self.file_name,self.ip,self.port, sock)
            message,client = sock.recvfrom(516)
            server_proccess.send_signal(signal.SIGINT)   # send Ctrl-C signal
            errorcode , errormessage = tftpclient.unpack_err(message)
            self.assertEqual(errormessage,"File Not Found")


    def test_existingfile(self):
        server_proccess = subprocess.Popen(self.args)
        time.sleep(0.2)
        
        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            tftpclient.sendRRQWRQ(2,self.file_name,self.ip,self.port, sock)
            message,client = sock.recvfrom(516)
            server_proccess.send_signal(signal.SIGINT)   # send Ctrl-C signal
            errorcode , errormessage = tftpclient.unpack_err(message)
            self.assertEqual(errormessage,"File already exists")

    def tearDown(self):
        #self.server_proccess.send_signal(signal.SIGINT)   # send Ctrl-C signal
        #stdout, stderr = self.server_proccess.communicate() 
        #print(stdout,stderr)
        print("finish")

if __name__ == "__main__":
    unittest.main(Reliability_tests())