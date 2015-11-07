'''
Created on Oct 12, 2015

@author: bamboo3250
'''
import serial
import os
from scanner import Scanner

class MegaCommunicator(object):
    sonar1Value = 0
    sonar2Value = 0
    sonar3Value = 0
    headingValue = 0
    stepsValue = 0
    sumSteps = 0
    accValue = 0
    adsValue = 0
    sensorValues = []
    status = []
    pollCount = 0
    stackSpace = 0
    
    port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=2.0)
    sc = Scanner("")
    
    timeout_flag = False
    
    def __init__(self):
        for i in range(15):
            self.sensorValues.append(0)
            self.status.append("changed")
    
    def readlineCR(self):
        rv = ""
        while True:
            ch = self.port.read();
            #print("ch = \"" + ch + "\"");
            #print("rv = \"" + rv + "\"");
            if ch == '\r':
                return rv
            if ch == '':
                self.timeout_flag = True
                print "time out!"
                return rv
            rv += ch
    
    def send(self, s):
        #print "Sending " + s
        self.port.write(s);
        return self.readlineCR()
        
    def waitForMegaToStartUp(self):
        while True:
            print "Saying Hello"
            rcv = self.send("H");
            print "Received " + rcv + "!"
            if (rcv == "A") :
                print "Mega is ready!"
                break
        
            
    def pollData(self):
        self.timeout_flag = False
        #print "Sending P..."
        rcv = self.send("P")
        #print "rcv from P = " + rcv
        
        if self.timeout_flag :
            print "resending P"
            return False 
        
        self.sc = Scanner(rcv)
        N = self.sc.nextInt()
        temp = N
        #print "N = " + str(N)
        for i in range (0, N):
            newValue = self.sc.nextInt()
            #print "i = " + str(i) + "  N = " + str(N) + " " + str(len(sensorValues))
            if newValue != self.sensorValues[i] :
                self.status[i] = "changed"
            else :
                self.status[i] = ""
            self.sensorValues[i] = newValue 
            temp += self.sensorValues[i]
            
        checkSum = self.sc.nextInt()
        if (checkSum != temp): # request resend immediately
            print str(checkSum) + " " + str(temp)
            print "check sum wrong!"
            return False
        else :
            os.system('clear')
            self.pollCount += 1
            #print self.pollCount
            print "Numbers of Data: " + str(N)
            
            self.sonar1Value    = self.sensorValues[0]
            self.sonar2Value    = self.sensorValues[1]
            self.sonar3Value    = self.sensorValues[2]
            self.stepsValue     = self.sensorValues[3]
            self.headingValue   = self.sensorValues[4]
            self.stackSpace     = self.sensorValues[5]
            self.accValue       = self.sensorValues[6]
            #self.adsValue       = self.sensorValues[7]
            
            print "sonar 1  \t" + str(self.sonar1Value)  + " " + self.status[0]
            print "sonar 2  \t" + str(self.sonar2Value)  + " " + self.status[1]
            print "sonar 3  \t" + str(self.sonar3Value)  + " " + self.status[2]
            print "Step     \t" + str(self.stepsValue)  + " " + self.status[3]
            print "Heading  \t" + str(self.headingValue)  + " " + self.status[4]
            print "Stack space \t" + str(self.stackSpace) + " " + self.status[5]
            print "ACC      \t" + str(self.accValue) + " " + self.status[6]
            #print "ADS      \t" + str(self.sensorValues[7]) + " " + self.status[7]
            
            self.sumSteps = self.sumSteps + self.stepsValue
        return True

    def getSonar1(self):
        return self.sonar1Value
    
    def getSonar2(self):
        return self.sonar2Value
    
    def getSonar3(self):
        return self.sonar3Value
    
    def getStep(self):
        return self.stepsValue
    
    def getSumStep(self):
        return self.sumSteps
    
    def getHeading(self):
        return self.headingValue
    
    def getAcc(self):
        return self.accValue
    
    def getAds(self):
        return self.adsValue
