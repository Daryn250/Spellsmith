import uuid
import json
import os
import pygame
from utility.item_utility.item import defaultItem  # Assuming your class is named `DefaultItem`
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

        grouped = {}
        for item in self.items:
            screen_name = getattr(item, "origin_screen", "unknown")

            next_screen_name = None
            if item.next_screen:
                for name, func in get_all_screen_functions():
                    if func == item.next_screen:
                        next_screen_name = name
                        break

            data = {
                "image": item.img_path,
                "uuid": item.uuid,
                "pos": item.pos,
                "type": item.type,
                "flags": item.flags,
                "animated": item.animated,
                "frameDuration": item.frameDuration,
                "next_screen": next_screen_name,
            }

            grouped.setdefault(screen_name, []).append(data)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(grouped, f, indent=4)


    def load_items(self, file_path, current_screen):
        if not os.path.exists(file_path):
            print(f"[ItemManager] No save file found at {file_path}")
            return

        with open(file_path, "r") as f:
            loaded_data = json.load(f)

        screen_data = loaded_data.get(current_screen, [])
        saved_uuids = {data["uuid"] for data in screen_data}
        self.items = [item for item in self.items if item.uuid not in saved_uuids]

        # Now load saved items
        for data in screen_data:
            screen_func = get_screen_function(data["next_screen"]) if data["next_screen"] else None
            item = defaultItem(
                img_path=data["image"],
                pos=tuple(data["pos"]),
                type=data["type"],
                flags=data.get("flags", []),
                animated=data.get("animated", False),
                frameDuration=data.get("frameDuration", 100),
                next_screen=(lambda s=screen_func: s) if screen_func else None
            )
            item.origin_screen = current_screen
            self.items.append(item)

