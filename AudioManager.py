'''
Created on Oct 4, 2015

@author: bamboo3250
'''
import pygame
import pyttsx

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
        
        self.engine = pyttsx.init()
        
        self.rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', self.rate-50)
        
        self.volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', self.volume+1.0)
        
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
        
    def playRequestStartingBlock(self):
        self.engine.say('Please enter Starting block.')
        self.engine.runAndWait()
    
    def playRequestStartingLevel(self):
        self.engine.say('Please enter the Starting level.')
        self.engine.runAndWait()
    
    def playStartingBlockLevelInvalid(self):
        self.engine.say('Starting block and Level are incorrect, please try again.')
        self.engine.runAndWait()
        
    def playRequestStartingNode(self):
        self.engine.say('Please enter Starting Node.')
        self.engine.runAndWait()
        
    def playStartingNodeIntegerError(self):
        self.engine.say('Please enter integers for Starting Node.')
        self.engine.runAndWait()
        
    def playStartingNodeInvalid(self):
        self.engine.say('Starting Node Invalid, please try again.')
        self.engine.runAndWait()
    
    def playRequestEndingBlock(self):
        self.engine.say('Please enter Ending block.')
        self.engine.runAndWait()
        
    def playRequestEndingLevel(self):
        self.engine.say('Please enter Ending level.')
        self.engine.runAndWait()
        
    def playEndingBlockLevelInvalid(self):
        self.engine.say('Ending block and Level are incorrect, please try again.')
        self.engine.runAndWait()
        
    def playRequestEndingNode(self):
        self.engine.say('Please enter Ending Node.')
        self.engine.runAndWait()
        
    def playEndingNodeIntegerError(self):
        self.engine.say('Please enter integers for Ending Node.')
        self.engine.runAndWait()
        
    def playEndingNodeInvalid(self):
        self.engine.say('Ending Node Invalid, please try again.')
        self.engine.runAndWait()
    
        
    