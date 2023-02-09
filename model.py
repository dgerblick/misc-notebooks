import glm
import struct
import numpy as np
from moderngl import Context
from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Vert:
    pos: glm.vec3
    norm: glm.vec3 = glm.vec3(0)
    uv: glm.vec2 = glm.vec2(0)


@dataclass
class Tri:
    v0: Vert
    v1: Vert
    v2: Vert

    def area(self):
        n = np.cross(self.v1.pos - self.v0.pos, self.v2.pos - self.v0.pos)
        return 0.5 * np.sqrt(n.dot(n))

    def norm(self):
        n = np.cross(self.v1.pos - self.v0.pos, self.v2.pos - self.v0.pos)
        return n / np.sqrt(n.dot(n))


class Model:
    verts_dict = {}
    verts = []
    tris = []

    def add_vert(self, v: Vert):
        self.verts_dict[v] = len(self.verts)
        self.verts.append(v)

    def vert(self, v: Vert) -> int:
        if v not in self.verts_dict:
            self.add_vert(v)
        return self.verts_dict[v]

    def add_tri(self, arg0: Tri | int, arg1: int = -1, arg2: int = -1):
        if isinstance(arg0, Tri):
            self.tris.append(
                [self.vert(arg0.v0), self.vert(arg0.v1), self.vert(arg0.v2)])
        elif isinstance(arg0, int) and arg1 >= 0 and arg2 >= 0:
            self.tris.append([arg0, arg1, arg2])

    def get_tri(self, idx: int):
        t = self.tris[idx]
        return Tri(self.verts[t[0]], self.verts[t[1]], self.verts[t[2]])

    def get_tris(self):
        for t in self.tris:
            yield Tri(self.verts[t[0]], self.verts[t[1]], self.verts[t[2]])

    def buffers(self, ctx: Context):
        vbo_pos = ctx.buffer(
            np.array([v.pos for v in self.verts]).astype('f4').tobytes())
        vbo_norm = ctx.buffer(
            np.array([v.norm for v in self.verts]).astype('f4').tobytes())
        vbo_uv = ctx.buffer(
            np.array([v.uv for v in self.verts]).astype('f4').tobytes())
        ibo = ctx.buffer(np.array(self.tris).astype('u4').tobytes())
        return vbo_pos, vbo_norm, vbo_uv, ibo

    def to_obj(self, filename):
        with open(filename, 'w') as of:
            for v in self.verts:
                of.write(f'v {v.pos[0]} {v.pos[1]} {v.pos[2]}\n')
                of.write(f'vn {v.norm[0]} {v.norm[1]} {v.norm[2]}\n')
                of.write(f'vt {v.uv[0]} {v.uv[1]}\n')
            for v0, v1, v2 in self.tris:
                v0, v1, v2 = v0 + 1, v1 + 1, v2 + 1
                of.write(f'f {v0}/{v0}/{v0} {v1}/{v1}/{v1} {v2}/{v2}/{v2}\n')

    def to_stl(self, filename):
        with open(filename, 'wb') as of:
            of.write(struct.pack('<80sI', b'\0' * 80, len(self.tris)))
            for t in self.get_tris():
                of.write(struct.pack('<12fH', *t.norm(), *
                         t.v0.pos, *t.v1.pos, *t.v2.pos, 0))
