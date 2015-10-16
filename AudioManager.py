'''
Created on Oct 4, 2015

@author: bamboo3250
'''
import pygame
import pyttsx
from threading import Thread

mainChan = None

audioQueue = []
audioDict = {}
isClosed = False

def isBusy():
    return pygame.mixer.get_busy()

def playInQueueAudio():
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

engine = pyttsx.init()

rate = engine.getProperty('rate')
engine.setProperty('rate', rate-50)

volume = engine.getProperty('volume')
engine.setProperty('volume', volume+1.0)

audioDict['warning'] = pygame.mixer.Sound("Audio/beep.wav")
audioDict['left'] = pygame.mixer.Sound("Audio/left.wav")
audioDict['right'] = pygame.mixer.Sound("Audio/right.wav")
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

playInQueueAudioThread = Thread(target = playInQueueAudio)
playInQueueAudioThread.start()

def play(audioName):
    print "play " + audioName 
    if (audioDict[audioName] != None) :
        audioQueue.append(audioDict[audioName])
    else:
        print audioName + " audio file doesn't exist!"

def playRequestStartingBlock():
    engine.say('Please enter Starting block.')
    engine.runAndWait()

def playRequestStartingLevel():
    engine.say('Please enter the Starting level.')
    engine.runAndWait()

def playStartingBlockLevelInvalid():
    engine.say('Starting block and Level are incorrect, please try again.')
    engine.runAndWait()
    
def playRequestStartingNode():
    engine.say('Please enter Starting Node.')
    engine.runAndWait()
    
def playStartingNodeIntegerError():
    engine.say('Please enter integers for Starting Node.')
    engine.runAndWait()
    
def playStartingNodeInvalid():
    engine.say('Starting Node Invalid, please try again.')
    engine.runAndWait()

def playRequestEndingBlock():
    engine.say('Please enter Ending block.')
    engine.runAndWait()
    
def playRequestEndingLevel():
    engine.say('Please enter Ending level.')
    engine.runAndWait()
    
def playEndingBlockLevelInvalid():
    engine.say('Ending block and Level are incorrect, please try again.')
    engine.runAndWait()
    
def playRequestEndingNode():
    engine.say('Please enter Ending Node.')
    engine.runAndWait()
    
def playEndingNodeIntegerError():
    engine.say('Please enter integers for Ending Node.')
    engine.runAndWait()
    
def playEndingNodeInvalid():
    engine.say('Ending Node Invalid, please try again.')
    engine.runAndWait()
