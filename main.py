import pygame
import pygame_gui.ui_manager
from functions import *

pygame.init()

width,length = 800, 600
surface = pygame.Surface((width,length))
manager= pygame_gui.UIManager((width, length))
window = pygame.display.set_mode((width, length))
window.fill((255,255,255))

bottomLayer = graphContainer(manager, window, surface)
hBar = bottomLayer.createScrollingContainer()
# topLayer = hudUI(manager, window, surface)
# for scrolling to work there must be something in the graph container
bottomLayer.draw_axis()
pygame.display.update() #embedded into a Functions class

clock = pygame.time.Clock()
running = True
while running:
    time_delta = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        manager.process_events(event)
    # print(hBar.get_current_value())
    manager.update(time_delta)
    manager.draw_ui(window)
    pygame.display.update()