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
            data = {
                "type": item.type,
                "pos": list(item.pos),  # JSON doesn't support tuples
                **item.to_nbt()
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
            data = json.load(f)

        screen_data = data.get(current_screen)
        if not screen_data:
            print(f"[ItemManager] No data for screen '{current_screen}' in {file_path}")
            return  # don't touch current items if screen has nothing to load

        # Get UUIDs that are going to be replaced
        saved_uuids = {entry["uuid"] for entry in screen_data if "uuid" in entry}
        self.items = [item for item in self.items if item.uuid not in saved_uuids]

        for entry in screen_data:
            type_ = entry["type"]
            pos = tuple(entry["pos"])
            nbt = {k: v for k, v in entry.items() if k not in {"type", "pos"}}

            try:
                item = defaultItem(type_, pos, nbt)
                self.items.append(item)
            except Exception as e:
                print(f"[ItemManager] Failed to load item {entry.get('uuid', '?')}: {e}")

    def getItemByUUID(self, uuid):
        for item in self.items:
            if item.uuid == uuid:
                return item
        return None

