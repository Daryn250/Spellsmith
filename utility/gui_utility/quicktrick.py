import pygame
import math

class QuickMenu:
    def __init__(self, center, radius, divisions, images):
        self.center = center
        self.base_radius = radius
        self.divisions = divisions
        self.image_paths = [f"{images}/{i}.png" for i in range(divisions)]

        self.progress = 0.0  # 0 hidden, 1 fully visible
        self.fade_speed = 3.0  # Controls how fast it fades in/out
        self.visible = True

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def update(self, dt):
        target = 1.0 if self.visible else 0.0
        if self.progress < target:
            self.progress += dt * self.fade_speed
            if self.progress > 1.0:
                self.progress = 1.0
        elif self.progress > target:
            self.progress -= dt * self.fade_speed
            if self.progress < 0.0:
                self.progress = 0.0

    def draw(self, surface):
        if self.progress <= 0:
            return

        cx, cy = self.center

        # Smooth scale and alpha based on progress
        circle_radius = int(self.base_radius * self.progress * 1.5)  # 1.5x larger
        img_radius = int(self.base_radius * self.progress)
        alpha = int(100 * self.progress)

        # Background circle with fading alpha and scaling
        shadow_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, alpha), (circle_radius, circle_radius), circle_radius)
        surface.blit(shadow_surface, (cx - circle_radius, cy - circle_radius))

        # Draw icons only if we have divisions
        if self.divisions == 0:
            return

        angle_per_div = 2 * math.pi / self.divisions
        for i, path in enumerate(self.image_paths):
            try:
                img = pygame.image.load(path).convert_alpha()
            except Exception as e:
                print(f"[QuickMenu] Failed to load {path}: {e}")
                continue

            # Scale icons with radius (optional)
            icon_size = max(16, int(32 * self.progress))  # scale from 16 to 32 px
            img = pygame.transform.scale(img, (icon_size, icon_size))

            angle = angle_per_div * i - math.pi / 2
            x = cx + math.cos(angle) * img_radius - img.get_width() // 2
            y = cy + math.sin(angle) * img_radius - img.get_height() // 2

            surface.blit(img, (x, y))
