# utility/shaderManager.py

import numpy as np
import pygame
import moderngl
from utility.gl_shader import Shader
import time

class ShaderManager:
    def __init__(self, ctx, initial_size):
        self.ctx = ctx
        self.active_name = None
        self.shaders = {}      # name -> Shader
        self.vaos = {}         # (name, vbo_id) -> VAO

        # single shared quad VBO
        verts = np.array([
    # position    # texcoords (flip X and Y)
    -1.0,  1.0,    1.0, 0.0,   # Top-left
    -1.0, -1.0,    1.0, 1.0,   # Bottom-left
     1.0,  1.0,    0.0, 0.0,   # Top-right
     1.0, -1.0,    0.0, 1.0,   # Bottom-right
], dtype='f4')


        self.quad_vbo = self.ctx.buffer(verts.tobytes())

        # cache: size -> (in_tex, out_tex, fbo)
        self.fbo_cache = {}
        # allocate initial size
        self.update_size(initial_size)

    def add_shader(self, name, vert_path, frag_path):
        with open(vert_path) as f:   vs = f.read()
        with open(frag_path) as f:   fs = f.read()
        self.shaders[name] = Shader(self.ctx, vs, fs)
        if self.active_name is None:
            self.active_name = name

    def set_active(self, name):
        if name in self.shaders:
            self.active_name = name
        else:
            print(f"[ShaderManager] no shader '{name}'")

    def get_vao(self, name):
        key = (name, id(self.quad_vbo))
        if key not in self.vaos:
            prog = self.shaders[name].program
            self.vaos[key] = self.ctx.vertex_array(
                prog,
                [(self.quad_vbo, '2f 2f', 'in_vert', 'in_texcoord')],
            )
        return self.vaos[key]

    def _alloc_textures(self, size, old):
        print(f"making texture for size {size}")
        if old !=None:
            a, b, c = old
            print(a, b, c)

        """Make in/out textures + fbo and stash them in fbo_cache."""
        in_tex = self.ctx.texture(size, 4, alignment=1)
        in_tex.filter  = (moderngl.NEAREST, moderngl.NEAREST)
        in_tex.swizzle = 'BGRA'

        out_tex = self.ctx.texture(size, 4, alignment=1)
        out_tex.filter  = (moderngl.NEAREST, moderngl.NEAREST)
        out_tex.swizzle = 'BGRA'

        fbo = self.ctx.framebuffer(color_attachments=[out_tex])
        self.fbo_cache[size] = (in_tex, out_tex, fbo)

    def update_size(self, size):
        """
        Ensure we have exactly one in/out‐texture + FBO for `size`:

        • If we already had a different size, release it.
        • Allocate only for the new size.
        """
        old = self.fbo_cache.pop(getattr(self, 'current_size', None), None)
        if old:
            in_tex, out_tex, fbo = old
            in_tex.release()
            out_tex.release()
            fbo.release()
            print(f"Released? in_tex valid: {in_tex.glo}, out_tex valid: {out_tex.glo}, fbo valid: {fbo.glo}")
            old = in_tex, out_tex, fbo


        # Now allocate fresh for the new size
        self._alloc_textures(size, old)
        self.current_size = size


    def render(self, surface):
        """
        1) upload surface -> in_tex
        2) bind uniforms
        3) draw quad into FBO
        4) return out_tex
        """
        if not self.active_name:
            return None

        size = surface.get_size()
        # If the surface size changed at runtime, re-alloc:
        if size != getattr(self, 'current_size', None):
            self.update_size(size)





        in_tex, out_tex, fbo = self.fbo_cache[size]

        # 1) upload pixels
        data = pygame.image.tostring(surface, 'RGBA', False)
        in_tex.write(data)
        in_tex.use(location=0)

        # 2) set common uniforms
        prog = self.shaders[self.active_name].program
        if 'tex' in prog:
            prog['tex'] = 0
        if 'time' in prog:
            prog['time'] = time.time() % 1000

        # 3) draw quad
        fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 1.0)
        self.get_vao(self.active_name).render(moderngl.TRIANGLE_STRIP)

        self.ctx.gc()
        # 4) hand back
        return out_tex
