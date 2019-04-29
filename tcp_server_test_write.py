import unittest
import os
import signal
import subprocess
import socket
import sys
import os
import time
import TFTP_TCPClient as tftpclient

class Reliability_tests(unittest.TestCase):

    def setUp(self):
        self.port = "53002"
        self.ip = "127.0.0.1"
        self.args = ["python3.7","TFTP_TCPServer.py","-p", f"{self.port}"]
        self.file_name="filedoesntexists.txt"
        
    def test_existingfile(self):
        server_proccess = subprocess.Popen(self.args)
        time.sleep(0.2)
        
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:
    
            sock.connect((self.ip,int(self.port)))
            packet = tftpclient.sendRRQWRQ(2,self.file_name, sock)
            message = sock.recv(516)
            confirm_code = tftpclient.autentication_message(message)
            server_proccess.send_signal(signal.SIGINT)   # send Ctrl-C signal
            #errormessage = tftpclient.unpack_err_write_test(message,confirm_code)
            #self.assertEqual(errormessage[2].decode(),"File Already Exists")
            self.assertEqual(confirm_code,5)

    def tearDown(self):
        #self.server_proccess.send_signal(signal.SIGINT)   # send Ctrl-C signal
        #stdout, stderr = self.server_proccess.communicate() 
        #print(stdout,stderr)
        print("finish")

if __name__ == "__main__":
    unittest.main(Reliability_tests())