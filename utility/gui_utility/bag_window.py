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

        # Add physics/logic update for bag contents
        if self.animation.finished:
            for item in self.bag.contents:
                item.update(None, gui_manager, virtual_size, bounds=self.get_bounds_rect(), dt=dt)
                for p in item.particles:
                    p.update()
                item.particles = [p for p in item.particles if p.is_alive()]

    def get_bounds_rect(self):
        x, y = self.pos
        width = int(200 * self.scale[0])
        height = int(200 * self.scale[1])
        return pygame.Rect(x, y, width, height)


    def try_add_item(self, item):
        if "unbaggable" not in item.flags:
            if not item in self.bag.contents:
                if len(self.bag.contents) < self.max_items:
                    self.bag.contents.append(item)
                    item.state = "bagged"
                    return True
                else:
                    item.vx = 4  # Throw outwards
                    item.vy = -3
                    item.state = "free"
                    return False
        
    def try_remove_item(self, item, item_manager):
        """Remove item from bag and hand it over to item_manager."""
        if not item in item_manager.items:
            if item in self.bag.contents:
                item_manager.add_item(item)
                item.state = "free"
                item.vx = 0
                item.vy = -2  # small upward hop for visual feedback
                return True
        return False


    def is_hovered(self, mouse_pos):
        x, y = self.pos
        width = int(200 * self.scale[0])
        height = int(200 * self.scale[1])
        rect = pygame.Rect(x, y, width, height)
        return rect.collidepoint(mouse_pos)


    def draw(self, surface, topleft, mouse, screensize, dragged_item=None):

        full_surf = pygame.Surface(screensize, pygame.SRCALPHA) # makes a surface ontop of everything to draw to
        
        # Update animated position
        if self.animation:
            x, y = self.pos
        else:
            x, y = topleft
            self.pos = topleft

        base_width, base_height = 200, 200
        scaled_width = int(base_width * self.scale[0])
        scaled_height = int(base_height * self.scale[1])
        bg_rect = pygame.Rect(x, y, scaled_width, scaled_height)

        # Draw shadow
        shadow = pygame.Surface((bg_rect.width + 6, bg_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=8)
        full_surf.blit(shadow, (bg_rect.x + 3, bg_rect.y + 3))

        # Draw background
        if self.bg_image:
            scaled_bg = pygame.transform.scale(self.bg_image, (scaled_width, scaled_height))
            full_surf.blit(scaled_bg, (x, y))
        else:
            pygame.draw.rect(full_surf, (30, 30, 30), bg_rect, border_radius=8)
        # Draw items in the bag
        for item in sorted(self.bag.contents, key=lambda i: i.pos[1]):
            item.draw(full_surf, screensize, None, None, 1)
            for p in item.particles:
                p.draw(full_surf)
        
        surface.blit(full_surf, (0,0))
                



    def handle_drop(self, item, mouse_pos, item_manager):
        if not self.is_hovered(mouse_pos):
            success = self.try_remove_item(item, item_manager)
            if success:
                # Create animation with on_complete callback at init
                
                item.trick = TrickAnimation([
                    {"time": 0.0, "scale": (0.5,0.5)},
                    {"time": 0.15, "scale": (1,1)},
                ])
                item.trick.on_complete=lambda item: self.bag.contents.remove(item)
                item.trick.reset()  # Resets internal time/index to properly detect on_complete

                return True
            else:
                return False
        else:

            success = self.try_add_item(item)
            if success:
                # Create animation with on_complete callback at init
                
                item.trick = TrickAnimation([
                    {"time": 0.0, "scale": (1,1)},
                    {"time": 0.15, "scale": (0.5,0.5)},
                ])
                item.trick.on_complete=lambda item: item_manager.remove_item(item.uuid)
                item.trick.reset()  # Resets internal time/index to properly detect on_complete
                
                return True
            else:
                # Rejected — throw out
                item.vx = 4
                item.vy = -3
                return False




