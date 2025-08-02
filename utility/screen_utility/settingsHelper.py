import os
import pygame
import time

class Dropdown:
    def __init__(self, rect, options, selected, font, label, id, settings=None, sfx=None):
        self.rect = pygame.Rect(rect)
        self.settings = settings
        self.label = label
        self.id = id
        self.open = False
        self.font = font
        self.sfx = sfx

        self.options = options
        self.selected = selected
        self.display_labels = [
            settings.translated_text(opt) if settings else opt
            for opt in options
        ]

        # Precompute width
        texts = [f"{label}: {lbl}" for lbl in self.display_labels]
        max_w = max(font.size(txt)[0] for txt in texts) if texts else 140
        self.rect.width = max(140, max_w + 10)
        self.option_rects = []

    def open_dropdown(self):
        self.open = True
        self.option_rects = []
        for i in range(len(self.options)):
            r = pygame.Rect(
                self.rect.x,
                self.rect.y + (i + 1) * self.rect.height,
                self.rect.width,
                self.rect.height
            )
            self.option_rects.append(r)

    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(mouse_pos):
                if not self.open:
                    self.open_dropdown()
                else:
                    self.open = False
                return None
            if self.open:
                for idx, r in enumerate(self.option_rects):
                    if r.collidepoint(mouse_pos):
                        self.selected = self.options[idx]
                        self.open = False
                        if self.sfx:
                            self.sfx.play_sound("gui_click")
                        return self.selected
                self.open = False
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, (40,40,40,220), self.rect, border_radius=4)
        idx = self.options.index(self.selected) if self.selected in self.options else -1
        lbl = self.display_labels[idx] if idx >= 0 else "None"
        txt = self.font.render(f"{self.label}: {lbl}", False, (255,255,255))
        surface.blit(txt, txt.get_rect(midleft=(self.rect.x+5, self.rect.centery)))
        if self.open:
            for i, opt in enumerate(self.options):
                r = self.option_rects[i]
                pygame.draw.rect(surface, (60,60,60,220), r, border_radius=4)
                surf = self.font.render(self.display_labels[i], False, (255,255,255))
                surface.blit(surf, surf.get_rect(midleft=(r.x+5, r.centery)))
                pygame.draw.rect(surface, (200,200,200), r, 1, border_radius=4)

class Slider:
    def __init__(self, rect, min_val, max_val, value, font, label, id, sfx=None):
        self.rect = pygame.Rect(rect)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.font = font
        self.label = label
        self.dragging = False
        self.id = id
        self.sfx = sfx
        self._last_sound = 0
        self._cd = 0.1

    def handle_event(self, event, mouse_pos):
        now = time.time()
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel = max(0, min(mouse_pos[0] - self.rect.x, self.rect.width))
            val = int(self.min_val + (rel / self.rect.width) * (self.max_val - self.min_val))
            if val != self.value:
                if now - self._last_sound > self._cd and self.sfx:
                    self.sfx.play_sound("gui_click")
                    self._last_sound = now
                self.value = val
            return self.value
        return None

    def draw(self, surface):
        pygame.draw.rect(surface, (40,40,40,220), self.rect, border_radius=4)
        fill = int((self.value - self.min_val)/(self.max_val - self.min_val)*self.rect.width)
        pygame.draw.rect(surface, (100,200,255), (self.rect.x,self.rect.y,fill,self.rect.height), border_radius=4)
        pygame.draw.rect(surface, (200,200,200), self.rect,1, border_radius=4)
        lbl = self.font.render(f"{self.label}: {self.value}", False, (255,255,255))
        surface.blit(lbl, (self.rect.x+5, self.rect.y-18))

class SettingsHelper:
    def __init__(self, screen_size, settings, helper, instance_manager):
        self.screen_size = screen_size
        self.settings = settings
        self.helper = helper
        self.font = pygame.font.Font(self.settings.font, 13)
        self.active = False
        self.tabs = ["Video","Audio","Controls","Misc"]
        self.active_tab = 0
        self.scroll_offset = 0
        self.scroll_target = 0
        self.scroll_speed = 20
        self.scroll_lerp = 0.2
        self.sfx = instance_manager.sfx_manager
        self.shader_mgr = instance_manager.shader_manager
        self.dirty = False
        self.margin = 20
        self.tab_width = 140
        self.start_y = self.margin+40
        self.elements = {}
        self._init_ui()

    def _init_ui(self):
        sw,sh = self.screen_size
        sx = self.tab_width+self.margin+10
        sy = self.margin+40
        w,h,sp = 140,22,35
        self.elements = {
            0: [
                Dropdown((sx,sy,w,h), self._scan_saves(), os.path.basename(self.settings.save_file).replace('.json',''), self.font, "Save File", "save_file", settings=self.settings, sfx=self.sfx),
                Dropdown((sx,sy+sp,w,h), self._scan_languages(), self.settings.language, self.font, "Language","language",settings=self.settings, sfx=self.sfx),
                Dropdown((sx,sy+2*sp,w,h), self._scan_fonts(), os.path.basename(self.settings.font), self.font, "Font","font",settings=self.settings, sfx=self.sfx),
                Slider((sx,sy+3*sp,w,20),8,40,self.settings.font_hover_size,self.font,"Font Hover Size","font_hover_size",sfx=self.sfx),
            ],
            1: [
                Slider((sx,sy,w,20),0,100,self.settings.music_volume,self.font,"Music Volume","music_volume",sfx=self.sfx),
                Slider((sx,sy+sp,w,20),0,100,self.settings.sfx_volume,self.font,"SFX Volume","sfx_volume",sfx=self.sfx),
                Slider((sx,sy+2*sp,w,20),0,100,self.settings.ambience_volume,self.font,"Ambience Volume","ambience_volume",sfx=self.sfx),
                Slider((sx,sy+3*sp,w,20),0,100,self.settings.npc_volume,self.font,"NPC Volume","npc_volume",sfx=self.sfx),
            ],
            2: [
                Dropdown((sx,sy,w,h),["mouse","controller"],self.settings.input_type,self.font,"Input Type","input_type",settings=self.settings, sfx=self.sfx),
            ],
            3: [
                
            ],
        }

    def get_active_elements(self):
        return self.elements.get(self.active_tab, [])

    def toggle(self):
        self.active = not self.active
        if self.active:
            self._init_ui()

    def update(self):
        self.scroll_offset += (self.scroll_target - self.scroll_offset)*self.scroll_lerp
        if self.dirty:
            self.settings.save()
            self.sfx.update_volume(
                self.settings.sfx_volume/100,
                self.settings.music_volume/100,
                self.settings.ambience_volume/100,
                self.settings.npc_volume/100
            )
            self.dirty=False
        for i,elem in enumerate(self.get_active_elements()):
            elem.rect.y = self.start_y - self.scroll_offset + i*60

    def handle_event(self, event, mouse_pos):
        if not self.active:
            return
        if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
            self.sfx.play_sound("gui_tab")
            self.toggle()
            return
        if event.type==pygame.MOUSEBUTTONDOWN:
            bx,by,h=20,20,36
            for i,_ in enumerate(self.tabs):
                r=pygame.Rect(bx,by+i*(h+10),self.tab_width,h)
                if r.collidepoint(mouse_pos):
                    self.active_tab=i
                    self.scroll_offset=0
                    self.scroll_target=0
                    self.sfx.play_sound("gui_tab")
                    self._init_ui()
            
        if event.type==pygame.MOUSEWHEEL:
            max_sc=max(0,len(self.get_active_elements())*60 - (self.screen_size[1]-self.start_y-40))
            self.scroll_target=max(0,min(self.scroll_target-event.y*self.scroll_speed,max_sc))
            self.sfx.play_sound("gui_scroll")
            return
        for elem in self.get_active_elements():
            res=elem.handle_event(event,mouse_pos)
            if res is not None:
                self.dirty=True
                if hasattr(elem,'selected'):
                    setattr(self.settings, elem.id, elem.selected)
                else:
                    setattr(self.settings, elem.id, elem.value)

    def draw(self, surface):
        if not self.active: return
        ov=pygame.Surface(self.screen_size, pygame.SRCALPHA); ov.fill((0,0,0,180)); surface.blit(ov,(0,0))
        bx,by,h=20,20,36
        for i,tab in enumerate(self.tabs):
            r=pygame.Rect(bx,by+i*(h+10),self.tab_width,h)
            col=(120,120,120) if i==self.active_tab else (80,80,80)
            pygame.draw.rect(surface,col,r,border_radius=4)
            surface.blit(self.font.render(tab,False,(255,255,255)),(r.x+10,r.y+6))
        for elem in self.get_active_elements(): elem.draw(surface)
        for elem in self.get_active_elements():
            if isinstance(elem, Dropdown) and elem.open: elem.draw(surface)
        vis=self.screen_size[1]-self.start_y-40; cnt=len(self.get_active_elements())*60
        if cnt>vis:
            hgt=max(40,int(vis*vis/cnt)); y=self.start_y+int(self.scroll_offset*vis/cnt); x=self.screen_size[0]-30
            pygame.draw.rect(surface,(80,80,80),(x,self.start_y,8,vis),border_radius=4)
            pygame.draw.rect(surface,(180,180,180),(x,y,8,hgt),border_radius=4)
    def _scan_saves(self):
        return [os.path.splitext(f)[0] for f in os.listdir('saves') if f.endswith('.json') and f!='settings.json']

    def _scan_languages(self):
        return [f[:-5] for f in os.listdir(os.path.join('assets','translations')) if f.endswith('.json')]

    def _scan_fonts(self):
        return [f for f in os.listdir('assets') if f.lower().endswith('.ttf')]