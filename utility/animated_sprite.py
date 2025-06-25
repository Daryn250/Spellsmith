import pygame
import os

class AnimatedTile:
    def __init__(self, folder_path, frame_duration=100, loop=True, error_image_path="assets/error.png"):
        self.error_frame = pygame.image.load(error_image_path).convert_alpha()
        self.frames = self._load_frames_from_folder(folder_path)
        if not self.frames:
            self.frames = [self.error_frame]

        self.index = 0
        self.frame_duration = frame_duration
        self.loop = loop
        self.timer = 0

    def _load_frames_from_folder(self, folder_path):
        supported = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        if folder_path.lower().endswith(supported):
            return [pygame.image.load(folder_path).convert_alpha()]
        else:
            files = sorted(f for f in os.listdir(folder_path) if f.lower().endswith(supported))
            frames = []

            for f in files:
                try:
                    full_path = os.path.join(folder_path, f)
                    img = pygame.image.load(full_path).convert_alpha()
                    frames.append(img)
                except Exception as e:
                    print(f"[AnimatedTile] Failed to load frame: {f} — {e}")
                    frames.append(self.error_frame)

            return frames

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.index += 1
            if self.index >= len(self.frames):
                if self.loop:
                    self.index = 0
                else:
                    self.index = len(self.frames) - 1

    def get_current_frame(self):
        return self.frames[self.index]

    def draw(self, surface, position, scale_to=None, blend=None):
        frame = self.get_current_frame()

        if scale_to:
            frame = pygame.transform.scale(frame, scale_to)

        surface.blit(frame, position, special_flags=blend if blend else 0)


