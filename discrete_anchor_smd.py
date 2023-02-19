import pygame, sys
import numpy as np
from pygame.locals import *
from pyo import *
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.textbox import TextBox
from audio_fbk import (
    AudioServer,
    AudioFbk,
    WindFbk,
    Thunk,

)
from multiprocessing import Process, Value
import zmq
import math


WHITE = (255, 255, 255)
RED   = (255,   0,   0)

SCREEN_WIDTH = 1500
SCREEN_HEIGHT = 1000





# Main Class
class MainRun(object):
        
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Horizontal Spring Mass Damper')

        self.mass = 50
        self.positionY = 100
        self.positionX = 210 
        self.velocityX = 0
        self.previous_bar = 0

        self.timeStep = 0.02

        self.red_circle = pygame.draw.rect(self.screen,(255,0,0),Rect(self.positionX - 25, self.positionY+10 , 60, 60), border_radius=30)
        self.anchorPoints = 0

        # Anchor position of spring
        self.anchorX = 20
        self.anchorY = 100
        self.k = 120 # Spring constant
        self.damping = 100
        self.forceX = 0

        self.audio_server = AudioServer()
        self.audio = WindFbk(self.audio_server)

        self.anchor_rect = pygame.rect.Rect(100, self.anchorY, 10, 80)

        self.mass_slider = Slider(self.screen, 100, 300, 200, 20, min=1, max=150, step=1, initial=self.mass)
        self.mass_text = TextBox(self.screen, 100, 300, 0, 0, fontSize=30)
        self.mass_text.disable()

        self.k_slider = Slider(self.screen, 400, 300, 200, 20, min=0, max=150, step=1, initial=self.k)
        self.k_text = TextBox(self.screen, 400, 300, 0, 0, fontSize=30)
        self.k_text.disable()

        self.damping_slider = Slider(self.screen, 700, 300, 200, 20, min=0, max=150, step=1, initial=self.damping)
        self.damping_text = TextBox(self.screen, 700, 300, 0, 0, fontSize=30)
        self.damping_text.disable()

        self.dragging = False
        self.anchorPos = 1

        self.length = Value('d', 0.0)
        self.process = Process(
            target=self.mp_zmq_server, args=(self.length,)
        )
        self.process.start()


        anchorPoints = 5
        self.bars = []
        for i in range(1, 7):
            self.bar = pygame.draw.rect(self.screen, 0, Rect(SCREEN_WIDTH/(anchorPoints + 1) * i, self.positionY+10 , 10, 60), border_radius=30)
            self.bars.append(self.bar)
        
        self.current_anchor_point = 0
        
        self.Main()

    
    def mp_zmq_server(self, length,):
        context = zmq.Context()
        #  Socket to talk to server
        print("Connecting to hello world server…")
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")


        while True:
            socket.send(b"Hello")
            #  Get the reply.
            message = socket.recv()
            length.value = float(message.decode())


    
    def spring_mass_damper(self):
        self.springForceX = -self.k * (self.positionX - self.anchor_rect.x) 
        self.dampingForceX = self.damping * self.velocityX
        self.forceX = self.springForceX  - self.dampingForceX
        self.accelerationX = self.forceX/self.mass
        self.velocityX = self.velocityX + self.accelerationX * self.timeStep  
        self.positionX = self.positionX + self.velocityX * self.timeStep

        self.mass_text.setText("Mass : " +  str(self.mass_slider.getValue()))
        self.k_text.setText("Spring Const. : " + str(self.k_slider.getValue()))
        self.damping_text.setText("Damping : " + str(self.damping_slider.getValue()))
        self.mass = self.mass_slider.getValue()
        self.k = self.k_slider.getValue()
        self.damping = self.damping_slider.getValue()
    

    def draw_elements(self):
        self.screen.fill((255, 255, 255))

        print(self.length.value)

        self.anchorPoints = 5
        # 20, 200 for mediapipe
        # 80, 120 for soli
        self.anchorPos = int(np.interp(self.length.value, [80, 120], [1, self.anchorPoints]))
        self.anchor_rect.x = SCREEN_WIDTH/(self.anchorPoints + 1) * self.anchorPos

        for i in range(1, self.anchorPoints+2):
            self.bar = pygame.draw.rect(self.screen, 0, Rect(SCREEN_WIDTH/(self.anchorPoints + 1) * i, self.positionY+10 , 10, 60), border_radius=30)

        self.green_rect = pygame.draw.rect(self.screen, 'green', self.anchor_rect, border_radius=30)
        self.red_circle = pygame.draw.rect(self.screen,(255,0,0),Rect(self.positionX - 25, self.positionY+10 , 60, 60), border_radius=30)
        pygame_widgets.update(events)
        pygame.display.update()
    

    def set_audio(self):
        # current_anchor = int(np.interp(self.length.value, [20, 200], [1, self.anchorPoints]))
        # if self.red_circle.collidelistall(self.bars):
        #     current_anchor = self.red_circle.collidelistall(self.bars)[0]

        #     if 

        if self.red_circle.colliderect(self.anchor_rect) and self.red_circle.collidelistall(self.bars):
            self.audio.set_rate(np.abs(self.velocityX * self.anchorPos)-10)
            # self.audio.play(0)

        # if self.red_circle.collidelistall(self.bars):
        #     if current_anchor != self.anchorPos:
        #         self.audio.play(current_anchor*2)
        #         print("true")
        # else:
        #     self.audio.play(0)


          
            
            
            
        # if self.red_circle.collidedict()
        # self.audio.set_rate(self.anchorPos)



    def Main(self):

        while True:                     
            for event in pygame.event.get(): 
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    # s.shutdown()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:            
                        if self.anchor_rect.collidepoint(event.pos):
                            self.dragging = True
                            mouse_x, mouse_y = event.pos
                            offset_x = self.anchor_rect.x - mouse_x
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:            
                        self.dragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        mouse_x, mouse_y = event.pos
                        self.anchor_rect.x = mouse_x + offset_x
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        self.anchor_rect.x = SCREEN_WIDTH/3 - 200

                    elif event.key == pygame.K_2:
                        self.anchor_rect.x = 2*SCREEN_WIDTH/3 - 200
                    elif event.key == pygame.K_3:
                        self.anchor_rect.x = SCREEN_WIDTH -200
            



            self.spring_mass_damper()
            # self.set_audio()
            self.draw_elements()
            

    
            
            # self.audio.set_rate(np.abs(self.velocityX)/100 * self.positionX/100)

            
            
            



                        
                        

                    
                

     
if __name__ == "__main__":
        MainRun()