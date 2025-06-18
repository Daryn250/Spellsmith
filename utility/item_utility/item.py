import pygame
import os
import uuid
from utility.animated_sprite import AnimatedTile
from utility.item_utility.charmWindows import returnCharmWindow


class defaultItem:
    def __init__(self, type, pos, nbt_data = {}):

        self.nbt =dict(nbt_data)

        self.type = type or "undefined_itemType"
        self.pos = pos

        self.__dict__.update(self.nbt)


        if self.animated:
            self.img = AnimatedTile(self.img_path, frame_duration=self.frameDuration)
        else:
            self.img = pygame.image.load(self.img_path).convert_alpha()



        # for the draggable flag
        if not hasattr(self, "vx"):
            self.rotation = 0.0
            self.rotational_velocity = 0.0

            self.vx = 0
            self.vy = 0

            self.currentGravity = 0.3
            self.storedGravity = 0.3

        self.floor = pos[1]
        self.dragging = False

        # for the charm class:
        self.is_clicked = False

        # for the hanging class
        self.NAIL_IMAGE = pygame.image.load("assets/gui/charm_board/nail.png").convert_alpha()
        self.attached_to = None
        self.show_nail = False


    def to_nbt(self, exclude=["pos", "type", "is_hovered", "img", "ovx", "ovy", "floor", "dragging", "nbt", "window", "NAIL_IMAGE"]):
        return {k: v for k, v in self.__dict__.items() if k not in exclude}


    @property
    def image(self):
        if self.animated:
            return self.img.get_current_frame()
        return self.img

    def draw(self, surface, screensize, gui_manager):
        angle = -self.rotation  # Invert for natural lean direction

        # Compute scale based on screen resolution
        x_scale = screensize[0] / 480
        y_scale = screensize[1] / 270
        scale = min(x_scale, y_scale)  # use uniform scaling to preserve aspect ratio

        # Scale image
        original_img = self.image
        scaled_size = (int(original_img.get_width() * scale), int(original_img.get_height() * scale))
        img = pygame.transform.scale(original_img, scaled_size)

        # Draw shadow
        shadow_width = img.get_width() * 0.8
        shadow_height = img.get_height() * 0.2
        shadow_alpha = 100 if not self.dragging else 20
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect())

        shadow_x = self.pos[0] + (img.get_width() - shadow_width) / 2
        shadow_y = self.floor + img.get_height() * 0.75  # Centered on floor
        surface.blit(shadow_surface, (shadow_x, shadow_y))

        # Rotate image
        rotated_img = pygame.transform.rotate(img, angle)
        rect = rotated_img.get_rect(center=(self.pos[0] + img.get_width() // 2,
                                            self.pos[1] + img.get_height() // 2))

        if self.is_clicked:
            # Create a mask from the rotated image
            mask = pygame.mask.from_surface(rotated_img)

            # Convert mask outline to polygon points
            outline_points = mask.outline()

            if outline_points:
                # Offset all points by the top-left position where image is drawn
                offset_outline = [(point[0] + rect.left, point[1] + rect.top) for point in outline_points]

                # Draw the outline as a polygon
                pygame.draw.polygon(surface, (255, 255, 255), offset_outline, width=3)

        if getattr(self, "show_nail", False):
            nail_img = self.NAIL_IMAGE
            nail_w, nail_h = nail_img.get_size()
            x = self.anchor_pos[0] + self.image.get_width() / 2
            y = self.anchor_pos[1]
            gui_manager.nails.append([nail_img, x, y])



        
        # Draw rotated image
        surface.blit(rotated_img, rect.topleft)


    def update(self, screen, gui_manager, virtual_size, dt=None):
        """Update physics, animation, and rotation for the item."""

        if self.animated:
            if dt:
                self.img.update(dt)
            else:
                print("dt not defined, exiting pygame")
                pygame.quit()

        # Handle rotation logic
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
            item_width, item_height = self.image.get_size()

            # Floor bounce
            if not self.dragging:
                if currentY > self.floor:
                    currentY = self.floor
                    self.vy = 0
                    self.vx /=1.5
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

        if "charm" in self.flags:
            if self.is_clicked:
                if not hasattr(self, "window"):
                    self.window = returnCharmWindow(self)
                    gui_manager.windows.append(self.window)
            elif hasattr(self, "window"):
                if self.window in gui_manager.windows:
                    gui_manager.windows.remove(self.window)
                del self.window

        if "hangable" in self.flags:
            if hasattr(self, "anchor") and self.anchor is not None and self.anchor_pos is not None:
                self.floor = 9999
                # 1. Get anchor's world position
                if self.anchor == "charmboard":
                    img = gui_manager.charmboard_img
                    img_width, img_height = img.get_size()
                    scale_x = virtual_size[0] / 480
                    scale_y = virtual_size[1] / 270
                    scaled_size = (img_width * scale_x, img_height * scale_y)
                    anchor_x = virtual_size[0] - scaled_size[0] * 1.25 + self.anchor_pos[0]
                    anchor_y = 25 + self.anchor_pos[1]
                    self.show_nail = True
                else:
                    anchor_x = self.anchor.pos[0] + self.anchor_pos[0]
                    anchor_y = self.anchor.pos[1] + self.anchor_pos[1]
                    self.show_nail = False

                # 2. Init values
                if not hasattr(self, "vx"): self.vx = 0
                if not hasattr(self, "vy"): self.vy = 0
                if not hasattr(self, "mass"): self.mass = 1
                if not hasattr(self, "rope_length"):
                    dx = self.pos[0] - anchor_x
                    dy = self.pos[1] - anchor_y
                    self.rope_length = max(10, (dx**2 + dy**2)**0.5)

                # 3. Apply gravity
                self.vy += self.currentGravity  # Feel free to tweak this

                # 4. Update position from velocity
                self.pos = (self.pos[0] + self.vx, self.pos[1] + self.vy)

                # 5. Rope soft constraint (spring effect)
                dx = self.pos[0] - anchor_x
                dy = self.pos[1] - anchor_y
                dist = (dx**2 + dy**2)**0.5

                if dist > self.rope_length:
                    stretch = dist - self.rope_length
                    pull_strength = 0.3  # How elastic it feels; tweak this!
                    nx, ny = dx / dist, dy / dist  # Normalize direction

                    # Apply spring-like force
                    self.vx -= nx * stretch * pull_strength
                    self.vy -= ny * stretch * pull_strength

                # 6. Damping
                self.vx /= self.friction
                self.vy /= self.friction
            else:
                self.show_nail = False # if not connected

        
    def start_screen_switch(self, screen, screenSwitcher):
        screenSwitcher.start(lambda: self.next_screen(screen))
        
    def set_position(self, pos):
        self.pos = pos

    def get_scaled_hitbox(self, screensize):
        # Compute scale based on screen size
        x_scale = screensize[0] / 480
        y_scale = screensize[1] / 270
        scale = min(x_scale, y_scale)

        # Scale dimensions
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)

        # Return rect with scaled size at position
        return pygame.Rect(self.pos[0], self.pos[1], width, height)

