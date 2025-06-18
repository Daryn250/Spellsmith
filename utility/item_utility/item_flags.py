import pygame

class DraggableFlag:
    dragging_item = None
    offset = (0, 0)
    last_pos = None

    @staticmethod
    def handle_event(event, item_list, mouse_pos, virtual_size, gui_manager):
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

                if hasattr(item, "anchor_pos"):
                    if item.anchor_pos==None:
                        HangableFlag.try_attatch(event, item, item_list, mouse_pos, virtual_size, gui_manager)

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
                HangableFlag.try_detatch(DraggableFlag.dragging_item)

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
    def try_attatch(event, item, itemlist, mouse_pos, virtual_size, gui_manager):
        if "hangable" not in item.flags:
            return

        mx, my = mouse_pos

        # --- 1. Check if charm is dropped on charmboard ---
        img = gui_manager.charmboard_img
        img_width, img_height = img.get_size()
        scale_x = virtual_size[0] / 480
        scale_y = virtual_size[1] / 270
        scaled_size = (img_width * scale_x, img_height * scale_y)

        top_right_x = virtual_size[0] - scaled_size[0] * 1.25
        top_right_y = 25
        charmboard_rect = pygame.Rect((top_right_x, top_right_y), scaled_size)

        if charmboard_rect.collidepoint(mx, my):
            item.anchor = "charmboard"
            # Store position relative to charmboard's top-left
            item.anchor_pos = (mx, my)
            print("connected to charmboard")
            return

        # --- 2. Check if dropped on another charm ---
        for candidate in reversed(itemlist):
            if candidate == item:
                continue
            if "charm" in getattr(candidate, "flags", []):
                candidate_rect = candidate.get_scaled_hitbox(virtual_size)
                if candidate_rect.collidepoint(mx, my):
                    item.anchor = candidate.uuid
                    item.anchor_pos = (mx - candidate.pos[0], my - candidate.pos[1])
                    print(f"connected to charm {candidate}")
                    return

        # --- 3. No valid anchor found ---
        item.anchor = None
        item.anchor_pos = None
        print("no candidate found.")
    def try_detatch(item):
        if hasattr(item, "anchor") and item.anchor is not None and item.anchor_pos is not None:
            # Determine anchor world position
            if item.anchor == "charmboard":
                anchor_x = item.anchor_pos[0]
                anchor_y = 25 + item.anchor_pos[1]
            else:
                anchor_x = item.anchor.pos[0] + item.anchor_pos[0]
                anchor_y = item.anchor.pos[1] + item.anchor_pos[1]

            # Compute current distance
            dx = item.pos[0] - anchor_x
            dy = item.pos[1] - anchor_y
            dist = (dx**2 + dy**2) ** 0.5

            # Check if stretched beyond 1.5x rope length
            if dist > item.rope_length * 4:
                item.anchor = None
                item.anchor_pos = None
                item.show_nail = False
