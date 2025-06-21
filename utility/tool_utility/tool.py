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
        if not hasattr(self, "quality_stars"):
            # compute quality in the future
            self.quality_stars = random.randint(1,6)

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

                self.squish = (1, 1) # 1 = no squish

            self.floor = pos[1]
            self.dragging = False

        # Load NBT values as attributes
        for key, value in self.nbt.items():
            setattr(self, key, value)

        self.load_layers()

    def load_layers(self):
        """Populates self.layers with ordered image paths."""
        self.layers.clear()
        for part in Tool.LAYER_ORDER:
            material = self.nbt.get(part)
            if material:
                path = f"assets/tools/{self.tool_type}/{part}/{material}.png"
                if os.path.exists(path):
                    self.layers.append(path)
                else:
                    print(f"[Tool] Missing asset: {path}")


    def draw(self, surface, VIRTUAL_SIZE, gui_manager, item_manager, rotation_scale):
        """Draws the full tool with smooth squish, top-left anchoring, and improved rotation."""
        angle = -getattr(self, "rotation", 0)
        x, y = self.pos
        ovx = getattr(self, "ovx", 0)
        ovy = getattr(self, "ovy", 0)
        rotation_scale = rotation_scale

        # Target squish based on velocity
        max_squish = 0.15
        target_squish_x = 1.0 + max(-max_squish, min(max_squish, -abs(ovx * 0.05)))
        target_squish_y = 1.0 + max(-max_squish, min(max_squish, -abs(ovy * 0.05)))

        # Smooth easing
        decay_rate = 0.1
        self.squish[0] += (target_squish_x - self.squish[0]) * decay_rate
        self.squish[1] += (target_squish_y - self.squish[1]) * decay_rate

        for path in self.layers:
            if path is None:
                continue
            try:
                base_img = pygame.image.load(path).convert_alpha()
            except pygame.error:
                print(f"[Tool] Failed to load image: {path}")
                continue

            # Step 1: Temporarily upscale image to improve rotation smoothness
            upscaled_size = (
                int(base_img.get_width() * rotation_scale),
                int(base_img.get_height() * rotation_scale)
            )
            highres_img = pygame.transform.scale(base_img, upscaled_size)

            # Step 2: Rotate the high-res image
            rotated_img = pygame.transform.rotate(highres_img, angle)

            # Step 3: Downscale to screen resolution and squish
            base_scale_x = (VIRTUAL_SIZE[0] / 480) * 2
            base_scale_y = (VIRTUAL_SIZE[1] / 270) * 2

            scale_x = base_scale_x * self.squish[0] / rotation_scale
            scale_y = base_scale_y * self.squish[1] / rotation_scale

            final_size = (
                int(rotated_img.get_width() * scale_x),
                int(rotated_img.get_height() * scale_y)
            )
            scaled_img = pygame.transform.scale(rotated_img, final_size)

            # Draw shadow first
            shadow_offset = (0, self.floor+10)
            shadow_img = scaled_img.copy()
            shadow_alpha = 100
            shadow_img.fill((0, 0, 0, shadow_alpha), special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(shadow_img, (x + shadow_offset[0], shadow_offset[1]))

            # Draw actual item
            surface.blit(scaled_img, (x, y))


            # Blit to screen at top-left
            surface.blit(scaled_img, (x, y))





    


    def update(self, screen, gui_manager, VIRTUAL_SIZE, dt):
        if "draggable" in self.flags:
            self.rotation += self.rotational_velocity
            self.rotational_velocity *= 0.85  # Friction decay
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

            # Left bound
            if currentX < 0:
                currentX = 0
                self.vx = abs(self.vx) / 1.1

            # Right bound   
            if currentX + item_width > screenW:   
                currentX = screenW - item_width   
                self.vx = -abs(self.vx) / 1.1   
            # Ceiling   
            if currentY < 0:   
                currentY = 0 
                self.vy = abs(self.vy) / 1.1   
            # Bottom bound   
            if currentY + item_height > screenH:   
                currentY = screenH - item_height   
                self.vy = abs(self.vy) / 1.1   
   
            self.pos = currentX, currentY   
        pass   
   
    def get_scaled_size(self, screensize):   
        """Returns the pixel-accurate bounding box (width, height) after scaling."""   
        x_scale = screensize[0] / 480
        y_scale = screensize[1] / 270
        scale = min(x_scale*2, y_scale*2)

        left, top, right, bottom = None, None, None, None

        for path in self.layers:
            if not path:
                continue
            try:
                img = pygame.image.load(path).convert_alpha()
            except:
                continue

            mask = pygame.mask.from_surface(img)
            rects = mask.get_bounding_rects()
            if not rects:
                continue  # fully transparent

            # Use union of all bounding rects
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
        # Calculate scale
        x_scale = (screensize[0] / 480) * 2
        y_scale = (screensize[1] / 270) * 2
        scale = min(x_scale, y_scale)

        # Determine max width/height of the tool
        max_width, max_height = 0, 0
        surfaces = []

        for path in self.layers:
            if not path:
                continue
            try:
                img = pygame.image.load(path).convert_alpha()
            except:
                continue

            scaled = pygame.transform.scale(
                img,
                (int(img.get_width() * scale), int(img.get_height() * scale))
            )

            surfaces.append(scaled)
            max_width = max(max_width, scaled.get_width())
            max_height = max(max_height, scaled.get_height())

        # Create blank transparent surface
        combined = pygame.Surface((max_width, max_height), pygame.SRCALPHA)
        for surf in surfaces:
            combined.blit(surf, (0, 0))  # Stack layers at (0, 0) offset

        return combined
    
    def get_collision_mask(self, screensize):
        combined_surface = self.get_combined_surface(screensize)
        return pygame.mask.from_surface(combined_surface)
    
    def is_point_inside(self, point, screensize):
        mask = self.get_collision_mask(screensize)
        rel_x = int(point[0] - self.pos[0])
        rel_y = int(point[1] - self.pos[1])
        if 0 <= rel_x < mask.get_size()[0] and 0 <= rel_y < mask.get_size()[1]:
            return mask.get_at((rel_x, rel_y)) == 1
        return False




    def to_nbt(self, exclude=["pos", "type", "is_hovered", "ovx", "ovy", "floor", "dragging", "nbt", "manager"]):
        return {k: v for k, v in self.__dict__.items() if k not in exclude}