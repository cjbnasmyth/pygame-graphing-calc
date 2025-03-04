import pygame
import pygame_gui
from pygame.locals import *

pygame.init()

width, length = 800, 600
surface = pygame.Surface((width, length))
manager = pygame_gui.UIManager((width, length))
window = pygame.display.set_mode((width, length))
window.fill((255, 255, 255))

hMove, vMove = 0, 0
cameraArray = [hMove, vMove]

clock = pygame.time.Clock()
running = True
while running:
    time_delta = clock.tick(60) / 1000
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                hMove -= 1
            if event.key == K_RIGHT:
                hMove += 1
            if event.key == K_UP:
                vMove += 1
            if event.key == K_DOWN:
                vMove -= 1
            print(hMove, vMove)
            # Only redraw when camera moves
            if hMove == 0 and vMove == 0:
                pygame.draw.line(window, (255, 0, 0), (100, 300), (700, 300), 2)
                pygame.draw.line(window, (0, 255, 0), (400, 100), (400, 500), 2)
                pygame.draw.line(window, (0, 0, 255), (400, 300), (400, 300), 2)
                print('redrawn')
            else:
                window.fill((255, 255, 255))  # Only fill the background when camera moves

    manager.process_events(event)
    manager.update(time_delta)
    manager.draw_ui(window)
    
    pygame.display.update()