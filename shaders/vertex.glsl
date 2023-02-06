#version 410

uniform mat4 modelView;
uniform mat4 modelViewN;
uniform mat4 proj;

layout(location = 0) in vec3 iPos;
layout(location = 1) in vec3 iNorm;

layout(location = 0) out vec3 oPos;
layout(location = 1) out vec3 oNorm;

void main() {
    oNorm = normalize(modelViewN * vec4(iNorm, 0)).xyz;

    vec4 vertPos = modelView * vec4(iPos, 1);
    oPos = vertPos.xyz / vertPos.w;
    gl_Position = proj * vertPos;
}
