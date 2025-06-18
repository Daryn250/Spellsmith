import pygame

class InfoWindow:
    def __init__(self, anchor, title, description, position, image_path=None, size=(150, 180), padding=8, scale=2):
        self.anchor_item = anchor
        self.title = title
        self.description = description
        self.image_path = image_path
        self.pos = position
        self.size = size  # Final display size (width only matters initially)
        self.padding = padding
        self.scale = scale
        self.render_width = size[0] * scale

        # Load pixel fonts
        self.font_title = pygame.font.Font("assets/spellsmithy.ttf", 20 * scale)
        self.font_content = pygame.font.Font("assets/spellsmithy.ttf", 16 * scale)

        # Load optional image
        self.image = None
        if self.image_path:
            raw_img = pygame.image.load(self.image_path).convert_alpha()
            self.image = raw_img

    def update_position(self, offset=None):
        if offset is None:
            offset = (20, 20)
        mx, my = self.anchor_item.pos
        self.pos = (mx + offset[0], my + offset[1])

    def draw(self, screen):
        x = self.padding * self.scale
        y = self.padding * self.scale
        max_width = self.render_width - 2 * x

        # Render title to measure space
        title_surf = self.font_title.render(self.title, False, (255, 255, 255))
        y += title_surf.get_height() + self.padding * self.scale

        # Measure wrapped description
        words = self.description.split(' ')
        line = ''
        description_surfs = []
        for word in words:
            test_line = line + word + ' '
            test_surf = self.font_content.render(test_line, False, (220, 220, 220))
            if test_surf.get_width() > max_width:
                description_surfs.append(self.font_content.render(line, False, (220, 220, 220)))
                y += description_surfs[-1].get_height() + 2 * self.scale
                line = word + ' '
            else:
                line = test_line
        if line:
            description_surfs.append(self.font_content.render(line, False, (220, 220, 220)))
            y += description_surfs[-1].get_height() + 2 * self.scale

        # Add space for image if present
        if self.image:
            img_w, img_h = self.image.get_size()
            scale_factor = max_width / img_w
            scaled_height = int(img_h * scale_factor)
            y += scaled_height + self.padding * self.scale

        # Add final bottom padding
        total_height = y + self.padding * self.scale

        # Now create surface based on actual size
        render_size = (self.render_width, total_height)
        surface = pygame.Surface(render_size, pygame.SRCALPHA)

        # Fill background and draw border
        surface.fill((0, 0, 0, 200))
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 3)

        # Reset draw y
        y = self.padding * self.scale
        surface.blit(title_surf, (x, y))
        y += title_surf.get_height() + self.padding * self.scale

        for surf in description_surfs:
            surface.blit(surf, (x, y))
            y += surf.get_height() + 2 * self.scale

        # Draw image
        if self.image:
            img_w, img_h = self.image.get_size()
            scale_factor = max_width / img_w
            scaled_height = int(img_h * scale_factor)
            scaled_img = pygame.transform.scale(self.image, (max_width, scaled_height))
            surface.blit(scaled_img, (x, y))
            y += scaled_height + self.padding * self.scale

        # Scale down and blit to screen
        final_display_size = (self.size[0], total_height // self.scale)
        scaled_surface = pygame.transform.scale(surface, final_display_size)
        screen.blit(scaled_surface, self.pos)
