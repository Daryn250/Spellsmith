import pygame
from utility.gui_utility.quicktrick import QuickMenu

class DraggableFlag:
    dragging_item = None
    offset = (0, 0)
    last_pos = None

    @staticmethod
    def handle_event(event, item_list, mouse_pos, virtual_size, gui_manager, item_manager):
        mx, my = mouse_pos
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for item in reversed(item_list):
                if "draggable" in getattr(item, "flags", []):

                    if hasattr(item, "type"):
                        rect = item.get_scaled_hitbox(virtual_size)
                        colliding = rect.collide_point(mx,my)
                    elif hasattr(item, "tool_type"):
                        colliding = item.is_point_inside((mx,my), virtual_size)

                    if colliding:
                        DraggableFlag.dragging_item = item
                        DraggableFlag.offset = (mx - item.pos[0], my - item.pos[1])
                        DraggableFlag.last_pos = item.pos
                        for slot in item_list:
                            if "slot" not in slot.flags:
                                continue
                            if slot.contains == DraggableFlag.dragging_item.uuid:
                                slot.contains = None
                                break
                        break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if DraggableFlag.dragging_item != None:
                item = DraggableFlag.dragging_item
                
                item.floor = item.pos[1] + 30
                item.currentGravity = item.storedGravity
                if hasattr(item, "ovx"):
                    if item.dragging_for>1:
                        item.vx = item.ovx
                        item.vy = item.ovy
                item.dragging_for = 0

                if hasattr(item, "anchor_pos"):
                    if item.anchor_pos==None:
                        HangableFlag.try_attatch(event, item, item_list, mouse_pos, virtual_size, gui_manager, item_manager)
                if hasattr(item, "anchor"):
                    if item.anchor == None:
                        detatch_connected(item, item_list, item_manager)
                SlotFlag.handle_event(event, item_list, mouse_pos, virtual_size)
                item.dragging = False
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
                if hasattr(DraggableFlag.dragging_item, "type"):
                    DraggableFlag.dragging_item.rotational_velocity += vx * 0.05
                elif hasattr(DraggableFlag.dragging_item, "tool_type"):
                    DraggableFlag.dragging_item.rotational_velocity += vx * 0.005
                DraggableFlag.dragging_item.ovx = vx
                DraggableFlag.dragging_item.ovy = vy
                
                HangableFlag.try_detatch(DraggableFlag.dragging_item, item_manager)
                

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
                        item.img.frames = item.img._load_frames_from_folder(f"assets/gui/charm_board/{item.charmType}/active")
                        item.img_path = f"assets/gui/charm_board/{item.charmType}/passive"
                    elif not inside and getattr(item, "is_clicked", False):
                        item.is_clicked = False
                        item.img.frames = item.img._load_frames_from_folder(f"assets/gui/charm_board/{item.charmType}/passive")
                        item.img_path = f"assets/gui/charm_board/{item.charmType}/passive"

class HangableFlag:
    @staticmethod
    def try_attatch(event, item, itemlist, mouse_pos, virtual_size, gui_manager, item_manager):
        if "hangable" not in item.flags:
            return
        if item.anchor!=None:
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
            return

        # --- 2. Check if dropped on another charm ---
        for candidate in reversed(itemlist):
            if candidate == item:
                continue

            if "charm" in getattr(candidate, "flags", []):
                candidate_rect = candidate.get_scaled_hitbox(virtual_size)

                # Prevent attaching to a charm that's already occupied
                connected_item = get_connected(candidate.uuid, itemlist, item_manager)
                if connected_item is not None:
                    continue

                # Check mouse overlap
                if candidate_rect.collidepoint(mx, my):
                    item.anchor = candidate.uuid
                    item.anchor_pos = (candidate.pos[0], candidate.pos[1])
                    return


        # --- 3. No valid anchor found ---
        item.anchor = None
        item.anchor_pos = None
    def try_detatch(item, item_manager):
        if hasattr(item, "anchor") and item.anchor is not None and item.anchor_pos is not None:
            # Determine anchor world position
            if item.anchor == "charmboard":
                anchor_x = item.anchor_pos[0]
                anchor_y = 25 + item.anchor_pos[1]
            else:
                anchoritem = item_manager.getItemByUUID(item.anchor)
                anchor_x = anchoritem.pos[0]
                anchor_y = anchoritem.pos[1]

            # Compute current distance
            dx = item.pos[0] - anchor_x
            dy = item.pos[1] - anchor_y
            dist = (dx**2 + dy**2) ** 0.5

            # Check if stretched beyond 1.5x rope length
            if dist > item.rope_length * 4:
                item.anchor = None
                item.anchor_pos = None
                item.show_nail = False
                return True

    
def detatch_connected(item, itemlist, item_manager):
    for a in itemlist:
        # If this item's anchor is the current item
        if getattr(a, "anchor", None) == item.uuid:
            # Detach this item
            a.anchor = None
            a.anchor_pos = None
            a.floor = a.pos[1]+30

            # Recursively detach any items anchored to this one
            detatch_connected(a, itemlist, item_manager)

def get_connected(item, itemlist, item_manager):
    """Returns the first item that is anchored to the given item, or None if none exist."""
    for other in itemlist:
        if hasattr(other, "anchor"):
            if other.anchor == item:
                return other
    return None

class SlotFlag:
    @staticmethod
    def handle_event(event, items, mouse_pos, virtual_size):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            for slot in [i for i in items if "slot" in getattr(i, "flags", [])]:
                slot_rect = slot.get_scaled_hitbox(virtual_size)
                for dragged in [j for j in items if getattr(j, "dragging", False)]:
                    if slot_rect.collidepoint(mouse_pos):
                        accepted = getattr(slot, "slot_accepts", None)
                        if accepted is None or dragged.type in accepted:
                            if slot.contains == None:
                                dragged.set_position(slot.pos)
                                slot.contains = dragged.uuid

    @staticmethod
    def draw_overlay(surface, items, dragged_item, mouse_pos, virtual_size):
        if not dragged_item:
            return

        for slot in [i for i in items if "slot" in getattr(i, "flags", [])]:
            accepted = getattr(slot, "slot_accepts", None)
            if accepted is not None and dragged_item.type not in accepted:
                continue

            if slot.contains != None:
                continue

            # --- Scale the ghost image correctly
            ghost_img = dragged_item.image.copy()
            ghost_img.set_alpha(100)

            # Get uniform screen scale
            x_scale = virtual_size[0] / 480
            y_scale = virtual_size[1] / 270
            scale = min(x_scale, y_scale)

            # Scale image
            scaled_size = (int(ghost_img.get_width() * scale), int(ghost_img.get_height() * scale))
            ghost_img = pygame.transform.scale(ghost_img, scaled_size)

            # Draw ghost image at slot's position
            surface.blit(ghost_img, slot.pos)

            # --- If hovering, draw glowing outline using image mask
            slot_rect = slot.get_scaled_hitbox(virtual_size)
            if slot_rect.collidepoint(mouse_pos):
                # Create mask and outline from the ghost image
                mask = pygame.mask.from_surface(ghost_img)
                outline = mask.outline()

                if outline:
                    # Offset the outline by the image position
                    offset_outline = [(slot.pos[0] + x, slot.pos[1] + y) for x, y in outline]
                    pygame.draw.polygon(surface, (255, 255, 255), offset_outline, width=1)

class TrickFlag: # allow performing of tricks when right clicked (tools only)
    @staticmethod
    def handle_event(event, item_list, mouse_pos, virtual_size, gui_manager):
        mx, my = mouse_pos

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for item in reversed(item_list):  # Topmost items get priority
                if hasattr(item, "type"):
                    continue # filter non-tool items
                if "tricks" in getattr(item, "flags", []):
                    if item.is_point_inside((mx,my), virtual_size):
                        gui_manager.quick_menu = QuickMenu(
                        center=(240, 135),
                        radius=60,
                        divisions=1,
                        images=f"assets/tools/{item.tool_type}/tricks"
                    )
                    else:
                        gui_manager.quick_menu.hide()