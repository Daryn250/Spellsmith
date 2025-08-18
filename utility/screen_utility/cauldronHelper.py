import pygame, math
from utility.item_utility.baseItem import BaseItem

class cauldronHelper:
    def __init__(self, item_manager, instance_manager, gui_manager, wave_speed=0.1, wave_height=5):
        self.item_manager = item_manager
        self.gui_manager = gui_manager # annoying but needed for removing items correctly

        # Images
        self.img_border = pygame.image.load("assets/screens/cauldron/base1.png").convert_alpha()
        self.img_bg = pygame.image.load("assets/screens/cauldron/backdrop.png").convert_alpha()

        self.base_virtual = (160, 90)  # logical coordinate space for positioning

        # Create drawer items
        self.top_drawer = DrawerItem(
            manager=item_manager,
            pos=(2, 1),
            closed_img="assets/screens/cauldron/drawers/top_drawer1.png",
            open_img="assets/screens/cauldron/drawers/top_drawer2.png",
            title = "Ingredients Drawer",
            instance_manager= instance_manager,
            gui_manager=gui_manager,
            allowed_types=["ingredients"] # change in the future to be catalysts
        )
        self.bottom_drawer = DrawerItem(
            manager=item_manager,
            pos=(3, 50),
            closed_img="assets/screens/cauldron/drawers/bottom_drawer1.png",
            open_img="assets/screens/cauldron/drawers/bottom_drawer2.png",
            title = "Catalysts Drawer",
            instance_manager= instance_manager,
            gui_manager=gui_manager,
            allowed_types=["catalysts"] # change in future to be ingredients
        )

        self.items = [self.top_drawer, self.bottom_drawer]
        for item in self.items:
            item.all_drawers = self.items

        # Wave animation
        self.wave_phase = 0.0
        self.wave_speed = wave_speed
        self.wave_height = wave_height

        # Upgrades
        self.upgrades = {}

    def update(self, dt, item_manager, mouse, base_screen):
        self.wave_phase = (self.wave_phase + (self.wave_speed * dt / 1000.0) * math.tau) % math.tau

        for drawer in self.items:
            drawer.update(
                screen=base_screen.virtual_surface,
                gui_manager=base_screen.gui_manager,
                virtual_size=base_screen.virtual_size,
                sfx=base_screen.instance_manager.sfx_manager,
                dt=dt
            )

    def handleEvents(self, event, virtual_mouse, virtual_size, basescreen):
        """Call this from your screen's mouse event handler"""
        for item in self.items:
            item.storage_window.handle_event(event, virtual_size, virtual_mouse)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for drawer in self.items:
                if drawer.get_fast_bbox(virtual_size).collidepoint(virtual_mouse):
                    if drawer.pixel_perfect_hit(virtual_mouse, virtual_size):
                        # Close all other drawers first
                        for other in self.items:
                            if other != drawer and other.open:
                                other.open = False
                                other.storage_window.open = False  # force close its window too

                        if drawer.open:
                            basescreen.instance_manager.sfx_manager.play_sound("gui_drawer_close")
                        else:
                            basescreen.instance_manager.sfx_manager.play_sound("gui_drawer_open")
                        drawer.toggle()
                        drawer.mouse_hovering = False


                
        if event.type == pygame.MOUSEMOTION:
            for drawer in self.items:
                if drawer.get_fast_bbox(virtual_size).collidepoint(virtual_mouse):
                    if drawer.pixel_perfect_hit(virtual_mouse, virtual_size):
                        if drawer.mouse_hovering!=True:
                            basescreen.instance_manager.sfx_manager.play_sound("gui_hover")
                        drawer.mouse_hovering = True
                    else:
                        drawer.mouse_hovering = False
                else:
                    drawer.mouse_hovering = False

                    

    def draw(self, surface, virtual_size):
        sx = virtual_size[0] / self.base_virtual[0]
        sy = virtual_size[1] / self.base_virtual[1]

        # Wave background
        bg = pygame.transform.scale(self.img_bg, virtual_size)
        wave_offset = int(math.sin(self.wave_phase) * self.wave_height * sy)
        surface.blit(bg, (0, wave_offset))

        

        # Border
        border_scaled = pygame.transform.scale(self.img_border, virtual_size)
        surface.blit(border_scaled, (0, 0))

        # Draw drawers
        for drawer in self.items:
            drawer.draw(surface, virtual_size)
    
    def draw_after_gui(self, surface, virtual_size):
        for drawer in self.items:
            if drawer.open:
                drawer.storage_window.draw(surface)

    def get_save_data(self):
        return {
            "upgrades": self.upgrades,
            "drawers": {drawer.item_name: drawer.get_save_data() for drawer in self.items}
        }

    def load_from_data(self, data):
        if not data:
            return
        self.upgrades = data.get("upgrades", {})
        drawer_data = data.get("drawers", {})
        for drawer in self.items:
            if drawer.item_name in drawer_data:
                drawer.load_from_data(drawer_data[drawer.item_name])
from utility.gui_utility.searchablewindow import SearchableWindow
from utility.item_utility.itemMaker import makeItem
class DrawerItem(BaseItem):
    def __init__(self, manager, pos, closed_img, open_img, title, instance_manager, gui_manager, allowed_types, all_drawers = None):
        super().__init__(manager, "drawer", pos, {"flags": ["inspectable"]})
        self.closed_img = pygame.image.load(closed_img).convert_alpha()
        self.open_img = pygame.image.load(open_img).convert_alpha()
        self.isDrawer = True
        self.item_name = closed_img.split("/")[-1].replace(".png", "")  # unique name
        self.open = False
        self.mouse_hovering = False

        
        self.base_pos = pos  # (x,y) in 160×90 space
        self.base_size = self.closed_img.get_size()

        self.storage_window = SearchableWindow(title, instance_manager, manager, gui_manager, allowed_types, 25) # manager for the item manager

        self.all_drawers=all_drawers

    def toggle(self):
        if self.all_drawers:
            # Close all other drawers first
            for other in self.all_drawers:
                if other != self and other.open:
                    other.open = False
                    other.storage_window.start_animation(-1)
        # Toggle self
        if self.open:
            self.storage_window.start_animation(-1)
        else:
            self.storage_window.start_animation(1)
        self.open = not self.open
        self.mouse_hovering = False


    def update(self, screen, gui_manager, virtual_size, sfx, dt):
        super().update(screen, gui_manager, virtual_size, sfx_manager=sfx, dt=dt)
        self.storage_window.update(dt)

    def draw(self, surface, virtual_size):
        sx = virtual_size[0] / 160
        sy = virtual_size[1] / 90
        scaled_w = int(self.base_size[0] * sx)
        scaled_h = int(self.base_size[1] * sy)
        draw_x = int(self.base_pos[0] * sx)
        draw_y = int(self.base_pos[1] * sy)
        img = self.open_img if self.open else self.closed_img
        img_scaled = pygame.transform.scale(img, (scaled_w, scaled_h))
        img_rect = img_scaled.get_rect(topleft=(draw_x, draw_y))
        surface.blit(img_scaled, (draw_x, draw_y))
        if self.mouse_hovering and self.open == False:
            mask = pygame.mask.from_surface(img_scaled)
            outline_points = mask.outline()
            if outline_points:
                offset_outline = [(x + draw_x, y + draw_y) for x, y in outline_points]
                pygame.draw.polygon(surface, (255, 255, 255), offset_outline, width=1)
       

    def get_fast_bbox(self, virtual_size, pos_override=None):
        sx = virtual_size[0] / 160
        sy = virtual_size[1] / 90
        scaled_w = int(self.base_size[0] * sx)
        scaled_h = int(self.base_size[1] * sy)
        draw_x = int(self.base_pos[0] * sx)
        draw_y = int(self.base_pos[1] * sy)
        return pygame.Rect(draw_x, draw_y, scaled_w, scaled_h)
    
    def pixel_perfect_hit(self, mouse_pos, virtual_size):
        """Check if mouse is actually over a non-transparent pixel."""
        sx = virtual_size[0] / 160
        sy = virtual_size[1] / 90
        scaled_w = int(self.base_size[0] * sx)
        scaled_h = int(self.base_size[1] * sy)
        draw_x = int(self.base_pos[0] * sx)
        draw_y = int(self.base_pos[1] * sy)

        # Select the correct image and scale
        img = self.open_img if self.open else self.closed_img
        img_scaled = pygame.transform.scale(img, (scaled_w, scaled_h))

        # Create mask and check local pixel position
        mask = pygame.mask.from_surface(img_scaled)
        local_x = mouse_pos[0] - draw_x
        local_y = mouse_pos[1] - draw_y

        if 0 <= local_x < scaled_w and 0 <= local_y < scaled_h:
            return mask.get_at((local_x, local_y))  # 1 if opaque pixel, 0 if transparent
        return False
    
    @property
    def capacity(self):
        """returns a normalized 0-1 value of capacity"""
        return max(len(self.storage_window.items)/self.storage_window.max_capacity, 0)
    

    def get_scaled_mask(self, screensize, pos_override=None):
        """Return a pixel-perfect pygame.Mask scaled to current screen size & scale."""
        s = self.scale
        x_scale = screensize[0] / 480 * s[0]
        y_scale = screensize[1] / 270 * s[1]
        scale = min(x_scale, y_scale)

        # Scale the image to the correct size
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        scaled_img = pygame.transform.smoothscale(self.image, (width, height))

        # Create a mask from the scaled image
        mask = pygame.mask.from_surface(scaled_img)

        # Calculate position
        pos = pos_override if pos_override else self.pos
        mask_pos = (pos[0] - width // 2, pos[1] - height // 2)

        return mask, mask_pos

    def update_hover(self, mouse_pos, virtual_size, use_pos_override=True):
        self.is_hovered = self.mouse_hovering

    def get_save_data(self):
        return self.storage_window.save_data()

    def load_from_data(self, data):
        self.storage_window.load_from_save_data(data)
        pass
