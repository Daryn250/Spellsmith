import pygame
import random
import math
from utility.animated_sprite import AnimatedTile

class Particle:
    def __init__(self, pos, color=(255, 255, 255), velocity=(0, 0), gravity=0.1,
                 lifetime=30, size=2, glow=False, glowtype=None, image=None,
                 animated_tile=None, rotation=None, rotation_speed=0, glowStrength = 20):
        self.x, self.y = pos
        self.base_color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.vx, self.vy = velocity
        self.gravity = gravity
        self.glow = glow
        self.glowstrength = glowStrength
        self.glowtype = glowtype or []
        self.image = image
        self.animated_tile = animated_tile
        self.rotation = rotation or 0
        self.rotation_speed = rotation_speed

    def update(self, dt=1):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1

        if hasattr(self, "animated_tile") and self.animated_tile:
            self.animated_tile.update(dt)

    def is_alive(self):
        return self.lifetime > 0

    def _pulse_alpha(self, base_alpha):
        pulse_speed = 0.15
        pulse = (math.sin(pygame.time.get_ticks() * pulse_speed / 1000 * 2 * math.pi) + 1) / 2
        return int(base_alpha * (0.6 + 0.4 * pulse))

    def _flicker_alpha(self, alpha):
        flicker = random.uniform(0.8, 1.2)
        return max(0, min(255, int(alpha * flicker)))

    def _shift_color(self, base_color):
        shift_amount = 30
        pulse_speed = 0.1
        t = (math.sin(pygame.time.get_ticks() * pulse_speed / 1000 * 2 * math.pi) + 1) / 2

        def shift(c): return max(0, min(255, int(c + shift_amount * (t - 0.5) * 2)))
        return tuple(shift(c) for c in base_color)

    def draw(self, surface):
        if self.lifetime <= 0:
            return

        # --- Compute alpha using fast fade-in and slow fade-out
        t = 1 - (self.lifetime / self.max_lifetime)
        fade_duration = 0.2
        if t < fade_duration:
            alpha = int(255 * (t / fade_duration))
        else:
            fade_out_t = (t - fade_duration) / (1 - fade_duration)
            alpha = int(255 * (1 - fade_out_t)**1.5)

        # Optionally override with glowtype effects
        if self.glowtype:
            if "pulse" in self.glowtype:
                alpha = self._pulse_alpha(alpha)
            if "flicker" in self.glowtype:
                alpha = self._flicker_alpha(alpha)
            if "shift" in self.glowtype:
                self.base_color = self._shift_color(self.base_color)  # update color

        pos = (int(self.x), int(self.y))

        # --- Animated Tile drawing
        if hasattr(self, "animated_tile") and self.animated_tile:
            frame = self.animated_tile.get_current_frame().copy()

            # Apply alpha to the entire surface
            frame.set_alpha(alpha)

            # Center the image around the particle position
            rect = frame.get_rect(center=pos)

            # Optional: draw soft glow underneath
            if self.glow:
                max_glow_radius = self.size * 6
                glow_surf = pygame.Surface((max_glow_radius * 2, max_glow_radius * 2), pygame.SRCALPHA)
                dim_alpha = max(0, min(255, int(alpha * 0.5)))
                glow_color = (dim_alpha, dim_alpha, dim_alpha)

                pygame.draw.circle(glow_surf, (*glow_color, int(alpha * 0.05)), (max_glow_radius, max_glow_radius), max_glow_radius)
                surface.blit(glow_surf, (pos[0] - max_glow_radius, pos[1] - max_glow_radius), special_flags=pygame.BLEND_ADD)

            surface.blit(frame, rect.topleft)

        # --- Static fallback (no animated tile)
        else:
            # Optional: draw soft glow
            if self.glow:
                max_glow_radius = self.size * self.glowstrength
                glow_surf = pygame.Surface((max_glow_radius * 2, max_glow_radius * 2), pygame.SRCALPHA)
                dim_alpha = max(0, min(255, int(alpha * 0.5)))
                glow_color = (dim_alpha, dim_alpha, dim_alpha)
                pygame.draw.circle(glow_surf, (*glow_color, dim_alpha), (max_glow_radius, max_glow_radius), max_glow_radius)
                surface.blit(glow_surf, (pos[0] - max_glow_radius, pos[1] - max_glow_radius), special_flags=pygame.BLEND_ADD)

            # Main particle
            pygame.draw.circle(surface, (*self.base_color, dim_alpha), pos, self.size)

    def _fade_in_out_alpha(self):
        t = 1 - (self.lifetime / self.max_lifetime)
        fade_duration = 0.2
        if t < fade_duration:
            return int(255 * (t / fade_duration))
        fade_out_t = (t - fade_duration) / (1 - fade_duration)
        return int(255 * (1 - fade_out_t)**1.5)


# Factory functions
def make_sparkles(center, count=5):
    particles = []
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(0, 50)
        x = center[0] + math.cos(angle) * radius
        y = center[1] + math.sin(angle) * radius
        p = Particle(
            pos=(x, y),
            color=(255, 255, 255),
            velocity=(0, 0),
            gravity=0,
            lifetime=random.randint(40,80),
            glow=False,
            animated_tile=AnimatedTile("assets/particles/sparkle", frame_duration=random.randint(10,15))
        )
        particles.append(p)
    return particles

def make_smoke(pos, count=5):
    particles = []
    for _ in range(count):
        vx = random.uniform(-1, 1)
        vy = random.uniform(-2, -0.5)
        p = Particle(
            pos=pos,
            color=(100, 100, 100),
            velocity=(vx, vy),
            gravity=0.05,
            lifetime=40,
            glow=False,
            animated_tile=AnimatedTile("assets/particles/smoke", frame_duration=80)
        )
        particles.append(p)
    return particles

def make_stars(pos, count=5):
    particles = []
    for _ in range(count):
        vx = random.uniform(-5, 5)
        vy = random.uniform(-5, 5)
        rot_speed = random.uniform(-5, 5)
        p = Particle(
            pos=pos,
            color=(255, 255, 255),
            velocity=(vx, vy),
            gravity=0,
            lifetime=random.randint(30, 40),
            glow=True,
            glowtype=["pulse"],
            rotation=random.uniform(0, 360),
            rotation_speed=rot_speed,
            animated_tile=AnimatedTile("assets/particles/stars", frame_duration=10)
        )
        particles.append(p)
    return particles

def make_fire(pos, count=5):
    particles = []
    for _ in range(count):
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(-1.5, -0.5)
        p = Particle(
            pos=pos,
            color=(255, 140, 0),
            velocity=(vx, vy),
            gravity=0.03,
            lifetime=30,
            glow=True,
            glowtype=["flicker", "pulse"],
            animated_tile=AnimatedTile("assets/particles/fire", frame_duration=50)
        )
        particles.append(p)
    return particles

def make_scale(pos, count=1):
    particles = []
    for _ in range(count):
        vx = random.uniform(-0.5, 0.5)
        vy = random.uniform(-1.5, -0.5)
        angle = random.uniform(0, 2 * math.pi)
        lt = random.randint(40,100)
        p = Particle(
            pos=pos,
            color=(255, 116, 4),
            velocity=(vx, vy),
            gravity=0.03,
            rotation = angle,
            lifetime=lt,
            glow=True,
            glowStrength=2
        )
        particles.append(p)
    return particles

make_particles_presets = {
    "sparkles": make_sparkles,
    "smoke": make_smoke,
    "stars": make_stars,
    "fire": make_fire,
    "scale": make_scale
}

