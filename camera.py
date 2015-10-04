import io
import socket
import struct
import time
import picamera

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)

# sender
print "setup client"
client_socket = socket.socket() 
client_socket.connect(('192.168.0.104', 8000))
client_connection = client_socket.makefile('wb')
print "finish setup client"

def sendInt(num):
    client_connection.write(struct.pack('>L', num))
    client_connection.flush()
    
print "sending 1"
sendInt(1);

# receiver
print "setup server"
server_socket = socket.socket()
server_socket.bind(('192.168.0.105', 8080))
server_socket.listen(0)
server_connection = server_socket.accept()[0].makefile('rb')
print "finish setup server"

def readInt():
    return struct.unpack('>L', server_connection.read(struct.calcsize('>L')))[0]

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
            packet = readInt()
            print "packet = " + str(packet)
            if (packet == 2) :
                print "Hello received"
                print "sending ACK"
                sendInt(3)
                break
        
        
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
            # Write the length of the capture to the stream and flush to
            # ensure it actually gets sent
            packet = readInt()
            print "packet = " + str(packet) 
            if (packet == 123):
                length = stream.tell()
                print length
                sendInt(length)
                
                # Rewind the stream and send the image data over the wire
                stream.seek(0)
                arr = stream.read()
                client_connection.write(arr)
                # If we've been capturing for more than 30 seconds, quit
                #if time.time() - start > 30:
                #    break
                # Reset the stream for the next capture
                stream.seek(0)
                stream.truncate()
                client_connection.flush()
            elif packet == 222 :
                break
    # Write a length of zero to the stream to signal we're done
    sendInt(0)
    
finally:
    client_connection.close()
    client_socket.close()