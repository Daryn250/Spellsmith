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



VIRTUAL_SIZE = (960, 540)
vscreen = VirtualScreen(VIRTUAL_SIZE)
tile_size = 32
FPS = 60

def testScreen(screen):
    switcher = ScreenSwitcher()
    clock = pygame.time.Clock()
    

    virtual_surface = vscreen.get_surface()

    item_manager = ItemManager()
    cursor_manager = CursorManager(virtual_surface)
    gui_manager = GUIManager()

    
    # load sprites:
    background = AnimatedTile("assets/table/background/table", frame_duration=150)

    item_manager.load_items("saves/save1.json", "testing")

    makeItem(item_manager, "iron_ingot", (200,200), "testing")


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

        # draw tiles
        #update
        background.update(dt)
        cursor_manager.update(dt, virtual_mouse)
        for item in item_manager.items:
            item.update(virtual_surface, gui_manager, VIRTUAL_SIZE, dt)
    

        

        # save
        item_manager.save_items("saves/save1.json")

        #clear screen and draw
        virtual_surface.fill((0,0,0))

        # draw background and lights
        background.draw(virtual_surface, (0, 0), scale_to = VIRTUAL_SIZE)

        # draw items
        for item in item_manager.items:
            item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, item_manager)

        # draw guis
        gui_manager.draw(virtual_surface, VIRTUAL_SIZE)

        # draw screenswitcher
        switcher.update_and_draw(screen)

        # draw cursor
        cursor_manager.draw(virtual_surface, virtual_mouse)

        vscreen.draw_to_screen(screen)
        
        pygame.display.flip()