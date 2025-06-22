import pygame
import math
def draw_pie_slice(surface, color, center, radius, start_angle, end_angle, points=10):
    """
    Draws a filled pie slice (wedge) on the given surface.
    
    - center: (x, y) center of the circle
    - radius: radius of the circle
    - start_angle, end_angle: angles in radians
    - points: number of edge points for the arc (higher = smoother)
    """
    cx, cy = center
    angle_step = (end_angle - start_angle) / points

    arc_points = [
        (cx + math.cos(start_angle + angle_step * i) * radius,
         cy + math.sin(start_angle + angle_step * i) * radius)
        for i in range(points + 1)
    ]

    pygame.draw.polygon(surface, color, [center] + arc_points)

class QuickMenu:
    def __init__(self, center, radius, total_slots, unlocked_slots, images_folder):
        self.center = center
        self.base_radius = radius
        self.total_slots = total_slots  # Always 6 in this case
        self.unlocked_slots = unlocked_slots  # 0 to 6
        self.image_paths = [f"{images_folder}/{i}.png" for i in range(total_slots)]

        self.progress = 0.0
        self.fade_speed = 3.0
        self.visible = True
        self.selected_index = None

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def update(self, dt, mouse_pos=None):
        target = 1.0 if self.visible else 0.0
        if self.progress < target:
            self.progress += dt * self.fade_speed
            self.progress = min(1.0, self.progress)
        elif self.progress > target:
            self.progress -= dt * self.fade_speed
            self.progress = max(0.0, self.progress)

        # Selection logic based on distance to icon centers
        self.selected_index = None
        if mouse_pos and self.progress > 0.2:
            mx, my = mouse_pos
            cx, cy = self.center
            icon_distance = self.base_radius * self.progress
            min_dist = float('inf')

            for i in range(self.unlocked_slots):
                angle = math.radians(60 * i) - math.pi / 2  # point upward first
                x = cx + math.cos(angle) * icon_distance
                y = cy + math.sin(angle) * icon_distance
                dist = math.hypot(mx - x, my - y)
                if dist < 32:  # arbitrary hover radius
                    if dist < min_dist:
                        min_dist = dist
                        self.selected_index = i

    def draw(self, surface):
        if self.progress <= 0:
            return

        cx, cy = self.center
        circle_radius = int(self.base_radius * self.progress * 1.5)
        icon_radius = int(self.base_radius * self.progress)
        alpha = int(100 * self.progress)
        icon_size = max(16, int(32 * self.progress))

        # Background circle
        shadow_surface = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(shadow_surface, (0, 0, 0, alpha), (circle_radius, circle_radius), circle_radius)
        surface.blit(shadow_surface, (cx - circle_radius, cy - circle_radius))

        for i in range(self.total_slots):
            if i >= len(self.image_paths):
                continue
            try:
                img = pygame.image.load(self.image_paths[i]).convert_alpha()
            except Exception as e:
                print(f"[QuickMenu] Failed to load {self.image_paths[i]}: {e}")
                continue

            angle = math.radians(60 * i) - math.pi / 2
            x = cx + math.cos(angle) * icon_radius
            y = cy + math.sin(angle) * icon_radius

            # Draw hover highlight if selected
            if i == self.selected_index and self.progress>0.75:
                # Draw white arc at tip of selected direction
                arc_radius = circle_radius - 10  # slightly inside outer edge
                arc_thickness = 6
                arc_length = math.radians(50)  # how wide the arc is

                # Create arc surface
                arc_surf = pygame.Surface((circle_radius * 2, circle_radius * 2), pygame.SRCALPHA)
                start_angle = angle - arc_length / 2
                end_angle = angle + arc_length / 2

                draw_pie_slice(
                    arc_surf,
                    (255, 255, 255, int(180 * self.progress)),
                    (circle_radius, circle_radius),
                    arc_radius,
                    start_angle,
                    end_angle,
                    points=12
                )
                draw_pie_slice(
                    arc_surf,
                    (0, 0, 0, 0),
                    (circle_radius, circle_radius),
                    arc_radius - arc_thickness,
                    start_angle - math.radians(1),
                    end_angle + math.radians(2),
                    points=12
                )
                surface.blit(arc_surf, (cx - circle_radius, cy - circle_radius))



            # Desaturate or darken locked slots
            if i >= self.unlocked_slots:
                img.fill((100, 100, 100, 100), special_flags=pygame.BLEND_RGBA_MULT)

            img = pygame.transform.scale(img, (icon_size, icon_size))
            surface.blit(img, (x - img.get_width() // 2, y - img.get_height() // 2))
