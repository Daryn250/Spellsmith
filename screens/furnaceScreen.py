from utility.screen_utility.baseScreen import BaseScreen
from utility.screen_utility.furnace_function import FurnaceHelper
from utility.item_utility.itemMaker import makeItem
from screens.workstation import workstation

def formattedScreenName():
    return "Furnace"

def furnace_default_items(manager):
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
        scaled = (pos[0] * (960 / 160), pos[1] * (540 / 90))
        makeItem(manager, "slot_node", scaled, "furnaceScreen", extra_nbt={"slot_name": name})

def furnaceScreen(screen, instance_manager, previous_screen=None):
    from utility.screen_utility.screenswitcher import ScreenSwitcher
    from utility.item_utility.ItemManager import ItemManager
    switcher = ScreenSwitcher()

    item_manager = ItemManager((960, 540))  # 🔧 shared instance
    helper = FurnaceHelper(item_manager)

    screen_instance = BaseScreen(
        screen=screen,
        virtual_size=(960, 540),
        screen_name="furnaceScreen",
        switcher=switcher,
        helper=helper,
        draw_bag=True,
        background=helper,
        item_manager=item_manager,
        default_items_func=furnace_default_items,
        previous_screen=workstation,
        instance_manager=instance_manager
    )

    # Inject the shared item manager
    screen_instance.run()

