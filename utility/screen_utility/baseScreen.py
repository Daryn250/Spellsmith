# utility/screen_utility/base_screen.py

import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.screen_utility.screenwrapper import VirtualScreen
from utility.cursor_utility.cursorManager import CursorManager
from utility.item_utility.ItemManager import ItemManager
from utility.item_utility.item_flags import * # import all item flags
from utility.gui_utility.guiManager import GUIManager

from utility.item_utility.itemMaker import makeItem
from utility.tool_utility.tool import Tool


class BaseScreen:
    def __init__(self, screen, virtual_size, screen_name, switcher, helper=None,
                draw_bag=True, draw_charmboard=False, draw_screennav = True, background=None,
                default_items_func=None, previous_screen=None,
                item_manager=None, override_draw = False,
                instance_manager = None):
        ...
        # screennav is the triangle in the corner that allows for easier screen navigation
        self.item_manager = item_manager if item_manager else ItemManager(virtual_size)

        self.screen = screen
        self.virtual_size = virtual_size
        self.vscreen = VirtualScreen(virtual_size)
        self.virtual_surface = self.vscreen.get_surface()
        self.override_draw = override_draw

        self.switcher = switcher
        self.screen_name = screen_name
        self.previous_screen = previous_screen

        self.helper = helper
        self.draw_bag = draw_bag
        self.draw_charmboard = draw_charmboard
        self.draw_screennav = draw_screennav
        self.background = background
        self.default_items_func = default_items_func  # callable function
        self.instance_manager = instance_manager if instance_manager != None else print("[BASESCREEN.py] No instance manager was passed in. very critical error prolly")

        self.cursor_manager = CursorManager(self.virtual_surface)
        self.gui_manager = GUIManager(self, charmboard=draw_charmboard)
        self.clock = pygame.time.Clock()
        

    def load_items(self, save_path):
        data = self.item_manager.load_items(save_path, self.screen_name)
        # data should be the full save dict, including helper data

        if self.draw_bag:
            self.gui_manager.bag_manager.load_bag(save_path, self.item_manager)

        if not self.item_manager.items and self.default_items_func:
            self.default_items_func(self.item_manager)

        if self.helper and data:
            screen_data = data.get(self.screen_name, {})  # extra helper data here
            if hasattr(self.helper, "restore"):
                self.helper.restore(screen_data)
                print(screen_data)
            elif hasattr(self.helper, "load_from_data"):
                self.helper.load_from_data(screen_data)
            else:
                print(f"⚠️ Helper for {self.screen_name} has no 'restore' or 'load_from_data' method.")



    def save_items(self, save_path):
        if hasattr(self.helper, "get_save_data"):
            extra = self.helper.get_save_data() if self.helper else None
        else:
            extra = None
        self.item_manager.save_items(save_path, self.screen_name, extra_screen_data=extra)

        self.gui_manager.save_bag(save_path)

    def handle_events(self, virtual_mouse):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_items(self.instance_manager.save_file)
                print("saving")
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if hasattr(self.helper, "handleEvents"):
                self.helper.handleEvents(event, virtual_mouse, self.virtual_size, self)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.cursor_manager.click()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.save_items(self.instance_manager.save_file)
                    if self.previous_screen:
                        if self.switcher.active:
                            self.switcher.force_finish()
                        else:
                            self.switcher.start(
                                next_screen_func=lambda: self.previous_screen(self.screen, self.instance_manager),
                                save_callback=lambda: self.save_items(self.instance_manager.save_file)
                            )
                    else:
                        print("⚠️ No previous screen set.")
                        pygame.quit()
                        sys.exit()

            # Combine items and bag contents for drag handling:
            combined_items = list(self.item_manager.items)
            # Add only items that are NOT already in item_manager.items to avoid duplicates
            combined_items.extend([item for item in self.gui_manager.bag_manager.contents if item not in self.item_manager.items])

            DraggableFlag.handle_event(event, combined_items, virtual_mouse, self.virtual_size, self.gui_manager, self.item_manager)

            # Adjust cursor based on dragging item temperature
            if DraggableFlag.dragging_item:
                if getattr(DraggableFlag.dragging_item, "temperature", 0) > 200:
                    self.cursor_manager.set_cursor("tongs", self.virtual_surface, "assets/cursor/tongs")
            else:
                self.cursor_manager.set_cursor("base", self.virtual_surface, "assets/cursor/defaultCursor")

            ScreenChangeFlag.handle_event(event, combined_items, virtual_mouse, self.screen, self.switcher, self.virtual_size, self)
            CharmFlag.handle_event(event, combined_items, virtual_mouse, self.virtual_size)
            TrickFlag.handle_event(event, combined_items, virtual_mouse, self.virtual_size, self.gui_manager)
            InspectableFlag.handle_event(event, combined_items, virtual_mouse, self.virtual_size, self.gui_manager)
            self.gui_manager.handleEvent(event, virtual_mouse)


    def update(self, dt, virtual_mouse):
        if self.helper:
            self.helper.update(dt, self.item_manager, virtual_mouse, self)

        self.cursor_manager.update(dt, virtual_mouse)

        for item in self.item_manager.items:
            if hasattr(item, "trick") and item.trick:
                item.trick.update(dt / 1000.0, item, self.virtual_size)
                if item.trick.finished:
                    item.trick = None
            item.update(self.virtual_surface, self.gui_manager, self.virtual_size, dt=dt)
            for p in item.particles:
                p.update()
            item.particles = [p for p in item.particles if p.is_alive()]

        self.gui_manager.update(dt / 1000, virtual_mouse, self.virtual_size)
        self.switcher.update(dt)

    def draw(self, virtual_mouse):
        self.virtual_surface.fill((0, 0, 0))
        if self.background and hasattr(self.background, "index"):
            self.background.draw(self.virtual_surface, (0, 0), scale_to=self.virtual_size)

        if self.helper and hasattr(self.helper, "draw"):
            self.helper.draw(self.virtual_surface, self.virtual_size)

        if self.override_draw == False:
            self.item_manager.draw_with_z_respect(self.virtual_surface, self.virtual_size, self.gui_manager, 5)

        dragged = next((i for i in self.item_manager.items if getattr(i, "dragging", False)), None)
        SlotFlag.draw_overlay(self.virtual_surface, self.item_manager.items, dragged, virtual_mouse, self.virtual_size)


        self.gui_manager.drawBag = self.draw_bag
        self.gui_manager.drawCharmBoard = self.draw_charmboard
        self.gui_manager.draw_screennav = self.draw_screennav
        if self.helper and hasattr(self.helper, "hide_gui") and self.helper.hide_gui:
            pass
        else:
            self.gui_manager.draw(self.virtual_surface, self.virtual_size, virtual_mouse, self.item_manager)

        if self.helper and hasattr(self.helper, "draw_after_gui"):
            self.helper.draw_after_gui(self.virtual_surface, self.virtual_size)


        self.item_manager.draw_dragged_item(self.virtual_surface, self.virtual_size, self.gui_manager, 5)
        self.cursor_manager.draw(self.virtual_surface, virtual_mouse)

        self.vscreen.draw_to_screen(self.screen)

        self.switcher.draw(self.screen)
        pygame.display.flip()


    def run(self):
        self.load_items(self.instance_manager.save_file)
        while True:
            dt = self.clock.tick(60)
            virtual_mouse = self.vscreen.get_virtual_mouse(self.screen.get_size())
            self.handle_events(virtual_mouse)
            self.update(dt, virtual_mouse)
            self.draw(virtual_mouse)
    
    def start_shake(self, duration, magnitude):
        self.vscreen.start_shake(duration, magnitude)

