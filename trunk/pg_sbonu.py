#!/usr/bin/env python
import time
import pygame
from pygame.locals import (
    FULLSCREEN,
    DOUBLEBUF,
    )


food_image_file = '../spider_plant.png'
SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_DIMENSIONS = 800, 600 # 1024, 768


screen = pygame.display.set_mode(SCREEN_DIMENSIONS, DOUBLEBUF)

food_image = pygame.image.load(food_image_file)
screen.blit(food_image, (100, 100))
pygame.display.flip()

raw_input('Press enter to quit..')
