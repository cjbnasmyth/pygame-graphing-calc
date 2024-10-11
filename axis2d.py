import pygame
from pygame.locals import *
import pygame_gui
import re

#https://stackoverflow.com/questions/59572663/pygame-window-not-showing-up
#https://pygame-gui.readthedocs.io/en/latest/events.html

# TO-DO
# FIX working out c value
# INtegrate into classes
# Formatting
# 


def show2D():
    pygame.init()

    window = pygame.display.set_mode((800, 600))

    window.fill((255, 255, 255))
    
    #x_line
    pygame.draw.line(window, (0, 0, 0), 
                    [100, 300], 
                    [500, 300], 5)

    #y_line
    pygame.draw.line(window, (0,0,0),
                    [300,500],
                    [300,100],5)
    
    #bounds square
    #https://stackoverflow.com/questions/6339057/draw-transparent-rectangles-and-polygons-in-pygame
    #set a transparent square to act as the bounds of the axis so that wehn a line intersects it the line is cut to the bounds
    # https://www.pygame.org/wiki/IntersectingLineDetection
    pygame.draw.line(window, (75,245,66),
                     [500,500],
                     [500,100],2)
    

    pygame.display.update()
    #UI manager handles call the update, draw and event handling functions of all the UI elements we create and assign to it
    manager = pygame_gui.UIManager((800,600))
    equation_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((500,500), (100, 50)),text='Show Equation', manager=manager)
    # gradient_slider = pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((500,100), (250,50)),start_value=0.0,value_range=[0,20], manager=manager)
    # gradient_output = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((575,200), (100,50)),manager=manager, text='Gradient Value')
    # c_slider= pygame_gui.elements.UIHorizontalSlider(relative_rect=pygame.Rect((500,300), (250,50)),start_value=0.0,value_range=[0,20], manager=manager)
    # c_output = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((575,400), (100,50)), text= 'C Value')
    gradient_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((500,100), (250,50)), manager=manager)
    c_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((500,300), (250,50)), manager=manager)
    
    clock = pygame.time.Clock()

    running = True
    while running:
        time_delta = clock.tick(60)/1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
            #     print('if statement one')
                # if event.ui_element == gradient_slider:
                #     c = 300
                #     m = gradient_slider.get_current_value()
                #     print(m)
                #     m = m*10
                # elif event.ui_element == c_slider:
                #     m = 1
                #     c = c_slider.get_current_value()
                #     c = (c*10)+300
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == equation_button:
                    # FIX WORKING OUT C
                    print('triggered')
                    m = (float(gradient_input.get_text()))
                    c = 300 -(float(c_input.get_text()))
                    if m > 10:
                        pass
                    elif m< 10:
                        next_y = (500-(500*(m)+c))+100
                        next_x = (next_y-c)/(m)
                    # while bounds == False:
                        # next_x = next_x+10
                        # next_y = next_y-(m/10)
                        # print(f'next_x: {next_x}, next_y: {next_y}')
                        # if next_x > 500:
                        #     bounds = True
                        #     next_x -= 10
                        #     next_y += (m/10)
                        # elif next_y < 100:
                        #     bounds = True
                        #     next_x -= 10
                        #     next_y += (m/10)
                        # else:
                        #     continue
                    print('reached line')
                    print(f'line quantities= m:{m},c:{c},next_x:{next_x},next_y{next_y}')
                    #M not working need to calculate in a way to faciliate quadartics etc. current approach incorrect
                    pygame.draw.line(window, (0,0,0),
                                    [300,c],
                                    [next_x,next_y],5)
                    equation_display = pygame_gui.elements.UITextBox(html_text = f'y = {gradient_input.get_text()}x + {c_input.get_text()}', relative_rect=pygame.Rect((500,400),(250,50)), manager=manager)
                    # pygame.draw.line(window, (0,0,0),
                    #                  [300,c],
                    #                  [-next_x,-next_y],5)
                    # NEED TO WORK OUT HOW TO APPLY bounds FUNCTION TO THIS AS WELL
                    # Make bounds a seperate function
                else:
                    pass
            # gradient_output.set_text(str(gradient_slider.get_current_value()))#BROKEN
            # c_output.set_text(str(c_slider.get_current_value()))#BROKEN
                    



            manager.process_events(event)
        manager.update(time_delta)
        manager.draw_ui(window)
        pygame.display.update()
    pygame.quit()

