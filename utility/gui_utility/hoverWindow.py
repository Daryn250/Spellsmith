import pygame
import math
from utility.animated_sprite import AnimatedTile
from utility.settingsManager import *
from utility.tool_utility.temperatureHandler import get_temp_range
from utility.gui_utility.color_utils import get_temperature_color

class HoverData:
    def __init__(self, label, value=None, data_type="number", anim_tile=None, color=(255, 255, 255), lookup_label = None):
        self.label = label
        self.value = value
        self.data_type = data_type  # "number", "percent", "highlight", "bar"
        self.anim_tile = anim_tile  # For highlight types
        self.color = color
        self.lookup_label = lookup_label
    def debug_print(self):
        print(f"label: {self.label}")
        print(f"value: {self.value}")
        print(f"data_type: {self.data_type}")
        print(f"color: {self.color}")
        print(f"lookup_label: {self.lookup_label}")

class HoverInfo:
    def __init__(self, title="", description="", icon=None, data=None, reduced_data=None, mode="default", source_item=None):
        self.title = title
        self.description = description
        self.icon = icon
        self.data = data if data else []
        self.reduced_data = reduced_data if reduced_data else []
        self.mode = mode
        self.margin = 6
        self.padding = 4
        self.columns = 3
        self.source_item = source_item  # tracks the item for updating information about the item so you dont gotta keep hovering over it lol

    def wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            test_line = (current + " " + word).strip()
            if font.size(test_line)[0] <= max_width:
                current = test_line
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return [font.render(line, False, (255, 255, 255)) for line in lines]

    def draw(self, surface, pos, settings, color=(255, 255, 255), bg_color=(0, 0, 0, 180)):
        font = pygame.font.Font(settings.font, settings.font_hover_size)
        small_font = pygame.font.Font(settings.font, settings.gui_size)
        reduced = self.mode == "reduced"
        small_font_reduced = pygame.font.Font(settings.font, int(12 * 0.75))

        data_to_draw = self.reduced_data if reduced else self.data
        highlights = [d for d in data_to_draw if d.data_type == "highlight" and d.anim_tile is not None]
        numbers = [d for d in data_to_draw if d.data_type in ("number", "percent") and d.value is not None]
        bars = [d for d in data_to_draw if d.data_type == "bar" and d.value is not None]

        title_surface = font.render(self.title, False, (255, 255, 255)) if self.title else None
        title_width = title_surface.get_width() if self.mode == "reduced" else max(200, title_surface.get_width())
        wrap_width = title_width - self.padding * 2

        lines = []
        line_widths = []

        if self.title:
            lines.append(title_surface)
            line_widths.append(title_surface.get_width())

        if self.description and not reduced:
            wrapped_desc = self.wrap_text(self.description, small_font, wrap_width)
            lines.extend(wrapped_desc)
            line_widths.extend([line.get_width() for line in wrapped_desc])

        number_lines = []
        tmp_font = small_font_reduced if reduced else small_font
        current_width = 0
        row = []

        for d in numbers:
            label = d.label
            value = f"{int(d.value * 100)}%" if d.data_type == "percent" else str(d.value)
            if label.lower() == "temperature":
                value += " degrees"
            text = f"{label}: {value}"
            text_width = tmp_font.size(text)[0]
            if current_width + text_width > wrap_width and row:
                number_lines.append(row)
                row = []
                current_width = 0
            row.append((label, value, d.color))
            current_width += text_width + 10
        if row:
            number_lines.append(row)

        bar_lines = [(d.label, min(max(d.value, 0), 1), d.color) for d in bars]
        for d in highlights:
            tmp_font = small_font_reduced if reduced else small_font
            line_widths.append(tmp_font.size(d.label)[0])

        # Highlight layout
        highlight_width = 60
        highlight_height = 30
        highlight_padding = 10
        highlight_rows = math.ceil(len(highlights) / self.columns)
        highlight_area_height = highlight_rows * (highlight_height + highlight_padding)

        number_height = len(number_lines) * (small_font.get_height() + 4)
        bar_height = len(bar_lines) * (small_font.get_height() + 4)

        content_max_width = max(line_widths + [title_width])
        if reduced:
            box_width = title_width + self.padding * 2
        else:
            box_width = max(content_max_width, self.columns * (highlight_width + highlight_padding)) + self.padding * 2


        text_height = sum(line.get_height() for line in lines)
        box_height = (
            self.padding * 2 +
            text_height + (4 if lines and not reduced else 0) +
            highlight_area_height + (8 if highlights else 0) +
            number_height + (8 if number_lines else 0) +
            bar_height + (30 if bar_lines else 0)
        )

        # Clamp position so the window is always fully onscreen
        surf_w, surf_h = surface.get_width(), surface.get_height()
        clamped_x = max(0, min(pos[0], surf_w - box_width))
        clamped_y = max(0, min(pos[1], surf_h - box_height))
        box_rect = pygame.Rect(clamped_x, clamped_y, box_width, box_height)
        pygame.draw.rect(surface, bg_color, box_rect, border_radius=6)

        y = clamped_y + self.padding

        for line in lines:
            surface.blit(line, (clamped_x + self.padding, y))
            y += line.get_height()

        if lines and not reduced:
            y += 4
            pygame.draw.line(surface, (100, 100, 100), (clamped_x + self.padding, y), (clamped_x + box_width - self.padding, y))
            y += 4

        # Draw highlight entries (3 per row)
        for i, d in enumerate(highlights):
            col = i % self.columns
            row = i // self.columns
            x = clamped_x + self.padding + col * (highlight_width + highlight_padding)
            y_offset = y + row * (highlight_height + highlight_padding)

            if isinstance(d.anim_tile, AnimatedTile):
                d.anim_tile.update(0)  # you may pass dt if needed
                d.anim_tile.draw(surface, (x, y_offset), scale_to=(highlight_width, highlight_height))
            else:
                pygame.draw.rect(surface, d.color, (x, y_offset, highlight_width, highlight_height), border_radius=4)

        if highlights:
            y += highlight_area_height + 4
            pygame.draw.line(surface, (100, 100, 100), (clamped_x + self.padding, y), (clamped_x + box_width - self.padding, y))
            y += 4

        for row_data in number_lines:
            x = clamped_x + self.padding
            for label, value, color_val in row_data:
                line_text = f"{label}: {value}"
                text_surface = tmp_font.render(line_text, False, color_val)
                surface.blit(text_surface, (x, y))
                x += text_surface.get_width() + 10
            y += small_font.get_height() + 4

        if number_lines:
            y += 4
            pygame.draw.line(surface, (100, 100, 100), (clamped_x + self.padding, y), (clamped_x + box_width - self.padding, y))
            y += 6

        for i, (label, val, color_val) in enumerate(bar_lines):
            bar_w = int(box_width * 0.6)  # 60% width
            bar_h = 20
            bar_x = clamped_x + (box_width - bar_w) // 2  # Center horizontally
            bar_y = y + i * (bar_h + 14)

            # Bar background
            pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=6)

            # Bar fill
            fill_width = int(bar_w * val)
            pygame.draw.rect(surface, color_val, (bar_x, bar_y, fill_width, bar_h), border_radius=6)

            # Centered text inside bar
            bar_label_text = f"{label}: {int(val * 100)}%"
            bar_label = small_font.render(bar_label_text, False, (0, 0, 0))
            label_x = bar_x + (bar_w - bar_label.get_width()) // 2
            label_y = bar_y + (bar_h - bar_label.get_height()) // 2
            surface.blit(bar_label, (label_x, label_y))

        if bar_lines:
            y += len(bar_lines) * (bar_h + 14)
            pygame.draw.line(surface, (100, 100, 100), (clamped_x + self.padding, y), (clamped_x + box_width - self.padding, y))
            y += 4


    
    def update(self, dt):
        """
        Updates AnimatedTiles and live data from the source item.
        """
        data_to_update = self.reduced_data if self.mode == "reduced" else self.data

        for d in data_to_update:
            # Update animation if it's a highlight
            if d.data_type == "highlight" and isinstance(d.anim_tile, AnimatedTile):
                try:
                    d.anim_tile.update(dt)
                except Exception as e:
                    
                    pass

            # Live-update value from the source item if applicable
            lookup_label = getattr(d, "lookup_label", None)
            if self.source_item and lookup_label:
                # Support nested attributes (e.g., blade.material)
                value = self.source_item
                for part in lookup_label.split("."):
                    if isinstance(value, dict):
                        value = value.get(part, None)
                    else:
                        value = getattr(value, part, None)
                if value is not None:
                    if d.data_type == "percent":
                        d.value = round(float(value), 3)
                    elif d.data_type == "number":
                        d.value = round(float(value), 1)
                        # Special temperature color logic
                        if lookup_label.lower() == "temperature" and hasattr(self.source_item, "material"):
                            material = getattr(self.source_item, "material")
                            temp_range = get_temp_range(material)
                            d.color = get_temperature_color(d.value, temp_range)
                    elif d.data_type == "bar":
                        d.value = max(0.0, min(1.0, float(value)))
                        if lookup_label.lower() == "rarity":
                            d.color = (
                                int(255 * (1 - d.value)),
                                int(255 * d.value),
                                0
                            )
                        elif lookup_label.lower() == "quality":
                            d.color = (
                                int(255 * d.value),
                                0,
                                255
                            )
            else:
                if not lookup_label:
                    print(f"[HoverWindow] Missing lookup_label for HoverData: label={getattr(d, 'label', None)}, data_type={getattr(d, 'data_type', None)}")
                elif not self.source_item:
                    print("[HoverWindow] source_item is None, cannot update window!")



def create_tool_hover_info(name, description, data_list, reduced_list=None):
    return HoverInfo(
        title=name,
        description=description,
        data=data_list,
        reduced_data=reduced_list,
        mode="reduced"
    )

def create_bag_hover_info(name, full, total, mode="default"):
    return HoverInfo(
        title=name,
        description="",
        data=[
            HoverData("Slots used", full, "number"),
            HoverData("Capacity", total, "number"),
            HoverData("Free slots", total - full, "number")
        ],
        reduced_data=[
            HoverData(f"{full}/{total} slots used", data_type="number")
        ],
        mode=mode
    )