# utility/shaderManager.py

import pygame
import moderngl
import numpy as np
import time
from pathlib import Path

class ShaderManager:
    def __init__(self, ctx: moderngl.Context, initial_size: tuple[int,int]):
        self.ctx = ctx
        # 1 quad VBO (x,y) + (u,v)
        verts = np.array([
            -1,  1,  0.0, 0.0,
            -1, -1,  0.0, 1.0,
             1,  1,  1.0, 0.0,
             1, -1,  1.0, 1.0,
        ], dtype='f4')
        self.quad_vbo = ctx.buffer(verts.tobytes())

        self.programs: dict[str, moderngl.Program] = {}
        self.vaos: dict[str, moderngl.VertexArray] = {}
        self.fbo_cache: dict[tuple[int,int], tuple] = {}

        # pre-allocate initial FBO textures
        self._ensure_fbo(initial_size)

    def load(self, name: str, vert_source: str | Path, frag_source: str | Path):
        """Compile and register a shader program from file paths or raw source strings."""
        if isinstance(vert_source, Path) or isinstance(vert_source, str) and Path(vert_source).exists():
            vs = Path(vert_source).read_text(encoding='utf-8')
        else:
            vs = vert_source  # treat as raw GLSL string

        if isinstance(frag_source, Path) or isinstance(frag_source, str) and Path(frag_source).exists():
            fs = Path(frag_source).read_text(encoding='utf-8')
        else:
            fs = frag_source  # treat as raw GLSL string

        prog = self.ctx.program(vertex_shader=vs, fragment_shader=fs)
        self.programs[name] = prog

    def _ensure_fbo(self, size: tuple[int,int]):
        """Make textures+FBO for this resolution if missing."""
        if size in self.fbo_cache:
            return
        w,h = size
        in_tex  = self.ctx.texture((w,h), 4, alignment=1)
        out_tex = self.ctx.texture((w,h), 4, alignment=1)
        for t in (in_tex, out_tex):
            t.filter = (moderngl.NEAREST, moderngl.NEAREST)
            t.swizzle = 'BGRA'
        fbo = self.ctx.framebuffer(color_attachments=[out_tex])
        self.fbo_cache[size] = (in_tex, out_tex, fbo)

    def _get_vao(self, name: str):
        """Lazily create a VAO that feeds quad_vbo into in_vert/in_uv."""
        if name not in self.vaos:
            prog = self.programs[name]
            # Explicitly tell moderngl how the VBO is structured: 2 floats (pos), 2 floats (uv)
            vao = self.ctx.vertex_array(
                prog,
                [(self.quad_vbo, '2f 2f', 'in_vert', 'in_uv')]
            )
            self.vaos[name] = vao
        return self.vaos[name]

    def post_process(self, passes: list[str], scene: pygame.Surface) -> pygame.Surface:
        """
        Run each named pass in order over `scene`, returning the final.
        Internally uses two ping-pong FBOs sized to scene.get_size().
        """
        size = scene.get_size()
        self._ensure_fbo(size)
        in_tex, out_tex, fbo = self.fbo_cache[size]

        # upload initial
        data = pygame.image.tostring(scene, 'RGBA', False)
        in_tex.write(data)
        in_tex.use(location=0)

        current_tex = in_tex
        for name in passes:
            prog = self.programs[name]
            # bind
            prog['tex'].value = 0
            if 'time' in prog:
                prog['time'].value = time.time() % 1000

            # render into out_tex
            fbo.use()
            self.ctx.clear(0.0,0.0,0.0,1.0)
            vao = self._get_vao(name)
            vao.render(mode=moderngl.TRIANGLE_STRIP)

            # swap
            current_tex, out_tex = out_tex, current_tex
            fbo = self.ctx.framebuffer(color_attachments=[out_tex])
            out_tex.use(location=0)

        # readback final
        final_data = current_tex.read()
        return pygame.image.frombuffer(final_data, size, 'RGBA')
