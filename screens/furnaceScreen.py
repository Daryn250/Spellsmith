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

VIRTUAL_SIZE = (960*2, 540*2)
vscreen = VirtualScreen(VIRTUAL_SIZE)
FPS = 60

def furnaceScreen(screen):
    switcher = ScreenSwitcher()
    clock = pygame.time.Clock()
    

    virtual_surface = vscreen.get_surface()

    item_manager = ItemManager()
    cursor_manager = CursorManager(virtual_surface)
    gui_manager = GUIManager()

    
    # load sprites:
    background = AnimatedTile("assets/screens/workstation/workstation.png", frame_duration=150)

    item_manager.load_items("saves/save1.json", "furnaceScreen")


    # run table
    while True:
        dt = clock.tick(FPS)
        virtual_mouse = vscreen.get_virtual_mouse(screen.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    cursor_manager.click()
                    # Check for input on buttons here:
            DraggableFlag.handle_event(event, item_manager.items, virtual_mouse, VIRTUAL_SIZE, gui_manager, item_manager) # rio de janero handle draggable items
            ScreenChangeFlag.handle_event(event, item_manager.items, virtual_mouse, screen, switcher, VIRTUAL_SIZE) # rio de janero 2 handle screen change boogaloo
            CharmFlag.handle_event(event, item_manager.items, virtual_mouse, VIRTUAL_SIZE)
            TrickFlag.handle_event(event, item_manager.items, virtual_mouse, VIRTUAL_SIZE, gui_manager)
        # draw tiles
        #update
        background.update(dt)
        cursor_manager.update(dt, virtual_mouse)
        for item in item_manager.items:
            if hasattr(item, "trick") and item.trick:
                item.trick.update(dt / 1000.0, item, VIRTUAL_SIZE)
                if item.trick.finished:
                    item.trick = None
            item.update(virtual_surface, gui_manager, VIRTUAL_SIZE, dt)

            for p in item.particles:
                p.update()
            item.particles = [p for p in item.particles if p.is_alive()]

        

            
        gui_manager.update(dt/1000, virtual_mouse)

        

        # save
        item_manager.save_items("saves/save1.json")

        #clear screen and draw
        virtual_surface.fill((0,0,0))

        # draw background and lights
        background.draw(virtual_surface, (0, 0), scale_to = VIRTUAL_SIZE)

        # draw items
        for item in item_manager.items:
            item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, item_manager, 10)

            for p in item.particles:
                p.draw(virtual_surface)


        # draw slot if available
        dragged = next((i for i in item_manager.items if getattr(i, "dragging", False)), None)
        SlotFlag.draw_overlay(virtual_surface, item_manager.items, dragged, virtual_mouse, VIRTUAL_SIZE)


        # draw guis
        gui_manager.draw(virtual_surface, VIRTUAL_SIZE)

        # draw screenswitcher
        
        # draw cursor
        cursor_manager.draw(virtual_surface, virtual_mouse)

        vscreen.draw_to_screen(screen)
        switcher.update_and_draw(screen, item_manager)

        
        pygame.display.flip()