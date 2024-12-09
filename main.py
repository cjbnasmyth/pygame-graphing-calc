import pygame
import pygame_gui.ui_manager
import pygame_widgets
from functions import *

pygame.init()

width,length = 800, 600
surface = pygame.Surface((width,length))
manager= pygame_gui.UIManager((width, length))
window = pygame.display.set_mode((width, length))
window.fill((255,255,255))

hMove, vMove = 0, 0
cameraArray = [hMove,vMove]
bottomLayer = mainMenu(manager, window, surface)
topLayer = startMenu(manager,window, surface)
# hBar = bottomLayer.createScrollingContainer()
# topLayer = hudUI(manager, window, surface)
# for scrolling to work there must be something in the graph container
#embedded into a Functions class

topLayer.createStartMenu()

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
                bottomLayer.hMove -= 1
            if event.key == K_RIGHT:
                bottomLayer.hMove += 1
            if event.key == K_UP:
                bottomLayer.vMove += 1
            if event.key == K_DOWN:
                bottomLayer.vMove -= 1
            print('redrawn')
            window.fill((255,255,255))
            bottomLayer.redrawPoints()
        if topLayer.state == 'main_menu':
            bottomLayer.createMainMenu()
    manager.process_events(event)

    manager.update(time_delta)
    manager.draw_ui(window)
    pygame_widgets.update(events)
    pygame.display.update()