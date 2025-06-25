import pygame

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


    def update(self, dt, item_manager):
        # Calculate fuel burn time decay
        if self.fuel_level > 0 and self.heat_active:
            self.fuel_level -= dt / 300000  # adjust rate if needed
            self.fuel_level = max(0.0, self.fuel_level)

        self.heat_active = False  # Reset, will turn True if any slot is heating

        # List of all slot names to heat
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

            # Check if item can be heated (either tool or regular item)
            if hasattr(item, "temperature"):
                if self.fuel_level > 0:
                    if item.temperature > getattr(item, "melting_point", 99999):
                        # play melting animation and delete item
                        pass
                    else:
                        item.temperature += dt / 100  # adjust heating rate here
                        print(item.temperature)
                        self.heat_active = True
                
        target_alpha = 255 if self.heat_active else 0
        alpha_diff = target_alpha - self.glow_alpha
        if abs(alpha_diff) > 0:
            # Change rate is proportional to time
            delta = (dt / self.glow_speed) * 255
            self.glow_alpha += delta if alpha_diff > 0 else -delta
            self.glow_alpha = max(0, min(255, self.glow_alpha))



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


        # ----- COAL DRAW -----
        coal_start_y = 62  # virtual pixels
        max_offset = coal_start_y

        offset_y_virtual = int((1 - self.fuel_level) * max_offset)
        coal_img_scaled = pygame.transform.scale(self.img_coal, virtual_size)
        screen_offset_y = int(offset_y_virtual * sy)

        clip_start_y = int(coal_start_y * sy)
        clip_height = virtual_size[1] - clip_start_y
        clip_rect = pygame.Rect(0, clip_start_y, virtual_size[0], clip_height)

        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        surface.blit(coal_img_scaled, (0, screen_offset_y))
        surface.set_clip(prev_clip)

        draw_scaled(self.img_border)



