import pygame
from utility.gui_utility.quicktrick import QuickMenu
from utility.item_utility.trickAnimation import *

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
                        colliding = rect.collidepoint(mx,my)
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
                        accepted = getattr(slot, "slot_accepts", [])
                        dragged_type = getattr(dragged, "type", getattr(dragged, "tool_type", None))
                        if is_valid_for_slot(slot, dragged) and slot.contains is None:

                            dragged.set_position(slot.pos)

                            dragged.trick = TrickAnimation([
                                {"time": 0.0, "scale": (1.2, 1.2), "particles":"sparkles"},
                                {"time": 0.1, "scale": (0.95, 0.95)},
                                {"time": 0.2, "scale": (1.0, 1.0)}
                            ])

                            slot.contains = dragged.uuid


    @staticmethod
    def draw_overlay(surface, items, dragged_item, mouse_pos, virtual_size):
        if not dragged_item:
            return

        for slot in [i for i in items if "slot" in getattr(i, "flags", [])]:
            if not is_valid_for_slot(slot, dragged_item):
                continue
            if slot.contains is not None:
                continue

            # --- Prepare ghost image
            if hasattr(dragged_item, "type"):
                ghost_img = dragged_item.image.copy()
            else:
                ghost_img = dragged_item.get_image(virtual_size)
            ghost_img.set_alpha(100)

            # Uniform screen scale (dragged item always drawn at scale 1)
            if hasattr(dragged_item, "type"):
                scale_x = virtual_size[0] / 480
                scale_y = virtual_size[1] / 270
            else:
                scale_x = dragged_item.scale[0]/2
                scale_y = dragged_item.scale[1]/2
            scaled_size = (
                int(ghost_img.get_width() * scale_x),
                int(ghost_img.get_height() * scale_y)
            )
            ghost_img = pygame.transform.scale(ghost_img, scaled_size)

            # Draw ghost centered at slot.pos
            ghost_rect = ghost_img.get_rect(center=slot.pos)
            surface.blit(ghost_img, ghost_rect.topleft)

            # --- Draw outline if hovered
            slot_rect = slot.get_scaled_hitbox(virtual_size)
            if slot_rect.collidepoint(mouse_pos):
                mask = pygame.mask.from_surface(ghost_img)
                outline = mask.outline()
                if outline:
                    offset_outline = [(ghost_rect.left + x, ghost_rect.top + y) for x, y in outline]
                    pygame.draw.polygon(surface, (255, 255, 255), offset_outline, width=1)


def is_valid_for_slot(slot, item):
    slot_name = getattr(slot, "slot_name", None)
    accepted = getattr(slot, "slot_accepts", [])

    item_type = getattr(item, "type", getattr(item, "tool_type", None))

    # Fuel slot restriction
    if slot_name == "fuel_input" and item_type != "fuel":
        return False
    
    if slot_name == "weapon_slot1" or slot_name == "weapon_slot2":
        if hasattr(item, "type"):
            return False
    
    if slot_name in ["furnace_input_1","furnace_input_2","furnace_input_3","furnace_input_4","furnace_input_5"]:
        if hasattr(item, "tool_type"):
            return False
        

    # If slot_accepts is empty, accept anything (unless blocked by above)
    if not accepted:
        return True

    # If slot_accepts is defined, item_type must be in it
    return item_type in accepted





class TrickFlag:
    right_mouse_held = False
    active_item = None

    @staticmethod
    def handle_event(event, item_list, mouse_pos, virtual_size, gui_manager):
        mx, my = mouse_pos

        # When RIGHT BUTTON is PRESSED
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            for item in reversed(item_list):  # Topmost first
                if hasattr(item, "type"):
                    continue  # Skip non-tools
                if "tricks" in getattr(item, "flags", []):
                    if item.is_point_inside((mx, my), virtual_size):
                        TrickFlag.right_mouse_held = True
                        TrickFlag.active_item = item
                        gui_manager.quick_menu = QuickMenu(
                            center=(mx, my), 
                            radius=35*(virtual_size[0]/480), 
                            total_slots=6, 
                            unlocked_slots=3, 
                            images_folder=f"assets/tools/{item.tool_type}/tricks")

                        break

        # When RIGHT BUTTON is RELEASED
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            TrickFlag.right_mouse_held = False

            # If a selection was made
            if gui_manager.quick_menu and gui_manager.quick_menu.selected_index is not None:
                chosen = gui_manager.quick_menu.selected_index
                print(f"Selected trick index: {chosen}")

                # You can now trigger animation, keyframe, etc., here.
                TrickFlag.active_item.original_pos = TrickFlag.active_item.pos
                TrickFlag.active_item.squish = [1.0, 1.0]  # if not already
                TrickFlag.active_item.trick = TrickAnimation(kickflip, on_complete=lambda i: print("Kickflip done!"))

                gui_manager.quick_menu = None
            elif gui_manager.quick_menu:
                gui_manager.quick_menu.hide()
            TrickFlag.active_item = None

        # Safety: If left mouse is clicked, cancel menu too
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if gui_manager.quick_menu:
                gui_manager.quick_menu.hide()
            TrickFlag.right_mouse_held = False
            TrickFlag.active_item = None

