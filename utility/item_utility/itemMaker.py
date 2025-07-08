from .baseItem import BaseItem, BottleItem, MaterialItem, CharmItem, PartItem
from utility.screen_utility.screenManager import get_screen_function

ITEM_BASES = {
    #### UTILITY ####
    "slot_node": {
        "class": "BaseItem",
        "type": "slot",
        "nbt": {
            "flags": ["slot", "invisible"],
            "slot_accepts": [],
            "img_path": "assets/very_important/cat.png",
            "animated": False,
            "contains": None
        }
    },
    "furnace": {
        "class": "BaseItem",
        "type": "furnace",
        "nbt": {
            "flags": ["draggable", "screen_change", "no_shadow", "unbaggable"],
            "img_path": "assets/screens/workstation/furnace.png",
            "animated": False,
            "next_screen": "furnaceScreen",
            "scale": (2, 2)
        }
    },
    "anvil": {
        "class": "BaseItem",
        "type": "anvil",
        "nbt": {
            "flags": ["draggable", "screen_change", "no_shadow", "unbaggable"],
            "img_path": "assets/screens/workstation/anvil.png",
            "animated": False,
            "next_screen": "anvilScreen",
            "scale": (2, 2)
        }
    },
    #### CHARMS ####
    "rain_charm": {
        "class": "CharmItem",
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/rain_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable"],
            "charmType": "rain_charm"
        }
    },
    "moon_charm": {
        "class": "CharmItem",
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/moon_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable"],
            "charmType": "moon_charm"
        }
    },
    "mana_charm": {
        "class": "CharmItem",
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/mana_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable"],
            "charmType": "mana_charm"
        }
    },
    #### MATERIALS ####
    "copper_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/copper/copper1.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "copper"
        }
    },
    "copper_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/copper/copper2.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "copper"
        }
    },
    "iron_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/iron/iron1.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "iron"
        }
    },
    "iron_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/iron/iron2.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "iron"
        }
    },
    "lead_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/lead/lead1.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "lead"
        }
    },
    "lead_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/lead/lead2.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "lead"
        }
    },
    "lomium_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/lomium/lomium1.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "lomium"
        }
    },
    "lomium_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/lomium/lomium2.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "lomium"
        }
    },
    "silver_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/silver/silver1.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "silver"
        }
    },
    "silver_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/silver/silver2.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "silver"
        }
    },
    "titanium_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/titanium/titanium1.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "titanium"
        }
    },
    "titanium_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/titanium/titanium2.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "titanium"
        }
    },
    "anodized_titanium_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/titanium/titanium3.png",
            "flags": ["draggable"],
            "temperature": 0,
            "material": "titanium"
        }
    },
    ### FUEL TYPES ###
    "large_coal": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/large_coal.png",
            "flags": ["draggable"],
            "fuel": 0.4
        }
    },
    "medium_coal": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/med_coal.png",
            "flags": ["draggable"],
            "fuel": 0.3
        }
    },
    "small_coal": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/small_coal.png",
            "flags": ["draggable"],
            "fuel": 0.2
        }
    },
    "log": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/log.png",
            "flags": ["draggable"],
            "fuel": 0.05
        }
    },
    ######## BOTTLES ############
    "large_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/large_bottle/img1.png",  # ✅ Points to actual image
            "flags": ["draggable"],
            "bottleType": "large_bottle",
            "capacity": 100,
            "contents": 50,
            "liquid": "water",
            "scale":[2,2]
        }
    },


}

item_class_map = {
    "BaseItem": BaseItem,
    "BottleItem": BottleItem,
    "MaterialItem": MaterialItem,
    "CharmItem": CharmItem,
    "PartItem": PartItem
}

class makeItem:
    def __init__(self, item_manager, itemType: str, pos, screen: str, extra_nbt=None):
        if itemType not in ITEM_BASES:
            raise ValueError(f"Unknown itemType: {itemType}")

        base = ITEM_BASES[itemType]
        nbt = base["nbt"].copy()
        item_class_name = base.get("class", "BaseItem")
        item_class = item_class_map.get(item_class_name, BaseItem)

        if extra_nbt:
            nbt.update(extra_nbt)

        nbt["origin_screen"] = screen

        if "next_screen" in nbt and isinstance(nbt["next_screen"], str):
            screen_name = nbt["next_screen"]
            screen_func = get_screen_function(screen_name)
            if screen_func:
                nbt["next_screen"] = screen_func
            else:
                print(f"[makeItem] Warning: Could not resolve screen '{screen_name}' to a function.")

        new_item = item_class(item_manager, base["type"], pos, nbt)

        item_manager.add_item(new_item)

        self.item = new_item
