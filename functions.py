import pygame
import pygame.display
from pygame.locals import *
import pygame_gui
import pygame_widgets as pw
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
import numpy as np
import math


# WORK OUT CLASS STRUCTURE
class Interfaces:
    def __init__(self, m, w, s):
        self.window = w
        self.manager = m
        self.surface = s
        self.widgets = {}
        self.state = 'start_menu'
        self.menu_created = False
        self.hMove, self.vMove = 0, 0

    def hideWidgets(self):
        for i in self.widgets.values():
            i.hide()

    def renderWidgets(self):
        for i in self.widgets.values():
            i.render()

    def getCameraPos(self):
        return [self.hMove, self.vMove]

    def changeState(self):
        if self.state =='start_menu':
            self.menu_created = False
            self.hideWidgets()
            self.state = 'main_menu'
        else:
            pass
        print("state changed")


# KEEP CODING THIS
class startMenu(Interfaces):
    def createStartMenu(self):
        self.menu_created = True
        self.window.fill((0,0,0))
        self.widgets['username'] = TextBox(
            self.window, 300, 100,
            200,80,
            placeholderText = 'Enter Username'
        )
        # ADD PASSWORD FONT
        self.widgets['password'] = TextBox(
            self.window, 300, 200,
            200, 80,
            placeholderText = 'Enter Password'
        )
        self.widgets['teacher'] = Button(
            self.window, 300, 300,
            100, 80,
            text = 'Teacher'
        )
        self.widgets['student'] = Button(
            self.window, 400, 300,
            100, 80,
            text = 'Student'
        )
        self.widgets['log_in_submit'] = Button(
            self.window, 300, 400,
            200, 80,
            text = 'Submit',
            onClick = self.changeState
        )




class mainMenu(Interfaces):
    def createMainMenu(self):
        self.menu_created = True
        self.window.fill((255,255,255))
        graph_surface = pygame.Surface((600,600))
        graph_surface.fill((255,255,255))
        self.widgets['inputEntry1'] = TextBox(
            self.window, 600, 200, 200, 80
        )
        
        self.drawAxis(graph_surface)

        # self.renderWidgets
        self.window.blit(graph_surface, (0,0))

    def drawAxis(self, s):
        self.drawXaxis(s)
        self.drawYAxis(s)
        self.drawZAxis(s)

    def drawXaxis(self, surface):
        # x line
        xStart = self.trigCalc([-300, 0,  0])
        xEnd = self.trigCalc([300,0,0])
        print([xStart, xEnd])
        pygame.draw.line(surface, (255,0,0),
                        [0, 300],
                        [600,300], 2)
    
    def drawYAxis(self, surface):
        # y line
        yStart = self.trigCalc([0,-300,0])
        yEnd = self.trigCalc([0,300,0])
        print([yStart, yEnd])
        pygame.draw.line(surface, (0,255,0),
                        yEnd,
                        yStart, 2)
    
    def drawZAxis(self, surface):
        # z line
        zStart = self.trigCalc([0,0,-300])
        zEnd = self.trigCalc([0,0,300])
        print([zStart, zEnd])
        pygame.draw.line(surface, (0,0,255),
                         zEnd,
                         zStart, 2)

    def redrawPoints(self):
        # change 'a' to input!!!!!!
        newPos = self.trigCalc(self.handleInput('a'))
        # DONE IN trigCalc? to ge thhe points to the center of the section ie 300, 300
        # newPos[0] += 300
        # newPos[1] += 300
        pygame.draw.circle(self.window, (0,0,0), (newPos[0],newPos[1]), 4)


    def trigCalc(self, elementPosition):
        # x,y,z is supposed to be the 'orientation of the camera'
        # Below is camera orientation
        cameraPostion = self.getCameraPos()
        # for i in range(0, len(elementPosition)):
        #     if elementPosition[i] is not 0:
        #         if i == 0:
        #             thetaX = self.hMove/math.sqrt((600^2)+(self.hMove^2))
        #             thetaX = math.cos(thetaX)
        #         elif i == 1:
        #             theta
        thetaX, thetaY, thetaZ = 0, 0, 0
        # A array is the 3D position of the point being projetced (ie the point before projection)
        aArray = np.array([elementPosition[0],elementPosition[1],elementPosition[2]])
        # what value for z??????
        cArray = np.array([cameraPostion[0],cameraPostion[1],1])
        subPostion = np.subtract(aArray, cArray)
        print(subPostion)
        # in matrix form????
        # WHAT SCALE????????? - normal coord scale which should thne be adjusted like line 114, 115
        dX = math.cos(thetaY)*(math.sin(thetaZ)*subPostion[1]+math.cos(thetaZ)*subPostion[0]) - math.sin(thetaY)*subPostion[2]
        dY = math.sin(thetaX)*(math.cos(thetaY)*subPostion[2]+math.sin(thetaY)*(math.sin(thetaZ)*subPostion[1]+math.cos(thetaZ)*subPostion[0])+math.cos(thetaX)*(math.cos(thetaZ*subPostion[1]-math.sin(thetaZ)*subPostion[0])))
        dZ = math.cos(thetaX)*(math.cos(thetaY)*subPostion[2]+math.sin(thetaY)*(math.sin(thetaZ)*subPostion[1]+math.cos(thetaZ)*subPostion[0])-math.sin(thetaX)*(math.cos(thetaZ*subPostion[1]-math.sin(thetaZ)*subPostion[0])))    
        print(f'dZ = {dZ}')
        if dZ == 0:
            print('Div by 0 error')
            return None, None
        projectedX = (cArray[2]/dZ)*dX + cArray[0]
        projetcedY = (cArray[2]/dZ)*dY + cArray[1]
        return [projectedX+300, projetcedY+300]

    # for working out the 3d coords of each point after input (whether that is equation or whatever)
    def handleInput(self, equation):
        return [1,1,1]      


