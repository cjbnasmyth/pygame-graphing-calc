import pygame
from pygame.locals import *
import pygame_gui
# from functions import

pygame.init()

window = pygame.display.set_mode((800, 600))

window.fill((255, 255, 255))
pygame.display.update()
manager = pygame_gui.UIManager((800,600))
# hud container contains all the inputs and everything EXCEPT the graph

# hud = pygame_gui.elements.UIPanel(relative_rect=pygame.Rect((800,600) ,(800,600)), manager=manager, object_id='hud')
# graph holds the scrollable container
graph = pygame_gui.elements.UIScrollingContainer(relative_rect=pygame.Rect((0,0),(800,600)), manager=manager, allow_scroll_x= True, allow_scroll_y= True, object_id= 'graph')
surface = pygame.Surface((800,600))

graph.set_scrollable_area_dimensions((2000,2000))
# x line
pygame.draw.line(surface, (0,0,0),
                 [100, 300],
                 [500,300], 2)

# y line
pygame.draw.line(surface, (0,0,0),
                 [300,500],
                 [300,100], 2)

pygame.display.update()
# https://pygame-gui.readthedocs.io/en/latest/quick_start.html
clock = pygame.time.Clock()
running = True

while running:
    time_delta = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        manager.process_events(event)
    
    manager.update(time_delta)
    manager.draw_ui(window)
pygame.display.update()
pygame.quit()


# ----TO-DO-----
# Container for the graph
# Matrix calculations for 3D
# 'Drag' the graph around 
# Points input 
# Show the values on the axis of the 3D graph
# Fill the 'shapes' with colour connecting the points