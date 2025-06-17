class GUIManager:
    def __init__(self):
        self.elements = []

    def update(self, dt, mouse_pos):
        for element in self.elements:
            element.update(dt, mouse_pos)

    def draw(self, surface):
        for element in self.elements:
            element.draw(surface)
