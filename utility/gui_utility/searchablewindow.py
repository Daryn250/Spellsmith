import pygame
from utility.item_utility.itemMaker import *
from utility.item_utility.item_flags import DraggableFlag
from utility.item_utility.item_to_info import item_to_info

class SearchableWindow:
    def __init__(self, title, instance_manager, item_manager, gui_manager, allowed_types, max_capacity = 10, width=300, slide_speed=2):
        self.title = title
        self.width = width
        self.slide_speed = slide_speed
        self.instance_manager = instance_manager
        self.font = pygame.font.Font(instance_manager.settings.font, 20)
        self.sfx = instance_manager.sfx_manager
        self.allowed_types = allowed_types
        self.gui_manager = gui_manager
        self.max_capacity = max_capacity

        # Animation
        self.x_offset = width  # starts off-screen
        self.target_x_offset = width
        self.animating = False
        self.anim_direction = 0  # 1 for opening, -1 for closing
        self.open = False

        # Search
        self.search_text = ""
        self.search_active = False

        # Items (full BaseItem objects)
        self.items = []
        self.hovered_item = None
        self.selected_item = None


        # Scrolling
        self.scroll_y = 0
        self.target_scroll_y = 0
        self.scroll_speed = 40
        self.scroll_smoothness = 0.2  # lower = smoother

        # Layout constants
        self.padding = 10
        self.search_height = 30
        self.item_height = 50
        self.icon_size = 40

        self.item_manager = item_manager

        # Frame image for icon (custom)
        self.icon_frame = pygame.Surface((self.icon_size, self.icon_size), pygame.SRCALPHA)
        pygame.draw.rect(self.icon_frame, (200, 200, 200), self.icon_frame.get_rect(), border_radius=6)

    def start_animation(self, direction):
        self.anim_direction = direction  # 1 = open, -1 = close
        self.anim_time = 0.0
        self.anim_duration = 0.1  # seconds
        self.animating = True

        if direction == 1:  # opening
            self.target_x_offset = 0
        else:  # closing
            self.target_x_offset = self.width


    def toggle(self):
        if self.open:
            self.start_animation(-1)
        else:
            self.start_animation(1)

    def update(self, dt):
        if self.animating:
            self.anim_time += (dt/1000)
            t = min(self.anim_time / self.anim_duration, 1.0)  # 0–1

            # cosine ease
            eased = (1 - math.cos(t * math.pi)) / 2  

            if self.anim_direction == 1:  # opening
                self.x_offset = self.width * (1 - eased)
            else:  # closing
                self.x_offset = self.width * eased

            if t >= 1.0:
                self.x_offset = self.target_x_offset
                self.animating = False
                self.open = self.anim_direction == 1  # track open state

        # Smooth scrolling
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * self.scroll_smoothness




    def add_item(self, item):
        """Store a full BaseItem object."""
        self.items.append(item)

    def handle_event(self, event, virtual_size, virtual_mouse):
        """Handle events with automatic scaling from virtual to real coordinates."""
        if not self.open:
            return
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.item_manager.get_dragged()!=None:
            # If mouse released inside the list_area
            if self.window_rect.collidepoint(virtual_mouse):
                if getattr(self.item_manager.get_dragged(), "type", None) in self.allowed_types:  # only allow certain type/flag
                    if len(self.items)<self.max_capacity:
                        self.add_item(self.item_manager.get_dragged())
                        self.sfx.play_sound("gui_success")
                        self.item_manager.remove_item(self.item_manager.get_dragged().uuid, self.gui_manager)

        
        

        if event.type == pygame.KEYDOWN:
            if self.search_active:
                if event.key == pygame.K_BACKSPACE:
                    self.search_text = self.search_text[:-1]
                elif event.key == pygame.K_RETURN:
                    self.search_active = False
                    self.sfx.play_sound("gui_success")
                else:
                    self.sfx.play_sound("gui_key_down")
                    self.search_text += event.unicode
        if event.type == pygame.KEYUP and self.search_active:
            self.sfx.play_sound("gui_key_up")

        if event.type == pygame.MOUSEMOTION:
            try:
                prev_hover = self.hovered_item
                self.hovered_item = None
                if self.list_area.collidepoint(virtual_mouse):
                    rel_y = virtual_mouse[1] - self.list_area.y - self.scroll_y
                    index = int(rel_y // self.item_height)
                    filtered = self.filtered_items()
                    if 0 <= index < len(filtered):
                        self.hovered_item = filtered[index]

                # play highlight sound when entering a new item
                if self.hovered_item is not None and self.hovered_item != prev_hover:
                    self.sfx.play_sound("gui_hover")
            except:
                pass


        
        elif event.type == pygame.MOUSEBUTTONDOWN and virtual_mouse:
            if event.button == 1:
                # --- Handle clicking on an item ---
                if self.list_area.collidepoint(virtual_mouse):
                    rel_y = virtual_mouse[1] - self.list_area.y - self.scroll_y
                    index = int(rel_y // self.item_height)
                    filtered = self.filtered_items()
                    if 0 <= index < len(filtered):
                        item = filtered[index]

                        # Remove it from the window right away
                        if item in self.items:
                            self.items.remove(item)
                        
                        self.item_manager.add_item(item)
                        item.pos = virtual_mouse

                        # Start dragging using the same logic as BaseScreen
                        mx, my = virtual_mouse
                        DraggableFlag.dragging_item = item
                        DraggableFlag.offset = (0, 0)
                        DraggableFlag.last_pos = virtual_mouse
                        item.dragging = True
                        item.dragging_for = 0
                        item.currentGravity = 0
                        item.floor = item.pos[1] + 30

                        self.sfx.play_sound("gui_pickup")
                        return  # prevent further handling



            elif event.button == 4:  # scroll up
                self.target_scroll_y = min(self.target_scroll_y + self.scroll_speed, 0)
            elif event.button == 5:  # scroll down
                max_scroll = -max(0, len(self.filtered_items()) * self.item_height - self.list_area.height)
                self.target_scroll_y = max(self.target_scroll_y - self.scroll_speed, max_scroll)


    def filtered_items(self):
        if not self.search_text:
            return self.items
        return [item for item in self.items if self.search_text.lower() in item.item_name.lower()]

    def draw(self, surface):
        screen_w, screen_h = surface.get_size()

        # Window position
        window_rect = pygame.Rect(screen_w - self.width + self.x_offset, 0, self.width, screen_h)
        self.window_rect = window_rect

        # Background
        bg = pygame.Surface((self.width, screen_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 180))  # translucent black
        surface.blit(bg, (window_rect.x, 0))

 

        # Title
        title_surf = self.font.render(self.title, False, (255, 255, 255))
        surface.blit(title_surf, (window_rect.x + self.padding, self.padding))

        # Search bar
        self.search_bar_rect = pygame.Rect(
            window_rect.x + self.padding,
            self.padding + title_surf.get_height() + 5,
            self.width - self.padding * 2,
            self.search_height
        )
        pygame.draw.rect(surface, (50, 50, 50), self.search_bar_rect, border_radius=4)
        search_text_surf = self.font.render(self.search_text or "Search...", False, (200, 200, 200))
        text_y = self.search_bar_rect.y + (self.search_bar_rect.height - search_text_surf.get_height()) // 2
        surface.blit(search_text_surf, (self.search_bar_rect.x + 5, text_y))


        # Item list area
        self.list_area = pygame.Rect(
            window_rect.x + self.padding,
            self.search_bar_rect.bottom + self.padding,
            self.width - self.padding * 2,
            screen_h - (self.search_bar_rect.bottom + self.padding)
        )

        # Clip for scrolling
        clip_backup = surface.get_clip()
        surface.set_clip(self.list_area)

        y_offset = self.list_area.y + self.scroll_y
        for item in self.filtered_items():
            row_rect = pygame.Rect(self.list_area.x, y_offset+2, self.list_area.width, self.item_height-2)

            # background box
            bg_color = (40, 40, 40)
            if item == self.hovered_item:
                bg_color = (70, 70, 100)
            pygame.draw.rect(surface, bg_color, row_rect, border_radius=8)

            # icon
            icon_rect = pygame.Rect(row_rect.x + self.padding,
                                    row_rect.y + (self.item_height - self.icon_size)//2,
                                    self.icon_size, self.icon_size)

            surface.blit(self.icon_frame, icon_rect.topleft)

            # Scale image proportionally
            img_w, img_h = item.image.get_size()
            scale = min(self.icon_size / img_w, self.icon_size / img_h)
            new_w, new_h = int(img_w * scale), int(img_h * scale)
            item_img = pygame.transform.scale(item.image, (new_w, new_h))

            # Center inside icon rect
            img_x = icon_rect.x + (self.icon_size - new_w)//2
            img_y = icon_rect.y + (self.icon_size - new_h)//2
            surface.blit(item_img, (img_x, img_y))


            # text
            display_name = item_to_info(item, False, self.instance_manager.settings.language).title
            text_surf = self.font.render(display_name, False, (255, 255, 255))

            surface.blit(text_surf, (icon_rect.right + self.padding, row_rect.y + (self.item_height - text_surf.get_height()) // 2))

            y_offset += self.item_height


        surface.set_clip(clip_backup)

        total_height = len(self.filtered_items()) * self.item_height
        if total_height > self.list_area.height:
            bar_height = max(20, self.list_area.height * self.list_area.height // total_height)
            scroll_range = total_height - self.list_area.height
            bar_y = self.list_area.y + int(-self.scroll_y / scroll_range * (self.list_area.height - bar_height))
            bar_rect = pygame.Rect(self.list_area.right - 6, bar_y, 4, bar_height)
            pygame.draw.rect(surface, (180, 180, 180), bar_rect, border_radius=2)


    def save_data(self):
        """
        Returns a JSON-compatible dict of loadable items for saving/loading.
        Each item is stored under a unique key.
        """
        save = {}
        for idx, item in enumerate(self.items):
            if not hasattr(item, "type"):
                continue

            data = {
                "class": item.__class__.__name__,
                "type": item.type,
                "pos": list(item.pos),
                **item.to_nbt()
            }

            # Handle callable next_screen
            if hasattr(item, "next_screen"):
                next_screen = item.next_screen
                data["next_screen"] = next_screen.__name__ if callable(next_screen) else next_screen

            # use index as key (or swap for a unique id if you have one)
            save[str(idx)] = data

        return save

    
    def load_from_save_data(self, data: dict):
        # takes a json dict and loads items to self
        saved_uuids = set(data.keys())
        self.items = [item for item in self.items if getattr(item, "uuid", None) not in saved_uuids]

        item_class_map = {
            "BaseItem": BaseItem,
            "BottleItem": BottleItem,
            "MaterialItem": MaterialItem,
            "CharmItem": CharmItem,
            "PartItem": PartItem,
            "GemItem": GemItem,
            "ToolItem": ToolItem
        }

        for uuid, entry in data.items():
            try:
                pos = tuple(entry["pos"])
                class_name = entry.get("class", "BaseItem")
                nbt = {k: v for k, v in entry.items() if k not in {"class", "type", "pos", "next_screen"}}

                item_type = entry["type"]
                item_class = item_class_map.get(class_name, BaseItem)
                item = item_class(self, item_type, pos, nbt)

                # restore uuid if item supports it
                if hasattr(item, "uuid"):
                    item.uuid = uuid

                # restore callable/next_screen if needed
                if "next_screen" in entry:
                    ns = entry["next_screen"]
                    item.next_screen = getattr(self, ns, ns)  # fallback: raw value

                self.items.append(item)

            except Exception as e:
                print(f"[SearchableWindow.py] Failed to load item: {entry.get('uuid', uuid)} - {e}")
