import pygame
from .bag_manager import BagManager
from .bag_window import BagWindow
from utility.item_utility.trickAnimation import TrickAnimation
from utility.gui_utility.QuickScreenSwitcherWindow import QuickScreenSwitcherWindow
from utility.screen_utility.screenManager import get_all_screen_functions, get_formatted_screen_name


class GUIManager:
    def __init__(self, screen, charmboard=True, bag=True):
        self.windows = []  # List of GUI windows (only first drawn)
        self.nails = []
        self.drawCharmBoard = charmboard
        self.charmboard_topright = None

        self.drawBag = bag
        self.bag_manager = BagManager(capacity=50)
        self.bag_window = BagWindow(self.bag_manager)

        self.quick_menu = None  # Optional QuickMenu

        self.charmboard_img = pygame.image.load("assets/gui/charm_board/charm_board.png").convert_alpha()
        self.bag_img_closed = pygame.image.load("assets/gui/bag/bag1.png").convert_alpha()
        self.bag_img_open = pygame.image.load("assets/gui/bag/bag2.png").convert_alpha()
        self.bag_img = self.bag_img_closed  # current bag icon

        screen_funcs = get_all_screen_functions()
        screen_names = [(get_formatted_screen_name(name), name) for name in screen_funcs]
        self.screenMenu = QuickScreenSwitcherWindow(screen_names, self.switch_to_screen, screen)
        self.arrow_rect = pygame.Rect(0, 0, 40, 40)  # Set properly in draw()
        self.screen_menu_rect =pygame.Rect(
    self.screenMenu.pos[0], 
    self.screenMenu.pos[1], 
    self.screenMenu.width, 
    self.screenMenu.scroll_area_height
)



    def update(self, dt, mouse, virtual_size):
        if self.screenMenu:
            self.screenMenu.update(dt, mouse)

        if self.bag_window in self.windows:
            self.bag_window.update(virtual_size, dt, self)

    def handleEvent(self, event, mouse):
        if self.arrow_rect.collidepoint(mouse):
            self.screenMenu.visible = True
        elif self.screen_menu_rect.collidepoint(mouse) and self.screenMenu.visible == True:
            self.screenMenu.visible = True
        else:
            self.screenMenu.visible = False

        self.screenMenu.handle_event(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.bag_manager.bag_rect and self.bag_manager.bag_rect.collidepoint(mouse):
                self.toggle_bag_window()

        if self.bag_window in self.windows:
            self.bag_window.handle_event(event)


    def toggle_bag_window(self):
        # Position bag window relative to bag icon
        bag_rect = self.bag_manager.bag_rect
        topleft = (bag_rect.right + 5, bag_rect.top - 155)  # fixed height offset

        self.bag_window.original_pos = topleft
        self.bag_window.pos = topleft  # reset position for animation

        if self.bag_window in self.windows:
            # Start closing animation
            def remove_window_when_done(_):
                if self.bag_window in self.windows:
                    self.windows.remove(self.bag_window)

            self.bag_window.animation = TrickAnimation(close_animation, on_complete=remove_window_when_done)
            self.bag_window.animation.reset()
            self.bag_img = self.bag_img_closed
        else:
            # Start opening animation
            self.bag_window.animation = TrickAnimation(open_animation)
            self.bag_window.animation.reset()
            self.windows.insert(0, self.bag_window)
            self.bag_img = self.bag_img_open

        self.bag_manager.hover_info = None

    def switch_to_screen(self, screen, screen_name):
        import utility.screen_utility.screenManager as screen_manager  # avoid circular import

        func = screen_manager.get_screen_function(screen_name)
        switcher = screen.switcher
        switcher.start(
            next_screen_func=lambda: func(screen.screen),
            save_callback=lambda: screen.save_items("saves/save1.json")
        )


    def draw(self, screen, screensize, mouse_pos, item_manager):
        screen_width, screen_height = screen.get_size()
        dragged_item = item_manager.get_dragged()

        # ---- Charmboard ----
        if self.drawCharmBoard:
            img_width, img_height = self.charmboard_img.get_size()
            scale_x = screensize[0] / 480
            scale_y = screensize[1] / 270
            scaled_size = (int(img_width * scale_x), int(img_height * scale_y))

            new_img = pygame.transform.scale(self.charmboard_img, scaled_size)
            top_right_pos = (screen_width - scaled_size[0] * 1.25, 25)
            screen.blit(new_img, top_right_pos)
            self.charmboard_topright = top_right_pos

        # ---- Bag Icon ----
        if self.drawBag:
            bag_width, bag_height = self.bag_img.get_size()
            scale_x = screensize[0] / 480
            scale_y = screensize[1] / 270
            bag_scaled = (int(bag_width * scale_x), int(bag_height * scale_y))

            bag_img_scaled = pygame.transform.scale(self.bag_img, bag_scaled)
            bottom_left_pos = (25, screen_height - bag_scaled[1] - 25)
            screen.blit(bag_img_scaled, bottom_left_pos)

            # Update bag hover rect
            self.bag_manager.bag_rect = pygame.Rect(bottom_left_pos, bag_scaled)
            self.bag_manager.update(mouse_pos)

            # Optional hover info
            if self.bag_manager.hover_info:
                font = pygame.font.SysFont(None, 20)
                info_pos = (bottom_left_pos[0] + bag_scaled[0] + 10, bottom_left_pos[1])
                self.bag_manager.hover_info.draw(screen, info_pos, font)

        # ---- Draw Charm Nails ----
        for img, x, y in self.nails:
            screen.blit(img, (x, y))
        self.nails.clear()

        # ---- Draw Top-Level Windows (like the Bag) ----
        if self.windows:
            window = self.windows[0]

            # Allow window to update its position if animating
            if hasattr(window, "update_position"):
                window.update_position()

            # Special-case for BagWindow: pass dragged item for interaction
            if window == self.bag_window:
                window.draw(screen, window.pos, mouse_pos, screensize, dragged_item)
            else:
                window.draw(screen, window.pos, mouse_pos, screensize)

        # ---- Draw screen switcher menu ----
        if self.screenMenu:
            self.screenMenu.draw(screen)

        # Draw arrow (screen switch toggle)
        arrow_color = (255, 255, 255) if self.screenMenu.visible else (100, 100, 100)
        arrow_pos = (screen_width - 50, screen_height - 50)
        self.arrow_rect.topleft = arrow_pos
        pygame.draw.polygon(screen, arrow_color, [
            (arrow_pos[0], arrow_pos[1]),
            (arrow_pos[0] + 20, arrow_pos[1] + 10),
            (arrow_pos[0], arrow_pos[1] + 20)
        ])

        # Update screen menu position and rect
        self.screenMenu.pos = (arrow_pos[0] - 140, arrow_pos[1] - 120)
        self.screen_menu_rect = pygame.Rect(self.screenMenu.pos[0], self.screenMenu.pos[1], self.screenMenu.width, len(self.screenMenu.screen_names) * self.screenMenu.entry_height)
        self.screenMenu.draw(screen)

    def save_bag(self, filepath):
        self.bag_manager.save_bag(filepath)

open_animation = [
    {"time": 0.0, "scale": (0.0, 0.0)},
    {"time": 0.2, "scale": (1.1, 1.1)},
    {"time": 0.4, "scale": (1.0, 1.0)},
]

close_animation = [
    {"time": 0.0, "scale": (1.0, 1.0)},
    {"time": 0.1, "scale": (1.1, 1.1)},
    {"time": 0.2, "scale": (0.0, 0.0)},
]
