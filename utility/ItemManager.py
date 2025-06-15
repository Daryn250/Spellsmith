import uuid
import json
import os
import pygame
from utility.item import defaultItem  # Assuming your class is named `DefaultItem`
from utility.screenManager import *

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
        save_data = []
        for item in self.items:
            next_screen_name = None
            if item.next_screen:
                # store the name of the function and not the actual function bc json
                for name, func in get_all_screen_functions().items():
                    if func == item.next_screen:
                        next_screen_name = name
                        break

            save_data.append({
                "uuid": item.uuid,
                "image": item.img_path,
                "pos": item.pos,
                "type": item.type,
                "flags": item.flags,
                "animated": item.animated,
                "frameDuration": item.frameDuration,
                "next_screen": next_screen_name,
            })

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(save_data, f, indent=4)

    def load_items(self, file_path):
        if not os.path.exists(file_path):
            print(f"[ItemManager] No save file found at {file_path}")
            return

        with open(file_path, "r") as f:
            loaded_data = json.load(f)

        # Remove any existing items with saved UUIDs
        saved_uuids = {data["uuid"] for data in loaded_data}
        self.items = [item for item in self.items if item.uuid not in saved_uuids]

        # Now load saved items
        for data in loaded_data:

            # screenchanger functions
            next_screen_name = data.get("next_screen")
            next_screen_func = None

            if next_screen_name:
                try:
                    next_screen_func = get_screen_function(next_screen_name)
                except Exception as e:
                    print(f"Warning: Failed to load screen function '{next_screen_name}': {e}")

            item = defaultItem(
                uuidSave=data["uuid"],
                img_path=data["image"],
                pos=data["pos"],
                type=data["type"],
                flags=data.get("flags", []),
                animated=data.get("animated", False),
                frameDuration=data.get("frameDuration", 100),
                next_screen=next_screen_func
            )
            self.items.append(item)
