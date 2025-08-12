import pygame
import moderngl
import ctypes
import os
user32 = ctypes.windll.user32
size = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


from utility.instanceManager import instanceManager
from utility.settingsManager import settingsManager


def run_game():
    # Initialize Pygame
    pygame.init()

    # Create the Pygame display with OpenGL enabled, resizing the window deletes the opengl flag. makes it work but change it when eventually adding shaders please
    screen = pygame.display.set_mode(
        (1920, 1080),
        flags=pygame.DOUBLEBUF | pygame.OPENGL,
    )

    # Force an initial resize event for layout consistency
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.event.post(pygame.event.Event(
        pygame.VIDEORESIZE,
        size=size,
        w=size[0],
        h=size[1]
    ))

    pygame.display.set_caption("SpellSmith")

    # Create a ModernGL context *AFTER* creating the OpenGL-enabled surface
    ctx = moderngl.create_context()
    ctx.enable_only(moderngl.BLEND)  # Enable blending only, for transparency


    # Start the game instance with the OpenGL context
    instanceManager(screen, settingsManager(), ctx)


# Entry point
run_game()
