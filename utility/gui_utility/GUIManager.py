import pygame
from .bag_manager import BagManager
from .bag_window import BagWindow
from utility.item_utility.trickAnimation import TrickAnimation

class GUIManager:
    def __init__(self, charmboard = True, bag = True):
        self.windows = []  # List of GUI windows (only first one will be drawn)
        self.nails = []
        self.drawCharmBoard = charmboard
        self.charmboard_topright = None

        self.drawBag = bag
        self.bag_manager = BagManager(capacity=50)
        self.bag_window = BagWindow(self.bag_manager)

        self.quick_menu = None  # Optional QuickMenu to draw

        # Load charmboard image
        self.charmboard_img = pygame.image.load("assets/gui/charm_board/charm_board.png").convert_alpha()
        self.bag_img = pygame.image.load("assets/gui/bag/bag1.png").convert_alpha()

    def update(self, dt, mouse, virtual_size):
        # Update quick menu animation if present
        if self.quick_menu:
            self.quick_menu.update(dt, mouse)
        
        if self.bag_window in self.windows:
            self.bag_window.update(virtual_size, dt)

    def handleEvent(self, event, mouse):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right-click
            if self.bag_manager.bag_rect and self.bag_manager.bag_rect.collidepoint(mouse):
                if self.bag_window in self.windows:
                    bag_rect = self.bag_manager.bag_rect
                    bag_window_width = self.bag_window.columns * (self.bag_window.slot_size + self.bag_window.spacing) + self.bag_window.bg_padding * 2 - self.bag_window.spacing
                    bag_window_height = self.bag_window.visible_rows * (self.bag_window.slot_size + self.bag_window.spacing) + self.bag_window.bg_padding * 2 - self.bag_window.spacing

                    topleft = (
                        bag_rect.right,
                        bag_rect.top - bag_window_height
                    )

                    self.bag_window.original_pos = topleft
                    self.bag_window.pos = topleft  # Reset pos for animation

                    # Define the close animation with a callback
                    def remove_window_when_done(item):
                        if self.bag_window in self.windows:
                            self.windows.remove(self.bag_window)

                    self.bag_window.animation = TrickAnimation(close_animation, on_complete=remove_window_when_done)
                    self.bag_window.animation.reset()
                    self.bag_img = pygame.image.load("assets/gui/bag/bag1.png").convert_alpha()
                else:
                    # Position where window should end up
                    bag_rect = self.bag_manager.bag_rect
                    bag_window_width = self.bag_window.columns * (self.bag_window.slot_size + self.bag_window.spacing) + self.bag_window.bg_padding * 2 - self.bag_window.spacing
                    bag_window_height = self.bag_window.visible_rows * (self.bag_window.slot_size + self.bag_window.spacing) + self.bag_window.bg_padding * 2 - self.bag_window.spacing

                    topleft = (
                        bag_rect.right,
                        bag_rect.top - bag_window_height
                    )

                    self.bag_window.original_pos = topleft
                    self.bag_window.pos = topleft  # Ensure initial pos
                    self.bag_window.animation = TrickAnimation(open_animation,)
                    self.bag_window.animation.reset()

                    self.windows.insert(0, self.bag_window)
                    self.bag_img = pygame.image.load("assets/gui/bag/bag2.png").convert_alpha()

                self.bag_manager.hover_info = None
        if self.bag_window in self.windows:
            self.bag_window.handle_event(event)


            

    def draw(self, screen, screensize, mouse_pos):
        screen_width, screen_height = screen.get_size()

        # Draw charmboard
        if self.drawCharmBoard:
            img_width, img_height = self.charmboard_img.get_size()
            scaled = (img_width * (screensize[0] / 480), img_height * (screensize[1] / 270))
            new_img = pygame.transform.scale(self.charmboard_img, scaled)

            top_right_pos = (screen_width - scaled[0] * 1.25, 25)  # Align to top-right corner
            screen.blit(new_img, top_right_pos)
            self.charmboard_topright = top_right_pos

        # Draw bag
        if self.drawBag:
            bag_width, bag_height = self.bag_img.get_size()
            bag_scaled = (
                bag_width * (screensize[0] / 480),
                bag_height * (screensize[1] / 270)
            )
            bag_img_scaled = pygame.transform.scale(self.bag_img, bag_scaled)

            bottom_left_pos = (25, screen_height - bag_scaled[1] - 25)
            screen.blit(bag_img_scaled, bottom_left_pos)

            # Update bag manager hover logic
            self.bag_manager.bag_rect = pygame.Rect(bottom_left_pos, bag_scaled)
            self.bag_manager.update(mouse_pos)

            # Draw hover info
            if self.bag_manager.hover_info:
                font = pygame.font.SysFont(None, 20)
                info_pos = (bottom_left_pos[0] + bag_scaled[0] + 10, bottom_left_pos[1])
                self.bag_manager.hover_info.draw(screen, info_pos, font)

        # Draw nails
        for img, x, y in self.nails:
            screen.blit(img, (x, y))
        self.nails.clear()

        # Draw only the topmost (first) window
        if self.windows:
            window = self.windows[0]
            if hasattr(window, "update_position"):
                window.update_position()
            if isinstance(window, BagWindow):
                # Adjust position so bag window's bottom-left is aligned with bag icon's top-right
                bag_rect = self.bag_manager.bag_rect
                bag_window_width = window.columns * (window.slot_size + window.spacing) + window.bg_padding * 2 - window.spacing
                bag_window_height = window.visible_rows * (window.slot_size + window.spacing) + window.bg_padding * 2 - window.spacing

                topleft = (
                    bag_rect.right,
                    bag_rect.top - bag_window_height
                )
                window.draw(screen, topleft)
            else:
                window.draw(screen)



        # visual polish on bag menu and functionality for dragging and dropping
        # if bag full throw item in opposite dir or something idk lol

        # Draw radial quick menu, if present
        if self.quick_menu:
            self.quick_menu.draw(screen)


open_animation = [
    {"time": 0.0, "scale": (0.0, 0.0)},  # start invisible and slightly below
    {"time": 0.2, "scale": (1.1, 1.1)},  # overshoot
    {"time": 0.4, "scale": (1.0, 1.0)},     # settle
]
close_animation = [
    {"time": 0.0, "scale": (1.0, 1.0)},  # start invisible and slightly below
    {"time": 0.1, "scale": (1.1, 1.1)},  # overshoot
    {"time": 0.2, "scale": (0.0, 0.0)},     # settle
]
