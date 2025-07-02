import pygame
from utility.cursor_utility.cursor import *

class CursorManager:
    def __init__(self, screen):
        self.current_cursor = BaseCursor(screen, "assets/cursor/defaultCursor")

    def set_cursor(self, cursor, screen, filepath):
        if type(cursor) == str:
            if cursor == "tongs":
                self.current_cursor = TongsCursor(screen, filepath)
            elif cursor == "base":
                self.current_cursor = BaseCursor(screen, filepath)
            elif cursor == "hammer":
                self.current_cursor = HammerCursor(screen, filepath)
        else:
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
