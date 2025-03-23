import pygame
import pygame.display
import pygame.freetype
from threading import Thread
from time import sleep
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
from collections import defaultdict
import ast


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


    # TEST THIS WITH BTOH MENUS
    def systemMessages(self, message, startMenu = False, error=False):
        if error:
            colour = (255,0,0)
        else:
            colour = (0,255,0)
        if startMenu:
            self.startMenuFont.render_to(self.window, (250,580), message, fgcolor=colour)
            print('rendered message')
            sleep(3)
            pygame.draw.rect(self.window, (0,50,0), pygame.Rect(400,580,400,20))
        else:
            self.startMenuFont.render_to(self.window, (600,20), message, fgcolor=colour)
            sleep(3)
            pygame.draw.rect(self.window, (255,245,255), pygame.Rect(600, 20, 200,20))
        
    # def renderWidgets(self):
    #     for i in self.widgets.values():
    #         i.render()

    
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
            logInFail = Thread(target=lambda: self.systemMessages('Error: Not Logged in', True, True), daemon=True)
            logInFail.start()
            return None
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
                    verifyFail = Thread(target=lambda: self.systemMessages('Error: Incorrect Password or Account Type', True, True), daemon=True)
                    verifyFail.start()
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
            emptyField = Thread(target=self.systemMessages('Error: Input field empty', True,True),daemon=True)
            emptyField.start()
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
            accountSuccess = Thread(target=self.systemMessages('Account Created!', True),daemon=True)
            accountSuccess.start()
            pygame.display.update()
        else:
            usernameTaken = Thread(target=self.systemMessages('Error: Username Already Taken', True, True), daemon=True)
            usernameTaken.start()
            pygame.display.update()
        conn.commit()
        cursor.close()
        conn.close()








class mainMenu(Interfaces):
    def __init__(self, m, w, s):
        self.hMove, self.vMove = 0, 0
        self.graph_surface = pygame.Surface((600,600))
        self.graphInputs = []
        self.inputSubmit = False
        self.mathConversion = {}
        self.drawnPoints = defaultdict(lambda: None)
        self.connectingLines = []
        self.lineChecker = False
        self.connectingLinesTemp = []
        self.deleteFromMenu = {}
        self.checkedPos = []  # Moved checkedPos to an instance variable
        super().__init__(m, w, s)
    

    def createMainMenu(self):
        self.state = 'main_menu'
        self.menu_created = True
        self.window.fill((255,255,255))

        self.graph_surface.fill((255,255,255))
        if config.menu_type == 'Teacher':
            self.widgets['createSession'] = Button(
                self.window, 600, 400, 190, 80, 
                text = 'Create Session',
                onClick = self.createSession
            )
        self.widgets['inputEntry1'] = TextBox(
            self.window, 600, 80, 60, 40,
            text = 'X'
        )

        self.widgets['inputEntry2'] = TextBox(
            self.window, 665, 80, 60, 40,
            text = 'Y'
        )
        
        self.widgets['inputEntry3'] = TextBox(
            self.window, 730, 80, 60, 40,
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
        
        self.drawAxis()

        # self.renderWidgets
        self.window.blit(self.graph_surface, (0,0))

    def addDrawnPoints(self, x ,y, value):
        self.drawnPoints[(x ,y)] = value

    def getDrawnPoint(self, x, y):
        return self.drawnPoints.get((x, y))

    def removeDrawnPoint(self, point):
        if point in self.drawnPoints:
            del self.drawnPoints[point]
        else:
            return None

    def drawAxis(self):
        self.drawXaxis()
        self.drawYAxis()
        self.drawZAxis()

    def createSession(self):
        pass

    def drawXaxis(self):
        # x line

        xStart = self.trigCalc([-200,0,0])
        xEnd = self.trigCalc([200,0,0])
        pygame.draw.line(self.graph_surface, (255,0,0),
                        xStart,
                        xEnd, 2)
        
        xlabelCoords = self.trigCalc([220,5,0])
        self.startMenuFont.render_to(self.graph_surface, (xlabelCoords[0], xlabelCoords[1]), 'X', fgcolor=(255,0,0))
    
    def drawYAxis(self):
        # y line
        yStart = self.trigCalc([0,-200,0])
        yEnd = self.trigCalc([0,200,0])
        pygame.draw.line(self.graph_surface, (0,255,0),
                        yStart,
                        yEnd, 2)
        
        yLabelCoords = self.trigCalc([5,220,0])
        self.startMenuFont.render_to(self.graph_surface, (yLabelCoords[0], yLabelCoords[1]), 'Y', fgcolor=(0,255,0))
    
    def drawZAxis(self):
        # z line
        zStart = self.trigCalc([0,0,-200])
        zEnd = self.trigCalc([0,0,200])
        pygame.draw.line(self.graph_surface, (0,0,255), zStart, zEnd, 2)

        zLabelCoords = self.trigCalc([5,5,220])
        self.startMenuFont.render_to(self.graph_surface, (zLabelCoords[0], zLabelCoords[1]), 'Z', fgcolor=(0,0,255))


    def redraw(self):
        self.graph_surface.fill((255,255,255))


        # attemtping to draw the axis and poitns in order however logic is flawed and causes bug when deleting points skip?
        if len(self.graphInputs) > 0:
            # count = 0
            # drawnX, drawnZ, drawnY = False, False, False
            # sortedInputs = sorted(self.graphInputs, key = lambda p : p[2], reverse=True)
            # transformedAxisEnd = {
            #     'x': None,
            #     'y': None,
            #     'z': None
            # }
            # for key in transformedAxisEnd:
            #     if key == 'x':
            #         x,y,z = self.pointTransformation([200,0,0])
            #         transformedAxisEnd['x'] = [x,y,z]
            #     elif key == 'y':
            #         x,y,z = self.pointTransformation([0,200,0])
            #         transformedAxisEnd['y'] = [x,y,z]
            #     elif key == 'z':
            #         x,y,z = self.pointTransformation([0,0,200])
            #         transformedAxisEnd['z'] = [x,y,z]
            # print(transformedAxisEnd)
            # axisEndPoints = []
            # for value in transformedAxisEnd.values():
            #     axisEndPoints.append(value)
            # sortedAxis = sorted(axisEndPoints, key = lambda p: p[2], reverse=True)
            # sortedInputsAndAxis = sortedInputs + sortedAxis
            # print(f'sortedInptusandaxis = {sortedInputsAndAxis}')
            # sortedInputsAndAxis = sorted(sortedInputsAndAxis, key= lambda p: p[2], reverse = True)
            for values in self.graphInputs: #Change to sortedInputsAndAxis
                # print(f'sortedAxis = {sortedAxis}, count = {count}')
                # if count < 3:
                #     if values == sortedAxis[count]:
                #         whatAxis = [key for key,value in transformedAxisEnd.items() if value == value]
                #         if whatAxis == 'x':
                #             self.drawXaxis()
                #             drawnX = True
                #         elif whatAxis == 'y':
                #             self.drawYAxis()
                #             drawnY = True
                #         elif whatAxis == 'z':
                #             self.drawZAxis()
                #             drawnZ = True
                #         count += 1
                #     else:
                #         print('REDRAWN POINT____')
                newPos = self.trigCalc(values)
                self.mathConversion[f'{values}'] = newPos
                pointCircle = pygame.draw.circle(self.graph_surface, (0,0,0), (newPos[0],newPos[1]), 4)
                self.addDrawnPoints(newPos[0],newPos[1], pointCircle)
        #     print(f'DRAW CHECKERS: {drawnX},{drawnY},{drawnZ}')
        #     if drawnX == False:
        #         self.drawXaxis()
        #     if drawnY == False:
        #         self.drawYAxis()
        #     if drawnZ == False:
        #         self.drawZAxis()
        # else:
        #     self.drawAxis()
        for line in self.connectingLines:
            linePos = [self.trigCalc(line[0]), self.trigCalc(line[1])]
            pygame.draw.line(self.graph_surface, (255,165,0), linePos[0], linePos[1], 2)
        pygame.draw.rect(self.window, (255,255,255), pygame.Rect(200,130,600,270))
        self.createPointsMenu()
        self.drawAxis() #DELET THIS
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

        rotatedPoint = (cosTheta * point) + (sinTheta * crossProduct) + ((1 - cosTheta) * dotProduct * axis)
        return rotatedPoint    
    
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

    def createPointsMenu(self):
        for count,point in enumerate(self.graphInputs[::-1]):
            y = 130+(30*count)
            label = len(self.graphInputs)-count
            self.startMenuFont.render_to(self.window, (600,y), f'{label}: {point}', fgcolor=(255,0,0))
            self.deleteFromMenu[label] = point
            self.widgets[label] = Button(
                self.window, 770, y,
                20,20,
                text = 'X',
                onClick = lambda x=label, y = point: self.deletePointFromGraph(x, y)
            )

    # Delete points logic isnt working ie the widgets doesnt get rid of the corresponding points could be due to new logic madem with recording points?
    def deletePointFromGraph(self,label, point):
        self.graphInputs.remove(point)
        self.widgets[label].hide()
        pygame.draw.circle(self.graph_surface, (255,255,255), (point[0],point[1]), 4)
        self.redraw()
        pass
    
    def lineDrawer(self, pos):
        x, y = pos
        for value in self.checkedPos:
            if value == pos:
                return None
            
        point3D = [key for key,value in self.mathConversion.items() if value[0] == x and value[1] == y][0]
        if self.lineChecker:
            self.connectingLinesTemp.append(point3D)
            try:
                start3D = ast.literal_eval(self.connectingLinesTemp[0])
                end3D = ast.literal_eval(self.connectingLinesTemp[1])
            except:
                print('Error evaluating the connecting lines input properly')
            
            self.connectingLines.append([start3D, end3D])
            self.redraw()
            self.connectingLinesTemp.clear()
            self.lineChecker = False
        else:
            self.connectingLinesTemp.append(point3D)
            self.checkedPos.append(pos)
            self.lineChecker = True

    
    # def fixedTrigCalc(self, elementPosition):
    #     x, y, z = elementPosition
    #     # Perform fixed calculations here
    #     # For simplicity, let's assume the fixed reference point is the origin (0, 0, 0)
    #     projectedX = (300 * x) / (300 + z)
    #     projectedY = (300 * y) / (300 + z)
    #     return [projectedX + 300, projectedY + 300]

    def handleInput(self):
        # Error message to prevent pointsMenu overflow
        if len(self.graphInputs) == 9:
            pMenuOverflowThread = Thread(target=lambda : self.systemMessages('Error: Max No. Points',False, True), daemon=True)
            pMenuOverflowThread.start()
            return None
        try:
            x_input = int(self.getInput('inputEntry1'))
            y_input = int(self.getInput('inputEntry2'))
            z_input = int(self.getInput('inputEntry3'))
        except ValueError:
            invalidInputType = Thread(target=lambda: self.systemMessages('Error: Invlaid Type Input', False, True), daemon=True)
            invalidInputType.start()
            return None
        if all(num > 200 for num in (x_input, y_input, z_input)):
            outOfRange = Thread(target=lambda: self.systemMessages('Error: Max Value = 200',False, True), daemon=True)
            outOfRange.start()
            return None
        self.graphInputs.append([x_input, y_input, z_input])
        self.inputSubmit = True
        self.redraw()



