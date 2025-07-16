import pygame

class ResultEntry:
    def __init__(self, game_name, grade, start_center, target_pos, delay, screen):
        self.text = f"{game_name}: {grade}"
        self.start_center = start_center
        self.current_pos = list(start_center)
        self.target_pos = target_pos
        self.scale = 2.5
        self.alpha = 0
        self.timer = 0
        self.delay = delay
        self.arrived = False
        self.font = screen.instance_manager.settings.font

    def update(self, dt):
        self.timer += dt
        if self.timer < self.delay:
            return

        t = min((self.timer - self.delay) / 600, 1.0)
        # Elastic easing out
        for i in range(2):
            self.current_pos[i] += (self.target_pos[i] - self.current_pos[i]) * 0.15

        self.alpha = min(255, self.alpha + dt * 0.8)
        self.scale += (1.0 - self.scale) * 0.1

        if not self.arrived and abs(self.current_pos[0] - self.target_pos[0]) < 1 and abs(self.current_pos[1] - self.target_pos[1]) < 1:
            self.arrived = True


class ResultsMinigame:
    def __init__(self, clip_rect, result_log, on_finish=None):
        self.clip_rect = clip_rect
        self.result_log = [r for r in result_log if r.get("game_name")]
        self.entries = []
        self.final_grade = None
        self.final_grade_pos = None
        self.final_grade_anim_pos = list(clip_rect.center)
        self.final_alpha = 0
        self.final_delay = 1000  # ms after all results appear
        self.final_timer = 0
        self.finished = False
        self.grade_animation_done = False

        self.on_finish = on_finish
        self._initialize()

    def _initialize(self):
        positions = self._layout_grid(len(self.result_log))
        delay_step = 400
        center = self.clip_rect.center

        score_map = {"perfect": 3, "good": 2, "ok": 1, "miss": 0}
        self.total_score = 0
        self.max_score = 0

        for i, (result, target_pos) in enumerate(zip(self.result_log, positions)):
            hits = result["hits"]
            score = sum(score_map.get(hit.lower(), 0) for hit in hits)
            max_score = len(hits) * 3
            self.total_score += score
            self.max_score += max_score
            ratio = score / max_score if max_score else 0

            grade = self._letter_grade(ratio)
            self.entries.append(ResultEntry(result["game_name"], grade, center, target_pos, i * delay_step))

    def _layout_grid(self, count, margin=100):
        max_rows = 4
        row_height = 40
        col_width = 220
        cols = (count - 1) // max_rows + 1
        positions = []

        for i in range(count):
            col = i // max_rows
            row = i % max_rows
            x = self.clip_rect.left + margin + col * col_width
            y_offset = 8  # 👈 custom vertical offset
            y = self.clip_rect.top + y_offset + row * row_height

            positions.append((x, y))
        return positions

    def update(self, dt, _):
        if self.finished:
            return

        all_arrived = True
        for entry in self.entries:
            entry.update(dt)
            if not entry.arrived:
                all_arrived = False

        if all_arrived:
            self.final_timer += dt
            if self.final_timer >= self.final_delay and not self.final_grade:
                self.ratioFinal = self.total_score / self.max_score if self.max_score else 0
                grade = self._letter_grade(self.ratioFinal)
                self.final_grade = grade

                box_margin = 10
                self.final_grade_pos = (
                    self.clip_rect.right - box_margin - 40,
                    self.clip_rect.top + box_margin + 40
                )

            if self.final_grade:
                for i in range(2):
                    self.final_grade_anim_pos[i] += (self.final_grade_pos[i] - self.final_grade_anim_pos[i]) * 0.1
                self.final_alpha = min(255, self.final_alpha + dt * 0.5)

                if abs(self.final_grade_anim_pos[0] - self.final_grade_pos[0]) < 1 and abs(self.final_grade_anim_pos[1] - self.final_grade_pos[1]) < 1:
                    self.grade_animation_done = True

                    if self.on_finish:
                        self.on_finish()

    def draw(self, surface, clip):
        prev_clip = surface.get_clip()
        surface.set_clip(clip)  # Use the passed-in clip, not self.clip_rect

        font = pygame.font.Font(self.font, 24)
        for entry in self.entries:
            text_surf = font.render(entry.text, False, (255, 255, 255))
            text_surf.set_alpha(min(255, int(entry.alpha)))
            scaled = pygame.transform.scale(
                text_surf,
                (int(text_surf.get_width() * entry.scale), int(text_surf.get_height() * entry.scale))
            )
            rect = scaled.get_rect(center=(int(entry.current_pos[0]), int(entry.current_pos[1])))
            surface.blit(scaled, rect)

        if self.final_grade:
            font_big = pygame.font.Font(self.font, 48)
            grade_text = font_big.render(self.final_grade, False, (255, 255, 100))
            grade_text.set_alpha(min(255, int(self.final_alpha)))
            rect = grade_text.get_rect(center=self.final_grade_anim_pos)
            surface.blit(grade_text, rect)

            # Draw grade box
            margin = 10
            box_rect = pygame.Rect(
                clip.right - 80 - margin,  # <- use `clip`, not self.clip_rect
                clip.top + margin,
                80, 80
            )
            pygame.draw.rect(surface, (255, 255, 255), box_rect, width=2)

            if self.grade_animation_done:
                prompt_font = pygame.font.Font(self.font, 20)
                prompt_text = prompt_font.render("Click to continue...", False, (255, 255, 255))
                prompt_rect = prompt_text.get_rect(center=(clip.centerx, clip.bottom - 20))
                surface.blit(prompt_text, prompt_rect)

        surface.set_clip(prev_clip)



    def handle_event(self, event, mouse_pos):
        if self.grade_animation_done and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.finished = True
            if self.on_finish:
                self.on_finish()


    def is_finished(self):
        return self.finished

    def _letter_grade(self, ratio):
        if ratio >= 1.5:
            return "U++"
        elif ratio >= 1.4:
            return "U+"
        elif ratio >= 1.3:
            return "U"
        elif ratio >= 1.2:
            return "S+++"
        elif ratio >= 1.1:
            return "S++"
        elif ratio >= 1:
            return "S+"
        elif ratio >= 0.95:
            return "S"
        elif ratio >= 0.9:
            return "A"
        elif ratio >= 0.8:
            return "B"
        elif ratio >= 0.7:
            return "C"
        elif ratio >= 0.6:
            return "D"
        else:
            return "F"
