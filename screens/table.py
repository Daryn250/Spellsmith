import pygame
import sys
from utility.screenswitcher import ScreenSwitcher


FPS = 60


# make utility for items, item creator:
# make saving data for items, item saving and loading
# make table screen an actual table and not the blue abyss of torture
# make utility or something for switching ores between screens? maybe just use an inventory or something. Unsure bc I want to have ores with different types of imperfections

def table(screen):
    switcher = ScreenSwitcher()
    clock = pygame.time.Clock()

    # run table
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
        screen.fill('blue')

        switcher.update_and_draw(screen)
        pygame.display.flip()