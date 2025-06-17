import pygame
import os
import uuid
from utility.animated_sprite import AnimatedTile

class defaultItem:
    def __init__(self, img_path, pos, type, flags=None, animated=False, frameDuration=100, uuidSave=None, friction = 1.05, next_screen = None, origin_screen = None):
        if not img_path or not os.path.exists(img_path):
            img_path = "assets/error.png"
        self.img_path = img_path
        self.animated = animated

        self.type = type

        if animated:
            self.img = AnimatedTile(img_path, frame_duration=frameDuration)
        else:
            self.img = pygame.image.load(img_path).convert_alpha()

        self.pos = pos
        self.flags = flags or []
        self.frameDuration = frameDuration
        self.uuid = uuidSave or str(uuid.uuid4())

        # for saving
        self.origin_screen = origin_screen

        # for the draggable flag
        self.rotation = 0.0
        self.rotational_velocity = 0.0

        self.vx = 0
        self.vy = 0

        self.friction = friction
        self.currentGravity = 0.3
        self.storedGravity = 0.3

        self.floor = pos[1]
        self.dragging = False

        # for the screen_change flag
        self.next_screen = next_screen

        # for the charm class:
        self.is_hovered = False
        self.on_hover = None
        self.on_unhover = None

    
    @property
    def image(self):
        if self.animated:
            return self.img.get_current_frame()
        return self.img

    def draw(self, surface):
        img = self.image
        angle = -self.rotation  # Invert for natural lean direction

        # Draw shadow
        shadow_width = img.get_width() * 0.8
        shadow_height = img.get_height() * 0.2
        shadow_alpha = 100 if not self.dragging else 20
        shadow_surface = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surface, (0, 0, 0, shadow_alpha), shadow_surface.get_rect())

        shadow_x = self.pos[0] + (img.get_width() - shadow_width) / 2
        shadow_y = self.floor + img.get_height()*0.75  # Centered on floor
        surface.blit(shadow_surface, (shadow_x, shadow_y))

        # Draw rotated image
        rotated_img = pygame.transform.rotate(img, angle)
        rect = rotated_img.get_rect(center=(self.pos[0] + img.get_width() // 2,
                                            self.pos[1] + img.get_height() // 2))
        


        surface.blit(rotated_img, rect.topleft)

    def update(self, screen, dt=None):
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
                # play hit sound
        
        

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

    def start_screen_switch(self, screen, screenSwitcher):
        screenSwitcher.start(lambda: self.next_screen(screen))
        
    def set_position(self, pos):
        self.pos = pos

    def get_rect(self):
        return self.img.get_rect(topleft=self.pos)
