#version 410

layout(triangles) in;
layout(triangle_strip, max_vertices = 3) out;

in Vert2Geom {
    vec3 pos;
    vec3 worldPos;
    vec3 norm;
    vec2 uv;
}
inData[];

out Geom2Frag {
    vec3 pos;
    vec3 norm;
    vec2 uv;
    noperspective vec3 edgeDist;
}
outData;

uniform mat4 view;
uniform mat4 modelViewN;
uniform int useSmoothShading;

void main() {
    // Adapted from OpenGL 4.0 Shading Language Cookbook by David Wolff, Chapter 6 pp.198-204
    vec3 p0 = vec3(view * (gl_in[0].gl_Position / gl_in[0].gl_Position.w));
    vec3 p1 = vec3(view * (gl_in[1].gl_Position / gl_in[1].gl_Position.w));
    vec3 p2 = vec3(view * (gl_in[2].gl_Position / gl_in[2].gl_Position.w));

    float a = length(p1 - p2);
    float b = length(p2 - p0);
    float c = length(p1 - p0);
    float alpha = acos((b * b + c * c - a * a) / (2.0 * b * c));
    float beta = acos((a * a + c * c - b * b) / (2.0 * a * c));
    float ha = abs(c * sin(beta));
    float hb = abs(c * sin(alpha));
    float hc = abs(b * sin(alpha));

    vec3 calcNorm = normalize(modelViewN * vec4(cross(inData[1].worldPos - inData[0].worldPos,
                                                      inData[2].worldPos - inData[0].worldPos),
                                                0))
                        .xyz;

    gl_Position = gl_in[0].gl_Position;
    outData.pos = inData[0].pos;
    outData.norm = useSmoothShading == 1 ? inData[0].norm : calcNorm;
    outData.uv = inData[0].uv;
    outData.edgeDist = vec3(ha, 0, 0);
    EmitVertex();

    gl_Position = gl_in[1].gl_Position;
    outData.pos = inData[1].pos;
    outData.norm = useSmoothShading == 1 ? inData[1].norm : calcNorm;
    outData.uv = inData[1].uv;
    outData.edgeDist = vec3(0, hb, 0);
    EmitVertex();

    gl_Position = gl_in[2].gl_Position;
    outData.pos = inData[2].pos;
    outData.norm = useSmoothShading == 1 ? inData[2].norm : calcNorm;
    outData.uv = inData[2].uv;
    outData.edgeDist = vec3(0, 0, hc);
    EmitVertex();

    EndPrimitive();
}
