# sanity_pp.py
import pygame, moderngl
from utility.shaderManager import ShaderManager

pygame.init()
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,
                                pygame.GL_CONTEXT_PROFILE_CORE)

screen_size = (640, 480)
pygame.display.set_mode(screen_size, pygame.OPENGL|pygame.DOUBLEBUF)
ctx = moderngl.create_context()

# load your image
img = pygame.image.load("hmg.png").convert_alpha()
img = pygame.transform.scale(img, screen_size)

# setup shaders
sm = ShaderManager(ctx, initial_size=screen_size)
sm.add_shader("invert",  "assets/shaders/_default.vert", "assets/shaders/invert.frag")
sm.add_shader("default", "assets/shaders/_default.vert", "assets/shaders/default.frag")

clock = pygame.time.Clock()
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    # run only the invert pass, then final passthrough
    sm.post_process(["invert"], img)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
