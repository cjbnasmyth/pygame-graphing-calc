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
import config
from mysql.connector import connect, Error
from collections import defaultdict


pygame.freetype.init()

class Interfaces:
    def __init__(self, m, w, s):
        self.window = w
        self.manager = m
        self.surface = s
        self.widgets = {}
        self.state = None
        # CONFIG FILE?
        self.defaultFont = pygame.freetype.Font(None, 20)
        self.pwdState = True
        self.menu_created = False

    def hideAllWidgets(self):
        for i in self.widgets.values():
            i.hide()


    def systemMessages(self, message, startMenu = False, error=False):
        if error:
            colour = (255,0,0)
        else:
            colour = (0,255,0)
        if startMenu:
            self.defaultFont.render_to(self.window, (300,580), message, fgcolor=colour)
            pygame.display.update()
            sleep(1)
            pygame.draw.rect(self.window, (0,0,0), pygame.Rect(300,580,500,20))
        else:
            if error:
                self.defaultFont.render_to(self.window, (600,20), 'Error:', fgcolor=colour)
                self.defaultFont.render_to(self.window, (600,40), message, fgcolor=colour)
            else:
                self.defaultFont.render_to(self.window, (600,20), message, fgcolor=colour)
            sleep(1)
            pygame.draw.rect(self.window, (255,255,255), pygame.Rect(600, 0, 200,80))
        
    # def renderWidgets(self):
    #     for i in self.widgets.values():
    #         i.render()

    
    def getInput(self, label):
        try:
            return self.widgets[label].getText()
        except:
            print(f'Label: {label} doesnt exsist') # Logs error in terminal

    def changeState(self):
        if self.state =='start_menu':
            self.hideAllWidgets()
            self.state = 'main_menu'
        elif self.state == 'main_menu':
            self.menu_created = False
            self.hideAllWidgets()
            self.state = 'start_menu'
        print(f"state changed state = {self.state}") # Logs change of state in terminal


class StartMenu(Interfaces):
    def __init__(self, m, w, s):
        self.targetUser = []
        super().__init__(m, w, s)
    def createStartMenu(self):
        self.state = 'start_menu'
        self.menu_created = True
        self.window.fill((0,0,0))
        self.defaultFont.render_to(self.window, (250,80), 'Username:', fgcolor=(255,255,255))
        self.widgets['username'] = TextBox(
            self.window, 250, 100,
            300,50
        )
        self.defaultFont.render_to(self.window, (250,180), 'Password:', fgcolor=(255,255,255))
        self.widgets['password'] = TextBox(
            self.window, 250, 200,
            300, 50,
            font = config.pwdFont
        )
        self.defaultFont.render_to(self.window, (600,260), 'Show', fgcolor=(255,255,255))
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
        if sqlSubmit == False:
            verifyFail = Thread(target=lambda: self.systemMessages('Error: Incorrect Password or Account Type', True, True), daemon=True)
            verifyFail.start()
            return None
        else:
            config.menu_type = self.widgets['account_type_dropdown'].getSelected()
            self.targetUser.clear()
            logInSuccess = Thread(target=lambda: self.systemMessages('Logged in!', True, False), daemon=True)
            logInSuccess.start()
            sleep(1)
            self.changeState()

    def getTextFields(self):
        username = self.getInput('username')
        password = self.getInput('password')
        accountType = self.widgets['account_type_dropdown'].getSelected()
        return [username, password, accountType]
    
    def checkSubmit(self):
        data = self.getTextFields()
        if [data[0],data[2]] != self.targetUser[0]:
            return False
        checkConn = connect(**config.DB_INFO) # Sensitive database info stored in separate config.py file
        checkCursor = checkConn.cursor(buffered=True)
        query = ('SELECT password, accountType FROM users '
                 'WHERE username = %s')
        checkCursor.execute(query, (data[0],)) # Takes the username as the input for query
        condition = checkCursor.fetchone()
        if condition:
                retrievedPassword, retrievedAccountType = condition
                if retrievedPassword != data[1] or retrievedAccountType != data[2]:
                    return False
                else:
                    return True
        else:
            return False


    def addAccount(self):
        data = self.getTextFields()
        conn = connect(**config.DB_INFO)
        cursor = conn.cursor(buffered=True)
        checkQuery = ('SELECT * FROM users '
                    'WHERE username = %s')
        cursor.execute(checkQuery, (data[0],))
        check = cursor.fetchone()
        if any(not element for element in data):
            emptyField = Thread(target=self.systemMessages('Error: Input field empty', True,True),daemon=True)
            emptyField.start()
            check = False
        else:
            pass 
        if check is None:
            addQuery = ('INSERT INTO users ' 
                    '(username, password, accountType) ' 
                    'VALUES (%s, %s, %s)')
            cursor.execute(addQuery, (data[0], data[1], data[2]))
            accountSuccess = Thread(target=self.systemMessages('Account Created!', True, False),daemon=True)
            accountSuccess.start()
            self.targetUser.append([data[0],data[2]])

        else:
            usernameTaken = Thread(target=self.systemMessages('Error: Username Already Taken', True, True), daemon=True)
            usernameTaken.start()

        conn.commit()
        cursor.close()
        conn.close() # Close connection to database preventing unwanted changes








class MainMenu(Interfaces):
    def __init__(self, m, w, s):
        self.hMove, self.vMove = 0, 0
        self.graph_surface = pygame.Surface((600,600))
        self.graphInputs = []
        self.mathConversion = {}
        self.drawnPoints = {}
        self.connectingLines = []
        self.lineChecker = False
        self.connectingLinesTemp = []
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
        self.window.blit(self.graph_surface, (0,0)) # Merges the graph surface onto the main surface


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
        self.defaultFont.render_to(self.graph_surface, (xlabelCoords[0], xlabelCoords[1]), 'X', fgcolor=(255,0,0))
    
    def drawYAxis(self):
        # y line
        yStart = self.projection([0,-200,0])
        yEnd = self.projection([0,200,0])
        pygame.draw.line(self.graph_surface, (0,255,0),
                        yStart,
                        yEnd, 2)
        
        yLabelCoords = self.projection([5,220,0])
        self.defaultFont.render_to(self.graph_surface, (yLabelCoords[0], yLabelCoords[1]), 'Y', fgcolor=(0,255,0))
    
    def drawZAxis(self):
        # z line
        zStart = self.projection([0,0,-200])
        zEnd = self.projection([0,0,200])
        pygame.draw.line(self.graph_surface, (0,0,255), zStart, zEnd, 2)

        zLabelCoords = self.projection([5,5,220])
        self.defaultFont.render_to(self.graph_surface, (zLabelCoords[0], zLabelCoords[1]), 'Z', fgcolor=(0,0,255))

    def getMathPoint(self, point3D):
        for key, value in self.mathConversion.items():
            if key == point3D:
                return value
        return None


    def redraw(self):
        self.graph_surface.fill((255,255,255))

        # Axis 1st
        self.drawAxis()

        # Points 2nd
        if len(self.graphInputs) > 0:
            for node in self.graphInputs:
                newPos = self.projection(node.pos)
                self.mathConversion[node.pos] = newPos
                pointCircle = pygame.draw.circle(self.graph_surface, (0,0,0), (newPos[0],newPos[1]), 4)
                self.addDrawnPoints(newPos[0],newPos[1], pointCircle)
        
        # Planes 3rd
        if len(self.connectingLines)>2:
            planeDetector = self.detectConnectedPlane(self.graphInputs)
            planePoints = []
            if planeDetector:
                for plane in planeDetector:
                    for node in plane:
                        planePoints.append(self.mathConversion.get(node.pos))
                    pygame.gfxdraw.filled_polygon(self.graph_surface, [value for value in planePoints], (160,244,225)) # Draws a polygon with the vertices being nodes in cycle
                    planePoints.clear()
            else:
                pass
        else:
            pass
        # Connecting lines 4th
        for line in self.connectingLines:
            startPos = self.projection(line.node1.pos)
            endPos = self.projection(line.node2.pos)
            pygame.draw.line(self.graph_surface, (255,165,0), startPos, endPos, 2)
        
        # Points labels 5th
        for node in self.graphInputs:
            labelFont = pygame.freetype.Font(None, 10) # Sets a smaller font size for labels
            xPointLabel = self.projection([node.x-5,-10,0])
            yPointLabel = self.projection([-20,node.y-5,0])
            zPointLabel = self.projection([-20,0,node.z-5])
            labelFont.render_to(self.graph_surface, (xPointLabel[0], xPointLabel[1]), str(node.x), fgcolor=(255,0,0))
            labelFont.render_to(self.graph_surface, (yPointLabel[0], yPointLabel[1]), str(node.y), fgcolor=(0,255,0))
            labelFont.render_to(self.graph_surface, (zPointLabel[0], zPointLabel[1]), str(node.z), fgcolor=(0,0,255))

        pygame.draw.rect(self.window, (255,255,255), pygame.Rect(200,130,600,270)) # Clears points menu area
        self.createPointsMenu()
        self.window.blit(self.graph_surface, (0,0))




    def rotatePoint(self, point, axis, theta):
        point = np.array(point) # Converts to a numpy array
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis) # Ensures that axis = a unit vector (np.linalg.norm(axis) = magnitude of vector)

        # Rodrigues' rotation formula
        cosTheta = np.cos(theta)
        sinTheta = np.sin(theta)
        crossProduct = np.cross(axis, point)
        dotProduct = np.dot(axis, point)

        rotatedPoint = (cosTheta * point) + (sinTheta * crossProduct) + ((1 - cosTheta) * dotProduct * axis)
        return rotatedPoint    
    
    def pointTransformation(self, point):
        
        yaw = np.radians(self.hMove) # Converts to radians
        pitch = np.radians(self.vMove)
        
        transformedPoint = self.rotatePoint(point, [0, 1, 0], yaw)
        transformedPoint = self.rotatePoint(transformedPoint, [1, 0, 0], pitch)

        return transformedPoint


    def projection(self, elementPosition):
        finalPoint = self.pointTransformation(elementPosition)

    

        screenCenterX, screenCenterY = 600//2, 600//2
        x, y, z = finalPoint
        scale = 1


        
        projectedX = (x * scale) + screenCenterX
        projectedY = (-y * scale) + screenCenterY

        return [projectedX, projectedY]

    def createPointsMenu(self):
        for count,point in enumerate(self.graphInputs[::-1]): # enumerate generates a tuple of (index, value) for each element in the list
            y = 130+(30*count)
            label = len(self.graphInputs)-count
            self.defaultFont.render_to(self.window, (600,y), f'{label}: {str(point.pos)}', fgcolor=(255,0,0))
            self.widgets[label] = Button(
                self.window, 770, y,
                20,20,
                text = 'X',
                onClick = lambda x=label, y = point: self.deletePointFromGraph(x, y)
            )

    def deletePointFromGraph(self,label, point):
        self.graphInputs.remove(point)
        self.widgets[label].hide() # ‘Deletes’ the widget from screen
        for connections in point.connections:
            if len(self.connectingLines) == 0:
                point.connections.clear()
            else:
                pass
            if connections in self.connectingLines:
                self.connectingLines.remove(connections)
            else:
                print(f"Warning: Tried to remove {connections}, but it wasn't in {self.connectingLines}") # Logs potentially error/warning in terminal
        self.redraw()



    def lineDrawer(self, pos):
        x, y = pos


        point3D = [key for key,value in self.mathConversion.items() if value[0] == x and value[1] == y][0] # Retrieves the corresponding 3D point for the given 2D values
        node = self.getNode(point3D) # Retrieves the node object corresponding to the 3D point
        if self.lineChecker:
            self.connectingLinesTemp.append(node)

            start3D = self.connectingLinesTemp[0]
            end3D = self.connectingLinesTemp[1]

            line = Lines(start3D,end3D)
            self.connectingLines.append(line)

            self.redraw()
            self.connectingLinesTemp.clear()
            self.lineChecker = False
        else:
            self.connectingLinesTemp.append(node)
            self.lineChecker = True
    
    def getNode(self,pos):
        for node in self.graphInputs:
            if node.pos == pos:
                return node

    def detectConnectedPlane(self, points):
        def dfs(node, visited, path, startNode):
            if node in path:
                # Cycle detected
                cycleStart = path.index(node)
                cycle = path[cycleStart:]  # Extract the cycle
                if cycle[0] == startNode:  # Ensure it's a closed polygon
                    sortedCycle = tuple(sorted(cycle, key=lambda n: (n.x, n.y, n.z)))
                    if sortedCycle not in uniquePolygons and len(sortedCycle) > 2:
                        uniquePolygons.add(sortedCycle)
                        polygons.append(cycle)
                return # Breaks recursion

            visited.add(node)
            path.append(node)

            for line in node.connections:
                nextNode = line.node2 if line.node1 == node else line.node1 # Ensures the next node is not the current node (ie choosing the right node from node1/node2)
                if nextNode not in visited or nextNode == startNode:
                    dfs(nextNode, visited, path, startNode)

            path.pop()

        polygons = []
        uniquePolygons = set()
        for point in points: # Iterates through all points
            visited = set()
            dfs(point, visited, [], point)

        return polygons
 
 





    def handleInput(self):
        # Error message to prevent pointsMenu overflow (spacing allows for 9)
        if len(self.graphInputs) == 9:
            pMenuOverflowThread = Thread(target=lambda : self.systemMessages('Max No. Points',False, True), daemon=True)
            pMenuOverflowThread.start()
            return None
        try:
            x_input = int(self.getInput('inputEntry1'))
            y_input = int(self.getInput('inputEntry2'))
            z_input = int(self.getInput('inputEntry3'))
        except:
            invalidInputType = Thread(target=lambda: self.systemMessages('Invlaid Type Input', False, True), daemon=True)
            invalidInputType.start()
            return None
        if max(x_input, y_input, z_input) > 200:
            outOfRange = Thread(target=lambda: self.systemMessages('Max Value = 200',False, True), daemon=True)
            outOfRange.start()
            return None
        
        self.graphInputs.append(Node(x_input,y_input,z_input))

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

