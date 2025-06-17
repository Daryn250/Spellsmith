import pygame

class InfoWindow:
    def __init__(self, title, data, position, size=(120, 80), padding=8):
        """
        title: str - the title text shown at the top
        data: dict - key/value pairs to show inside
        position: tuple - (x, y) position above charm
        size: tuple - (width, height)
        """
        self.title = title
        self.data = data
        self.pos = position
        self.size = size
        self.padding = padding

        self.font_title = pygame.font.SysFont(None, 20)
        self.font_content = pygame.font.SysFont(None, 18)

        self.surface = pygame.Surface(self.size, pygame.SRCALPHA)

    def draw(self, screen):
        self.surface.fill((0, 0, 0, 200))  # semi-transparent background

        # Draw white border
        pygame.draw.rect(self.surface, (255, 255, 255), self.surface.get_rect(), 2)

        # Draw title
        title_surf = self.font_title.render(self.title, True, (255, 255, 255))
        self.surface.blit(title_surf, (self.padding, self.padding))

        # Draw data
        y = self.padding + title_surf.get_height() + 4
        for key, value in self.data.items():
            line = f"{key}: {value}"
            text_surf = self.font_content.render(line, True, (220, 220, 220))
            self.surface.blit(text_surf, (self.padding, y))
            y += text_surf.get_height() + 2

        # Blit to screen
        screen.blit(self.surface, self.pos)
