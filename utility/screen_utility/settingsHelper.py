import os
import pygame

class Dropdown:
    def __init__(self, rect, options, selected, font, label, id, settings=None):
        self.rect = pygame.Rect(rect)
        self.settings = settings
        self.label = label
        self.id = id
        self.open = False
        self.font = font

        # Internal option keys and selected key
        self.options = options  # ["on", "off"] etc.
        self.selected = selected  # "on"

        # Get translated labels if settings passed
        self.display_labels = [
            settings.translated_text(opt) if settings else opt
            for opt in options
        ]

        # Compute width based on max translated label
        label_texts = [f"{label}: {lbl}" for lbl in self.display_labels]
        max_width = max([font.size(txt)[0] for txt in label_texts]) if label_texts else 140
        self.rect.width = max(140, max_width + 10)



    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.open = not self.open
        elif event.type == pygame.MOUSEBUTTONDOWN and self.open:
            for i, opt in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                if opt_rect.collidepoint(mouse_pos):
                    self.selected = opt
                    self.open = False
                    return opt
            self.open = False

        # NEW: Only allow changing selection on scroll if open and mouse is over dropdown
        if event.type == pygame.MOUSEWHEEL and self.open and self.rect.collidepoint(mouse_pos):
            idx = self.options.index(self.selected)
            idx = (idx - event.y) % len(self.options)  # Scroll up/down changes index
            self.selected = self.options[idx]
            return self.selected

        return None


    def draw(self, surface):
        pygame.draw.rect(surface, (40, 40, 40, 220), self.rect, border_radius=4)
        label_index = self.options.index(self.selected)
        label_text = f"{self.label}: {self.display_labels[label_index]}"
        label_surf = self.font.render(label_text, False, (255, 255, 255))
        text_rect = label_surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        surface.blit(label_surf, text_rect)

        # ...
        if self.open:
            for i, opt in enumerate(self.options):
                opt_rect = pygame.Rect(self.rect.x, self.rect.y + (i+1)*self.rect.height, self.rect.width, self.rect.height)
                pygame.draw.rect(surface, (60, 60, 60, 220), opt_rect, border_radius=4)

                opt_surf = self.font.render(self.display_labels[i], False, (255, 255, 255))
                opt_rect_inner = opt_surf.get_rect(midleft=(opt_rect.x + 5, opt_rect.centery))
                surface.blit(opt_surf, opt_rect_inner)
                pygame.draw.rect(surface, (200, 200, 200), opt_rect, 1, border_radius=4)


class Slider:
    def __init__(self, rect, min_val, max_val, value, font, label, id):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.font = font
        self.label = label
        self.dragging = False
        self.id = id

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = mouse_pos[0] - self.rect.x
            rel_x = max(0, min(rel_x, self.rect.width))
            self.value = int(self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val))
        return self.value

    def draw(self, surface):
        pygame.draw.rect(surface, (40, 40, 40, 220), self.rect, border_radius=4)
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        pygame.draw.rect(surface, (100, 200, 255), (self.rect.x, self.rect.y, fill_width, self.rect.height), border_radius=4)
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 1, border_radius=4)
        label_surf = self.font.render(f"{self.label}: {self.value}", False, (255, 255, 255))
        surface.blit(label_surf, (self.rect.x + 5, self.rect.y - 18))

class SettingsHelper:
    def __init__(self, screen_size, settings_manager, helper):
        self.screen_size = screen_size
        self.settings = settings_manager
        self.helper = helper
        self.font = pygame.font.Font(self.settings.font, 13)
        self.active = False
        self.tabs = ["Video", "Audio", "Controls", "Misc"]
        #self.tabs = [self.settings.translated_text(t) for t in self.tabs]
        self.active_tab = 0
        self.scroll_offset = 0
        self.scroll_target = 0
        self.scroll_speed = 20  # how much scroll wheel changes scroll_target per tick
        self.scroll_lerp_speed = 0.2  # lerp speed for smooth scrolling

        self.margin = 20
        self.tab_width = 140
        self.start_y = self.margin + 40
        self.start_x = self.tab_width + self.margin
        self._init_ui()
        self._refresh_ui_fonts_and_labels()

    def _scan_languages(self):
        folder = os.path.join("assets", "translations")
        return [f[:-5] for f in os.listdir(folder) if f.endswith(".json")]

    def _scan_fonts(self):
        folder = "assets"
        return [f for f in os.listdir(folder) if f.lower().endswith(".ttf")]

    def _init_ui(self):
        sw, sh = self.screen_size
        tab_width = 140  # width of the left tabs
        margin = 20
        start_x = tab_width + margin + 10  # right of tabs + margin
        start_y = margin + 40
        element_width = 140
        element_height = 22
        spacing = 35


        self.elements_by_tab = {
            # add translations with self.settings.get_translated_text() or whatever teh function is
            0: [  # Video
                Dropdown((start_x, start_y, element_width, element_height), self._scan_languages(), self.settings.language, self.font, self.settings.translated_text("Language"), "label.language"),
                Dropdown((start_x, start_y + spacing, element_width, element_height), self._scan_fonts(), os.path.basename(self.settings.font), self.font, self.settings.translated_text("Font"), "label.font"),
                Slider((start_x, start_y + spacing * 2, element_width, 20), 8, 40, self.settings.font_hover_size, self.font, self.settings.translated_text("Font Hover Size"), "label.font_hover_size"),
            ],
            1: [  # Audio
                Slider((start_x, start_y, element_width, 20), 0, 100, 50, self.font, self.settings.translated_text("Music Volume"), "label.music_volume"),
                Slider((start_x, start_y + spacing, element_width, 20), 0, 100, 70, self.font, self.settings.translated_text("SFX Volume"), "label.sfx_volume"),
            ],
            2: [  # Controls
                Dropdown((start_x, start_y, element_width, element_height), ["mouse", "controller"], self.settings.input_type, self.font, self.settings.translated_text("Input Type"), "label.input_type"),
            ],
            3: [  # Misc
                Dropdown((start_x, start_y, element_width, element_height), ["on", "off"], "on", self.font, self.settings.translated_text("Tooltips"), "label.tooltips"),
            ],
        }


        self.ui_elements = self.elements_by_tab[self.active_tab]

        
    def get_active_elements(self):
        return self.elements_by_tab.get(self.active_tab, [])


    def open(self):
        self.active = True
        self._init_ui()

    def close(self):
        self.active = False
        self.settings.save()

    def toggle(self):
        if self.active:
            self.close()
        else:
            self.open()

    def handle_event(self, event, mouse_pos):
        if not self.active:
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()

        if event.type == pygame.MOUSEBUTTONDOWN:
            tab_x = 20  # left margin
            tab_y = 20  # top margin
            tab_height = 36

            for i, tab in enumerate(self.tabs):
                tab_rect = pygame.Rect(tab_x, tab_y + i * (tab_height + 10), self.tab_width, tab_height)
                if tab_rect.collidepoint(mouse_pos):
                    self.active_tab = i
                    self.scroll_offset = 0
                    self._init_ui()

        if event.type == pygame.MOUSEWHEEL:
            # Update scroll target smoothly and clamp later
            self.scroll_target += -event.y * self.scroll_speed

            # Calculate max scroll based on content height
            visible_height = self.screen_size[1] - self.start_y - 40
            content_height = len(self.get_active_elements()) * 60  # keep 60 or replace with your spacing

            max_scroll = max(0, content_height - visible_height)
            self.scroll_target = max(0, min(self.scroll_target, max_scroll))

        # Smoothly interpolate current scroll offset to target scroll
        self.scroll_offset += (self.scroll_target - self.scroll_offset) * self.scroll_lerp_speed

        # Update UI element positions using current scroll_offset (smooth)
        for i, elem in enumerate(self.get_active_elements()):
            elem.rect.y = self.start_y - self.scroll_offset + i * 60

        changed = False
        for elem in self.get_active_elements():
            result = elem.handle_event(event, mouse_pos)
            if result is not None:
                changed = True
                # Update settings based on the element label or type
                if isinstance(elem, Dropdown):
                    if elem.id == "label.language":
                        self.settings.language = elem.selected
                    elif elem.id == "label.font":
                        self.settings.font = os.path.join("assets", elem.selected)
                    elif elem.id == "label.input_type":
                        self.settings.input_type = elem.selected
                    if elem.id == "label.tooltips":
                        self.settings.tooltips = elem.selected
                        pass
                elif isinstance(elem, Slider):
                    if elem.id == "label.font_hover_size":
                        self.settings.font_hover_size = elem.value
                    elif elem.id == "label.music_volume":
                        self.settings.music_volume = elem.value
                    elif elem.id == "label.music_volume":
                        self.settings.sfx_volume = elem.value


        if changed:
            self.settings.save()
            self.helper._init_buttons(self.settings.font)
            self.font = pygame.font.Font(self.settings.font, 15)
            self._refresh_ui_fonts_and_labels() # this function is breaking it
    
    def _refresh_ui_fonts_and_labels(self):
        self.font = pygame.font.Font(self.settings.font, 13)
        for tab_id, elements in self.elements_by_tab.items():
            for elem in elements:
                elem.font = self.font
                elem.label = self.settings.translated_text(elem.label)
                if isinstance(elem, Dropdown):
                    elem.display_labels = [self.settings.translated_text(opt) for opt in elem.options]

                    # Recalculate width to fit updated translations
                    label_texts = [f"{elem.label}: {lbl}" for lbl in elem.display_labels]
                    max_width = max([self.font.size(txt)[0] for txt in label_texts]) if label_texts else 140
                    elem.rect.width = max(140, max_width + 10)


    def draw(self, surface):
        if not self.active:
            return
        overlay = pygame.Surface(self.screen_size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        tab_x = 20
        tab_y = 20
        tab_width = 140
        tab_height = 36

        for i, tab in enumerate(self.tabs):
            rect = pygame.Rect(tab_x, tab_y + i * (tab_height + 10), tab_width, tab_height)
            color = (120, 120, 120) if i == self.active_tab else (80, 80, 80)
            pygame.draw.rect(surface, color, rect, border_radius=4)
            label = self.font.render(tab, False, (255, 255, 255))
            surface.blit(label, (rect.x + 10, rect.y + 6))


        # Draw UI elements
        for elem in self.get_active_elements():
            elem.draw(surface)

        # Ensure dropdowns draw on top
        for elem in self.get_active_elements():
            if isinstance(elem, Dropdown) and elem.open:
                elem.draw(surface)

        # Scrollbar
        visible_height = self.screen_size[1] - self.start_y - 40
        content_height = len(self.get_active_elements()) * 60

        if content_height > visible_height:
            scrollbar_height = max(40, int(visible_height * visible_height / content_height))
            scrollbar_y = self.start_y + int(self.scroll_offset * visible_height / content_height)
            scrollbar_x = self.screen_size[0] - 30  # 30 px from right edge
            pygame.draw.rect(surface, (80, 80, 80), (scrollbar_x, self.start_y, 8, visible_height), border_radius=4)
            pygame.draw.rect(surface, (180, 180, 180), (scrollbar_x, scrollbar_y, 8, scrollbar_height), border_radius=4)



