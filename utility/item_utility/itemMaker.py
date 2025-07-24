from .baseItem import *
from utility.screen_utility.screenManager import get_screen_function

ITEM_BASES = {
    #### UTILITY ####
    "slot_node": {
        "class": "BaseItem",
        "type": "slot",
        "nbt": {
            "flags": ["slot", "invisible", "no_shadow"],
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
            "flags": ["draggable", "screen_change", "unbaggable", "inspectable"],
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
            "flags": ["draggable", "screen_change", "unbaggable", "inspectable"],
            "img_path": "assets/screens/workstation/anvil.png",
            "animated": False,
            "next_screen": "anvilScreen",
            "scale": (2, 2)
        }
    },
    "map": {
        "class": "BaseItem",
        "type": "paper",
        "nbt": {
            "flags": ["draggable", "screen_change", "unbaggable", "background", "no_shadow", "inspectable"],
            "img_path": "assets/screens/table/paper1.png",
            "animated": False,
            "next_screen": "mapScreen",
            "scale": (2, 2)
        }
    },
    "craft": {
        "class": "BaseItem",
        "type": "paper",
        "nbt": {
            "flags": ["draggable", "screen_change", "unbaggable", "background", "no_shadow", "inspectable"],
            "img_path": "assets/screens/table/paper2.png",
            "animated": False,
            "next_screen": "workstation",
            "scale": (2, 2)
        }
    },
    #### ISLANDS FOR MAP ####
    "map_boat": {
        "class": "IslandItem",
        "type": "island",
        "nbt": {
            "island_name": "boat",
            "flags": ["screen_change", "island", "no_shadow", "inspectable"],
            "img_path": "assets/screens/map/boat",
            "animated": True,
            "next_screen": "main_menu",
            "scale": (1,1)
        }
    },
    "island1": {
        "class": "IslandItem",
        "type": "island",
        "nbt": {
            "island_name": "island1",
            "flags": ["screen_change", "island", "no_shadow", "inspectable"],
            "img_path": "assets/screens/map/islands/island1.png",
            "animated": False,
            "next_screen": "main_menu",
            "scale": (1,1)
        }
    },
    "island2": {
        "class": "IslandItem",
        "type": "island",
        "nbt": {
            "island_name": "island2",
            "flags": ["screen_change", "island", "no_shadow", "inspectable"],
            "img_path": "assets/screens/map/islands/beach_island.png",
            "animated": False,
            "next_screen": "main_menu",
            "scale": (1,1)
        }
    },
    "island3": {
        "class": "IslandItem",
        "type": "island",
        "nbt": {
            "island_name": "island3",
            "flags": ["screen_change", "island", "no_shadow", "inspectable"],
            "img_path": "assets/screens/map/islands/mountain_island.png",
            "animated": False,
            "next_screen": "main_menu",
            "scale": (1,1)
        }
    },
    #### CHARMS ####
    "rain_charm": {
        "class": "CharmItem",
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/rain_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable", "inspectable"],
            "charmType": "rain_charm"
        }
    },
    "moon_charm": {
        "class": "CharmItem",
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/moon_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable", "inspectable"],
            "charmType": "moon_charm"
        }
    },
    "mana_charm": {
        "class": "CharmItem",
        "type": "charm",
        "nbt": {
            "img_path": "assets/gui/charm_board/mana_charm/passive",
            "animated": True,
            "flags": ["draggable", "charm", "hangable", "inspectable"],
            "charmType": "mana_charm"
        }
    },
    #### MATERIALS ####
    "copper_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/copper/copper_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "copper"
        }
    },
    "copper_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/copper/copper1.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "copper"
        }
    },
    "copper_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/copper/copper2.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "copper"
        }
    },
    "iron_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/iron/iron_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "iron"
        }
    },
    "iron_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/iron/iron1.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "iron"
        }
    },
    "iron_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/iron/iron2.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "iron"
        }
    },
    "lead_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/lead/lead_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "lead"
        }
    },
    "lead_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/lead/lead1.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "lead"
        }
    },
    "lead_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/lead/lead2.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "lead"
        }
    },
    "lomium_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/lomium/lomium_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "lomium"
        }
    },
    "lomium_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/lomium/lomium1.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "lomium"
        }
    },
    "lomium_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/lomium/lomium2.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "lomium"
        }
    },
    "silver_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/silver/silver_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "silver"
        }
    },
    "silver_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/silver/silver1.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "silver"
        }
    },
    "silver_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/silver/silver2.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "silver"
        }
    },
    "titanium_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/titanium/titanium_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "titanium"
        }
    },
    "titanium_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/titanium/titanium1.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "titanium"
        }
    },
    "titanium_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/titanium/titanium2.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "titanium"
        }
    },
    "thanium_rock": {
        "class": "MaterialItem",
        "type": "rock",
        "nbt": {
            "img_path": "assets/items/materials/thanium/thanium_rock.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "thanium"
        }
    },
    "thanium_ore": {
        "class": "MaterialItem",
        "type": "ore",
        "nbt": {
            "img_path": "assets/items/materials/thanium/thanium_ore.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "thanium"
        }
    },
    "thanium_ingot": {
        "class": "MaterialItem",
        "type": "ingot",
        "nbt": {
            "img_path": "assets/items/materials/thanium/thanium_ingot.png",
            "flags": ["draggable", "inspectable"],
            "temperature": 0,
            "material": "thanium"
        }
    },
    ### FUEL TYPES ###
    "large_coal": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/large_coal.png",
            "flags": ["draggable", "inspectable"],
            "fuel": 0.4
        }
    },
    "medium_coal": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/med_coal.png",
            "flags": ["draggable", "inspectable"],
            "fuel": 0.3
        }
    },
    "small_coal": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/small_coal.png",
            "flags": ["draggable", "inspectable"],
            "fuel": 0.2
        }
    },
    "log": {
        "class": "MaterialItem",
        "type": "fuel",
        "nbt": {
            "img_path": "assets/items/fuel/log.png",
            "flags": ["draggable", "inspectable"],
            "fuel": 0.05
        }
    },
    ######## BOTTLES ############
    "large_bottle": {
        "class": "BottleItem",
        "type": "bottle",
        "nbt": {
            "img_path": "assets/items/bottles/large_bottle/img1.png",
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "inspectable"],
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
            "flags": ["draggable", "shiny", "inspectable"],
            "scale":(1,1)
        }
    },
    "citrine": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/citrine/gem.png",
            "shine_path": "assets/items/gems/citrine/shine.png",
            "flags": ["draggable", "shiny", "inspectable"],
            "scale":(1,1)
        }
    },
    "emerald": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/emerald/gem.png",
            "shine_path": "assets/items/gems/emerald/shine.png",
            "flags": ["draggable", "shiny", "inspectable"],
            "scale":(1,1)
        }
    },
    "rhotochrosite": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/rhotochrosite/gem.png",
            "shine_path": "assets/items/gems/rhotochrosite/shine.png",
            "flags": ["draggable", "shiny", "inspectable"],
            "scale":(1,1)
        }
    },
    "tourmaline": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/tourmaline/gem.png",
            "shine_path": "assets/items/gems/tourmaline/shine.png",
            "flags": ["draggable", "shiny", "inspectable"],
            "scale":(1,1)
        }
    },
    "flawless_tourmaline": {
        "class":"GemItem",
        "type":"gem",
        "nbt": {
            "img_path": "assets/items/gems/tourmaline/perfect.png",
            "shine_path": "assets/items/gems/tourmaline/shine_perfect.png",
            "flags": ["draggable", "shiny", "inspectable"],
            "scale":(1,1)
        }
    },
    ##### PARTS #####
    "rounded_pommel": {
        "class":"PartItem",
        "type":"pommel",
        "nbt": {
            # pass in img_path as extra nbt as such: "assets/tools/parts/{name}/{material}.png"
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"common",
        }
    },
    "spiked_pommel": {
        "class":"PartItem",
        "type":"pommel",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"uncommon",
        }
    },
    "blunt_pommel": {
        "class":"PartItem",
        "type":"pommel",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"rare",
        }
    },
    "crystal_pommel": {
        "class":"PartItem",
        "type":"pommel",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "gem":None,
            "rarity":"rare+",
        }
    },
    "dagger_pommel": {
        "class":"PartItem",
        "type":"pommel",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"unique",
        }
    },
    "orb_pommel": {
        "class":"PartItem",
        "type":"pommel",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "gem":None,
            "rarity":"elite",
        }
    },
    ### GUARDS ###
    "cross_guard": {
        "class":"PartItem",
        "type":"guard",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"common",
        }
    },
    "quillon_guard": {
        "class":"PartItem",
        "type":"guard",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"uncommon",
        }
    },
    "basket_guard": {
        "class":"PartItem",
        "type":"guard",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"rare+",
        }
    },
    "mortuary_guard": {
        "class":"PartItem",
        "type":"guard",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"unique",
        }
    },
    ### HANDLES ###
    "one_hand_handle": {
        "class":"PartItem",
        "type":"handle",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"common",
        }
    },
    "two_handed_handle": {
        "class":"PartItem",
        "type":"handle",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"uncommon",
        }
    },
    ### BLADES ###
    "longsword_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"common",
        }
    },
    "falchion_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"uncommon",
        }
    },
    "greatsword_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"rare",
        }
    },
    "jian_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"rare+",
        }
    },
    "rapier_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"unique",
        }
    },
    "tachi_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"elite",
        }
    },
    "cinquedea_blade": {
        "class":"PartItem",
        "type":"blade",
        "nbt": {
            # pass in img_path as extra nbt ^^^
            "flags": ["draggable", "inspectable"],
            "scale":(1.5,1.5),
            "default_scale":(1.5,1.5),
            "temperature": 0,
            "rarity":"elite",
        }
    },
    "sword": {
        "class":"ToolItem",
        "type":"sword",
        "nbt": {
            "flags": ["draggable", "inspectable"]
        }
    }
}

item_class_map = {
    "BaseItem": BaseItem,
    "BottleItem": BottleItem,
    "MaterialItem": MaterialItem,
    "CharmItem": CharmItem,
    "PartItem": PartItem,
    "GemItem": GemItem,
    "ToolItem": ToolItem
}

class makeItem:
    def __init__(self, item_manager, itemType: str, pos, screen: str, extra_nbt=None):
        if itemType.lower() not in ITEM_BASES:
            raise ValueError(f"Unknown itemType: {itemType}")

        base = ITEM_BASES[itemType.lower()]
        nbt = base["nbt"].copy()
        item_class_name = base.get("class", "BaseItem")
        item_class = item_class_map.get(item_class_name, BaseItem)

        if extra_nbt:
            nbt.update(extra_nbt)

        nbt["origin_screen"] = screen
        nbt["item_name"] = itemType

        if "next_screen" in nbt and isinstance(nbt["next_screen"], str):
            screen_name = nbt["next_screen"]
            screen_func = get_screen_function(screen_name)
            if screen_func:
                nbt["next_screen"] = screen_func
            else:
                nbt["next_screen"] = get_screen_function("main_menu")
                print(f"[makeItem] Warning: Could not resolve screen '{screen_name}' to a function, defaulting to main menu for security.")

        new_item = item_class(item_manager, base["type"], pos, nbt)

        item_manager.add_item(new_item)

        self.item = new_item

def item_debug(item_manager, start_pos=(50, 50), screen_name="main_menu", spacing=48, max_columns=10):
    """Spawns all non-part items in a grid for debug purposes."""
    x, y = start_pos
    col = 0

    for name, data in ITEM_BASES.items():
        nbt = {}
        if data.get("class") == "PartItem":
            continue  # Skip parts
        
        try:
            makeItem(item_manager, name, (x, y), screen_name, nbt)
        except Exception as e:
            print(f"item {name} failed to load: {e}")

        col += 1
        if col >= max_columns:
            col = 0
            x = start_pos[0]
            y += spacing
        else:
            x += spacing


