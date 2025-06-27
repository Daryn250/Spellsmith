import pygame
from utility.particle import make_particles_presets



def lerp(a, b, t):
    return a + (b - a) * t


class TrickAnimation:
    def __init__(self, keyframes, on_complete=None):
        """
        keyframes: list of dicts, each with:
            - time: float (seconds)
            - pos_offset: (x, y) tuple (optional)
            - rot_offset: float (optional)
            - scale: (sx, sy) tuple (optional)
            - event: string or callable (optional)
            - callback: function(item) (optional)
        on_complete: optional callback when done
        """
        self.keyframes = sorted(keyframes, key=lambda f: f["time"])
        self.time = 0.0
        self.index = 0
        self.finished = False
        self.on_complete = on_complete
        self.prev_frame = None

    def update(self, dt, item, VIRTUAL_SIZE):
        if self.finished:
            return

        self.time += dt

        # Ensure we have a valid pair of keyframes
        if self.index >= len(self.keyframes) - 1:
            self.finished = True
            if self.on_complete:
                self.on_complete(item)
            return

        prev = self.keyframes[self.index]
        next_ = self.keyframes[self.index + 1]

        t0 = prev["time"]
        t1 = next_["time"]
        local_t = (self.time - t0) / (t1 - t0) if t1 > t0 else 0
        local_t = max(0.0, min(1.0, local_t))  # Clamp just in case


        # Interpolate rotation
        if "rot_offset" in prev and "rot_offset" in next_:
            item.rotation = lerp(prev["rot_offset"], next_["rot_offset"], local_t)

        # Interpolate scale
        if "scale" in prev and "scale" in next_:
            sx0, sy0 = prev["scale"]
            sx1, sy1 = next_["scale"]
            if hasattr(item, "squish"):
                item.squish = [lerp(sx0, sx1, local_t), lerp(sy0, sy1, local_t)]
            elif hasattr(item, "scale"):
                item.scale = [lerp(sx0, sx1, local_t), lerp(sy0, sy1, local_t)]

        # Interpolate position
        if "pos_offset" in prev and "pos_offset" in next_:
            px0, py0 = prev["pos_offset"]
            px1, py1 = next_["pos_offset"]
            interp_x = lerp(px0, px1, local_t)
            interp_y = lerp(py0, py1, local_t)

            sx = (VIRTUAL_SIZE[0] / 480)
            sy = (VIRTUAL_SIZE[1] / 270)

            item.pos = (
                item.original_pos[0] + interp_x * sx,
                item.original_pos[1] + interp_y * sy
            )

        # Trigger particles or events at the right time
        if "particles" in next_ and self.time >= t1:
            preset_name = next_["particles"]
            if preset_name in make_particles_presets:
                new_particles = make_particles_presets[preset_name](item.pos, count=6)
                item.particles.extend(new_particles)

        if "event" in next_ and self.time >= t1:
            if callable(next_["event"]):
                next_["event"](item)
            else:
                print(f"[TrickEvent] {next_['event']}")

        if "callback" in next_ and self.time >= t1:
            next_["callback"](item)

        # Advance index if needed
        if self.time >= t1:
            self.index += 1
            if self.index >= len(self.keyframes) - 1:
                self.finished = True
                if self.on_complete:
                    self.on_complete(item)




    def reset(self):
        self.time = 0.0
        self.index = 0
        self.finished = False
        self.prev_frame = None

# Example usage:
kickflip = [
    {"time": 0.0, "rot_offset": 0, "pos_offset": (0, 0), "scale": (1.0, 1.0)},
    {"time": 0.5, "rot_offset": -25, "pos_offset": (0, 0), "scale": (1, 1.0)},  # squished horizontally
    {"time": 1, "rot_offset": -55, "pos_offset": (0, 0), "scale": (1.0, 1.0)},   # flipped horizontally
    {"time": 1.5, "rot_offset": 1, "pos_offset": (0, 80), "scale": (1.0, 1.0)},
    {"time": 2, "event": "landed"},
]

