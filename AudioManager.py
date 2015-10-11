'''
Created on Oct 4, 2015

@author: bamboo3250
'''
import pygame

class AudioManager(object):
    '''
    classdocs
    '''
    mainChan = None

    warning_audio = None
    left_audio = None
    right_audio = None

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.warning_audio = pygame.mixer.Sound("beep.wav")
        self.left_audio = pygame.mixer.Sound("left.wav")
        self.right_audio = pygame.mixer.Sound("right.wav")
        
        self.mainChan = pygame.mixer.Channel(1)
        self.mainChan.set_volume(1.0)
        
    def play(self, audioFile):
        if (pygame.mixer.get_busy() == False) :
            self.mainChan.play(audioFile)
    
    def playWarning(self):
        self.play(self.warning_audio)
        
    def playLeft(self):
        self.play(self.left_audio)
        
    def playRight(self):
        self.play(self.right_audio)
        
    