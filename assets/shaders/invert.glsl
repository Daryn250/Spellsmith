#VERTEX
#version 330

in vec2 in_vert;
in vec2 in_text;
out vec2 v_text;

void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
    v_text = in_text;
}

#FRAGMENT
#version 330

uniform sampler2D tex;
in vec2 v_text;
out vec4 frag_color;

void main() {
    vec4 color = texture(tex, v_text);
    frag_color = vec4(1.0 - color.rgb, color.a);
}
