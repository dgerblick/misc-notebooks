#version 410

layout(location = 0) in vec3 iPos;
layout(location = 1) in vec3 iNorm;

layout(location = 0) out vec4 oColor;

uniform vec3 lightPos;
uniform vec3 lightAmb;
uniform vec3 lightDiff;
uniform vec3 lightSpec;
uniform vec3 matAmb;
uniform vec3 matDiff;
uniform vec3 matSpec;
uniform float matShine;

void main() {
    vec3 ambient = matAmb * lightAmb;

    vec3 norm = normalize(iNorm);
    vec3 lightDir = normalize(lightPos - iPos);
    float diff = max(dot(lightDir, norm), 0.0);
    vec3 diffuse = diff * matDiff * lightDiff;

    vec3 specular = vec3(0.0);
    if (diff > 0) {
        vec3 reflectDir = reflect(-lightDir, norm);
        vec3 viewDir = normalize(-iPos);
        float spec = pow(max(dot(reflectDir, viewDir), 0.0), matShine);
        specular = spec * lightSpec * matSpec;
    }

    oColor = vec4(ambient + diffuse + specular, 1);
}
