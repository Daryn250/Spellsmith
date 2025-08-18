import pygame
import sys
import math
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.itemMaker import *
from utility.screen_utility.cauldronHelper import *
from utility.item_utility.ItemManager import ItemManager
from utility.gui_utility.GUIManager import GUIManager

def formattedScreenName():
    return "Cauldron"

def default_items_func(item_manager):
    pass

def cauldronScreen(screen, instance_manager, prev_screen = None):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)

    item_manager = ItemManager(virtual_size)
    

    from screens.workstation import workstation  # Import early to support previous_screen lambda

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="cauldronScreen",
        switcher=switcher,
        draw_bag=True,
        item_manager=item_manager,
        draw_charmboard=True,
        default_items_func=default_items_func,
        previous_screen=workstation,  # Reference to the previous screen function
        instance_manager = instance_manager
    )
    base.helper = cauldronHelper(item_manager, instance_manager, base.gui_manager)

    base.run()
