# utility/gl_shader.py


class Shader:
    def __init__(self, ctx, vertex_source, fragment_source):
        self.ctx = ctx
        self.program = self.ctx.program(
            vertex_shader   = vertex_source,
            fragment_shader = fragment_source,
        )
