from .item import defaultItem
from utility.screen_utility.screenManager import get_screen_function

ITEM_BASES = {
    #### UTILITY ####
    "slot_node": {
        "type": "slot",
        "nbt": {
            "flags": ["slot", "invisible"],
            "slot_accepts": [],  # allowed item names
            "img_path": "assets/very_important/cat.png",  # optional fallback
            "animated": False,
            "contains": None
        }
    },
    "furnace": {
        "type": "furnace",
        "nbt": {
            "flags": ["draggable", "screen_change", "no_shadow", "unbaggable"],
            "img_path": "assets/screens/workstation/furnace.png",  # optional fallback
            "animated": False,
            "next_screen":"furnaceScreen",
            "scale":(2,2)
        }
    },
    "anvil": {
        "type": "anvil",
        "nbt": {
            "flags": ["draggable", "screen_change", "no_shadow", "unbaggable"],
            "img_path": "assets/screens/workstation/anvil.png",  # optional fallback
            "animated": False,
            "next_screen":"anvilScreen",
            "scale":(2,2)
        }
    },
    #### CHARMS ####
    "rain_charm": {
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/rain_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable"],
            "charmType": "rain_charm",
        }
    },
    "moon_charm": {
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/moon_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable"],
            "charmType": "moon_charm",
        }
    },
    "mana_charm": {
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/mana_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable"],
            "charmType": "mana_charm",
        }
    },
    #### MATERIALS ####
    "copper_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/copper/copper1.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "copper_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/copper/copper2.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "iron_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/iron/iron1.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "iron_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/iron/iron2.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "lead_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/lead/lead1.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "lead_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/lead/lead2.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "lomium_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/lomium/lomium1.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "lomium_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/lomium/lomium2.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "silver_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/silver/silver1.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "silver_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/silver/silver2.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "titanium_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/titanium/titanium1.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "titanium_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/titanium/titanium2.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    "anodized_titanium_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/titanium/titanium3.png",
            "flags": ["draggable"],
            "temperature":0
        }
    },
    ### FUEL TYPES ###
    "large_coal": {
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/large_coal.png",
            "flags": ["draggable"],
            "fuel":0.4
        }
    },
    "medium_coal": {
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/med_coal.png",
            "flags": ["draggable"],
            "fuel":0.3
        }
    },
    "small_coal": {
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/small_coal.png",
            "flags": ["draggable"],
            "fuel":0.2
        }
    },
    "log": {
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/log.png",
            "flags": ["draggable"],
            "fuel":0.05
        }
    },
}

class makeItem:
    def __init__(self, item_manager, itemType: str, pos, screen: str, extra_nbt=None):
        if itemType not in ITEM_BASES:
            raise ValueError(f"Unknown itemType: {itemType}")

        base = ITEM_BASES[itemType]
        nbt = base["nbt"].copy()
        if extra_nbt:
            nbt.update(extra_nbt)

        # Inject origin screen
        nbt["origin_screen"] = screen

        # If there's a next_screen key, resolve it to an actual screen function
        if "next_screen" in nbt and isinstance(nbt["next_screen"], str):
            screen_name = nbt["next_screen"]
            screen_func = get_screen_function(screen_name)
            if screen_func:
                nbt["next_screen"] = screen_func
            else:
                print(f"[makeItem] Warning: Could not resolve screen '{screen_name}' to a function.")

        # Create the item
        new_item = defaultItem(item_manager, itemType, pos, nbt)

        # Add it to the manager
        item_manager.add_item(new_item)

        # Save for external access
        self.item = new_item
