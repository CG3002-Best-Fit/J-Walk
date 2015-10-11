'''
Created on Sep 26, 2015

@author: bamboo3250
'''
from time import sleep

from threading import Thread
from AudioManager import AudioManager
from MegaCommunicator import MegaCommunicator
from SocketCommunicator import SocketCommunicator
from CameraReader import CameraReader

isProgramAlive = True

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
        
def pollData():
    global isProgramAlive
    try:
        while isProgramAlive:
            isSuccessful = megaCommunicator.pollData()
            if isSuccessful:
                if (megaCommunicator.getStep() > 0): 
                    pass
                
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
    global isProgramAlive
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

if __name__ == '__main__':
    megaCommunicator.waitForMegaStartUp()
    getUserInput()
    startThreads()