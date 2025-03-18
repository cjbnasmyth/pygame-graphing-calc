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
        self.graph_surface = pygame.Surface((600,600))
        self.widgets = {}
        self.state = None
        self.type = None
        # CONFIG FILE?
        self.startMenuFont = pygame.freetype.Font(None, 20)
        self.accountActive = False
        self.pwdState = 'password'
        self.menu_created = False

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


class startMenu(Interfaces):
    def createStartMenu(self):
        self.state = 'start_menu'
        self.menu_created = True
        print('test')
        self.window.fill((0,0,0))
        # forgot password? LATER
        self.startMenuFont.render_to(self.window, (250,80), 'Username:', fgcolor=(255,255,255))
        self.widgets['username'] = TextBox(
            self.window, 250, 100,
            300,50
        )
        self.startMenuFont.render_to(self.window, (250,180), 'Password:', fgcolor=(255,255,255))
        self.widgets['password'] = TextBox(
            self.window, 250, 200,
            300, 50,
            font = config.pwdFont
        )
        self.startMenuFont.render_to(self.window, (600,260), 'Show', fgcolor=(255,255,255))
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
            150, 80,
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
            pygame.display.update()
        else:
            self.startMenuFont.render_to(self.window, (400,760), 'Username already taken', fgcolor=(255,0,0))
            pygame.display.update()
        conn.commit()
        cursor.close()
        conn.close()








class mainMenu(Interfaces):
    def __init__(self, m, w, s):
        self.hMove, self.vMove, self.zoom = 0, 0, -500
        self.graph_surface = pygame.Surface((600,600))
        self.graphInputs = []
        self.inputSubmit = False
        super().__init__(m, w, s)
    

    def createMainMenu(self):
        self.state = 'main_menu'
        self.menu_created = True
        self.window.fill((255,255,255))

        self.graph_surface.fill((255,255,255))
        if config.menu_type == 'Teacher':
            print('created button')
            self.widgets['createSession'] = Button(
                self.window, 600, 400, 190, 80, 
                text = 'Create Session',
                onClick = self.createSession
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
        
        self.drawAxis(self.graph_surface)

        # self.renderWidgets
        self.window.blit(self.graph_surface, (0,0))

    def drawAxis(self, s):
        self.drawXaxis(s)
        self.drawYAxis(s)
        self.drawZAxis(s)

    def createSession(self):
        pass

    def drawXaxis(self, surface):
        # x line

        xStart = self.trigCalc([-200,0,0])
        xEnd = self.trigCalc([200,0,0])
        print([xStart, xEnd])
        pygame.draw.line(surface, (255,0,0),
                        xStart,
                        xEnd, 2)
    
    def drawYAxis(self, surface):
        # y line
        yStart = self.trigCalc([0,-200,0])
        yEnd = self.trigCalc([0,200,0])
        print([yStart, yEnd])
        pygame.draw.line(surface, (0,255,0),
                        yStart,
                        yEnd, 2)
    
    def drawZAxis(self, surface):
        # z line
        zStart = self.trigCalc([0,0,-200])
        zEnd = self.trigCalc([0,0,200])
        print([zStart, zEnd])
        pygame.draw.line(surface, (0,0,255), zStart, zEnd, 2)

    # Have to do one movement after clicking submit to render the point
    # The axis move with the camera movements
    def redrawPoints(self):
        self.graph_surface.fill((255,255,255))
        if len(self.graphInputs) > 0:
            for inputs in self.graphInputs:
                newPos = self.trigCalc(inputs)
                pygame.draw.circle(self.graph_surface, (0,0,0), (newPos[0],newPos[1]), 4)
        else:
            pass
        self.drawAxis(self.graph_surface)
        self.inputSubmit = False
        self.window.blit(self.graph_surface, (0,0))


    # def getCameraPos(self):

    #     yaw = np.radians(self.hMove)
    #     pitch = np.radians(self.vMove)
        
    #     # Calculate camera position based on spherical coordinates (using zoom as radius)
    #     x = self.zoom * np.cos(pitch) * np.sin(yaw)
    #     y = self.zoom * np.sin(pitch)
    #     z = self.zoom * np.cos(pitch) * np.cos(yaw)
    #     # https://en.wikipedia.org/wiki/Spherical_coordinate_system#Cartesian_coordinates
    #     # x = self.zoom * np.sin(pitch) * np.cos(yaw)
    #     # y = self.zoom * np.sin(pitch) * np.sin(yaw)
    #     # z = self.zoom * np.cos(pitch)
    #     # https://stackoverflow.com/questions/5278417/rotating-body-from-spherical-coordinates
    #     # x = self.zoom * np.sin(pitch) * np.cos(yaw)
    #     # y = (self.zoom * np.sin(pitch)* np.sin(yaw)) * np.cos(2) - (self.zoom * np.cos(pitch)) * np.sin(2)
    #     # z = (self.zoom * np.sin(pitch)*np.sin(yaw)) * np.sin(2) + (self.zoom * np.cos(pitch)) * np.cos(2)

    #     return np.array([x, y, z])

    def rotatePoint(self, point, axis, theta):
        # https://math.stackexchange.com/questions/4373008/rotation-of-a-point-around-an-axis-using-the-cartesian-coordinates
        point = np.array(point)
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)

        # Rodrigues' rotation formula
        cosTheta = np.cos(theta)
        sinTheta = np.sin(theta)
        crossProduct = np.cross(axis, point)
        dotProduct = np.dot(axis, point)

        return (cosTheta * point) + (sinTheta * crossProduct) + ((1 - cosTheta) * dotProduct * axis)        
    def pointTransformation(self, point):
        
        yaw = np.radians(self.hMove)
        pitch = np.radians(self.vMove)

        # yawMatrix = np.array([
        #     [np.cos(yaw), 0, np.sin(yaw)],
        #     [0, 1, 0],
        #     [-np.sin(yaw), 0, np.cos(yaw)]
        # ])

        # pitchMatrix = np.array([
        #     [1, 0, 0],
        #     [0, np.cos(pitch), -np.sin(pitch)],
        #     [0, np.sin(pitch), np.cos(pitch)]
        # ])

        # relativePos = np.array(point) - np.array(self.getCameraPos())
        # transformedPoint = pitchMatrix @ (yawMatrix @ relativePos)

        transformedPoint = self.rotatePoint(point, [0, 1, 0], yaw)
        transformedPoint = self.rotatePoint(transformedPoint, [1, 0, 0], pitch)

        return transformedPoint


    def trigCalc(self, elementPosition):
        # if whatAxis == 'x':
        #     i = 0
        # elif whatAxis == 'y':
        #     i = 1
        # elif whatAxis == 'z' or whatAxis == None:
        #     i = 2
        # cameraPostion = self.getCameraPos()
  
        # # How to work out the camera z value (300)??? when using the 2 hMove and vMove 
        # print(f'cam pos: {cameraPostion}')
        # print(f'elem pos: {elementPosition}')
        # projectedX = (300*(cameraPostion[0]+ elementPosition[0])) / (300+ elementPosition[i])
        # projectedY = (300*(cameraPostion[1]+ elementPosition[1])) / (300+ elementPosition[i])
        # return [(projectedX+300)-cameraPostion[0], (projectedY+300)-cameraPostion[1]]
        finalPoint = self.pointTransformation(elementPosition)
    

        screenCenterX, screenCenterY = 600//2, 600//2
        x, y, z = finalPoint
        scale = 1

        
        projectedX = (x * scale) + screenCenterX
        projectedY = (-y * scale) + screenCenterY


        return [projectedX, projectedY]


    # def fixedTrigCalc(self, elementPosition):
    #     x, y, z = elementPosition
    #     # Perform fixed calculations here
    #     # For simplicity, let's assume the fixed reference point is the origin (0, 0, 0)
    #     projectedX = (300 * x) / (300 + z)
    #     projectedY = (300 * y) / (300 + z)
    #     return [projectedX + 300, projectedY + 300]

    # for working out the 3d coords of each point after input (whether that is equation or whatever)
    def handleInput(self):
        x_input = int(self.getInput('inputEntry1'))
        y_input = int(self.getInput('inputEntry2'))
        z_input = int(self.getInput('inputEntry3'))
        self.graphInputs.append([x_input, y_input, z_input])
        self.inputSubmit = True
        self.redrawPoints()


