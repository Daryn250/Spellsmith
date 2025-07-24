import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.cursor_utility.cursorManager import CursorManager
from utility.cursor_utility.cursor import HammerCursor
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.screen_utility.settingsHelper import SettingsHelper
from utility.button import Button
import math
import random

from screens.table import table  # next screen

def formattedScreenName():
    return "Main Menu"

class MainMenuHelper:
    def __init__(self, screen_size, instance_manager):
        self.tile_size = 32
        self.screen_size = screen_size
        self.tiles = []  # Each tile: {"tile": AnimatedTile, "duration": int, "offset": float, "phase": float}
        self.instance_manager = instance_manager
        self.language = instance_manager.settings.language
        self.settings = instance_manager.settings
        self.font = instance_manager.settings.font
        self.settings_helper = SettingsHelper(screen_size, self.settings, self)
        self._init_ocean_tiles()
        self._init_buttons()
        self.time_elapsed = 0
        

        # Boat animation
        self.boat_sprite = AnimatedTile("assets/boat", frame_duration=150)  # Replace with actual path if different

    def _init_ocean_tiles(self):
        sw, sh = self.screen_size
        cols = sw // self.tile_size + 1
        rows = sh // self.tile_size + 1

        for y in range(rows):
            row = []
            for x in range(cols):
                duration = random.randint(1000, 1500)  # Variable frame durations
                anim = AnimatedTile("assets/ocean", frame_duration=duration)
                anim.current_time = random.randint(0, duration)  # Offset animation start
                row.append({
                    "tile": anim,
                    "phase": random.uniform(0, 2 * math.pi),
                })
            self.tiles.append(row)

    def _init_buttons(self, newfont = None):
        sw, sh = self.screen_size
        center_x = sw // 20 + 50
        font = pygame.font.Font(self.font if newfont==None else newfont, 20)
        self.buttons = [
            Button(None, (center_x, sh * 2 // 5), self.settings.translated_text("play"), font, "White", "gray"),
            Button(None, (center_x, sh // 2), self.settings.translated_text("settings"), font, "White", "gray"),
            Button(None, (center_x, int(sh * 0.9)), self.settings.translated_text("quit"), font, "White", "indianred1")
        ]
        # Calculate menu bar width based on longest button text
        self.menu_bar_font = font
        self.menu_bar_width = max(font.size(btn.text_input)[0] for btn in self.buttons) + 40  # 40px padding


    def update(self, dt, item_manager, mouse, screen):
        self.time_elapsed += dt / 1000
        for row in self.tiles:
            for cell in row:
                cell["tile"].update(dt)
        self.boat_sprite.update(dt)

    def draw(self, surface, virtual_size):
        background = pygame.Surface(virtual_size, pygame.SRCALPHA)
        pygame.draw.rect(background, (6,45,83), (0,0,virtual_size[0], virtual_size[1]))
        surface.blit(background, (0,0))
        sw, sh = virtual_size
        wave_amplitude = 3
        wave_speed = 2

        frequency = 0.4  # smaller = longer wavelength
        wave_amplitude = 3
        wave_speed = 2

        for y, row in enumerate(self.tiles):
            for x, cell in enumerate(row):
                tile = cell["tile"]
                px = x * self.tile_size
                position_offset = px + y * self.tile_size  # diagonal phase shift
                wave = math.sin(position_offset * frequency + self.time_elapsed * wave_speed)
                py = y * self.tile_size + wave * wave_amplitude

                tile.draw(surface, (px, py))


        # Boat drawing
        boat_img = self.boat_sprite.get_current_frame()
        boat_rect = boat_img.get_rect(center=(sw // 2, sh // 2))
        self.boat_sprite.draw(surface, boat_rect)

        # Menu bar
        menu_surface = pygame.Surface((self.menu_bar_width, sh), pygame.SRCALPHA)
        pygame.draw.rect(menu_surface, (0, 0, 0, 128), (0, 0, self.menu_bar_width, sh))
        surface.blit(menu_surface, (sw // 20, 0))

        # Buttons (center text in menu bar)
        for btn in self.buttons:
            # Center the text in the menu bar
            font = btn.font
            text = btn.text_input
            text_surf = font.render(text, False, btn.base_color)
            text_rect = text_surf.get_rect()
            # Center horizontally in menu bar
            text_rect.centerx = sw // 20 + self.menu_bar_width // 2
            # Keep the y position as before
            text_rect.centery = btn.y_pos
            surface.blit(text_surf, text_rect)
            # Update button hitbox to match centered text
            btn.rect = text_rect.copy()
            # Optionally, draw button background/hover effect if needed
        self.settings_helper.draw(surface)

    def handle_event(self, event, virtual_mouse, switcher, screen):
        if self.settings_helper.active:
            self.settings_helper.handle_event(event, virtual_mouse)
            return  # prevent menu input while settings open

        for btn in self.buttons:
            btn.changeColor(virtual_mouse)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons[0].checkForInput(virtual_mouse):  # Play
                switcher.start(lambda: table(screen, self.instance_manager), None)
            elif self.buttons[1].checkForInput(virtual_mouse):  # Settings
                self.settings_helper.toggle()
            elif self.buttons[2].checkForInput(virtual_mouse):  # Quit
                pygame.quit()
                sys.exit()




def main_menu(screen, instance_manager):
    switcher = ScreenSwitcher()
    virtual_size = (480, 270)
    helper = MainMenuHelper(virtual_size, instance_manager)

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="main_menu",
        switcher=switcher,
        draw_bag=False,
        draw_charmboard=False,
        background=None,
        default_items_func=None,
        previous_screen=None,
        helper=helper,
        item_manager=None,
        draw_screennav=False,
        instance_manager = instance_manager
    )


    # override base's handle_events to include helper event handling
    def handle_events_with_buttons(virtual_mouse):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                base.save_items(instance_manager.save_file)
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                base.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            helper.handle_event(event, virtual_mouse, base.switcher, screen)
            base.cursor_manager.click() if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 else None

    base.handle_events = handle_events_with_buttons
    base.run()
