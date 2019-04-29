import unittest
import os
import signal
import subprocess
import socket
import sys
import os
import time
import TFTP_UDPClient as tftpclient
import pexpect

class Reliability_tests(unittest.TestCase):

    def setUp(self):
        print("-------------------SETUP TEST-------------------")
        self.port = 53010
        self.ip = "127.0.0.1"
        self.args = ["python3","TFTP_UDPServer.py","-p", f"{self.port}"]
        self.read_name="filedoesntexists.txt"
        self.write_name="log.txt" 
        self.server_proccess = subprocess.Popen(self.args)


    def test_nofile(self):
        print("-------------------TEST NO FILE-------------------")
        packets=0


        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)
            tftpclient.sendRRQWRQ(1,self.read_name,self.ip,self.port, sock)

            try:

                message,client = sock.recvfrom(516)
                print(client)
                errorcode , errormessage = tftpclient.unpack_err(message)
                self.assertEqual(errormessage,"File Not Found")

                
            except socket.error:
                print("error")

                
    def test_existingfile(self):
        print("-------------------TEST EXISTING FILE-------------------")
        packets=0

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)
            while packets < 10:

                last_packet=tftpclient.sendRRQWRQ(2,self.write_name,self.ip,self.port, sock)

                try:

                    message,client = sock.recvfrom(516)
                    print(client)
                    errorcode , errormessage = tftpclient.unpack_err(message)
                    self.assertEqual(errormessage,"File already exists")
                        
                    break
                    
                except socket.error:
                    packets = packets +1

    def test_existingfile(self):
        print("-------------------TEST EXISTING FILE-------------------")
        packets=0

        with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as sock:
            
            tftpclient.configure_socket(sock,999999)
            while packets < 10:

                last_packet=tftpclient.sendRRQWRQ(2,self.write_name,self.ip,self.port, sock)

                try:

                    message,client = sock.recvfrom(516)
                    print(client)
                    errorcode , errormessage = tftpclient.unpack_err(message)
                    self.assertEqual(errormessage,"File already exists")
                        
                    break
                    
                except socket.error:
                    packets = packets +1


    def tearDown(self):
        self.server_proccess.terminate()
        print("-------------------FINISH TEST-------------------")

if __name__ == "__main__":
    unittest.main(Reliability_tests())