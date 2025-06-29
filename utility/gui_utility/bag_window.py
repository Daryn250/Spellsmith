import pygame
from utility.item_utility.trickAnimation import TrickAnimation

class BagWindow:
    def __init__(self, bag_manager):
        self.bag = bag_manager
        self.animation = None
        self.original_pos = (0, 0)
        self.scale = [1.0, 1.0]
        self.pos = (0, 0)

        self.max_items = 50
        self.item_size = 24
        self.padding = 8
        self.spacing = 6

        self.hovered = False
        self.bg_image = pygame.image.load("assets/gui/bag/bag_window_bg.png").convert_alpha()

        

    def handle_event(self, event):
        pass  # no interaction yet, handled by draggable system

    def update(self, virtual_size, dt):
        if self.animation:
            self.animation.update(dt, self, virtual_size)

    def try_add_item(self, item):
        if len(self.bag.contents) < self.max_items:
            self.bag.contents.append(item)
            self.bag.save()
            return True
        else:
            item.vx = 4  # Throw outwards
            item.vy = -3
            item.state = "free"
            return False

    def is_hovered(self, mouse_pos):
        x, y = self.pos
        width = int(200 * self.scale[0])
        height = int(150 * self.scale[1])
        rect = pygame.Rect(x, y, width, height)
        return rect.collidepoint(mouse_pos)


    def draw(self, surface, topleft, mouse, dragged_item=None):
        # Update animated position
        if self.animation:
            x, y = self.pos
        else:
            x, y = topleft
            self.pos = topleft

        base_width, base_height = 200, 150
        scaled_width = int(base_width * self.scale[0])
        scaled_height = int(base_height * self.scale[1])
        bg_rect = pygame.Rect(x, y, scaled_width, scaled_height)

        # Draw shadow
        shadow = pygame.Surface((bg_rect.width + 6, bg_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=8)
        surface.blit(shadow, (bg_rect.x + 3, bg_rect.y + 3))

        # Draw background
        if self.bg_image:
            scaled_bg = pygame.transform.scale(self.bg_image, (scaled_width, scaled_height))
            surface.blit(scaled_bg, (x, y))
        else:
            pygame.draw.rect(surface, (30, 30, 30), bg_rect, border_radius=8)

        # Draw bag contents
        for i, item in enumerate(self.bag.contents):
            col = i % 10
            row = i // 10
            item_x = x + int(self.padding * self.scale[0]) + col * int((self.item_size + self.spacing) * self.scale[0])
            item_y = y + int(self.padding * self.scale[1]) + row * int((self.item_size + self.spacing) * self.scale[1])
            item_size_scaled = (int(self.item_size * self.scale[0]), int(self.item_size * self.scale[1]))
            item.draw_at(surface, (item_x, item_y), size=item_size_scaled)


    def handle_drop(self, item, mouse_pos, item_manager):
        if not self.is_hovered(mouse_pos):
            return False  # Not dropped on bag

        success = self.bag.add_item(item)
        if success:
            # Create animation with on_complete callback at init
            item.trick = TrickAnimation([
                {"time": 0.0, "scale": item.scale},
                {"time": 0.15, "scale": (0.0, 0.0)},
            ])
            item.trick.on_complete=lambda item: item_manager.remove_item(item.uuid)
            item.trick.reset()  # Resets internal time/index to properly detect on_complete

            return True
        else:
            # Rejected — throw out
            item.vx = 4
            item.vy = -3
            item.state = "free"
            return False




