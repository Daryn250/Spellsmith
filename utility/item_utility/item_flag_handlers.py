import pygame
import random
from utility.item_utility.charmWindows import returnCharmWindow
from utility.particle import make_scale
from utility.screen_utility.screenManager import get_screen_function


def handle_draggable(item, screen, gui_manager, virtual_size, bounds=None):
    item.rotation += getattr(item, "rotational_velocity", 0)
    item.rotational_velocity *= 0.85
    if abs(item.rotation) < 0.1:
        item.rotation = 0.0
        item.rotational_velocity = 0.0
    else:
        item.rotation *= 0.9

    if bounds is not None and item in getattr(gui_manager.bag_manager, "contents", []):
        screenX, screenY, screenW, screenH = bounds
    elif screen:
        screenX, screenY, screenW, screenH = 0, 0, screen.get_width(), screen.get_height()
    else:
        screenX, screenY, screenW, screenH = 0, 0, 480, 270

    currentX, currentY = item.pos
    if not item.dragging:
        currentX += getattr(item, "vx", 0)
        currentY += getattr(item, "vy", 0)

    item.vx /= getattr(item, "friction", 1.05)
    item.vy += getattr(item, "currentGravity", 0.3)

    item_width, item_height = item.image.get_size()
    half_width = item_width // 2
    half_height = item_height // 2

    # 🔸 Slosh inertia for BottleItems
    if hasattr(item, "liquid_rotational_velocity"):
        # Parameters you can tweak
        slosh_strength = 0.05     # How much movement contributes
        stiffness = 0.02          # How strongly it wants to return to center
        damping = 0.93             # How much energy is lost per frame (0.9 = light damping)

        # Calculate movement-based input
        movement_input = item.ovx if item.dragging else item.vx
        item.liquid_rotational_velocity += movement_input * slosh_strength

        # Spring force pulling back toward center
        item.liquid_rotational_velocity -= item.liquid_rotation * stiffness

        # Apply damping to slow down over time
        item.liquid_rotational_velocity *= damping

        # Update rotation value
        item.liquid_rotation += item.liquid_rotational_velocity
        max_rotation = 45  # radians or whatever makes sense for your bottle
        item.liquid_rotation = max(-max_rotation, min(max_rotation, item.liquid_rotation))



    if not item.dragging and item.vy > 0:
        if currentY > getattr(item, "floor", currentY):
            currentY = item.floor
            item.vy = 0
            item.vx /= 1.5

    if not item.dragging:
        if currentX - half_width < screenX:
            currentX = screenX + half_width
            item.vx = abs(item.vx) / 1.1
        if currentX + half_width > screenX + screenW:
            currentX = screenX + screenW - half_width
            item.vx = -abs(item.vx) / 1.1
        if currentY - half_height < screenY:
            currentY = screenY + half_height
            item.vy = abs(item.vy) / 1.1
        if currentY + half_height > screenY + screenH:
            currentY = screenY + screenH - half_height
            item.vy = abs(item.vy) / 1.1

    item.pos = (currentX, currentY)



def handle_charm(item, screen, gui_manager):
    if item.is_clicked:
        if not hasattr(item, "window") or item.window is None:
            item.window = returnCharmWindow(item)
            gui_manager.windows.append(item.window)
    elif hasattr(item, "window") and item.window:
        if item.window in gui_manager.windows:
            gui_manager.windows.remove(item.window)
        item.window = None


def handle_hangable(item, screen):
    if not hasattr(item, "anchor") or item.anchor is None or item.anchor_pos is None:
        item.show_nail = False
        return

    if item.anchor == "charmboard":
        anchor_x = item.anchor_pos[0]
        anchor_y = 25 + item.anchor_pos[1]
        item.show_nail = True
    else:
        anchor_item = item.manager.getItemByUUID(item.anchor)
        if anchor_item is None:
            raise LookupError(f"Could not find anchor item with UUID {item.anchor}")
        anchor_x = anchor_item.pos[0]
        anchor_y = anchor_item.pos[1]
        item.show_nail = False

    item.floor = screen.get_height() - item.image.get_height() * 2

    item.vx = getattr(item, "vx", 0)
    item.vy = getattr(item, "vy", 0)
    item.mass = getattr(item, "mass", 1)
    if not hasattr(item, "rope_length"):
        dx = item.pos[0] - anchor_x
        dy = item.pos[1] - anchor_y
        item.rope_length = max(20, (dx ** 2 + dy ** 2) ** 0.5)
    item.rope_length = min(item.rope_length, 20)

    item.vy += getattr(item, "currentGravity", 0.3)

    if not item.dragging:
        item.pos = (item.pos[0] + item.vx, item.pos[1] + item.vy)

    dx = item.pos[0] - anchor_x
    dy = item.pos[1] - anchor_y
    dist = (dx ** 2 + dy ** 2) ** 0.5
    nx, ny = dx / (dist or 1), dy / (dist or 1)
    stretch = dist - item.rope_length
    pull_strength = 0.1
    item.vx -= (nx * stretch * pull_strength) / 3
    item.vy -= (ny * stretch * pull_strength) / 3

    item.vx *= 0.8
    item.vy *= 0.8

    max_velocity = 20
    item.vx = max(min(item.vx, max_velocity), -max_velocity)
    item.vy = max(min(item.vy, max_velocity), -max_velocity)

    item.rotational_velocity -= item.vx * 0.01
    item.rotational_velocity *= 0.95

    if item.anchor != "charmboard":
        item.anchor_pos = (anchor_x, anchor_y)


def handle_temperature_particles(item):
    if getattr(item, "temperature", 0) >= 500:
        if random.random() < item.temperature / 50000:
            item.particles.extend(make_scale(item.pos, count=1))


def handle_screen_switch(item, screen, screen_switcher):
    if isinstance(item.next_screen, str):
        item.next_screen = get_screen_function(item.next_screen)
    screen_switcher.start(lambda: item.next_screen(screen))
