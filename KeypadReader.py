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
    
    preKeyPressed = "###"
    
    def __init__(self):
        self.preKeyPressed = "###"
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
                            print "Play " + self.MATRIX[i][j]
                            AudioManager.play(self.MATRIX[i][j])
                            print self.MATRIX[i][j] + " pressed"
                            self.preKeyPressed = self.preKeyPressed[1:] + self.MATRIX[i][j]
                            print "history = " + self.preKeyPressed
                            GPIO.output(self.COL[j],1)
                            if self.history == "**#" :
                                print "Throw Exception"
                                raise ValueError("Re-enter Input")
                            time.sleep(0.05)
                            print "return " + self.MATRIX[i][j]
                            return self.MATRIX[i][j]
                    GPIO.output(self.COL[j],1)
                    time.sleep(0.05)
            
        except KeyboardInterrupt:
            print "Keyboard has problem!!!"
            GPIO.cleanup();
        return '0'

    def getNumber(self):
        result = ""
        while True:
            c = self.getKeyPress()
            if c == '#':
                if result == "" :
                    result = "0"
                return int(result)
            elif c == '*':
                result = ""
            else: 
                result = result + c
        return 0
