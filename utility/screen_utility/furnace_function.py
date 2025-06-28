import pygame
import random

class FurnaceHelper:
    def __init__(self, item_manager):
        self.item_manager = item_manager
        self.heat_active = False
        self.fuel_level = 1  # Goes from 0 to 1

        # Load images
        self.img_border = pygame.image.load("assets/screens/furnace/border.png").convert_alpha()
        self.img_icons = pygame.image.load("assets/screens/furnace/icons.png").convert_alpha()
        self.img_glow = pygame.image.load("assets/screens/furnace/glow.png").convert_alpha()
        self.img_coal = pygame.image.load("assets/screens/furnace/coal.png").convert_alpha()

        self.base_virtual = (480, 270)  # Reference resolution

        self.glow_alpha = 0  # Current alpha of glow image
        self.glow_speed = 300  # milliseconds it takes to fully fade in or out

        self.coal_shake_timer = 0
        self.coal_shake_amount = 1  # pixels of shake intensity
        self.coal_lerp_offset = 0   # easing offset when fuel is added
        self.coal_lerp_speed = 0.005  # lower is slower easing



    def update(self, dt, item_manager):
        MAX_FUEL = 1.0  # Maximum stored fuel level
        BASE_DRAIN_RATE = dt / 100000  # base drain rate for 1 item

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

                    item_manager.remove_item(fuel_item.uuid)
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
            drain_amount = BASE_DRAIN_RATE * active_heating_items
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


        # ----- COAL DRAW (coal lowers as fuel lowers) -----
        coal_img_scaled = pygame.transform.scale(self.img_coal, virtual_size)

        # Total vertical travel range of coal (in virtual pixels)
        coal_start_y = 62
        max_offset = coal_start_y

        # Compute vertical offset from full (0) to empty (max_offset)
        offset_y_virtual = int((1 - self.fuel_level) * max_offset)

        # Add easing (coal shifts slightly upward after adding fuel)
        eased_offset = int(-10 * (1 - (self.coal_lerp_offset ** 2)))  # smooth ease up

        # Add jitter if shaking
        shake_x = shake_y = 0
        if self.coal_shake_timer > 0:
            shake_x = random.randint(-self.coal_shake_amount, self.coal_shake_amount)
            shake_y = random.randint(-self.coal_shake_amount, self.coal_shake_amount)

        # Convert to screen offset
        screen_offset_y = int((offset_y_virtual + eased_offset) * sy)

        # Draw the entire coal image, just offset down based on fuel level
        surface.blit(coal_img_scaled, (shake_x, screen_offset_y + shake_y))




        draw_scaled(self.img_border)

    def get_save_data(self):
        return {"furnaceScreen": {
        "fuel_level": self.fuel_level
        }
    }
    def load_from_data(self, data):
        self.fuel_level = data.get("fuel_level", 1.0)


