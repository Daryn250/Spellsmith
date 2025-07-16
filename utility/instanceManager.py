from screens.main_menu import main_menu
class instanceManager:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.save_file = None # change to be the location of the save file
        main_menu(screen, self)