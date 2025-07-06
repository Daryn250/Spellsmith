import pygame
import math
import random

class QuenchMinigame:
    def __init__(self, virtual_size, difficulty, clip_rect, screen, item_image=None, on_finish=None):
        self.font = pygame.font.Font("assets/GothicByte.ttf", 15)
        self.virtual_size = virtual_size
        self.clip_rect = clip_rect
        self.screen = screen
        self.difficulty = difficulty
        self.item_image = item_image
        self.on_finish_callback = on_finish

        self.max_timer = 15000
        self.timer = self.max_timer

        self.temp = 100.0
        self.max_temp = 100.0
        self.warp = 0.0
        self.max_warp = 100.0
        self.warp_danger_delay = 1500 - difficulty * 100
        self.dip_time = 0

        self.is_dipping = False
        self.finished = False
        self.success = False
        self.particles = []

        self.cool_rate = 0.0008 + difficulty * 0.0001
        self.warp_rate = 0.0005 + difficulty * 0.0001
        self.recover_rate = 0.00004

        self.shake_offset = 0
        self.shake_timer = 0

        # Layout
        self.bar_spacing = 30
        self.bar_width = 30

        total_width = self.bar_width * 3 + self.bar_spacing * 2 + 80  # 3 bars + 2 spacings + dip button
        start_x = clip_rect.centerx - total_width // 2
        bar_height = clip_rect.height - 80

        self.temp_bar = pygame.Rect(start_x, clip_rect.top + 40, self.bar_width, bar_height)
        self.warp_bar = pygame.Rect(self.temp_bar.right + self.bar_spacing, self.temp_bar.top, self.bar_width, bar_height)
        self.danger_bar = pygame.Rect(self.warp_bar.right + self.bar_spacing, self.temp_bar.top, self.bar_width, bar_height)
        self.dip_button = pygame.Rect(self.danger_bar.right + self.bar_spacing, clip_rect.bottom - 60, 80, 40)

    def update(self, dt, virtual_mouse):
        if self.finished:
            return

        if self.is_dipping:
            self.dip_time += dt
            self.temp = max(0, self.temp - self.cool_rate * dt * math.sqrt(self.temp))

            dip_sec = self.dip_time / 1000
            if dip_sec >= 4:  # only add warp if in red segment
                self.warp += self.warp_rate * 3 * dt * math.sqrt(dip_sec / 2)  # faster warp
                self.warp = min(self.max_warp, self.warp)
                self.shake_timer = 100
        else:
            self.dip_time = 0
            self.warp = max(0, self.warp - self.recover_rate * dt)

        if self.shake_timer > 0:
            self.shake_offset = random.randint(-2, 2)
            self.shake_timer -= dt
        else:
            self.shake_offset = 0

        self.timer -= dt
        if self.timer <= 0 or self.warp >= self.max_warp:
            self.finish(success=False)
        elif self.temp <= 0:
            self.finish(success=True)

    def handle_event(self, event, virtual_mouse):
        if self.finished:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.dip_button.collidepoint(virtual_mouse):
                self.is_dipping = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.is_dipping = False

    def draw(self, surface, clip_rect):
        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        # Temp bar
        temp_ratio = self.temp / self.max_temp
        pygame.draw.rect(surface, (50, 50, 50), self.temp_bar)
        pygame.draw.rect(surface, (0, 0, 255), (
            self.temp_bar.left,
            self.temp_bar.bottom - self.temp_bar.height * temp_ratio,
            self.temp_bar.width,
            self.temp_bar.height * temp_ratio
        ))
        temp_label = self.font.render("Temp", False, (255, 255, 255))
        surface.blit(temp_label, (self.temp_bar.left, self.temp_bar.bottom + 5))

        # Warp bar with shake
        warp_ratio = self.warp / self.max_warp
        warp_x = self.warp_bar.left + self.shake_offset
        pygame.draw.rect(surface, (80, 80, 80), (warp_x, self.warp_bar.top, self.warp_bar.width, self.warp_bar.height))
        pygame.draw.rect(surface, (200, 0, 0), (
            warp_x,
            self.warp_bar.bottom - self.warp_bar.height * warp_ratio,
            self.warp_bar.width,
            self.warp_bar.height * warp_ratio
        ))
        warp_label = self.font.render("Warp", False, (255, 255, 255))
        surface.blit(warp_label, (warp_x - 5, self.warp_bar.bottom + 5))

        # Dynamic danger indicator bar
        segments = 3
        segment_height = self.danger_bar.height // segments
        dip_time_sec = self.dip_time / 1000
        for i in range(segments):
            seg_y = self.danger_bar.top + i * segment_height
            seg_color = [(0,255,0), (255,255,0), (255,0,0)][i]
            threshold = [1, 2.5, 4][i]  # seconds thresholds
            if dip_time_sec >= threshold:
                pygame.draw.rect(surface, seg_color, (self.danger_bar.left, seg_y, self.danger_bar.width, segment_height))

        # Timer
        time_ratio = max(0, self.timer / self.max_timer)
        pygame.draw.rect(surface, (100, 100, 100), (clip_rect.left + 10, clip_rect.top + 10, 150, 10))
        pygame.draw.rect(surface, (0, 255, 0), (clip_rect.left + 10, clip_rect.top + 10, int(150 * time_ratio), 10))

        # Dip button
        pygame.draw.rect(surface, (180, 180, 255), self.dip_button)
        label = self.font.render("Dip", False, (0, 0, 0))
        surface.blit(label, label.get_rect(center=self.dip_button.center))

        if self.item_image:
            img_rect = self.item_image.get_rect(center=clip_rect.center)
            surface.blit(self.item_image, img_rect)

        for p in self.particles:
            p.draw(surface)

        surface.set_clip(prev_clip)

    def finish(self, success):
        self.finished = True
        self.success = success
        if self.on_finish_callback:
            self.on_finish_callback(self.get_result())

    def get_result(self):
        max_score = self.max_temp + self.max_warp
        temp_remaining = self.temp
        warp_penalty = self.warp
        score_ratio = (max_score - (temp_remaining+(warp_penalty*1.5)))/max_score
        score_ratio = max(0.0, min(1.0, score_ratio))

        if score_ratio >= 0.9:
            grade = "perfect"
        elif score_ratio >= 0.7:
            grade = "good"
        elif score_ratio >= 0.5:
            grade = "ok"
        else:
            grade = "miss"

        return {
            "success": self.success,
            "final_temp": self.temp,
            "warp": self.warp,
            "time_remaining": max(0, self.timer / 1000),
            "score": score_ratio,
            "hits": [grade]
        }



