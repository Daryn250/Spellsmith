import pygame
import moderngl


from utility.instanceManager import instanceManager
from utility.settingsManager import settingsManager


def run_game():
    # Initialize Pygame
    pygame.init()

    # Create the Pygame display with OpenGL enabled
    screen = pygame.display.set_mode(
        (960, 540),
        flags=pygame.DOUBLEBUF | pygame.OPENGL,
    )

    # Force an initial resize event for layout consistency
    pygame.event.post(pygame.event.Event(
        pygame.VIDEORESIZE,
        size=(960, 540),
        w=960,
        h=540
    ))

    pygame.display.set_caption("SpellSmith")

    # Create a ModernGL context *AFTER* creating the OpenGL-enabled surface
    ctx = moderngl.create_context()
    ctx.enable_only(moderngl.BLEND)  # Enable blending only, for transparency


    # Start the game instance with the OpenGL context
    instanceManager(screen, settingsManager(), ctx)


# Entry point
run_game()
