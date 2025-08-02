#version 330
uniform sampler2D tex;
in vec2 v_texcoord;
out vec4 fragColor;
void main() {
    vec4 c = texture(tex, v_texcoord);
    // for test, output c directly:
    fragColor = c;
}