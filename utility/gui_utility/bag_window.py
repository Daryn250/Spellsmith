import pygame

class BagWindow:
    def __init__(self, bag_manager):
        self.bag = bag_manager
        self.scroll_y = 0.0
        self.max_scroll = 0.0  # computed dynamically
        self.scroll_vy= 0.0
        self.scroll_speed = 3  # adjust scroll strength per mousewheel tick

        self.animation = None
        self.original_pos = (0, 0)  # set during draw or show
        self.scale = [1.0, 1.0]     # used for rendering
        self.pos = (0, 0)           # updated by animation


        self.columns = 5
        self.visible_rows = 5
        self.slot_size = 36  # slightly smaller
        self.spacing = 4
        self.bg_padding = 8  # margin around grid

        self.hovered = False

        self.bg_image = pygame.image.load("assets/gui/bag/bag_window_bg.png").convert_alpha()

    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.scroll_vy -= event.y * self.scroll_speed

            

    def update(self, virtual_size, dt):
        # Calculate scroll bounds every update
        total_slots = len(self.bag.slots)
        rows = (total_slots + self.columns - 1) // self.columns
        total_height = rows * (self.slot_size + self.spacing) - self.spacing
        visible_height = self.visible_rows * (self.slot_size + self.spacing) - self.spacing
        self.max_scroll = max(0, total_height - visible_height)

        self.scroll_y += self.scroll_vy
        self.scroll_vy /= 1.3
        self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))


        if self.animation:
            self.animation.update(dt, self, virtual_size)




    def draw(self, surface, topleft):
    # Use the animated offset *relative to* the topleft position
        if self.animation:
            x, y = self.pos  # animated position
        else:
            x, y = topleft
            self.pos = topleft

        total_slots = len(self.bag.slots)
        rows = (total_slots + self.columns - 1) // self.columns
        total_height = rows * (self.slot_size + self.spacing) - self.spacing
        visible_height = self.visible_rows * (self.slot_size + self.spacing) - self.spacing


        total_width = self.columns * (self.slot_size + self.spacing) - self.spacing
        bg_rect = pygame.Rect(x, y, total_width + self.bg_padding * 2, visible_height + self.bg_padding * 2)

            # Apply scale for animation
        scaled_width = int((total_width + self.bg_padding * 2) * self.scale[0])
        scaled_height = int((visible_height + self.bg_padding * 2) * self.scale[1])
        bg_rect = pygame.Rect(x, y, scaled_width, scaled_height)

        # Shadow
        shadow = pygame.Surface((bg_rect.width + 6, bg_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=8)
        surface.blit(shadow, (bg_rect.x + 3, bg_rect.y + 3))

        # Background (flat color or image)
        if self.bg_image:
            scaled_bg = pygame.transform.scale(self.bg_image, (bg_rect.width, bg_rect.height))
            surface.blit(scaled_bg, (x, y))
        else:
            pygame.draw.rect(surface, (30, 30, 30), bg_rect, border_radius=8)


        # Set clipping so items outside are not drawn
        previous_clip = surface.get_clip()
        surface.set_clip(bg_rect)

        for index, item in enumerate(self.bag.slots):
            row = index // self.columns
            col = index % self.columns

            slot_x = x + self.bg_padding + col * (self.slot_size + self.spacing)
            slot_y = y + self.bg_padding + row * (self.slot_size + self.spacing) - int(self.scroll_y)

            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_size, self.slot_size)

            if bg_rect.colliderect(slot_rect):
                pygame.draw.rect(surface, (60, 23, 15), slot_rect, border_radius=6)
                if item:
                    # draw item image here
                    pass

        surface.set_clip(previous_clip)

        # === Scrollbar ===
        if self.max_scroll > 0:  # only draw scrollbar if content is scrollable
            scrollbar_width = 3
            track_color = (20, 20, 20, 180)
            handle_color = (180, 180, 180)

            # Scrollbar track
            scrollbar_x = bg_rect.right - scrollbar_width - 4  # inset from edge
            scrollbar_y = y + self.bg_padding
            scrollbar_height = visible_height

            pygame.draw.rect(
                surface,
                track_color,
                (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height),
                border_radius=3
            )

            # Scrollbar handle
            handle_height = max(20, scrollbar_height * (visible_height / (total_height + 1)))
            handle_y = scrollbar_y + (self.scroll_y / self.max_scroll) * (scrollbar_height - handle_height)

            pygame.draw.rect(
                surface,
                handle_color,
                (scrollbar_x, handle_y, scrollbar_width, handle_height),
                border_radius=3
            )



