#!/usr/bin/env python3
"""
Tilemap drawer with:
 - support for a single tileset image (tiles/tileset.png) OR a folder of tiles
 - clickable palette showing actual tiles
 - dynamic layer selector (click to choose, right-click to delete, + to add)
 - save/load JSON, export CSV per layer
Controls:
 - Left click: paint selected tile on current layer
 - Right click: erase tile on current layer (or right-click a layer button to delete it)
 - Mouse wheel: next/prev tile
 - Click a tile in the palette: select that tile
 - Click a layer button to select layer
 - Right-click a layer button to delete (if more than 1)
 - Click + under the layers to add a layer
 - N : add new layer
 - D : delete current layer (if >1)
 - S : save project (JSON)
 - L : load project (JSON)
 - E : export current layer to CSV
 - R : reset all layers (clears)
 - Esc or close window: quit
"""
import pygame
import os
import json
import csv
from pathlib import Path

pygame.init()

# ---------- CONFIG ----------
TILES_FOLDER = "tiles"                # folder with tiles or containing tileset.png
TILESET_NAME = "tileset.png"          # if present inside TILES_FOLDER -> use spritesheet
DEFAULT_TILE_SIZE = 32                # tile size in pixels (will scale images to this)
MAP_COLS = 40                         # width (tiles)
MAP_ROWS = 25                         # height (tiles)
PALETTE_WIDTH = 260                   # palette area width (right)
WINDOW_W = MAP_COLS * DEFAULT_TILE_SIZE + PALETTE_WIDTH
WINDOW_H = MAP_ROWS * DEFAULT_TILE_SIZE
FONT = pygame.font.SysFont("Consolas", 14)
SAVE_PATH = "tilemap_project.json"
# ----------------------------

screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
pygame.display.set_caption("Tilemap Drawer (tileset + layers)")
clock = pygame.time.Clock()

# ---- Helpers to load tiles ----
def load_tiles_from_folder(folder, tile_size):
    tiles = []
    filenames = []
    p = Path(folder)
    if not p.exists():
        p.mkdir(parents=True, exist_ok=True)
    for f in sorted(p.iterdir()):
        if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".bmp", ".gif"):
            # skip tileset file (handled separately)
            if f.name == TILESET_NAME:
                continue
            try:
                img = pygame.image.load(str(f)).convert_alpha()
                img = pygame.transform.scale(img, (tile_size, tile_size))
                tiles.append(img)
                filenames.append(str(f))
            except Exception as e:
                print("Failed loading", f, e)
    return tiles, filenames

def load_tiles_from_spritesheet(path, tile_size):
    tiles = []
    filenames = []
    p = Path(path)
    if not p.exists():
        return tiles, filenames
    img = pygame.image.load(str(p)).convert_alpha()
    w, h = img.get_size()
    cols = w // tile_size
    rows = h // tile_size
    for ry in range(rows):
        for rx in range(cols):
            rect = pygame.Rect(rx*tile_size, ry*tile_size, tile_size, tile_size)
            surf = img.subsurface(rect).copy()
            tiles.append(surf)
            # store filename + index so save/load can re-create
            filenames.append(f"{str(p)}::idx{ry*cols+rx}")
    return tiles, filenames

# Data model: list of layers, each layer is rows x cols with tile indices (or -1)
def make_empty_layer(cols, rows):
    return [[-1 for _ in range(cols)] for _ in range(rows)]

def save_project_json(path, meta, layers):
    data = {
        "meta": meta,   # contains tile_size, tilesource (tileset or file list), TILES_FOLDER
        "cols": MAP_COLS,
        "rows": MAP_ROWS,
        "layers": layers,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print("Saved", path)

def load_project_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def export_layer_csv(layer, path):
    with open(path, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        for row in layer:
            writer.writerow(row)
    print("Exported CSV:", path)

# ---- Auto-detect tileset or folder ----
tiles = []
tile_filenames = []
tileset_path = Path(TILES_FOLDER) / TILESET_NAME
using_tileset = False

if tileset_path.exists():
    tiles, tile_filenames = load_tiles_from_spritesheet(tileset_path, DEFAULT_TILE_SIZE)
    using_tileset = True
else:
    tiles, tile_filenames = load_tiles_from_folder(TILES_FOLDER, DEFAULT_TILE_SIZE)
    using_tileset = False

if not tiles:
    # placeholder
    surf = pygame.Surface((DEFAULT_TILE_SIZE, DEFAULT_TILE_SIZE), pygame.SRCALPHA)
    surf.fill((200, 50, 50))
    tiles = [surf]
    tile_filenames = ["__placeholder__"]
    using_tileset = False

# ---- State ----
tile_size = DEFAULT_TILE_SIZE
cols = MAP_COLS; rows = MAP_ROWS
palette_x = cols * tile_size
layers = [make_empty_layer(cols, rows)]
current_layer = 0
selected_tile = 0
running = True

# UI layout for layers area
LAYER_BTN_H = 28
LAYER_AREA_TOP = 8
LAYER_AREA_PAD = 6
LAYER_AREA_HEIGHT = 220  # enough room for many layers; if overflow, it will clip
LAYER_BTN_W = PALETTE_WIDTH - 16

def draw_ui(surface):
    # palette background
    palette_rect = pygame.Rect(palette_x, 0, PALETTE_WIDTH, WINDOW_H)
    pygame.draw.rect(surface, (28, 28, 32), palette_rect)

    # ---- draw layer selector area ----
    la_x = palette_x + 8
    la_y = LAYER_AREA_TOP
    max_buttons_visible = (LAYER_AREA_HEIGHT - 40) // (LAYER_BTN_H + 6)
    # draw each layer as a button
    for i, _ in enumerate(layers):
        btn_rect = pygame.Rect(la_x, la_y + i * (LAYER_BTN_H + 6), LAYER_BTN_W, LAYER_BTN_H)
        # highlight selected layer
        if i == current_layer:
            pygame.draw.rect(surface, (80, 120, 160), btn_rect)
        else:
            pygame.draw.rect(surface, (50, 50, 60), btn_rect)
        label = FONT.render(f"Layer {i+1}", True, (230, 230, 230))
        surface.blit(label, (btn_rect.x + 8, btn_rect.y + 6))
        # small delete hint (right side)
        del_label = FONT.render("R-Click delete", True, (180, 120, 120))
        surface.blit(del_label, (btn_rect.right - del_label.get_width() - 8, btn_rect.y + 6))

    # add-layer button
    add_rect = pygame.Rect(la_x, la_y + len(layers) * (LAYER_BTN_H + 6), LAYER_BTN_W, LAYER_BTN_H)
    pygame.draw.rect(surface, (70, 90, 70), add_rect)
    plus_label = FONT.render("+ Add Layer (click)", True, (230, 230, 230))
    surface.blit(plus_label, (add_rect.x + 8, add_rect.y + 6))

    # small mode text (tileset or folder)
    mode_text = "Tileset" if using_tileset else "Folder"
    surf_mode = FONT.render(f"Tilesource: {mode_text}", True, (200,200,200))
    surface.blit(surf_mode, (la_x, add_rect.bottom + 8))

    # ---- draw palette tiles ----
    padding = 8
    thumb = tile_size
    palette_y_start = add_rect.bottom + 36
    cols_in_palette = max(1, PALETTE_WIDTH // (thumb + padding))
    x = palette_x + padding
    y = palette_y_start
    for idx, t in enumerate(tiles):
        r = pygame.Rect(x, y, thumb, thumb)
        surface.blit(t, r.topleft)
        border_col = (255, 200, 40) if idx == selected_tile else (80, 80, 80)
        pygame.draw.rect(surface, border_col, r, 2)
        # show index number
        idx_label = FONT.render(str(idx), True, (200,200,200))
        surface.blit(idx_label, (r.x+2, r.y+2))
        x += thumb + padding
        if (idx + 1) % cols_in_palette == 0:
            x = palette_x + padding
            y += thumb + padding

    # ---- info / shortcuts ----
    info_lines = [
        f"Layer: {current_layer+1}/{len(layers)}  (click to select, right-click to delete)",
        "N: new layer  D: delete layer",
        f"Tile: {selected_tile+1}/{len(tiles)}  (wheel)",
        "Left: paint   Right: erase",
        "S: save JSON   L: load JSON",
        "E: export current layer CSV",
        "R: clear all layers",
        "Esc: quit",
    ]
    iy = WINDOW_H - 20 * len(info_lines) - 10
    for line in info_lines:
        surface.blit(FONT.render(line, True, (220, 220, 220)), (palette_x + 8, iy))
        iy += 18

def world_pos_from_mouse(mx, my):
    # map area is at (0,0)-(cols*tile_size, rows*tile_size)
    if mx < 0 or my < 0 or mx >= cols * tile_size or my >= rows * tile_size:
        return None
    tx = int(mx // tile_size)
    ty = int(my // tile_size)
    if tx < 0 or ty < 0 or tx >= cols or ty >= rows:
        return None
    return tx, ty

def draw_map(surface):
    # fill background
    surface.fill((80, 120, 160), (0,0, cols*tile_size, rows*tile_size))

    # draw layers in order
    for layer in layers:
        for y in range(rows):
            for x in range(cols):
                tid = layer[y][x]
                if tid is not None and tid >= 0 and tid < len(tiles):
                    tile_img = tiles[tid]
                    surface.blit(tile_img, (x*tile_size, y*tile_size))

    # grid overlay
    for x in range(cols+1):
        pygame.draw.line(surface, (40,40,40), (x*tile_size,0), (x*tile_size, rows*tile_size))
    for y in range(rows+1):
        pygame.draw.line(surface, (40,40,40), (0,y*tile_size), (cols*tile_size, y*tile_size))

# ---- main loop ----
while running:
    dt = clock.tick(60) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # If clicked in palette area -> check for layer buttons & palette tiles
            if mx >= palette_x:
                # layer area rect
                la_x = palette_x + 8
                la_y = LAYER_AREA_TOP
                add_rect = pygame.Rect(la_x, la_y + len(layers) * (LAYER_BTN_H + 6), LAYER_BTN_W, LAYER_BTN_H)
                # check layer buttons
                # each button starts at la_y and stacks with (LAYER_BTN_H + 6) spacing
                clicked_layer = None
                for i in range(len(layers)):
                    btn_rect = pygame.Rect(la_x, la_y + i * (LAYER_BTN_H + 6), LAYER_BTN_W, LAYER_BTN_H)
                    if btn_rect.collidepoint(mx, my):
                        clicked_layer = i
                        break
                if clicked_layer is not None:
                    if event.button == 1:  # left -> select
                        current_layer = clicked_layer
                    elif event.button == 3:  # right -> delete (if >1)
                        if len(layers) > 1:
                            layers.pop(clicked_layer)
                            current_layer = max(0, current_layer - 1)
                    continue
                # add button clicked?
                if add_rect.collidepoint(mx, my):
                    if event.button == 1:
                        layers.append(make_empty_layer(cols, rows))
                        current_layer = len(layers) - 1
                    continue

                # palette tile clicks (below layer area)
                padding = 8
                thumb = tile_size
                palette_y_start = add_rect.bottom + 36
                cols_in_palette = max(1, PALETTE_WIDTH // (thumb + padding))
                rel_x = mx - palette_x - padding
                rel_y = my - palette_y_start
                if rel_x >= 0 and rel_y >= 0:
                    col_idx = int(rel_x // (thumb + padding))
                    row_idx = int(rel_y // (thumb + padding))
                    idx = row_idx * cols_in_palette + col_idx
                    if 0 <= idx < len(tiles):
                        selected_tile = idx
                continue

            # Map clicks (left paint, right erase); wheel handled by separate cases
            if event.button == 1:  # left -> paint
                pos = world_pos_from_mouse(mx, my)
                if pos:
                    tx, ty = pos
                    layers[current_layer][ty][tx] = selected_tile
            elif event.button == 3:  # right -> erase
                pos = world_pos_from_mouse(mx, my)
                if pos:
                    tx, ty = pos
                    layers[current_layer][ty][tx] = -1
            elif event.button == 4:  # wheel up -> next tile
                selected_tile = (selected_tile + 1) % len(tiles)
            elif event.button == 5:  # wheel down -> prev tile
                selected_tile = (selected_tile - 1) % len(tiles)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_LEFTBRACKET:
                current_layer = max(0, current_layer - 1)
            elif event.key == pygame.K_RIGHTBRACKET:
                current_layer = min(len(layers)-1, current_layer + 1)
            elif event.key == pygame.K_n:
                layers.append(make_empty_layer(cols, rows))
                current_layer = len(layers)-1
            elif event.key == pygame.K_d:
                if len(layers) > 1:
                    layers.pop(current_layer)
                    current_layer = max(0, current_layer-1)
            elif event.key == pygame.K_s:
                # save JSON (store metadata about whether using tileset or folder)
                meta = {
                    "tile_size": tile_size,
                    "using_tileset": using_tileset,
                    "tileset_path": str(tileset_path) if using_tileset else None,
                    "tile_files": tile_filenames if not using_tileset else None,
                }
                save_project_json(SAVE_PATH, meta, layers)
            elif event.key == pygame.K_l:
                # load JSON
                try:
                    data = load_project_json(SAVE_PATH)
                    meta = data.get("meta", {})
                    if meta.get("tile_size") == tile_size:
                        # reload tiles according to saved meta
                        if meta.get("using_tileset") and meta.get("tileset_path"):
                            tpath = Path(meta.get("tileset_path"))
                            if tpath.exists():
                                tiles, tile_filenames = load_tiles_from_spritesheet(tpath, tile_size)
                                using_tileset = True
                                tileset_path = tpath
                            else:
                                print("Saved tileset missing:", tpath)
                        elif meta.get("tile_files"):
                            # try to match current folder files; if not found preserve indices
                            # NOTE: this simple loader assumes same folder structure / filenames
                            tile_filenames = meta.get("tile_files", [])
                            # try to load each file (if missing will use placeholder)
                            new_tiles = []
                            for fname in tile_filenames:
                                try:
                                    img = pygame.image.load(fname).convert_alpha()
                                    img = pygame.transform.scale(img, (tile_size, tile_size))
                                    new_tiles.append(img)
                                except Exception as e:
                                    print("Missing tile file", fname, e)
                                    # placeholder
                                    surf = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
                                    surf.fill((120, 60, 60))
                                    new_tiles.append(surf)
                            tiles = new_tiles
                            using_tileset = False
                        else:
                            print("No tile information in saved file.")
                        # load layers
                        loaded_layers = data.get("layers", [])
                        if loaded_layers:
                            # convert to our format (lists)
                            layers.clear()
                            for L in loaded_layers:
                                layers.append([list(row) for row in L])
                            current_layer = 0
                            print("Loaded project from", SAVE_PATH)
                        else:
                            print("No layers in saved file.")
                    else:
                        print("Tile size mismatch; cannot load.")
                except Exception as e:
                    print("Failed to load:", e)
            elif event.key == pygame.K_e:
                # export current layer to CSV
                out = f"layer_{current_layer+1}.csv"
                export_layer_csv(layers[current_layer], out)
            elif event.key == pygame.K_r:
                # reset all layers
                layers = [make_empty_layer(cols, rows)]
                current_layer = 0

    # continuous drawing with mouse button held
    buttons = pygame.mouse.get_pressed()
    if buttons[0]:
        mx, my = pygame.mouse.get_pos()
        if mx < palette_x:
            pos = world_pos_from_mouse(mx, my)
            if pos:
                tx, ty = pos
                layers[current_layer][ty][tx] = selected_tile
    elif buttons[2]:
        mx, my = pygame.mouse.get_pos()
        if mx < palette_x:
            pos = world_pos_from_mouse(mx, my)
            if pos:
                tx, ty = pos
                layers[current_layer][ty][tx] = -1

    # Draw
    screen.fill((50,50,50))
    # draw map area
    map_surface = screen.subsurface(pygame.Rect(0,0, cols*tile_size, rows*tile_size))
    draw_map(map_surface)
    # draw palette and UI
    draw_ui(screen)

    pygame.display.flip()

pygame.quit()
