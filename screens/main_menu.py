import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.cursor_utility.cursorManager import CursorManager
from utility.cursor_utility.cursor import HammerCursor
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.button import Button

from screens.table import table  # next screen

def formattedScreenName():
    return "Main Menu"

class MainMenuHelper:
    def __init__(self, screen_size):
        self.bg_tile = AnimatedTile("assets/ocean", frame_duration=150)
        self.boat_sprite = AnimatedTile("assets/boat", frame_duration=100)
        self.tile_size = 32
        self.buttons = []
        self.screen_size = screen_size
        self._init_buttons()

    def _init_buttons(self):
        sw, sh = self.screen_size
        center_x = sw // 20 + 50
        self.buttons = [
            Button(None, (center_x, sh * 2 // 5), "play", pygame.font.Font(None, 32), "White", "gray"),
            Button(None, (center_x, sh // 2), "settings", pygame.font.Font(None, 32), "White", "gray"),
            Button(None, (center_x, int(sh * 0.9)), "quit", pygame.font.Font(None, 32), "White", "indianred1")
        ]

    def update(self, dt, item_manager):
        self.bg_tile.update(dt)
        self.boat_sprite.update(dt)

    def draw(self, surface, virtual_size):
        sw, sh = virtual_size
        for y in range(0, sh, self.tile_size):
            for x in range(0, sw, self.tile_size):
                self.bg_tile.draw(surface, (x, y))

        boat_img = self.boat_sprite.get_current_frame()
        boat_rect = boat_img.get_rect(center=(sw // 2, sh // 2))
        self.boat_sprite.draw(surface, boat_rect)

        menu_surface = pygame.Surface((sw, sh), pygame.SRCALPHA)
        menu_bar = pygame.draw.rect(menu_surface, (0, 0, 0, 128), (sw // 20, 0, 100, sh))
        surface.blit(menu_surface, (0, 0))

        for btn in self.buttons:
            btn.update(surface)

    def handle_event(self, event, virtual_mouse, switcher, screen):
        for btn in self.buttons:
            btn.changeColor(virtual_mouse)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.buttons[0].checkForInput(virtual_mouse):  # Play
                switcher.start(lambda: table(screen))
            elif self.buttons[1].checkForInput(virtual_mouse):  # Settings
                pass  # placeholder
            elif self.buttons[2].checkForInput(virtual_mouse):  # Quit
                pygame.quit()
                sys.exit()


def main_menu(screen):
    switcher = ScreenSwitcher()
    virtual_size = (480, 270)
    helper = MainMenuHelper(virtual_size)

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
        item_manager=None
    )

    base.cursor_manager.set_cursor("hammer", base.virtual_surface, "assets/cursor/hammerCursor")

    # override base's handle_events to include helper event handling
    def handle_events_with_buttons(virtual_mouse):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                base.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            helper.handle_event(event, virtual_mouse, base.switcher, screen)
            base.cursor_manager.click() if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 else None

    base.handle_events = handle_events_with_buttons
    base.run()
