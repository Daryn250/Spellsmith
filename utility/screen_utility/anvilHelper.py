import pygame
from pygame import Surface
from utility.item_utility.item_flags import SlotFlag
from utility.item_utility.itemMaker import makeItem
from utility.button import Button
from utility.minigame_utility.minigameManager import MiniGameManager
from utility.tool_utility.temperatureHandler import get_temp_range

class AnvilHelper:
    def __init__(self, item_manager):
        self.background = pygame.image.load("assets/screens/anvil/anvil.png").convert_alpha()

        # --- Hammer Button ---
        self.hammer_button_img = pygame.image.load("assets/screens/anvil/hammer_button.png").convert_alpha()
        self.hammer_button_img = pygame.transform.scale(self.hammer_button_img, (self.hammer_button_img.get_width()*2, self.hammer_button_img.get_height()*2))
        self.hammer_button = Button(
            image=self.hammer_button_img,
            pos=(0, 0),  # will be repositioned dynamically
            text_input="",  # No text
            font=pygame.font.Font(None, 1),
            base_color=(0, 0, 0),  # Irrelevant
            hovering_color=(0, 0, 0)
        )
        self.hammer_button_visible = False

        self.base_screen = None

        # --- Hammering Window ---
        self.hammer_window_img = pygame.image.load("assets/screens/anvil/hammer_window.png").convert_alpha()
        self.hammering_active = False
        self.hammer_window_y = item_manager.VIRTUAL_SIZE[1]  # Offscreen (you can set to virtual_size[1])
        self.hammer_window_target_y = 0
        self.item_manager = item_manager

        # --- GUI Control Flag ---
        self.hide_gui = False

        self.minigame_manager = None

    
    def update(self, dt, item_manager, virtual_mouse = None, screen = None):
        self.hammer_button_visible = False
        if screen == None:
            raise KeyError("no screen parsed. please parse a screen for this function.")
        # ---- Check if there's a valid item in the slot ----
        slot = item_manager.getSlotByName("anvil_input_1")
        if slot and slot.contains:
            item = item_manager.getItemByUUID(slot.contains)
            if item and not item.dragging:
                temp = getattr(item, "temperature", 0)
                minTemp = get_temp_range(item.material).get("min")
                maxTemp = get_temp_range(item.material).get("max")
                if minTemp <= temp <= maxTemp:
                    self.hammer_button_visible = True
                    # Center button under the item
                    button_x = item.pos[0]
                    button_y = item.pos[1] + 50
                    self.hammer_button.rect.center = (button_x, button_y)
                    self.hammer_button.text_rect.center = (button_x, button_y)
                    self.item_in_slot = item
                    

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

        if self.minigame_manager:
            self.minigame_manager.update(dt, virtual_mouse)
            if self.minigame_manager.finished:
                # delete the item on the anvil and then replace it with the new item, add smoke particles.
                s = self.item_in_slot # if breaks then serious issue cuz how you do that
                item_manager.remove_item(self.item_in_slot.uuid)
                i = self.minigame_manager.selected
                name = i.get("key")
                makeItem(item_manager, name, (slot.pos), screen.screen_name, 
                         {"img_path": f"assets/tools/parts/{name}/{s.material}.png", 
                          "material":s.material, 
                          "mass":s.mass, 
                          "quality":self.minigame_manager.final_grade
                          }
                    )
                print("finished!")
                self.hammering_active = False
                self.minigame_manager = None
                slot.locked = False




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
        if self.minigame_manager:
            self.minigame_manager.draw(surface)


    def handleEvents(self, event, pos, virtual_size, screen):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hammer_button_visible and self.hammer_button.checkForInput(pos):
                if self.hammering_active:
                    self.hammering_active = False
                    self.minigame_manager = None
                    slot = screen.item_manager.getSlotByName("anvil_input_1")
                    slot.locked = False
                    screen.gui_manager.gui_input = True
                else:
                    self.hammering_active = True
                    slot = screen.item_manager.getSlotByName("anvil_input_1")
                    slot.locked = True
                    self.minigame_manager = MiniGameManager(virtual_size, self)
                    screen.gui_manager.gui_input = False
        if self.minigame_manager:
            self.minigame_manager.handle_event(event, pos)



    def get_save_data(self):
        return {
            "anvilScreen": {
            }
        }

    def load_from_data(self, data):
        return
