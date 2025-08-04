from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.anvilHelper import AnvilHelper
from utility.item_utility.itemMaker import makeItem
from screens.workstation import workstation

def formattedScreenName():
    return "Anvil"

def anvilDefaultItems(manager):
    named_slots = [
        ("anvil_input_1", (66, 17))
    ]
    for name, pos in named_slots:
        scaled = (pos[0] * (960 / 160), pos[1] * (540 / 90))
        makeItem(manager, "slot_node", scaled, "anvilScreen", extra_nbt={"slot_name": name})

def anvilScreen(screen, instance_manager, previous_screen=None):
    from utility.screen_utility.screenswitcher import ScreenSwitcher
    from utility.item_utility.ItemManager import ItemManager
    switcher = ScreenSwitcher()

    item_manager = ItemManager((960, 540))  # 🔧 shared instance
    helper = AnvilHelper(item_manager)

    

    screen_instance = BaseScreen(
        screen=screen,
        virtual_size=(960, 540),
        screen_name="anvilScreen",
        switcher=switcher,
        helper=helper,
        draw_bag=True,
        background=helper,
        item_manager=item_manager,
        default_items_func=anvilDefaultItems,
        previous_screen=workstation,
        instance_manager=instance_manager,
    )
    helper.base_screen = screen_instance
    
    screen_instance.run()

