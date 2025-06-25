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
            "flags": ["draggable", "screen_change"],
            "img_path": "assets/screens/workstation/furnace.png",  # optional fallback
            "animated": False,
            "next_screen":"furnaceScreen"
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
        }
    },
    "copper_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/copper/copper2.png",
            "flags": ["draggable"],
        }
    },
    "iron_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/iron/iron1.png",
            "flags": ["draggable"],
        }
    },
    "iron_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/iron/iron2.png",
            "flags": ["draggable"],
        }
    },
    "lead_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/lead/lead1.png",
            "flags": ["draggable"],
        }
    },
    "lead_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/lead/lead2.png",
            "flags": ["draggable"],
        }
    },
    "lomium_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/lomium/lomium1.png",
            "flags": ["draggable"],
        }
    },
    "lomium_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/lomium/lomium2.png",
            "flags": ["draggable"],
        }
    },
    "silver_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/silver/silver1.png",
            "flags": ["draggable"],
        }
    },
    "silver_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/silver/silver2.png",
            "flags": ["draggable"],
        }
    },
    "titanium_ore": {
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/titanium/titanium1.png",
            "flags": ["draggable"],
        }
    },
    "titanium_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/titanium/titanium2.png",
            "flags": ["draggable"],
        }
    },
    "anodized_titanium_ingot": {
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/titanium/titanium3.png",
            "flags": ["draggable"],
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

        # Inject origin_screen directly into the item's NBT :DDD thank you ai i praise you for doing what i sometimes cant
        nbt["origin_screen"] = screen

        new_item = defaultItem(item_manager, itemType, pos, nbt)

        # Add to item manager
        item_manager.add_item(new_item)

        # Optionally store reference
        self.item = new_item
