import pygame
import os
from utility.particle import Particle

class Cursor:
    def __init__(self, virtual_screen, cursor_root=None):
        self.virtual_screen = virtual_screen
        self.cursor_root = cursor_root
        self.visible = True
        self._pending_hide = True
        self._initialized = False
        self.idle_frames = []
        self.click_frames = []
        self.current_frames = []
        self.current_frame_index = 0
        self.animation_timer = 0
        self.frame_delay = 50  # ms
        self.clicking = False
        self.finished_click_animation = False
        self.mouse_held = False
        self.particles = []
        
    def _try_initialize(self):
        if self._initialized:
            return

        if pygame.display.get_surface() is not None:
            pygame.mouse.set_visible(False)  # Prevent flashing default

            if self.cursor_root and not self.idle_frames:
                self.load_animations(self.cursor_root)
            
            if not self.idle_frames:
                print("Cursor: idle_frames missing, using fallback.")
                self.idle_frames = [self._create_fallback_frame()]

            if not self.click_frames:
                print("Cursor: click_frames missing, using fallback.")
                self.click_frames = self.idle_frames

            self.current_frames = self.idle_frames
            self.current_frame_index = 0

            self._initialized = True

    def load_animations(self, folder):
        idle_path = os.path.join(folder, "default")
        click_path = os.path.join(folder, "click_anim")
        self.idle_frames = self._load_frames(idle_path)
        self.click_frames = self._load_frames(click_path)
        self.current_frames = self.idle_frames or [self._create_fallback_frame()]

    def _load_frames(self, folder):
        frames = []
        if not os.path.exists(folder):
            print(f"Cursor Warning: folder {folder} does not exist.")
            return frames

        for filename in sorted(os.listdir(folder)):
            if filename.lower().endswith((".png", ".jpg", ".bmp")):
                path = os.path.join(folder, filename)
                try:
                    img = pygame.image.load(path).convert_alpha()
                    frames.append(img)
                except Exception as e:
                    print(f"Error loading frame {path}: {e}")
        return frames

    def _create_fallback_frame(self):
        surf = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.line(surf, (255, 0, 0), (0, 0), (15, 15), 2)
        pygame.draw.line(surf, (255, 0, 0), (15, 0), (0, 15), 2)
        return surf

    def get_cursor_tip_position(self):
        """Returns bottom-left corner of the hammer in virtual coordinates. for particles."""
        if not self._initialized:
            return 0, 0  # fallback

        window_size = pygame.display.get_surface().get_size()
        mouse_x, mouse_y = self.virtual_screen.get_virtual_mouse(window_size)

        
        # Use current frame to get cursor size
        frame = self.click_frames[self.current_frame_index] if self.clicking else self.idle_frames[self.current_frame_index]
        width, height = frame.get_width(), frame.get_height()

        hammer_x = mouse_x - width // 2
        hammer_y = mouse_y + height // 2  # bottom edge

        return hammer_x, hammer_y

    def update(self, dt):
        self._try_initialize()
        if not self._initialized:
            return

        # Update mouse held state
        self.mouse_held = pygame.mouse.get_pressed()[0]

        # Get the current animation set
        if self.clicking:
            frames = self.click_frames
        else:
            frames = self.idle_frames

        if not frames:
            return

        self.animation_timer += dt
        if self.animation_timer >= self.frame_delay:
            self.animation_timer = 0
            if self.clicking:
                if self.current_frame_index < len(frames) - 1:
                    self.current_frame_index += 1
                else:
                    if not self.animation_done:
                        self.animation_done = True

                        # get the hammer position
                        hammer_x, hammer_y = self.get_cursor_tip_position() # bottom left
                        # try to get color
                        try:
                            color = self.virtual_screen.surface.get_at((hammer_x, hammer_y))[:3]
                        except:
                            color = (255, 255, 255)  # fallback color

                        for _ in range(4):  # Spawn 10 particles
                            self.particles.append(Particle((hammer_x, hammer_y), color, lifetime=30))

                        if hasattr(self.virtual_screen, "start_shake"):
                            self.virtual_screen.start_shake(duration=10, magnitude=6)

                        # play sounds here for click
                    if not self.mouse_held:
                        self.clicking = False
                        self.animation_done = False
                        self.current_frame_index = 0

            else:
                # Idle loop
                self.current_frame_index = (self.current_frame_index + 1) % len(frames)
        
        # particle logic for hammer cursor
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)

    def click(self):
        if not self._initialized:
            return
        if self.clicking:
            return  # don't restart mid-animation

        self.clicking = True
        self.animation_done = False
        self.current_frame_index = 0
        self.animation_timer = 0

    def draw(self, surface):
        self._try_initialize()

        if not self._initialized:
            return

        mouse_pos = self.virtual_screen.get_virtual_mouse(pygame.display.get_window_size())

        # Determine which animation frames to use
        frames = self.click_frames if self.clicking and self.click_frames else self.idle_frames

        # Safety: prevent crash if frames are still empty
        if not frames:
            return

        # Clamp index
        if self.current_frame_index >= len(frames):
            self.current_frame_index = len(frames) - 1

        for particle in self.particles:
            particle.draw(surface)

        current = frames[self.current_frame_index]
        surface.blit(current, (
            mouse_pos[0] - current.get_width() // 2,
            mouse_pos[1] - current.get_height() // 2
        ))


