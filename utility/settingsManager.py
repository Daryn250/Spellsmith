# saves settings
class settingsManager:
    def __init__(self):
        self.font = "assets\hydrophilia.iced-regular.ttf"
        self.language = "english"
        self.font_hover_size = 15
        self.gui_size = 12
        self.input_type = "mouse"
        self.discovered_islands = ["island1", "island2"]

        # maybe save and load these variables, they are important lol