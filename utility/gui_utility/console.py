import pygame
import sys
import json

class DebugConsole:
    def __init__(self, base_screen):
        self.screen = base_screen
        self.active = False
        self.input_text = ""
        self.font = pygame.font.Font("assets\Tiny5-Regular.ttf", 16)
        self.rect = pygame.Rect(40, 40, 600, 260)
        self.close_rect = pygame.Rect(40 + 600 - 40, 40, 30, 30)  # Close button (top right)
        self.info_lines = []
        self.max_info_lines = 100  # allow more lines for scrolling
        self.last_command = ""
        self.cursor_visible = True
        self.cursor_interval = 500  # ms
        self.cursor_pos = 0  # Position in input_text
        self.scroll_offset = 0  # For scrolling info lines
        self.line_height = 18  # Reduced margin between lines
        self.autocomplete_matches = []
        self.autocomplete_index = 0
        self.command_usages = {
            "spawn": "spawn <item> [nbt_json]",
            "get": "get <attr_path>",
            "list": "list [attr_path]",
            "ls": "ls [attr_path]",
            "help": "help",
            "clear": "clear",
            "run": "run <attr_path>([args])",
            "modify": "modify <attr_path> <value>",
            "version": "version"
        }

    def toggle(self):
        self.active = not self.active
        self.input_text = ""
        self.info_lines = []
        self.last_command = ""
        self.cursor_visible = True
        self.cursor_pos = 0

    def handle_event(self, event):
        if not self.active:
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.run_command(self.input_text)
                self.last_command = self.input_text
                self.input_text = ""
                self.cursor_pos = 0
                self.scroll_offset = 0
                self.autocomplete_matches = []
                self.autocomplete_index = 0
            elif event.key == pygame.K_TAB:
                # Autocomplete to the current selection in the list
                if self.autocomplete_matches:
                    suggestion = self.autocomplete_matches[self.autocomplete_index]
                    before_cursor = self.input_text[:self.cursor_pos]
                    parts = before_cursor.split()
                    if not parts:
                        self.input_text = suggestion + ' '
                        self.cursor_pos = len(self.input_text)
                    elif len(parts) == 1:
                        self.input_text = suggestion + ' '
                        self.cursor_pos = len(self.input_text)
                    elif len(parts) >= 2:
                        cmd = parts[0]
                        arg = parts[1]
                        if cmd == "spawn":
                            self.input_text = cmd + ' ' + suggestion + ' '
                            self.cursor_pos = len(self.input_text)
                        elif cmd in ("get", "list", "ls"):
                            # Complete the attribute path
                            rest = before_cursor.split(' ', 1)[-1]
                            if '.' in rest:
                                base = rest[:rest.rfind('.')+1]
                                self.input_text = cmd + ' ' + base + suggestion
                            else:
                                self.input_text = cmd + ' ' + suggestion
                            self.cursor_pos = len(self.input_text)
                    self.autocomplete_matches = []
                    self.autocomplete_index = 0
                else:
                    self.handle_autocomplete()
            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.input_text = self.input_text[:self.cursor_pos-1] + self.input_text[self.cursor_pos:]
                    self.cursor_pos -= 1
                self.autocomplete_matches = []
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.input_text):
                    self.input_text = self.input_text[:self.cursor_pos] + self.input_text[self.cursor_pos+1:]
                self.autocomplete_matches = []
            elif event.key == pygame.K_ESCAPE:
                self.toggle()
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
                self.autocomplete_matches = []
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.input_text):
                    self.cursor_pos += 1
                self.autocomplete_matches = []
            elif event.key == pygame.K_UP:
                # Prevent up arrow from recalling last command if autocomplete list is open
                if self.autocomplete_matches:
                    self.autocomplete_index = (self.autocomplete_index - 1) % len(self.autocomplete_matches)
                elif self.input_text == "" and self.scroll_offset < self.get_max_scroll():
                    self.scroll_offset += 1
                elif self.last_command:
                    self.input_text = self.last_command
                    self.cursor_pos = len(self.input_text)
                self.autocomplete_matches = [] if not self.autocomplete_matches else self.autocomplete_matches
            elif event.key == pygame.K_DOWN:
                if self.input_text == "" and self.scroll_offset > 0:
                    self.scroll_offset -= 1
                elif self.autocomplete_matches:
                    self.autocomplete_index = (self.autocomplete_index + 1) % len(self.autocomplete_matches)
            elif event.key == pygame.K_v and (event.mod & pygame.KMOD_CTRL):
                try:
                    import pyperclip #type: ignore
                    paste = pyperclip.paste()
                    self.input_text = self.input_text[:self.cursor_pos] + paste + self.input_text[self.cursor_pos:]
                    self.cursor_pos += len(paste)
                except Exception:
                    pass
                self.autocomplete_matches = []
            else:
                # Only add printable, non-empty unicode characters
                if len(self.input_text) < 256 and event.unicode and event.unicode.isprintable():
                    self.input_text = self.input_text[:self.cursor_pos] + event.unicode + self.input_text[self.cursor_pos:]
                    self.cursor_pos += 1
                self.autocomplete_matches = []
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.close_rect.collidepoint(event.pos):
                self.toggle()
        elif event.type == pygame.MOUSEWHEEL:
            if event.y > 0:
                self.scroll_offset = min(self.scroll_offset + 1, self.get_max_scroll())
            elif event.y < 0:
                self.scroll_offset = max(self.scroll_offset - 1, 0)

    def get_max_scroll(self):
        # Calculate how many wrapped lines there are
        max_width = self.rect.width - 20
        all_wrapped = []
        for line in self.info_lines:
            all_wrapped.extend(self.wrap_text(line, self.font, max_width))
        visible_lines = (self.rect.height - 60) // self.line_height
        return max(0, len(all_wrapped) - visible_lines)

    def run_command(self, command_line):
        if not command_line.strip():
            return
        parts = command_line.strip().split(maxsplit=2)
        if not parts:
            return
        cmd = parts[0].lower()
        if cmd == "spawn":
            if len(parts) < 2:
                self.add_info("Usage: spawn <item> [nbt_json]")
                return
            item_type = parts[1]
            nbt = {}
            if len(parts) == 3:
                try:
                    nbt = json.loads(parts[2])
                except Exception as e:
                    self.add_info(f"NBT error: {e}")
                    return
            try:
                from utility.item_utility.itemMaker import makeItem
                item = makeItem(self.screen.item_manager, item_type, (200, 200), self.screen.screen_name, nbt)
                self.add_info(f"Spawned: {item_type}")
            except Exception as e:
                self.add_info(f"Spawn error: {e}")
        elif cmd == "help":
            self.add_info("Commands: spawn, help, get, ls/list, run, modify, version")
        elif cmd == "clear":
            self.info_lines = []
        elif cmd == "get":
            # Support nested attributes, e.g. helper.fuel_level
            if len(parts) < 2:
                self.add_info("Usage: get <attr_path>")
                return
            attr_path = parts[1].split('.')
            obj = self.screen
            try:
                for attr in attr_path:
                    obj = getattr(obj, attr)
                self.add_info(f"{parts[1]}: {obj}")
            except Exception as e:
                self.add_info(f"get error: {e}")
        elif cmd == "list" or cmd == 'ls':
            # List all attributes of an object, optionally nested
            target = self.screen
            if len(parts) >= 2:
                attr_path = parts[1].split('.')
                try:
                    for attr in attr_path:
                        target = getattr(target, attr)
                except Exception as e:
                    self.add_info(f"ls error: {e}")
                    return
            attrs = dir(target)
            # Filter out dunder methods
            attrs = [a for a in attrs if not a.startswith('__')]
            self.add_info(f"Attributes: {', '.join(attrs)}")
        elif cmd == "run":
            # Usage: run <attr_path>([args])
            if len(parts) < 2:
                self.add_info("Usage: run <attr_path>([args])")
                return
            import ast
            expr = parts[1]
            # Support multi-word input for arguments
            if len(parts) > 2:
                expr += ' ' + ' '.join(parts[2:])
            try:
                # Parse the function call
                tree = ast.parse(expr, mode='eval')
                if not isinstance(tree.body, ast.Call):
                    self.add_info("run error: must be a function call")
                    return
                # Traverse the attribute path
                node = tree.body.func
                obj = self.screen
                attrs = []
                while isinstance(node, ast.Attribute):
                    attrs.append(node.attr)
                    node = node.value
                if isinstance(node, ast.Name):
                    attrs.append(node.id)
                else:
                    self.add_info("run error: invalid attribute path")
                    return
                attrs = list(reversed(attrs))
                for attr in attrs:
                    obj = getattr(obj, attr)
                # Evaluate arguments
                args = []
                kwargs = {}
                for arg in tree.body.args:
                    args.append(ast.literal_eval(arg))
                for kw in tree.body.keywords:
                    kwargs[kw.arg] = ast.literal_eval(kw.value)
                result = obj(*args, **kwargs)
                if result != None:
                    self.add_info(f"run result: {result}")
            except Exception as e:
                self.add_info(f"run error: {e}")
        elif cmd == "modify":
            # Usage: modify <attr_path> <value>
            if len(parts) < 3:
                self.add_info("Usage: modify <attr_path> <value>")
                return
            attr_path = parts[1].split('.')
            obj = self.screen
            try:
                for attr in attr_path[:-1]:
                    obj = getattr(obj, attr)
                final_attr = attr_path[-1]
                import ast
                value = ast.literal_eval(parts[2]) if parts[2] else parts[2]
                setattr(obj, final_attr, value)
                self.add_info(f"{parts[1]} set to {value}")
            except Exception as e:
                self.add_info(f"modify error: {e}")
        elif cmd == "honse":
            try:
                raise PermissionError("you do not have permission to access the honse.")
            except Exception as e:
                self.add_info(f"honse error: {e}")
        elif cmd == "version" or cmd == "vers":
            try:
                self.add_info(f"Version: {self.screen.instance_manager.version}")
            except Exception as e:
                self.add_info(f"version error: {e}")
        else:
            self.add_info(f"Unknown command: {cmd}")

    def add_info(self, msg):
        self.info_lines.append(str(msg))
        if len(self.info_lines) > self.max_info_lines:
            self.info_lines = self.info_lines[-self.max_info_lines:]

    def update(self, dt):
        # Blinking cursor logic (dt in ms)
        if not hasattr(self, 'cursor_accum'):
            self.cursor_accum = 0
        self.cursor_accum += dt
        if self.cursor_accum >= self.cursor_interval:
            self.cursor_visible = not self.cursor_visible
            self.cursor_accum = 0

    def wrap_text(self, text, font, max_width):
        words = text.split(' ')
        lines = []
        current = ''
        for word in words:
            test = current + (' ' if current else '') + word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def handle_autocomplete(self):
        before_cursor = self.input_text[:self.cursor_pos]
        parts = before_cursor.split()
        if not parts:
            self.autocomplete_matches = [c for c in self.command_usages.keys()]
            self.autocomplete_index = 0
            return
        if len(parts) == 1:
            matches = [c for c in self.command_usages.keys() if c.startswith(parts[0]) and c != 'spawn']
            if not matches:
                self.autocomplete_matches = []
                return
            if len(matches) == 1:
                cmd = matches[0]
                self.input_text = cmd + ' '
                self.cursor_pos = len(self.input_text)
                self.autocomplete_matches = []
            else:
                self.autocomplete_matches = matches
                self.autocomplete_index = 0
        elif len(parts) >= 2:
            cmd = parts[0]
            arg = parts[1]
            if cmd == "spawn":
                # Autocomplete item types from item_to_info and ITEM_BASES, but never suggest 'spawn'
                try:
                    from utility.item_utility import item_to_info
                    from utility.item_utility import itemMaker
                    item_names = set(item_to_info.window_data.keys())
                    item_names.update(itemMaker.ITEM_BASES.keys())
                    item_names.discard('spawn')
                    item_names = sorted(item_names)
                except Exception:
                    item_names = []
                matches = [n for n in item_names if n.startswith(arg)]
                if not matches:
                    self.autocomplete_matches = []
                    return
                if len(matches) == 1:
                    new_input = cmd + ' ' + matches[0] + ' '
                    self.input_text = new_input
                    self.cursor_pos = len(self.input_text)
                    self.autocomplete_matches = []
                else:
                    self.autocomplete_matches = matches
                    self.autocomplete_index = 0
            elif cmd in ("get", "list", "ls"):
                obj = self.screen
                attr_path = arg.split('.')
                try:
                    for a in attr_path[:-1]:
                        obj = getattr(obj, a)
                    attrs = [a for a in dir(obj) if not a.startswith('__')]
                    matches = [a for a in attrs if a.startswith(attr_path[-1])]
                except Exception:
                    matches = []
                if not matches:
                    self.autocomplete_matches = []
                    return
                if len(matches) == 1:
                    new_arg = '.'.join(attr_path[:-1] + [matches[0]])
                    self.input_text = cmd + ' ' + new_arg
                    self.cursor_pos = len(self.input_text)
                    self.autocomplete_matches = []
                else:
                    self.autocomplete_matches = matches
                    self.autocomplete_index = 0

    def draw(self, surface):
        if not self.active:
            return
        # Draw usage/help above the window
        usage = ""
        before_cursor = self.input_text.strip().split()
        if before_cursor:
            cmd = before_cursor[0]
            usage = self.command_usages.get(cmd, "")
        if usage:
            usage_font = self.font
            usage_surf = usage_font.render(usage, True, (200, 255, 255, 120))
            usage_bg = pygame.Surface((self.rect.width, usage_surf.get_height()+6), pygame.SRCALPHA)
            usage_bg.fill((30, 30, 30, 120))
            surface.blit(usage_bg, (self.rect.x, self.rect.y - usage_surf.get_height() - 10))
            surface.blit(usage_surf, (self.rect.x + 10, self.rect.y - usage_surf.get_height() - 7))
        # Draw semi-transparent background
        s = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        s.fill((30, 30, 30, 220))
        surface.blit(s, (self.rect.x, self.rect.y))
        pygame.draw.rect(surface, (200, 200, 200), self.rect, 2)
        # Draw suggestion line (ghosted suggestion, then real text on top)
        input_prefix = "> "
        input_display = input_prefix + self.input_text
        # Always show inline autocomplete suggestion if available
        suggestion = None
        if self.autocomplete_matches and self.input_text is not None:
            suggestion = self.autocomplete_matches[self.autocomplete_index]
        else:
            # Try to generate a suggestion even if autocomplete_matches is empty
            before_cursor = self.input_text[:self.cursor_pos]
            parts = before_cursor.split()
            if not parts:
                possible = [c for c in self.command_usages.keys() if c]
                if possible:
                    suggestion = possible[0]
            elif len(parts) == 1:
                matches = [c for c in self.command_usages.keys() if c.startswith(parts[0])]
                if matches:
                    suggestion = matches[0]
            elif len(parts) >= 2:
                cmd = parts[0]
                arg = parts[1]
                if cmd == "spawn":
                    try:
                        from utility.item_utility import item_to_info
                        from utility.item_utility import itemMaker
                        item_names = set(item_to_info.window_data.keys())
                        item_names.update(itemMaker.ITEM_BASES.keys())
                        item_names = sorted(item_names)
                    except Exception:
                        item_names = []
                    matches = [n for n in item_names if n.startswith(arg)]
                    if matches:
                        suggestion = matches[0]
                elif cmd in ("get", "list", "ls"):
                    obj = self.screen
                    attr_path = arg.split('.')
                    try:
                        for a in attr_path[:-1]:
                            obj = getattr(obj, a)
                        attrs = [a for a in dir(obj) if not a.startswith('__')]
                        matches = [a for a in attrs if a.startswith(attr_path[-1])]
                    except Exception:
                        matches = []
                    if matches:
                        suggestion = matches[0]
        if suggestion:
            before_cursor = self.input_text[:self.cursor_pos]
            parts = before_cursor.split()
            if len(parts) == 0:
                word = ''
            elif before_cursor.endswith(' '):
                word = ''
            else:
                word = parts[-1]
            if suggestion.startswith(word):
                ghost = suggestion[len(word):]
                suggestion_display = input_prefix + self.input_text[:self.cursor_pos] + ghost
                ghost_txt = self.font.render(suggestion_display, False, (180, 180, 180))
                surface.blit(ghost_txt, (self.rect.x + 10, self.rect.y + 10))
            else:
                ghost_txt = self.font.render(input_display, False, (180, 180, 180))
                surface.blit(ghost_txt, (self.rect.x + 10, self.rect.y + 10))
        else:
            ghost_txt = self.font.render(input_display, False, (180, 180, 180))
            surface.blit(ghost_txt, (self.rect.x + 10, self.rect.y + 10))
        # Draw actual input text on top (so it overwrites the ghosted part)
        txt = self.font.render(input_display, False, (0, 255, 0))
        surface.blit(txt, (self.rect.x + 10, self.rect.y + 10))
        # Draw blinking cursor at the correct position
        if self.cursor_visible:
            prefix = input_prefix + self.input_text[:self.cursor_pos]
            cursor_x = self.rect.x + 10 + self.font.size(prefix)[0]
            cursor_y = self.rect.y + 10
            cursor_h = self.font.get_height()
            pygame.draw.line(surface, (0, 255, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + cursor_h), 2)
        # Autocomplete overlay (draw on top of console output for visibility)
        if self.autocomplete_matches:
            ac_font = self.font
            ac_bg_height = min(120, 20*len(self.autocomplete_matches))
            ac_bg = pygame.Surface((self.rect.width-20, ac_bg_height), pygame.SRCALPHA)
            ac_bg.fill((40, 40, 40, 240))  # More opaque for better contrast
            ac_y = self.rect.y + 40  # Draw just below the input line
            surface.blit(ac_bg, (self.rect.x + 10, ac_y))
            for i, match in enumerate(self.autocomplete_matches[:6]):
                color = (60, 255, 255) if i == self.autocomplete_index else (180,180,180)
                ac_txt = ac_font.render(match, False, color)
                surface.blit(ac_txt, (self.rect.x + 18, ac_y + 2 + i*20))
        # Info lines (output) with wrapping and scrolling
        y = self.rect.y + 50
        max_width = self.rect.width - 20
        all_wrapped = []
        for line in self.info_lines:
            all_wrapped.extend(self.wrap_text(line, self.font, max_width))
        visible_lines = (self.rect.height - 60) // self.line_height
        start = max(0, len(all_wrapped) - visible_lines - self.scroll_offset)
        end = start + visible_lines
        for wline in all_wrapped[start:end]:
            info_txt = self.font.render(wline, False, (255, 255, 255))
            surface.blit(info_txt, (self.rect.x + 10, y))
            y += self.line_height
        # Draw scroll bar
        if len(all_wrapped) > visible_lines:
            bar_height = max(20, int(visible_lines / len(all_wrapped) * (self.rect.height - 60)))
            bar_y = self.rect.y + 50 + int((start / max(1, len(all_wrapped))) * (self.rect.height - 60 - bar_height))
            bar_x = self.rect.x + self.rect.width - 8
            pygame.draw.rect(surface, (80, 200, 200), (bar_x, bar_y, 6, bar_height), border_radius=3)
        # Close button (X)
        pygame.draw.rect(surface, (200, 80, 80), self.close_rect)
        x_txt = self.font.render("Esc", False, (255, 255, 255))
        x_center = self.close_rect.x + (self.close_rect.width - x_txt.get_width()) // 2
        y_center = self.close_rect.y + (self.close_rect.height - x_txt.get_height()) // 2
        surface.blit(x_txt, (x_center, y_center))

# Example usage in your main loop:
# debug_console = DebugConsole(item_manager)
# In event loop: debug_console.handle_event(event)
# To toggle: if event.key == pygame.K_F1: debug_console.toggle()
# In draw: debug_console.draw(screen)