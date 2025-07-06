import pygame
import os
from utility.settingsManager import get_font

class CountdownMiniGame:
    def __init__(self, virtual_size, duration=3000, on_finish_callback=None, font_path=get_font(), font_size=48, item = {}):
        self.virtual_size = virtual_size
        self.duration = duration
        self.timer = duration
        self.finished = False
        self.on_finish_callback = on_finish_callback

        self.item = item

        # Load font
        if os.path.exists(font_path):
            self.font = pygame.font.Font(font_path, font_size)
        else:
            self.font = pygame.font.SysFont("arial", font_size)  # fallback

    def update(self, dt, virtual_mouse):
        if self.finished:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.timer = 0
            self.finished = True
            if self.on_finish_callback:
                self.on_finish_callback()

    def handle_event(self, event, mouse_pos):
        pass  # No interaction needed

    def draw(self, surface, clip_rect=None):
        if self.finished:
            return

        prev_clip = surface.get_clip()
        if clip_rect:
            surface.set_clip(clip_rect)

        # === Draw time bar ===
        bar_height = 10
        bar_margin = 5
        bar_width = clip_rect.width - 2 * bar_margin
        x = clip_rect.left + bar_margin
        y = clip_rect.bottom - bar_height - bar_margin

        remaining_ratio = max(0.0, self.timer / self.duration)
        current_width = int(bar_width * remaining_ratio)

        pygame.draw.rect(surface, (80, 80, 80), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 200, 0), (x, y, current_width, bar_height))

        # === Draw numeric countdown ===
        seconds_remaining = max(0, int(self.timer / 1000))
        countdown_surface = self.font.render(str(seconds_remaining + 1), True, (255, 255, 255))
        countdown_rect = countdown_surface.get_rect(center=clip_rect.center)
        surface.blit(countdown_surface, countdown_rect)

        # === Draw title of what you're making ===
        if hasattr(self, "item") and isinstance(self.item, dict):
            name = self.item.get("name", "???")
            title_text = name
            title_surface = self.font.render(title_text, True, (255, 255, 100))
            title_rect = title_surface.get_rect(midbottom=(clip_rect.centerx, countdown_rect.top - 10))
            surface.blit(title_surface, title_rect)

        surface.set_clip(prev_clip)


    def get_result(self):
        return {
        }
