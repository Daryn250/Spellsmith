# helps wrap during resizing of the screen

import pygame
import random

class VirtualScreen:
    def __init__(self, virtual_size):
        self.virtual_width, self.virtual_height = virtual_size
        self.surface = pygame.Surface(virtual_size)

        self.shake_timer = 0
        self.shake_duration = 0
        self.shake_magnitude = 0

    def get_surface(self):
        """Get the surface to draw your game onto."""
        return self.surface

    def draw_to_screen(self, target_screen):
        window_width, window_height = target_screen.get_size()

        # Calculate scale factor that fills screen (cropping excess)
        scale = max(
            window_width / self.virtual_width,
            window_height / self.virtual_height
        )

        # Final scaled size
        scaled_width = int(self.virtual_width * scale)
        scaled_height = int(self.virtual_height * scale)

        # Scale virtual surface
        scaled_surface = pygame.transform.scale(self.surface, (scaled_width, scaled_height))

        # Default crop offset (centered)
        offset_x = (scaled_width - window_width) // 2
        offset_y = (scaled_height - window_height) // 2

        # Shake offsets
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x += random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y += random.randint(-self.shake_magnitude, self.shake_magnitude)

        # Clamp offset to keep subsurface in bounds
        offset_x = max(0, min(offset_x, scaled_width - window_width))
        offset_y = max(0, min(offset_y, scaled_height - window_height))

        # Safe subsurface crop
        cropped_surface = scaled_surface.subsurface(
            (offset_x, offset_y, window_width, window_height)
        )

        # Blit final result
        target_screen.blit(cropped_surface, (0, 0))


    def get_virtual_mouse(self, window_size):
        """Map real mouse position to virtual resolution (cropping version)."""
        win_w, win_h = window_size

        scale = max(
            win_w / self.virtual_width,
            win_h / self.virtual_height
        )

        scaled_width = self.virtual_width * scale
        scaled_height = self.virtual_height * scale

        offset_x = (scaled_width - win_w) / 2
        offset_y = (scaled_height - win_h) / 2

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Translate to scaled virtual space
        virt_x = (mouse_x + offset_x) / scale
        virt_y = (mouse_y + offset_y) / scale

        return int(virt_x), int(virt_y)
    
    def get_virtual_mouse_now(self):
        return self.get_virtual_mouse(pygame.display.get_surface().get_size())
    
    def start_shake(self, duration, magnitude):
        self.shake_timer = duration
        self.shake_duration = duration
        self.shake_magnitude = magnitude




