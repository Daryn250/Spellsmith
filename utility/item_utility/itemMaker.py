from .baseItem import *
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
            "flags": ["draggable", "screen_change", "unbaggable"],
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
            "flags": ["draggable", "screen_change", "unbaggable"],
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
            "img_path": "assets/items/bottles/large_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "large_bottle",
            "capacity": 10, # units of liquid
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "hexagon_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/hexagon_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "hexagon_bottle",
            "capacity": 7,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "gold_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/gold_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "gold_bottle",
            "capacity": 10,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "crescent_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/crescent_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "crescent_bottle",
            "capacity": 7,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "circle_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/circle_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "circle_bottle",
            "capacity": 6,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "spiked_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/spiked_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "spiked_bottle",
            "capacity": 10,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "uranium_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/uranium_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "uranium_bottle",
            "capacity": 11,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "tall_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/tall_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "tall_bottle",
            "capacity": 9,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "small_uranium_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/small_uranium_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "small_uranium_bottle",
            "capacity": 3,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "small_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/small_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "small_bottle",
            "capacity": 3,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "red_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/red_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "red_bottle",
            "capacity": 5,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "mini_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/mini_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "mini_bottle",
            "capacity": 1,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "brown_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/brown_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "brown_bottle",
            "capacity": 4,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    "chain_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/chain_bottle/img1.png",
            "flags": ["draggable"],
            "bottleType": "chain_bottle",
            "capacity": 6,
            "contents": 0,
            "liquid": None,
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5)
        }
    },
    ###### GEMS #########
    "aquamarine": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/aquamarine/gem.png",
            "shine_path": "assets/items/gems/aquamarine/shine.png",
            "flags": ["draggable", "shiny"],
            "scale":(1,1)
        }
    },
    "citrine": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/citrine/gem.png",
            "shine_path": "assets/items/gems/citrine/shine.png",
            "flags": ["draggable", "shiny"],
            "scale":(1,1)
        }
    },
    "emerald": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/emerald/gem.png",
            "shine_path": "assets/items/gems/emerald/shine.png",
            "flags": ["draggable", "shiny"],
            "scale":(1,1)
        }
    },
    "rhotochrosite": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/rhotochrosite/gem.png",
            "shine_path": "assets/items/gems/rhotochrosite/shine.png",
            "flags": ["draggable", "shiny"],
            "scale":(1,1)
        }
    },
    "tourmaline": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/tourmaline/gem.png",
            "shine_path": "assets/items/gems/tourmaline/shine.png",
            "flags": ["draggable", "shiny"],
            "scale":(1,1)
        }
    },
    "flawless_tourmaline": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/tourmaline/perfect.png",
            "shine_path": "assets/items/gems/tourmaline/shine_perfect.png",
            "flags": ["draggable", "shiny"],
            "scale":(1,1)
        }
    },

}

item_class_map = {
    "BaseItem": BaseItem,
    "BottleItem": BottleItem,
    "MaterialItem": MaterialItem,
    "CharmItem": CharmItem,
    "PartItem": PartItem,
    "GemItem": GemItem,
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
