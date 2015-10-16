'''
Created on Oct 12, 2015

@author: bamboo3250
'''
import picamera
from threading import Thread
import time, io

class CameraReader(object):
    imageQueue = []
    readImageThread = None
    camera = None
    isCameraStopped = False
    
    def startReadingImage(self):
        try:
            with picamera.PiCamera() as self.camera:
                self.camera.resolution = (640, 480)
                # Start a preview and let the camera warm up for 2 seconds
                #camera.start_preview()
                time.sleep(2)
        
                stream = io.BytesIO()
                for foo in self.camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                    stream.seek(0)
                    buf = stream.read()
                    self.imageQueue.append(buf)
                    while (len(self.imageQueue) > 10):
                        self.imageQueue.pop(0)  
                    #print "length of Image Queue: " + str(len(self.imageQueue)) + " " + str(len(buf))
                    stream.seek(0)
                    stream.truncate()
                    
                    if self.isCameraStopped:
                        break
                self.camera.close()
        except:
            if self.camera != None:
                self.camera.close()
            print "Camera is not working..."
      
    def __init__(self):
        self.readImageThread = Thread(target = self.startReadingImage)
        self.readImageThread.start()
    
    def joinThread(self):
        self.readImageThread.join()
    
    def getImage(self):
        lastImageIndex = len(self.imageQueue) - 1
        if (lastImageIndex >= 0):
            return self.imageQueue[lastImageIndex]
        return []
    
    def close(self):
        self.isCameraStopped = True
        
