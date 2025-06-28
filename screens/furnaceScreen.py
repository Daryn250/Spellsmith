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

from utility.screen_utility.furnace_function import FurnaceHelper
VIRTUAL_SIZE = (480*2, 270*2)
vscreen = VirtualScreen(VIRTUAL_SIZE)
FPS = 60

def furnaceScreen(screen):
    switcher = ScreenSwitcher()
    clock = pygame.time.Clock()
    

    virtual_surface = vscreen.get_surface()

    item_manager = ItemManager(VIRTUAL_SIZE)
    cursor_manager = CursorManager(virtual_surface)
    gui_manager = GUIManager(charmboard = False)

    
    # load sprites:
    # Load furnace helper
    furnace = FurnaceHelper(item_manager)

    # Attempt to load items and metadata for the screen
    furnace_data = item_manager.load_items("saves/save1.json", "furnaceScreen")

    # If loading failed, manually create slots
    if furnace_data is False:
        named_slots = [
            ("furnace_input_1", (32, 23)),
            ("furnace_input_2", (56, 23)),
            ("furnace_input_3", (80, 23)),
            ("furnace_input_4", (104, 23)),
            ("furnace_input_5", (128, 23)),
            ("fuel_input", (80, 75)),
            ("weapon_slot1", (42, 45)),
            ("weapon_slot2", (120, 45)),
        ]
        for name, pos in named_slots:
            scaled = (pos[0] * (VIRTUAL_SIZE[0] / 160), pos[1] * (VIRTUAL_SIZE[1] / 90))
            slot_item = makeItem(item_manager, "slot_node", scaled, "furnaceScreen", extra_nbt={"slot_name": name}).item

    # Restore furnace state if metadata is available
    elif furnace_data:
        furnace.fuel_level = furnace_data.get("fuel_level", 1.0)
    makeItem(item_manager, "iron_ore", (200,200), "furnaceScreen")
    Tool(item_manager, "sword", (300, 200), {
        "blade":"copper",
        "guard":"titanium",
        "pommel":"lomium",
        "handle":"blue",
        "origin_screen":"furnaceScreen"
    })
    


    # run table
    while True:
        dt = clock.tick(FPS)
        virtual_mouse = vscreen.get_virtual_mouse(screen.get_size())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                item_manager.save_items("saves/save1.json", extra_screen_data=furnace.get_save_data())
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    cursor_manager.click()
                    # Check for input on buttons here:
            # exit screen and go back
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from screens.workstation import workstation
                    item_manager.save_items("saves/save1.json", extra_screen_data=furnace.get_save_data())
                    switcher.start(lambda: workstation(screen))

            DraggableFlag.handle_event(event, item_manager.items, virtual_mouse, VIRTUAL_SIZE, gui_manager, item_manager) # rio de janero handle draggable items
            if DraggableFlag.dragging_item != None:
                if getattr(DraggableFlag.dragging_item, "temperature", 0) > 200:
                    cursor_manager.set_cursor("tongs", virtual_surface, "assets/cursor/tongs")
            else:
                cursor_manager.set_cursor("base", virtual_surface, "assets/cursor/defaultCursor")
            ScreenChangeFlag.handle_event(event, item_manager.items, virtual_mouse, screen, switcher, VIRTUAL_SIZE) # rio de janero 2 handle screen change boogaloo
            CharmFlag.handle_event(event, item_manager.items, virtual_mouse, VIRTUAL_SIZE)
            TrickFlag.handle_event(event, item_manager.items, virtual_mouse, VIRTUAL_SIZE, gui_manager)
            gui_manager.handleEvent(event, virtual_mouse)
        # draw tiles
        #update
        furnace.update(dt, item_manager)
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

        

            
        gui_manager.update(dt/1000, virtual_mouse, VIRTUAL_SIZE)

        

        # save
        


        #clear screen and draw
        virtual_surface.fill((0,0,0))

        # draw background and lights
        furnace.draw(virtual_surface, VIRTUAL_SIZE)

        # draw items
        for item in item_manager.items:
            item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, item_manager, 10)

            for p in item.particles:
                p.draw(virtual_surface)


        # draw slot if available
        dragged = next((i for i in item_manager.items if getattr(i, "dragging", False)), None)
        SlotFlag.draw_overlay(virtual_surface, item_manager.items, dragged, virtual_mouse, VIRTUAL_SIZE)


        # draw guis
        gui_manager.draw(virtual_surface, VIRTUAL_SIZE, virtual_mouse)

        # draw screenswitcher
        
        # draw cursor
        cursor_manager.draw(virtual_surface, virtual_mouse)

        vscreen.draw_to_screen(screen)
        switcher.update_and_draw(screen, item_manager, dt)

        
        pygame.display.flip()