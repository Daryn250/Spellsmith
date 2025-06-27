from .hoverWindow import *
class BagManager:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.slots = [None for _ in range(capacity)]
        self.hovered = False
        self.hover_info = None
        self.bag_rect = None  # Set externally when drawing the bag

    def upgrade(self, new_capacity):
        if new_capacity > self.capacity:
            self.slots += [None] * (new_capacity - self.capacity)
            self.capacity = new_capacity

    def get_items(self):
        return [slot for slot in self.slots if slot is not None]

    def update(self, mouse_pos):
        if self.bag_rect and self.bag_rect.collidepoint(mouse_pos):
            self.hovered = True
            self.hover_info = create_bag_hover_info("Bag", len(self.get_items()), self.capacity, mode="reduced")
        else:
            self.hovered = False
            self.hover_info = None

