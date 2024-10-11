import pygame
from pygame.locals import *
import pygame_gui
import pygame_gui.elements.ui_horizontal_scroll_bar


class Functions:
    def __init__(self, m, w, s):
        self.window = w
        self.manager = m
        self.surface = s
    # def update(self):
    #     return pygame.display.update()


class graphContainer(Functions):
    # def __init__(self,c):
    #     self.container = c

    # def createContainer(self):


    # def createScrollingContainer(self):
    #     # self.s = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect((0,0),(800,600)), manager=self.manager, allow_scroll_x= True, allow_scroll_y= True, object_id= 'graph')
    #     # self.s.set_scrollable_area_dimensions((2000,2000)) #Must be greater than 800,600
    #     self.hBar = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((0,580),(780,20)), start_value= 0, value_range=[0,380], manager=self.manager)
    #     self.vBar = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((780,0),(20,580)), start_value=0, value_range=[0,380], manager=self.manager)
    #     # self.hBar.set_current_value(195,False)
    #     return self.hBar, self.vBar

    def graphMovement(self):
        
    def draw_axis(self):
        # x line
        pygame.draw.line(self.window, (0,0,0),
                        [0, 300],
                        [780,300], 2)
        
        # y line
        pygame.draw.line(self.window, (0,0,0),
                        [400,580],
                        [400,0], 2)
    
    def redraw(self):
        pass

    def trigCalc(self):
        pass

    def getScollValue(self):
        pass

class hudUI(Functions):
    def createGUI(self):
        self.hud = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((800,600) ,(800,600)), manager=self.manager, object_id='hud')
