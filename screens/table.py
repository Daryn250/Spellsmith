import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.itemMaker import makeItem

def formattedScreenName():
    return "Table"

def default_items_func(item_manager):
    return # none for now :)

def table(screen, prev_screen = None):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)
    background = AnimatedTile("assets/screens/table/table1.png", frame_duration=150)

    from screens.main_menu import main_menu  # Import early to support previous_screen lambda

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="table",
        switcher=switcher,
        draw_bag=True,
        draw_charmboard=True,
        background=background,
        default_items_func=default_items_func,
        previous_screen=main_menu  # Reference to the previous screen function
    )
    base.run()
