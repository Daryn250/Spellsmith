# utility/shaderManager.py

import time
import numpy as np
import pygame
import moderngl
from utility.gl_shader import Shader

class ShaderManager:
    def __init__(self, ctx: moderngl.Context, initial_size: tuple[int,int]):
        self.ctx       = ctx
        self.programs  = {}      # name -> Shader (wrapper, has .program)
        self.vaos      = {}      # name -> moderngl.VertexArray
        self.fbo_cache = {}      # size -> (tex_in, tex_out, fbo)
    
        # build one full-screen quad VBO (x,y)+(u,v)
        verts = np.array([
            -1.0,  1.0,  0.0, 1.0,
            -1.0, -1.0,  0.0, 0.0,
             1.0,  1.0,  1.0, 1.0,
             1.0, -1.0,  1.0, 0.0,
        ], dtype='f4')
        self.quad_vbo = ctx.buffer(verts.tobytes())
    
        # prep FBO for initial size
        self._ensure_fbo(initial_size)
    
    def add_shader(self, name: str, vert_path: str, frag_path: str):
        vs = open(vert_path).read()
        fs = open(frag_path).read()
        shader = Shader(self.ctx, vs, fs)
        self.programs[name] = shader
    
    def _get_vao(self, prog_name: str) -> moderngl.VertexArray:
        if prog_name not in self.vaos:
            prog = self.programs[prog_name].program
            # attribute locations: 0=in_vert, 1=in_uv
            self.vaos[prog_name] = self.ctx.vertex_array(
                prog,
                [(self.quad_vbo, '2f 2f', 0, 1)]
            )
        return self.vaos[prog_name]
    
    def _ensure_fbo(self, size: tuple[int,int]):
        if size in self.fbo_cache:
            return
        w, h = size
        tex_in  = self.ctx.texture((w, h), 4, alignment=1)
        tex_out = self.ctx.texture((w, h), 4, alignment=1)
        for t in (tex_in, tex_out):
            t.filter  = (moderngl.NEAREST, moderngl.NEAREST)
            t.swizzle = 'BGRA'
        fbo = self.ctx.framebuffer(color_attachments=[tex_out])
        self.fbo_cache[size] = (tex_in, tex_out, fbo)
    
    def post_process(self,
                     passes: list[str],
                     source_surf: pygame.Surface):
        size = source_surf.get_size()
        tex_in, tex_out, fbo = self.fbo_cache[size]
    
        # 1) upload source into tex_in
        raw = pygame.image.tostring(source_surf, 'RGBA', False)
        tex_in.write(raw, viewport=(0, 0, *size))
        tex_in.use(location=0)
    
        ping, pong = tex_in, tex_out
    
        # 2) ping-pong each pass
        for name in passes:
            prog = self.programs[name].program
            if 'tex'  in prog: prog['tex']  = 0
            if 'time' in prog: prog['time'] = time.time() % 1000
    
            # draw ping → pong
            fbo.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)
            self._get_vao(name).render(moderngl.TRIANGLE_STRIP)
    
            # swap
            ping, pong = pong, ping
            fbo = self.ctx.framebuffer(color_attachments=[pong])
            pong.use(location=0)
    
            # … after your ping–pong loop …

            # 3) final draw: ping now holds the result of the last effect
            self.ctx.screen.use()
            self.ctx.clear(0.0, 0.0, 0.0, 1.0)

            # bind the inverted texture
            ping.use(location=0)

            # draw with the *passthrough* shader, NOT the effect shader
            self._get_vao("default") \
                .render(moderngl.TRIANGLE_STRIP)

