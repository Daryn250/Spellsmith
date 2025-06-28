import pygame

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
        width = 200
        height = 150
        rect = pygame.Rect(x, y, width, height)
        return rect.collidepoint(mouse_pos)

    def draw(self, surface, topleft, mouse, dragged_item=None):
        if self.animation:
            x, y = self.pos
        else:
            x, y = topleft
            self.pos = topleft

        # Base size of bag window
        base_width, base_height = 200, 150

        # Apply scaling from animation
        scaled_width = int(base_width * self.scale[0])
        scaled_height = int(base_height * self.scale[1])

        bg_rect = pygame.Rect(x, y, scaled_width, scaled_height)

        # Shadow (also scale shadow surface accordingly)
        shadow = pygame.Surface((bg_rect.width + 6, bg_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=8)
        surface.blit(shadow, (bg_rect.x + 3, bg_rect.y + 3))

        # Background image or solid color, scaled to current size
        if self.bg_image:
            scaled_bg = pygame.transform.scale(self.bg_image, (scaled_width, scaled_height))
            surface.blit(scaled_bg, (x, y))
        else:
            pygame.draw.rect(surface, (30, 30, 30), bg_rect, border_radius=8)

        # Draw items inside bag, scaled & positioned by scale
        for i, item in enumerate(self.bag.contents):
            col = i % 10
            row = i // 10
            item_x = x + int(self.padding * self.scale[0]) + col * int((self.item_size + self.spacing) * self.scale[0])
            item_y = y + int(self.padding * self.scale[1]) + row * int((self.item_size + self.spacing) * self.scale[1])

            # Draw each item scaled by current scale (optional: you can keep items fixed size if you want)
            item_size_scaled = (int(self.item_size * self.scale[0]), int(self.item_size * self.scale[1]))
            item.draw_at(surface, (item_x, item_y), size=item_size_scaled)

        # Shrink dragged item if hovered
        if dragged_item and self.is_hovered(mouse):
            shrink_size = int(dragged_item.base_size * 0.25)
            dragged_item.draw_at(surface, mouse, size=(shrink_size, shrink_size))

