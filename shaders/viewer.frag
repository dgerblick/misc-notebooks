#version 410

in Geom2Frag {
    vec3 pos;
    vec3 norm;
    vec2 uv;
    noperspective vec3 edgeDist;
}
inData;

layout(location = 0) out vec4 fragColor;

uniform vec3 lightPos;
uniform vec3 lightAmb;
uniform vec3 lightDiff;
uniform vec3 lightSpec;

uniform vec3 matAmb;
uniform vec3 matDiff;
uniform vec3 matSpec;
uniform float matShine;

uniform vec4 wireframeColor;
uniform float wireframeWidth;

uniform sampler2D mainTex;
uniform sampler2D normalMap;

uniform int useWireframe;
uniform int useTextureMap;

void main() {
    vec3 ambient = matAmb * lightAmb;

    vec3 norm = normalize(inData.norm);

    vec3 lightDir = normalize(lightPos - inData.pos);
    float diff = max(dot(lightDir, norm), 0.0);
    vec3 surfaceDiff = matDiff;
    if (useTextureMap == 1) {
        surfaceDiff = texture(mainTex, inData.uv).rgb;
    }
    vec3 diffuse = diff * lightDiff * surfaceDiff;

    vec3 specular = vec3(0.0);
    if (diff > 0) {
        vec3 reflectDir = reflect(-lightDir, norm);
        vec3 viewDir = normalize(-inData.pos);
        float spec = pow(max(dot(reflectDir, viewDir), 0.0), matShine);
        specular = spec * lightSpec * matSpec;
    }

    fragColor = vec4(ambient + diffuse + specular, 1);
    float d = min(inData.edgeDist.x, min(inData.edgeDist.y, inData.edgeDist.z));
    if (useWireframe == 1 && d < wireframeWidth) {
        fragColor = wireframeColor;
    }
}
