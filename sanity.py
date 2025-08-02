import pygame
import moderngl
import numpy as np

# Constants
WINDOW_SIZE = (400, 300)

# Init pygame
pygame.init()
screen = pygame.display.set_mode(WINDOW_SIZE, pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption("ModernGL Invert Shader Test")

# Create OpenGL context
ctx = moderngl.create_context()

# Vertex and fragment shaders
vertex_shader = """
#version 330
in vec2 in_vert;
in vec2 in_texcoord;
out vec2 v_texcoord;
void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_texcoord = in_texcoord;
}
"""

fragment_shader = """
#version 330
uniform sampler2D tex;
in vec2 v_texcoord;
out vec4 fragColor;
void main() {
    vec4 color = texture(tex, v_texcoord);
    fragColor = vec4(vec3(1.0) - color.rgb, color.a);  // Invert RGB
}
"""

# Full-screen quad
vertices = np.array([
    -1.0,  1.0, 0.0, 1.0,
    -1.0, -1.0, 0.0, 0.0,
     1.0,  1.0, 1.0, 1.0,
     1.0, -1.0, 1.0, 0.0,
], dtype='f4')

vbo = ctx.buffer(vertices.tobytes())
prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
vao = ctx.vertex_array(prog, [(vbo, '2f 2f', 'in_vert', 'in_texcoord')])

# Create a Pygame surface and draw something
surf = pygame.Surface(WINDOW_SIZE)
surf.fill((50, 100, 200))
pygame.draw.circle(surf, (255, 255, 255), (200, 150), 80)

# Upload to texture
texture = ctx.texture(WINDOW_SIZE, 4, pygame.image.tostring(surf, 'RGBA'))
texture.use()

# Render loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    ctx.clear(0.0, 0.0, 0.0, 1.0)
    vao.render(moderngl.TRIANGLE_STRIP)
    pygame.display.flip()

pygame.quit()
