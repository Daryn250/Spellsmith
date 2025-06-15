import pygame
import sys
from utility.animated_sprite import AnimatedTile
from utility.screenwrapper import VirtualScreen
from utility.button import Button
from utility.cursor import Cursor
from utility.screenswitcher import ScreenSwitcher

# screens
from screens.table import table

VIRTUAL_SIZE = (480, 270)
vscreen = VirtualScreen(VIRTUAL_SIZE)
cursor = Cursor(vscreen, "assets/cursor")
tile_size = 32
FPS = 60



def main_screen(screen):
    switcher = ScreenSwitcher()
    clock = pygame.time.Clock()

    virtual_surface = vscreen.get_surface()
    screenWidth, screenHeight = VIRTUAL_SIZE
    # Load tiles and sprite
    bg_tile = AnimatedTile("assets/ocean", frame_duration=150)
    boat_sprite = AnimatedTile("assets/boat", frame_duration=100)
    sprite_img = boat_sprite.get_current_frame()
    center_rect = sprite_img.get_rect(center=(screenWidth // 2, screenHeight // 2))

    while True:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse click
                    cursor.click()
                    # Check for input on buttons:
                    if PLAYBUTTON.checkForInput(vscreen.get_virtual_mouse(screen.get_size())):
                        switcher.start(lambda: table(screen))
                    if SETTINGSBUTTON.checkForInput(vscreen.get_virtual_mouse(screen.get_size())):
                        pass
                    if QUITBUTTON.checkForInput(vscreen.get_virtual_mouse(screen.get_size())):
                        pygame.quit()
                        sys.exit()

        # Update animation
        bg_tile.update(dt)
        boat_sprite.update(dt)
        cursor.update(dt)

        # Draw to virtual surface
        virtual_surface.fill((0, 0, 0))  # Clear

        for y in range(0, screenHeight, tile_size): # virtual width and height
            for x in range(0, screenWidth, tile_size):
                bg_tile.draw(virtual_surface, (x,y))

        # Update center sprite

        center_rect = sprite_img.get_rect(center=(screenWidth // 2, screenHeight // 2))

        boat_sprite.draw(virtual_surface, center_rect)


        # make and blit the menu bar to the screen
        menu_bar_surface = pygame.Surface((screenWidth, screenHeight), pygame.SRCALPHA)

        menu_bar = pygame.draw.rect(menu_bar_surface, (0, 0, 0, 128), (screenWidth // 20, 0, 100, screenHeight))

        # black menu bar
        virtual_surface.blit(menu_bar_surface, (0, 0))

        # buttons :3
        PLAYBUTTON = Button(None, (menu_bar.center[0],screenHeight*(2/5)), "play", pygame.font.Font(None, 32), "White", "gray")
        SETTINGSBUTTON = Button(None, (menu_bar.center[0],screenHeight//2), "settings", pygame.font.Font(None, 32), "White", "gray")
        QUITBUTTON = Button(None, (menu_bar.center[0],screenHeight-(screenHeight*.1)), "quit", pygame.font.Font(None, 32), "White", "indianred1")
        
        virtual_mouse = vscreen.get_virtual_mouse(screen.get_size())

        PLAYBUTTON.changeColor(virtual_mouse)
        PLAYBUTTON.update(vscreen.surface)

        SETTINGSBUTTON.changeColor(virtual_mouse)
        SETTINGSBUTTON.update(vscreen.surface)

        QUITBUTTON.changeColor(virtual_mouse)
        QUITBUTTON.update(vscreen.surface)

        virtual_mouse = vscreen.get_virtual_mouse(screen.get_size())

        cursor.draw(virtual_surface)
        # Offset if needed (optional: use top-left instead of center)

        # Scale to fit screen
        

        vscreen.draw_to_screen(screen)
        switcher.update_and_draw(screen)

        pygame.display.flip()

