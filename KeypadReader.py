import RPi.GPIO as GPIO
import time
import AudioManager

class KeypadReader(object):
    MATRIX = [['1','2','3'],
              ['4','5','6'],
              ['7','8','9'],
              ['*','0','#']]
    
    COL = [8,4,2] ##connect the pins in reverse: 2,4,8
    ROW = [11,9,7,3] ## 3,7,9,11
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        for j in range(3):
            GPIO.setup(self.COL[j],GPIO.OUT)
            GPIO.output(self.COL[j], 1)
            
        for i in range(4):
            GPIO.setup(self.ROW[i],GPIO.IN, pull_up_down = GPIO.PUD_UP)

    def getKeyPressed(self):
        try:
            while(True):
                for j in range(3):
                    GPIO.output(self.COL[j],0)
                    for i in range(4):
                        if GPIO.input(self.ROW[i]) == 0:
                            GPIO.output(self.COL[j],1)
                            AudioManager.play(self.MATRIX[i][j])
                            print self.MATRIX[i][j] + " pressed"
                            return self.MATRIX[i][j]
                    
            
        except KeyboardInterrupt:
                GPIO.cleanup();
        return '0'

    def getNumber(self):
        result = ""
        try:
            while(True):
                for j in range(3):
                    GPIO.output(self.COL[j],0)
                    
                    for i in range(4):
                        if GPIO.input(self.ROW[i]) == 0:
                            GPIO.output(self.COL[j],1)
                            AudioManager.play(self.MATRIX[i][j])
                            print self.MATRIX[i][j] + " pressed"
                            
                            if (self.MATRIX[i][j] == '#'):
                                
                                if (result == "") :
                                    result = "0"
                                return result
                            elif (self.MATRIX[i][j] == '*'):
                                result = ""
                            else:
                                result = result + self.MATRIX[i][j]
                            
                            print "result = " + result
                            
                    time.sleep(0.05)
            
        except KeyboardInterrupt:
                GPIO.cleanup();
        return result
