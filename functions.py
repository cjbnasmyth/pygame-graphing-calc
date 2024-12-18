import pygame
import pygame.display
from pygame.locals import *
import pygame_gui
import pygame_widgets as pw
from pygame_widgets.textbox import TextBox
from pygame_widgets.button import Button
from pygame_widgets.dropdown import Dropdown
import numpy as np
import math
import config
from mysql.connector import connect, Error


# WORK OUT CLASS STRUCTURE
class Interfaces:
    def __init__(self, m, w, s):
        self.window = w
        self.manager = m
        self.surface = s
        self.widgets = {}
        self.state = None
        self.type = None
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

    # NEED TO WORK OUT HOW state AND menu_created ARE MANAGED
    def changeState(self):
        if self.state =='start_menu':
            self.hideWidgets()
            self.state = 'main_menu'
        elif self.state == 'main_menu':
            # menu_created affecting loop
            self.menu_created = False
            self.hideWidgets()
            self.state = 'start_menu'
        print(f"state changed state = {self.state}")


# KEEP CODING THIS
class startMenu(Interfaces):
    def createStartMenu(self):
        self.state = 'start_menu'
        self.menu_created = True
        print('test')
        self.window.fill((0,0,0))
        # placeholder pygame text for 'ENter username:' and 'Enter password:
        self.widgets['username'] = TextBox(
            self.window, 250, 100,
            300,50
        )
        pwdFont = pygame.font.Font('password.ttf')
        self.widgets['password'] = TextBox(
            self.window, 250, 200,
            300, 50,
            font = pwdFont
        )

        self.widgets['account_type_dropdown'] = Dropdown(
            self.window, 550, 100,
            150, 80, name = 'Select Account Type',
            choices=[
                'Teacher',
                'Student',
            ],
            values = ['Teacher', 'Student']
        )
        self.widgets['create_account'] = Button(
            self.window, 550, 400,
            100, 80,
            text = 'Create Account',
            onClick = self.addAccount
        )

        self.widgets['log_in_submit'] = Button(
            self.window, 350, 400,
            100, 80,
            text = 'Submit',
            onClick = self.checkType
        )
    
    # changeState and checkType *********
    def checkType(self):
        config.menu_type = self.widgets['account_type_dropdown'].getSelected()
        self.changeState()

    
    def addAccount(self):
        username = self.getInput('username')
        password = self.getInput('password')
        accountType = self.widgets['account_type_dropdown'].getSelected()
        print(accountType)
        # DISPLAY ACCOUNT CONFIRMATION + USERNAME/PASSWORD EXSIST

        conn = connect(**config.DB_INFO)
        cursor = conn.cursor()
        checkQuery = ('SELECT * FROM users'
                      'WHERE username = %s')
        check = cursor.execute(checkQuery, username)
        if check == None or check == ' ' or check == []:
            addQuery = ('INSERT INTO users ' 
                    '(username, password, accountType) ' 
                    'VALUES (%s, %s, %s)')
            cursor.execute(addQuery, (username, password, accountType))
        else:
            print('else')
            # TEXT TO DISPLAY ITS INVALID
        conn.commit()
        cursor.close()
        conn.close()

    def getInput(self, label):
        return self.widgets[label].getText()







class mainMenu(Interfaces):
    def createMainMenu(self):
        self.state = 'main_menu'
        self.menu_created = True
        self.window.fill((255,255,255))
        graph_surface = pygame.Surface((600,600))
        graph_surface.fill((255,255,255))
        if config.menu_type == 'Teacher':
            print('created button')
            self.widgets['createSession'] = Button(
                self.window, 600, 600, 200, 80
            )
        self.widgets['inputEntry1'] = TextBox(
            self.window, 600, 200, 100, 80
        )
        
        self.widgets['back'] = Button(
            self.window, 600, 400, 100, 80,
            text = 'Back',
            onClick = self.changeState
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


