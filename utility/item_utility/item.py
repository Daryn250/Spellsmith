import pygame
import os
import uuid
from utility.animated_sprite import AnimatedTile
from utility.item_utility.charmWindows import returnCharmWindow


class defaultItem:
    def __init__(self, manager, type, pos, nbt_data = {}):

        self.manager = manager

        self.nbt =dict(nbt_data)

        self.type = type or "undefined_itemType"
        self.pos = pos

        self.__dict__.update(self.nbt)

        if not hasattr(self, "animated"):
            self.animated = False
        if not hasattr(self, "frameDuration") and self.animated:
            self.frameDuration = 100
        if not hasattr(self, "img_path"):
            self.img_path = "assets/error.png"
        if not hasattr(self, "friction"):
            self.friction = 1.05
        if not hasattr(self, "flags"):
            self.flags = []
        
        if not hasattr(self, "anchor_pos") and "hangable" in self.flags:
            self.anchor_pos = None
            self.anchor = None
        
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


    def to_nbt(self, exclude=["manager", "pos", "type", "is_hovered", "img", "ovx", "ovy", "floor", "dragging", "nbt", "window", "NAIL_IMAGE"]):
        return {k: v for k, v in self.__dict__.items() if k not in exclude}


    @property
    def image(self):
        if self.animated:
            return self.img.get_current_frame()
        return self.img

    def draw(self, surface, screensize, gui_manager, item_manager):
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
            x = self.anchor_pos[0] + (nail_img.get_width()*1.5)
            y = self.anchor_pos[1]
            gui_manager.nails.append([nail_img, x, y])

        # Draw rope if anchored
        if "hangable" in self.flags and hasattr(self, "anchor_pos") and self.anchor_pos:
            # Define rope start and end
            if self.anchor == "charmboard":
                rope_start = self.anchor_pos[0]+ img.get_width()//2, self.anchor_pos[1]
            else:
                anchor_item = item_manager.getItemByUUID(self.anchor)
                rope_start = anchor_item.pos[0] + img.get_width()//2, anchor_item.pos[1]+ img.get_height()

            rope_end = (self.pos[0] + img.get_width() // 2, self.pos[1] + img.get_height() // 6)

            # Optionally add rope slack curvature (simple midpoint sag)
            mid_x = (rope_start[0] + rope_end[0]) / 2
            mid_y = (rope_start[1] + rope_end[1]) / 2 + 2  # 10px sag, you can make this dynamic

            # Use quadratic Bézier-style curve approximation (3-point rope)
            pygame.draw.lines(surface, (34, 32, 52), False, [
                rope_start,
                (mid_x, mid_y),
                rope_end
            ], width=2)




        
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
                    anchor_x = self.anchor_pos[0]
                    anchor_y = 25 + self.anchor_pos[1]
                    self.show_nail = True
                else:
                    # get item by uuid
                    anchoritem = self.manager.getItemByUUID(self.anchor)
                    if anchoritem==None:
                        raise LookupError(f"the item with uuid {self.anchor} could not be found")
                    anchor_x = anchoritem.pos[0]
                    anchor_y = anchoritem.pos[1]
                    self.show_nail = False

                # 2. Init values
                if not hasattr(self, "vx"): self.vx = 0
                if not hasattr(self, "vy"): self.vy = 0
                if not hasattr(self, "mass"): self.mass = 1
                if not hasattr(self, "rope_length"):
                    dx = self.pos[0] - anchor_x
                    dy = self.pos[1] - anchor_y
                    self.rope_length = max(20, (dx**2 + dy**2)**0.5)
                if self.rope_length>20:
                    self.rope_length = 20

                # 3. Apply gravity
                self.vy += self.currentGravity

                # 4. Update position from velocity IF NOT DRAGGING
                if not self.dragging:
                    self.pos = (self.pos[0] + self.vx, self.pos[1] + self.vy)

                # 5. Rope soft constraint (spring effect)
                dx = self.pos[0] - anchor_x
                dy = self.pos[1] - anchor_y
                dist = (dx**2 + dy**2)**0.5
                nx, ny = dx / (dist or 1), dy / (dist or 1)

                stretch = dist - self.rope_length
                pull_strength = 0.1  # more gentle for stability
                self.vx -= (nx * stretch * pull_strength)/3
                self.vy -= (ny * stretch * pull_strength)/3

                # 6. Damping
                self.vx *= 0.8
                self.vy *= 0.8

                # Clamp velocities to prevent explosive forces
                max_velocity = 20
                self.vx = max(min(self.vx, max_velocity), -max_velocity)
                self.vy = max(min(self.vy, max_velocity), -max_velocity)

                # 7. Rotational physics
                self.rotational_velocity -= self.vx * 0.01
                self.rotational_velocity *= 0.95

                
                if self.anchor!="charmboard":
                    self.anchor_pos = anchor_x,anchor_x

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

