import pygame
import random
import math
from utility.animated_sprite import AnimatedTile
from utility.screen_utility.screenManager import get_screen_function
import json
from utility.item_utility.item_flag_handlers import *
from utility.particle import make_tiny_sparkle
import os
import time


def get_shadow_offset(screen_width, item_x, intensity=0.3, vertical_push=10):
    # Light sources at 2/6 and 4/6 of screen width
    light1_x = screen_width * (2 / 6)
    light2_x = screen_width * (4 / 6)

    # Average light direction
    avg_light_x = (light1_x + light2_x) / 2

    # Direction from light to object
    dx = item_x - avg_light_x

    # Apply intensity scaling and return horizontal + vertical offset
    return int(dx * intensity), vertical_push


class BaseItem:
    def __init__(self, manager, type, pos, nbt_data={}):
        self.manager = manager
        self.nbt = dict(nbt_data)
        self.type = type or "undefined_itemType"
        self.pos = pos
        self.__dict__.update(self.nbt)

        self.flags = getattr(self, "flags", [])
        self.animated = getattr(self, "animated", False)
        self.scale = getattr(self, "scale", [1, 1])

        if self.animated:
            self.frameDuration = getattr(self, "frameDuration", 100)
            self.img = AnimatedTile(getattr(self, "img_path", "assets/error.png"), frame_duration=self.frameDuration)
        else:
            self.img = pygame.image.load(getattr(self, "img_path", "assets/error.png")).convert_alpha()
        

        if "draggable" in self.flags:
            if not hasattr(self, "vx"):
                self.rotation = 0.0
                self.rotational_velocity = 0.0

                self.vx = 0
                self.vy = 0

                self.currentGravity = 0.3
                self.storedGravity = 0.3

                self.ovx = getattr(self, "ovx", 0)
                self.ovy = getattr(self, "ovy", 0)
                self.dragging_for = 0

                self.item_hit_floor = False

            self.floor = pos[1]
            self.dragging = False


        # for the hanging class
        if "hangable" in self.flags:
            self.NAIL_IMAGE = pygame.image.load("assets/gui/charm_board/nail.png").convert_alpha()
            self.attached_to = None
            self.show_nail = False

        self.particles = []

        self.is_hovered = False  # Track hover state for all items

    @property
    def image(self):
        return self.img.get_current_frame() if self.animated else self.img

    

    def to_nbt(self, exclude=[]):
        base_exclude = [
            "manager", "pos", "type", "is_hovered", "img", "floor", "ovx", "ovy",
            "dragging", "nbt", "window", "NAIL_IMAGE", "trick", "particles", "locked",
            "liquid_anim", "cork_img", "original_mask_img", "cached_mask_surface", "cached_mask",
            "shine_img", "glow_img", "layer_surfaces", "_base_combined_surface", "_cached_image", "_cached_rotation", "_cached_scale",
            "_cached_scaled_img", "_cached_mask", "_last_cache_key", "_cached_shadow_img", "_cached_hitbox_rect", "_cached_shadow_offset",
            "window_last_pos",
        ]
        # Exclude all callables (functions/methods)
        for k, v in list(self.__dict__.items()):
            if callable(v) and k not in base_exclude:
                base_exclude.append(k)
        safe_nbt = {}
        for k, v in self.__dict__.items():
            if k in base_exclude or k in exclude:
                continue
            safe_nbt[k] = v
        return safe_nbt


    def update(self, screen, gui_manager, virtual_size, sfx_manager, bounds=None, dt=None):
        if self.animated and dt:
            self.img.update(dt)

        if "draggable" in self.flags:
            handle_draggable(self, screen, gui_manager, virtual_size, sfx_manager, bounds)

        if "hangable" in self.flags:
            handle_hangable(self, screen)
        
        if "inspectable" in self.flags:
            handle_inspectable(self, gui_manager, dt)


        handle_temperature(self, dt)

    def draw(self, surface, screensize, gui_manager, item_manager, rotation_scale, pos_override = None):
        if "invisible" in self.flags:
            return
        

        angle = -getattr(self, "rotation", 0)
        s = getattr(self, "scale", (1, 1))
        x_scale = (screensize[0] / 480) * s[0]
        y_scale = (screensize[1] / 270) * s[1]
        scale = min(x_scale, y_scale)

        original_img = self.image
        scaled_size = (
            int(original_img.get_width() * scale),
            int(original_img.get_height() * scale)
        )
        img = pygame.transform.scale(original_img, scaled_size)

        center_x, center_y = self.pos if pos_override == None else pos_override
        rotated_img = pygame.transform.rotate(img, angle)
        rotated_rect = rotated_img.get_rect(center=(center_x, center_y))

        if "no_shadow" not in self.flags:
            if getattr(self, "state", None) == "bagged":
                SHADOW_OFFSET = (5, -5)
            else:
                SHADOW_OFFSET = (10, -10)
            shadow_bottom_y = getattr(self, "floor", rotated_rect.bottom)

            # Simulate blur by drawing multiple semi-transparent shadows
            shadow_img = pygame.transform.scale(
                rotated_img,
                (rotated_img.get_width(), int(rotated_img.get_height() * 0.5))
            )

            for blur_radius in range(4):  # Number of blur layers
                alpha = 60 // (blur_radius + 1)  # Decreasing alpha
                offset = blur_radius  # Spread radius

                blurred_shadow = pygame.Surface(shadow_img.get_size(), pygame.SRCALPHA)
                blurred_shadow.blit(shadow_img, (0, 0))
                blurred_shadow.fill((0, 0, 0, alpha if not getattr(self, "dragging", False) else alpha // 4), special_flags=pygame.BLEND_RGBA_MULT)

                shadow_pos = (
                    rotated_rect.centerx - shadow_img.get_width() // 2 + SHADOW_OFFSET[0] + offset,
                    shadow_bottom_y + SHADOW_OFFSET[1] + offset
                )

                surface.blit(blurred_shadow, shadow_pos)






        if getattr(self, "highlighted", False):
            mask = pygame.mask.from_surface(rotated_img)
            outline_points = mask.outline()
            if outline_points:
                offset_outline = [(x + rotated_rect.left, y + rotated_rect.top) for x, y in outline_points]
                pygame.draw.polygon(surface, (255, 255, 255), offset_outline, width=3)

        if hasattr(self, "temperature"):
            temp = self.temperature
            max_temp = 1000
            glow_strength = min(1.0, temp / max_temp)

            if glow_strength > 0.01:
                glow_surface = pygame.Surface(rotated_img.get_size(), pygame.SRCALPHA)
                mask = pygame.mask.from_surface(rotated_img)
                outline_surface = mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

                tint_color = (int(255 * glow_strength), int(32 * glow_strength), 0, int(160 * glow_strength))
                tint_surface = pygame.Surface(rotated_img.get_size(), pygame.SRCALPHA)
                tint_surface.fill(tint_color)

                outline_surface.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                rotated_img.blit(outline_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

                if temp >= 200:
                    glow_strength = min(1.0, (temp - 200) / 800)
                    def lerp(a, b, t): return int(a + (b - a) * t)
                    base_color = (
                        lerp(255, 255, glow_strength),
                        lerp(50, 255, glow_strength),
                        lerp(0, 200, glow_strength)
                    )
                    for i in range(3):
                        ring_strength = glow_strength / ((i + 1) ** 2)
                        ring_radius = int(rotated_img.get_width() * (0.6 + 0.2 * i) * glow_strength)
                        ring_color = tuple(int(c * ring_strength) for c in base_color)
                        if ring_radius > 0:
                            glow_surface = pygame.Surface((ring_radius * 2, ring_radius * 2), pygame.SRCALPHA)
                            pygame.draw.circle(glow_surface, ring_color, (ring_radius, ring_radius), ring_radius)
                            surface.blit(glow_surface, (center_x - ring_radius, center_y - ring_radius), special_flags=pygame.BLEND_RGB_ADD)

        surface.blit(rotated_img, rotated_rect.topleft)

    def set_position(self, pos):
        self.pos = pos
        if "draggable" in self.flags:
            self.vx = 0
            self.vy = 0
            self.floor = pos[1]
            self.ovx = 0
            self.ovy = 0
            self.rotation = 0

    def get_scaled_hitbox(self, screensize, pos_override=None):
        s = self.scale
        x_scale = screensize[0] / 480 * s[0]
        y_scale = screensize[1] / 270 * s[1]
        scale = min(x_scale, y_scale)
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)

        pos = pos_override if pos_override else self.pos
        return pygame.Rect(pos[0] - width // 2, pos[1] - height // 2, width, height)

    def get_fast_bbox(self, screensize, pos_override=None):
        """
        Returns a fast, axis-aligned bounding box for quick collision checks.
        This uses the unrotated, scaled image size and current (or override) position.
        """
        s = self.scale
        x_scale = screensize[0] / 480 * s[0]
        y_scale = screensize[1] / 270 * s[1]
        scale = min(x_scale, y_scale)
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        pos = pos_override if pos_override else self.pos
        return pygame.Rect(pos[0] - width // 2, pos[1] - height // 2, width, height)


    @property
    def uniform_scale(self):
        scale = self.scale
        return (scale, scale) if isinstance(scale, (int, float)) else scale
    

    def start_screen_switch(self, screen, screenSwitcher, baseScreen):
        if type(self.next_screen) == str:
            self.next_screen = get_screen_function(self.next_screen)
        screenSwitcher.start(lambda: self.next_screen(screen, baseScreen.instance_manager),
                             save_callback=lambda: baseScreen.save_items(baseScreen.instance_manager.save_file),
                             sfx_manager = baseScreen.instance_manager.sfx_manager)

    def update_hover(self, mouse_pos, virtual_size, use_pos_override=True):
        """
        Update self.is_hovered based on mouse position and bounding box checks.
        If use_pos_override is True, use self.pos_override if present; otherwise use self.pos.
        """
        pos_to_use = getattr(self, "pos_override", self.pos) if use_pos_override else self.pos
        # Fast bbox check
        if hasattr(self, "get_fast_bbox") and self.get_fast_bbox(virtual_size, pos_override=pos_to_use).collidepoint(mouse_pos):
            rect = self.get_scaled_hitbox(virtual_size, pos_override=pos_to_use)
            self.is_hovered = rect.collidepoint(mouse_pos)
        else:
            self.is_hovered = False

class BottleItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        self.capacity = getattr(self, "capacity", 100)
        self.contents = getattr(self, "contents", 0)
        self.liquid = getattr(self, "liquid", None)
        self.bottleType = getattr(self, "bottleType", None)

        if self.bottleType is None:
            raise ValueError("No bottle type given, cannot generate mask")

        # --- Liquid Animation ---
        if self.liquid!=None:
            self.liquid_anim = AnimatedTile(f"assets/liquids/{self.liquid}", frame_duration=3)
            self.liquid_rotation = 0.0
            self.liquid_rotational_velocity = 0.0

        # --- Load mask image and cache scaled version + alpha mask ---
        self.cork_img = pygame.image.load(f"assets/items/bottles/{self.bottleType}/img3.png").convert_alpha()

        self.original_mask_img = pygame.image.load(f"assets/items/bottles/{self.bottleType}/img2.png").convert_alpha()
        self.cached_mask_size = None  # will store size of last scaled mask
        self.cached_mask_surface = None
        self.cached_mask = None  # pygame.mask.Mask

    def update_mask_cache(self, bottle_size):
        """Update cached mask surface and mask if bottle size changed"""
        if self.cached_mask_size != bottle_size:
            self.cached_mask_size = bottle_size
            self.cached_mask_surface = pygame.transform.scale(self.original_mask_img, bottle_size)
            self.cached_mask = pygame.mask.from_surface(self.cached_mask_surface)
    
    def update(self, screen, gui_manager, virtual_size, sfx, dt):
        super().update(screen, gui_manager, virtual_size, sfx_manager=sfx, dt=dt)
        if self.liquid!=None:
            self.liquid_anim.update(dt)

    def draw(self, surface, screensize, gui_manager, item_manager, rotation_scale):
        if "invisible" in self.flags:
            return

        # --- Scale and rotation setup ---
        angle = -getattr(self, "rotation", 0)
        s = self.scale
        x_scale = (screensize[0] / 480) * s[0]
        y_scale = (screensize[1] / 270) * s[1]
        scale = min(x_scale, y_scale)

        center_x, center_y = self.pos
        bottle_size = (
            int(self.image.get_width() * scale),
            int(self.image.get_height() * scale)
        )
        bottle_img = pygame.transform.scale(self.image, bottle_size)
        self.update_mask_cache(bottle_size)

        rotated_bottle = pygame.transform.rotate(bottle_img, angle)
        bottle_rect = rotated_bottle.get_rect(center=(center_x, center_y))

        # --- Draw shadow first ---
        if "no_shadow" not in self.flags:
            shadow_img = pygame.transform.scale(
                rotated_bottle,
                (rotated_bottle.get_width(), int(rotated_bottle.get_height() * 0.5))
            )
            shadow_surface = pygame.Surface(shadow_img.get_size(), pygame.SRCALPHA)
            shadow_surface.blit(shadow_img, (0, 0))
            shadow_surface.fill((0, 0, 0, 20 if self.dragging else 80), special_flags=pygame.BLEND_RGBA_MULT)

            SHADOW_OFFSET = (10, -10)
            shadow_bottom_y = self.floor
            shadow_pos = (
                bottle_rect.centerx - shadow_surface.get_width() // 2 + SHADOW_OFFSET[0],
                shadow_bottom_y + SHADOW_OFFSET[1]
            )
            surface.blit(shadow_surface, shadow_pos)

        # --- Prepare mask and liquid ---
        upright_mask_surf = self.cached_mask.to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        rotated_mask = pygame.transform.rotate(upright_mask_surf, angle)
        mask_rect = rotated_mask.get_rect()

        if self.liquid!=None:
            liquid_frame = self.liquid_anim.get_current_frame()
            liquid_size = (bottle_size[1], bottle_size[1])  # square image
            liquid_img = pygame.transform.scale(liquid_frame, liquid_size)
            sloshed_liquid = pygame.transform.rotate(liquid_img, self.liquid_rotation)
            sloshed_rect = sloshed_liquid.get_rect()

            fill_ratio = min(max(self.contents / self.capacity, 0), 1)
            fill_offset = int((1.0 - fill_ratio) * bottle_size[1])
            liquid_x = (mask_rect.width // 2) - (sloshed_rect.width // 2)
            liquid_y = (mask_rect.height // 2) - (sloshed_rect.height // 2) + fill_offset

            liquid_surface = pygame.Surface(mask_rect.size, pygame.SRCALPHA)
            liquid_surface.blit(sloshed_liquid, (liquid_x, liquid_y))
            masked_liquid = liquid_surface.copy()
            masked_liquid.blit(rotated_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            masked_rect = masked_liquid.get_rect(center=(center_x, center_y))

        # --- Render final visuals ---
        if self.liquid!=None:
            surface.blit(masked_liquid, masked_rect.topleft)
        surface.blit(rotated_bottle, bottle_rect.topleft)

        # --- Cork on top ---
        cork_img = pygame.transform.scale(self.cork_img, bottle_size)
        rotated_cork = pygame.transform.rotate(cork_img, angle)
        cork_rect = rotated_cork.get_rect(center=(center_x, center_y))
        surface.blit(rotated_cork, cork_rect.topleft)
    
    def set_position(self, pos):
        super().set_position(pos)
        self.scale = getattr(self, "default_scale", self.scale)

class MaterialItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        self.temperature = getattr(self, "temperature", 0)
        self.mass = getattr(self, "mass", 1)

class CharmItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        if "charm" not in self.flags:
            self.flags.append("charm")
        self.is_clicked = False
        self.window = None

class PartItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        self.material = getattr(self, "material", "wood")
        self.part_type = getattr(self, "part_type", "handle")

class SlotItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)    
class GemItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        self.shine_path = getattr(self, "shine_path", None)
        if self.shine_path!=None:
            self.shine_img = pygame.image.load(self.shine_path).convert_alpha()
        self.shine_alpha = 0
        self.shine_time = 0
        self.shine_speed = getattr(self, "shine_speed", 0.3)  # Pulses per second
        self.is_shiny = "shiny" in self.flags
        self.glow_path = getattr(self, "glow_path", "assets/misc/glow_img2.png")
        if self.is_shiny:
            self.glow_img = pygame.image.load(self.glow_path).convert_alpha()
        else:
            self.glow_img = None


    def update(self, screen, gui_manager, virtual_size, bounds=None, dt=None):
        super().update(screen, gui_manager, virtual_size, bounds, dt)
        if dt:
            self.shine_time += dt / 1000
            pulse = math.sin(self.shine_time * math.pi * self.shine_speed)
            self.shine_alpha = int(127 + 128 * pulse)  # 0–255 range for alpha
            if self.is_shiny:
                if random.random() < 0.05:  # Adjust spawn rate as needed
                    bounds = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
                    bounds.center = self.pos
                    rand_pos = (
                        random.randint(bounds.left, bounds.right),
                        random.randint(bounds.top, bounds.bottom)
                    )
                    self.particles.extend(make_tiny_sparkle(rand_pos, count=1))


    def draw(self, surface, screensize, gui_manager, item_manager, rotation_scale):
        if "invisible" in self.flags:
            return

        angle = -getattr(self, "rotation", 0)
        s = getattr(self, "scale", (1, 1))
        x_scale = (screensize[0] / 480) * s[0]
        y_scale = (screensize[1] / 270) * s[1]
        scale = min(x_scale, y_scale)

        original_img = self.image
        scaled_size = (
            int(original_img.get_width() * scale),
            int(original_img.get_height() * scale)
        )
        img = pygame.transform.scale(original_img, scaled_size)
        rotated_img = pygame.transform.rotate(img, angle)
        rotated_rect = rotated_img.get_rect(center=self.pos)

        # 🌈 Custom shadow using gem color
        if "no_shadow" not in self.flags:
            SHADOW_OFFSET = (10, -10)
            shadow_bottom_y = getattr(self, "floor", rotated_rect.bottom)

            shadow_img = pygame.transform.scale(
                rotated_img,
                (rotated_img.get_width(), int(rotated_img.get_height() * 0.5))
            )

            gem_color = getattr(self, "shadow_color", (255, 255, 255))  # default cyan glow
            for blur_radius in range(4):
                alpha = 60 // (blur_radius + 1)
                offset = blur_radius

                blurred_shadow = pygame.Surface(shadow_img.get_size(), pygame.SRCALPHA)
                blurred_shadow.blit(shadow_img, (0, 0))

                # Apply the colored tint here
                tint_surface = pygame.Surface(shadow_img.get_size(), pygame.SRCALPHA)
                r, g, b = gem_color
                tint_surface.fill((r, g, b, alpha if not getattr(self, "dragging", False) else alpha // 4))
                blurred_shadow.blit(tint_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

                shadow_pos = (
                    rotated_rect.centerx - shadow_img.get_width() // 2 + SHADOW_OFFSET[0] + offset,
                    shadow_bottom_y + SHADOW_OFFSET[1] + offset
                )

                surface.blit(blurred_shadow, shadow_pos)

        # ✨ Shine and base image
        surface.blit(rotated_img, rotated_rect.topleft)
        if self.is_shiny and self.glow_img:
            # Match glow size to full gem image
            glow_w = rotated_img.get_width()
            glow_h = rotated_img.get_height()
            scaled_glow = pygame.transform.scale(self.glow_img, (glow_w, glow_h))
            rotated_glow = pygame.transform.rotate(scaled_glow, angle)

            # Optional: Apply soft blur effect by layering semi-transparent versions
            for i in range(1):  # Number of blur layers
                blur_alpha = int(50 / (i + 1))  # Decreasing alpha per layer
                blur_scale = 1.0 + 0.1 * i  # Slightly increase size per layer

                blurred_size = (
                    int(rotated_glow.get_width() * blur_scale),
                    int(rotated_glow.get_height() * blur_scale)
                )
                blurred_glow = pygame.transform.smoothscale(rotated_glow, blurred_size)

                # Center it again after scaling
                blurred_rect = blurred_glow.get_rect(center=self.pos)

                # Set alpha manually
                blurred_glow.set_alpha(blur_alpha)
                surface.blit(blurred_glow, blurred_rect.topleft, special_flags=pygame.BLEND_ADD)


        



        if self.shine_img is not None:
            shine_scaled = pygame.transform.scale(
                self.shine_img,
                (
                    int(self.shine_img.get_width() * scale),
                    int(self.shine_img.get_height() * scale)
                )
            )
            shine_rotated = pygame.transform.rotate(shine_scaled, angle)
            shine_rotated.set_alpha(self.shine_alpha)
            shine_rect = shine_rotated.get_rect(center=self.pos)
            surface.blit(shine_rotated, shine_rect.topleft)
        
        for p in self.particles[:]:
            p.update()
            if not p.is_alive():
                self.particles.remove(p)
            else:
                p.draw(surface)

class IslandItem(BaseItem):
    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        self.hovered = False
        self.name = getattr(self, "name", "???")
        self.description = getattr(self, "description", "*insert cool description here*")

class ToolItem(BaseItem):
    LAYER_ORDER = ["blade", "guard", "pommel", "handle", "effect"]
    TOOLITEM_DEBUG = False  # Set to True for debug output
    # Profiling counters
    _profile_counts = {"_update_cache": 0, "get_scaled_hitbox": 0, "get_scaled_mask": 0}
    _profile_times = {"_update_cache": 0.0, "get_scaled_hitbox": 0.0, "get_scaled_mask": 0.0}
    _profile_frame = 0

    def __init__(self, manager, type, pos, nbt_data={}):
        super().__init__(manager, type, pos, nbt_data)
        # Shrink default scale
        self.scale = getattr(self, "scale", [0.7, 0.7])
        self.nbt = dict(nbt_data)
        self._cached_shadow_img = None
        self._cached_shadow_offset = None

    # Class-level cache for part images
    _part_image_cache = {}

    def _get_part_image(self, part_type, material):
        key = (part_type, material)
        if key in ToolItem._part_image_cache:
            return ToolItem._part_image_cache[key]
        path = f"assets/tools/parts/{part_type}/{material}.png"
        if os.path.exists(path):
            surf = pygame.image.load(path).convert_alpha()
            ToolItem._part_image_cache[key] = surf
            return surf
        ToolItem._part_image_cache[key] = None
        return None

    def _compose_tool_surface(self):
        # Compose the tool image (unscaled, unrotated) with new alignment logic and decorations
        part_surfs = {}
        part_sizes = {}
        decorations = {}
        # Load part images and decorations
        for part in ["blade", "handle", "pommel", "guard"]:
            part_info = self.nbt.get(part)
            if not part_info or not isinstance(part_info, dict):
                continue
            material = part_info.get("material")
            part_type = part_info.get("type", part)
            if not material:
                continue
            surf = self._get_part_image(part_type, material)
            part_surfs[part] = surf
            part_sizes[part] = surf.get_size() if surf else (0, 0)
            # Check for decoration
            deco_folder = f"assets/tools/parts/decoration_{part_type}"
            if os.path.isdir(deco_folder):
                # Find first png in folder (or you can extend to support multiple)
                for fname in os.listdir(deco_folder):
                    if fname.endswith(".png"):
                        deco_path = os.path.join(deco_folder, fname)
                        try:
                            decorations[part] = pygame.image.load(deco_path).convert_alpha()
                        except Exception as e:
                            print(f"[ToolItem] Failed to load decoration for {part}: {e}")
                        break

        blade_w, blade_h = part_sizes.get("blade", (0, 0))
        handle_w, handle_h = part_sizes.get("handle", (0, 0))
        pommel_w, pommel_h = part_sizes.get("pommel", (0, 0))
        guard_w, guard_h = part_sizes.get("guard", (0, 0))

        # --- Calculate positions ---
        # Blade: center left at (0, center_y)
        blade_pos = (0, 0)
        # Handle: right at (0, center_y)
        handle_pos = (-handle_w, 0)
        # Pommel: left of handle
        pommel_pos = (-handle_w - pommel_w, 0)

        # Find total width and height for surface
        min_x = min(0, handle_pos[0], pommel_pos[0])
        total_w = blade_w + handle_w + pommel_w
        max_h = max(blade_h, handle_h, pommel_h, guard_h)
        total_h = max_h
        center_y_img = total_h // 2
        composed = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

        # Calculate offsets for each part
        # Blade: center left at (handle_w + pommel_w, center_y_img)
        blade_draw_x = handle_w + pommel_w
        blade_draw_y = center_y_img - blade_h // 2
        # Handle: right at (handle_w + pommel_w, center_y_img)
        handle_draw_x = pommel_w
        handle_draw_y = center_y_img - handle_h // 2
        # Pommel: left at (0, center_y_img)
        pommel_draw_x = 0
        pommel_draw_y = center_y_img - pommel_h // 2
        # Guard: center between blade's left and handle's right
        guard_center_x = (blade_draw_x + handle_draw_x + handle_w) // 2
        guard_draw_x = guard_center_x - guard_w // 2
        guard_draw_y = center_y_img - guard_h // 2

        # --- Draw order: pommel, handle, blade, guard ---
        if pommel_w and pommel_h and part_surfs.get("pommel"):
            composed.blit(part_surfs["pommel"], (pommel_draw_x, pommel_draw_y))
            if decorations.get("pommel"):
                composed.blit(decorations["pommel"], (pommel_draw_x, pommel_draw_y))
        if handle_w and handle_h and part_surfs.get("handle"):
            composed.blit(part_surfs["handle"], (handle_draw_x, handle_draw_y))
            if decorations.get("handle"):
                composed.blit(decorations["handle"], (handle_draw_x, handle_draw_y))
        if blade_w and blade_h and part_surfs.get("blade"):
            composed.blit(part_surfs["blade"], (blade_draw_x, blade_draw_y))
            if decorations.get("blade"):
                composed.blit(decorations["blade"], (blade_draw_x, blade_draw_y))
        if guard_w and guard_h and part_surfs.get("guard"):
            composed.blit(part_surfs["guard"], (guard_draw_x, guard_draw_y))
            if decorations.get("guard"):
                composed.blit(decorations["guard"], (guard_draw_x, guard_draw_y))

        if self.TOOLITEM_DEBUG:
            print(f"[ToolItem] part_sizes: {part_sizes}")
            print(f"[ToolItem] draw_x: blade={blade_draw_x}, handle={handle_draw_x}, pommel={pommel_draw_x}, guard={guard_draw_x}")
            print(f"[ToolItem] nbt_data: {self.nbt}")
        return composed, (pommel_draw_x, center_y_img, guard_draw_x, handle_draw_x, pommel_draw_x, blade_draw_x)

    def _update_cache(self, screensize, rotation_scale, angle):
        if self.TOOLITEM_DEBUG:
            t0 = time.perf_counter()
        # Only update if something changed (do NOT include position in cache key)
        cache_key = (tuple(sorted(self.nbt.items())), tuple(self.scale), screensize, rotation_scale, angle)
        if getattr(self, '_last_cache_key', None) == cache_key:
            if self.TOOLITEM_DEBUG:
                ToolItem._profile_counts["_update_cache"] += 1
                ToolItem._profile_times["_update_cache"] += time.perf_counter() - t0
            return
        composed, _ = self._compose_tool_surface()
        scale_x = (screensize[0] / 480) * 1 * self.scale[0] / rotation_scale
        scale_y = (screensize[1] / 270) * 1 * self.scale[1] / rotation_scale
        upscaled_size = (
            int(composed.get_width() * rotation_scale),
            int(composed.get_height() * rotation_scale),
        )
        highres_img = pygame.transform.scale(composed, upscaled_size)
        rotated_img = pygame.transform.rotate(highres_img, angle)
        final_width = int(rotated_img.get_width() * abs(scale_x))
        final_height = int(rotated_img.get_height() * abs(scale_y))
        scaled_img = pygame.transform.scale(rotated_img, (final_width, final_height))
        if scale_x < 0 or scale_y < 0:
            scaled_img = pygame.transform.flip(scaled_img, scale_x < 0, scale_y < 0)
        self._cached_scaled_img = scaled_img
        self._cached_mask = pygame.mask.from_surface(scaled_img)
        # After computing self._cached_mask
        rects = self._cached_mask.get_bounding_rects()
        self._cached_hitbox_rect = rects[0] if rects else pygame.Rect(0, 0, 1, 1)

        # Cache the shadow image as well
        shadow_img = scaled_img.copy()
        shadow_alpha = 100
        shadow_img.fill((0, 0, 0, shadow_alpha), special_flags=pygame.BLEND_RGBA_MULT)
        self._cached_shadow_img = shadow_img
        self._cached_shadow_offset = (0, 10)  # Default shadow offset
        self._last_cache_key = cache_key
        if self.TOOLITEM_DEBUG:
            ToolItem._profile_counts["_update_cache"] += 1
            ToolItem._profile_times["_update_cache"] += time.perf_counter() - t0

    def get_scaled_mask(self, screensize, rotation_scale=1.0):
        if self.TOOLITEM_DEBUG:
            t0 = time.perf_counter()
        angle = -getattr(self, "rotation", 0)
        self._update_cache(screensize, rotation_scale, angle)
        if self.TOOLITEM_DEBUG:
            ToolItem._profile_counts["get_scaled_mask"] += 1
            ToolItem._profile_times["get_scaled_mask"] += time.perf_counter() - t0
        return self._cached_mask

    def get_scaled_hitbox(self, screensize, pos_override=None, rotation_scale=1.0):
        if self.TOOLITEM_DEBUG:
            t0 = time.perf_counter()
        angle = -getattr(self, "rotation", 0)
        self._update_cache(screensize, rotation_scale, angle)
        bounding = self._cached_hitbox_rect.copy()
        center_x, center_y = self.pos if pos_override is None else pos_override
        bounding.center = (center_x, center_y)
        if self.TOOLITEM_DEBUG:
            ToolItem._profile_counts["get_scaled_hitbox"] += 1
            ToolItem._profile_times["get_scaled_hitbox"] += time.perf_counter() - t0
            ToolItem._profile_frame += 1
            if ToolItem._profile_frame % 120 == 0:
                print("[ToolItem PROFILE] Calls (120f):", dict(ToolItem._profile_counts))
                print("[ToolItem PROFILE] Time (s, 120f):", {k: round(v, 4) for k, v in ToolItem._profile_times.items()})
                # Reset for next window
                for k in ToolItem._profile_counts:
                    ToolItem._profile_counts[k] = 0
                for k in ToolItem._profile_times:
                    ToolItem._profile_times[k] = 0.0
        return bounding

    def get_fast_bbox(self, screensize, pos_override=None):
        """
        Returns a fast, axis-aligned bounding box for quick collision checks for ToolItem.
        Uses the cached scaled image size if available, otherwise falls back to BaseItem logic.
        """
        if hasattr(self, '_cached_scaled_img') and self._cached_scaled_img is not None:
            width = self._cached_scaled_img.get_width()
            height = self._cached_scaled_img.get_height()
        else:
            s = self.scale
            x_scale = screensize[0] / 480 * s[0]
            y_scale = screensize[1] / 270 * s[1]
            scale = min(x_scale, y_scale)
            width = int(64 * scale)  # fallback guess
            height = int(64 * scale)
        pos = pos_override if pos_override else self.pos
        return pygame.Rect(pos[0] - width // 2, pos[1] - height // 2, width, height)

    def draw(self, surface, screensize, gui_manager, item_manager, rotation_scale, pos_override=None):
        angle = -getattr(self, "rotation", 0)
        self._update_cache(screensize, rotation_scale, angle)
        center_x, center_y = self.pos if pos_override is None else pos_override
        scaled_img = self._cached_scaled_img
        draw_x = center_x - scaled_img.get_width() // 2
        draw_y = center_y - scaled_img.get_height() // 2
        # Draw shadow (cached)
        if self._cached_shadow_img is not None:
            shadow_x = draw_x + self._cached_shadow_offset[0]
            shadow_y = draw_y + self._cached_shadow_offset[1]
            surface.blit(self._cached_shadow_img, (shadow_x, shadow_y))
        # Draw actual item
        surface.blit(scaled_img, (draw_x, draw_y))
        # Optionally print debug info
        if self.TOOLITEM_DEBUG:
            print(f"[ToolItem] draw at ({draw_x}, {draw_y}), size {scaled_img.get_size()}")

    @property
    def rarity(self):
        from utility.item_utility.itemMaker import ITEM_BASES
        # get all pieces and their rarity scores and then average them
        a = 0
        b = 0
        rarity_map = {
            "common": 0.1, "uncommon": 0.2, "rare": 0.4, "rare+": 0.5,
            "unique": 0.6, "elite": 0.7, "legendary": 0.85, "mythic": 0.95, "fabled": 1.0
        }
        parts = [self.blade, self.guard, self.handle, self.pommel] # parts of weapon

        try:
            for part in parts:
                data = ITEM_BASES.get(part.get("type"))
                if data == None:
                    continue
                rarity_str = data.get("nbt").get("rarity") # returns a str, eg. "common"
                a += rarity_map[rarity_str]
                b +=1
            return a/b

        except Exception as e:
            raise KeyError(f"tool {self} with itemtype {self.type} couldnt return rarity: {e}")

    @property
    def magic(self):
        from utility.item_utility.itemMaker import ITEM_BASES
        # get all pieces and their magic scores and then average them
        a = 0
        b = 0
        parts = [self.blade, self.guard, self.handle, self.pommel] # parts of weapon

        try:
            for part in parts:
                data = ITEM_BASES.get(part.get("type"))
                if data == None:
                    continue
                magic_int = data.get("nbt").get("magic") # returns an int 0-1, eg. 0.1
                a += magic_int
                b +=1
            return a/b

        except Exception as e:
            raise KeyError(f"tool {self} with itemtype {self.type} couldnt return magic: {e}")
    
    @property
    def quality(self):
        a = 0
        b = 0
        parts = [self.blade, self.guard, self.handle, self.pommel] # parts of weapon

        try:
            for part in parts:
                a += part.get("quality")
                b +=1
            return round(a/b, 3)

        except Exception as e:
            raise KeyError(f"tool {self} with itemtype {self.type} couldnt return magic: {e}")



