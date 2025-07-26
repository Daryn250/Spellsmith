from screens.main_menu import main_menu
class instanceManager:
    def __init__(self, screen, settings):
        self.version = "pre-alpha 0.1.1"
        self.screen = screen
        self.settings = settings
        self.save_file = "saves/save1.json" # change to be the location of the save file
        self.settings.save_file = self.save_file
        self.settings.instance_manager = self
        self.settings.load()

        # set the weather and time initially, will be changed later if there's a weather save in the save file
        self.weather = {"type":None, "intensity":0, "time":0, "moon":0}

        main_menu(screen, self)