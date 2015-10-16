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
    
    #RPI_IP = "192.168.1.212"   #Sevin
    RPI_IP = "192.168.0.109"   #YuShuen
    #RPI_IP = "172.25.104.193"   #COM1
    #COM_IP = "192.168.1.107"   #Sevin
    COM_IP = "192.168.0.104"   #Yu Shuen
    #COM_IP = "172.25.98.98"    #COM1
    
    def sendInt(self, num):
        self.client_connection.write(struct.pack('>L', num))
    
    def readInt(self):
        return struct.unpack('>L', self.server_connection.read(struct.calcsize('>L')))[0]
    
    def sendArray(self, arr):
        self.client_connection.write(arr) 

    def flush(self):
        self.client_connection.flush()

    def __init__(self):
        # sender
        print "setup client to " + str(self.COM_IP)
        self.client_socket = socket.socket() 
        self.client_socket.connect((self.COM_IP, 8000))
        self.client_connection = self.client_socket.makefile('wb')
        print "finish setup client"
        
        print "sending 1"
        self.sendInt(1)
        self.flush()
        # receiver
        print "setup server from " + str(self.RPI_IP)
        self.server_socket = socket.socket()
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.RPI_IP, 8029))
        self.server_socket.listen(0)
        self.server_connection = self.server_socket.accept()[0].makefile('rb')
        print "finish setup server"
        
    def closeConnection(self):
        self.client_connection.close()
        self.client_socket.close()
        self.server_connection.close()
        self.server_socket.close()
