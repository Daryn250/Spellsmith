import pygame
import sys
from utility.screenswitcher import ScreenSwitcher


FPS = 60

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