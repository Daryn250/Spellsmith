import pygame
import random

class VirtualScreen:
    def __init__(self, virtual_size):
        self.virtual_width, self.virtual_height = virtual_size
        self.surface = pygame.Surface(virtual_size)

        self.shake_timer = 0
        self.shake_duration = 0
        self.shake_magnitude = 0
        self.shake_offset = (0, 0)

        self.output_size = virtual_size

    def get_surface(self):
        """Get the surface to draw your game onto."""
        return self.surface

    def draw_to_screen(self, target_screen, source_surface=None):
        if source_surface is None:
            source_surface = self.surface

        window_width, window_height = target_screen.get_size()

        # Calculate scale factor to fill screen (crop excess)
        scale = max(
            window_width / self.virtual_width,
            window_height / self.virtual_height
        )

        # Final scaled size
        scaled_width = int(self.virtual_width * scale)
        scaled_height = int(self.virtual_height * scale)

        # ✅ Apply screen shake BEFORE scaling
        if self.shake_timer > 0:
            self.shake_timer -= 1
            offset_x = random.randint(-self.shake_magnitude, self.shake_magnitude)
            offset_y = random.randint(-self.shake_magnitude, self.shake_magnitude)
            self.shake_offset = (offset_x, offset_y)
        else:
            self.shake_offset = (0, 0)

        # Create a temporary surface for shaking
        temp_surface = pygame.Surface((self.virtual_width, self.virtual_height))
        temp_surface.fill((0, 0, 0))  # Black border padding for shake

        ox, oy = self.shake_offset
        temp_surface.blit(source_surface, (ox, oy))


        # Scale the temp surface
        scaled_surface = pygame.transform.scale(temp_surface, (scaled_width, scaled_height))

        # Center-crop to screen size
        offset_x = (scaled_width - window_width) // 2
        offset_y = (scaled_height - window_height) // 2

        # Crop the center region to match window size
        cropped_surface = scaled_surface.subsurface(
            (offset_x, offset_y, window_width, window_height)
        )

        # Blit to screen
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

        # ✅ Account for shake offset if needed
        shake_x, shake_y = self.shake_offset
        virt_x -= shake_x
        virt_y -= shake_y

        return int(virt_x), int(virt_y)

    def get_virtual_mouse_now(self):
        return self.get_virtual_mouse(pygame.display.get_surface().get_size())

    def start_shake(self, duration, magnitude):
        self.shake_timer = duration
        self.shake_duration = duration
        self.shake_magnitude = magnitude

    def resize(self, width, height):
        """
        Call this when the window is resized.
        We'll update our output_size so draw_to_screen scales correctly.
        """
        self.output_size = (width, height)