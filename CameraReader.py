'''
Created on Oct 12, 2015

@author: bamboo3250
'''
import picamera
from threading import Thread
import time, io

class CameraReader(object):
    imageQueue = []
    sendImageThread = Thread(target = startReadingImage)
    
    def __init__(self):
        self.sendImageThread.start()
    
    def joinThread(self):
        self.sendImageThread.join()
    
    def startReadingImage(self):
        with picamera.PiCamera() as camera:
            camera.resolution = (640, 480)
            # Start a preview and let the camera warm up for 2 seconds
            camera.start_preview()
            time.sleep(2)
    
            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg', use_video_port=True):
                stream.seek(0)
                buf = stream.read()
                self.imageQueue.append(buf)
    
    def getImage(self):
        lastImageIndex = len(self.imageQueue) - 1
        if (lastImageIndex >= 0):
            result = self.imageQueue[lastImageIndex]
            while len(self.imageQueue) > 0:
                self.imageQueue.pop(0)
            return result
        return []