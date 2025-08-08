# utility/screen_utility/base_screen.py

import pygame
import sys
import moderngl
import numpy as np
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.screen_utility.screenwrapper import VirtualScreen
from utility.cursor_utility.cursorManager import CursorManager
from utility.item_utility.ItemManager import ItemManager
from utility.item_utility.item_flags import * # import all item flags
from utility.gui_utility.GUIManager import GUIManager
from utility.item_utility.itemMaker import makeItem
from utility.gui_utility.console import DebugConsole  # <-- Add this import


class BaseScreen:
    def __init__(self, screen, virtual_size, screen_name, switcher, helper=None,
                draw_bag=True, draw_charmboard=False, draw_screennav = True, background=None,
                default_items_func=None, previous_screen=None,
                item_manager=None, override_draw = False,
                instance_manager = None, day_ambience = [], night_ambience = []):
        ...
        # screennav is the triangle in the corner that allows for easier screen navigation
        self.item_manager = item_manager if item_manager else ItemManager(virtual_size)

        self.screen = screen
        self.virtual_size = virtual_size
        self.vscreen = VirtualScreen(virtual_size)
        self.virtual_surface = self.vscreen.get_surface()
        self.override_draw = override_draw

        self.switcher = switcher
        # play the screen switch in sound
        instance_manager.sfx_manager.play_sound("gui_swooshout")

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
        self.debug_console = DebugConsole(self)  # <-- Initialize DebugConsole

        self.ctx = instance_manager.ctx
        self.instance_manager = instance_manager

        # Reuse the one shared quad VBO
        

        # Ask your ShaderManager for the cached VAO for this VBO + shader program:


        if instance_manager.is_daytime():
            for pth in day_ambience:
                self.instance_manager.sfx_manager.play_ambience(pth)
        else:
            pass


    


    def load_items(self, save_path):
        # check if save is empty, if is then set it to have {}
        import os
        if not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write('{}')
        
        screen_helper_data = self.item_manager.load_items(save_path, self.screen_name)
        # screen_helper_data is the _screen_data dict for this screen (or {})

        if self.draw_bag:
            self.gui_manager.bag_manager.load_bag(save_path, self.item_manager)

        if not self.item_manager.items and self.default_items_func:
            self.default_items_func(self.item_manager)

        if self.helper and screen_helper_data is not None:
            if hasattr(self.helper, "restore"):
                self.helper.restore(screen_helper_data)
            elif hasattr(self.helper, "load_from_data"):
                self.helper.load_from_data(screen_helper_data)
            else:
                return
                print(f"⚠️ Helper for {self.screen_name} has no 'restore' or 'load_from_data' method.") # make unreachable to ignore the FREAKIN warning



    def save_items(self, save_path):
        if hasattr(self.helper, "get_save_data"):
            extra = self.helper.get_save_data() if self.helper else None
        else:
            extra = None
        self.item_manager.save_items(save_path, self.screen_name, extra_screen_data=extra)

        self.gui_manager.save_bag(save_path)

    def handle_events(self, virtual_mouse):
        for event in pygame.event.get():
            if self.debug_console.active:
                self.debug_console.handle_event(event)
                # Allow closing with close button or ESC, but block other game input if console is open
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    continue
                if event.type == pygame.MOUSEBUTTONDOWN:
                    continue
            if event.type == pygame.QUIT:
                self.save_items(self.instance_manager.save_file)
                print("saving")
                pygame.quit()
                sys.exit()

            
                



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
                                save_callback=lambda: self.save_items(self.instance_manager.save_file),
                                sfx_manager = self.instance_manager.sfx_manager
                            )
                    else:
                        print("⚠️ No previous screen set.")
                        pygame.quit()
                        sys.exit()
                # Toggle debug console with '/'
                if event.key == pygame.K_SLASH:
                    self.debug_console.toggle()

            # Combine items and bag contents for drag handling:
            combined_items = list(self.item_manager.items)
            
            # Add only items that are NOT already in item_manager.items to avoid duplicates
            combined_items.extend([item for item in self.gui_manager.bag_manager.contents if item not in self.item_manager.items])
            if hasattr(self.helper, "items"):
                combined_items.extend([item for item in self.helper.items if item not in self.item_manager.items])
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
            InspectableFlag.handle_event(event, combined_items, virtual_mouse, self.virtual_size, self.gui_manager, self.item_manager, self.instance_manager.settings)
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
            item.update(self.virtual_surface, self.gui_manager, self.virtual_size, self.instance_manager.sfx_manager, dt=dt)
            for p in item.particles:
                p.update()
            item.particles = [p for p in item.particles if p.is_alive()]
        
        self.debug_console.update(dt)

        self.gui_manager.update(dt / 1000, virtual_mouse, self.virtual_size)
        self.switcher.update(dt)

    def draw(self, virtual_mouse):
        self.virtual_surface.fill((0, 0, 0))

        if self.background and hasattr(self.background, "index"):
            self.background.draw(self.virtual_surface, (0, 0), scale_to=self.virtual_size)

        if self.helper and hasattr(self.helper, "draw"):
            self.helper.draw(self.virtual_surface, self.virtual_size)

        if not self.override_draw:
            self.item_manager.draw_with_z_respect(self.virtual_surface, self.virtual_size, self.gui_manager, 5)

        dragged = next((i for i in self.item_manager.items if getattr(i, "dragging", False)), None)
        SlotFlag.draw_overlay(self.virtual_surface, self.item_manager.items, dragged, virtual_mouse, self.virtual_size)

        self.gui_manager.drawBag = self.draw_bag
        self.gui_manager.drawCharmBoard = self.draw_charmboard
        self.gui_manager.draw_screennav = self.draw_screennav
        if not (self.helper and hasattr(self.helper, "hide_gui") and self.helper.hide_gui):
            self.gui_manager.draw(self.virtual_surface, self.virtual_size, virtual_mouse, self.item_manager)

        if self.helper and hasattr(self.helper, "draw_after_gui"):
            self.helper.draw_after_gui(self.virtual_surface, self.virtual_size)

        self.item_manager.draw_dragged_item(self.virtual_surface, self.virtual_size, self.gui_manager, 5)

        self.debug_console.draw(self.virtual_surface)
        self.cursor_manager.draw(self.virtual_surface, virtual_mouse)


        
        # call post processing here when needed
        


        self.vscreen.draw_to_screen(self.screen, source_surface=self.virtual_surface)

        self.switcher.draw(self.screen)
        pygame.display.flip()




    def run(self):
        self.load_items(self.instance_manager.save_file)
        while True:
            dt = self.clock.tick(60)
            # Print FPS to the same line
            print(f"FPS: {self.clock.get_fps():.1f}", end="\r", flush=True)
            virtual_mouse = self.vscreen.get_virtual_mouse(self.screen.get_size())
            self.handle_events(virtual_mouse)
            self.update(dt, virtual_mouse)
            self.draw(virtual_mouse)
    
    def start_shake(self, duration, magnitude):
        self.vscreen.start_shake(duration, magnitude)

