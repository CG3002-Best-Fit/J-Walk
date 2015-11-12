'''
Created on Oct 4, 2015

@author: bamboo3250
'''
import pygame
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
    global isClosed, audioQueue
    while isClosed == False:
        if (len(audioQueue) > 0) and (isBusy() == False):
            audioFile = audioQueue[0]
            audioQueue.pop(0)
            mainChan.play(audioFile)
    print "Audio is closing..."
            
def closeAudio():
    global isClosed
    isClosed = True

#pygame.mixer.pre_init(8000, -16, 2, 4096)
pygame.init()
pygame.mixer.init()

audioDict['beep'] = pygame.mixer.Sound("Audio/beep.wav")
audioDict['left'] = pygame.mixer.Sound("Audio/left.wav")
audioDict['right'] = pygame.mixer.Sound("Audio/right.wav")
audioDict['straight_ahead'] = pygame.mixer.Sound("Audio/straight_ahead.wav")
audioDict['obstacle_ahead'] = pygame.mixer.Sound("Audio/obstacle_ahead.wav")
audioDict['obstacle_left'] = pygame.mixer.Sound("Audio/obstacle_left.wav")
audioDict['obstacle_right'] = pygame.mixer.Sound("Audio/obstacle_right.wav")
audioDict['node_reached'] = pygame.mixer.Sound("Audio/node_reached.wav")
audioDict['node'] = pygame.mixer.Sound("Audio/node.wav")
audioDict['enter_building'] = pygame.mixer.Sound("Audio/44100Hz/enter_building.wav")
audioDict['enter_level'] = pygame.mixer.Sound("Audio/44100Hz/enter_level.wav")
audioDict['enter'] = pygame.mixer.Sound("Audio/44100Hz/enter.wav")


audioDict['0'] = pygame.mixer.Sound("Audio/44100Hz/0.wav")
audioDict['1'] = pygame.mixer.Sound("Audio/44100Hz/1.wav")
audioDict['2'] = pygame.mixer.Sound("Audio/44100Hz/2.wav")
audioDict['3'] = pygame.mixer.Sound("Audio/44100Hz/3.wav")
audioDict['4'] = pygame.mixer.Sound("Audio/44100Hz/4.wav")
audioDict['5'] = pygame.mixer.Sound("Audio/44100Hz/5.wav")
audioDict['6'] = pygame.mixer.Sound("Audio/44100Hz/6.wav")
audioDict['7'] = pygame.mixer.Sound("Audio/44100Hz/7.wav")
audioDict['8'] = pygame.mixer.Sound("Audio/44100Hz/8.wav")
audioDict['9'] = pygame.mixer.Sound("Audio/44100Hz/9.wav")
audioDict['*'] = pygame.mixer.Sound("Audio/44100Hz/clear.wav")
audioDict['#'] = pygame.mixer.Sound("Audio/44100Hz/enter.wav")

mainChan = pygame.mixer.Channel(1)
mainChan.set_volume(1.0)

musicList = ['crossing field.mp3', 
             'Bravely You.mp3', 
             'EXTRA MAGIC HOUR.mp3', 
             'Fubuki.mp3', 
             'Hatsunetsu Days.mp3', 
             'Miiro.mp3',
             'Kibou no Uta.mp3',
             'THE HERO !!.mp3']

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
    
if __name__ == '__main__':
    #play('enter_building')
    Thread(target = loadBGM).start()
    sleep(10)
    while (pygame.mixer.music.get_busy()):
        pass
    
