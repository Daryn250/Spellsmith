import os
import json
from .hoverWindow import *
from utility.item_utility.baseItem import *

class BagManager:
    def __init__(self, gui_manager, capacity=10):
        self.capacity = capacity
        self.contents = []
        self.hovered = False
        self.hover_info = None
        self.bag_rect = None
        self.gui_manager = gui_manager

    def upgrade(self, new_capacity):
        if new_capacity > self.capacity:
            self.capacity = new_capacity

    def add_item(self, item):
        if len(self.contents) < self.capacity:
            self.contents.append(item)
            return True
        return False

    def remove_item(self, item):
        if item in self.contents:
            self.contents.remove(item)

    def get_items(self):
        return self.contents.copy()

    def update(self, mouse_pos):
        if self.bag_rect and self.bag_rect.collidepoint(mouse_pos):
            self.hovered = True
            self.hover_info = create_bag_hover_info("Bag", len(self.contents), self.capacity, mode="reduced")
        else:
            self.hovered = False
            self.hover_info = None

    def save_bag(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        bag_items = []
        for item in self.contents:
            if hasattr(item, "type"):
                entry = {
                    "class": item.__class__.__name__,
                    "type": item.type,
                    "pos": list(item.pos),
                    **item.to_nbt()
                }
            else:
                continue

            bag_items.append(entry)

        data["bag_contents"] = bag_items

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_bag(self, file_path, item_manager, screen_name="bag_screen"):
        if not os.path.exists(file_path):
            print(f"[BagManager] No save file at {file_path}")
            return False

        with open(file_path, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"[BagManager] Failed to parse JSON from {file_path}")
                return False

        bag_data = data.get("bag_contents", [])
        self.contents.clear()

        item_class_map = {
            "BaseItem": BaseItem,
            "BottleItem": BottleItem,
            "MaterialItem": MaterialItem,
            "CharmItem": CharmItem,
            "PartItem": PartItem,
            "GemItem": GemItem,
            "ToolItem": ToolItem
        }

        for entry in bag_data:
            try:
                pos = tuple(entry.get("pos", (0, 0)))
                class_name = entry.get("class", "BaseItem")
                nbt = {k: v for k, v in entry.items() if k not in {"class", "type", "pos"}}

                item_type = entry["type"]
                item_class = item_class_map.get(class_name, BaseItem)
                item = item_class(self, item_type, pos, nbt)

                item.state = "bagged"
                self.contents.append(item)

            except Exception as e:
                print(f"[BagManager] Failed to load item {entry.get('uuid', 'unknown')}: {e}")

        return True
