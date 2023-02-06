#version 410

in vec2 iPos;

void main() {
    gl_Position = vec4(iPos, 0.0, 1.0);
}
