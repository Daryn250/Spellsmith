# tool class
# you have layers of a tool, which are images that can be layered ontop of eachother
# each image is rendered in the following sequence:
# blade => guard => pommel => handle => effects
# in the future, I want to add things like strings that hang from the weapon that you can add.

import pygame
import os
import random

class Tool:
    LAYER_ORDER = ["blade", "guard", "pommel", "handle", "effect"]
    
    def __init__(self, manager, tool_type, pos, nbt={}):
        self.manager = manager
        self.nbt = dict(nbt)
        self.tool_type = tool_type
        self.flags = ["tool", "draggable", "tricks"]
        self.pos = pos
        self.layers = []  # now stores file paths instead of surfaces
        self.particles = []
        self.scale = [1,1]

        if not hasattr(self, "flags"):
            self.flags = []
        if not hasattr(self, "animated"):
            self.animated = False
        if not hasattr(self, "frameDuration") and self.animated:
            self.frameDuration = 100
        if not hasattr(self, "img_path"):
            self.img_path = "assets/error.png"
        if not hasattr(self, "friction"):
            if self.flags != []:
                self.friction = 1.05
        if not hasattr(self, "layer_surfaces"):
            self.layer_surfaces = []
        if not hasattr(self, "quality_stars"):
            # compute quality in the future
            self.quality_stars = random.randint(1,6)
        if not hasattr(self, "temperature"):
            # compute quality in the future
            self.temperature = 0

        # Check required fields
        if "origin_screen" not in self.nbt:
            print(f"[Tool WARNING] NBT is missing 'origin_screen' key: {self.nbt}")

        if "draggable" in self.flags:
            if not hasattr(self, "vx"):
                self.rotation = 0.0
                self.rotational_velocity = 0.0

                self.vx = 0
                self.vy = 0

                self.currentGravity = 0.3
                self.storedGravity = 0.3


            self.floor = pos[1]
            self.dragging = False

        # Load NBT values as attributes
        for key, value in self.nbt.items():
            setattr(self, key, value)

        self.load_layers()

        manager.add_item(self)

    def load_layers(self):
        """Load and cache surfaces for all layers (avoid repeated disk loads)."""
        self.layers.clear()
        self.layer_surfaces = []

        for part in Tool.LAYER_ORDER:
            material = self.nbt.get(part)
            if material:
                path = f"assets/tools/{self.tool_type}/{part}/{material}.png"
                if os.path.exists(path):
                    try:
                        surf = pygame.image.load(path).convert_alpha()
                        self.layer_surfaces.append(surf)
                    except Exception as e:
                        print(f"[Tool] Failed to load image: {path} - {e}")
                else:
                    print(f"[Tool] Missing asset: {path}")

        # ✅ Combine and generate mask *after* layer surfaces are loaded
        self._base_combined_surface = self._combine_layers()
        if self._base_combined_surface is not None:
            x_scale = (self.manager.VIRTUAL_SIZE[0] / 480) * 2
            y_scale = (self.manager.VIRTUAL_SIZE[1] / 270) * 2
            scale = min(x_scale, y_scale)

            scaled_surface = pygame.transform.scale(
                self._base_combined_surface,
                (
                    int(self._base_combined_surface.get_width() * scale),
                    int(self._base_combined_surface.get_height() * scale),
                )
            )
            self._collision_mask = pygame.mask.from_surface(scaled_surface)
        else:
            self._collision_mask = None


        # Cache for transformed surface
        self._cached_image = None
        self._cached_rotation = None
        self._cached_scale = None


    def _combine_layers(self):
        """Combine layer_surfaces into one surface at original size."""
        if not self.layer_surfaces:
            return None
        max_width = max(s.get_width() for s in self.layer_surfaces)
        max_height = max(s.get_height() for s in self.layer_surfaces)
        combined = pygame.Surface((max_width, max_height), pygame.SRCALPHA)
        for surf in self.layer_surfaces:
            combined.blit(surf, (0, 0))
        return combined

    def draw(self, surface, VIRTUAL_SIZE, gui_manager, item_manager, rotation_scale):
        angle = -getattr(self, "rotation", 0)
        scale_x = (VIRTUAL_SIZE[0] / 480) * 2 * self.scale[0] / rotation_scale
        scale_y = (VIRTUAL_SIZE[1] / 270) * 2 * self.scale[1] / rotation_scale

        if (self._cached_image is None or
            self._cached_rotation != angle or
            self._cached_scale != (scale_x, scale_y)):

            if self._base_combined_surface is None:
                return

            upscaled_size = (
                int(self._base_combined_surface.get_width() * rotation_scale),
                int(self._base_combined_surface.get_height() * rotation_scale),
            )
            highres_img = pygame.transform.scale(self._base_combined_surface, upscaled_size)
            rotated_img = pygame.transform.rotate(highres_img, angle)
            final_width = int(rotated_img.get_width() * abs(scale_x))
            final_height = int(rotated_img.get_height() * abs(scale_y))
            scaled_img = pygame.transform.scale(rotated_img, (final_width, final_height))

            if scale_x < 0 or scale_y < 0:
                scaled_img = pygame.transform.flip(scaled_img, scale_x < 0, scale_y < 0)

            self._cached_image = scaled_img
            self._cached_rotation = angle
            self._cached_scale = (scale_x, scale_y)

        draw_x = self.pos[0] - self._cached_image.get_width() // 2
        draw_y = self.pos[1] - self._cached_image.get_height() // 2

        # Draw shadow
        shadow_img = self._cached_image.copy()
        shadow_alpha = 100
        shadow_img.fill((0, 0, 0, shadow_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(shadow_img, (draw_x, draw_y + 10))

        if hasattr(self, "temperature"):
            temp = self.temperature
            max_temp = 1000
            glow_strength = min(1.0, temp / max_temp)

            if glow_strength > 0.01:
                # Create a glow surface with the same size
                glow_surface = pygame.Surface(self._cached_image.get_size(), pygame.SRCALPHA)

                # Create a mask from the rotated image
                mask = pygame.mask.from_surface(self._cached_image)
                outline_surface = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

                # Tint the white surface red-orange based on temperature
                tint_color = (int(255 * glow_strength), int(32 * glow_strength), 0, int(160 * glow_strength))
                tint_surface = pygame.Surface(self._cached_image.get_size(), pygame.SRCALPHA)
                tint_surface.fill(tint_color)

                # Use the mask to apply tint only where visible
                outline_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # Additive blend onto the rotated image
                # Create a temp copy to draw the glow onto
                tool_image = self._cached_image.copy()
                tool_image.blit(outline_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

                # Add a smooth, color-shifting additive glow around hot items
                if temp >= 200:
                    glow_strength = min(1.0, (temp - 200) / 800)  # Scale from 0 to 1

                    def lerp(a, b, t): return int(a + (b - a) * t)

                    base_color = (
                        lerp(255, 255, glow_strength),
                        lerp(50, 255, glow_strength),
                        lerp(0, 200, glow_strength)
                    )

                    for i in range(3):
                        # Inverse square brightness falloff
                        ring_strength = glow_strength / ((i + 1) ** 2)
                        ring_radius = int(self._cached_image.get_width() * (0.6 + 0.2 * i) * glow_strength)
                        ring_color = tuple(int(c * ring_strength) for c in base_color)

                        if ring_radius > 0:
                            glow_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                            pygame.draw.circle(
                                glow_surface,
                                ring_color,
                                (ring_radius, ring_radius),
                                ring_radius
                            )
                            surface.blit(
                                glow_surface,
                                (self.pos[0] - ring_radius, self.pos[1] - ring_radius),
                                special_flags=pygame.BLEND_RGB_ADD
                            )

        # Draw actual tool
        # surface.blit(self._cached_image, (draw_x, draw_y))
        surface.blit(tool_image, (draw_x, draw_y))



    def set_position(self, pos):
        self.pos = pos
        if "draggable" in self.flags:
            self.vx = 0
            self.vy = 0
            self.floor = pos[1]
            self.ovx = 0
            self.ovy = 0
            self.rotation = 0





    


    def update(self, screen, gui_manager, VIRTUAL_SIZE, dt):
        if "draggable" in self.flags:
            # Don't decay rotation if trick is active
            if not hasattr(self, "trick") or getattr(self.trick, "finished", True):
                self.rotation += self.rotational_velocity
                self.rotational_velocity *= 0.85
                if abs(self.rotation) < 0.1:
                    self.rotation = 0.0
                    self.rotational_velocity = 0.0
                else:
                    self.rotation *= 0.9


            # Physics & bounds
            screenW, screenH = screen.get_size()
            currentX, currentY = self.pos

            # Apply velocity
            if self.dragging!=True:
                currentX += self.vx
                currentY += self.vy

            # Apply friction (to gradually reduce movement)
            self.vx /= self.friction

            # Gravity
            self.vy += self.currentGravity

            # Bounds and bounce
            item_width, item_height = self.get_scaled_size(VIRTUAL_SIZE)


            # Floor bounce — only if not dragging and falling down
            if not self.dragging and self.vy > 0:
                if currentY > self.floor:
                    currentY = self.floor
                    self.vy = 0
                    self.vx /= 1.5

            half_width = item_width // 2
            half_height = item_height // 2

            # Left bound
            if currentX - half_width < 0:
                currentX = half_width
                self.vx = abs(self.vx) / 1.1

            # Right bound
            if currentX + half_width > screenW:
                currentX = screenW - half_width
                self.vx = -abs(self.vx) / 1.1

            # Top
            if currentY - half_height < 0:
                currentY = half_height
                self.vy = abs(self.vy) / 1.1

            # Bottom
            if currentY + half_height > screenH:
                currentY = screenH - half_height
                self.vy = abs(self.vy) / 1.1

   
            self.pos = currentX, currentY   
        pass   
   
    def get_scaled_size(self, screensize):   
        """Returns the pixel-accurate bounding box (width, height) after scaling."""   
        x_scale = (screensize[0] / 480) * 2
        y_scale = (screensize[1] / 270) * 2
        scale = min(x_scale, y_scale)

        left, top, right, bottom = None, None, None, None

        for surf in self.layer_surfaces:
            if not surf:
                continue

            mask = pygame.mask.from_surface(surf)
            rects = mask.get_bounding_rects()
            if not rects:
                continue  # fully transparent

            for bbox in rects:
                if left is None:
                    left, top, right, bottom = bbox.left, bbox.top, bbox.right, bbox.bottom
                else:
                    left = min(left, bbox.left)
                    top = min(top, bbox.top)
                    right = max(right, bbox.right)
                    bottom = max(bottom, bbox.bottom)

        if left is None:
            return (0, 0)

        unscaled_width = right - left
        unscaled_height = bottom - top
        return (int(unscaled_width * scale), int(unscaled_height * scale))

    def get_combined_surface(self, screensize):
        """Returns a combined surface of all layers scaled to the screen size."""
        x_scale = (screensize[0] / 480) * 2
        y_scale = (screensize[1] / 270) * 2
        scale = min(x_scale, y_scale)

        surfaces = []
        max_width, max_height = 0, 0

        for surf in self.layer_surfaces:
            scaled = pygame.transform.scale(
                surf,
                (int(surf.get_width() * scale), int(surf.get_height() * scale))
            )
            surfaces.append(scaled)
            max_width = max(max_width, scaled.get_width())
            max_height = max(max_height, scaled.get_height())

        combined = pygame.Surface((max_width, max_height), pygame.SRCALPHA)
        for s in surfaces:
            combined.blit(s, (0, 0))

        return combined

    
    def get_collision_mask(self, screensize):
        return self._collision_mask
    
    def is_point_inside(self, point, screensize):
        mask = self.get_collision_mask(screensize)
        if mask is None:
            return False

        rel_x = int(point[0] - (self.pos[0] - mask.get_size()[0] // 2))
        rel_y = int(point[1] - (self.pos[1] - mask.get_size()[1] // 2))

        if 0 <= rel_x < mask.get_size()[0] and 0 <= rel_y < mask.get_size()[1]:
            return mask.get_at((rel_x, rel_y)) == 1
        return False


    def get_image(self, screensize):
        return self.get_combined_surface(screensize)




    def to_nbt(self, exclude=["pos", "type", "is_hovered", "ovx", "ovy", "floor", "dragging", "nbt", "manager", "layers", "trick", "layer_surfaces", "_cached_image",
                              "_base_combined_surface", "_collision_mask"]):
        return {k: v for k, v in self.__dict__.items() if k not in exclude}