#version 410

uniform mat4 modelView;
uniform mat4 modelViewN;
uniform mat4 proj;

in vec3 pos;
in vec3 norm;
in vec2 uv;

out Vert2Geom {
    vec3 pos;
    vec3 worldPos;
    vec3 norm;
    vec2 uv;
}
outData;

void main() {
    outData.norm = normalize(modelViewN * vec4(norm, 0)).xyz;
    outData.uv = uv;
    vec4 vertPos = modelView * vec4(pos, 1);
    outData.pos = vertPos.xyz / vertPos.w;
    outData.worldPos = pos;
    gl_Position = proj * vertPos;
}
