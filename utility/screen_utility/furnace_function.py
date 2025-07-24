import pygame
import random
from utility.item_utility.baseItem import BaseItem

class FurnaceHelper:
    def __init__(self, item_manager, fuel_level=0):
        self.item_manager = item_manager
        self.heat_active = False
        self.fuel_level = fuel_level  # Always a float, never None

        # Load images
        self.img_border = pygame.image.load("assets/screens/furnace/border.png").convert_alpha()
        self.img_icons = pygame.image.load("assets/screens/furnace/icons.png").convert_alpha()
        self.img_glow = pygame.image.load("assets/screens/furnace/glow.png").convert_alpha()

        self.base_virtual = (480, 270)  # Reference resolution

        self.glow_alpha = 0  # Current alpha of glow image
        self.glow_speed = 300  # milliseconds it takes to fully fade in or out

        self.coal_shake_timer = 0
        self.coal_shake_amount = 1  # pixels of shake intensity
        self.coal_lerp_offset = 0   # easing offset when fuel is added
        self.coal_lerp_speed = 0.005  # lower is slower easing

        # Create CoalItem for display, use current fuel_level
        self.coal_item = CoalItem(
            manager=None,  # Not managed by item_manager
            pos=(0, 0),
            img_path="assets/screens/furnace/coal.png",
            fuel_level=self.fuel_level
        )
        self.items = [self.coal_item]
        


    def update(self, dt, item_manager, mouse, base_screen):
        MAX_FUEL = 1.0  # Maximum stored fuel level
        BASE_DRAIN_RATE = dt / 300000  # base drain rate for 1 item

        self.heat_active = False  # Reset; will be set True if anything gets heated
        active_heating_items = 0

        # ----- HANDLE FUEL INPUT -----
        fuel_slot = item_manager.getSlotByName("fuel_input")
        if fuel_slot and fuel_slot.contains:
            fuel_item = item_manager.getItemByUUID(fuel_slot.contains)
            if fuel_item and getattr(fuel_item, "fuel", 0) > 0:
                available_space = MAX_FUEL - self.fuel_level
                if fuel_item.fuel <= available_space:
                    self.fuel_level += fuel_item.fuel
                    self.fuel_level = min(MAX_FUEL, self.fuel_level)

                    item_manager.remove_item(fuel_item.uuid, base_screen.gui_manager)
                    fuel_slot.contains = None
                    print(f"[Furnace] Consumed fuel item for {fuel_item.fuel} energy. New level: {self.fuel_level:.2f}")

                    # Trigger coal shake and ease-up effect
                    self.coal_shake_timer = 200  # ms
                    self.coal_lerp_offset = 1.0

        # ----- HANDLE HEATING ITEMS -----
        heat_slots = [
            "furnace_input_1", "furnace_input_2", "furnace_input_3",
            "furnace_input_4", "furnace_input_5",
            "weapon_slot1", "weapon_slot2"
        ]

        for slot_name in heat_slots:
            slot = item_manager.getSlotByName(slot_name)
            if not slot or not slot.contains:
                continue

            item = item_manager.getItemByUUID(slot.contains)
            if not item:
                continue

            if hasattr(item, "temperature"):
                if self.fuel_level > 0:
                    if item.temperature > getattr(item, "melting_point", 99999):
                        # TODO: handle melting behavior
                        pass
                    else:
                        item.temperature += dt / 100  # heating rate
                        active_heating_items += 1
                        self.heat_active = True

        # ----- DRAIN FUEL BASED ON ACTIVE HEATED SLOTS -----
        if self.fuel_level > 0 and active_heating_items > 0:
            drain_amount = (BASE_DRAIN_RATE * active_heating_items)
            self.coal_item.draining = drain_amount*dt
            self.fuel_level -= drain_amount
            self.fuel_level = max(0.0, self.fuel_level)

        # ----- Handle glow alpha fade -----
        target_alpha = 255 if self.heat_active else 0
        alpha_diff = target_alpha - self.glow_alpha
        if abs(alpha_diff) > 0:
            delta = (dt / self.glow_speed) * 255
            self.glow_alpha += delta if alpha_diff > 0 else -delta
            self.glow_alpha = max(0, min(255, self.glow_alpha))

        # Handle coal shake timer
        if self.coal_shake_timer > 0:
            self.coal_shake_timer -= dt
            if self.coal_shake_timer < 0:
                self.coal_shake_timer = 0

        # Ease up offset
        if self.coal_lerp_offset > 0:
            self.coal_lerp_offset -= dt * self.coal_lerp_speed
            self.coal_lerp_offset = max(0, self.coal_lerp_offset)

        # ----- COAL OFFSET CALCULATION FOR DRAWING -----
        # Compute vertical offset from full (0) to empty (max_offset)
        coal_start_y = 62
        max_offset = coal_start_y
        offset_y_virtual = int((1 - self.fuel_level) * max_offset)

        # Add easing (coal shifts slightly upward after adding fuel)
        eased_offset = int(-10 * (1 - (self.coal_lerp_offset ** 2)))  # smooth ease up

        # Add jitter if shaking
        shake_x = shake_y = 0
        if self.coal_shake_timer > 0:
            shake_x = random.randint(-self.coal_shake_amount, self.coal_shake_amount)
            shake_y = random.randint(-self.coal_shake_amount, self.coal_shake_amount)

        sy = base_screen.virtual_size[1] / self.base_virtual[1] if hasattr(base_screen, 'virtual_size') else 1
        screen_offset_y = int((offset_y_virtual + eased_offset) * sy)

        # Update CoalItem state
        self.coal_item.update(
            screen=base_screen.virtual_surface,
            gui_manager=base_screen.gui_manager,
            virtual_size=base_screen.virtual_size,
            dt=dt,
            fuel_level=self.fuel_level,
            shake_x=shake_x,
            shake_y=shake_y,
            offset_y=screen_offset_y,
            eased_offset=0
        )
        # Set coal_item.pos to match draw position for correct hitbox/event logic
        self.coal_item.pos = (shake_x, screen_offset_y + 0 + shake_y)


    def draw(self, surface, virtual_size):
        sx = virtual_size[0] / self.base_virtual[0]
        sy = virtual_size[1] / self.base_virtual[1]

        def draw_scaled(img):
            scaled = pygame.transform.scale(img, virtual_size)
            surface.blit(scaled, (0, 0))

        # Always draw icons first
        draw_scaled(self.img_icons)

        # Glow when furnace is heating
        if self.glow_alpha > 0:
            glow = pygame.transform.scale(self.img_glow, virtual_size)
            glow.set_alpha(int(self.glow_alpha))
            surface.blit(glow, (0, 0))

        # Draw CoalItem (handles its own offset, shake, etc)
        self.coal_item.draw(surface, virtual_size)

        draw_scaled(self.img_border)

    def get_save_data(self):
        return  {
        "fuel_level": self.fuel_level
        }
    
    def load_from_data(self, data):
        if data !=False:
            self.fuel_level = data.get("fuel_level", 1.0)
            # Also update coal_item's fuel_level to match
            self.coal_item.fuel_level = self.fuel_level

class CoalItem(BaseItem):
    def __init__(self, manager, pos, img_path, fuel_level=1.0):
        super().__init__(manager, "coal", pos, {"flags":["inspectable"]})
        self.img_path = img_path
        self.img = pygame.image.load(img_path).convert_alpha()
        self.fuel_level = fuel_level
        self.draining = 0
        self.shake_x = 0
        self.shake_y = 0
        self.offset_y = 0
        self.eased_offset = 0
        self.isCoal = True
        self.item_name = "coal_pile"
        
        

    def update(self, screen, gui_manager, virtual_size, dt, fuel_level, shake_x, shake_y, offset_y, eased_offset):
        super().update(screen, gui_manager, virtual_size, dt=dt)
        self.fuel_level = fuel_level
        self.shake_x = shake_x
        self.shake_y = shake_y
        self.offset_y = offset_y
        self.eased_offset = eased_offset

    def draw(self, surface, virtual_size):
        base_w, base_h = 132, 28  # new coal image size
        scale_x = virtual_size[0] / 160
        scale_y = virtual_size[1] / 90
        scaled_w = int(base_w * scale_x)
        scaled_h = int(base_h * scale_y)
        coal_img_scaled = pygame.transform.scale(self.img, (scaled_w, scaled_h))
        # Center X, bottom of image at bottom of screen, offset_y moves the image up
        x = virtual_size[0] // 2
        y = virtual_size[1] - scaled_h + self.offset_y + self.eased_offset + self.shake_y
        draw_x = x - scaled_w // 2
        draw_y = y
        surface.blit(coal_img_scaled, (draw_x, draw_y))

    def get_scaled_hitbox(self, screensize, pos_override=None):
        base_w, base_h = 132, 28
        scale_x = screensize[0] / 160
        scale_y = screensize[1] / 90
        scaled_w = int(base_w * scale_x)
        scaled_h = int(base_h * scale_y)
        x = screensize[0] // 2
        y = screensize[1] - scaled_h + self.offset_y + self.eased_offset + self.shake_y
        return pygame.Rect(x - scaled_w // 2, y, scaled_w, scaled_h)

    def get_fast_bbox(self, screensize, pos_override=None):
        base_w, base_h = 132, 28
        scale_x = screensize[0] / 160
        scale_y = screensize[1] / 90
        scaled_w = int(base_w * scale_x)
        scaled_h = int(base_h * scale_y)
        x = screensize[0] // 2
        y = screensize[1] - scaled_h + self.offset_y + self.eased_offset + self.shake_y
        return pygame.Rect(x - scaled_w // 2, y, scaled_w, scaled_h)


