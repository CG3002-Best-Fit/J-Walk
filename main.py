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
from GridMapNavigator import GridMapNavigator
import time

isProgramAlive = True
willProgramBeReseted = True

megaCommunicator = MegaCommunicator()
cameraReader = None #CameraReader()
keypadReader = KeypadReader()
mapNavigator = MapNavigator()
gridMapNavigator = GridMapNavigator()
socketCommunicator = None

def obstacleDetected(value):
    return (10 <= value and value < 100)

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
    global isProgramAlive, willProgramBeReseted
    try:
        while isProgramAlive:
            keyPressed = keypadReader.getKeyPressed()
            if keyPressed == '*':
                print "System is shutting down!!!"
                isProgramAlive = False
                break
            elif keyPressed == '#':
                print "System is being reseted!!!"
                willProgramBeReseted = True
                isProgramAlive = False
                break
            elif keyPressed == '0':
                doCalibration()
                break
    except:
        print "Oops! Something went wrong in terminateSystemByKeypad()!"
        isProgramAlive = False

def navigate():
    print "Start Navigating"
    global isProgramAlive, mapNavigator, gridMapNavigator
    try:
        while isProgramAlive:
            #hasNextNode = mapNavigator.getInstruction()
            gridMapNavigator.getInstruction()
            if gridMapNavigator.hasReachedDestination:
                print "You reached destination!!!"
                break;
            time.sleep(2)
    except:
        print "Oops! Something went wrong in navigate()!"
        isProgramAlive = False
    
    print "Navigation is stopping..."

def pollData():
    global isProgramAlive, mapNavigator
    try:
        counterToPutObstacle1 = 2
        counterToPutObstacle2 = 2
        counterToPutObstacle3 = 2
        counterToRemoveObstacle1 = 2
        while isProgramAlive:
            while gridMapNavigator.isCalculating:
                pass
            isSuccessful = megaCommunicator.pollData()
            if isSuccessful:
                #mapNavigator.setHeading(megaCommunicator.getHeading())
                gridMapNavigator.curHeading = megaCommunicator.getHeading()
                if (megaCommunicator.getStep() > 0):
                    #mapNavigator.stepAhead(megaCommunicator.getStep())
                    print "Stepped ahead", megaCommunicator.getStep()
                    gridMapNavigator.stepAhead(megaCommunicator.getStep())
                #print "acc = " + str(megaCommunicator.getAcc())
                
                if (megaCommunicator.getSonar1() == 1) and (gridMapNavigator.isInStaircaseMode == False): # straight ahead sonar
                    print "Front clear!!!"
                    if counterToPutObstacle1 > 0:
                        counterToPutObstacle1 = counterToPutObstacle1 - 1
                    if counterToPutObstacle1 == 0:
                        counterToPutObstacle1 = 2
                        gridMapNavigator.putObstacle(0)
                    counterToRemoveObstacle1 = 2
                else :
                    print "Front not clear!!!"
                    if counterToRemoveObstacle1 > 0:
                        counterToRemoveObstacle1 = counterToRemoveObstacle1 - 1
                    if counterToRemoveObstacle1 == 0:
                        counterToRemoveObstacle1 = 2
                        gridMapNavigator.removeObstacle(0)
                        gridMapNavigator.detectNoWall(0)
                    counterToPutObstacle1 = 2
                    
                if (megaCommunicator.getSonar2() == 1) and (gridMapNavigator.isInStaircaseMode == False): # left sonar
                    print "Left clear!!!"
                    if counterToPutObstacle2 > 0:
                        counterToPutObstacle2 = counterToPutObstacle2 - 1
                    if counterToPutObstacle2 == 0:
                        counterToPutObstacle2 = 2
                        #gridMapNavigator.putObstacle(-45)
                else :
                    print "Left not clear!!!"
                    counterToPutObstacle2 = 2
                    gridMapNavigator.detectNoWall(-45)
                #    gridMapNavigator.removeObstacle(-45)
                    
                if (megaCommunicator.getSonar3() == 1) and (gridMapNavigator.isInStaircaseMode == False): # right sonar
                    print "Right clear!!!"
                    if counterToPutObstacle3 > 0:
                        counterToPutObstacle3 = counterToPutObstacle3 - 1
                    if counterToPutObstacle3 == 0:
                        counterToPutObstacle3 = 2
                        #gridMapNavigator.putObstacle(45)
                else:
                    print "Right not clear!!!"
                    counterToPutObstacle3 = 2
                    gridMapNavigator.detectNoWall(45)
                #    gridMapNavigator.removeObstacle(45)
                    
                    
                #if megaCommunicator.getAds() == 1:
                #    AudioManager.playImmediately('beep')
                
                time.sleep(0.5)
    except :
        print "Oops! Something went wrong in pollData()!"
        isProgramAlive = False
    
    print "Exiting pollData()..."

def sendDataToComp():
    global isProgramAlive, mapNavigator, socketCommunicator, cameraReader, gridMapNavigator
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
                    #socketCommunicator.sendInt(mapNavigator.getCurrentBuilding())
                    #socketCommunicator.sendInt(mapNavigator.getCurrentLevel())
                    #socketCommunicator.sendInt(mapNavigator.curX)
                    #socketCommunicator.sendInt(mapNavigator.curY)
                    #socketCommunicator.sendInt(mapNavigator.curHeading)
                    socketCommunicator.sendInt(gridMapNavigator.curBuilding)
                    socketCommunicator.sendInt(gridMapNavigator.curLevel)
                    socketCommunicator.sendInt(gridMapNavigator.curX)
                    socketCommunicator.sendInt(gridMapNavigator.curY)
                    socketCommunicator.sendInt(gridMapNavigator.curHeading + gridMapNavigator.offsetDirection)
                    socketCommunicator.sendInt(megaCommunicator.getSumStep())
                    socketCommunicator.sendInt(megaCommunicator.getAds())
                    
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

def doCalibration():
    while True:
        print "Sending C to start Calibration"
        rcv = megaCommunicator.send("C");
        print "Received " + rcv
        if (rcv == "A") :
            break
    

def waitForMegaToStartUp():
    megaCommunicator.waitForMegaToStartUp()
    doCalibration()
    
    while True:
        print "Press 1 to stop Calibration!" 
        keyPressed = keypadReader.getKeyPressed()
        print "keyPressed = " + keyPressed
        if (keyPressed == '1'):
            while True:
                print "Sending S to stop Calibration"
                rcv = megaCommunicator.send("S");
                print "Received " + rcv
                if (rcv == "A") :
                    print "Calibration is finished!"
                    break
            break

def init():
    global socketCommunicator, mapNavigator, gridMapNavigator
    try:
        waitForMegaToStartUp()
        
        while True:
            userInput = getUserInput()
            try :
                #isValid = mapNavigator.setStartAndEndPoint(userInput)
                userInputDict = {'startBlock':userInput[0], 'startLevel':userInput[1], 'startId':userInput[2],
                                 'endBlock':userInput[3], 'endLevel':userInput[4], 'endId':userInput[5]}
                isValid = gridMapNavigator.setStartAndEndPoint(userInputDict)
                if isValid == False :
                    print "Invalid path!! Please re-enter!!"
                else :
                    break
            except:
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
        