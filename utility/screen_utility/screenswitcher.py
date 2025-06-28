import pygame
import pygame.gfxdraw  # Make sure to import this!

class ScreenSwitcher:
    def __init__(self):
        surf = pygame.display.get_surface()
        screen_size = surf.get_width(), surf.get_height()
        self.max_radius = (screen_size[0]**2 + screen_size[1]**2)**0.5  # diagonal length
        self.radius_float = self.max_radius  # start fully covered
        self.radius = int(self.radius_float)

        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.center = (surf.get_width() // 2, surf.get_height() // 2)

        self.screenStart = True
        self.finished = False
        self.active = False
        self.next_screen_func = None
        self.transition_speed = 1  # pixels per second (adjust to control timing)

    def start(self, next_screen_func):
        surf = pygame.display.get_surface()
        screen_size = surf.get_width(), surf.get_height()
        self.center = (surf.get_width() // 2, surf.get_height() // 2)
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)

        self.max_radius = (screen_size[0]**2 + screen_size[1]**2)**0.5
        self.radius_float = 0
        self.radius = 0
        self.active = True
        self.finished = False
        self.next_screen_func = next_screen_func

    def update_and_draw(self, target_surface, item_manager, dt):
        speed = self.transition_speed * dt  # pixels per second scaled by real dt


        self.overlay.fill((0, 0, 0, 0))  # Clear overlay

        if self.active:
            self.radius_float += speed
            self.radius = int(self.radius_float)

            if self.radius >= self.max_radius:
                self.radius = int(self.max_radius)
                self.finished = True
                self.active = False
                if self.next_screen_func:
                    self.next_screen_func()

        elif self.screenStart:
            self.radius_float -= speed
            self.radius = int(self.radius_float)

            if self.radius <= 0:
                self.radius = 0
                self.screenStart = False

        # Draw the anti-aliased circle if radius > 0
        if self.radius > 0:
            cx, cy = self.center
            pygame.gfxdraw.aacircle(self.overlay, int(cx), int(cy), self.radius, (0, 0, 0, 255))
            pygame.gfxdraw.filled_circle(self.overlay, int(cx), int(cy), self.radius, (0, 0, 0, 255))
            target_surface.blit(self.overlay, (0, 0))
