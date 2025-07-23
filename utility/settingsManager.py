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

    def translated_text(self, text, lowercase = True):
        # Build the path to the language file
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