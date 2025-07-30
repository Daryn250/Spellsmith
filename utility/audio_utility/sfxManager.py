import pygame
import os
import random
import re

class SoundManager:
    def __init__(
        self,
        audio_folder="audio",
        sfx_volume=1.0,
        music_volume=0.7,
        ambience_volume=0.5,
        npc_volume=0.8
    ):
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

        self.sfx_folder = os.path.join("assets", audio_folder, "sfx")
        self.music_folder = os.path.join("assets", audio_folder, "music")
        self.sounds = {}  # Optional: preload cache

        self.fadeout_time = 0
        self.fadein_time = 0

        pygame.mixer.set_num_channels(32)
        self.channels = {
            "sfx": pygame.mixer.Channel(0),
            "ambience": pygame.mixer.Channel(1),
            "npc": pygame.mixer.Channel(2),
        }

        self.channels["sfx"].set_volume(sfx_volume)
        self.channels["ambience"].set_volume(ambience_volume)
        self.channels["npc"].set_volume(npc_volume)
        pygame.mixer.music.set_volume(music_volume)

    def update_volume(self, sfx, music, ambience, npc):
        self.channels["sfx"].set_volume(sfx)
        self.channels["ambience"].set_volume(ambience)
        self.channels["npc"].set_volume(npc)
        pygame.mixer.music.set_volume(music)

    def set_channel_volume(self, channel_name, volume):
        if channel_name in self.channels:
            self.channels[channel_name].set_volume(volume)

    def _get_sound(self, sound_type, material):
        if "_" not in sound_type and material is None:
            print(f"Invalid sound_type format: {sound_type}")
            return None

        parts = sound_type.split("_")
        if len(parts) == 1:
            folder = base_name = parts[0]
        else:
            folder, *base_parts = parts
            base_name = "_".join(base_parts)

        folder_path = os.path.join(self.sfx_folder, folder)

        search_paths = []
        if material:
            search_paths.append(os.path.join(folder_path, material))
            search_paths.append(os.path.join(folder_path, "general"))
        search_paths.append(folder_path)

        for path in search_paths:
            if os.path.isdir(path):
                matches = self._find_matching_sounds(path, base_name)
                if matches:
                    return random.choice(matches)

        fallback = os.path.join(folder_path, f"{base_name}.wav")
        if os.path.isfile(fallback):
            try:
                return pygame.mixer.Sound(fallback)
            except Exception as e:
                print(f"Error loading fallback: {fallback}: {e}")

        print(f"No sound found for '{sound_type}' with material '{material}'")
        return None

    def _find_matching_sounds(self, folder_path, base_name):
        pattern = re.compile(rf"^{re.escape(base_name)}(\(|_)?\d+?\)?\.wav$", re.IGNORECASE)
        matches = []
        for fname in os.listdir(folder_path):
            if pattern.match(fname):
                try:
                    matches.append(pygame.mixer.Sound(os.path.join(folder_path, fname)))
                except Exception as e:
                    print(f"Error loading {fname}: {e}")
        return matches

    def play_sound(self, sound_type, material=None, fade_in_ms=None, loop=False, volume=1.0):
        sound = self._get_sound(sound_type, material)
        if not sound:
            return
        loops = -1 if loop else 0
        fade_ms = fade_in_ms if fade_in_ms is not None else self.fadein_time

        chan = pygame.mixer.find_channel()
        if chan:
            chan.set_volume(volume)
            chan.play(sound, loops=loops, fade_ms=fade_ms)
        else:
            print("No free channel for sound effect.")

    def loop_sound(self, sound_type, material=None, volume=1.0):
        self.play_sound(sound_type, material, loop=True, volume=volume)

    def play_ambience(self, sound_type, material=None, fade_in_ms=500, loop=True):
        sound = self._get_sound(sound_type, material)
        if not sound:
            return
        chan = self.channels["ambience"]
        if not chan.get_busy():
            chan.play(sound, loops=-1 if loop else 0, fade_ms=fade_in_ms)

    def stop_ambience(self, fade_out_ms=500):
        chan = self.channels["ambience"]
        if chan.get_busy():
            chan.fadeout(fade_out_ms)

    def play_npc_voice(self, sound_type, material=None, fade_in_ms=100, loop=False):
        sound = self._get_sound(sound_type, material)
        if not sound:
            return
        chan = self.channels["npc"]
        if chan.get_busy():
            chan.fadeout(self.fadeout_time)
        chan.play(sound, loops=-1 if loop else 0, fade_ms=fade_in_ms)

    def stop_npc_voice(self, fade_out_ms=300):
        chan = self.channels["npc"]
        if chan.get_busy():
            chan.fadeout(fade_out_ms)

    def play_music(self, filename, fade_in_ms=1000, loop=-1):
        path = os.path.join(self.music_folder, filename)
        if not pygame.mixer.music.get_busy():
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(loops=loop, fade_ms=fade_in_ms)
            except Exception as e:
                print(f"Music load/play error: {e}")

    def stop_music(self, fade_out_ms=1000):
        pygame.mixer.music.fadeout(fade_out_ms)

    def play_random_sound_folder(self, folder_path, volume=1.0):
        """Play a random .wav sound from any folder."""
        if not os.path.isdir(folder_path):
            print(f"Invalid folder path: {folder_path}")
            return
        candidates = [f for f in os.listdir(folder_path) if f.lower().endswith(".wav")]
        if not candidates:
            print(f"No .wav files in {folder_path}")
            return
        choice = random.choice(candidates)
        try:
            sound = pygame.mixer.Sound(os.path.join(folder_path, choice))
            chan = pygame.mixer.find_channel()
            if chan:
                chan.set_volume(volume)
                chan.play(sound)
        except Exception as e:
            print(f"Error playing sound from folder: {e}")

    def preload_sounds(self):
        """Optional method: load all .wav files into self.sounds for instant access."""
        for root, dirs, files in os.walk(self.sfx_folder):
            for fname in files:
                if fname.lower().endswith(".wav"):
                    fpath = os.path.join(root, fname)
                    try:
                        self.sounds[fpath] = pygame.mixer.Sound(fpath)
                    except Exception as e:
                        print(f"Failed to preload {fpath}: {e}")
