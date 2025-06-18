import pygame

class DraggableFlag:
    dragging_item = None
    offset = (0, 0)
    last_pos = None

    @staticmethod
    def handle_event(event, item_list, mouse_pos, virtual_size):
        mx, my = mouse_pos

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item in reversed(item_list):
                if "draggable" in getattr(item, "flags", []):
                    rect = item.get_scaled_hitbox(virtual_size)
                    if rect.collidepoint(mx, my):
                        DraggableFlag.dragging_item = item
                        DraggableFlag.offset = (mx - item.pos[0], my - item.pos[1])
                        DraggableFlag.last_pos = item.pos
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if DraggableFlag.dragging_item != None:
                item = DraggableFlag.dragging_item
                item.dragging = False
                item.floor = item.pos[1] + 30
                item.currentGravity = item.storedGravity
                if hasattr(item, "ovx"):
                    if item.dragging_for>1:
                        item.vx = item.ovx
                        item.vy = item.ovy
                item.dragging_for = 0

            DraggableFlag.dragging_item = None
            DraggableFlag.last_pos = None

        elif event.type == pygame.MOUSEMOTION:
            if DraggableFlag.dragging_item:
                DraggableFlag.dragging_item.floor = DraggableFlag.dragging_item.pos[1] + 30 # set value so it doesn't interfere with dragging
                DraggableFlag.dragging_item.dragging = True
                if hasattr(DraggableFlag.dragging_item, "dragging_for"):
                    DraggableFlag.dragging_item.dragging_for +=1
                else:
                    DraggableFlag.dragging_item.dragging_for = 1
                dx, dy = DraggableFlag.offset
                new_pos = (mx - dx, my - dy)

                old_x, old_y = DraggableFlag.last_pos
                vx = new_pos[0] - old_x
                vy = new_pos[1] - old_y
                DraggableFlag.last_pos = new_pos

                DraggableFlag.dragging_item.pos = new_pos

                # Apply rotational velocity based on horizontal speed
                DraggableFlag.dragging_item.currentGravity = 0
                DraggableFlag.dragging_item.rotational_velocity += vx * 0.05
                DraggableFlag.dragging_item.ovx = vx
                DraggableFlag.dragging_item.ovy = vy

class ScreenChangeFlag:
    @staticmethod
    def handle_event(event, item_list, mouse_pos, screen, screenSwitcher, virtual_size):
        mx, my = mouse_pos

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for item in reversed(item_list):  # Topmost items get priority
                if "screen_change" in getattr(item, "flags", []):
                    rect = item.get_scaled_hitbox(virtual_size)
                    if rect.collidepoint(mx, my):
                        if hasattr(item, "next_screen"):
                            item.start_screen_switch(screen, screenSwitcher)
                        else:
                            print(f"Warning: Item {item} has 'screen_change' flag but no 'next_screen' method.")
                        break

class CharmFlag:
    @staticmethod
    def handle_event(event, itemlist, mouse_pos, virtual_size):
        mx, my = mouse_pos
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item in reversed(itemlist):  # Reversed in case of overlap, top items get priority
                if "charm" in getattr(item, "flags", []):
                    rect = item.get_scaled_hitbox(virtual_size)
                    inside = rect.collidepoint(mx, my)

                    if inside and not getattr(item, "is_clicked", False):
                        item.is_clicked = True
                    elif not inside and getattr(item, "is_clicked", False):
                        item.is_clicked = False

class HangableFlag:
    @staticmethod
    def handle_event(event, itemlist, mouse_pos, virtual_size):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            item = DraggableFlag.dragging_item
            if item and "hangable" in getattr(item, "flags", []):
                # You can define a function to find the closest valid anchor
                anchor = HangableFlag.find_anchor(item, itemlist, virtual_size)

                if anchor:
                    # Snap item to anchor
                    item.pos = HangableFlag.snap_to_anchor(anchor, item)
                    item.floor = item.pos[1]  # fix vertical settling
                    item.attached_to = anchor
                    item.show_nail = "charmboard" in getattr(anchor, "flags", [])
                else:
                    # Unanchor and let fall
                    if hasattr(item, "attached_to"):
                        del item.attached_to
                    item.show_nail = False

    @staticmethod
    def find_anchor(item, itemlist, virtual_size):
        # Find anchor within proximity (you define the threshold logic)
        mx, my = item.pos
        for candidate in itemlist:
            if candidate == item:
                continue
            if "charmboard" in getattr(candidate, "flags", []) or "charm" in getattr(candidate, "flags", []):
                rect = candidate.get_scaled_hitbox(virtual_size)
                if rect.collidepoint(mx, my):
                    return candidate
        return None

    @staticmethod
    def snap_to_anchor(anchor, item):
        anchor_rect = anchor.get_rect()
        # You can tweak the anchor point as desired
        x = anchor.pos[0] + anchor_rect.width // 2 - item.image.get_width() // 2
        y = anchor.pos[1] + anchor_rect.height
        return (x, y)

