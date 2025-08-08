#version 330 core
uniform sampler2D tex;
in vec2 v_uv; 
out vec4 fragColor;

void main() {
    vec3 c = texture(tex, v_uv).rgb;
    float brightness = max(max(c.r, c.g), c.b);
    vec3 bloom = brightness > 0.8 ? c * 0.5 : vec3(0.0);
    fragColor = vec4(c + bloom, 1.0);
}
