'''
Created on Sep 26, 2015

@author: bamboo3250
'''
from time import sleep
import math
from threading import Thread
from AudioManager import AudioManager
from MegaCommunicator import MegaCommunicator
from SocketCommunicator import SocketCommunicator
from CameraReader import CameraReader
from NewMapDownload import downloadMap

isProgramAlive = True
STEP_LENGTH = 38 #cm

buildingId = "1" #COM1
level = "2"
mapHeading = 0

curX = 0
curY = 0

audioManager = AudioManager()
megaCommunicator = MegaCommunicator()
cameraReader = CameraReader()

def obstacleDetected(value):
    return (10 <= value and value < 80)

def startThreads():
    # start polling sensor data from Mega
    pollDataThread = Thread(target = pollData)
    pollDataThread.start()
    
    # start sending data to Comp via Socket
    sendDataToCompThread = Thread(target = sendDataToComp)
    sendDataToCompThread.start()
    
    sendDataToCompThread.join()
    pollDataThread.join()

def calculateNewPos(steps):
    global curX, curY, mapHeading
    curHeading = megaCommunicator.getHeading()
    totalHeading = 90 - (curHeading + mapHeading)
    curX = curX + STEP_LENGTH * math.cos(math.radians(totalHeading));
    curY = curY + STEP_LENGTH * math.sin(math.radians(totalHeading));

def pollData():
    global isProgramAlive
    try:
        while isProgramAlive:
            isSuccessful = megaCommunicator.pollData()
            if isSuccessful:
                if (megaCommunicator.getStep() > 0): 
                    calculateNewPos(megaCommunicator.getStep());
                
                if (obstacleDetected(megaCommunicator.getSonar1())):
                    audioManager.play("left")
        
                if (obstacleDetected(megaCommunicator.getSonar2())):
                    audioManager.play("right")
        
                if (obstacleDetected(megaCommunicator.getSonar3())):
                    audioManager.play("warning")
                sleep(0.5)
    finally:
        isProgramAlive = False


def sendDataToComp():
    global isProgramAlive, curX, curY
    socketCommunicator = SocketCommunicator()
    try:
        while isProgramAlive:
            print "waiting for Hello"
            packet = socketCommunicator.readInt()
            print "packet = " + str(packet)
            if (packet == 2) :
                print "Hello received"
                print "sending ACK"
                socketCommunicator.sendInt(3)
                break
            
            packet = socketCommunicator.readInt()
            print "packet = " + str(packet) 
            if (packet == 123):
                img = cameraReader.getImage()
                length = len(img)
                
                print "Cur Pos: " + str(curX) + ", " + str(curY) ;
                socketCommunicator.sendInt(curX)
                socketCommunicator.sendInt(curY)
                heading = megaCommunicator.getHeading()
                print "Heading: " + str(heading);
                socketCommunicator.sendInt(heading)
                print "Length: " + str(length)
                socketCommunicator.sendInt(length)
                
                socketCommunicator.client_connection.flush()
            elif packet == 222 :
                break
        # Write a length of zero to the stream to signal we're done
        socketCommunicator.sendInt(0)
        
    finally:
        socketCommunicator.closeConnection()
        isProgramAlive = False
            
def getUserInput():
    pass

def downloadMaps():
    global buildingId, level, mapHeading
    mapInfoInput = [buildingId, level]
    mapInfo = downloadMap(mapInfoInput)
    if (mapInfo['info']['northAt'] != "") :
        mapHeading = int(mapInfo['info']['northAt'])

if __name__ == '__main__':
    megaCommunicator.waitForMegaToStartUp()
    getUserInput()
    downloadMaps()
    startThreads()