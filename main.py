'''
Created on Sep 26, 2015

@author: bamboo3250
'''

import seriat
import os

from time import sleep
from scanner import Scanner
from audioManager import AudioManager
from threading import Thread 
from camera import sendImage

port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=2.0)
sc = Scanner("")
timeout_flag = False
audioManager = AudioManager()

def readlineCR():
    rv = ""
    while True:
        ch = port.read();
        #print("ch = \"" + ch + "\"");
        #print("rv = \"" + rv + "\"");
        if ch == '\r':
            return rv
        if ch == '':
            global timeout_flag
            timeout_flag = True
            print "time out!"
            return rv
        rv += ch

sensorValues = []
status = []

def init():
    #port = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3.0)
    for i in range(0, 15):
        sensorValues.append(-1)
        status.append("changed")


def waitForMegaStartUp():
    while True:
        port.write("H");
        print "Saying Hello"
        rcv = readlineCR()
        print "Received " + rcv
        if (rcv == "A") :
            print "Mega is ready!"
            break



def obstacleDetected(u):
    return (10 <= sensorValues[u] and sensorValues[u] < 80)


def pollData():
    pollCount = 0
    while True:
        port.write("P");
        rcv = readlineCR()
        global timeout_flag
        if timeout_flag :
            timeout_flag = False
            print "resending P"
            continue 
        #print rcv
        sc = Scanner(rcv)
        
        N = sc.nextInt()
        temp = N
        for i in range (0, N):
            newValue = sc.nextInt()
            if newValue != sensorValues[i] :
                status[i] = "changed"
            else :
                status[i] = ""
            sensorValues[i] = newValue 
            temp += sensorValues[i]
            
        checkSum = sc.nextInt()
        if (checkSum != temp): # request resend immediately
            print str(checkSum) + " " + str(temp)
            print "check sum wrong!"
        
            continue
        else :
            os.system('clear')
            pollCount += 1
            print pollCount
            print "Numbers of Data: " + str(N)
            
            print "sonar 1  \t" + str(sensorValues[0])  + " " + status[0]
            print "sonar 2  \t" + str(sensorValues[1])  + " " + status[1]
            print "sonar 3  \t" + str(sensorValues[2])  + " " + status[2]
            print "accel X  \t" + str(sensorValues[3])  + " " + status[3]
            print "accel Y  \t" + str(sensorValues[4])  + " " + status[4]
            print "accel Z  \t" + str(sensorValues[5])  + " " + status[5]
            print "gyro X   \t" + str(sensorValues[6])  + " " + status[6]
            print "gyro Y   \t" + str(sensorValues[7])  + " " + status[7]
            print "gyro Z   \t" + str(sensorValues[8])  + " " + status[8]
            print "ADS      \t" + str(sensorValues[9])  + " " + status[9]
            print "compass  \t" + str(sensorValues[10]) + " " + status[10]
            print "altitude \t" + str(sensorValues[11]) + " " + status[11]

        if (obstacleDetected(0)):
            audioManager.playLeft()

        if (obstacleDetected(1)):
            audioManager.playRight()

        if (obstacleDetected(2)):
            audioManager.playWarning()

        sleep(0.5)

def startThreads():
    pollDataThread = Thread(target = pollData)
    pollDataThread.start()
    
    sendImageThread = Thread(target = sendImage)
    sendImageThread.start()
    
    pollDataThread.join()
    sendImageThread.join()
    

if __name__ == '__main__':
    waitForMegaStartUp()
    startThreads()
    #pollData()
