import uuid
import json
import os
import pygame
from utility.item_utility.baseItem import *
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
            else:
                continue

            # Fix: next_screen may be in item, not in data yet
            if hasattr(item, "next_screen"):
                if callable(getattr(item, "next_screen", None)):
                    data["next_screen"] = item.next_screen.__name__
                else:
                    data["next_screen"] = item.next_screen
            elif "next_screen" in data:
                if callable(data["next_screen"]):
                    data["next_screen"] = data["next_screen"].__name__

            screen_items.append(data)

        # Save as a dict with 'items' and '_screen_data' for the current screen
        screen_dict = {"items": screen_items}
        if extra_screen_data is not None:
            screen_dict["_screen_data"] = extra_screen_data
        existing_data[current_screen] = screen_dict

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

        # Support both new (dict) and old (list) formats
        if isinstance(screen_data, dict):
            items_data = screen_data.get("items", [])
            screen_meta = screen_data.get("_screen_data", {})
        elif isinstance(screen_data, list):
            items_data = screen_data
            # Try to get legacy _screen_data from root
            screen_meta = data.get("_screen_data", {})
        else:
            items_data = []
            screen_meta = {}

        saved_uuids = {entry.get("uuid") for entry in items_data if "uuid" in entry}
        self.items = [item for item in self.items if getattr(item, "uuid", None) not in saved_uuids]

        item_class_map = {
            "BaseItem": BaseItem,
            "BottleItem": BottleItem,
            "MaterialItem": MaterialItem,
            "CharmItem": CharmItem,
            "PartItem": PartItem,
            "GemItem": GemItem,
            "ToolItem": ToolItem
        }

        for entry in items_data:
            try:
                pos = tuple(entry["pos"])
                class_name = entry.get("class", "BaseItem")
                nbt = {k: v for k, v in entry.items() if k not in {"class", "type", "pos"}}


                item_type = entry["type"]
                item_class = item_class_map.get(class_name, BaseItem)
                item = item_class(self, item_type, pos, nbt)

                self.items.append(item)

            except Exception as e:
                print(f"[ItemManager] Failed to load item: {entry.get('uuid', 'unknown')} - {e}")

        return screen_meta or {}

    def remove_item(self, uuid, gui_manager = None):
        # Remove the item and its window if present
        items_to_remove = [item for item in self.items if getattr(item, "uuid", None) == uuid]
        for item in items_to_remove:
            if hasattr(item, "window"):
                if gui_manager == None:
                    raise ValueError("paramater gui manager is none, this is an issue please pass it in homeboy")
                if item.window in gui_manager.windows:
                    gui_manager.windows.remove(item.window)
                item.window = None
        self.items = [item for item in self.items if getattr(item, "uuid", None) != uuid]
        for item in self.items:
            if getattr(item, "contains", None) == uuid:
                item.contains = None

    def draw_with_z_respect(self, virtual_surface, VIRTUAL_SIZE, gui_manager, rotation_scale=1):
        dragged_item = None
        background_items = []
        foreground_items = []

        for item in self.items:
            is_dragged = getattr(item, "dragging", False)
            is_animating = hasattr(item, "animation") and not item.animation.finished

            if is_dragged:
                dragged_item = item
            elif is_animating:
                continue
            elif "background" in getattr(item, "flags", []):
                background_items.append(item)
            else:
                foreground_items.append(item)

        # Sort both background and foreground items by their Y position
        background_items.sort(key=lambda item: item.pos[1])
        foreground_items.sort(key=lambda item: item.pos[1])

        # Draw background items first
        for item in background_items:
            item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, self, rotation_scale)

        # Then draw foreground items
        for item in foreground_items:
            item.draw(virtual_surface, VIRTUAL_SIZE, gui_manager, self, rotation_scale)

        # Then draw particles
        for item in background_items + foreground_items:
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
