from utility.screen_utility.screenswitcher import ScreenSwitcher
from utility.item_utility.ItemManager import ItemManager
from utility.screen_utility.baseScreen import BaseScreen
from utility.item_utility.itemMaker import makeItem
from utility.settingsManager import *
from utility.animated_sprite import AnimatedTile
from screens.table import table
import pygame
import os
import random

class MapHelper:
    def __init__(self, size, item_manager, settings, background_color=(178, 152, 135)):
        self.map_border = pygame.image.load("assets/screens/map/border.png").convert_alpha()
        self.map_border = pygame.transform.scale(self.map_border, size)
        self.map_border_original = self.map_border.copy()
        self.zoom = 1
        self.pan = [0, 0]  # mutable for lerping
        self.target_zoom = 1
        self.target_pan = [0, 0]
        self.lerp_speed = 5

        self.discovered = settings.discovered_islands
        self.margin_width = [6 * (size[0] / 180), 6 * (size[1] / 90)]
        self.item_manager = item_manager

        self.dragging = False
        self.last_mouse = (0, 0)
        self.background_color = background_color

        # Ocean tiles setup
        self.tile_size = 128  # Scale up tiles for visibility
        self.ocean_tiles = []
        sw, sh = size
        cols = sw // self.tile_size + 3
        rows = sh // self.tile_size + 3
        tile_folder = "assets/ocean/map_ocean"
        for y in range(rows):
            row = []
            for x in range(cols):
                anim_tile = AnimatedTile(tile_folder, frame_duration=1500,scale=(4,4))  # Adjust frame_duration as needed
                row.append(anim_tile)
            self.ocean_tiles.append(row)
        # Animation offset for diagonal movement
        self.ocean_anim_offset = [0.0, 0.0]
        self.ocean_anim_speed = 5  # pixels per second, adjust for desired speed

    def handleEvents(self, event, virtual_mouse, virtual_size, base_screen):
        if event.type == pygame.MOUSEWHEEL:
            old_zoom = self.target_zoom
            # Calculate new zoom
            if event.y > 0:
                new_zoom = old_zoom * 1.1
            else:
                new_zoom = old_zoom * 0.9
            new_zoom = max(0.5, min(3.0, new_zoom))

            # Calculate zoom relative to mouse position
            center_x, center_y = virtual_size[0] // 2, virtual_size[1] // 2
            mouse_x, mouse_y = virtual_mouse

            # Map coords under mouse before zoom
            mouse_map_x = (mouse_x - center_x - self.target_pan[0]) / old_zoom
            mouse_map_y = (mouse_y - center_y - self.target_pan[1]) / old_zoom

            # Update target pan to keep mouse position fixed
            self.target_pan[0] = mouse_x - center_x - mouse_map_x * new_zoom
            self.target_pan[1] = mouse_y - center_y - mouse_map_y * new_zoom

            self.target_zoom = new_zoom

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = True
            self.last_mouse = virtual_mouse

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        if event.type == pygame.MOUSEMOTION and self.dragging:
            dx = virtual_mouse[0] - self.last_mouse[0]
            dy = virtual_mouse[1] - self.last_mouse[1]
            self.target_pan[0] += dx
            self.target_pan[1] += dy
            self.last_mouse = virtual_mouse

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.target_zoom = 1
                self.target_pan = [0, 0]

    def update(self, dt, item_manager, mouse, screen):
        self.zoom += (self.target_zoom - self.zoom) * min(1, self.lerp_speed * dt)
        self.pan[0] += (self.target_pan[0] - self.pan[0]) * min(1, self.lerp_speed * dt)
        self.pan[1] += (self.target_pan[1] - self.pan[1]) * min(1, self.lerp_speed * dt)
        # Animate ocean tiles
        offset_delta = self.ocean_anim_speed * dt / 1000.0
        self.ocean_anim_offset[0] -= offset_delta  # move left
        self.ocean_anim_offset[1] -= offset_delta  # move up
        for row in self.ocean_tiles:
            for anim_tile in row:
                anim_tile.update(dt)
        # ...existing code...

    def draw(self, screen, size):
        map_surface = pygame.Surface(size, pygame.SRCALPHA)
        sw, sh = size
        tile_w, tile_h = self.tile_size, self.tile_size

        # Calculate base screen center and pan + anim offsets
        center_x, center_y = sw // 2, sh // 2
        total_offset_x = self.pan[0] + self.ocean_anim_offset[0]
        total_offset_y = self.pan[1] + self.ocean_anim_offset[1]

        # Get starting tile index and pixel offset for seamless scrolling
        start_x = ((center_x + total_offset_x) % tile_w)
        start_y = ((center_y + total_offset_y) % tile_h)

        # Draw enough tiles to cover the screen plus margin
        for y, row in enumerate(self.ocean_tiles):
            for x, anim_tile in enumerate(row):
                frame = anim_tile.get_current_frame()

                px = (start_x + x * tile_w)
                py = (start_y + y * tile_h)

                map_surface.blit(frame, (px-tile_w, py-tile_h))

        # Draw islands (with scaling and override positioning)
        for item in self.item_manager.items:
            if getattr(item, "type", None) != "island" or "invisible" in item.flags:
                continue

            original_pos = item.pos
            original_scale = item.scale

            offset_x = (original_pos[0] * self.zoom) + self.pan[0]
            offset_y = (original_pos[1] * self.zoom) + self.pan[1]
            draw_pos = (center_x + offset_x, center_y + offset_y)

            item.scale = [s * self.zoom for s in original_scale]
            item.pos_override = draw_pos
            item.draw(map_surface, size, None, self.item_manager, 5, pos_override=draw_pos)
            item.scale = original_scale

        # Draw map border and final render
        border_rect = self.map_border.get_rect(center=(sw // 2, sh // 2))
        map_surface.blit(self.map_border, border_rect)
        screen.blit(map_surface, (0, 0))



    def get_save_data(self):
        return {"map": {
            "zoom": self.zoom,
            "pan": self.pan
        }}

    def load_from_data(self, data):
        if data!=False:
            self.zoom = data.get("zoom", 1.0)
            self.pan = data.get("pan", [0, 0])
            self.target_zoom = self.zoom
            self.target_pan = list(self.pan)

def default_items(manager):
    makeItem(manager, "map_boat", (0, 0), "map")
    makeItem(manager, "island1", (75, 242), "map")
    makeItem(manager, "island2", (150, -364), "map")
    makeItem(manager, "island3", (225, 364), "map")

def mapScreen(screen, instance_manager, prev_screen = None):
    switcher = ScreenSwitcher()
    virtual_size = (960, 540)

    item_manager = ItemManager(virtual_size)
    helper = MapHelper(virtual_size, item_manager, instance_manager.settings)

    base = BaseScreen(
        screen=screen,
        virtual_size=virtual_size,
        screen_name="map",
        switcher=switcher,
        draw_bag=False,
        draw_charmboard=False,
        background=None,
        default_items_func=default_items,
        previous_screen=table,
        helper=helper,
        item_manager=item_manager,
        override_draw = True,
        draw_screennav=False,
        instance_manager=instance_manager
    )

    base.run()
