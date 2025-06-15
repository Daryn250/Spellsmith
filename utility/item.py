import pygame
import os
import sys
import uuid
from utility.animated_sprite import AnimatedTile

class defaultItem:
    def __init__(self, img_path, pos, flags=None, animated=False, frameDuration=100, uuidSave=None):
        if not img_path or not os.path.exists(img_path):
            img_path = "assets/error.png"
        self.img_path = img_path
        self.animated = animated

        if animated:
            self.img = AnimatedTile(img_path, frame_duration=frameDuration)
        else:
            self.img = pygame.image.load(img_path).convert_alpha()

        self.pos = pos
        self.flags = flags or []
        self.frameDuration = frameDuration
        self.uuid = uuidSave or str(uuid.uuid4())

        # for the draggable flag
        self.rotation = 0.0
        self.rotational_velocity = 0.0

        self.vx = 0
        self.vy = 0
        self.z = 0 # set equal to screensize - y

    
    @property
    def image(self):
        if self.animated:
            return self.img.get_current_frame()
        return self.img


    def draw(self, surface):
        img = self.img
        angle = -self.rotation  # Invert for natural lean direction

        rotated_img = pygame.transform.rotate(img, angle)
        rect = rotated_img.get_rect(center=(self.pos[0] + img.get_width() // 2,
                                            self.pos[1] + img.get_height() // 2))
        surface.blit(rotated_img, rect.topleft)


    def update(self, *args, dt = None):
        """Call all flag functions with self as an argument (future-proofing)."""
        if self.animated:
            if dt:
                self.img.update(dt)
            else:
                print("dt not defined, exiting pygame")
                pygame.quit()
        
        for flag in self.flags:
            if callable(flag):
                flag(self, *args)
        
        if "draggable" in self.flags:
            # Apply rotational velocity to rotation
            self.rotation += self.rotational_velocity

            # Decay rotational velocity over time
            self.rotational_velocity *= 0.85  # Friction

            # Slowly restore rotation to 0 if near
            if abs(self.rotation) < 0.1:
                self.rotation = 0.0
                self.rotational_velocity = 0.0
            else:
                self.rotation *=0.9

    def set_position(self, pos):
        self.pos = pos

    def get_rect(self):
        return self.img.get_rect(topleft=self.pos)
