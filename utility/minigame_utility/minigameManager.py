import random
import pygame
from utility.minigame_utility.hammer_game import HammerMiniGame
from utility.minigame_utility.countdown import CountdownMiniGame
from utility.minigame_utility.selector import WeaponSelector
from utility.minigame_utility.heattreatminigame import HeatTreatMinigame
from utility.minigame_utility.quenchMinigame import QuenchMinigame
from utility.minigame_utility.SliderMinigame import SliderMinigame

from utility.tool_utility.temperatureHandler import get_temp_range

class MiniGameManager:
    def __init__(self, virtual_size, helper):
        self.item = None
        self.current_game = None
        self.game_queue = []
        self.result_log = []
        self.finished = False

        self.base_screen = helper.base_screen

        self.selector = WeaponSelector(virtual_size, helper.item_in_slot)
        self.anvil_item = helper.item_in_slot
        self.in_selector = True

        self.virtual_size = virtual_size
        self.minigame_top_left = (4 * (virtual_size[0] / 160), 39 * (virtual_size[1] / 90))
        self.minigame_bottom_right = (155 * (virtual_size[0] / 160), 86 * (virtual_size[1] / 90))
        self.minigame_width = self.minigame_bottom_right[0] - self.minigame_top_left[0]
        self.minigame_height = self.minigame_bottom_right[1] - self.minigame_top_left[1]

    def _setup_games_for_item(self, item):

        self.game_queue.append(CountdownMiniGame(self.virtual_size, item = self.selector.get_selected_type()))

        material = getattr(self.anvil_item, "material", "unexplicible error with material please consult the minigame manager")
        temp = getattr(self.anvil_item, "temperature", "how you do this")
        max_temp = get_temp_range(material).get("max")
        rarity = item.get("rarity")
        key = item.get("key")
        part = item.get("part")
        mass = item.get("mass")

        rarity_map = {
            "common": 0.1, "uncommon": 0.2, "rare": 0.4, "rare+": 0.5,
            "unique": 0.6, "elite": 0.7, "legendary": 0.85, "mythic": 0.95, "fabled": 1.0
        }
        rarity_scale = rarity_map.get(item.get("rarity", "common"), 0.1)

        difficulty = round(((max_temp+1)/temp)+(mass/2)+(rarity_scale*10))

        if part == "pommel":
            self.game_queue.append(HammerMiniGame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(SliderMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(HeatTreatMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(QuenchMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
        
        if part == "guard":
            self.game_queue.append(HammerMiniGame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(SliderMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(HeatTreatMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(QuenchMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
        
        if part == "blade":
            self.game_queue.append(HammerMiniGame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(SliderMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(HeatTreatMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))
            self.game_queue.append(QuenchMinigame(self.virtual_size, difficulty, self.clip, self.base_screen))




        

        self._next_game()



    def _next_game(self):
        if self.game_queue:
            self.current_game = self.game_queue.pop(0)
        else:
            self.current_game = None
            self.finished = True

    def update(self, dt, virtual_mouse):
        if self.finished:
            return

        if self.in_selector:
            self.selector.update(dt, virtual_mouse)
            return

        if self.current_game:
            self.current_game.update(dt, virtual_mouse)
            if self.current_game.finished:
                result = self.current_game.get_result()
                self.result_log.append(result)
                self._next_game()

    def draw(self, surface):
        clip_rect = pygame.Rect(
            self.minigame_top_left[0], self.minigame_top_left[1],
            self.minigame_width, self.minigame_height
        )
        self.clip = clip_rect

        prev_clip = surface.get_clip()
        surface.set_clip(clip_rect)

        if self.in_selector:
            self.selector.draw(surface, clip_rect)  # ✅ Pass clip_rect here
        elif self.current_game:
            self.current_game.draw(surface, clip_rect)

        surface.set_clip(prev_clip)


    def handle_event(self, event, mouse_pos):
        if self.in_selector:
            self.selector.handle_event(event, mouse_pos)

            if self.selector.finished:
                selected_type = self.selector.get_selected_type()
                print(selected_type)
                self._setup_games_for_item(selected_type)
                self.in_selector = False
            return

        if self.current_game:
            self.current_game.handle_event(event, mouse_pos)

    def get_final_score(self):
        if not self.finished:
            return None

        score_map = {"perfect": 3, "good": 2, "ok": 1, "miss": 0}

        total = 0
        max_score = 0
        for result in self.result_log:
            for hit in result.get("hits", []):
                total += score_map.get(hit, 0)
                max_score += 3

        ratio = total / max_score if max_score else 0
        print(ratio)
        if ratio >= 0.9:
            return "perfect"
        elif ratio >= 0.7:
            return "good"
        elif ratio >= 0.5:
            return "ok"
        else:
            return "bad"

