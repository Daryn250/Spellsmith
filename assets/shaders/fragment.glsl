#version 330 core //version

in vec3 fragmentColor; // The color of the current coordinate/
in vec2 fragmentTexCoord; // The texture coordinate which we will use in the sampler2D lookup.

out vec4 color; // The color we are outputting.

uniform sampler2D imageTexture; // The texture which the shader is provided.

void main() {
    color = texture(imageTexture, fragmentTexCoord); //Peform the above desribed lookup and output it to the color.
}