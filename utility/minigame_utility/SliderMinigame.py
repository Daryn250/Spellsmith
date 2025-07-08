import pygame
import random
import math
from utility.particle import make_particles_presets  # if not already imported
from utility.settingsManager import get_font


class SliderMinigame:
    def __init__(self, virtual_size, difficulty, clip_rect, screen, on_finish=None):
        self.font = pygame.font.Font(get_font(), 16)
        self.clip_rect = clip_rect
        self.screen = screen
        self.on_finish_callback = on_finish
        self.difficulty = difficulty

        self.target = random.randint(1, 100)
        self.timer = max(4000, 10000 - difficulty * 750)
        self.max_timer = self.timer
        self.finished = False
        self.success = False

        self.particles = []
        self.locked = False

        self.rough = 0
        self.fine = 0
        self.lockdt = 1000000000000000000000000

        self.slider_width = 240
        self.slider_height = 30
        self.slider_spacing = 60  # increased spacing
        self.slider_bar_color = (120, 120, 120)
        self.slider_fill_color = (0, 200, 255)

        cx = clip_rect.centerx
        bottom = clip_rect.bottom - 60  # moved down

        self.slider_rects = [
            pygame.Rect(cx - self.slider_width // 2, bottom - self.slider_spacing, self.slider_width, self.slider_height),  # Rough
            pygame.Rect(cx - self.slider_width // 2, bottom, self.slider_width, self.slider_height),                        # Fine
        ]

        self.hitboxes = [r.inflate(0, 10) for r in self.slider_rects]
        self.dragging = [False, False]

    def update(self, dt, virtual_mouse):
        if self.finished:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.finish()

        # Update particles
        for p in self.particles:
            p.update(dt)
        self.particles = [p for p in self.particles if p.is_alive()]

        # Auto-lock if correct number hit
        if not self.locked and self.total_value() == self.target:
            self.locked = True
            self.spawn_stars()
            self.lockdt = self.timer
        if self.timer - self.lockdt >= 1000:
            self.finish()

    def handle_event(self, event, virtual_mouse):
        if self.finished or self.locked:
            return

        mx, my = virtual_mouse

        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, hitbox in enumerate(self.hitboxes):
                if hitbox.collidepoint(mx, my):
                    self.dragging[i] = True

        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = [False, False]

        if event.type == pygame.MOUSEMOTION:
            for i in range(2):
                if self.dragging[i]:
                    ratio = (mx - self.slider_rects[i].left) / self.slider_width
                    ratio = max(0, min(1, ratio))
                    if i == 0:
                        self.rough = round(ratio * 10) * 10
                    else:
                        self.fine = round(ratio * 10)

    def draw(self, surface, clip_rect):
        surface.set_clip(clip_rect)

        # Number line
        left_x = clip_rect.left + 10
        right_x = clip_rect.right - 10
        pygame.draw.line(surface, (255, 255, 255), (left_x, clip_rect.top + 50), (right_x, clip_rect.top + 50), 2)

        for i in range(0, 101, 10):
            x = left_x + (right_x - left_x) * (i / 100)
            pygame.draw.line(surface, (200, 200, 200), (x, clip_rect.top + 45), (x, clip_rect.top + 55), 1)
            label = self.font.render(str(i), True, (255, 255, 255))
            surface.blit(label, (x - label.get_width() // 2, clip_rect.top + 60))

        # Arrows
        def draw_arrow(x, color, y=clip_rect.top + 40):
            pygame.draw.polygon(surface, color, [(x, y), (x - 5, y - 10), (x + 5, y - 10)])

        target_x = left_x + (right_x - left_x) * (self.target / 100)
        draw_arrow(target_x, (255, 255, 0))  # Target arrow

        current_total = self.total_value()
        current_x = left_x + (right_x - left_x) * (current_total / 100)
        draw_arrow(current_x, (0, 255, 255), clip_rect.top + 35)  # Current total arrow

        # Target label
        label = self.font.render(f"Target: {self.target}", True, (255, 255, 0))
        surface.blit(label, (clip_rect.centerx - label.get_width() // 2, clip_rect.top + 10))

        # Sliders
        labels = ["Rough", "Fine"]
        values = [self.rough, self.fine]
        maxes = [100, 10]

        for i in range(2):
            rect = self.slider_rects[i]
            max_val = maxes[i]
            pygame.draw.rect(surface, self.slider_bar_color, rect)
            fill_width = (values[i] / max_val) * self.slider_width
            pygame.draw.rect(surface, self.slider_fill_color, (rect.left, rect.top, fill_width, rect.height))
            name = self.font.render(f"{labels[i]}: {values[i]}", True, (255, 255, 255))
            surface.blit(name, (rect.left, rect.top - 24))

        # Total
        result_label = self.font.render(f"Total: {current_total}", True, (255, 255, 255))
        surface.blit(result_label, (clip_rect.centerx - result_label.get_width() // 2, clip_rect.bottom - 30))

        # Timer
        time_ratio = self.timer / self.max_timer
        pygame.draw.rect(surface, (50, 50, 50), (clip_rect.left + 10, clip_rect.top + 30, 100, 5))
        pygame.draw.rect(surface, (0, 255, 0), (clip_rect.left + 10, clip_rect.top + 30, int(100 * time_ratio), 5))

        # Particles
        for p in self.particles:
            p.draw(surface)

        surface.set_clip(None)

    def total_value(self):
        return self.rough + self.fine

    def finish(self):
        self.finished = True
        self.success = self.total_value() == self.target
        if self.on_finish_callback:
            self.on_finish_callback(self.get_result())

    def get_result(self):
        total = self.total_value()
        delta = abs(self.target - total)
        if delta == 0:
            grade = "perfect"
        elif delta <= 2:
            grade = "good"
        elif delta <= 5:
            grade = "ok"
        else:
            grade = "miss"

        return {"success": self.success, 
                "target": self.target, 
                "value": total, 
                "grade": grade, 
                "hits": [grade],
                "game_name":"Balancing"}

    def spawn_stars(self):
        total = self.total_value()
        text = self.font.render(f"Total: {total}", True, (255, 255, 255))
        text_x = self.clip_rect.centerx - text.get_width() // 2
        text_y = self.clip_rect.bottom - 30
        center = (text_x + text.get_width() // 2, text_y + text.get_height() // 2)

        self.particles.extend(make_particles_presets["stars"](center, count=8))
