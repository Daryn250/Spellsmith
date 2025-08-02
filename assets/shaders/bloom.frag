#version 330 core
uniform sampler2D tex;
in vec2 v_texcoord;
out vec4 fragColor;

// sample offsets
const float offset = 1.0 / 300.0;  

void main() {
    vec3 col = texture(tex, v_texcoord).rgb;

    // Bright-pass: keep only bright parts
    float bright = max(max(col.r, col.g), col.b) - 0.7;
    vec3 brightCol = max(vec3(0.0), col - vec3(0.7));

    // simple blur: sample neighbors
    vec3 blur = vec3(0.0);
    blur += texture(tex, v_texcoord + vec2(-offset, 0)).rgb;
    blur += texture(tex, v_texcoord + vec2( offset, 0)).rgb;
    blur += texture(tex, v_texcoord + vec2(0, -offset)).rgb;
    blur += texture(tex, v_texcoord + vec2(0,  offset)).rgb;
    blur *= 0.25;  // average

    // composite: original + blurred bright areas
    fragColor = vec4(col + brightCol * blur * 2.0, 1.0);
}
