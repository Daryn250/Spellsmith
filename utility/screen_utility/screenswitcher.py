import pygame
class ScreenSwitcher:
    def __init__(self):
        surf = pygame.display.get_surface()
        screen_size = surf.get_width(), surf.get_height()
        self.radius = int((screen_size[0]**2 + screen_size[1]**2)**0.5)  # Covers whole screen diagonally
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.center = (surf.get_width() // 2, surf.get_height() // 2)

        self.screenStart = True # for fading into a screen
        self.finished = False
        self.active = False # fading out of a screen
        self.next_screen_func = None

    def start(self, next_screen_func):
        surf = pygame.display.get_surface()
        self.center = (surf.get_width() // 2, surf.get_height() // 2)
        screen_size = surf.get_width(), surf.get_height()
        self.active = True
        self.radius = 0
        self.finished = False
        self.next_screen_func = next_screen_func
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.max_radius = int((screen_size[0]**2 + screen_size[1]**2)**0.5)  # Covers whole screen diagonally

    def update_and_draw(self, target_surface):
        if self.active:
            # Clear overlay to fully transparent
            self.overlay.fill((0, 0, 0, 0))

            # Draw expanding black circle
            pygame.draw.circle(self.overlay, (0, 0, 0, 255), self.center, self.radius)

            # Blit the overlay onto the screen
            target_surface.blit(self.overlay, (0, 0))

            # Increase radius
            self.radius += 30

            # Switch screens once fully covered
            if self.radius >= self.max_radius and not self.finished:
                self.finished = True
                self.active = False
                if self.next_screen_func:
                    self.next_screen_func()
        
        if self.screenStart:
            # Clear overlay to fully transparent
            self.overlay.fill((0, 0, 0, 0))

            # Draw expanding black circle
            pygame.draw.circle(self.overlay, (0, 0, 0, 255), self.center, self.radius)

            # Blit the overlay onto the screen
            target_surface.blit(self.overlay, (0, 0))

            # Increase radius
            self.radius -= 30

            # Switch screens once fully covered
            if self.radius <= 0:
                self.radius = 0
                self.screenStart = False
