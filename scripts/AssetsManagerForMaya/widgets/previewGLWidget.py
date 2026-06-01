#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PreviewGLWidget —— 资产 FBX 三维预览(自写 OpenGL 视口)。

作为 widgets/previewWidget.PreviewWidget 的 drop-in 替换:选中资产时用纯 Python
解析其 FBX 几何(utils/fbxMesh),在我们自己的 QOpenGLWidget 里渲染,支持鼠标自由
旋转/缩放/平移。**全程在内存里完成,不向用户的 Maya 场景添加任何东西。**

设计要点:
  * GLView: QOpenGLWidget 子类,独立 GL 上下文;lambert headlight 着色(双面,
    避免反向缠绕的面发黑);LMB 旋转、滚轮缩放、MMB/Shift+LMB 平移、双击重新框选。
  * 解析在后台线程(QThreadPool),只产出顶点数组(不碰 GL);主线程回调里交给 GLView,
    VBO 上传延迟到 paintGL(此时 GL 上下文为当前)。按 (路径, mtime) 做小 LRU 缓存。
  * 防抖 200ms + 去重:列表里快速切换时不会每个都解析。
  * 回退:无 FBX / 解析失败 / GL 初始化失败 → 显示 icon 图(QStackedWidget page0),
    所以即使某台机器 GL 异常,工具也只是退化为图片预览,不会报错。

drop-in 接口与 PreviewWidget 一致:clear() / setTitle() / setPreviewPixmap() /
playerEnabled()。回退到旧 icon 预览只需把 assetTools_optimized.py:157 改回
previewWidget.PreviewWidget()。
"""

import os
import math

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from utils import fbxMesh

try:
    from PySide2.QtWidgets import QOpenGLWidget
    _HAS_QOPENGL = True
except Exception:
    QOpenGLWidget = QtWidgets.QWidget  # 占位基类;无 QOpenGLWidget 时不会实例化 GLView
    _HAS_QOPENGL = False


# OpenGL 常量(PySide2 不直接暴露枚举,这里按值硬编码)
_GL_DEPTH_TEST = 0x0B71
_GL_COLOR_BUFFER_BIT = 0x00004000
_GL_DEPTH_BUFFER_BIT = 0x00000100
_GL_TRIANGLES = 0x0004
_GL_FLOAT = 0x1406

_VERT_SHADER = """
#version 120
attribute vec3 a_pos;
attribute vec3 a_nrm;
uniform mat4 u_mvp;
varying vec3 v_nrm;
void main() {
    v_nrm = a_nrm;
    gl_Position = u_mvp * vec4(a_pos, 1.0);
}
"""

_FRAG_SHADER = """
#version 120
varying vec3 v_nrm;
uniform vec3 u_lightDir;
void main() {
    vec3 n = normalize(v_nrm);
    // 双面光照:abs 让反向缠绕的面也被照亮,避免发黑
    float d = abs(dot(n, normalize(-u_lightDir)));
    vec3 base = vec3(0.78, 0.78, 0.80);
    vec3 col = base * (0.28 + 0.72 * d);
    gl_FragColor = vec4(col, 1.0);
}
"""


class GLView(QOpenGLWidget):
    """嵌入式 OpenGL 视口,渲染一份静态网格,支持轨道相机交互。"""

    initFailed = QtCore.Signal()

    def __init__(self, parent=None):
        super(GLView, self).__init__(parent)

        fmt = QtGui.QSurfaceFormat()
        fmt.setDepthBufferSize(24)
        fmt.setSamples(4)  # MSAA,边缘更平滑(驱动不支持则忽略)
        self.setFormat(fmt)

        self._gl = None
        self._program = None
        self._vbo = None
        self._a_pos = -1
        self._a_nrm = -1
        self._u_mvp = -1
        self._u_light = -1
        self._init_failed = False

        # 待上传的网格(在 paintGL 里上传,确保 GL 上下文为当前)
        self._pending_bytes = None
        self._pending_count = 0
        self._count = 0
        self._dirty = False

        # 轨道相机
        self._az = 35.0
        self._el = 18.0
        self._dist = 5.0
        self._radius = 1.0
        self._target = QtGui.QVector3D(0.0, 0.0, 0.0)
        self._last_pos = None
        self._last_btn = None

        self.setMouseTracking(False)
        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    # ----------------------------------------------------------- 网格接口
    def setMesh(self, interleaved_bytes, vertex_count, bbox_min, bbox_max):
        """设置要显示的网格(纯数据,不在此处碰 GL)。"""
        self._pending_bytes = interleaved_bytes
        self._pending_count = vertex_count
        self._dirty = True
        self._fitTo(bbox_min, bbox_max)
        self.update()

    def clearMesh(self):
        self._pending_bytes = None
        self._pending_count = 0
        self._count = 0
        self._dirty = True
        self.update()

    def _fitTo(self, bbox_min, bbox_max):
        cx = (bbox_min[0] + bbox_max[0]) * 0.5
        cy = (bbox_min[1] + bbox_max[1]) * 0.5
        cz = (bbox_min[2] + bbox_max[2]) * 0.5
        self._target = QtGui.QVector3D(cx, cy, cz)
        dx = bbox_max[0] - bbox_min[0]
        dy = bbox_max[1] - bbox_min[1]
        dz = bbox_max[2] - bbox_min[2]
        r = 0.5 * math.sqrt(dx * dx + dy * dy + dz * dz)
        self._radius = r if r > 1e-6 else 1.0
        # 把包围球放进 45° 视野:dist = r / sin(fov/2),留些余量
        self._dist = self._radius / math.sin(math.radians(22.5)) * 1.2
        self._az = 35.0
        self._el = 18.0

    # ----------------------------------------------------------- GL 生命周期
    def initializeGL(self):
        try:
            ctx = self.context()
            self._gl = ctx.functions()
            self._gl.initializeOpenGLFunctions()

            self._program = QtGui.QOpenGLShaderProgram(self)
            # strip()：#version 必须是源码首行(部分驱动严格,前导空行会报错)
            ok = self._program.addShaderFromSourceCode(
                QtGui.QOpenGLShader.Vertex, _VERT_SHADER.strip())
            ok = self._program.addShaderFromSourceCode(
                QtGui.QOpenGLShader.Fragment, _FRAG_SHADER.strip()) and ok
            ok = self._program.link() and ok
            if not ok:
                raise RuntimeError("shader link failed: %s" % self._program.log())

            self._a_pos = self._program.attributeLocation("a_pos")
            self._a_nrm = self._program.attributeLocation("a_nrm")
            self._u_mvp = self._program.uniformLocation("u_mvp")
            self._u_light = self._program.uniformLocation("u_lightDir")
        except Exception:
            self._init_failed = True
            self.initFailed.emit()

    def resizeGL(self, w, h):
        if self._gl:
            self._gl.glViewport(0, 0, w, max(1, h))

    def paintGL(self):
        if self._init_failed or not self._gl or not self._program:
            return

        bg = 35.0 / 255.0
        self._gl.glClearColor(bg, bg + 1.0 / 255.0, bg + 4.0 / 255.0, 1.0)
        self._gl.glClear(_GL_COLOR_BUFFER_BIT | _GL_DEPTH_BUFFER_BIT)
        self._gl.glEnable(_GL_DEPTH_TEST)

        if self._dirty:
            self._uploadPending()

        if self._count <= 0 or self._vbo is None:
            return

        eye, light = self._cameraVectors()
        mvp = self._mvp(eye)

        self._program.bind()
        self._program.setUniformValue(self._u_mvp, mvp)
        self._program.setUniformValue(self._u_light, light)

        self._vbo.bind()
        stride = 6 * 4
        self._program.enableAttributeArray(self._a_pos)
        self._program.setAttributeBuffer(self._a_pos, _GL_FLOAT, 0, 3, stride)
        self._program.enableAttributeArray(self._a_nrm)
        self._program.setAttributeBuffer(self._a_nrm, _GL_FLOAT, 3 * 4, 3, stride)

        self._gl.glDrawArrays(_GL_TRIANGLES, 0, self._count)

        self._program.disableAttributeArray(self._a_pos)
        self._program.disableAttributeArray(self._a_nrm)
        self._vbo.release()
        self._program.release()

    def _uploadPending(self):
        self._dirty = False
        if not self._pending_bytes or self._pending_count <= 0:
            self._count = 0
            return
        if self._vbo is None:
            self._vbo = QtGui.QOpenGLBuffer(QtGui.QOpenGLBuffer.VertexBuffer)
            self._vbo.create()
        self._vbo.bind()
        self._vbo.allocate(self._pending_bytes, len(self._pending_bytes))
        self._vbo.release()
        self._count = self._pending_count
        self._pending_bytes = None  # 已上传到 GPU,释放内存副本

    # ----------------------------------------------------------- 相机
    def _cameraVectors(self):
        ar = math.radians(self._az)
        er = math.radians(self._el)
        ce = math.cos(er)
        d = QtGui.QVector3D(ce * math.sin(ar), math.sin(er), ce * math.cos(ar))
        eye = self._target + d * self._dist
        light = (self._target - eye)
        if light.length() > 1e-6:
            light.normalize()
        return eye, light

    def _mvp(self, eye):
        w = float(self.width())
        h = float(max(1, self.height()))
        near = max(self._dist - self._radius * 2.0, self._radius * 0.01, 0.001)
        far = self._dist + self._radius * 2.0 + 1.0
        proj = QtGui.QMatrix4x4()
        proj.perspective(45.0, w / h, near, far)
        view = QtGui.QMatrix4x4()
        view.lookAt(eye, self._target, QtGui.QVector3D(0.0, 1.0, 0.0))
        return proj * view

    def _basis(self):
        """返回相机的 right / up 向量(用于平移)。"""
        ar = math.radians(self._az)
        er = math.radians(self._el)
        ce = math.cos(er)
        fwd = QtGui.QVector3D(-ce * math.sin(ar), -math.sin(er), -ce * math.cos(ar))
        up = QtGui.QVector3D(0.0, 1.0, 0.0)
        right = QtGui.QVector3D.crossProduct(fwd, up)
        if right.length() > 1e-6:
            right.normalize()
        true_up = QtGui.QVector3D.crossProduct(right, fwd)
        if true_up.length() > 1e-6:
            true_up.normalize()
        return right, true_up

    # ----------------------------------------------------------- 鼠标交互
    def mousePressEvent(self, e):
        self._last_pos = e.pos()
        self._last_btn = e.button()
        self.setFocus()

    def mouseMoveEvent(self, e):
        if self._last_pos is None:
            return
        dx = e.x() - self._last_pos.x()
        dy = e.y() - self._last_pos.y()
        self._last_pos = e.pos()

        btn = self._last_btn
        mods = e.modifiers()
        pan = (btn == QtCore.Qt.MiddleButton) or \
              (btn == QtCore.Qt.LeftButton and (mods & QtCore.Qt.ShiftModifier))

        if pan:
            right, up = self._basis()
            scale = self._dist * 0.0015
            self._target = self._target - right * (dx * scale) + up * (dy * scale)
        elif btn == QtCore.Qt.LeftButton:
            self._az -= dx * 0.4
            self._el += dy * 0.4
            self._el = max(-89.0, min(89.0, self._el))
        self.update()

    def mouseReleaseEvent(self, e):
        self._last_pos = None
        self._last_btn = None

    def wheelEvent(self, e):
        delta = e.angleDelta().y()
        if delta == 0:
            return
        factor = math.pow(0.9, delta / 120.0)
        self._dist = max(self._radius * 0.05, min(self._radius * 50.0, self._dist * factor))
        self.update()

    def mouseDoubleClickEvent(self, e):
        # 重新框选:复位相机角度与距离(target/radius 已由 setMesh 算好)
        self._dist = self._radius / math.sin(math.radians(22.5)) * 1.2
        self._az = 35.0
        self._el = 18.0
        self.update()


# --------------------------------------------------------------------------- 异步解析
class _ParseSignals(QtCore.QObject):
    done = QtCore.Signal(str, object)
    failed = QtCore.Signal(str)


class _ParseTask(QtCore.QRunnable):
    def __init__(self, path, signals):
        super(_ParseTask, self).__init__()
        self._path = path
        self._signals = signals

    def run(self):
        try:
            md = fbxMesh.read(self._path)
            self._signals.done.emit(self._path, md)
        except Exception:
            self._signals.failed.emit(self._path)


# --------------------------------------------------------------------------- 容器控件
class PreviewGLWidget(QtWidgets.QWidget):
    """drop-in 替换 PreviewWidget 的 FBX 三维预览控件。"""

    _CACHE_CAP = 8

    def __init__(self, isPlayer=True):
        super(PreviewGLWidget, self).__init__()

        self.isPlayer = isPlayer
        self._name = None
        self._fallback_icon = ""
        self._fallback_pixmap = None
        self._current_fbx = None        # 当前请求/显示的 FBX(去重 + 防过期)
        self._gl_failed = not _HAS_QOPENGL
        self._cache = {}                # path -> (mtime, MeshData)
        self._cache_order = []

        self._buildUI()

        # 解析线程池 + 信号
        self._pool = QtCore.QThreadPool(self)
        self._pool.setMaxThreadCount(2)
        self._signals = _ParseSignals()
        self._signals.done.connect(self._onParsed)
        self._signals.failed.connect(self._onParseFailed)

        # 防抖
        self._load_timer = QtCore.QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.setInterval(200)
        self._load_timer.timeout.connect(self._loadPending)
        self._pending_fbx = None
        self._pending_icon = None

    # ------------------------------------------------------------------ UI
    def _buildUI(self):
        vLayout = QtWidgets.QVBoxLayout(self)
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)

        self._stack = QtWidgets.QStackedWidget(self)

        # page0: 回退图片
        self._image_label = QtWidgets.QLabel()
        self._image_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._image_label.setStyleSheet(
            "background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, "
            "fx:0.5, fy:0.5, stop:0 rgba(35, 36, 39, 100), stop:1 rgba(35, 36, 39, 255));"
        )
        self._stack.addWidget(self._image_label)  # index 0

        # page1: GL 视口(仅在 QOpenGLWidget 可用时)
        self._gl_view = None
        if _HAS_QOPENGL:
            self._gl_view = GLView(self)
            self._gl_view.initFailed.connect(self._onGLFailed)
            self._stack.addWidget(self._gl_view)  # index 1

        vLayout.addWidget(self._stack)

        font = QtGui.QFont(u"Microsoft YaHei UI", 10)
        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setStyleSheet(
            "color: rgb(150, 150, 150);background-color: rgb(29, 29, 29);"
        )
        self.title_label.setFixedHeight(45)
        self.title_label.setFont(font)
        vLayout.addWidget(self.title_label)

    def resizeEvent(self, e):
        self.setMaximumHeight(self.width() + 45)
        if self._stack.currentIndex() == 0 and self._fallback_pixmap:
            self._applyFallbackPixmap()
        super(PreviewGLWidget, self).resizeEvent(e)

    # ------------------------------------------------- 对外接口(drop-in)
    def setTitle(self, name, zh_name):
        self._name = str(name) if name is not None else None
        if zh_name is not None:
            self.title_label.setText(u"Name： " + str(name) + u"\n中文名： " + str(zh_name))
        else:
            self.title_label.setText(u"Name： " + str(name) + u"\n中文名： ")

    def setPreviewPixmap(self, path, _type=None):
        """收到 icon 路径 → 派生 FBX 路径 → 防抖加载。FBX 缺失/失败时回退显示该 icon。"""
        self._fallback_icon = path or ""
        fbx = self._deriveFbxPath(path, self._name)
        self._scheduleLoad(fbx, path)

    def playerEnabled(self, value):
        # FBX 三维预览无图片序列播放器,空实现保持接口兼容
        pass

    def clear(self):
        self._load_timer.stop()
        self._pending_fbx = None
        self._pending_icon = None
        self._current_fbx = None
        self.title_label.clear()
        self._image_label.clear()
        self._fallback_pixmap = None
        self._fallback_icon = ""
        if self._gl_view is not None:
            self._gl_view.clearMesh()
        self._stack.setCurrentIndex(0)

    # ----------------------------------------------------------- 加载调度
    def _deriveFbxPath(self, icon_path, name):
        """icon 路径 + 资产名 → FBX 路径(同 detailPath 约定)。
        例 .../ZangJinQiangYu/Icon/ZangJinQiangYu.png → .../ZangJinQiangYu/FBX/ZangJinQiangYu.fbx
        """
        if not icon_path or not name:
            return ""
        ip = icon_path.replace("\\", "/")
        root = ip.split("Icon")[0]
        if not root.endswith("/"):
            root += "/"
        return "%sFBX/%s.fbx" % (root, name)

    def _scheduleLoad(self, fbx, icon):
        self._pending_fbx = fbx
        self._pending_icon = icon
        self._load_timer.start()

    def _loadPending(self):
        self.loadFbx(self._pending_fbx, self._pending_icon)

    def loadFbx(self, fbx_path, fallback_icon=None):
        norm = fbx_path.replace("\\", "/") if fbx_path else ""

        # GL 不可用 / 无 FBX / 文件不存在 → 回退 icon
        if self._gl_failed or self._gl_view is None or not norm or not os.path.isfile(norm):
            self._current_fbx = None
            self._showFallback(fallback_icon)
            return

        if norm == self._current_fbx:
            return  # 已在显示(去重)

        self._current_fbx = norm
        self._fallback_icon = fallback_icon or self._fallback_icon

        # 缓存命中(按 mtime 校验)→ 直接显示
        cached = self._cacheGet(norm)
        if cached is not None:
            self._gl_view.setMesh(cached.interleaved, cached.vertex_count,
                                  cached.bbox_min, cached.bbox_max)
            self._stack.setCurrentIndex(1)
            return

        # 否则后台解析
        self._pool.start(_ParseTask(norm, self._signals))

    def _onParsed(self, path, md):
        if path != self._current_fbx:
            return  # 已切换到别的资产,丢弃过期结果
        self._cachePut(path, md)
        if self._gl_view is not None:
            self._gl_view.setMesh(md.interleaved, md.vertex_count, md.bbox_min, md.bbox_max)
            self._stack.setCurrentIndex(1)

    def _onParseFailed(self, path):
        if path != self._current_fbx:
            return
        self._current_fbx = None
        self._showFallback(self._fallback_icon)

    def _onGLFailed(self):
        # GL 初始化失败:永久退化为 icon 预览
        self._gl_failed = True
        self._showFallback(self._fallback_icon)

    # ----------------------------------------------------------- 缓存(小 LRU)
    def _cacheGet(self, path):
        rec = self._cache.get(path)
        if not rec:
            return None
        mtime, md = rec
        try:
            if os.path.getmtime(path) != mtime:
                return None  # 文件已更新,缓存失效
        except OSError:
            return None
        # 命中,挪到最近使用
        try:
            self._cache_order.remove(path)
        except ValueError:
            pass
        self._cache_order.append(path)
        return md

    def _cachePut(self, path, md):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None
        self._cache[path] = (mtime, md)
        if path in self._cache_order:
            self._cache_order.remove(path)
        self._cache_order.append(path)
        while len(self._cache_order) > self._CACHE_CAP:
            old = self._cache_order.pop(0)
            self._cache.pop(old, None)

    # ----------------------------------------------------------- 回退图片
    def _showFallback(self, icon_path):
        path = (icon_path or "").replace("\\", "/")
        if path and os.path.isfile(path):
            self._fallback_pixmap = QtGui.QPixmap(path)
            self._applyFallbackPixmap()
        else:
            self._fallback_pixmap = None
            self._image_label.clear()
        self._stack.setCurrentIndex(0)

    def _applyFallbackPixmap(self):
        if not self._fallback_pixmap or self._fallback_pixmap.isNull():
            return
        w = max(1, self._image_label.width())
        h = max(1, self._image_label.height())
        self._image_label.setPixmap(
            self._fallback_pixmap.scaled(
                w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
            )
        )
