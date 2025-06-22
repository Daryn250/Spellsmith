import pygame

class GUIManager:
    def __init__(self):
        self.windows = []  # List of GUI windows (only first one will be drawn)
        self.nails = []
        self.drawCharmBoard = True
        self.charmboard_topright = None

        self.quick_menu = None  # Optional QuickMenu to draw

        # Load charmboard image
        self.charmboard_img = pygame.image.load("assets/gui/charm_board/charm_board.png").convert_alpha()

    def update(self, dt, mouse):
        # Update quick menu animation if present
        if self.quick_menu:
            self.quick_menu.update(dt, mouse)

    def draw(self, screen, screensize):
        screen_width, screen_height = screen.get_size()

        # Draw charmboard
        if self.drawCharmBoard:
            img_width, img_height = self.charmboard_img.get_size()
            scaled = (img_width * (screensize[0] / 480), img_height * (screensize[1] / 270))
            new_img = pygame.transform.scale(self.charmboard_img, scaled)

            top_right_pos = (screen_width - scaled[0] * 1.25, 25)  # Align to top-right corner
            screen.blit(new_img, top_right_pos)
            self.charmboard_topright = top_right_pos

        # Draw nails
        for img, x, y in self.nails:
            screen.blit(img, (x, y))
        self.nails.clear()

        # Draw only the topmost (first) window
        if self.windows:
            window = self.windows[0]
            if hasattr(window, "update_position"):
                window.update_position()
            window.draw(screen)

        # Draw radial quick menu, if present
        if self.quick_menu:
            self.quick_menu.draw(screen)
