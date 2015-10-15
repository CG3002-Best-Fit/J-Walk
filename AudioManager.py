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

    audio_zero = None
    audio_one = None
    
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.engine = pyttsx.init()
        
        self.rate = self.engine.getProperty('rate')
        self.engine.setProperty('rate', self.rate-50)
        
        self.volume = self.engine.getProperty('volume')
        self.engine.setProperty('volume', self.volume+1.0)
        
        self.warning_audio = pygame.mixer.Sound("Audio/beep.wav")
        self.left_audio = pygame.mixer.Sound("Audio/left.wav")
        self.right_audio = pygame.mixer.Sound("Audio/right.wav")
	self.audio_zero = pygame.mixer.Sound("Audio/0.wav")
	self.audio_one = pygame.mixer.Sound("Audio/1.wav")
	self.audio_two = pygame.mixer.Sound("Audio/2.wav")
	self.audio_three = pygame.mixer.Sound("Audio/3.wav")
	self.audio_four = pygame.mixer.Sound("Audio/4.wav")
	self.audio_five = pygame.mixer.Sound("Audio/5.wav")
	self.audio_six = pygame.mixer.Sound("Audio/6.wav")
	self.audio_seven = pygame.mixer.Sound("Audio/7.wav")
	self.audio_eight = pygame.mixer.Sound("Audio/8.wav")
	self.audio_nine = pygame.mixer.Sound("Audio/9.wav")
	self.clear_audio = pygame.mixer.Sound("Audio/clear.wav")
	self.enter_audio = pygame.mixer.Sound("Audio/enter.wav")
        
        self.mainChan = pygame.mixer.Channel(1)
        self.mainChan.set_volume(1.0)
        
    def play(self, audioFile):
        if (pygame.mixer.get_busy() == False) :
            self.mainChan.play(audioFile)
    
    def playNumber(self, num):
        print "play " + num 
        if num == '0':
	    self.play(self.audio_zero)
	elif num == '1':
	    self.play(self.audio_one)
	elif num == '2':
	    self.play(self.audio_two)
	elif num == '3':
	    self.play(self.audio_three)
	elif num == '4':
	    self.play(self.audio_four)
	elif num == '5':
	    self.play(self.audio_five)
	elif num == '6':
	    self.play(self.audio_six)
	elif num == '7':
	    self.play(self.audio_seven)
	elif num == '8':
	    self.play(self.audio_eight)
	elif num == '9':
	    self.play(self.audio_nine)
	elif num == '*':
	    self.play(self.clear_audio)
	else:
	    self.play(self.enter_audio)

    def playWarning(self):
        if (pygame.mixer.get_busy() == False) :
            self.play(self.warning_audio)
        
    def playLeft(self):
        if (pygame.mixer.get_busy() == False) :
            self.play(self.left_audio)
        
    def playRight(self):
        if (pygame.mixer.get_busy() == False) :
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
    
        
    
