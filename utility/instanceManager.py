from screens.main_menu import main_menu
class instanceManager:
    def __init__(self, screen, settings):
        self.version = "pre-alpha 0.1.1"
        self.screen = screen
        self.settings = settings
        self.save_file = "saves/save1.json" # change to be the location of the save file
        main_menu(screen, self)