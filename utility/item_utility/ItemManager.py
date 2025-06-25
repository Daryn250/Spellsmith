import uuid
import json
import os
import pygame
from utility.item_utility.item import defaultItem  # Assuming your class is named `DefaultItem` # it is thank you chat gpt you're amazing
from utility.tool_utility.tool import Tool
from utility.screen_utility.screenManager import *

class ItemManager:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        if not hasattr(item, "uuid"):
            item.uuid = str(uuid.uuid4())
        self.items.append(item)

    def remove_by_uuid(self, uuid_to_remove):
        self.items = [item for item in self.items if getattr(item, "uuid", None) != uuid_to_remove]


    def save_items(self, file_path):
        import os
        import json

        # Load existing data if it exists
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = {}
        else:
            existing_data = {}

        # Build screen-specific group of current items
        grouped = {}
        for item in self.items:
            screen_name = getattr(item, "origin_screen", "unknown")
            
            if hasattr(item, "type"):
                data = {
                    "type": item.type,
                    "pos": list(item.pos),
                    **item.to_nbt()
                }
            elif hasattr(item, "tool_type"):
                data = {
                    "tool_type": item.tool_type,
                    "pos": list(item.pos),
                    **item.to_nbt()
                }
            else:
                continue

            # Convert next_screen function to its name
            if "next_screen" in data and callable(data["next_screen"]):
                data["next_screen"] = data["next_screen"].__name__

            grouped.setdefault(screen_name, []).append(data)

        # Update only the relevant screen section
        for screen_name, items in grouped.items():
            existing_data[screen_name] = items

        # Ensure save directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Write merged result
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

        # Remove existing items with matching UUIDs
        saved_uuids = {entry.get("uuid") for entry in screen_data if "uuid" in entry}
        self.items = [item for item in self.items if getattr(item, "uuid", None) not in saved_uuids]

        for entry in screen_data:
            try:
                pos = tuple(entry["pos"])
                nbt = {k: v for k, v in entry.items() if k not in {"type", "tool_type", "pos"}}

                if "tool_type" in entry:
                    tool_type = entry["tool_type"]
                    item = Tool(self, tool_type, pos, nbt)
                    self.items.append(item)

                elif "type" in entry:
                    item_type = entry["type"]
                    item = defaultItem(self, item_type, pos, nbt)
                    self.items.append(item)

                else:
                    raise ValueError("Item entry missing both 'type' and 'tool_type' fields")

            except Exception as e:
                print(f"[ItemManager] Failed to load item: {entry.get('uuid', 'unknown')} - {e}")


    def getItemByUUID(self, uuid):
        for item in self.items:
            if item.uuid == uuid:
                return item
        return None
    
    def getSlotByName(self, name):
        for item in self.items:
            if "slot" in item.flags: 
                if getattr(item, "slot_name", None) == name:
                    return item
        return None

