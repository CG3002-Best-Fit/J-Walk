'''
Created on Oct 12, 2015

@author: bamboo3250
'''
import struct
import socket

class SocketCommunicator(object):
    client_socket = None
    server_socket = None
    client_connection = None
    server_connection = None
    
    RPI_IP = "192.168.1.212"
    COM_IP = "192.168.1.107"
    
    def sendInt(self, num):
        self.client_connection.write(struct.pack('>L', num))
        self.client_connection.flush()
    
    def readInt(self):
        return struct.unpack('>L', self.server_connection.read(struct.calcsize('>L')))[0]
    

    def __init__(self):
        # sender
        print "setup client to " + str(self.COM_IP)
        self.client_socket = socket.socket() 
        self.client_socket.connect((self.COM_IP, 8000))
        self.client_connection = self.client_socket.makefile('wb')
        print "finish setup client"
        
        print "sending 1"
        self.sendInt(1);
        
        # receiver
        print "setup server from " + str(self.RPI_IP)
        self.server_socket = socket.socket()
        self.server_socket.bind((self.RPI_IP, 8080))
        self.server_socket.listen(0)
        self.server_connection = self.server_socket.accept()[0].makefile('rb')
        print "finish setup server"
        
    def closeConnection(self):
        self.client_connection.close()
        self.client_socket.close()
        self.server_connection.close()
        self.server_socket.close()