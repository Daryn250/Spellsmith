import pygame
import screens.main_menu as main_menu
import screens.testing as test
import screens.workstation as workstation

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), pygame.SCALED | pygame.DOUBLEBUF)

    pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, size=(480,270), w=480, h=270))
    pygame.display.set_caption("SpellSmith")

    #main_menu.main_screen(screen) uncomment when done testing
    workstation.workstation(screen)

run_game()
