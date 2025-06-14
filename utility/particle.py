import pygame
import random
import math

class Particle:
    def __init__(self, pos, color, velocity=None, gravity = None, lifetime=30, size=2, glow=False, glowtype = None):
        self.x, self.y = pos
        self.base_color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx = velocity[0] if velocity else random.uniform(-2, 2)
        self.vy = velocity[1] if velocity else random.uniform(-2, -1)
        self.gravity = gravity or 0.1  # simple gravity
        self.glow = glow
        self.glowtype = glowtype

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

    def is_alive(self):
        return self.lifetime > 0

    def _pulse_alpha(self, base_alpha):
        # Pulse alpha oscillates sinusoidally between 60% and 100% of base alpha
        pulse_speed = 0.15  # controls speed of pulse
        pulse = (math.sin(pygame.time.get_ticks() * pulse_speed / 1000 * 2 * math.pi) + 1) / 2
        return int(base_alpha * (0.6 + 0.4 * pulse))

    def _flicker_alpha(self, alpha):
        # Flicker randomly varies alpha ±20%
        flicker = random.uniform(0.8, 1.2)
        flickered = int(alpha * flicker)
        return max(0, min(255, flickered))

    def _shift_color(self, base_color):
        # Shift color slightly (pulse hue shift)
        # Simple approach: oscillate RGB components slightly around base color
        shift_amount = 30  # max shift per channel
        pulse_speed = 0.1
        t = (math.sin(pygame.time.get_ticks() * pulse_speed / 1000 * 2 * math.pi) + 1) / 2

        def shift_channel(c):
            return max(0, min(255, int(c + shift_amount * (t - 0.5) * 2)))

        return tuple(shift_channel(c) for c in base_color)

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        base_alpha = int(255 * (self.lifetime / self.max_lifetime))
        alpha = base_alpha
        color = self.base_color

        # Apply glowtype effects
        if self.glowtype:
            if "pulse" in self.glowtype:
                alpha = self._pulse_alpha(alpha)
            if "flicker" in self.glowtype:
                alpha = self._flicker_alpha(alpha)
            if "shift" in self.glowtype:
                color = self._shift_color(color)

        pos = (int(self.x), int(self.y))

        pygame.draw.circle(surface, (0, 0, 0, alpha), pos, self.size + 1)

        if self.glow:
            max_glow_radius = self.size * 6
            glow_surf = pygame.Surface((max_glow_radius * 2, max_glow_radius * 2), pygame.SRCALPHA)

            layer_radius = int(max_glow_radius * 1)
            layer_alpha = int(alpha * 0.02)  # very dim glow

            # Dim the color by halving each RGB component
            dimmed_color = tuple(c // 2 for c in color)

            pygame.draw.circle(
                glow_surf,
                (*dimmed_color, layer_alpha),
                (max_glow_radius, max_glow_radius),
                layer_radius
            )

            surface.blit(
                glow_surf,
                (pos[0] - max_glow_radius, pos[1] - max_glow_radius),
                special_flags=pygame.BLEND_ADD
            )



        # Draw black outline and solid particle
        
        pygame.draw.circle(surface, (*color, alpha), pos, self.size)

