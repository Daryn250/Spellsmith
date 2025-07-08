import uuid
import json
import os
import pygame
from utility.item_utility.baseItem import BaseItem, BottleItem, MaterialItem, CharmItem, PartItem
from utility.tool_utility.tool import Tool
from utility.screen_utility.screenManager import *

class ItemManager:
    def __init__(self, virtual_size):
        self.VIRTUAL_SIZE = virtual_size
        self.items = []

    def add_item(self, item):
        if not hasattr(item, "uuid"):
            item.uuid = str(uuid.uuid4())
        self.items.append(item)

    def remove_by_uuid(self, uuid_to_remove):
        self.items = [item for item in self.items if getattr(item, "uuid", None) != uuid_to_remove]

    def save_items(self, file_path, current_screen, extra_screen_data=None):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        screen_items = []
        for item in self.items:
            screen_name = getattr(item, "origin_screen", "unknown")
            if screen_name != current_screen:
                continue

            if hasattr(item, "type"):
                data = {
                    "class": item.__class__.__name__,
                    "type": item.type,
                    "pos": list(item.pos),
                    **item.to_nbt()
                }
            elif hasattr(item, "tool_type"):
                data = {
                    "class": "Tool",
                    "tool_type": item.tool_type,
                    "pos": list(item.pos),
                    **item.to_nbt()
                }
            else:
                continue

            if "next_screen" in data and callable(data["next_screen"]):
                data["next_screen"] = data["next_screen"].__name__

            screen_items.append(data)

        existing_data[current_screen] = screen_items

        if extra_screen_data:
            existing_data["_screen_data"] = extra_screen_data

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as f:
            json.dump(existing_data, f, indent=4)

    def load_items(self, file_path, current_screen):
        if not os.path.exists(file_path):
            print(f"[ItemManager] No save file found at {file_path}")
            return

        with open(file_path, "r") as f:
            data = json.load(f)

        screen_data = data.get(current_screen)
        if not screen_data:
            print(f"[ItemManager] No data for screen '{current_screen}' in {file_path}")
            return False

        saved_uuids = {entry.get("uuid") for entry in screen_data if "uuid" in entry}
        self.items = [item for item in self.items if getattr(item, "uuid", None) not in saved_uuids]

        item_class_map = {
            "BaseItem": BaseItem,
            "BottleItem": BottleItem,
            "MaterialItem": MaterialItem,
            "CharmItem": CharmItem,
            "PartItem": PartItem,
            "Tool": Tool
        }

        for entry in screen_data:
            try:
                pos = tuple(entry["pos"])
                class_name = entry.get("class", "BaseItem")
                nbt = {k: v for k, v in entry.items() if k not in {"class", "type", "tool_type", "pos"}}

                if class_name == "Tool":
                    tool_type = entry["tool_type"]
                    item = Tool(self, tool_type, pos, nbt)
                else:
                    item_type = entry["type"]
                    item_class = item_class_map.get(class_name, BaseItem)
                    item = item_class(self, item_type, pos, nbt)

                self.items.append(item)

            except Exception as e:
                print(f"[ItemManager] Failed to load item: {entry.get('uuid', 'unknown')} - {e}")

        screen_meta = data.get("_screen_data", {}).get(current_screen)
        return screen_meta or {}

    def remove_item(self, uuid):
        self.items = [item for item in self.items if getattr(item, "uuid", None) != uuid]
        for item in self.items:
            if getattr(item, "contains", None) == uuid:
                item.contains = None

    def draw_with_z_respect(self, virtual_surface, VIRTUAL_SIZE, gui_manager, rotation_scale=1):
        dragged_item = None
        items_to_draw = []

        for item in self.items:
            is_dragged = getattr(item, "dragging", False)
            is_animating = hasattr(item, "animation") and not item.animation.finished

            if is_dragged:
                dragged_item = item
            elif is_animating:
                continue
            else:
                items_to_draw.append(item)

        items_to_draw.sort(key=lambda item: item.pos[1])

        for item in items_to_draw:
            item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, self, rotation_scale)
            for p in item.particles:
                p.draw(virtual_surface)

    def draw_dragged_item(self, virtual_surface, VIRTUAL_SIZE, gui_manager, rotation_scale=1):
        for item in self.items:
            is_dragged = getattr(item, "dragging", False)
            is_animating = hasattr(item, "animation") and not item.animation.finished

            if is_dragged or is_animating:
                item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, self, rotation_scale)
                for p in item.particles:
                    p.draw(virtual_surface)

    def getItemByUUID(self, uuid):
        for item in self.items:
            if item.uuid == uuid:
                return item
        return None

    def get_dragged(self):
        for item in self.items:
            if getattr(item, "dragging", False) == True:
                return item
        return None

    def getSlotByName(self, name):
        for item in self.items:
            if "slot" in item.flags: 
                if getattr(item, "slot_name", None) == name:
                    return item
        return None
