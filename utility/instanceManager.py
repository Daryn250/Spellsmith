from screens.main_menu import main_menu
from utility.audio_utility.sfxManager import SoundManager
from utility.shaderManager import ShaderManager
import numpy as np
class instanceManager:
    def __init__(self, screen, settings, context):
        self.version = "pre-alpha 0.1.1"
        self.screen = screen
        self.settings = settings
        self.save_file = "saves/save1.json" # change to be the location of the save file
        self.settings.save_file = self.save_file
        self.settings.instance_manager = self
        self.settings.load()
        self.ctx = context
        s = self.settings
        self.sfx_manager = SoundManager("audio", s.sfx_volume/100, s.music_volume/100, s.ambience_volume/100, s.npc_volume/100)



        # set the weather and time initially, will be changed later if there's a weather save in the save file
        self.weather = {"type":None, "intensity":0, "time":0, "moon":0}



        # Shader manager. this is a nightmare on earth
        self.shader_manager = ShaderManager(ctx=self.ctx, initial_size=screen.get_size())
        self.shader_manager.add_shader("bloom",
                                       "assets/shaders/_default.vert",
                                       "assets/shaders/bloom.frag")
        self.global_shaders = ["bloom"]

        

        main_menu(screen, self)
    
    def is_daytime(self):
        return True # dont worry bout it rn :D