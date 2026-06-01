#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fbxMesh —— 纯 Python 解析 FBX(二进制 7.x)几何 + 材质,供自写 OpenGL 预览使用。

只用标准库(os/struct/zlib/array/math)，**不依赖** PySide2 / numpy / Autodesk FBX SDK，
全程在内存里解析，**不向 Maya 场景添加任何东西**。这是 AssetsManager「资产 FBX 三维
预览」的取数层(见 widgets/previewGLWidget.py)。

read(path) -> MeshData：
  - 抽取所有 Mesh 几何的顶点/法线/UV，按其所属 Model 的局部变换(Lcl TRS + Geometric*)
    经 Connections 放置，三角化后**按材质分组**为若干子网格(submesh)，每个子网格带固有色
    (DiffuseColor)与可选漫反射贴图路径。合并为一份交错缓冲(pos3+nrm3+uv2, float32)。
  - 贴图路径在此解析(候选:FBX 内记录路径 / fbx 同目录 / {资产根}/Texture|Textures|Images/)。
    本模块保持 Qt-free，只回传**文件路径**;QImage 由上层在 worker 线程加载、GUI 线程上传。
  - 解析失败 / 不支持(ASCII FBX、NURBS 等)抛 FbxParseError；上层据此回退显示 icon。

已知简化：
  - 只读二进制 FBX(Maya FBXExport 默认即二进制)；ASCII FBX 不支持。
  - 旋转按 Maya 默认 XYZ 顺序；暂不处理 PreRotation/PostRotation/旋转轴心。
  - 非索引(每三角形 3 个角点)输出 —— 解析快、避免逐角点字典去重的开销(大网格友好)。
  - 假设小端(Windows/Mac x64/ARM 均小端)。
"""

import os
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
        arr.frombytes(raw)
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
    # Maya 默认旋转顺序 XYZ：列向量约定下合成矩阵 = Rz * Ry * Rx
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


# --------------------------------------------------------------------------- Properties70
def _p70(node, name):
    """从某节点的 Properties70 取某属性的数值尾部(如 Lcl Translation -> [x,y,z])。"""
    p = node.first("Properties70")
    if not p:
        return None
    for c in p.children:
        if c.name == "P" and c.props and c.props[0] == name:
            nums = [x for x in c.props[1:]
                    if isinstance(x, (int, float)) and not isinstance(x, bool)]
            return nums if nums else None
    return None


# --------------------------------------------------------------------------- 变换装配
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


def _scene_ids(root):
    """收集 Objects 里各类对象 id,以及 Connections 的 OO 关系。"""
    objects = root.first("Objects")
    connections = root.first("Connections")
    models, geom_ids, mat_ids = {}, set(), set()
    if objects:
        for c in objects.children:
            if not c.props or not isinstance(c.props[0], int):
                continue
            oid = c.props[0]
            if c.name == "Model":
                models[oid] = c
            elif c.name == "Geometry":
                geom_ids.add(oid)
            elif c.name == "Material":
                mat_ids.add(oid)
    oo = []  # (child, parent)
    if connections:
        for c in connections.children:
            if c.name == "C" and len(c.props) >= 3 and c.props[0] == "OO":
                oo.append((c.props[1], c.props[2]))
    return models, geom_ids, mat_ids, oo


def _build_transforms(root):
    """geometryId -> 世界变换矩阵(含 Geometric);解析不出则空表(全用单位阵)。"""
    models, geom_ids, _mat_ids, oo = _scene_ids(root)
    if not models or not oo:
        return {}

    geom_to_model, model_parent = {}, {}
    for child, parent in oo:
        if child in geom_ids and parent in models:
            geom_to_model[child] = parent
        elif child in models and parent in models:
            model_parent[child] = parent

    local_cache, world_cache = {}, {}

    def model_world(mid, stack):
        if mid in world_cache:
            return world_cache[mid]
        if mid in stack:
            return _identity()
        stack.add(mid)
        loc = local_cache.get(mid)
        if loc is None:
            loc = local_cache[mid] = _model_local(models[mid])
        pid = model_parent.get(mid)
        w = _matmul(model_world(pid, stack), loc) if pid in models else loc
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


# --------------------------------------------------------------------------- 材质 / 贴图
def _texture_filenames(tex_node):
    out = []
    for key in ("RelativeFilename", "FileName", "Filename"):
        n = tex_node.first(key)
        if n and n.props and isinstance(n.props[0], str) and n.props[0]:
            out.append(n.props[0])
    return out


def _resolve_texture(stored_list, fbx_path):
    if not stored_list:
        return None
    fbx_dir = os.path.dirname(fbx_path)
    root = os.path.dirname(fbx_dir)  # 资产根(fbx 在 .../<asset>/FBX/)
    cands = []
    for stored in stored_list:
        s = stored.replace("\\", "/")
        base = os.path.basename(s)
        cands += [s,
                  os.path.join(fbx_dir, s),
                  os.path.join(fbx_dir, base),
                  os.path.join(root, "Texture", base),
                  os.path.join(root, "Textures", base),
                  os.path.join(root, "Images", base)]
    for c in cands:
        try:
            if c and os.path.isfile(c):
                return c.replace("\\", "/")
        except Exception:
            pass
    return None


def _material_color(mat_node):
    c = _p70(mat_node, "DiffuseColor") or _p70(mat_node, "Diffuse")
    if c and len(c) >= 3:
        return (float(c[0]), float(c[1]), float(c[2]))
    return None


def _parse_materials(root, fbx_path):
    """{materialId: {'color':(r,g,b)|None, 'texture':path|None}}。"""
    objects = root.first("Objects")
    connections = root.first("Connections")
    if not objects:
        return {}
    textures, mats = {}, {}
    for c in objects.children:
        if not c.props or not isinstance(c.props[0], int):
            continue
        oid = c.props[0]
        if c.name == "Material":
            mats[oid] = c
        elif c.name == "Texture":
            fns = _texture_filenames(c)
            if fns:
                textures[oid] = fns
    mat_tex = {}  # materialId -> [filenames]
    if connections:
        for c in connections.children:
            if c.name != "C" or len(c.props) < 3 or c.props[0] != "OP":
                continue
            child_id, parent_id = c.props[1], c.props[2]
            prop = str(c.props[3]) if len(c.props) > 3 else ""
            if child_id in textures and parent_id in mats and "Diffuse" in prop:
                mat_tex[parent_id] = textures[child_id]
    out = {}
    for mid, node in mats.items():
        out[mid] = {
            "color": _material_color(node),
            "texture": _resolve_texture(mat_tex.get(mid), fbx_path),
        }
    return out


def _geom_material_lists(root):
    """{geomId: [materialId,...]}(连接顺序;LayerElementMaterial 的索引指向它)。"""
    models, geom_ids, mat_ids, oo = _scene_ids(root)
    if not mat_ids or not oo:
        return {}
    model_mats, geom_to_model = {}, {}
    for child, parent in oo:
        if child in mat_ids and parent in models:
            model_mats.setdefault(parent, []).append(child)
        elif child in geom_ids and parent in models:
            geom_to_model[child] = parent
    out = {}
    for gid, mid in geom_to_model.items():
        out[gid] = model_mats.get(mid, [])
    return out


# --------------------------------------------------------------------------- 每角点索引器
def _layer_indexer(geom, layer_name, data_name, idx_name, comp, default_ref):
    layer = geom.first(layer_name)
    if not layer:
        return None
    darr = layer.first(data_name)
    if not darr or not darr.props:
        return None
    data = darr.props[0]
    mit = layer.first("MappingInformationType")
    rit = layer.first("ReferenceInformationType")
    mapping = mit.props[0] if (mit and mit.props) else "ByPolygonVertex"
    ref = rit.props[0] if (rit and rit.props) else default_ref
    didx = None
    if not ref.startswith("Direct"):
        ii = layer.first(idx_name)
        didx = ii.props[0] if (ii and ii.props) else None
    by_vertex = mapping.startswith("ByVert") or mapping.startswith("ByControl")

    def index(cpi, pvc):
        key = cpi if by_vertex else pvc
        if didx is not None:
            if key < 0 or key >= len(didx):
                return None
            key = didx[key]
        base = key * comp
        if base < 0 or base + comp - 1 >= len(data):
            return None
        return base

    return data, index


def _normal_indexer(geom):
    return _layer_indexer(geom, "LayerElementNormal", "Normals", "NormalsIndex", 3, "Direct")


def _uv_indexer(geom):
    return _layer_indexer(geom, "LayerElementUV", "UV", "UVIndex", 2, "IndexToDirect")


def _material_layer(geom):
    """返回 (mapping, materials_int_array) 或 None。"""
    layer = geom.first("LayerElementMaterial")
    if not layer:
        return None
    marr = layer.first("Materials")
    mit = layer.first("MappingInformationType")
    mapping = mit.props[0] if (mit and mit.props) else "AllSame"
    arr = marr.props[0] if (marr and marr.props) else None
    return mapping, arr


# --------------------------------------------------------------------------- MeshData
_DEFAULT_COLOR = (0.78, 0.78, 0.80)
_FPV = 8  # floats per vertex: pos3 + nrm3 + uv2


class Submesh(object):
    __slots__ = ("first", "count", "color", "texture")

    def __init__(self, first, count, color, texture):
        self.first = first      # 起始角点索引(用于 glDrawArrays first)
        self.count = count      # 角点数(用于 glDrawArrays count)
        self.color = color      # (r,g,b) 固有色
        self.texture = texture  # 漫反射贴图文件路径 或 None


class MeshData(object):
    __slots__ = ("interleaved", "submeshes", "bbox_min", "bbox_max", "vertex_count")

    def __init__(self, interleaved, submeshes, bbox_min, bbox_max, vertex_count):
        self.interleaved = interleaved   # bytes: [px,py,pz,nx,ny,nz,u,v] * vertex_count (float32)
        self.submeshes = submeshes       # list[Submesh]
        self.bbox_min = bbox_min
        self.bbox_max = bbox_max
        self.vertex_count = vertex_count

    def center_radius(self):
        cx = (self.bbox_min[0] + self.bbox_max[0]) * 0.5
        cy = (self.bbox_min[1] + self.bbox_max[1]) * 0.5
        cz = (self.bbox_min[2] + self.bbox_max[2]) * 0.5
        dx = self.bbox_max[0] - self.bbox_min[0]
        dy = self.bbox_max[1] - self.bbox_min[1]
        dz = self.bbox_max[2] - self.bbox_min[2]
        radius = 0.5 * math.sqrt(dx * dx + dy * dy + dz * dz)
        return (cx, cy, cz), (radius if radius > 1e-6 else 1.0)


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
    try:
        geom_mats = _geom_material_lists(root)
        mat_info = _parse_materials(root, path)
    except Exception:
        geom_mats, mat_info = {}, {}

    # 按材质(固有色+贴图)分桶,保持出现顺序
    buckets = {}
    bucket_order = []

    def bucket_for(matid):
        info = mat_info.get(matid) if matid is not None else None
        color = (info.get("color") if info else None) or _DEFAULT_COLOR
        texture = info.get("texture") if info else None
        key = (color, texture)
        b = buckets.get(key)
        if b is None:
            b = buckets[key] = array.array('f')
            bucket_order.append(key)
        return b

    inf = float("inf")
    min_x = min_y = min_z = inf
    max_x = max_y = max_z = -inf

    for geom in objects.children:
        if geom.name != "Geometry":
            continue
        vnode = geom.first("Vertices")
        pnode = geom.first("PolygonVertexIndex")
        if not vnode or not vnode.props or not pnode or not pnode.props:
            continue
        verts = vnode.props[0]
        pvi = pnode.props[0]
        if len(verts) < 9 or len(pvi) < 3:
            continue

        gid = geom.props[0] if geom.props and isinstance(geom.props[0], int) else None
        M = xforms.get(gid)

        nrm = _normal_indexer(geom)
        normals, nindex = (nrm[0], nrm[1]) if nrm else (None, None)
        uvl = _uv_indexer(geom)
        uvs, uindex = (uvl[0], uvl[1]) if uvl else (None, None)

        mat_list = geom_mats.get(gid, [])
        matlayer = _material_layer(geom)

        def mat_for_poly(p):
            if not mat_list:
                return None
            if matlayer is None:
                return mat_list[0]
            mapping, arr = matlayer
            if mapping.startswith("AllSame") or not arr:
                idx = arr[0] if arr else 0
            else:
                idx = arr[p] if p < len(arr) else 0
            if idx < 0 or idx >= len(mat_list):
                idx = 0
            return mat_list[idx]

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

        def corner_uv(cpi, pvc):
            if uvs is None:
                return (0.0, 0.0)
            base = uindex(cpi, pvc)
            if base is None:
                return (0.0, 0.0)
            return (uvs[base], uvs[base + 1])

        poly = []
        poly_index = 0
        for pvc in range(len(pvi)):
            idx = pvi[pvc]
            if idx < 0:
                poly.append((~idx, pvc))
                bucket = bucket_for(mat_for_poly(poly_index))
                for k in range(1, len(poly) - 1):
                    a, b_, c = poly[0], poly[k], poly[k + 1]
                    p0 = world_pos(a[0]); p1 = world_pos(b_[0]); p2 = world_pos(c[0])
                    n0 = corner_normal(a[0], a[1])
                    n1 = corner_normal(b_[0], b_[1])
                    n2 = corner_normal(c[0], c[1])
                    if n0 is None or n1 is None or n2 is None:
                        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
                        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
                        n0 = n1 = n2 = _normalize(uy * vz - uz * vy,
                                                  uz * vx - ux * vz,
                                                  ux * vy - uy * vx)
                    t0 = corner_uv(a[0], a[1])
                    t1 = corner_uv(b_[0], b_[1])
                    t2 = corner_uv(c[0], c[1])
                    for (px, py, pz), (nx, ny, nz), (tu, tv) in (
                            (p0, n0, t0), (p1, n1, t1), (p2, n2, t2)):
                        bucket.append(px); bucket.append(py); bucket.append(pz)
                        bucket.append(nx); bucket.append(ny); bucket.append(nz)
                        bucket.append(tu); bucket.append(tv)
                        if px < min_x: min_x = px
                        if py < min_y: min_y = py
                        if pz < min_z: min_z = pz
                        if px > max_x: max_x = px
                        if py > max_y: max_y = py
                        if pz > max_z: max_z = pz
                poly = []
                poly_index += 1
            else:
                poly.append((idx, pvc))

    if not bucket_order:
        raise FbxParseError("no triangles extracted")

    out = array.array('f')
    submeshes = []
    for key in bucket_order:
        b = buckets[key]
        nverts = len(b) // _FPV
        if nverts == 0:
            continue
        first = len(out) // _FPV
        out.extend(b)
        color, texture = key
        submeshes.append(Submesh(first, nverts, color, texture))

    if not submeshes:
        raise FbxParseError("no triangles extracted")

    total = len(out) // _FPV
    return MeshData(out.tobytes(), submeshes, (min_x, min_y, min_z), (max_x, max_y, max_z), total)
