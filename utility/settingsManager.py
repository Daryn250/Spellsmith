import os
import json

class settingsManager:
    def __init__(self):
        self.font = "assets\\hydrophilia.iced-regular.ttf"
        self.language = "english"
        self.font_hover_size = 15
        self.gui_size = 12
        self.input_type = "mouse"
        self.discovered_islands = ["island1", "island2"]
        self.settings_path = os.path.join("saves", "settings.json")
        self.load()

    def save(self):
        data = {
            "font": self.font,
            "language": self.language,
            "font_hover_size": self.font_hover_size,
            "gui_size": self.gui_size,
            "input_type": self.input_type
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
            except Exception as e:
                print(f"[settingsManager] Error loading settings: {e}")

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