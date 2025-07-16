import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.itemMaker import makeItem
from screens.table import table  # Import early to support previous_screen lambda
import math

class WorkstationHelper:
    def __init__(self, screen_size, brightness=1.0, enable_blur=False):
        self.backdrop_anim = AnimatedTile("assets/screens/workstation/backdrop.png", frame_duration=120)
        self.overlay_anim = AnimatedTile("assets/screens/workstation/workstation.png", frame_duration=150)

        self.screen_size = screen_size
        self.time = 0.0
        self.brightness = brightness
        self.sway_amplitude = 3  # pixels
        self.sway_speed = 1.5     # radians/sec
        self.enable_blur = enable_blur

    def update(self, dt, item_manager, virtual_mouse, screen):
        self.backdrop_anim.update(dt)
        self.overlay_anim.update(dt)
        self.time += dt / 1000

    def apply_brightness(self, surface):
        if self.brightness == 1.0:
            return surface

        result = surface.copy()
        if self.brightness < 1.0:
            dim_value = int(self.brightness * 255)
            result.fill((dim_value, dim_value, dim_value, 255), special_flags=pygame.BLEND_RGBA_MULT)
        else:
            added = int((self.brightness - 1.0) * 255)
            result.fill((added, added, added, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return result

    def apply_blur(self, surface, strength=2):
        if not self.enable_blur or strength < 1:
            return surface

        w, h = surface.get_size()
        scaled_down = pygame.transform.smoothscale(surface, (w // strength, h // strength))
        return pygame.transform.smoothscale(scaled_down, (w, h))

    def draw(self, surface, virtual_size):
        sw, sh = virtual_size

        # Backdrop sway
        sway_y = (math.sin(self.time * self.sway_speed) * self.sway_amplitude)+ self.sway_amplitude
        backdrop_img = self.backdrop_anim.get_current_frame()
        backdrop_scaled = pygame.transform.scale(backdrop_img, virtual_size)

        # Apply brightness and blur to backdrop
        adjusted = self.apply_brightness(backdrop_scaled)
        final_backdrop = self.apply_blur(adjusted)

        surface.blit(final_backdrop, (0, sway_y))

        # Overlay image (non-swaying foreground like table assets)
        overlay_img = self.overlay_anim.get_current_frame()
        overlay_scaled = pygame.transform.scale(overlay_img, virtual_size)
        surface.blit(overlay_scaled, (0, 0))

    def handle_event(self, event, virtual_mouse, switcher, screen):
        pass

def formattedScreenName():
    return "Workstation"

def default_items_func(item_manager):
    makeItem(item_manager, "furnace", (200, 300), "workstation")
    makeItem(item_manager, "anvil", (400, 300), "workstation")

def workstation(screen, instance_manager, prev_screen = None):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)
    helper = WorkstationHelper(virtual_size)
    

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="workstation",
        switcher=switcher,
        draw_bag=True,
        helper = helper,
        draw_charmboard=False,
        default_items_func=default_items_func,
        previous_screen=table,  # Reference to the previous screen function
        instance_manager= instance_manager
    )
    base.run()
