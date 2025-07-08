import pygame
import random
import math
from utility.particle import make_particles_presets
from utility.settingsManager import get_font
class HeatTreatMinigame:
    def __init__(self, virtual_size, difficulty, clip_rect, screen, on_finish=None):
        self.font = pygame.font.Font(get_font(), 15)
        self.virtual_size = virtual_size
        self.clip_rect = clip_rect
        self.screen = screen
        self.on_finish_callback = on_finish
        self.difficulty = difficulty

        self.star_emit_timer = 0

        self.timer = 6000
        self.max_timer = self.timer

        self.temp = 0.0
        self.max_temp = 100.0
        self.target_min = random.uniform(60, 70)
        self.target_max = self.target_min + 10

        self.temp_fall_rate = 0.03 + 0.001 * difficulty
        self.billows_power = 7 + difficulty
        self.overheat_flash_timer = 0

        self.particles = []
        self.finished = False
        self.hits = []

        self.progress = 0.0  # New progress bar value
        self.max_progress = 1000  # arbitrary target fill level

        


        # Layout
        center_x = clip_rect.centerx
        self.bar_rect = pygame.Rect(center_x - 15, clip_rect.top + 40, 30, clip_rect.height - 80)
        self.progress_bar_rect = pygame.Rect(self.bar_rect.left - 20, self.bar_rect.top, 10, self.bar_rect.height)


        # After defining self.bar_rect and self.progress_bar_rect

        # Load and scale billow images
        self.billow_img_closed = pygame.transform.scale_by(
            pygame.image.load("assets/screens/anvil/billows/billows2.png").convert_alpha(), 2.0)
        self.billow_img_open = pygame.transform.scale_by(
            pygame.image.load("assets/screens/anvil/billows/billows1.png").convert_alpha(), 2.0)

        self.billow_state = "open"  # start open

        # Position billows to the right of the bar
        self.billow_rect = self.billow_img_closed.get_rect(
            topleft=(self.bar_rect.right + 30, self.bar_rect.bottom - self.billow_img_closed.get_height()))


    def update(self, dt, virtual_mouse):
        if self.finished:
            return
        


        self.temp = max(0.0, self.temp - self.temp_fall_rate * dt)

        if self.target_min <= self.temp <= self.target_max:
            self.progress = min(self.max_progress, self.progress + dt)
            self.star_emit_timer += dt
            if self.star_emit_timer >= 1000:
                self.star_emit_timer = 0
                # Emit star particles inside the green zone
                for _ in range(3):  # Number of stars per second
                    x = random.randint(self.bar_rect.left, self.bar_rect.right)
                    zone_top = self.bar_rect.top + self.bar_rect.height * (1 - self.target_max / self.max_temp)
                    zone_bottom = self.bar_rect.top + self.bar_rect.height * (1 - self.target_min / self.max_temp)
                    y = random.randint(int(zone_top), int(zone_bottom))
                    self.particles.extend(make_particles_presets["stars"]((x, y)))
        else:
            self.progress = max(0, self.progress - (dt / 5))
            self.star_emit_timer = 0  # Reset if out of range


        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]

        if self.overheat_flash_timer > 0:
            self.overheat_flash_timer -= dt

        self.timer -= dt
        if self.timer <= 0:
            self.finish()

    def handle_event(self, event, virtual_mouse):
        if self.finished:
            return

        if self.billow_rect.collidepoint(virtual_mouse):
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.billow_state = "closed"  # Pressed = closed
                if self.temp >= self.max_temp:
                    self.screen.start_shake(10, 4)
                    self.overheat_flash_timer = 250
                else:
                    self.temp = min(self.max_temp, self.temp + self.billows_power)
                    self.screen.start_shake(2, 1)

                    # Emit from left center
                    emit_x = self.billow_rect.left
                    emit_y = self.billow_rect.top + self.billow_rect.height // 2
                    self.particles.extend(make_particles_presets["smoke"]((emit_x, emit_y)))

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.billow_state = "open"  # Released = open



    def draw(self, surface, clip_rect):
        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        if self.overheat_flash_timer > 0:
            overlay = pygame.Surface((clip_rect.width, clip_rect.height), pygame.SRCALPHA)
            overlay.fill((255, 0, 0, 100))
            surface.blit(overlay, (clip_rect.left, clip_rect.top))

        # --- Thermometer gradient ---
        grad_surface = pygame.Surface((self.bar_rect.width, self.bar_rect.height))
        for i in range(self.bar_rect.height):
            t = i / self.bar_rect.height
            r = int(255 * t)
            g = int(100 * (1 - t))
            b = int(255 * (1 - t))
            pygame.draw.line(grad_surface, (r, g, b), (0, self.bar_rect.height - i - 1), (self.bar_rect.width, self.bar_rect.height - i - 1))
        surface.blit(grad_surface, self.bar_rect.topleft)

        # --- Target range ---
        zone_top = self.bar_rect.top + self.bar_rect.height * (1 - self.target_max / self.max_temp)
        zone_bottom = self.bar_rect.top + self.bar_rect.height * (1 - self.target_min / self.max_temp)
        pygame.draw.rect(surface, (100, 255, 100), (self.bar_rect.left, zone_top, self.bar_rect.width, zone_bottom - zone_top))

        # --- Temperature marker ---
        temp_height = self.bar_rect.height * (self.temp / self.max_temp)
        pygame.draw.rect(surface, (255, 255, 255), (self.bar_rect.left, self.bar_rect.bottom - temp_height, self.bar_rect.width, 2))

        # --- Progress bar ---
        progress_ratio = self.progress / self.max_progress
        progress_height = self.progress_bar_rect.height * progress_ratio
        pygame.draw.rect(surface, (60, 60, 60), self.progress_bar_rect)
        pygame.draw.rect(surface, (0, 200, 255), (
            self.progress_bar_rect.left,
            self.progress_bar_rect.bottom - progress_height,
            self.progress_bar_rect.width,
            progress_height
        ))

        # --- Timer ---
        bar_x = clip_rect.left + 10
        bar_y = clip_rect.top + 10
        remaining = max(0, self.timer) / self.max_timer
        pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, 100, 10))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(100 * remaining), 10))

        # --- Billows ---
        billow_image = self.billow_img_open if self.billow_state == "open" else self.billow_img_closed
        surface.blit(billow_image, self.billow_rect.topleft)


        # --- Particles ---
        for p in self.particles:
            p.draw(surface)

        surface.set_clip(prev_clip)

    def finish(self):
        self.finished = True
        self.fill_ratio = self.progress / self.max_progress  # ← Store this

        if self.fill_ratio >= 0.9:
            self.hits = ["perfect"]
        elif self.fill_ratio >= 0.7:
            self.hits = ["good"]
        elif self.fill_ratio >= 0.5:
            self.hits = ["ok"]
        else:
            self.hits = ["miss"]

        if self.on_finish_callback:
            self.on_finish_callback(self.get_result())

    def get_result(self):
        return {
            "score": self.fill_ratio,  # ← return normalized range 0.0–1.0
            "target_range": (self.target_min, self.target_max),
            "final_temp": self.temp,
            "hits": self.hits,
            "game_name":"Heat Treating"
        }

