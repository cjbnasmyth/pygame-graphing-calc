import pygame
import pygame.display
import pygame.freetype
from threading import Thread
from time import sleep
import pygame.gfxdraw
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
        self.widgets = {}
        self.state = None
        # CONFIG FILE?
        self.startMenuFont = pygame.freetype.Font(None, 20)
        self.accountActive = False
        self.pwdState = True
        self.menu_created = False

    def hideWidgets(self):
        for i in self.widgets.values():
            i.hide()


    def systemMessages(self, message, startMenu = False, error=False):
        if error:
            colour = (255,0,0)
        else:
            colour = (0,255,0)
        if startMenu:
            self.startMenuFont.render_to(self.window, (300,580), message, fgcolor=colour)
            pygame.display.update()
            sleep(1)
            pygame.draw.rect(self.window, (0,0,0), pygame.Rect(300,580,400,20))
        else:
            self.startMenuFont.render_to(self.window, (600,20), message, fgcolor=colour)
            pygame.display.update()
            sleep(1)
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


class StartMenu(Interfaces):
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
        if state:
            self.pwdState = False
            temp_text = self.widgets['password'].getText()
            self.widgets['password'].hide()
            self.widgets['temp'] =TextBox(
                self.window, 250, 200,
                300, 50,
                placeholderText = temp_text
            )
        else:
            self.pwdState = True
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
            accountSuccess = Thread(target=self.systemMessages('Account Created!', True, False),daemon=True)
            accountSuccess.start()
            pygame.display.update()
        else:
            usernameTaken = Thread(target=self.systemMessages('Error: Username Already Taken', True, True), daemon=True)
            usernameTaken.start()
            pygame.display.update()
        conn.commit()
        cursor.close()
        conn.close()








class MainMenu(Interfaces):
    def __init__(self, m, w, s):
        self.hMove, self.vMove = 0, 0
        self.graph_surface = pygame.Surface((600,600))
        self.graphInputs = []
        self.inputSubmit = False
        self.mathConversion = {}
        self.drawnPoints = {}
        self.connectingLines = []
        self.lineChecker = False
        self.connectingLinesTemp = []
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
        else:
            self.widgets['joinSession'] = Button(
                self.window, 600, 400, 190, 80,
                text = 'Join Session',
                onClick = self.joinSession
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
    
    def joinSession(self):
        pass

    def drawXaxis(self):
        # x line

        xStart = self.projection([-200,0,0])
        xEnd = self.projection([200,0,0])
        pygame.draw.line(self.graph_surface, (255,0,0),
                        xStart,
                        xEnd, 2)
        
        xlabelCoords = self.projection([220,5,0])
        self.startMenuFont.render_to(self.graph_surface, (xlabelCoords[0], xlabelCoords[1]), 'X', fgcolor=(255,0,0))
    
    def drawYAxis(self):
        # y line
        yStart = self.projection([0,-200,0])
        yEnd = self.projection([0,200,0])
        pygame.draw.line(self.graph_surface, (0,255,0),
                        yStart,
                        yEnd, 2)
        
        yLabelCoords = self.projection([5,220,0])
        self.startMenuFont.render_to(self.graph_surface, (yLabelCoords[0], yLabelCoords[1]), 'Y', fgcolor=(0,255,0))
    
    def drawZAxis(self):
        # z line
        zStart = self.projection([0,0,-200])
        zEnd = self.projection([0,0,200])
        pygame.draw.line(self.graph_surface, (0,0,255), zStart, zEnd, 2)

        zLabelCoords = self.projection([5,5,220])
        self.startMenuFont.render_to(self.graph_surface, (zLabelCoords[0], zLabelCoords[1]), 'Z', fgcolor=(0,0,255))

    def getMathPoint(self, point3D):
        for key, value in self.mathConversion.items():
            if key == point3D:
                return value
        return None


    def redraw(self):
        self.graph_surface.fill((255,255,255))
        self.drawAxis()

        # print(f'connectingLines.itesm() {self.connectingLines.items()}')
        # for key,value in self.connectingLines.items():
        #     linePos = [self.projection(list(key)), self.projection(list(value))]
        #     # print(f'drawing line with this start {list(key)} and end {list(value)}')
        #     pygame.draw.line(self.graph_surface, (255,165,0), linePos[0], linePos[1], 2)

        # This logic not working leads to one of the connecting lines (last one to be drawn?) to be hiden/removed from self.connectingLines\\\\\\
        if len(self.graphInputs) > 0:
            for node in self.graphInputs:
                newPos = self.projection(node.pos)
                self.mathConversion[node.pos] = newPos
                pointCircle = pygame.draw.circle(self.graph_surface, (0,0,0), (newPos[0],newPos[1]), 4)
                self.addDrawnPoints(newPos[0],newPos[1], pointCircle)
        
        
        if len(self.connectingLines)>2:
            start = self.connectingLines[0].node1
            planeDectector = self.detectConnectedPlane(self.graphInputs)
            print(f'planeDectector: {planeDectector}')
            planePoints = []
            if planeDectector:
                for plane in planeDectector:
                    for node in plane:
                        planePoints.append(self.mathConversion.get(node.pos))
                    print(f'drawing polygon at {planePoints}')
                    pygame.gfxdraw.filled_polygon(self.graph_surface, [value for value in planePoints], (0,50,0))
                    planePoints.clear()
            else:
                pass
        else:
            pass

        for line in self.connectingLines:
            startPos = self.projection(line.node1.pos)
            endPos = self.projection(line.node2.pos)
            pygame.draw.line(self.graph_surface, (255,165,0), startPos, endPos, 2)
        

        pygame.draw.rect(self.window, (255,255,255), pygame.Rect(200,130,600,270))
        self.createPointsMenu()
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


    def projection(self, elementPosition):
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
            self.startMenuFont.render_to(self.window, (600,y), f'{label}: {str(point.pos)}', fgcolor=(255,0,0))
            self.widgets[label] = Button(
                self.window, 770, y,
                20,20,
                text = 'X',
                onClick = lambda x=label, y = point: self.deletePointFromGraph(x, y)
            )

    def deletePointFromGraph(self,label, point):
        self.graphInputs.remove(point)
        self.widgets[label].hide()
        # pygame.draw.circle(self.graph_surface, (255,255,255), (point.x,point.y), 4)
        self.redraw()
        for connections in point.connections:
            # start = self.projection(connections.node1.pos)
            # end = self.projection(connections.node2.pos)
            # pygame.draw.line(self.graph_surface, (255,255,255), start, end, 2) 
            self.connectingLines.remove(connections)
            self.redraw()
        pass


    def lineDrawer(self, pos):
        x, y = pos

        # for value in self.checkedPos:
        #     if value == pos:
        #         return None

        point3D = [key for key,value in self.mathConversion.items() if value[0] == x and value[1] == y][0]
        node = self.getNode(point3D)
        print(self.connectingLinesTemp)
        if self.lineChecker:
            self.connectingLinesTemp.append(node)
            try:
                start3D = self.connectingLinesTemp[0]
                end3D = self.connectingLinesTemp[1]
            except:
                print('Error evaluating the connecting lines input properly')
            
            line = Lines(start3D,end3D)

            self.connectingLines.append(line)

            # print(f'linedrawer connecting lines {self.connectingLines} and the given start {tuple(start3D)} and end {tuple(end3D)}')
            self.redraw()
            self.connectingLinesTemp.clear()
            self.lineChecker = False
        else:
            
            self.connectingLinesTemp.append(node)
            self.checkedPos.append(pos)
            self.lineChecker = True
    
    def getNode(self,pos):
        for node in self.graphInputs:
            print(node.pos, pos, type(node.pos), type(pos))
            if node.pos == pos:
                return node

# Need this to be called when ever a connecting line is drawn
# Need to manipulate connectedlines list to be a dict where the start is the key and the end is the value
# Would this work or would it miss casses?
# Should then draw a  pygame.gfxdraw.filled_polygon() with the points as the parameters
    def detectConnectedPlane(self, points):
        def dfs(node, visited, path, start_node):
            if node in path:
                # Cycle detected
                cycle_start_index = path.index(node)
                cycle = path[cycle_start_index:]  # Extract the cycle
                if cycle[0] == start_node:  # Ensure it's a closed polygon
                    # Sort nodes in the cycle to create a canonical representation
                    sorted_cycle = tuple(sorted(cycle, key=lambda n: (n.x, n.y, n.z)))
                    if sorted_cycle not in unique_polygons and len(sorted_cycle) > 2:
                        unique_polygons.add(sorted_cycle)
                        polygons.append(cycle)
                return

            visited.add(node)
            path.append(node)

            for line in node.connections:
                next_node = line.node2 if line.node1 == node else line.node1
                if next_node not in visited or next_node == start_node:
                    dfs(next_node, visited, path, start_node)

            path.pop()  # Backtrack

        polygons = []
        unique_polygons = set()  # To store unique polygons
        for point in points:
            visited = set()
            dfs(point, visited, [], point)

        return polygons
 
 





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
        if all(num >= 200 for num in (x_input, y_input, z_input)):
            outOfRange = Thread(target=lambda: self.systemMessages('Error: Max Value = 200',False, True), daemon=True)
            outOfRange.start()
            return None
        self.graphInputs.append(Node(x_input,y_input,z_input))
        self.inputSubmit = True
        self.redraw()


# For connecting lines
class Node:
    def __init__(self,x,y,z):
        self.pos = (x,y,z)
        self.x = x
        self.y = y
        self.z = z
        self.connections = []


class Lines:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.node1.connections.append(self)
        self.node2.connections.append(self)

