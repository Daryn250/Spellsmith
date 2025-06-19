# simplifies screen creation !
import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.screen_utility.screenwrapper import VirtualScreen
from utility.cursor_utility.cursorManager import CursorManager
from utility.item_utility.ItemManager import ItemManager
from utility.item_utility.item_flags import * # import all item flags
from utility.gui_utility.guiManager import GUIManager
from utility.screen_utility.screenManager import *

class screenSimplifier:
    def __init__(self, resolution, fps, name, background_info: tuple):
        '''
        resolution: (width, height) tuple for virtual screen
        fps: target framerate
        name: screen name (must exist in screenManager)
        background_info: (sprite_folder_path, frame_duration)
        '''
        pygame.init()
        self.virtual_size = resolution
        self.fps = fps
        self.name = name

        if name not in get_all_screen_functions():
            raise KeyError(f"Screen name '{name}' not in screenManager.py")

        self.screen = pygame.display.set_mode(resolution, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.vscreen = VirtualScreen(resolution)
        self.virtual_surface = self.vscreen.get_surface()

        self.item_manager = ItemManager()
        self.cursor_manager = CursorManager(self.virtual_surface)
        self.gui_manager = GUIManager()
        self.switcher = ScreenSwitcher()

        bg_path, frame_duration = background_info
        self.background = AnimatedTile(bg_path, frame_duration)

        self.item_manager.load_items("saves/save1.json", self.name)

    def run(self):
        while True:
            dt = self.clock.tick(self.fps)
            virtual_mouse = self.vscreen.get_virtual_mouse(self.screen.get_size())

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.cursor_manager.click()

                DraggableFlag.handle_event(event, self.item_manager.items, virtual_mouse, self.virtual_size, self.gui_manager, self.item_manager)
                ScreenChangeFlag.handle_event(event, self.item_manager.items, virtual_mouse, self.screen, self.switcher, self.virtual_size)
                CharmFlag.handle_event(event, self.item_manager.items, virtual_mouse, self.virtual_size)

            # Update
            self.background.update(dt)
            self.cursor_manager.update(dt, virtual_mouse)
            for item in self.item_manager.items:
                item.update(self.virtual_surface, self.gui_manager, self.virtual_size, dt)

            # Save items
            self.item_manager.save_items("saves/save1.json")

            # Draw
            self.virtual_surface.fill((0, 0, 0))
            self.background.draw(self.virtual_surface, (0, 0), scale_to=self.virtual_size)

            for item in self.item_manager.items:
                item.draw(self.virtual_surface, self.virtual_size, self.gui_manager, self.item_manager)

            self.gui_manager.draw(self.virtual_surface, self.virtual_size)
            self.switcher.update_and_draw(self.screen)
            self.cursor_manager.draw(self.virtual_surface, virtual_mouse)

            self.vscreen.draw_to_screen(self.screen)
            pygame.display.flip()
