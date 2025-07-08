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

    def update(self, virtual_size, dt, gui_manager):
        if self.animation:
            self.animation.update(dt, self, virtual_size)

        if self.animation.finished:
            for item in self.bag.contents:
                if item.dragging:
                    continue
                if item.state == "bagged":
                    item.update(None, gui_manager, virtual_size, bounds=self.get_bounds_rect(), dt=dt)
                    for p in item.particles:
                        p.update()
                    item.particles = [p for p in item.particles if p.is_alive()]

    def get_bounds_rect(self):
        x, y = self.pos
        width = int(200 * self.scale[0])
        height = int(200 * self.scale[1])
        return pygame.Rect(x, y, width, height)

    def is_hovered(self, mouse_pos):
        return self.get_bounds_rect().collidepoint(mouse_pos)

    def try_add_item(self, item):
        if "unbaggable" not in item.flags:
            if item not in self.bag.contents:
                if len(self.bag.contents) < self.max_items:
                    self.bag.contents.append(item)
                    item.state = "bagged"
                    return True
                else:
                    item.vx = 4
                    item.vy = -3
                    item.state = "free"
                    return False

    def try_remove_item(self, item, item_manager):
        if item in self.bag.contents and item not in item_manager.items:
            self.bag.contents.remove(item)
            item_manager.add_item(item)
            item.state = "free"
            item.vx = 0
            item.vy = -2
            return True
        return False

    def draw(self, surface, topleft, mouse, screensize, dragged_item=None):
        full_surf = pygame.Surface(screensize, pygame.SRCALPHA)

        if self.animation:
            x, y = self.pos
        else:
            x, y = topleft
            self.pos = topleft

        base_width, base_height = 200, 200
        scaled_width = int(base_width * self.scale[0])
        scaled_height = int(base_height * self.scale[1])
        bg_rect = pygame.Rect(x, y, scaled_width, scaled_height)

        shadow = pygame.Surface((bg_rect.width + 6, bg_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=8)
        full_surf.blit(shadow, (bg_rect.x + 3, bg_rect.y + 3))

        if self.bg_image:
            scaled_bg = pygame.transform.scale(self.bg_image, (scaled_width, scaled_height))
            full_surf.blit(scaled_bg, (x, y))
        else:
            pygame.draw.rect(full_surf, (30, 30, 30), bg_rect, border_radius=8)

        for item in sorted(self.bag.contents, key=lambda i: i.pos[1]):
            if item.state == "bagged":
                item.draw(full_surf, screensize, None, None, 1)
                for p in item.particles:
                    p.draw(full_surf)

        # DEBUG: bag bounds
        surface.blit(full_surf, (0, 0))

    def handle_drop(self, item, mouse_pos, item_manager):
        in_bag = self.is_hovered(mouse_pos)
        if not in_bag and item in self.bag.contents:
            # 👋 Remove from bag
            success = self.try_remove_item(item, item_manager)
            if success:
                s = getattr(item, "default_scale", (1,1))
                item.trick = TrickAnimation([
                    {"time": 0.0, "scale": (s[0]/2, s[1]/2)},
                    {"time": 0.15, "scale": s},
                ])
                item.trick.on_complete = None
                item.trick.reset()
            return success

        elif in_bag and item not in self.bag.contents:
            # 💼 Add to bag
            success = self.try_add_item(item)
            if success:
                s = getattr(item, "default_scale", (1,1))
                item.trick = TrickAnimation([
                    {"time": 0.0, "scale": s},
                    {"time": 0.15, "scale": (s[0]/2, s[1]/2)},
                ])
                item.trick.on_complete = lambda item: item_manager.remove_item(item.uuid)
                item.trick.reset()
            return success

        return False
