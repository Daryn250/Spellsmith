import pygame
import pygame.gfxdraw

class ScreenSwitcher:
    def __init__(self, transition_duration=1.0):
        surf = pygame.display.get_surface()
        screen_size = surf.get_width(), surf.get_height()
        self.max_radius = (screen_size[0] ** 2 + screen_size[1] ** 2) ** 0.5
        self.radius = self.max_radius

        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.center = (surf.get_width() // 2, surf.get_height() // 2)

        self.screenStart = True
        self.finished = False
        self.active = False
        self.transition_phase = "out"

        self.next_screen_func = None
        self.save_callback = None

        self.transition_duration = transition_duration
        self.elapsed_time = 0.0

    def start(self, next_screen_func, save_callback):
        surf = pygame.display.get_surface()
        screen_size = surf.get_width(), surf.get_height()
        self.center = (surf.get_width() // 2, surf.get_height() // 2)
        self.overlay = pygame.Surface(screen_size, pygame.SRCALPHA)
        self.max_radius = (screen_size[0] ** 2 + screen_size[1] ** 2) ** 0.5

        self.next_screen_func = next_screen_func
        self.save_callback = save_callback

        self.active = True
        self.finished = False
        self.elapsed_time = 0.0
        self.transition_phase = "in"

    def force_finish(self):
        """Forcefully finish the transition immediately."""
        if self.active and self.transition_phase == "in":
            self.radius = int(self.max_radius)
            self.active = False
            self.finished = True

            if self.save_callback:
                self.save_callback()
            if self.next_screen_func:
                self.next_screen_func()

    def update(self, dt):
        if self.active or self.screenStart:
            self.elapsed_time += dt / 1000.0
            progress = min(self.elapsed_time / self.transition_duration, 1.0)

            if self.transition_phase == "in":
                self.radius = int(progress * self.max_radius)
                if progress >= 1.0:
                    self.force_finish()

            elif self.transition_phase == "out":
                self.radius = int((1.0 - progress) * self.max_radius)
                if progress >= 1.0:
                    self.radius = 0
                    self.screenStart = False
        else:
            self.radius = 0

    def draw(self, target_surface):
        self.overlay.fill((0, 0, 0, 0))
        if self.radius > 0:
            cx, cy = map(int, self.center)
            r = int(self.radius)
            pygame.gfxdraw.aacircle(self.overlay, cx, cy, r, (0, 0, 0, 255))
            pygame.gfxdraw.filled_circle(self.overlay, cx, cy, r, (0, 0, 0, 255))
            target_surface.blit(self.overlay, (0, 0))
