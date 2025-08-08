# utility/gl_shader.py

class Shader:
    def __init__(self, ctx, vertex_source, fragment_source):
        """
        Wraps a ModernGL program. You pass in raw GLSL source strings
        for the vertex and fragment stages.
        """
        self.ctx = ctx
        self.program = self.ctx.program(
            vertex_shader   = PASSTHROUGH_VERT,
            fragment_shader = INVERT_FRAG,
        )


# ------------------------------------------------------------------
# Built-in GLSL snippets

# A simple pass-through vertex shader.  It takes a 2D position + UV
# and forwards the UV to the fragment stage.
PASSTHROUGH_VERT = """#version 330 core
layout(location = 0) in vec2 in_vert;
layout(location = 1) in vec2 in_uv;
out vec2 v_uv;
void main() {
    v_uv = in_uv;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
"""

# A minimal invert-colors fragment shader.  Samples `tex` at v_uv,
# then outputs (1−rgb, a).
INVERT_FRAG = """#version 330 core
uniform sampler2D tex;
in vec2 v_uv;
out vec4 outColor;
void main() {
    vec4 c = texture(tex, v_uv);
    outColor = vec4(vec3(1.0) - c.rgb, c.a);
}
"""
