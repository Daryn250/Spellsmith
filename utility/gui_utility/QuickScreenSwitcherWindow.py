import pygame
from utility.item_utility.trickAnimation import TrickAnimation

class QuickScreenSwitcherWindow:
    def __init__(self, screen_names, on_select_callback, screen):
        self.screen_names = screen_names  # list of (formatted_name, internal_name)
        self.on_select_callback = on_select_callback
        self.pos = (0, 0)
        self.width = 140
        self.entry_height = 30
        self.font = pygame.font.Font(None, 26)
        self.hover_index = -1
        self.visible = False

        self.mainScreen = screen

        # Scroll values
        self.scroll_offset = 0.0
        self.scroll_velocity = 0.0
        self.max_visible = 5
        self.scroll_area_height = self.entry_height * self.max_visible

    def update(self, dt, mouse_pos):
        if not self.visible:
            return

        # Smooth scroll deceleration
        self.scroll_offset += self.scroll_velocity
        self.scroll_velocity *= 0.85

        max_scroll = max(0, len(self.screen_names) * self.entry_height - self.scroll_area_height)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        mx, my = mouse_pos
        x, y = self.pos
        self.hover_index = -1

        for i, (formatted, _) in enumerate(self.screen_names):
            draw_y = y + i * self.entry_height - self.scroll_offset
            entry_rect = pygame.Rect(x, draw_y, self.width, self.entry_height)
            if entry_rect.collidepoint(mx, my):
                self.hover_index = i
                break

    def handle_event(self, event):
        if not self.visible:
            return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # scroll up
                self.scroll_velocity -= 5
            elif event.button == 5:  # scroll down
                self.scroll_velocity += 5
            elif event.button == 1:  # left click
                if self.hover_index is not None and 0 <= self.hover_index < len(self.screen_names):
                    selected = self.screen_names[self.hover_index][1]
                    self.on_select_callback(self.mainScreen, selected)

    def draw(self, surface):
        if not self.visible:
            return

        x, y = self.pos
        total_items = len(self.screen_names)
        show_scrollbar = total_items > self.max_visible

        clip_rect = pygame.Rect(x, y, self.width, self.scroll_area_height)
        surface.set_clip(clip_rect)

        for i, (formatted, _) in enumerate(self.screen_names):
            draw_y = y + i * self.entry_height - self.scroll_offset
            rect = pygame.Rect(x, draw_y, self.width, self.entry_height)
            color = (180, 180, 180) if i == self.hover_index else (50, 50, 50)
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 1)

            text = self.font.render(formatted, True, (255, 255, 255))
            surface.blit(text, (x + 10, draw_y + 5))

        surface.set_clip(None)

        # ----- Draw Scrollbar -----
        if show_scrollbar:
            scrollbar_x = x + self.width - 6
            scrollbar_y = y
            scrollbar_width = 4
            scrollbar_height = self.scroll_area_height

            # Height proportional to visible range
            content_height = total_items * self.entry_height
            thumb_height = max(20, (self.scroll_area_height / content_height) * self.scroll_area_height)
            scroll_ratio = self.scroll_offset / (content_height - self.scroll_area_height)
            thumb_y = y + scroll_ratio * (self.scroll_area_height - thumb_height)

            pygame.draw.rect(surface, (30, 30, 30), (scrollbar_x, scrollbar_y, scrollbar_width, scrollbar_height))  # background
            pygame.draw.rect(surface, (255, 255, 255), (scrollbar_x, thumb_y, scrollbar_width, thumb_height))  # thumb
