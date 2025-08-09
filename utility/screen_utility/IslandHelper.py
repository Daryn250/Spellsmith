import pygame
import csv

REFERENCE_VSIZE = pygame.Vector2(160, 90)

class IslandHelper:
    def __init__(self, tileset_path, map_csv_path, vsize, tile_size=32):
        self.vsize = pygame.Vector2(vsize)
        self.ref_vsize = REFERENCE_VSIZE

        # Tile settings
        self.tile_size = tile_size
        self.tiles = self.load_tileset(tileset_path, tile_size)
        self.tile_map = self.load_csv_map(map_csv_path)
        self.map_width = len(self.tile_map[0])
        self.map_height = len(self.tile_map)

        # Zoom and Pan State
        self.zoom = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.5

        self.pan = pygame.Vector2(0, 0)
        self.target_pan = pygame.Vector2(0, 0)

        self.dragging = False
        self.last_mouse_pos = pygame.Vector2(0, 0)
        self.lerp_speed = 5.0  # Controls smoothness

        # Items
        self.items = []
        self.load_items()

    # ---------- Loading ----------
    def load_tileset(self, path, tile_size):
        """Slice tileset into individual tile Surfaces."""
        tileset_img = pygame.image.load(path).convert_alpha()
        tiles = []
        tiles_x = tileset_img.get_width() // tile_size
        tiles_y = tileset_img.get_height() // tile_size

        for y in range(tiles_y):
            for x in range(tiles_x):
                rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                tile = tileset_img.subsurface(rect)
                tiles.append(tile)
        return tiles

    def load_csv_map(self, path):
        with open(path) as f:
            reader = csv.reader(f)
            return [[int(x) for x in row] for row in reader]

    def load_items(self):
        self.items.append(self.HouseItem(self, (5, 5)))  # tile coordinates

    # ---------- Input Handling ----------
    def handle_event(self, event, virtual_mouse, virtual_size, base_screen):
        mouse = virtual_mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.dragging = True
                self.last_mouse_pos = mouse
            elif event.button == 4:
                self._zoom_at_mouse(mouse, 1.1)
            elif event.button == 5:
                self._zoom_at_mouse(mouse, 0.9)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            delta = mouse - self.last_mouse_pos
            self.target_pan += delta
            self.last_mouse_pos = mouse

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.target_zoom = 1.0
                self.target_pan = pygame.Vector2(0, 0)

    def _zoom_at_mouse(self, mouse, zoom_factor):
        old_zoom = self.target_zoom
        new_zoom = max(self.min_zoom, min(self.max_zoom, old_zoom * zoom_factor))

        center = self.vsize / 2
        mouse_offset = mouse - center
        world_mouse = (mouse_offset - self.target_pan) / old_zoom

        self.target_zoom = new_zoom
        self.target_pan = mouse_offset - world_mouse * new_zoom

    # ---------- Update ----------
    def update(self, dt, item_manager, mouse, base_screen):
        self.base_screen = base_screen

        lerp_amt = min(1, self.lerp_speed * dt)
        self.zoom += (self.target_zoom - self.zoom) * lerp_amt
        self.pan += (self.target_pan - self.pan) * lerp_amt

        for item in self.items:
            item.update(base_screen, base_screen.gui_manager, self.vsize, base_screen.instance_manager.sfx_manager)

    # ---------- Drawing ----------
    def draw(self, surface, virtual_size):
        self.draw_tilemap(surface)

        for item in self.items:
            item.draw(surface, self.zoom, self.pan, self.tile_size)

    def draw_tilemap(self, surface):
        tile_w = self.tile_size * self.zoom
        tile_h = self.tile_size * self.zoom

        start_x = max(0, int(-self.pan.x // tile_w))
        start_y = max(0, int(-self.pan.y // tile_h))
        end_x = min(self.map_width, int((surface.get_width() - self.pan.x) // tile_w) + 1)
        end_y = min(self.map_height, int((surface.get_height() - self.pan.y) // tile_h) + 1)

        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_id = self.tile_map[y][x]
                if tile_id >= 0:  # -1 means empty space
                    tile_img = pygame.transform.scale(
                        self.tiles[tile_id], (int(tile_w), int(tile_h))
                    )
                    draw_x = x * tile_w + self.pan.x
                    draw_y = y * tile_h + self.pan.y
                    surface.blit(tile_img, (draw_x, draw_y))

    # ---------- Save / Load ----------
    def get_save_data(self):
        return {"items": [item.get_save_data() for item in self.items]}

    def load_from_data(self, data):
        if data:
            for item_data in data.get("items", []):
                self.items.append(self.HouseItem.from_save_data(self, item_data))

    # ---------- Item Class ----------
    class HouseItem:
        def __init__(self, manager, tile_pos, nbt_data=None):
            self.manager = manager
            self.tile_pos = pygame.Vector2(tile_pos)
            self.nbt_data = nbt_data or {}
            self.image = pygame.image.load("assets/error.png").convert_alpha()
            self.rect = self.image.get_rect()

        def update(self, base_screen, gui_manager, vsize, sfx_manager):
            pass

        def draw(self, surface, zoom, pan, tile_size):
            scaled_img = pygame.transform.scale(
                self.image,
                (int(self.rect.width * zoom), int(self.rect.height * zoom))
            )
            screen_pos = self.tile_pos.elementwise() * (tile_size * zoom) + pan
            draw_pos = screen_pos - pygame.Vector2(scaled_img.get_width() // 2,
                                                   scaled_img.get_height() // 2)
            surface.blit(scaled_img, draw_pos)

        def get_save_data(self):
            return {
                "type": "house",
                "pos": list(self.tile_pos),
                "nbt": self.nbt_data
            }

        @staticmethod
        def from_save_data(helper, data):
            return IslandHelper.HouseItem(helper, data["pos"], data.get("nbt"))
