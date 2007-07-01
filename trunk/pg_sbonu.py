#!/usr/bin/env python
import time
import pygame
from pygame.locals import (
    FULLSCREEN,
    DOUBLEBUF,
    )


white = (255,) * 3
dark_green = 25, 85, 45
light_green = 200, 255, 200

food_image_file = 'data/spider_plant.png'
bug_image_file = 'data/bug0.png'

SCREEN_WIDTH, SCREEN_HEIGHT = SCREEN_DIMENSIONS = 800, 600 # 1024, 768


screen = pygame.display.set_mode(SCREEN_DIMENSIONS, DOUBLEBUF)
screen.fill(light_green)

food_image = pygame.image.load(food_image_file)
bug_image = pygame.image.load(bug_image_file)

screen.blit(food_image, (133, 100))
screen.blit(bug_image, (100, 90))

pygame.display.flip()

raw_input('Press enter to quit..')
