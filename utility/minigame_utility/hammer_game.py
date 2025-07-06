import pygame
import random
from utility.particle import make_particles_presets

class MovingTarget:
    def __init__(self, start, end, speed):
        self.start = start
        self.end = end
        self.speed = speed
        self.t = 0

    def update(self, dt):
        self.t += dt * self.speed
        if self.t > 1:
            self.t = 1
        x = int(self.start[0] * (1 - self.t) + self.end[0] * self.t)
        y = int(self.start[1] * (1 - self.t) + self.end[1] * self.t)
        return x, y

class GravityTarget:
    def __init__(self, start, velocity):
        self.x, self.y = start
        self.vx, self.vy = velocity
        self.gravity = 0.02

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.vx *=0.95
        self.vy *=0.95
        return int(self.x), int(self.y)
from utility.settingsManager import get_font
class HammerMiniGame:
    def __init__(self, virtual_size, difficulty, clip_rect, screen, on_finish = None):
        self.font = pygame.font.Font(get_font(), 15)
        self.virtual_size = virtual_size
        self.clip_rect = clip_rect

        self.difficulty = round(max(1, difficulty/1.1))

        self.target_radius = 40
        self.target_timer = 0
        self.targets = []
        self.current_index = 0
        self.hit_flash_timer = 0

        self.floating_words = []
        self.particles = []
        self.screen = screen

        self.score = 0
        self.max_score = 0
        self.results = []

        self.target_count = 3 + difficulty * 2
        self.time_per_target = max(400, 2000 - difficulty * 100)

        self.generate_targets()
        self.finished = False
        self.on_finish_callback = on_finish

    def generate_targets(self):
        if not self.clip_rect:
            left, top = 0, 0
            right, bottom = self.virtual_size
        else:
            left = self.clip_rect.left
            top = self.clip_rect.top
            right = self.clip_rect.right
            bottom = self.clip_rect.bottom

        safe_margin = self.target_radius + 50

        for _ in range(self.target_count):
            if self.difficulty >= 4 and random.random() < 0.3:
                start = (
                    random.randint(left + safe_margin, right - safe_margin),
                    random.randint(top + safe_margin, bottom - safe_margin)
                )
                end = (
                    random.randint(left + safe_margin, right - safe_margin),
                    random.randint(top + safe_margin, bottom - safe_margin)
                )
                self.targets.append(MovingTarget(start, end, speed=1 / self.time_per_target))

            elif self.difficulty >= 6 and random.random() < 0.3:
                start = (
                    random.randint(left + safe_margin, right - safe_margin),
                    bottom + 10  # slightly offscreen so it flies up
                )
                velocity = (random.uniform(-1.5, 1.5), random.uniform(-13, -16))
                self.targets.append(GravityTarget(start, velocity))

            else:
                cx = random.randint(left + safe_margin, right - safe_margin)
                cy = random.randint(top + safe_margin, bottom - safe_margin)
                self.targets.append((cx, cy))

        self.target_timer = self.time_per_target
        self.max_score = self.target_count * 1.25




    def update(self, dt, virtual_mouse):
        if self.finished:
            return

        # Update floating words
        for word in self.floating_words:
            word["x"] += word["vx"]
            word["y"] += word["vy"]
            word["rotation"] += word["rotation_speed"]
            word["life"] -= dt
        self.floating_words = [w for w in self.floating_words if w["life"] > 0]

        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]

        # ✅ Move the current target if needed
        if self.current_index < len(self.targets):
            t = self.targets[self.current_index]
            if isinstance(t, (MovingTarget, GravityTarget)):
                self.current_target_pos = t.update(dt)
            else:
                self.current_target_pos = t  # Static target

        self.target_timer -= dt
        if self.target_timer <= 0:
            self.results.append("miss")
            self.spawn_floating_word("Miss...", virtual_mouse, (255, 255, 255))
            self.next_target()

    def get_current_target_pos(self):
        return getattr(self, "current_target_pos", (0, 0))


    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.handle_click(mouse_pos)

    def get_current_target_pos(self):
        t = self.targets[self.current_index]
        if isinstance(t, (MovingTarget, GravityTarget)):
            return t.update(0)
        return t

    def handle_click(self, pos):
        if self.finished or self.current_index >= len(self.targets):
            return

        cx, cy = self.get_current_target_pos()
        dist = ((pos[0] - cx) ** 2 + (pos[1] - cy) ** 2) ** 0.5

        if dist <= self.target_radius:
            if dist < self.target_radius * 0.3:
                self.score += 2
                self.results.append("perfect")
                self.spawn_floating_word("Perfect!", pos, (255, 255, 100))
                particles = make_particles_presets["stars"](pos, count=5)
                self.screen.start_shake(10, 3)
            else:
                self.score += 1
                self.results.append("Good")
                self.spawn_floating_word("Good!", pos, (150, 200, 255))
                particles = make_particles_presets["sparkles"](pos, count=3)
                self.screen.start_shake(7, 1)

            self.particles.extend(particles)
            self.hit_flash_timer = 150
            self.next_target()

    def next_target(self):
        self.current_index += 1
        if self.current_index >= len(self.targets):
            self.finish()
        else:
            self.target_timer = self.time_per_target

    def finish(self):
        self.finished = True
        if self.on_finish_callback:
            self.on_finish_callback(self.results)

    def get_result(self):
        return {
            "score": self.score,
            "max_score": self.max_score,
            "hits": self.results
        }

    def draw(self, surface, clip_rect):
        if self.finished or self.current_index >= len(self.targets):
            return

        cx, cy = self.get_current_target_pos()
        elapsed = self.time_per_target - self.target_timer
        progress = max(0.0, min(1.0, elapsed / self.time_per_target))

        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        color = (255, 255, 0) if self.hit_flash_timer > 0 else (255, 0, 0)
        pygame.draw.circle(surface, color, (cx, cy), self.target_radius, 2)

        shrinking_radius = int(self.target_radius * (1 - progress) + 1 * progress)
        pygame.draw.circle(surface, (100, 100, 255), (cx, cy), shrinking_radius, 1)

        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 4)

        bar_width = 100
        remaining = max(0, self.target_timer) / self.time_per_target
        if self.clip_rect:
            bar_x = self.clip_rect.left + 10
            bar_y = self.clip_rect.top + 10
        else:
            bar_x = 20
            bar_y = 20

        pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, 100, 10))
        pygame.draw.rect(surface, (0, 200, 0), (bar_x, bar_y, int(100 * remaining), 10))

        for word in self.floating_words:
            alpha = max(0, min(255, int((word["life"] / 100) * 255)))
            text_surface = self.font.render(word["text"], True, word["color"])
            text_surface.set_alpha(alpha)
            rotated = pygame.transform.rotate(text_surface, word["rotation"])
            rect = rotated.get_rect(center=(word["x"], word["y"]))
            surface.blit(rotated, rect)

        for p in self.particles:
            p.draw(surface)

        score_text = f"Score: {self.score}/{self.max_score}"
        target_text = f"Target: {self.current_index+1}/{self.target_count}"

        score_surface = self.font.render(score_text, False, (255, 255, 255))
        target_surface = self.font.render(target_text, False, (200, 200, 200))

        surface.blit(score_surface, (bar_x, bar_y + 18))
        surface.blit(target_surface, (bar_x, bar_y + 50))

        #self.draw_debug_paths(surface)


        surface.set_clip(prev_clip)
    def draw_debug_paths(self, surface):
        for t in self.targets:
            if isinstance(t, MovingTarget):
                pygame.draw.line(surface, (100, 100, 100), t.start, t.end, 1)

    def spawn_floating_word(self, text, pos, color):
        word = {
            "text": text,
            "x": pos[0],
            "y": pos[1],
            "vx": random.uniform(-1.5, 1.5),
            "vy": -2,
            "rotation": random.uniform(-15, 15),
            "rotation_speed": random.uniform(-2, 2),
            "life": 255,
            "color": color
        }
        self.floating_words.append(word)
