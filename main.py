import pygame
import screens.main_menu as main_menu
import screens.workstation as workstation
import screens.furnaceScreen as furnaceScreen
from utility.instanceManager import instanceManager
from utility.settingsManager import settingsManager

def run_game():
    pygame.init()
    screen = pygame.display.set_mode((800, 600), flags = pygame.DOUBLEBUF | pygame.HWACCEL, vsync=60)

    pygame.event.post(pygame.event.Event(pygame.VIDEORESIZE, size=(480,270), w=480, h=270))
    pygame.display.set_caption("SpellSmith")

    instanceManager(screen, settingsManager())

run_game()
