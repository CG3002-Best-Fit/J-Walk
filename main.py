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
willProgramBeReseted = True

megaCommunicator = MegaCommunicator()
cameraReader = None #CameraReader()
keypadReader = KeypadReader()
mapNavigator = MapNavigator()
socketCommunicator = None

def obstacleDetected(value):
    return (10 <= value and value < 50)

def startThreads():
    
    terminateSystemByKeypadThread = Thread(target = terminateSystemByKeypad)
    terminateSystemByKeypadThread.start()
    
    # start polling sensor data from Mega
    pollDataThread = Thread(target = pollData)
    pollDataThread.start()
    
    # start sending data to Comp via Socket
    sendDataToCompThread = Thread(target = sendDataToComp)
    sendDataToCompThread.start()
    
    navigateThread = Thread(target = navigate)
    navigateThread.start()
    
    try:
        terminateSystemByKeypadThread.join()
    except:
        isProgramAlive = False
    
    try:
        sendDataToCompThread.join()
    except:
        pass
    
    try:
        pollDataThread.join()
    except:
        isProgramAlive = False
    
    try:
        navigateThread.join()
    except:
        isProgramAlive = False

def terminateSystemByKeypad():
    global isProgramAlive
    try:
        while isProgramAlive:
            keyPressed = keypadReader.getKeyPressed()
            if keyPressed == '*':
                print "System is shutting down!!!"
                isProgramAlive = False
                break;
            elif keyPressed == '#':
                print "System is being reseted!!!"
                willProgramBeReseted = True
                isProgramAlive = False
                break;
    except:
        print "Oops! Something went wrong in terminateSystemByKeypad()!"
        isProgramAlive = False

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
            isSuccessful = megaCommunicator.pollData()
            if isSuccessful:
                mapNavigator.setHeading(megaCommunicator.getHeading())
                if (megaCommunicator.getStep() > 0):
                    mapNavigator.stepAhead(megaCommunicator.getStep())
                print "acc = " + str(megaCommunicator.getAcc())
                #if (obstacleDetected(megaCommunicator.getSonar1())):
                #    AudioManager.play('obstacle_left')
        
                #if (obstacleDetected(megaCommunicator.getSonar2())):
                #    AudioManager.play('obstacle_right')
        
                #if (obstacleDetected(megaCommunicator.getSonar3())):
                #    AudioManager.play('obstacle_ahead')
                time.sleep(0.5)
    except :
        print "Oops! Something went wrong in pollData()!"
        isProgramAlive = False
    
    print "Exiting pollData()..."

def sendDataToComp():
    global isProgramAlive, mapNavigator, socketCommunicator, cameraReader
    if socketCommunicator.isConnectionSuccessful:
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
                    #if cameraReader == None:
                    #    cameraReader = CameraReader()
                    #img = cameraReader.getImage()
                    #length = len(img)
                    #print "length of Image = " + str(length)
                    
                    #print "Cur Pos: " + str(curX) + ", " + str(curY)
                    #print "Heading: " + str(heading)
                    socketCommunicator.sendInt(mapNavigator.getCurrentBuilding())
                    socketCommunicator.sendInt(mapNavigator.getCurrentLevel())
                    socketCommunicator.sendInt(mapNavigator.curX)
                    socketCommunicator.sendInt(mapNavigator.curY)
                    socketCommunicator.sendInt(mapNavigator.curHeading)
                    #print "Length: " + str(length)
                    length = 0
                    socketCommunicator.sendInt(length)
                    #if (length > 0):
                    #    socketCommunicator.sendArray(img)
                    
                    socketCommunicator.flush()
                elif packet == 222 :
                    break
            # Write a length of zero to the stream to signal we're done
            socketCommunicator.sendInt(0)
        except:
            print "Oops! Socket or Camera went wrong... but the program still continues..."
            #isProgramAlive = False
    
    print "Exiting sendDataToComp()"
        
def getUserInput():
    print "Enter Start Block:"
    AudioManager.play('enter_building')
    print "Try getting a number"
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
        print "keyPressed = " + keyPressed
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
        waitForMegaToStartUp()
        
        while True:
            try :
                userInput = getUserInput()
                isValid = mapNavigator.setStartAndEndPoint(userInput)
                if isValid == False :
                    print "(" + str(userInput[0]) + ", " + userInput[1] + ", " + userInput[2] 
                    print "Invalid path!! Please re-enter!!"
                else :
                    break
            except ValueError:
                print "Reset input!! Please re-enter!!"
                continue
            
        
        print "setting up socket"
        socketCommunicator = SocketCommunicator()
        if (socketCommunicator.isConnectionSuccessful == False):
            socketCommunicator.closeConnection()
            print "Connection Failed!"
        else :
            print "finish setting up socket"
        return True
    except:
        print "Init has problem!!!"
        return False

if __name__ == '__main__':
    while willProgramBeReseted:
        isProgramAlive = True
        willProgramBeReseted = False
    
        Thread(target = AudioManager.loadBGM).start()   # play background music
        AudioManager.init()                             # create thread to play audio
        isEverythingReady = init()                      # check everything is ready
        AudioManager.stopBGM()                          # stop background music
        if isEverythingReady:
            print "Starting threads..."
            startThreads()
        
        print "Oops! Something went wrong. The program will be terminated..."
        AudioManager.closeAudio()
        
        if (cameraReader != None):
            cameraReader.close()
            print "Closed the camera"
        
        if (socketCommunicator != None and socketCommunicator.isConnectionSuccessful):
            socketCommunicator.closeConnection()
            print "Closed connections"
        