import pygame
import pygame_gui
import random


# Create a simple 800 by 600 px window that is definitly too small for the big
# surfaces
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Create the UIManager
manager = pygame_gui.UIManager((width, height))

# Create a UIScrollingContainer that fits exactly into the window/screen
# defined above
scroll_space = pygame_gui.elements.UIScrollingContainer(
    relative_rect = pygame.Rect((0,0),(width,height)),
    manager=manager)

scroll_space.set_scrollable_area_dimensions((2000,2000))

loaded_image = pygame.image.load("tree.jpg")
grid_image = pygame_gui.elements.UIImage(
    relative_rect=pygame.Rect((0,0),(2000,2000)),
    image_surface=loaded_image,
    manager=manager,
    container=scroll_space)


clock = pygame.time.Clock()
running = True
while running:
    time_delta = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Make sure to pass all GUI events also to the UIManager
        manager.process_events(event)

    # The UIImanager has to be updated with the time that has passed since the
    # last update call 
    manager.update(time_delta)
    # Call the draw_ui() function of the manager to draw all UI elements
    # handled by the pygame_gui UiManager
    manager.draw_ui(screen)

    pygame.display.update()