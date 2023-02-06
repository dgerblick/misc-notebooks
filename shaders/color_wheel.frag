#version 410
#define PI 3.1415926538

out vec4 oColor;

uniform vec2 screenSize;

void main() {
    vec2 pos = 2.0 * gl_FragCoord.xy / screenSize - 1.0;
    float c = clamp(length(pos), 0, 1);
    float hue = atan(pos.y, pos.x) + PI;
    float h = hue / (PI / 3);
    float x = c * (1 - abs(mod(h, 2) - 1));

    vec3 rgb;
    if (0 <= h && h < 1)
        rgb = vec3(c, x, 0);
    else if (1 <= h && h < 2)
        rgb = vec3(x, c, 0);
    else if (2 <= h && h < 3)
        rgb = vec3(0, c, x);
    else if (3 <= h && h < 4)
        rgb = vec3(0, x, c);
    else if (4 <= h && h < 5)
        rgb = vec3(x, 0, c);
    else if (5 <= h && h < 6)
        rgb = vec3(c, 0, x);

    oColor = vec4(rgb, 1);
}
