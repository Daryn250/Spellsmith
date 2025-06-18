class GUIManager:
    def __init__(self):
        self.windows = []

    def draw(self, screen):
        for window in self.windows:
            if hasattr(window, "update_position"):
                window.update_position()
            window.draw(screen)
