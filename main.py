'''
Created on Sep 26, 2015

@author: bamboo3250
'''
import math
from threading import Thread
from AudioManager import AudioManager
from MegaCommunicator import MegaCommunicator
from SocketCommunicator import SocketCommunicator
from CameraReader import CameraReader
import Map
import RPi.GPIO as GPIO
import time
from StdSuites.AppleScript_Suite import result

isProgramAlive = True
STEP_LENGTH = 38 #cm

buildingId = "1" #COM1
level = "2"
mapHeading = 0

curX = 100
curY = 100
curHeading = 0

shortestPath =[]
graphList = []

audioManager = AudioManager()
megaCommunicator = MegaCommunicator()
cameraReader = None


GPIO.setmode(GPIO.BCM)

MATRIX=[['1','2','3'],
        ['4','5','6'],
        ['7','8','9'],
        ['*','0','#'] ]

COL = [8,4,2] ##connect the pins in reverse: 2,4,8
ROW = [11,9,7,3] ## 3,7,9,11

for j in range(3):
    GPIO.setup(COL[j],GPIO.OUT)
    GPIO.output(COL[j], 1)
    
for i in range(4):
    GPIO.setup(ROW[i],GPIO.IN, pull_up_down = GPIO.PUD_UP)


def obstacleDetected(value):
    return (10 <= value and value < 80)

def startThreads():
    # start polling sensor data from Mega
    pollDataThread = Thread(target = pollData)
    pollDataThread.start()
    
    # start sending data to Comp via Socket
    sendDataToCompThread = Thread(target = sendDataToComp)
    sendDataToCompThread.start()
    
    navigateThread = Thread(target = navigate)
    navigateThread.start()
    
    sendDataToCompThread.join()
    pollDataThread.join()
    navigateThread.join()

def calculateNewPos(steps):
    global curX, curY, mapHeading, curHeading
    curHeading = megaCommunicator.getHeading()
    totalHeading = 90 - (curHeading + mapHeading)
    curX = max(0, curX + STEP_LENGTH * math.cos(math.radians(totalHeading)));
    curY = max(0, curY + STEP_LENGTH * math.sin(math.radians(totalHeading)));

def navigate():
    global shortestPath, graphList, curHeading, curX, curY
    
    while len(shortestPath) > 0:
        shortestPath = Map.travelDirection(curHeading, curX, curY, shortestPath, graphList)
        

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
                time.sleep(0.5)
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
        
        
def getNumberFromKeypad():
    result = ""
    try:
        while(True):
            for j in range(3):
                GPIO.output(COL[j],0)
                
                for i in range(4):
                    if GPIO.input(ROW[i]) == 0:
                        if (MATRIX[i][j] == '#'):
                            return result
                        elif (MATRIX[i][j] == '*'):
                            result = ""
                        else:
                            result = result + MATRIX[i][j]
                        #print MATRIX[i][j]
                        
                GPIO.output(COL[j],1)
                time.sleep(0.05)
        
    except KeyboardInterrupt:
            GPIO.cleanup();
    return result

def getUserInput():
    startingBlock = getNumberFromKeypad()
    print startingBlock
    
    startingLevel = getNumberFromKeypad()
    print startingLevel
    
    startingId = getNumberFromKeypad()
    print startingId
    
    endingBlock = getNumberFromKeypad()
    endingLevel = getNumberFromKeypad()
    endingId = getNumberFromKeypad()
    

def downloadMaps():
    global buildingId, level, mapHeading
    mapInfoInput = [buildingId, level]
    mapInfo = Map.downloadMap(mapInfoInput)
    if (mapInfo['info']['northAt'] != "") :
        mapHeading = int(mapInfo['info']['northAt'])

if __name__ == '__main__':
    global shortestPath, graphList
    
    megaCommunicator.waitForMegaToStartUp()
    getUserInput()
    #downloadMaps()
    
    info = Map.startup()
    startNode = info[0]
    endNode = info[1]
    buildingInfo = info[2]
    totalInfoMatrix = info[3]
    
    graphList = Map.parseInfo(buildingInfo, totalInfoMatrix)
    shortestPath = Map.shortestPath(graphList, startNode, endNode)
    
    startThreads()
