import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screenswitcher import ScreenSwitcher
from utility.screenwrapper import VirtualScreen
from utility.cursor import Cursor
from utility.item import defaultItem
from utility.ItemManager import ItemManager
from utility.item_flags import DraggableFlag # allow items to be dragged


VIRTUAL_SIZE = (480, 270)
vscreen = VirtualScreen(VIRTUAL_SIZE)
cursor = Cursor(vscreen, "assets/cursor")
tile_size = 32
FPS = 60


# make utility or something for switching ores between screens? maybe just use an inventory or something. Unsure bc I want to have ores with different types of imperfections

def table(screen):
    switcher = ScreenSwitcher()
    clock = pygame.time.Clock()

    virtual_surface = vscreen.get_surface()
    screenWidth, screenHeight = VIRTUAL_SIZE

    item_manager = ItemManager()

    # load sprites:
    background = AnimatedTile("assets/table/background/table", frame_duration=150)
    background_lights = AnimatedTile("assets/table/background/lighting", frame_duration=150)

    #test_item = defaultItem(None, (240,90), flags=["save", "draggable"])
    #item_manager.add_item(test_item)

    item_manager.load_items("saves/save1.json")



    # run table
    while True:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    cursor.click()
                    # Check for input on buttons here:
            DraggableFlag.handle_event(event, item_manager.items, vscreen.get_virtual_mouse(screen.get_size())) # rio de janero handle draggable items
                    

        # draw tiles
        #update
        background.update(dt)
        background_lights.update(dt)
        cursor.update(dt)
        for item in item_manager.items:
            item.update(dt)

        

        # save
        item_manager.save_items("saves/save1.json")

        #clear screen and draw
        virtual_surface.fill((0,0,0))

        # draw background and lights
        background.draw(virtual_surface, (0, 0), scale_to = VIRTUAL_SIZE)

        # draw items
        for item in item_manager.items:
            item.draw(virtual_surface)

        background_lights.draw(virtual_surface, (0, 0), scale_to=VIRTUAL_SIZE, blend=pygame.BLEND_ADD)

        

        cursor.draw(virtual_surface)

        vscreen.draw_to_screen(screen)
        switcher.update_and_draw(screen)
        pygame.display.flip()