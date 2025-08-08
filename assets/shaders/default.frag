#version 330 core

// The rendered texture from the previous pass
uniform sampler2D tex;

// The interpolated UVs from your vertex shader
in vec2 v_uv;

// Final color output
out vec4 outColor;

void main() {
    // Just sample the texture and output it unchanged
    outColor = texture(tex, v_uv);
}
