import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

MATRIX=[[1,2,3],
		[4,5,6],
		[7,8,9],
		['*',0,'#'] ]

COL = [8,4,2] ##connect the pins in reverse: 2,4,8
ROW = [11,9,7,3] ## 3,7,9,11

for j in range(3):
	GPIO.setup(COL[j],GPIO.OUT)
	GPIO.output(COL[j], 1)
	
for i in range(4):
	GPIO.setup(ROW[i],GPIO.IN, pull_up_down = GPIO.PUD_UP)
	
try:

	while(True):
		for j in range(3):
			GPIO.output(COL[j],0)
			
			for i in range(4):
				if GPIO.input(ROW[i]) == 0:
					print MATRIX[i][j]
					
			GPIO.output(COL[j],1)
			time.sleep(0.05)
			
except KeyboardInterrupt:
		GPIO.cleanup();
