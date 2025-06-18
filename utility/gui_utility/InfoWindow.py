import pygame

class InfoWindow:
    def __init__(self, anchor, title, description, position, image_path=None, size=(150, 180), padding=8):
        self.anchor_item = anchor
        self.title = title
        self.description = description
        self.image_path = image_path
        self.pos = position
        self.size = size  # Final display size (width only matters initially)
        self.padding = padding


        # touch these and the code breaks not even gonna lie
        self.display_width, self.display_height = size
        self.render_width = self.display_width
        self.scale = 1
        #

        self.cached_surface = None
        self.cached_display_size = None
        self.cached_total_height = None
        self.needs_redraw = True

        # Load pixel fonts
        self.font_title = pygame.font.Font("assets/spellsmithy.ttf", 20 )
        self.font_content = pygame.font.Font("assets/spellsmithy.ttf", 16 )

        # Load optional image
        self.image = None
        if self.image_path:
            raw_img = pygame.image.load(self.image_path)
            self.image = raw_img

    def update_position(self, offset=None):
        if offset is None:
            offset = (20, 20)
        mx, my = self.anchor_item.pos
        self.pos = (mx + offset[0], my + offset[1])

    def draw(self, screen):
        if not self.needs_redraw:
            screen.blit(self.cached_surface, (round(self.pos[0]), round(self.pos[1])))
            return

        x = int(self.padding * self.scale)
        y = int(self.padding * self.scale)
        max_width = self.render_width - 2 * x

        title_surf = self.font_title.render(self.title, False, (255, 255, 255))
        title_height = title_surf.get_height()
        y += title_height + int(self.padding * self.scale)

        words = self.description.split(' ')
        line = ''
        description_surfs = []
        for word in words:
            test_line = line + word + ' '
            test_surf = self.font_content.render(test_line, False, (220, 220, 220))
            if test_surf.get_width() > max_width:
                final_surf = self.font_content.render(line, False, (220, 220, 220))
                description_surfs.append(final_surf)
                y += final_surf.get_height() + int(2 * self.scale)
                line = word + ' '
            else:
                line = test_line
        if line:
            final_surf = self.font_content.render(line, False, (220, 220, 220))
            description_surfs.append(final_surf)
            y += final_surf.get_height() + int(2 * self.scale)

        image_height = 0
        if self.image:
            img_w, img_h = self.image.get_size()
            scale_factor = max_width / img_w
            image_height = int(img_h * scale_factor)
            y += image_height + int(self.padding * self.scale)

        total_height = y + int(self.padding * self.scale)
        self.cached_total_height = total_height

        render_size = (self.render_width, total_height)
        surface = pygame.Surface(render_size)
        surface.set_alpha(None)
        surface.fill((15, 15, 15))
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 3)

        # Re-draw everything to the cached surface
        y = int(self.padding * self.scale)
        surface.blit(title_surf, (x, y))
        y += title_height + int(self.padding * self.scale)
        for surf in description_surfs:
            surface.blit(surf, (x, y))
            y += surf.get_height() + int(2 * self.scale)
        if self.image:
            scaled_img = pygame.transform.scale(self.image, (max_width, image_height))
            surface.blit(scaled_img, (x, y))
            y += image_height + int(self.padding * self.scale)

        final_height = total_height // self.scale
        if final_height % 2 != 0:
            final_height += 1
        final_display_size = (self.size[0], final_height)
        self.cached_display_size = final_display_size

        self.cached_surface = pygame.transform.scale(surface, final_display_size)
        screen.blit(self.cached_surface, (round(self.pos[0]), round(self.pos[1])))

        self.needs_redraw = False



