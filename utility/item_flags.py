import pygame
import math

class DraggableFlag:
    dragging_item = None
    offset = (0, 0)
    last_pos = None

    @staticmethod
    def handle_event(event, item_list, mouse_pos):
        mx, my = mouse_pos

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item in reversed(item_list):
                if "draggable" in getattr(item, "flags", []):
                    rect = item.image.get_rect(topleft=item.pos)
                    if rect.collidepoint(mx, my):
                        DraggableFlag.dragging_item = item
                        DraggableFlag.offset = (mx - item.pos[0], my - item.pos[1])
                        DraggableFlag.last_pos = item.pos
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            DraggableFlag.dragging_item = None
            DraggableFlag.last_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if DraggableFlag.dragging_item:
                dx, dy = DraggableFlag.offset
                new_pos = (mx - dx, my - dy)

                old_x, old_y = DraggableFlag.last_pos
                vx = new_pos[0] - old_x
                vy = new_pos[1] - old_y
                DraggableFlag.last_pos = new_pos

                DraggableFlag.dragging_item.pos = new_pos

                # Apply rotational velocity based on horizontal speed
                # You can tweak the multiplier for effect
                DraggableFlag.dragging_item.rotational_velocity += vx * 0.2
