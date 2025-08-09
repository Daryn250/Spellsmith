import pygame
import sys
import math
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.itemMaker import *
from utility.screen_utility.IslandHelper import IslandHelper



def formattedScreenName():
    return "Island"

def default_items_func(item_manager):
    pass

def island(screen, instance_manager, prev_screen = None):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)
    helper = IslandHelper("assets/screens/island/island1.png", virtual_size)

    from screens.mapScreen import mapScreen  # Import early to support previous_screen lambda

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="island",
        switcher=switcher,
        draw_bag=True,
        draw_charmboard=True,
        helper=helper,
        default_items_func=default_items_func,
        previous_screen=mapScreen,  # Reference to the previous screen function
        instance_manager = instance_manager
    )
    helper.base_screen = base

    base.run()
