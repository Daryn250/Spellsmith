import pygame
import math
import random
from utility.button import Button

class WeaponSelector:
    def __init__(self, virtual_size, item_on_anvil):
        self.virtual_size = virtual_size
        self.scroll_x = 0
        self.scroll_target = 0
        self.scroll_easing = 0.15
        self.items = []
        self.selected_index = 0
        self.font_title = pygame.font.Font("assets/GothicByte.ttf", 24)
        self.font_desc = pygame.font.Font("assets/GothicByte.ttf", 18)


        self.item_on_anvil = item_on_anvil
        self.material = getattr(item_on_anvil, "material", "copper")

        self.folder_stack = ["root"]
        self.unlocked_keys = set()
        # Unlock root folders and all their children
        for root_key in ["swords", "daggers", "scythes", "spears"]:
            self._unlock_recursive(root_key)
        self.key_lookup = self._build_key_lookup()
        self.structure = self._generate_structure()
        


        self.card_width = 180
        self.card_height = 220
        self.spacing = 30
        self.finished = False

        self.default_card_img = pygame.image.load("assets/screens/anvil/selector/folder.png").convert_alpha()

        self.button_back_img = pygame.image.load("assets/screens/anvil/selector/button1.png").convert_alpha()
        self.button_back_img = pygame.transform.scale(self.button_back_img, (self.button_back_img.get_width()*2, self.button_back_img.get_height()*2))
        self.button_info_img = pygame.image.load("assets/screens/anvil/selector/button2.png").convert_alpha()
        self.button_info_img = pygame.transform.scale(self.button_info_img, (self.button_info_img.get_width()*2, self.button_info_img.get_height()*2))
        self.button_start_img = pygame.image.load("assets/screens/anvil/selector/button3.png").convert_alpha()
        self.button_start_img = pygame.transform.scale(self.button_start_img, (self.button_start_img.get_width()*2, self.button_start_img.get_height()*2))

        self.font_dummy = pygame.font.Font(None, 1)  # Needed by Button class but text will be invisible

        self.button_back = Button(self.button_back_img, (100, self.virtual_size[1] - 60), "", self.font_dummy, (0,0,0), (0,0,0))
        self.button_info = Button(self.button_info_img, (200, self.virtual_size[1] - 60), "", self.font_dummy, (0,0,0), (0,0,0))
        self.button_start = Button(self.button_start_img, (self.virtual_size[0] - 100, self.virtual_size[1] - 60), "", self.font_dummy, (0,0,0), (0,0,0))

        self.all_buttons = [self.button_back, self.button_info, self.button_start]


        self.rotation_angles = {}
        self.rotation_velocities = {}
        self.scales = {}
        self.scale_target = 1

        # Hover state tracking
        self.hovered_index = None
        self.allow_hover = True  # Set to False if keyboard is used

        self.previewing_item = None  # Stores selected item for preview


        self.animate_cards()

    def _unlock_recursive(self, key):
        # Unlock key itself
        self.unlocked_keys.add(key)
        # Unlock children if any
        children = self._base_structure().get(key, {})
        for child_info in children.values():  # now each child_info is a dict
            child_key = child_info["key"]  # extract the key string
            if child_key not in self.unlocked_keys:
                self._unlock_recursive(child_key)


    
    def _base_structure(self):
        return {
            "root": {
                "Swords": {"key": "sword", "preview_path": "assets/previews/swords_preview.png"},
                "Daggers": {"key": "dagger", "preview_path": "assets/previews/daggers_preview.png"},
                "Scythes": {"key": "scythe", "preview_path": "assets/previews/scythes_preview.png"},
                "Spears": {"key": "spear", "preview_path": "assets/previews/spears_preview.png"},
            },
            "sword": {
                "Pommels": {"key": "pommel", "preview_path": "assets/previews/pommel.png"},
                "Guards": {"key": "guard", "preview_path": "assets/previews/guard.png"},
                "Handles": {"key": "handle", "preview_path": "assets/previews/handle.png"},
                "Blades": {"key": "blade", "preview_path": "assets/previews/blade.png"},
            },
            "pommel": {
                "Rounded Pommel": {"key": "rounded_pommel", "type": "item", "rarity": "common", "preview_path": "assets/previews/pommel.png", "mass":1},
                "Spiked Pommel": {"key": "spiked_pommel", "type": "item", "rarity": "uncommon", "preview_path": "assets/previews/pommel.png", "mass":2.5},
                "Blunt Pommel": {"key": "blunt_pommel", "type": "item", "rarity": "rare", "preview_path": "assets/previews/pommel.png", "mass":3},
                "Crystal Pommel": {"key": "crystal_pommel", "type": "item", "rarity": "rare+", "preview_path": "assets/previews/pommel.png", "mass":4},
                "Dagger Pommel": {"key": "dagger_pommel", "type": "item", "rarity": "unique", "preview_path": "assets/previews/pommel.png", "mass":4.5},
                "Orb Pommel": {"key": "orb_pommel", "type": "item", "rarity": "elite", "preview_path": "assets/previews/pommel.png", "mass":5},
                "Medallion Pommel": {"key": "medallion_pommel", "type": "item", "rarity": "legendary", "preview_path": "assets/previews/pommel.png", "mass":6},
                "Horned Pommel": {"key": "horned_pommel", "type": "item", "rarity": "mythic", "preview_path": "assets/previews/pommel.png", "mass":8},
                "Dragonslayer Pommel": {"key": "dragonslayer_pommel", "type": "item", "rarity": "fabled", "preview_path": "assets/previews/pommel.png", "mass":10},
                },

            "dagger": {
                "Pommel": {"key": "pommel", "preview_path": "assets/previews/pommel.png"},
                "Cross Guards": {"key": "guard", "preview_path": "assets/previews/cross_guard.png"},
                "Grips": {"key": "grip", "preview_path": "assets/previews/grip.png"},
                "Blade": {"key": "dagger_blade", "preview_path": "assets/previews/dagger_blade.png"},
            },
            "scythe": {
                "Grips": {"key": "grip", "preview_path": "assets/previews/grip.png"},
                "Snath": {"key": "scythe_handle", "preview_path": "assets/previews/scythe_handle.png"},
                "Chine": {"key": "scythe_support", "preview_path": "assets/previews/scythe_support.png"},
                "Blade": {"key": "scythe_blade", "preview_path": "assets/previews/scythe_blade.png"},
            },
            "spear": {
                "Grips": {"key": "grip", "preview_path": "assets/previews/grip.png"},
                "Handles": {"key": "spear_handle", "preview_path": "assets/previews/spear_handle.png"},
                "Spear Heads": {"key": "spearhead", "preview_path": "assets/previews/spearhead.png"},
            },
        }


    def _build_key_lookup(self):
        base = self._base_structure()
        lookup = {}

        def recurse(folder, tool_family=None, parent_part=None):
            for name, info in base.get(folder, {}).items():
                key = info["key"]
                item_type = info.get("type", "folder")
                
                if folder == "root":
                    # top-level: this is a new weapon type
                    current_tool_family = key
                    current_part = None
                else:
                    current_tool_family = tool_family
                    current_part = key if item_type == "folder" else parent_part

                lookup[key] = {
                    "tool_family": current_tool_family,
                    "part": current_part,
                    "type": item_type
                }

                if item_type == "folder":
                    recurse(key, current_tool_family, current_part)


        recurse("root")
        return lookup

    def _generate_structure(self):
        base = self._base_structure()

        expanded = {}
        for folder, contents in base.items():
            expanded[folder] = []
            for name, info in contents.items():
                key = info["key"]
                item_type = info.get("type", "folder")
                rarity = info.get("rarity", "common")
                rarity_icon_path = f"assets/screens/anvil/rarityCards/{rarity}.png"

                # in the future load the correct preview image by getting the material of the item on the table
                # and then using the following path to load the preview image
                """tool_family = self.key_lookup.get(key, {}).get("tool_family", "unknown")
                part = self.key_lookup.get(key, {}).get("part", "unknown")
                fn = f"assets/tools/{tool_family}/{part}/{self.material}.png"""


                try:
                    preview_img = pygame.image.load(info.get[preview_img]).convert_alpha()
                except:
                    preview_img = pygame.image.load("assets/error.png").convert_alpha()

                try:
                    rarity_img = pygame.image.load(rarity_icon_path).convert_alpha()
                except:
                    rarity_img = None

                expanded[folder].append({
                    "type": item_type,
                    "name": name,
                    "key": key,
                    "locked": key not in self.unlocked_keys,
                    "preview": preview_img,
                    "rarity": rarity,
                    "rarity_img": rarity_img,
                    "mass": info.get("mass", 0)
                })
        return expanded




    
    def animate_cards(self):
        for i in range(len(self.get_current_folder())):
            self.rotation_velocities[i] = random.uniform(-2, 2)
            self.rotation_angles[i] = 0
            self.scales[i] = 1.2  # Start scaled up

    
    def _get_clicked_index(self, mouse_pos, clip_rect=None):
        items = self.get_current_folder()
        if clip_rect:
            _, clip_y, _, clip_h = clip_rect
            y = clip_y + (clip_h // 2 - self.card_height // 2)
        else:
            y = self.virtual_size[1] // 2 - self.card_height // 2

        x0 = 80 + self.scroll_x

        for i in range(len(items)):
            x = x0 + i * (self.card_width + self.spacing)
            rect = pygame.Rect(x, y, self.card_width, self.card_height)
            if rect.collidepoint(mouse_pos):
                return i
        return None


    def update(self, dt, virtual_mouse):
        items = self.get_current_folder()

        # Proper content width calculation
        item_count = len(items)
        if item_count > 0:
            content_width = item_count * (self.card_width + self.spacing) - self.spacing
            visible_width = self.virtual_size[0] - 160  # 80px margin left + right
            max_scroll = max(0, content_width - visible_width)
        else:
            max_scroll = 0

        # Clamp scroll target BEFORE applying it

        # Apply easing only ONCE
        dx = self.scroll_target - self.scroll_x
        self.scroll_x += dx * self.scroll_easing

        # Animate cards (rotation/scale)
        for i in range(len(items)):
            self.rotation_velocities.setdefault(i, 0)
            self.rotation_angles.setdefault(i, 0)

            self.rotation_velocities[i] += dx * 0.005
            self.rotation_velocities[i] *= 0.85

            if abs(self.rotation_angles[i]) > 0:
                if self.rotation_angles[i] < 0:
                    self.rotation_velocities[i] += (-self.rotation_angles[i]) / random.uniform(7, 13)
                else:
                    self.rotation_velocities[i] -= (self.rotation_angles[i]) / random.uniform(7, 13)

            self.rotation_angles[i] += self.rotation_velocities[i]

            # Smooth scale animation
            current_scale = self.scales.get(i, 1.0)
            self.scales[i] = current_scale + (self.scale_target - current_scale) * 0.1

        # Hover
        if self.allow_hover:
            self._update_hover(virtual_mouse)





    def _update_hover(self, mouse_pos):
        items = self.get_current_folder()
        x0 = 80 + self.scroll_x
        y = self.virtual_size[1] // 2 - self.card_height // 2

        for i, item in enumerate(items):
            x = x0 + i * (self.card_width + self.spacing)
            base_rect = pygame.Rect(x, y, self.card_width, self.card_height)

            # Apply same rotation and scale as draw()
            rarity = item.get("rarity", "common")
            rarity_img = item.get("rarity_img")
            base_img = (
                pygame.transform.scale(rarity_img, (self.card_width, self.card_height))
                if rarity != "common" and rarity_img
                else pygame.transform.scale(self.default_card_img, (self.card_width, self.card_height))
            )
            angle = self.rotation_angles.get(i, 0)
            scale = self.scales.get(i, 1.0)
            rotated_img = pygame.transform.rotozoom(base_img, angle, scale)
            rotated_rect = rotated_img.get_rect(center=base_rect.center)

            if rotated_rect.collidepoint(mouse_pos):
                # Optional: more accurate shape detection with mask
                mask = pygame.mask.from_surface(rotated_img)
                rel_x = mouse_pos[0] - rotated_rect.x
                rel_y = mouse_pos[1] - rotated_rect.y
                if 0 <= rel_x < rotated_rect.width and 0 <= rel_y < rotated_rect.height:
                    if mask.get_at((int(rel_x), int(rel_y))):
                        if self.hovered_index != i:
                            self.hovered_index = i
                            self.selected_index = i
                        return

        self.hovered_index = None

    def draw_fullscreen_item_preview(self, surface):
        item = self.previewing_item
        if not item:
            return

        center_x = self.virtual_size[0] // 2
        center_y = self.virtual_size[1] // 2

        surface.fill((10, 10, 10))  # Dark background

        # Item preview image
        preview = item.get("preview")
        if preview:
            scaled = pygame.transform.scale(preview, (180, 180))
            surface.blit(scaled, scaled.get_rect(center=(center_x-120, center_y)))

        # Item name
        name_surf = self.font_title.render(item["name"], False, (255, 255, 255))
        surface.blit(name_surf, name_surf.get_rect(center=(center_x, center_y - 200)))

        # Stat bars
        def draw_bar(label, value, y_offset, color):
            max_width = 300
            bar_height = 20
            value = max(0, min(value, 1))
            pygame.draw.rect(surface, (50, 50, 50), (center_x - max_width // 2, center_y + y_offset, max_width, bar_height))
            pygame.draw.rect(surface, color, (center_x - max_width // 2, center_y + y_offset, int(max_width * value), bar_height))
            text = self.font_desc.render(label, False, (255, 255, 255))
            surface.blit(text, (center_x - max_width // 2, center_y + y_offset - 22))

        # Mock values for now
        rarity_map = {
            "common": 0.1, "uncommon": 0.2, "rare": 0.4, "rare+": 0.5,
            "unique": 0.6, "elite": 0.7, "legendary": 0.85, "mythic": 0.95, "fabled": 1.0
        }
        rarity_val = rarity_map.get(item.get("rarity", "common"), 0.1)
        difficulty = 1
        power = min(1.0, float(item.get("mass", 1)) / 100000)

        draw_bar("Rarity", rarity_val, 40, (90, 150, 255))
        draw_bar("Difficulty", difficulty, 80, (255, 180, 80))
        draw_bar("Power", power, 120, (255, 60, 60))

        # Confirm / Back
        confirm_txt = self.font_desc.render("[Enter] Confirm    [Backspace] Cancel", False, (180, 180, 180))
        surface.blit(confirm_txt, confirm_txt.get_rect(center=(center_x, center_y + 200)))



    def handle_event(self, event, mouse_pos):
        if self.previewing_item:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.finished = True
                elif event.key == pygame.K_BACKSPACE:
                    self.previewing_item = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.button_back.checkForInput(mouse_pos):
                    self.previewing_item = None
                    return
                elif self.button_info.checkForInput(mouse_pos):
                    print("Info pressed in preview.")  # You can show more info here later
                    return
                elif self.button_start.checkForInput(mouse_pos):
                    self.tryFinish()
                    return

            return  # Skip all other interactions while previewing


        if event.type == pygame.KEYDOWN:
            self.allow_hover = False  # Stop hover updates until mouse moves
            if event.key == pygame.K_RIGHT:
                self.selected_index = min(self.selected_index + 1, len(self.get_current_folder()) - 1)
            elif event.key == pygame.K_LEFT:
                self.selected_index = max(self.selected_index - 1, 0)
            elif event.key == pygame.K_RETURN:
                selected = self.get_current_folder()[self.selected_index]
                if selected["type"] == "folder":
                    self.folder_stack.append(selected["key"])
                    self.animate_cards()
                elif selected["type"] == "item":
                    print(f"Selected FINAL item: {selected['name']} ({selected['key']})")
                    self.previewing_item = selected
            elif event.key == pygame.K_BACKSPACE:
                if len(self.folder_stack) > 1:
                    self.folder_stack.pop()
                    self.animate_cards()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked_index = self._get_clicked_index(mouse_pos, getattr(self, "last_clip_rect", None))
                if clicked_index is not None:
                    self.selected_index = clicked_index
                    selected = self.get_current_folder()[clicked_index]
                    if selected["type"] == "folder":
                        self.folder_stack.append(selected["key"])
                        self.animate_cards()
                    elif selected["type"] == "item":
                        self.previewing_item = selected





            elif event.button == 4:
                self.scroll_target -= 80
            elif event.button == 5:
                self.scroll_target += 80


        elif event.type == pygame.MOUSEMOTION:
            self.allow_hover = True  # Resume hover tracking

    def get_current_folder(self):
        return self.structure.get(self.folder_stack[-1], [])

    def draw_item_grid(self, surface, clip_rect=None):
        items = self.get_current_folder()
        if clip_rect:
            _, clip_y, _, clip_h = clip_rect
            y = clip_y + (clip_h // 2 - self.card_height // 2)
            self.last_clip_rect = clip_rect
        else:
            y = self.virtual_size[1] // 2 - self.card_height // 2

        x0 = 80 + self.scroll_x

        for i, item in enumerate(items):
            x = x0 + i * (self.card_width + self.spacing)
            rect = pygame.Rect(x, y, self.card_width, self.card_height)

            # Select background based on rarity
            rarity = item.get("rarity", "common")
            rarity_img = item.get("rarity_img")
            base_img = (
                pygame.transform.scale(rarity_img, (self.card_width, self.card_height))
                if rarity != "common" and rarity_img
                else pygame.transform.scale(self.default_card_img, (self.card_width, self.card_height))
            )

            angle = self.rotation_angles.get(i, 0)
            scale = self.scales.get(i, 1.0)

            rotated_img = pygame.transform.rotozoom(base_img, angle, scale)
            rotated_rect = rotated_img.get_rect(center=rect.center)
            surface.blit(rotated_img, rotated_rect.topleft)

            # Alpha mask outline for selection
            if i == self.selected_index:
                mask = pygame.mask.from_surface(rotated_img)
                outline = mask.outline()
                if outline:
                    offset = rotated_rect.topleft
                    pygame.draw.lines(surface, (255, 255, 0), True,
                                    [(x + offset[0], y + offset[1]) for x, y in outline], 1)

            # Preview image
            preview_img = item.get("preview")
            if preview_img:
                preview_scaled = pygame.transform.scale(preview_img, (self.card_width - 60, self.card_width - 60))
                preview_scaled = pygame.transform.rotate(preview_scaled, angle)
                preview_rect = preview_scaled.get_rect(center=(rect.centerx, y + 70))
                surface.blit(preview_scaled, preview_rect)

            # Name text
            name = self.font_title.render(item["name"], False, (255, 255, 255))
            name_rect = name.get_rect(center=(rect.centerx, y + 130))
            surface.blit(name, name_rect)

            # Description
            desc = "Folder" if item["type"] == "folder" else "Minimum Mass: " + str(item["mass"])
            desc_surf = self.font_desc.render(desc, False, (180, 180, 180))
            desc_rect = desc_surf.get_rect(center=(rect.centerx, y + 170))
            surface.blit(desc_surf, desc_rect)
    
    def draw(self, surface, clip_rect=None):
        if self.previewing_item:
            self.draw_fullscreen_item_preview(surface)
            for button in self.all_buttons:
                button.update(surface)
        else:
            self.draw_item_grid(surface, clip_rect)

    def tryFinish(self):
        i = self.item_on_anvil
        i2 = self.previewing_item
        if getattr(i, "mass", 1) >= i2.get("mass"):
            self.finished = True

    def get_selected_type(self):
        # {'type': 'item', 
        # 'name': 'Rounded', 
        # 'key': 'rounded_pommel', 
        # 'locked': True, 
        # 'preview': <Surface(32x32x32 SW)>, 
        # 'rarity': 'common', 
        # 'rarity_img': <Surface(18x22x32 SW)>, 
        # 'mass': '1'}
        return self.previewing_item


