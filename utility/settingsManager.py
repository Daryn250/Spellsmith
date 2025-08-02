import os
import json
import pygame

class settingsManager:
    def __init__(self):
        self.font = "assets\\hydrophilia.iced-regular.ttf" # default font
        self.language = "english"
        self.font_hover_size = 15
        self.gui_size = 12
        self.input_type = "mouse"
        self.discovered_islands = ["island1", "island2"]
        self.save_file = None
        self.instance_manager = None # insert from instance manager
        self.settings_path = os.path.join("saves", "settings.json")
        self.sfx_volume = 0.5
        self.music_volume = 0.5
        self.ambience_volume = 0.5
        self.npc_volume = 0.5

        self.shader = ""

    def save(self):
        
        data = {
            "font": self.font,
            "language": self.language,
            "font_hover_size": self.font_hover_size,
            "gui_size": self.gui_size,
            "input_type": self.input_type,
            "save_file": self.save_file,
            "sfx_volume": self.sfx_volume,
            "music_volume": self.music_volume,
            "ambience_volume": self.ambience_volume,
            "npc_volume": self.npc_volume,
            "shader": self.shader
        }
        os.makedirs(os.path.dirname(self.settings_path), exist_ok=True)
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self):
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.font = data.get("font", self.font)
                self.language = data.get("language", self.language)
                self.font_hover_size = data.get("font_hover_size", self.font_hover_size)
                self.gui_size = data.get("gui_size", self.gui_size)
                self.input_type = data.get("input_type", self.input_type)
                self.save_file = data.get("save_file", "saves/save1.json")
                self.sfx_volume = data.get("sfx_volume", self.sfx_volume)
                self.music_volume = data.get("music_volume", self.music_volume)
                self.ambience_volume = data.get("ambience_volume", self.ambience_volume)
                self.npc_volume = data.get("npc_volume", self.npc_volume)
                if self.instance_manager !=None:
                    self.instance_manager.save_file = self.save_file
            except Exception as e:
                print(f"[settingsManager] Error loading settings: {e}")
        if not os.path.exists(self.font):
            self.font = "freesansbold.ttf" #pygame will change this to freesans bold, allowing the user to still exist somehow

    def translated_text(self, text, lowercase = True):
        # Build the path to the language file
        if text == None:
            return
        text = text.lower() if lowercase else text
        lang_file = os.path.join("assets", "translations", f"{self.language}.json")
        if not os.path.exists(lang_file):
            return text
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Look for the "other" section
            other = data.get("other", {})
            return other.get(text, text)

        except Exception as e:
            print(f"[settingsManager] Error loading language file: {e}")
            return text