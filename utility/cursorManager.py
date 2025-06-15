import pygame
from utility.cursor import HammerCursor
from utility.cursor import BaseCursor

class CursorManager:
    def __init__(self, screen):
        self.current_cursor = BaseCursor(screen, "assets/cursor/defaultCursor")

    def set_cursor(self, cursor):
        self.current_cursor = cursor

    def update(self, dt, mouse):
        if self.current_cursor:
            self.current_cursor.update(dt, mouse)

    def draw(self, surface, mouse):
        if self.current_cursor:
            self.current_cursor.draw(surface, mouse)

    def click(self):
        if self.current_cursor:
            self.current_cursor.click()
