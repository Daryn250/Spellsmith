import pygame

class HoverInfo:
    def __init__(self, mode="reduced", title="", lines=None, icon=None):
        """
        :param mode: 'reduced', 'full', or 'tool'
        :param title: Title/header for the tooltip
        :param lines: List of strings to render as information
        :param icon: Optional pygame.Surface to show to the left of the text
        """
        self.mode = mode
        self.title = title
        self.lines = lines if lines else []
        self.icon = icon

    def draw(self, surface, pos, font, color=(255, 255, 255), padding=5, bg_color=(0, 0, 0, 180)):
        max_width = 0
        rendered_lines = []

        title_surf = font.render(self.title, True, color)
        rendered_lines.append(title_surf)
        max_width = title_surf.get_width()

        for line in self.lines:
            text_surf = font.render(line, True, color)
            rendered_lines.append(text_surf)
            max_width = max(max_width, text_surf.get_width())

        total_height = sum(surf.get_height() for surf in rendered_lines) + padding * 2
        icon_width = self.icon.get_width() if self.icon else 0
        total_width = max_width + padding * 2 + icon_width

        # Draw background box
        box_rect = pygame.Rect(pos[0], pos[1], total_width, total_height)
        bg_surface = pygame.Surface(box_rect.size, pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        surface.blit(bg_surface, box_rect.topleft)

        # Draw icon
        x_offset = padding
        if self.icon:
            surface.blit(self.icon, (pos[0] + padding, pos[1] + padding))
            x_offset += self.icon.get_width() + padding

        # Draw text lines
        y = pos[1] + padding
        for surf in rendered_lines:
            surface.blit(surf, (pos[0] + x_offset, y))
            y += surf.get_height()

def create_bag_hover_info(name, full, total, mode="reduced"):
    if mode == "reduced":
        return HoverInfo(
            mode="reduced",
            title=name,
            lines=[f"{full}/{total} slots used"]
        )
    elif mode == "full":
        return HoverInfo(
            mode="full",
            title=name,
            lines=[
                f"Slots used: {full}",
                f"Capacity: {total}",
                f"Free slots: {total - full}"
            ]
        )
    else:
        return HoverInfo(title="Bag", lines=["Unknown mode"])
        

def create_tool_hover_info(tool_name, stats_dict):
    return HoverInfo(
        mode="tool",
        title=tool_name,
        lines=[f"{key}: {value}" for key, value in stats_dict.items()]
    )
