import pygame
import os
import sys

def pwdPath(relateivePath):
    try:
        basePath = sys._MEIPASS
    except AttributeError:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relateivePath)
pygame.font.init()
menu_type = ''
pwdFont = pygame.font.Font(pwdPath('password.ttf'))


DB_INFO = {
    'user': '25charlie',
    'password': '?r954ykL3',
    'host': '77.68.120.9',
    'database': '25charlie'
}