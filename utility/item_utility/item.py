import pygame
import os
import uuid
import random
from utility.animated_sprite import AnimatedTile
from utility.item_utility.charmWindows import returnCharmWindow
from utility.screen_utility.screenManager import *
from utility.particle import make_scale


class defaultItem:
    def __init__(self, manager, type, pos, nbt_data = {}):

        self.manager = manager

        self.nbt =dict(nbt_data)

        self.type = type or "undefined_itemType"
        self.pos = pos

        self.__dict__.update(self.nbt)



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
        if not hasattr(self, "scale"):
            self.scale = [1,1]
        
        self.particles = []
        
        if not hasattr(self, "anchor_pos") and "hangable" in self.flags:
            self.anchor_pos = None
            self.anchor = None
        
        if self.animated:
            self.img = AnimatedTile(self.img_path, frame_duration=self.frameDuration)
        else:
            self.img = pygame.image.load(self.img_path).convert_alpha()



        # for the draggable flag
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

        # for the charm class:
        if "charm" in self.flags:
            self.is_clicked = False

        # for the hanging class
        if "hangable" in self.flags:
            self.NAIL_IMAGE = pygame.image.load("assets/gui/charm_board/nail.png").convert_alpha()
            self.attached_to = None
            self.show_nail = False


    def to_nbt(self, exclude=["manager", "pos", "type", "is_hovered", "img", "ovx", "ovy", "floor", "dragging", "nbt", "window", "NAIL_IMAGE", "trick", "particles"]):
        return {k: v for k, v in self.__dict__.items() if k not in exclude}

    def draw_at(self, surface, pos, size=None):
        if self.image is None:
            return

        # Use base size if not provided
        if size is None:
            size = (self.image.get_width(), self.image.get_height())

        # Scale image
        image = pygame.transform.scale(self.image, size)

        # Optional: draw shadow
        shadow = image.copy()
        shadow.fill((0, 0, 0, 100), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(shadow, (pos[0], pos[1] + 10))

        # Draw image centered at pos
        draw_x = pos[0] - image.get_width() // 2
        draw_y = pos[1] - image.get_height() // 2
        surface.blit(image, (draw_x, draw_y))

    @property
    def image(self):
        if self.animated:
            return self.img.get_current_frame()
        return self.img

    def draw(self, surface, screensize, gui_manager, item_manager, rotation_scale):
        if "invisible" in self.flags:
            return  # skip drawing logic :D it's invisible

        angle = -getattr(self, "rotation", 0)  # Invert for natural lean direction

        # Compute scale based on screen resolution
        s = getattr(self, "scale", (1, 1))
        x_scale = (screensize[0] / 480) * s[0]
        y_scale = (screensize[1] / 270) * s[1]
        scale = min(x_scale, y_scale)  # Use uniform scaling to preserve aspect ratio

        # Scale image
        original_img = self.image
        scaled_size = (
            int(original_img.get_width() * scale),
            int(original_img.get_height() * scale)
        )
        img = pygame.transform.scale(original_img, scaled_size)

        # Compute center point
        center_x, center_y = self.pos  # self.pos is now treated as the CENTER

        # Rotate image around its center
        rotated_img = pygame.transform.rotate(img, angle)
        rotated_rect = rotated_img.get_rect(center=(center_x, center_y))

        # Draw shadow
        if "no_shadow" not in self.flags:
            shadow_width = img.get_width() * 0.8
            shadow_height = img.get_height() * 0.2
            shadow_alpha = 100 if getattr(self, "dragging", False) else 20
            shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect())

            shadow_x = center_x - shadow_width / 2
            if hasattr(self, "floor"):
                shadow_y = self.floor + img.get_height() * 0.75  # Centered on floor
            else:
                shadow_y = center_y + img.get_height() * 0.75 / 2
            surface.blit(shadow_surface, (shadow_x, shadow_y))

        # Draw outline if clicked
        if getattr(self, "is_clicked", False):
            mask = pygame.mask.from_surface(rotated_img)
            outline_points = mask.outline()
            if outline_points:
                offset_outline = [(x + rotated_rect.left, y + rotated_rect.top) for x, y in outline_points]
                pygame.draw.polygon(surface, (255, 255, 255), offset_outline, width=3)

        # Draw rope if anchored
        if "hangable" in self.flags and hasattr(self, "anchor_pos") and self.anchor_pos:
            img_w, img_h = img.get_size()

            if self.anchor == "charmboard":
                rope_start = self.anchor_pos[0] + img_w // 2, self.anchor_pos[1]
            else:
                anchor_item = item_manager.getItemByUUID(self.anchor)
                rope_start = anchor_item.pos[0], anchor_item.pos[1]  # Assuming center-based too

            rope_end = (center_x, center_y - img_h // 2 + img_h // 6)

            mid_x = (rope_start[0] + rope_end[0]) / 2
            mid_y = (rope_start[1] + rope_end[1]) / 2 + 2  # Sag

            pygame.draw.lines(surface, (34, 32, 52), False, [
                rope_start,
                (mid_x, mid_y),
                rope_end
            ], width=2)

            if getattr(self, "show_nail", False):
                x, y = rope_start
                gui_manager.nails.append([self.NAIL_IMAGE, x, y])

        # Temperature-based overlay using alpha mask
        if hasattr(self, "temperature"):
            temp = self.temperature
            max_temp = 1000
            glow_strength = min(1.0, temp / max_temp)

            if glow_strength > 0.01:
                # Create a glow surface with the same size
                glow_surface = pygame.Surface(rotated_img.get_size(), pygame.SRCALPHA)

                # Create a mask from the rotated image
                mask = pygame.mask.from_surface(rotated_img)
                outline_surface = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

                # Tint the white surface red-orange based on temperature
                tint_color = (int(255 * glow_strength), int(32 * glow_strength), 0, int(160 * glow_strength))
                tint_surface = pygame.Surface(rotated_img.get_size(), pygame.SRCALPHA)
                tint_surface.fill(tint_color)

                # Use the mask to apply tint only where visible
                outline_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                # Additive blend onto the rotated image
                rotated_img.blit(outline_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
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
                        ring_radius = int(rotated_img.get_width() * (0.6 + 0.2 * i) * glow_strength)
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
                                (center_x - ring_radius, center_y - ring_radius),
                                special_flags=pygame.BLEND_RGB_ADD
                            )
        # Finally draw the rotated image centered at self.pos
        surface.blit(rotated_img, rotated_rect.topleft)



    def update(self, screen, gui_manager, virtual_size, bounds=None, dt=None):
        """Update physics, animation, and rotation for the item."""
        if self.animated:
            if dt:
                self.img.update(dt)
            else:
                print("dt not defined, exiting pygame")
                pygame.quit()

        if "draggable" in self.flags:
            self.rotation += self.rotational_velocity
            self.rotational_velocity *= 0.85
            if abs(self.rotation) < 0.1:
                self.rotation = 0.0
                self.rotational_velocity = 0.0
            else:
                self.rotation *= 0.9

            # 📦 Use bounded area if provided (like for BagWindow), otherwise screen
            if bounds is not None and self in gui_manager.bag_manager.contents and getattr(self, "state", None) == "bagged":
                screenX, screenY, screenW, screenH = bounds
            elif screen is not None:
                screenX, screenY, screenW, screenH = 0, 0, screen.get_width(), screen.get_height()
            else:
                screenX, screenY, screenW, screenH = 0, 0, 480, 270  # fallback


            currentX, currentY = self.pos

            # Apply velocity if not being dragged
            if not self.dragging:
                currentX += self.vx
                currentY += self.vy

            self.vx /= self.friction
            self.vy += self.currentGravity

            # Bounds — use scaled image if possible
            if hasattr(self, "get_scaled_size"):
                item_width, item_height = self.get_scaled_size(virtual_size)
            else:
                item_width, item_height = self.image.get_size()

            half_width = item_width // 2
            half_height = item_height // 2

            # Floor bounce
            if not self.dragging and self.vy > 0:
                if currentY > self.floor:
                    currentY = self.floor
                    self.vy = 0
                    self.vx /= 1.5
            
            if not self.dragging:

            # Edge bounds
                if currentX - half_width < screenX:
                    currentX = screenX + half_width
                    self.vx = abs(self.vx) / 1.1

                if currentX + half_width > screenX + screenW:
                    currentX = screenX + screenW - half_width
                    self.vx = -abs(self.vx) / 1.1

                if currentY - half_height < screenY:
                    currentY = screenY + half_height
                    self.vy = abs(self.vy) / 1.1

                if currentY + half_height > screenY + screenH:
                    currentY = screenY + screenH - half_height
                    self.vy = abs(self.vy) / 1.1


            self.pos = (currentX, currentY)

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
                self.floor = screen.get_height()-(self.image.get_height()*2)
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

        if getattr(self, "temperature", 0) >= 500:
            if random.random() < self.temperature/50000:  # Tune this spawn rate as needed
                self.particles.extend(make_scale(self.pos, count=1))


        
    def start_screen_switch(self, screen, screenSwitcher):
        if type(self.next_screen) == str:
            self.next_screen = get_screen_function(self.next_screen)
        screenSwitcher.start(lambda: self.next_screen(screen))
        
    def set_position(self, pos):
        self.pos = pos
        if "draggable" in self.flags:
            self.vx = 0
            self.vy = 0
            self.floor = pos[1]
            self.ovx = 0
            self.ovy = 0
            self.rotation = 0

    def get_scaled_hitbox(self, screensize):
        # Compute scale based on screen size
        s = getattr(self, "scale", (1, 1))
        x_scale = screensize[0] / 480 * s[0]
        y_scale = screensize[1] / 270 * s[1]
        scale = min(x_scale, y_scale)

        # Scale dimensions
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)

        # Center hitbox on self.pos (which is now the center of the item)
        top_left_x = int(self.pos[0] - width // 2)
        top_left_y = int(self.pos[1] - height // 2)

        return pygame.Rect(top_left_x, top_left_y, width, height)


    @property
    def uniform_scale(self):
        scale = getattr(self, "scale", 1)
        if isinstance(scale, (int, float)):
            return (scale, scale)
        return scale

