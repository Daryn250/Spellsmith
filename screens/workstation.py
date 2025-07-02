import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.itemMaker import makeItem
from screens.table import table  # Import early to support previous_screen lambda

def formattedScreenName():
    return "Workstation"

def default_items_func(item_manager):
    makeItem(item_manager, "furnace", (200, 300), "workstation")
    makeItem(item_manager, "anvil", (400, 300), "workstation")

def workstation(screen, prev_screen = None):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)
    background = AnimatedTile("assets/screens/workstation/workstation.png", frame_duration=150)

    

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="workstation",
        switcher=switcher,
        draw_bag=True,
        draw_charmboard=False,
        background=background,
        default_items_func=default_items_func,
        previous_screen=table  # Reference to the previous screen function
    )
    base.run()
