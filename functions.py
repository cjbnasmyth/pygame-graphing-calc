import pygame
import pygame.display
import pygame.freetype
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

pygame.freetype.init()

class Interfaces:
    def __init__(self, m, w, s):
        self.window = w
        self.manager = m
        self.surface = s
        self.widgets = {}
        self.state = None
        self.type = None
        # CONFIG FILE?
        self.startMenuFont = pygame.freetype.Font(None, 20)
        self.accountActive = False
        self.pwdState = 'password'
        self.menu_created = False
        self.hMove, self.vMove = 0, 0

    def hideWidgets(self):
        for i in self.widgets.values():
            i.hide()

    # USE THIS TO GET RID OF TEXT, BUT WHEN TO CALL IT IDK?
    def clearText(self, menu):
        # if menu == 'start_menu':
        #     pygame.draw.rect(self.window, (0,0,0), pygame.Rect(0,540,800,40))
        # elif menu == 'main_menu':
        #     # same as above but change the x, y to message area on the main menu
            pass

    def renderWidgets(self):
        for i in self.widgets.values():
            i.render()

    def getCameraPos(self):
        return [self.hMove, self.vMove]
    
    def getInput(self, label):
        try:
            return self.widgets[label].getText()
        except:
            print(f'Label: {label} doesnt exsist')

    def changeState(self):
        if self.state =='start_menu':
            self.hideWidgets()
            self.state = 'main_menu'
        elif self.state == 'main_menu':
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
        # forgot password? LATER
        # placeholder pygame text for 'Enter username:' and 'Enter password:
        self.widgets['username'] = TextBox(
            self.window, 250, 100,
            300,50
        )
        self.widgets['password'] = TextBox(
            self.window, 250, 200,
            300, 50,
            font = config.pwdFont
        )

        self.widgets['show_password'] = Button(
            self.window, 600, 200,
            50, 50,
            onClick = lambda: self.showPass(self.pwdState)
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
    
    # FOR SHOWING PASSWORD BUTTON 
    def showPass(self, state):
        if state == 'password':
            self.pwdState = 'normal'
            temp_text = self.widgets['password'].getText()
            print(temp_text)
            self.widgets['password'].hide()
            self.widgets['temp'] =TextBox(
                self.window, 250, 200,
                300, 50,
                placeholderText = temp_text
            )
        else:
            self.pwdState = 'password'
            self.widgets['temp'].hide()
            self.widgets['password'].show()

    # DOESNT WORK NEED TO CATCH CASE WHERE USER CHANGES INFO AFTER CREATING ACCONT
    def checkType(self):
        sqlSubmit = self.checkSubmit()
        print(sqlSubmit)
        if self.accountActive == False or sqlSubmit == False:
            self.startMenuFont.render_to(self.window, (1,580), 'Not logged in', fgcolor=(255,0,0))
            print(f'denied accountActive: {self.accountActive}, sqlSubmit: {sqlSubmit}')
            pass
        else:
            config.menu_type = self.widgets['account_type_dropdown'].getSelected()
            self.changeState()

    def getTextFields(self):
        username = self.getInput('username')
        password = self.getInput('password')
        accountType = self.widgets['account_type_dropdown'].getSelected()
        return [username, password, accountType]
    
    # STILL DOESNT WORK INPUT VALID ACCOUNT DATA THEN empty field
    def checkSubmit(self):
        data = self.getTextFields()
        checkConn = connect(**config.DB_INFO)
        checkCursor = checkConn.cursor(buffered=True)
        query = ('SELECT password, accountType FROM users '
                 'WHERE username = %s')
        checkCursor.execute(query, (data[0],))
        condition = checkCursor.fetchone()
        # run if non-empty tuple
        if condition:
                # unpacks tuple
                retrievedPassword, retrievedAccountType = condition
                if retrievedPassword != data[1] or retrievedAccountType != data[2]:
                    self.startMenuFont.render_to(self.window, (400,760), 'Incorrect password or account type', fgcolor=(255,0,0))
                    return False
                else:
                    return True


    def addAccount(self):
        data = self.getTextFields()
        # DISPLAY ACCOUNT CONFIRMATION + USERNAME/PASSWORD EXSIST
        conn = connect(**config.DB_INFO)
        cursor = conn.cursor(buffered=True)
        checkQuery = ('SELECT * FROM users '
                    'WHERE username = %s')
        cursor.execute(checkQuery, (data[0],))
        check = cursor.fetchone()
        print(checkQuery)
        if any(not element for element in data):
            self.startMenuFont.render_to(self.window, (400,760), 'Input field empty', fgcolor=(255,0,0))
            check = False
        else:
            pass
        print(check)   
        if check is None:
            self.accountActive = True
            addQuery = ('INSERT INTO users ' 
                    '(username, password, accountType) ' 
                    'VALUES (%s, %s, %s)')
            cursor.execute(addQuery, (data[0], data[1], data[2]))
            print('text')
            self.startMenuFont.render_to(self.window, (400,760), 'Account created!', fgcolor=(0,255,0))
        else:
            self.startMenuFont.render_to(self.window, (400,760), 'Username already taken', fgcolor=(255,0,0))
        conn.commit()
        cursor.close()
        conn.close()








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
            self.window, 600, 100, 60, 80,
            text = 'X'
        )

        self.widgets['inputEntry2'] = TextBox(
            self.window, 665, 100, 60, 80,
            text = 'Y'
        )
        
        self.widgets['inputEntry3'] = TextBox(
            self.window, 730, 100, 60, 80,
            text = 'Z'
        )

        self.widgets['submit'] = Button(
            self.window, 600, 500, 90, 80,
            text = 'Submit',
            onClick = self.handleInput
        )

        self.widgets['back'] = Button(
            self.window, 700, 500, 90, 80,
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
        # what value for z?????? looking down the barrel of the Z axis so therefore should be the max value? (max value on the pygame coord scale?)
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
        x_input = self.getInput('inputEntry1')
        y_input = self.getInput('inputEntry2')
        z_input = self.getInput('inputEntry3')
        return [x_input, y_input, z_input]


