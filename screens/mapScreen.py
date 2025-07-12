from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.ItemManager import ItemManager
from utility.screen_utility.baseScreen import BaseScreen
from utility.item_utility.itemMaker import makeItem

class MapHelper:
    def __init__(self, size, item_manager):
        self.map_border = "assets/screens/map/map_border.png"
        self.zoom = 0 # consider saving? dunno
        self.pan = (0,0) # top left for now
        self.discovered = {} # list of discovered areas to draw.
        self.all = {
             "island1": lambda: makeItem(item_manager, "island1", (200,200), "map")
        }
        self.margin_width = [6 * (size[0]/180), 6*(size[1]/90)]
    
    def handle_events(self, event, virtual_mouse, virtual_size, base_screen):
        pass
    
    def update(self, dt, item_manager, mouse, screen):
        pass
    def draw(self, screen, size):

        pass

    def get_save_data(self):
            return {"map": {
            "zoom": self.zoom,
            "pan": self.pan,
            "discovered": self.discovered
            }
        }
    
    def load_from_data(self, data):
        self.fuel_level = data.get("fuel_level", 1.0)

def mapScreen(screen):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)
    
    item_manager=ItemManager(virtual_size)
    helper=MapHelper(virtual_size, item_manager)

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="map",
        switcher=switcher,
        draw_bag=False,
        draw_charmboard=False,
        background=None,
        default_items_func=None,
        previous_screen=None,
        helper = helper,
        item_manager= item_manager
    )

    base.run()