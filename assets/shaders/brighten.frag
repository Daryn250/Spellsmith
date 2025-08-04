#version 330
uniform sampler2D tex;
in vec2 v_uv;
out vec4 outColor;
void main() {
    vec4 c = texture(tex, v_uv);
    outColor = vec4(min(c.rgb + 0.2, vec3(1.0)), c.a);
}
