import pygame
import pygame_gui.ui_manager
import pygame_widgets
import ast
from functions import *

pygame.init() # Intitializing the pygame module

width,length = 800, 600
surface = pygame.Surface((width,length))
manager= pygame_gui.UIManager((width, length))
window = pygame.display.set_mode((width, length))
window.fill((255,255,255))

hMove, vMove = 0, 0
bottomLayer = MainMenu(manager, window, surface) # Instantiating the MainMenu object
topLayer = StartMenu(manager,window, surface) # Instantiating the StartMenu object


topLayer.createStartMenu() # topLayer refers to the start menu screen

clock = pygame.time.Clock()
running = True
while running:
    time_delta = clock.tick(60)/1000
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and bottomLayer.menu_created == True:
            if event.key == K_LEFT:
                bottomLayer.hMove += 2
            if event.key == K_RIGHT:
                bottomLayer.hMove -= 2
            if event.key == K_UP:
                bottomLayer.vMove += 2
            if event.key == K_DOWN:
                bottomLayer.vMove -= 2
            window.fill((255,255,255))
            bottomLayer.drawnPoints.clear()
            bottomLayer.redraw()
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y  = event.pos
            values = bottomLayer.drawnPoints.values()
            for values in values:
                if values.collidepoint(event.pos):
                    drawerPos = [key for key,value in bottomLayer.drawnPoints.items() if value == values][0] # Retrieves the 2D point of the pygame object clicked on
                    bottomLayer.lineDrawer(drawerPos)
        if topLayer.state == 'main_menu':
            bottomLayer.createMainMenu()
            topLayer.state = 'start_menu'
        if bottomLayer.state == 'start_menu':
            topLayer.createStartMenu()
            bottomLayer.state = 'main_menu'

    manager.process_events(event)

    manager.update(time_delta)
    manager.draw_ui(window)
    pygame_widgets.update(events)
    pygame.display.update()