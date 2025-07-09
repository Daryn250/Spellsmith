import pygame
import random
import math
from utility.animated_sprite import AnimatedTile
from utility.item_utility.charmWindows import returnCharmWindow
from utility.screen_utility.screenManager import get_screen_function
import json
from utility.item_utility.item_flag_handlers import (
    handle_draggable,
    handle_charm,
    handle_hangable,
    handle_temperature_particles
)
from utility.particle import make_tiny_sparkle

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

            self.floor = pos[1]
            self.dragging = False

        # for the charm class:
        if "charm" in self.flags:
            self.is_clicked = False

        # for the hanging class
        if "hangable" in self.flags:
            self.NAIL_IMAGE = pygame.image.load("assets/gui/charm_board/nail.png").convert_alpha()
            self.attached_to = None
            self.show_nail = False

        self.particles = []

    @property
    def image(self):
        return self.img.get_current_frame() if self.animated else self.img

    

    def to_nbt(self, exclude=[]):
        base_exclude = [
            "manager", "pos", "type", "is_hovered", "img", "floor", "ovx", "ovy",
            "dragging", "nbt", "window", "NAIL_IMAGE", "trick", "particles", "locked",
            "liquid_anim", "cork_img", "original_mask_img", "cached_mask_surface", "cached_mask",
            "shine_img", "glow_img"
        ]
        safe_nbt = {}
        for k, v in self.__dict__.items():
            if k in base_exclude or k in exclude:
                continue
            safe_nbt[k] = v
        return safe_nbt


    def update(self, screen, gui_manager, virtual_size, bounds=None, dt=None):
        if self.animated and dt:
            self.img.update(dt)

        if "draggable" in self.flags:
            handle_draggable(self, screen, gui_manager, virtual_size, bounds)

        if "charm" in self.flags:
            handle_charm(self, screen, gui_manager)

        if "hangable" in self.flags:
            handle_hangable(self, screen)

        handle_temperature_particles(self)

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

        center_x, center_y = self.pos
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






        if getattr(self, "is_clicked", False):
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

    def get_scaled_hitbox(self, screensize):
        s = self.scale
        x_scale = screensize[0] / 480 * s[0]
        y_scale = screensize[1] / 270 * s[1]
        scale = min(x_scale, y_scale)
        width = int(self.image.get_width() * scale)
        height = int(self.image.get_height() * scale)
        return pygame.Rect(self.pos[0] - width // 2, self.pos[1] - height // 2, width, height)

    @property
    def uniform_scale(self):
        scale = self.scale
        return (scale, scale) if isinstance(scale, (int, float)) else scale

    def start_screen_switch(self, screen, screenSwitcher, baseScreen):
        if type(self.next_screen) == str:
            self.next_screen = get_screen_function(self.next_screen)
        screenSwitcher.start(lambda: self.next_screen(screen),
                             save_callback=lambda: baseScreen.save_items("saves/save1.json"))


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
        self.liquid_anim = AnimatedTile("assets/liquids/water", frame_duration=100)
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
        surface.blit(masked_liquid, masked_rect.topleft)
        surface.blit(rotated_bottle, bottle_rect.topleft)

        # --- Cork on top ---
        cork_img = pygame.transform.scale(self.cork_img, bottle_size)
        rotated_cork = pygame.transform.rotate(cork_img, angle)
        cork_rect = rotated_cork.get_rect(center=(center_x, center_y))
        surface.blit(rotated_cork, cork_rect.topleft)


        


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

    def update(self, screen, gui_manager, *args, **kwargs):
        super().update(screen, gui_manager, *args, **kwargs)
        if self.is_clicked:
            if self.window is None:
                self.window = returnCharmWindow(self)
                gui_manager.windows.append(self.window)
        elif self.window:
            if self.window in gui_manager.windows:
                gui_manager.windows.remove(self.window)
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

