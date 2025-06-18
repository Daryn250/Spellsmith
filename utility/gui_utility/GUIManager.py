import pygame

class GUIManager:
    def __init__(self):
        self.windows = []
        self.drawCharmBoard = True

        # Load charmboard image
        self.charmboard_img = pygame.image.load("assets/gui/charm_board/charm_board.png").convert_alpha()

    def draw(self, screen, screensize):
        screen_width, screen_height = screen.get_size()

        if self.drawCharmBoard:
            img_width, img_height = self.charmboard_img.get_size()
            scaled = (img_width* (screensize[0]/480), img_height* (screensize[1]/270))
            new_img = pygame.transform.scale(self.charmboard_img, scaled)

            top_right_pos = (screen_width - scaled[0]*1.25, 25)  # Align to top-right corner
            screen.blit(new_img, top_right_pos)

        # Draw all GUI windows
        for window in self.windows:
            if hasattr(window, "update_position"):
                window.update_position()
            window.draw(screen)
