#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fbxMesh —— 纯 Python 解析 FBX(二进制 7.x)几何，供自写 OpenGL 预览使用。

只用标准库(struct/zlib/array/math)，**不依赖** PySide2 / numpy / Autodesk FBX SDK，
全程在内存里解析，**不向 Maya 场景添加任何东西**。这是 AssetsManager「资产 FBX 三维
预览」的取数层(见 widgets/previewGLWidget.py)。

read(path) -> MeshData：
  - 抽取所有 Mesh 几何的顶点/法线，按其所属 Model 的局部变换(Lcl TRS + Geometric*)
    经 Connections 放置，三角化后合并为一份交错缓冲(position+normal, float32)。
  - 解析失败 / 不支持(ASCII FBX、NURBS 等)抛 FbxParseError；上层据此回退显示 icon。

已知简化(M1)：
  - 只读二进制 FBX(Maya FBXExport 默认即二进制)；ASCII FBX 不支持。
  - 旋转按 Maya 默认 XYZ 顺序；暂不处理 PreRotation/PostRotation/旋转轴心(M2)。
  - UV/贴图暂不解析(M1 纯着色)；法线缺失时按面法线平铺(flat)。
  - 假设小端(Windows/Mac x64/ARM 均小端)。
"""

import struct
import zlib
import array
import math


class FbxParseError(Exception):
    pass


# --------------------------------------------------------------------------- 节点树
class _Node(object):
    __slots__ = ("name", "props", "children")

    def __init__(self, name):
        self.name = name
        self.props = []
        self.children = []

    def first(self, name):
        for c in self.children:
            if c.name == name:
                return c
        return None


_HEADER = b"Kaydara FBX Binary  \x00"


def _read_property(data, pos):
    tc = chr(data[pos])
    pos += 1
    if tc == 'Y':
        return struct.unpack_from("<h", data, pos)[0], pos + 2
    if tc == 'C':
        return (data[pos] != 0), pos + 1
    if tc == 'I':
        return struct.unpack_from("<i", data, pos)[0], pos + 4
    if tc == 'F':
        return struct.unpack_from("<f", data, pos)[0], pos + 4
    if tc == 'D':
        return struct.unpack_from("<d", data, pos)[0], pos + 8
    if tc == 'L':
        return struct.unpack_from("<q", data, pos)[0], pos + 8
    if tc in ('f', 'd', 'l', 'i', 'b'):
        _array_len, encoding, comp_len = struct.unpack_from("<III", data, pos)
        pos += 12
        raw = data[pos:pos + comp_len]
        pos += comp_len
        if encoding == 1:
            raw = zlib.decompress(raw)
        fmt = {'f': 'f', 'd': 'd', 'l': 'q', 'i': 'i', 'b': 'b'}[tc]
        arr = array.array(fmt)
        try:
            arr.frombytes(raw)
        except AttributeError:  # py2 名为 fromstring，本仓 py3.7 用不到，保险
            arr.fromstring(raw)
        return arr, pos
    if tc == 'S' or tc == 'R':
        length = struct.unpack_from("<I", data, pos)[0]
        pos += 4
        v = data[pos:pos + length]
        pos += length
        if tc == 'S':
            v = v.decode("utf-8", "replace")
        return v, pos
    raise FbxParseError("unknown property type %r at %d" % (tc, pos - 1))


def _read_node(data, pos, use64):
    if use64:
        end_offset, num_props, _plen = struct.unpack_from("<QQQ", data, pos)
        pos += 24
    else:
        end_offset, num_props, _plen = struct.unpack_from("<III", data, pos)
        pos += 12
    name_len = data[pos]
    pos += 1
    if end_offset == 0:
        return None, pos  # 空记录(列表结束哨兵)
    name = data[pos:pos + name_len].decode("utf-8", "replace")
    pos += name_len
    node = _Node(name)
    for _ in range(num_props):
        val, pos = _read_property(data, pos)
        node.props.append(val)
    # 子节点：从当前 pos 到 end_offset
    while pos < end_offset:
        child, pos = _read_node(data, pos, use64)
        if child is None:
            break
        node.children.append(child)
    return node, end_offset


def _parse_tree(data):
    if data[:len(_HEADER)] != _HEADER:
        raise FbxParseError("not a binary FBX (header mismatch)")
    version = struct.unpack_from("<I", data, 23)[0]
    use64 = version >= 7500
    pos = 27
    root = _Node("__root__")
    n = len(data)
    while pos < n:
        node, pos = _read_node(data, pos, use64)
        if node is None:
            break
        root.children.append(node)
    return root


# --------------------------------------------------------------------------- 矩阵(行主序 16)
def _identity():
    return [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


def _matmul(a, b):
    r = [0.0] * 16
    for i in range(4):
        ai0, ai1, ai2, ai3 = a[i * 4], a[i * 4 + 1], a[i * 4 + 2], a[i * 4 + 3]
        for j in range(4):
            r[i * 4 + j] = ai0 * b[j] + ai1 * b[4 + j] + ai2 * b[8 + j] + ai3 * b[12 + j]
    return r


def _translation(t):
    m = _identity()
    m[3], m[7], m[11] = t[0], t[1], t[2]
    return m


def _scale(s):
    return [s[0], 0, 0, 0, 0, s[1], 0, 0, 0, 0, s[2], 0, 0, 0, 0, 1.0]


def _rotx(d):
    a = math.radians(d); c = math.cos(a); s = math.sin(a)
    return [1.0, 0, 0, 0, 0, c, -s, 0, 0, s, c, 0, 0, 0, 0, 1.0]


def _roty(d):
    a = math.radians(d); c = math.cos(a); s = math.sin(a)
    return [c, 0, s, 0, 0, 1.0, 0, 0, -s, 0, c, 0, 0, 0, 0, 1.0]


def _rotz(d):
    a = math.radians(d); c = math.cos(a); s = math.sin(a)
    return [c, -s, 0, 0, s, c, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]


def _euler_xyz(r):
    # Maya 默认旋转顺序 XYZ：先绕 X，列向量约定下合成矩阵 = Rz * Ry * Rx
    return _matmul(_rotz(r[2]), _matmul(_roty(r[1]), _rotx(r[0])))


def _local_matrix(t, r, s):
    return _matmul(_translation(t), _matmul(_euler_xyz(r), _scale(s)))


def _xform_point(m, x, y, z):
    return (m[0] * x + m[1] * y + m[2] * z + m[3],
            m[4] * x + m[5] * y + m[6] * z + m[7],
            m[8] * x + m[9] * y + m[10] * z + m[11])


def _xform_dir(m, x, y, z):
    return (m[0] * x + m[1] * y + m[2] * z,
            m[4] * x + m[5] * y + m[6] * z,
            m[8] * x + m[9] * y + m[10] * z)


# --------------------------------------------------------------------------- 变换装配
def _p70(model, name):
    """从 Model 的 Properties70 取某属性的数值尾部(如 Lcl Translation -> [x,y,z])。"""
    p = model.first("Properties70")
    if not p:
        return None
    for c in p.children:
        if c.name == "P" and c.props and c.props[0] == name:
            nums = [x for x in c.props[1:]
                    if isinstance(x, (int, float)) and not isinstance(x, bool)]
            return nums if nums else None
    return None


def _model_local(model):
    t = _p70(model, "Lcl Translation") or [0.0, 0.0, 0.0]
    r = _p70(model, "Lcl Rotation") or [0.0, 0.0, 0.0]
    s = _p70(model, "Lcl Scaling") or [1.0, 1.0, 1.0]
    return _local_matrix(t[:3], (r + [0, 0, 0])[:3], (s + [1, 1, 1])[:3])


def _geometric(model):
    t = _p70(model, "GeometricTranslation") or [0.0, 0.0, 0.0]
    r = _p70(model, "GeometricRotation") or [0.0, 0.0, 0.0]
    s = _p70(model, "GeometricScaling") or [1.0, 1.0, 1.0]
    if t[:3] == [0, 0, 0] and r[:3] == [0, 0, 0] and s[:3] == [1, 1, 1]:
        return None
    return _local_matrix(t[:3], (r + [0, 0, 0])[:3], (s + [1, 1, 1])[:3])


def _build_transforms(root):
    """返回 geometryId -> 世界变换矩阵(已含 Geometric)；解析不出则空表(全用单位阵)。"""
    objects = root.first("Objects")
    connections = root.first("Connections")
    if not objects or not connections:
        return {}

    models = {}        # id -> Model 节点
    geom_ids = set()   # 所有 Geometry 的 id
    for c in objects.children:
        if not c.props:
            continue
        oid = c.props[0]
        if not isinstance(oid, int):
            continue
        if c.name == "Model":
            models[oid] = c
        elif c.name == "Geometry":
            geom_ids.add(oid)

    geom_to_model = {}
    model_parent = {}
    for c in connections.children:
        if c.name != "C" or len(c.props) < 3 or c.props[0] != "OO":
            continue
        child_id, parent_id = c.props[1], c.props[2]
        if child_id in geom_ids and parent_id in models:
            geom_to_model[child_id] = parent_id
        elif child_id in models and parent_id in models:
            model_parent[child_id] = parent_id

    local_cache = {}

    def model_local(mid):
        if mid not in local_cache:
            local_cache[mid] = _model_local(models[mid])
        return local_cache[mid]

    world_cache = {}

    def model_world(mid, stack):
        if mid in world_cache:
            return world_cache[mid]
        if mid in stack:  # 防环
            return _identity()
        stack.add(mid)
        loc = model_local(mid)
        pid = model_parent.get(mid)
        w = _matmul(model_world(pid, stack), loc) if (pid in models) else loc
        stack.discard(mid)
        world_cache[mid] = w
        return w

    out = {}
    for gid, mid in geom_to_model.items():
        try:
            w = model_world(mid, set())
            geo = _geometric(models[mid])
            out[gid] = _matmul(w, geo) if geo else w
        except Exception:
            out[gid] = _identity()
    return out


# --------------------------------------------------------------------------- 法线
def _normal_indexer(geom):
    """返回 (normals_array, index(cpi, pvc)->base_or_None) 或 None。"""
    layer = geom.first("LayerElementNormal")
    if not layer:
        return None
    narr = layer.first("Normals")
    if not narr or not narr.props:
        return None
    normals = narr.props[0]

    mit = layer.first("MappingInformationType")
    rit = layer.first("ReferenceInformationType")
    nmap = mit.props[0] if (mit and mit.props) else "ByPolygonVertex"
    nref = rit.props[0] if (rit and rit.props) else "Direct"

    nidx = None
    if not nref.startswith("Direct"):
        ni = layer.first("NormalsIndex") or layer.first("NormalIndex")
        nidx = ni.props[0] if (ni and ni.props) else None

    by_vertex = nmap.startswith("ByVert")  # ByVertex / ByVertice

    def index(cpi, pvc):
        key = cpi if by_vertex else pvc
        if nidx is not None:
            if key < 0 or key >= len(nidx):
                return None
            key = nidx[key]
        base = key * 3
        if base < 0 or base + 2 >= len(normals):
            return None
        return base

    return normals, index


# --------------------------------------------------------------------------- MeshData
class MeshData(object):
    __slots__ = ("interleaved", "vertex_count", "bbox_min", "bbox_max")

    def __init__(self, interleaved, vertex_count, bbox_min, bbox_max):
        self.interleaved = interleaved      # bytes: [px,py,pz,nx,ny,nz] * vertex_count (float32)
        self.vertex_count = vertex_count    # 三角形角点数(= 三角形数 * 3)，用 glDrawArrays
        self.bbox_min = bbox_min            # (x,y,z)
        self.bbox_max = bbox_max

    def center_radius(self):
        cx = (self.bbox_min[0] + self.bbox_max[0]) * 0.5
        cy = (self.bbox_min[1] + self.bbox_max[1]) * 0.5
        cz = (self.bbox_min[2] + self.bbox_max[2]) * 0.5
        dx = self.bbox_max[0] - self.bbox_min[0]
        dy = self.bbox_max[1] - self.bbox_min[1]
        dz = self.bbox_max[2] - self.bbox_min[2]
        radius = 0.5 * math.sqrt(dx * dx + dy * dy + dz * dz)
        if radius <= 1e-6:
            radius = 1.0
        return (cx, cy, cz), radius


def _normalize(x, y, z):
    n = math.sqrt(x * x + y * y + z * z)
    if n < 1e-12:
        return 0.0, 0.0, 1.0
    return x / n, y / n, z / n


def read(path):
    """解析 FBX，返回 MeshData。失败抛 FbxParseError。"""
    try:
        with open(path, "rb") as f:
            data = f.read()
    except (IOError, OSError) as e:
        raise FbxParseError("cannot read file: %s" % e)

    if not data:
        raise FbxParseError("empty file")

    root = _parse_tree(data)
    objects = root.first("Objects")
    if not objects:
        raise FbxParseError("no Objects section")

    xforms = _build_transforms(root)

    out = array.array('f')
    inf = float("inf")
    bmin_x = bmin_y = bmin_z = inf
    max_x = max_y = max_z = -inf
    corners = 0

    for geom in objects.children:
        if geom.name != "Geometry":
            continue
        vnode = geom.first("Vertices")
        pnode = geom.first("PolygonVertexIndex")
        if not vnode or not vnode.props or not pnode or not pnode.props:
            continue
        verts = vnode.props[0]   # double array, xyz...
        pvi = pnode.props[0]     # int array
        if len(verts) < 9 or len(pvi) < 3:
            continue

        gid = geom.props[0] if geom.props and isinstance(geom.props[0], int) else None
        M = xforms.get(gid)

        nrm = _normal_indexer(geom)
        normals = nrm[0] if nrm else None
        nindex = nrm[1] if nrm else None

        # 控制点世界坐标缓存(同一 geometry 内复用)
        pcache = {}

        def world_pos(cpi):
            p = pcache.get(cpi)
            if p is None:
                b = cpi * 3
                x, y, z = verts[b], verts[b + 1], verts[b + 2]
                p = _xform_point(M, x, y, z) if M else (x, y, z)
                pcache[cpi] = p
            return p

        def corner_normal(cpi, pvc):
            if normals is None:
                return None
            base = nindex(cpi, pvc)
            if base is None:
                return None
            nx, ny, nz = normals[base], normals[base + 1], normals[base + 2]
            if M:
                nx, ny, nz = _xform_dir(M, nx, ny, nz)
            return _normalize(nx, ny, nz)

        # 收集一个多边形(角点 = (控制点索引, polygon-vertex 计数))，遇负值收尾后扇形三角化
        poly = []
        for pvc in range(len(pvi)):
            idx = pvi[pvc]
            if idx < 0:
                poly.append((~idx, pvc))
                # 三角化
                for k in range(1, len(poly) - 1):
                    tri = (poly[0], poly[k], poly[k + 1])
                    p0 = world_pos(tri[0][0])
                    p1 = world_pos(tri[1][0])
                    p2 = world_pos(tri[2][0])

                    n0 = corner_normal(tri[0][0], tri[0][1])
                    n1 = corner_normal(tri[1][0], tri[1][1])
                    n2 = corner_normal(tri[2][0], tri[2][1])
                    if n0 is None or n1 is None or n2 is None:
                        # 面法线(flat)
                        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
                        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
                        fn = _normalize(uy * vz - uz * vy,
                                        uz * vx - ux * vz,
                                        ux * vy - uy * vx)
                        n0 = n1 = n2 = fn

                    for (px, py, pz), (nx, ny, nz) in ((p0, n0), (p1, n1), (p2, n2)):
                        out.append(px); out.append(py); out.append(pz)
                        out.append(nx); out.append(ny); out.append(nz)
                        if px < bmin_x: bmin_x = px
                        if py < bmin_y: bmin_y = py
                        if pz < bmin_z: bmin_z = pz
                        if px > max_x: max_x = px
                        if py > max_y: max_y = py
                        if pz > max_z: max_z = pz
                    corners += 3
                poly = []
            else:
                poly.append((idx, pvc))

    if corners == 0:
        raise FbxParseError("no triangles extracted")

    return MeshData(out.tobytes(), corners,
                    (bmin_x, bmin_y, bmin_z),
                    (max_x, max_y, max_z))
