import pygame
from pygame import Surface
from utility.item_utility.item_flags import SlotFlag
from utility.button import Button

class AnvilHelper:
    def __init__(self, item_manager):
        self.background = pygame.image.load("assets/screens/anvil/anvil.png").convert_alpha()
        self.slot_rect = pygame.Rect(100, 100, 50, 50)  # Replace later with dynamic slot logic

        # --- Hammer Button ---
        self.hammer_button_img = pygame.image.load("assets/screens/anvil/hammer_button.png").convert_alpha()
        self.hammer_button = Button(
            image=self.hammer_button_img,
            pos=(0, 0),  # will be repositioned dynamically
            text_input="",  # No text
            font=pygame.font.Font(None, 1),
            base_color=(0, 0, 0),  # Irrelevant
            hovering_color=(0, 0, 0)
        )
        self.hammer_button_visible = False

        # --- Hammering Window ---
        self.hammer_window_img = pygame.image.load("assets/screens/anvil/hammer_window.png").convert_alpha()
        self.hammering_active = False
        self.hammer_window_y = item_manager.VIRTUAL_SIZE[1]  # Offscreen (you can set to virtual_size[1])
        self.hammer_window_target_y = 0
        self.item_manager = item_manager

        # --- GUI Control Flag ---
        self.hide_gui = False

    def update(self, dt, item_manager):
        self.hammer_button_visible = False

        # ---- Check if there's a valid item in the slot ----
        slot = item_manager.getSlotByName("anvil_input_1")
        if slot and slot.contains:
            item = item_manager.getItemByUUID(slot.contains)
            if item and not item.dragging:
                temp = getattr(item, "temperature", 0)
                if 400 <= temp <= 800:
                    self.hammer_button_visible = True
                    # Center button under the item
                    button_x = item.pos[0]
                    button_y = item.pos[1] + 50
                    self.hammer_button.rect.center = (button_x, button_y)
                    self.hammer_button.text_rect.center = (button_x, button_y)

        # ---- Determine virtual height (safe fallback) ----
        virtual_height = getattr(item_manager, "virtual_size", (0, 1080))[1]

        # ---- Smooth ease toward target ----
        target_y = 0 if self.hammering_active else virtual_height
        delta = target_y - self.hammer_window_y
        easing_speed = 0.015  # How fast the window moves (can tweak)
        self.hammer_window_y += delta * easing_speed * dt

        # ---- Snap to target when close enough ----
        if abs(delta) < 0.5:
            self.hammer_window_y = target_y





    def draw(self, surface: Surface, virtual_size):
        # ---- Scaled background ----
        scaled_bg = pygame.transform.scale(self.background, virtual_size)
        surface.blit(scaled_bg, (0, 0))

        # ---- Hammer button ----
        if self.hammer_button_visible:
            mouse = pygame.mouse.get_pos()
            self.hammer_button.changeColor(mouse)
            self.hammer_button.update(surface)

        
    
    def draw_after_gui(self, surface, virtual_size): # draw after the gui so items and such aren't visible
        # ---- Sliding minigame window ----
        scaled_window = pygame.transform.scale(self.hammer_window_img, virtual_size)
        surface.blit(scaled_window, (0, self.hammer_window_y))

    def handleEvents(self, event, pos):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hammer_button_visible and self.hammer_button.checkForInput(pos):
                self.hammering_active = not self.hammering_active

    def get_save_data(self):
        return {
            "anvilScreen": {
            }
        }

    def load_from_data(self, data):
        return
