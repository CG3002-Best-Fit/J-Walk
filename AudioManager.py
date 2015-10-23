'''
Created on Oct 4, 2015

@author: bamboo3250
'''
import pygame
#import pyttsx
from threading import Thread
from time import sleep
import random

mainChan = None

audioQueue = []
audioDict = {}
isClosed = False

def isBusy():
    return pygame.mixer.get_busy()

def playInQueueAudio():
    print "playInQueueAudio() is starting..."
    global isClosed
    while isClosed == False:
        if (len(audioQueue) > 0) and (isBusy() == False):
            audioFile = audioQueue[0]
            audioQueue.pop(0)
            mainChan.play(audioFile)
    print "Audio is closing..."
            
def closeAudio():
    global isClosed
    isClosed = True

pygame.init()
pygame.mixer.init()

#engine = pyttsx.init()

#rate = engine.getProperty('rate')
#engine.setProperty('rate', rate-50)

#volume = engine.getProperty('volume')
#engine.setProperty('volume', volume+1.0)

audioDict['beep'] = pygame.mixer.Sound("Audio/beep.wav")
audioDict['left'] = pygame.mixer.Sound("Audio/left.wav")
audioDict['right'] = pygame.mixer.Sound("Audio/right.wav")
audioDict['straight_ahead'] = pygame.mixer.Sound("Audio/straight_ahead.wav")
audioDict['obstacle_ahead'] = pygame.mixer.Sound("Audio/obstacle_ahead.wav")
audioDict['obstacle_left'] = pygame.mixer.Sound("Audio/obstacle_left.wav")
audioDict['obstacle_right'] = pygame.mixer.Sound("Audio/obstacle_right.wav")
audioDict['node_reached'] = pygame.mixer.Sound("Audio/node_reached.wav")
audioDict['node'] = pygame.mixer.Sound("Audio/node.wav")
audioDict['enter_building'] = pygame.mixer.Sound("Audio/enter_building.wav")
audioDict['enter_level'] = pygame.mixer.Sound("Audio/enter_level.wav")
audioDict['enter'] = pygame.mixer.Sound("Audio/enter.wav")


audioDict['0'] = pygame.mixer.Sound("Audio/0.wav")
audioDict['1'] = pygame.mixer.Sound("Audio/1.wav")
audioDict['2'] = pygame.mixer.Sound("Audio/2.wav")
audioDict['3'] = pygame.mixer.Sound("Audio/3.wav")
audioDict['4'] = pygame.mixer.Sound("Audio/4.wav")
audioDict['5'] = pygame.mixer.Sound("Audio/5.wav")
audioDict['6'] = pygame.mixer.Sound("Audio/6.wav")
audioDict['7'] = pygame.mixer.Sound("Audio/7.wav")
audioDict['8'] = pygame.mixer.Sound("Audio/8.wav")
audioDict['9'] = pygame.mixer.Sound("Audio/9.wav")
audioDict['*'] = pygame.mixer.Sound("Audio/clear.wav")
audioDict['#'] = pygame.mixer.Sound("Audio/enter.wav")

mainChan = pygame.mixer.Channel(1)
mainChan.set_volume(1.0)

musicList = ['crossing field.mp3', 
             'Bravely You.mp3', 
             'EXTRA MAGIC HOUR.mp3', 
             'Fubuki.mp3', 
             'Hatsunetsu Days.mp3', 
             'Miiro.mp3',
             'Kibou no Uta.mp3']

def init():
    global isClosed, audioQueue
    isClosed = False
    audioQueue = []
    playInQueueAudioThread = Thread(target = playInQueueAudio)
    playInQueueAudioThread.start()

def loadBGM():
    global isClosed
    song = random.choice(musicList)
    pygame.mixer.music.set_volume(0.1)

    print song
    pygame.mixer.music.load('Audio/' + song)
    playBGM()
    

def playBGM():
    pygame.mixer.music.play()
    
    
def stopBGM():
    pygame.mixer.music.fadeout(2000)

def playImmediately(audioName):
    if (audioDict[audioName] != None) :
        mainChan.play(audioDict[audioName])
    else :
        print audioName + " audio file doesn't exist!"

def play(audioName):
    #print "play " + audioName 
    if (audioDict[audioName] != None) :
        audioQueue.append(audioDict[audioName])
    else:
        print audioName + " audio file doesn't exist!"

def playNumber(number):
    for c in str(number):
        if (c == '.'): 
            break
        play(c)

#def playString(s):
#    engine.say(s)
#    engine.runAndWait()

#def playRequestStartingBlock():
#    engine.say('Please enter Starting block.')
#    engine.runAndWait()

#def playRequestStartingLevel():
#    engine.say('Please enter the Starting level.')
#    engine.runAndWait()

#def playStartingBlockLevelInvalid():
#    engine.say('Starting block and Level are incorrect, please try again.')
#    engine.runAndWait()
    
#def playRequestStartingNode():
#    engine.say('Please enter Starting Node.')
#    engine.runAndWait()
    
#def playStartingNodeIntegerError():
#    engine.say('Please enter integers for Starting Node.')
#    engine.runAndWait()
    
#def playStartingNodeInvalid():
#    engine.say('Starting Node Invalid, please try again.')
#    engine.runAndWait()

#def playRequestEndingBlock():
#    engine.say('Please enter Ending block.')
#    engine.runAndWait()
    
#def playRequestEndingLevel():
#    engine.say('Please enter Ending level.')
#    engine.runAndWait()
    
#def playEndingBlockLevelInvalid():
#    engine.say('Ending block and Level are incorrect, please try again.')
#    engine.runAndWait()
    
#def playRequestEndingNode():
#    engine.say('Please enter Ending Node.')
#    engine.runAndWait()
    
#def playEndingNodeIntegerError():
#    engine.say('Please enter integers for Ending Node.')
#    engine.runAndWait()
    
#def playEndingNodeInvalid():
#    engine.say('Ending Node Invalid, please try again.')
#    engine.runAndWait()
    
if __name__ == '__main__':
    #play('enter_building')
    Thread(target = loadBGM).start()
    sleep(10)
    while (pygame.mixer.music.get_busy()):
        pass
    
