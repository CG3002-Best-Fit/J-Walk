import io
import socket
import struct
import time
import picamera

class MyCamera:
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

    def sendImage(self):
        #init()
        
        try:
            with picamera.PiCamera() as camera:
                camera.resolution = (640, 480)
                # Start a preview and let the camera warm up for 2 seconds
                camera.start_preview()
                time.sleep(2)
        
                # Note the start time and construct a stream to hold image data
                # temporarily (we could write it directly to connection but in this
                # case we want to find out the size of each capture first to keep
                # our protocol simple)
                #start = time.time()
                while True:
                    print "waiting for Hello"
                    packet = self.readInt()
                    print "packet = " + str(packet)
                    if (packet == 2) :
                        print "Hello received"
                        print "sending ACK"
                        self.sendInt(3)
                        break
                
                
                stream = io.BytesIO()
                for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                    # Write the length of the capture to the stream and flush to
                    # ensure it actually gets sent
                    packet = self.readInt()
                    print "packet = " + str(packet) 
                    if (packet == 123):
                        length = stream.tell()
                        heading = getHeading()
                        print "Heading: " + str(heading);
                        self.sendInt(heading)
                        print "Length: " + str(length)
                        self.sendInt(length)
                        
                        # Rewind the stream and send the image data over the wire
                        stream.seek(0)
                        arr = stream.read()
                        self.client_connection.write(arr)
                        # If we've been capturing for more than 30 seconds, quit
                        #if time.time() - start > 30:
                        #    break
                        # Reset the stream for the next capture
                        stream.seek(0)
                        stream.truncate()
                        self.client_connection.flush()
                    elif packet == 222 :
                        break
            # Write a length of zero to the stream to signal we're done
            self.sendInt(0)
            
        finally:
            self.client_connection.close()
            self.client_socket.close()
            self.server_connection.close()
            self.server_socket.close()
        
if __name__ == '__main__':
    myCamera = MyCamera()
    myCamera.sendImage()
    