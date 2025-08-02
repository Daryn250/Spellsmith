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


        # Build your shared quad once:
        quad_verts = np.array([
            -1.0,  1.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
             1.0, -1.0, 1.0, 0.0,
        ], dtype='f4')
        self.shared_quad_vbo = self.ctx.buffer(quad_verts.tobytes())

        # Build your shader manager once:
        self.shader_manager = ShaderManager(ctx=self.ctx, initial_size=screen.get_size())
        self.shader_manager.add_shader("default",
                                       "assets/shaders/_default.vert",
                                       "assets/shaders/default.shader")
        self.shader_manager.add_shader("bloom",
                                       "assets/shaders/_default.vert",
                                       "assets/shaders/bloom.frag")
        self.shader_manager.add_shader("warp",
                                       "assets/shaders/_default.vert",
                                       "assets/shaders/warp.frag")
        self.shader_manager.set_active("bloom")

        # Pull out the *one* pair of textures for your active shader:
        active = self.shader_manager.active_name
        sh = self.shader_manager.shaders[active]
        # these live inside the Shader instance and are never reallocated:
        

        main_menu(screen, self)
    
    def is_daytime(self):
        return True # dont worry bout it rn :D