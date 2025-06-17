class Charm:
    def __init__(self, charmItem):
        self.item = charmItem
        self._was_hovered_last_frame = False
        self.is_hovered = False  # explicitly store this for external use

    @property
    def pos(self):
        return self.item.pos

    @property
    def type(self):
        return self.item.type

    def update(self, dt, mouse_pos):
        mx, my = mouse_pos
        rect = self.item.image.get_rect(topleft=self.item.pos)
        self.is_hovered = rect.collidepoint(mx, my)

        if hasattr(self.item, "update"):
            self.item.update(dt)

    def draw(self, surface):
        self.item.draw(surface)
