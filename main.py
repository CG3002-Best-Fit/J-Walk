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
cameraReader = None #CameraReader()
keypadReader = KeypadReader()
mapNavigator = MapNavigator()
socketCommunicator = None

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
    
    #sendDataToCompThread.join()
    pollDataThread.join()
    navigateThread.join()

def navigate():
    global isProgramAlive
    try:
        while isProgramAlive:
            hasNextNode = mapNavigator.getInstruction()
            if hasNextNode == False:
                print "You reached destination!!!"
                break;
            time.sleep(1)
    except:
        print "Oops! Something went wrong in navigate()!"
        isProgramAlive = False
    
    print "Navigation is stopping..."

def pollData():
    global isProgramAlive, mapNavigator
    try:
        while isProgramAlive:
            isSuccessful = True#megaCommunicator.pollData()
            if isSuccessful:
                mapNavigator.setHeading(megaCommunicator.getHeading())
                if (megaCommunicator.getStep() > 0):
                    mapNavigator.stepAhead()
                
                if (obstacleDetected(megaCommunicator.getSonar1())):
                    AudioManager.play('left')
        
                if (obstacleDetected(megaCommunicator.getSonar2())):
                    AudioManager.play('right')
        
                if (obstacleDetected(megaCommunicator.getSonar3())):
                    AudioManager.play('warning')
                time.sleep(0.5)
    except :
        print "Oops! Something went wrong in pollData()!"
        isProgramAlive = False
    
    print "Exiting pollData()..."

def sendDataToComp():
    global isProgramAlive, mapNavigator, socketCommunicator, cameraReader
    try:
        while isProgramAlive:            
            packet = socketCommunicator.readInt()
            #print "packet = " + str(packet) 
            if (packet == 2) :
                print "Hello received"
                print "sending ACK"
                socketCommunicator.sendInt(3)
                socketCommunicator.flush()
            elif (packet == 123):
                if cameraReader == None:
                    cameraReader = CameraReader()
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
    except:
        print "Oops! Socket or Camera went wrong..."
        isProgramAlive = False
    
    print "Exiting sendDataToComp()"
        
def getUserInput():
    print "Enter Start Block:"
    AudioManager.play('enter_building')
    startingBlock = keypadReader.getNumber()
    print "Start Block: " + str(startingBlock)
    
    print "Enter Start Level:"
    AudioManager.play('enter_level')
    startingLevel = keypadReader.getNumber()
    print "Start Level: " + str(startingLevel)
    
    print "Enter Start Id:"
    AudioManager.play('enter')
    startingId = keypadReader.getNumber()
    print "Start Id: " + str(startingId)
    
    print "Enter End Block:"
    AudioManager.play('enter_building')
    endingBlock = keypadReader.getNumber()
    print "End Block: " + str(endingBlock)
    
    print "Enter End Level:"
    AudioManager.play('enter_level')
    endingLevel = keypadReader.getNumber()
    print "End Level: " + str(endingLevel)
    
    print "Enter End Id:"
    AudioManager.play('enter')
    endingId = keypadReader.getNumber()
    print "End Id: " + str(endingId)
    
    return [startingBlock, startingLevel, startingId, endingBlock, endingLevel, endingId]

def waitForMegaToStartUp():
    megaCommunicator.waitForMegaToStartUp()
    while True:
        print "Press 1 to stop Calibration!" 
        keyPressed = keypadReader.getKeyPressed()
        if (keyPressed == '1'):
            while True:
                print "Sending 1 to stop Calibration"
                rcv = megaCommunicator.send("1");
                print "Received " + rcv
                if (rcv == "A") :
                    print "Calibration is finished!"
                    return

def init():
    global socketCommunicator
    try:
        #waitForMegaToStartUp()
        
        while True:
            userInput = getUserInput()
            isValid = mapNavigator.setStartAndEndPoint(userInput)
            if isValid == False :
                print "(" + str(userInput[0]) + ", " + userInput[1] + ", " + userInput[2] 
                print "Invalid path!! Please re-enter!!"
            else :
                break
        
        print "setting up socket"
        socketCommunicator = SocketCommunicator()
        if (socketCommunicator.isConnectionSuccessful == False):
            socketCommunicator.closeConnection()
            print "Connection Failed!"
            return False
        else :
            print "finish setting up socket"
        return True
    except:
        
        return False

if __name__ == '__main__':
    Thread(target = AudioManager.loadBGM).start()   # play background music
    AudioManager.init()                             # create thread to play audio
    isEverythingReady = init()                      # check everything is ready
    #AudioManager.stopBGM()                          # stop background music
    if isEverythingReady:
        print "Starting threads..."
        startThreads()
    
    print "Oops! Something went wrong. The program will be terminated..."
    AudioManager.closeAudio()
    
    if (cameraReader != None):
        cameraReader.close()
        print "Closed the camera"
    
    if (socketCommunicator != None):
        socketCommunicator.closeConnection()
        print "Closed connections"
        