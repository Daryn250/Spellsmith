import os
import json
import random
from .hoverWindow import *
from utility.item_utility.item import defaultItem
from utility.tool_utility.tool import Tool

class BagManager:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.contents = []  # List of actual item objects in the bag
        self.hovered = False
        self.hover_info = None
        self.bag_rect = None  # Set externally by GUIManager when drawing the bag

    def upgrade(self, new_capacity):
        if new_capacity > self.capacity:
            self.capacity = new_capacity

    def add_item(self, item):
        """Attempt to add an item. Return True if successful, False if full."""
        if len(self.contents) < self.capacity:
            self.contents.append(item)
            return True
        else:
            return False  # bag full

    def remove_item(self, item):
        if item in self.contents:
            self.contents.remove(item)

    def get_items(self):
        return self.contents.copy()

    def update(self, mouse_pos):
        if self.bag_rect and self.bag_rect.collidepoint(mouse_pos):
            self.hovered = True
            self.hover_info = create_bag_hover_info(
                "Bag", len(self.contents), self.capacity, mode="reduced"
            )
        else:
            self.hovered = False
            self.hover_info = None

    def save_bag(self, file_path):
        # Load existing data or create new dict
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        # Serialize each item in contents to dict
        saved_items = []
        for item in self.contents:
            # You can customize how your item serializes here
            if hasattr(item, "type"):
                item_data = {
                    "type": item.type,
                    **getattr(item, "to_nbt", lambda: {})()
                }
            elif hasattr(item, "tool_type"):
                item_data = {
                    "tool_type": item.tool_type,
                    **getattr(item, "to_nbt", lambda: {})()
                }
            else:
                # fallback or skip
                continue

            # Include position if available
            if hasattr(item, "pos"):
                item_data["pos"] = list(item.pos)

            saved_items.append(item_data)

        data["bag_contents"] = saved_items

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_bag(self, file_path, item_manager, screen_name="bag_screen"):
        """
        Load bag contents from file_path, reconstruct items using makeItem.
        `item_manager` is your item manager instance.
        `screen_name` is the origin screen identifier for bag items.
        """
        if not os.path.exists(file_path):
            print(f"[BagManager] No save file found at {file_path}")
            return False

        with open(file_path, "r") as f:
            data = json.load(f)

        bag_data = data.get("bag_contents", [])
        self.contents.clear()

        for entry in bag_data:
            try:
                pos = tuple(entry["pos"])
                nbt = {k: v for k, v in entry.items() if k not in {"type", "tool_type", "pos"}}

                if "tool_type" in entry:
                    tool_type = entry["tool_type"]
                    item = Tool(item_manager, tool_type, pos, nbt)
                    self.contents.append(item)

                elif "type" in entry:
                    item_type = entry["type"]
                    item = defaultItem(item_manager, item_type, pos, nbt)
                    self.contents.append(item)

                else:
                    raise ValueError("Item entry missing both 'type' and 'tool_type' fields")

            except Exception as e:
                print(f"[ItemManager] Failed to load item: {entry.get('uuid', 'unknown')} - {e}")

        return True
