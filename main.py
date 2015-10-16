'''
Created on Sep 26, 2015

@author: bamboo3250
'''
from threading import Thread
import AudioManager
from MegaCommunicator import MegaCommunicator
from SocketCommunicator import SocketCommunicator
from CameraReader import CameraReader
from KeypadReader import KeypadReader
from Map import MapNavigator
import time

isProgramAlive = True

megaCommunicator = MegaCommunicator()
cameraReader = CameraReader()
keypadReader = KeypadReader()
mapNavigator = MapNavigator()

def obstacleDetected(value):
    return (10 <= value and value < 50)

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

def navigate():
    while True:
        hasNextNode = mapNavigator.getInstruction()
        if hasNextNode == False:
            print "You reached destination!!!"
            break;

def pollData():
    global isProgramAlive
    try:
        while isProgramAlive:
            isSuccessful = megaCommunicator.pollData()
            if isSuccessful:
                if (megaCommunicator.getStep() > 0):
                    mapNavigator.setHeading(megaCommunicator.getHeading())
                    mapNavigator.stepAhead()
                
                if (obstacleDetected(megaCommunicator.getSonar1())):
                    AudioManager.play('left')
        
                if (obstacleDetected(megaCommunicator.getSonar2())):
                    AudioManager.play('right')
        
                if (obstacleDetected(megaCommunicator.getSonar3())):
                    AudioManager.play('warning')
                time.sleep(0.5)
    finally:
        isProgramAlive = False

def sendDataToComp():
    global isProgramAlive
    print "setting up socket"
    socketCommunicator = SocketCommunicator()
    print "finish setting up socket"
    try:
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
                #print "Heading: " + str(heading)
                socketCommunicator.sendInt(mapNavigator.getCurrentBuilding())
                socketCommunicator.sendInt(mapNavigator.getCurrentLevel())
                socketCommunicator.sendInt(mapNavigator.curX)
                socketCommunicator.sendInt(mapNavigator.curY)
                socketCommunicator.sendInt(mapNavigator.curHeading)
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
    startingBlock = keypadReader.getNumber()
    print startingBlock
    
    startingLevel = keypadReader.getNumber()
    print startingLevel
    
    startingId = keypadReader.getNumber()
    print startingId
    
    endingBlock = keypadReader.getNumber()
    print endingBlock
    
    endingLevel = keypadReader.getNumber()
    print endingLevel
    
    endingId = keypadReader.getNumber()
    print endingId
    return [startingBlock, startingLevel, startingId, endingBlock, endingLevel, endingId]

def waitForMegaToStartUp():
    megaCommunicator.waitForMegaToStartUp()
    while True:
        keyPressed = keypadReader.getKeyPressed()
        if (keyPressed == '1'):
            while True:
                print "Sending 1 to stop Calibration"
                rcv = megaCommunicator.send("1");
                print "Received " + rcv
                if (rcv == "A") :
                    print "Calibration is ready!"
                    return

if __name__ == '__main__':
    waitForMegaToStartUp()
    
    while True:
        userInput = getUserInput()
        isValid = mapNavigator.setStartAndEndPoint(userInput)
        if isValid == False :
            print "Invalid path!! Please re-enter!!"
        else :
            break
    
    startThreads()
