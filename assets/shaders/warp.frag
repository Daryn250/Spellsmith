#version 330 core
uniform sampler2D tex;
uniform float time;
in vec2 v_texcoord;
out vec4 fragColor;

void main() {
    float wave = sin((v_texcoord.y + time * 0.5) * 20.0) * 0.005;
    vec2 uv = v_texcoord + vec2(wave, 0.0);
    fragColor = texture(tex, uv);
}
