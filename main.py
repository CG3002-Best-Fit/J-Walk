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
from Map import downloadMap

isProgramAlive = True
STEP_LENGTH = 38 #cm

buildingId = "1" #COM1
level = "2"
mapHeading = 0

curX = 100
curY = 100

audioManager = AudioManager()
megaCommunicator = MegaCommunicator()
cameraReader = None

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
    curX = max(0, curX + STEP_LENGTH * math.cos(math.radians(totalHeading)));
    curY = max(0, curY + STEP_LENGTH * math.sin(math.radians(totalHeading)));

def pollData():
    global isProgramAlive
    try:
        while isProgramAlive:
            isSuccessful = megaCommunicator.pollData()
            if isSuccessful:
                if (megaCommunicator.getStep() > 0): 
                    calculateNewPos(megaCommunicator.getStep());
                
                if (obstacleDetected(megaCommunicator.getSonar1())):
                    audioManager.playLeft()
        
                if (obstacleDetected(megaCommunicator.getSonar2())):
                    audioManager.playRight()
        
                if (obstacleDetected(megaCommunicator.getSonar3())):
                    audioManager.playWarning()
                sleep(0.5)
    finally:
        isProgramAlive = False


def sendDataToComp():
    global isProgramAlive, curX, curY
    print "setting up socket"
    socketCommunicator = SocketCommunicator()
    print "finish setting up socket"
    try:
        cameraReader = CameraReader()
        print "waiting for Hello"
        packet = socketCommunicator.readInt()
        print "packet = " + str(packet)
        if (packet == 2) :
            print "Hello received"
            print "sending ACK"
            socketCommunicator.sendInt(3)
            socketCommunicator.flush()
        
        while isProgramAlive:            
            packet = socketCommunicator.readInt()
            #print "packet = " + str(packet) 
            if (packet == 123):
                img = cameraReader.getImage()
                length = len(img)
                #print "length of Image = " + str(length)
                
                #print "Cur Pos: " + str(curX) + ", " + str(curY)
                socketCommunicator.sendInt(curX)
                socketCommunicator.sendInt(curY)
                heading = megaCommunicator.getHeading()
                #print "Heading: " + str(heading)
                socketCommunicator.sendInt(heading)
                #print "Length: " + str(length)
                socketCommunicator.sendInt(length)
                if (len(img) > 0):
                    socketCommunicator.sendArray(img)
                
                socketCommunicator.flush()
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
