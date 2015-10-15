'''
Created on Oct 12, 2015

@author: bamboo3250
'''
import picamera
from threading import Thread
import time, io

class CameraReader(object):
    imageQueue = []
    sendImageThread = None    

    def startReadingImage(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            # Start a preview and let the camera warm up for 2 seconds
            #camera.start_preview()
            #time.sleep(2)
    
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                stream.seek(0)
                buf = stream.read()
                self.imageQueue.append(buf)
                while (len(self.imageQueue) > 10):
                    self.imageQueue.pop(0)  
                #print "length of Image Queue: " + str(len(self.imageQueue)) + " " + str(len(buf))
                stream.seek(0)
                stream.truncate()
      
    def __init__(self):
        self.sendImageThread = Thread(target = self.startReadingImage)
        self.sendImageThread.start()
    
    def joinThread(self):
        self.sendImageThread.join()
    
    def getImage(self):
        lastImageIndex = len(self.imageQueue) - 1
        if (lastImageIndex >= 0):
            result = self.imageQueue[lastImageIndex]
            #while len(self.imageQueue) > 0:
            #    self.imageQueue.pop(0)
            return result
        return []
