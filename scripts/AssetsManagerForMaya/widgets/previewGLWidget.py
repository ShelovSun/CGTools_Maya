#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PreviewGLWidget —— 资产 FBX 三维预览(自写 OpenGL 视口)。

作为 widgets/previewWidget.PreviewWidget 的 drop-in 替换:选中资产时用纯 Python
解析其 FBX 几何/材质(utils/fbxMesh),在我们自己的 QOpenGLWidget 里渲染,支持鼠标
自由旋转/缩放/平移,**并显示漫反射贴图/固有色**。全程内存内完成,**不向用户的
Maya 场景添加任何东西**。

设计要点:
  * GLView: QOpenGLWidget 子类,独立 GL 上下文;按材质分子网格绘制(各自固有色/贴图),
    key+fill 双向光照(双面,避免反向缠绕发黑);LMB 旋转、滚轮缩放、MMB/Shift+LMB
    平移、双击重新框选。
  * 解析在后台线程(QThreadPool):worker 调 fbxMesh.read 得到几何 + 子网格(含贴图路径),
    并在 worker 线程加载贴图 QImage(已竖直翻转以匹配 GL);主线程回调里交给 GLView,
    VBO 与 GL 纹理在 paintGL 上传(此时 GL 上下文为当前)。按 (路径, mtime) 做小 LRU 缓存。
  * 三态显示:模型 / 加载中 / 回退图(无 FBX、解析失败、GL 不可用时显示 icon)。
  * 防抖 200ms + 去重。

drop-in 接口:clear() / setTitle() / setPreviewPixmap() / playerEnabled()。
回退到旧 icon 预览只需把 assetTools_optimized.py 改回 previewWidget.PreviewWidget()。
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


# OpenGL 常量(PySide2 不直接暴露枚举,按值硬编码)
_GL_DEPTH_TEST = 0x0B71
_GL_COLOR_BUFFER_BIT = 0x00004000
_GL_DEPTH_BUFFER_BIT = 0x00000100
_GL_TRIANGLES = 0x0004
_GL_FLOAT = 0x1406

_STRIDE = 8 * 4  # pos3 + nrm3 + uv2,float32

_VERT_SHADER = """
#version 120
attribute vec3 a_pos;
attribute vec3 a_nrm;
attribute vec2 a_uv;
uniform mat4 u_mvp;
varying vec3 v_nrm;
varying vec2 v_uv;
void main() {
    v_nrm = a_nrm;
    v_uv = a_uv;
    gl_Position = u_mvp * vec4(a_pos, 1.0);
}
"""

_FRAG_SHADER = """
#version 120
varying vec3 v_nrm;
varying vec2 v_uv;
uniform vec3 u_lightDir;     // key 光方向(相机前向)
uniform vec3 u_baseColor;    // 无贴图时的固有色
uniform int  u_useTex;
uniform sampler2D u_tex;
void main() {
    vec3 n = normalize(v_nrm);
    // 双面光照:abs 让反向缠绕的面也被照亮
    float d1 = abs(dot(n, normalize(-u_lightDir)));        // key(随相机)
    float d2 = abs(dot(n, normalize(vec3(-0.3, 0.6, 0.2)))); // fill(固定)
    float lit = 0.22 + 0.78 * d1 + 0.25 * d2;
    vec3 base = (u_useTex == 1) ? texture2D(u_tex, v_uv).rgb : u_baseColor;
    gl_FragColor = vec4(base * lit, 1.0);
}
"""


class GLView(QOpenGLWidget):
    """嵌入式 OpenGL 视口,按材质分子网格渲染一份静态网格,支持轨道相机交互。"""

    initFailed = QtCore.Signal()

    def __init__(self, parent=None):
        super(GLView, self).__init__(parent)

        fmt = QtGui.QSurfaceFormat()
        fmt.setDepthBufferSize(24)
        fmt.setSamples(4)  # MSAA(驱动不支持则忽略)
        self.setFormat(fmt)

        self._gl = None
        self._program = None
        self._vbo = None
        self._a_pos = self._a_nrm = self._a_uv = -1
        self._u_mvp = self._u_light = self._u_base = self._u_useTex = self._u_tex = -1
        self._init_failed = False

        # 待上传(在 paintGL 上传,确保 GL 上下文为当前)
        self._pending_bytes = None
        self._pending_count = 0
        self._pending_submeshes = []
        self._pending_images = {}
        self._dirty = False

        self._count = 0
        self._submeshes = []
        self._textures = {}  # texture_path -> QOpenGLTexture

        # 轨道相机
        self._az = 35.0
        self._el = 18.0
        self._dist = 5.0
        self._radius = 1.0
        self._target = QtGui.QVector3D(0.0, 0.0, 0.0)
        self._last_pos = None
        self._last_btn = None

        self.setFocusPolicy(QtCore.Qt.WheelFocus)

    # ----------------------------------------------------------- 网格接口
    def setMesh(self, interleaved_bytes, submeshes, images, bbox_min, bbox_max):
        self._pending_bytes = interleaved_bytes
        self._pending_count = sum(s.count for s in submeshes) if submeshes else 0
        self._pending_submeshes = submeshes or []
        self._pending_images = images or {}
        self._dirty = True
        self._fitTo(bbox_min, bbox_max)
        self.update()

    def clearMesh(self):
        self._pending_bytes = None
        self._pending_count = 0
        self._pending_submeshes = []
        self._pending_images = {}
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
        self._dist = self._radius / math.sin(math.radians(22.5)) * 1.2
        self._az = 35.0
        self._el = 18.0

    # ----------------------------------------------------------- GL 生命周期
    def initializeGL(self):
        try:
            self._gl = self.context().functions()
            self._gl.initializeOpenGLFunctions()

            self._program = QtGui.QOpenGLShaderProgram(self)
            # strip()：#version 必须是源码首行(部分驱动严格)
            ok = self._program.addShaderFromSourceCode(
                QtGui.QOpenGLShader.Vertex, _VERT_SHADER.strip())
            ok = self._program.addShaderFromSourceCode(
                QtGui.QOpenGLShader.Fragment, _FRAG_SHADER.strip()) and ok
            ok = self._program.link() and ok
            if not ok:
                raise RuntimeError("shader link failed: %s" % self._program.log())

            self._a_pos = self._program.attributeLocation("a_pos")
            self._a_nrm = self._program.attributeLocation("a_nrm")
            self._a_uv = self._program.attributeLocation("a_uv")
            self._u_mvp = self._program.uniformLocation("u_mvp")
            self._u_light = self._program.uniformLocation("u_lightDir")
            self._u_base = self._program.uniformLocation("u_baseColor")
            self._u_useTex = self._program.uniformLocation("u_useTex")
            self._u_tex = self._program.uniformLocation("u_tex")
        except Exception:
            self._init_failed = True
            self.initFailed.emit()

    def resizeGL(self, w, h):
        if self._gl:
            self._gl.glViewport(0, 0, w, max(1, h))

    def paintGL(self):
        if self._init_failed or not self._gl or not self._program:
            return

        bg = 38.0 / 255.0
        self._gl.glClearColor(bg, bg, bg + 3.0 / 255.0, 1.0)
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
        self._program.setUniformValue(self._u_tex, 0)

        self._vbo.bind()
        self._program.enableAttributeArray(self._a_pos)
        self._program.setAttributeBuffer(self._a_pos, _GL_FLOAT, 0, 3, _STRIDE)
        self._program.enableAttributeArray(self._a_nrm)
        self._program.setAttributeBuffer(self._a_nrm, _GL_FLOAT, 3 * 4, 3, _STRIDE)
        if self._a_uv >= 0:
            self._program.enableAttributeArray(self._a_uv)
            self._program.setAttributeBuffer(self._a_uv, _GL_FLOAT, 6 * 4, 2, _STRIDE)

        for sm in self._submeshes:
            tex = self._textures.get(sm.texture) if sm.texture else None
            if tex is not None:
                self._program.setUniformValue(self._u_useTex, 1)
                tex.bind(0)
            else:
                self._program.setUniformValue(self._u_useTex, 0)
                c = sm.color or (0.78, 0.78, 0.80)
                self._program.setUniformValue(self._u_base,
                                              QtGui.QVector3D(c[0], c[1], c[2]))
            self._gl.glDrawArrays(_GL_TRIANGLES, sm.first, sm.count)
            if tex is not None:
                tex.release(0)

        self._program.disableAttributeArray(self._a_pos)
        self._program.disableAttributeArray(self._a_nrm)
        if self._a_uv >= 0:
            self._program.disableAttributeArray(self._a_uv)
        self._vbo.release()
        self._program.release()

    def _uploadPending(self):
        self._dirty = False

        # 销毁旧纹理(此处 GL 上下文为当前)
        for t in self._textures.values():
            try:
                t.destroy()
            except Exception:
                pass
        self._textures = {}

        if not self._pending_bytes or self._pending_count <= 0:
            self._count = 0
            self._submeshes = []
            return

        if self._vbo is None:
            self._vbo = QtGui.QOpenGLBuffer(QtGui.QOpenGLBuffer.VertexBuffer)
            self._vbo.create()
        self._vbo.bind()
        self._vbo.allocate(self._pending_bytes, len(self._pending_bytes))
        self._vbo.release()

        self._count = self._pending_count
        self._submeshes = self._pending_submeshes

        for sm in self._submeshes:
            tp = sm.texture
            if tp and tp in self._pending_images and tp not in self._textures:
                try:
                    tex = QtGui.QOpenGLTexture(self._pending_images[tp])
                    tex.setMinificationFilter(QtGui.QOpenGLTexture.LinearMipMapLinear)
                    tex.setMagnificationFilter(QtGui.QOpenGLTexture.Linear)
                    tex.setWrapMode(QtGui.QOpenGLTexture.Repeat)
                    self._textures[tp] = tex
                except Exception:
                    pass

        self._pending_bytes = None  # 已传 GPU,释放内存副本
        self._pending_images = {}

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
        ar = math.radians(self._az)
        er = math.radians(self._el)
        ce = math.cos(er)
        fwd = QtGui.QVector3D(-ce * math.sin(ar), -math.sin(er), -ce * math.cos(ar))
        right = QtGui.QVector3D.crossProduct(fwd, QtGui.QVector3D(0.0, 1.0, 0.0))
        if right.length() > 1e-6:
            right.normalize()
        up = QtGui.QVector3D.crossProduct(right, fwd)
        if up.length() > 1e-6:
            up.normalize()
        return right, up

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

        mods = e.modifiers()
        pan = (self._last_btn == QtCore.Qt.MiddleButton) or \
              (self._last_btn == QtCore.Qt.LeftButton and (mods & QtCore.Qt.ShiftModifier))
        if pan:
            right, up = self._basis()
            scale = self._dist * 0.0015
            self._target = self._target - right * (dx * scale) + up * (dy * scale)
        elif self._last_btn == QtCore.Qt.LeftButton:
            self._az -= dx * 0.4
            self._el = max(-89.0, min(89.0, self._el + dy * 0.4))
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
        self._dist = self._radius / math.sin(math.radians(22.5)) * 1.2
        self._az = 35.0
        self._el = 18.0
        self.update()


# --------------------------------------------------------------------------- 异步解析
class _ParseSignals(QtCore.QObject):
    done = QtCore.Signal(str, object, object)  # path, MeshData, images{path:QImage}
    failed = QtCore.Signal(str)


class _ParseTask(QtCore.QRunnable):
    def __init__(self, path, signals):
        super(_ParseTask, self).__init__()
        self._path = path
        self._signals = signals

    def run(self):
        try:
            md = fbxMesh.read(self._path)
            # 在 worker 线程加载贴图(QImage 非 GUI 对象,可在子线程加载;竖直翻转以匹配 GL)
            images = {}
            for sm in md.submeshes:
                tp = sm.texture
                if tp and tp not in images:
                    img = QtGui.QImage(tp)
                    if not img.isNull():
                        images[tp] = img.mirrored(False, True)
            self._signals.done.emit(self._path, md, images)
        except Exception:
            self._signals.failed.emit(self._path)


# --------------------------------------------------------------------------- 容器控件
class PreviewGLWidget(QtWidgets.QWidget):
    """drop-in 替换 PreviewWidget 的 FBX 三维预览控件。"""

    _CACHE_CAP = 8
    _PAGE_FALLBACK = 0
    _PAGE_GL = 1
    _PAGE_LOADING = 2

    _GRADIENT_BG = (
        "background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, "
        "fx:0.5, fy:0.5, stop:0 rgba(35, 36, 39, 100), stop:1 rgba(35, 36, 39, 255));"
    )

    def __init__(self, isPlayer=True):
        super(PreviewGLWidget, self).__init__()

        self.isPlayer = isPlayer
        self._name = None
        self._fallback_icon = ""
        self._fallback_pixmap = None
        self._current_fbx = None        # 当前请求/显示的 FBX(去重 + 防过期)
        self._gl_failed = not _HAS_QOPENGL
        self._cache = {}                # path -> (mtime, MeshData, images)
        self._cache_order = []

        self._buildUI()

        self._pool = QtCore.QThreadPool(self)
        self._pool.setMaxThreadCount(2)
        self._signals = _ParseSignals()
        self._signals.done.connect(self._onParsed)
        self._signals.failed.connect(self._onParseFailed)

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
        self._image_label.setStyleSheet(self._GRADIENT_BG)
        self._stack.addWidget(self._image_label)            # index 0

        # page1: GL 视口(仅在 QOpenGLWidget 可用时)
        self._gl_view = None
        if _HAS_QOPENGL:
            self._gl_view = GLView(self)
            self._gl_view.initFailed.connect(self._onGLFailed)
            self._stack.addWidget(self._gl_view)            # index 1
        else:
            self._stack.addWidget(QtWidgets.QWidget())      # 占位,保持索引一致

        # page2: 加载中
        self._loading_label = QtWidgets.QLabel(u"加载中…")
        self._loading_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._loading_label.setStyleSheet(
            self._GRADIENT_BG + "color: rgb(180, 180, 180);")
        self._loading_label.setFont(QtGui.QFont(u"Microsoft YaHei UI", 11))
        self._stack.addWidget(self._loading_label)          # index 2

        vLayout.addWidget(self._stack)

        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setStyleSheet(
            "color: rgb(150, 150, 150);background-color: rgb(29, 29, 29);")
        self.title_label.setFixedHeight(45)
        self.title_label.setFont(QtGui.QFont(u"Microsoft YaHei UI", 10))
        vLayout.addWidget(self.title_label)

    def resizeEvent(self, e):
        self.setMaximumHeight(self.width() + 45)
        if self._stack.currentIndex() == self._PAGE_FALLBACK and self._fallback_pixmap:
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
        self._fallback_icon = path or ""
        fbx = self._deriveFbxPath(path, self._name)
        self._scheduleLoad(fbx, path)

    def playerEnabled(self, value):
        pass  # FBX 预览无序列播放器,空实现保持接口兼容

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
        self._stack.setCurrentIndex(self._PAGE_FALLBACK)

    # ----------------------------------------------------------- 加载调度
    def _deriveFbxPath(self, icon_path, name):
        """icon 路径 + 资产名 → FBX 路径(同 detailPath 约定)。
        例 .../X/Icon/X.png → .../X/FBX/X.fbx
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

        if self._gl_failed or self._gl_view is None or not norm or not os.path.isfile(norm):
            self._current_fbx = None
            self._showFallback(fallback_icon)
            return

        if norm == self._current_fbx:
            return  # 去重

        self._current_fbx = norm
        self._fallback_icon = fallback_icon or self._fallback_icon

        cached = self._cacheGet(norm)
        if cached is not None:
            md, images = cached
            self._gl_view.setMesh(md.interleaved, md.submeshes, images,
                                  md.bbox_min, md.bbox_max)
            self._stack.setCurrentIndex(self._PAGE_GL)
            return

        self._stack.setCurrentIndex(self._PAGE_LOADING)
        self._pool.start(_ParseTask(norm, self._signals))

    def _onParsed(self, path, md, images):
        if path != self._current_fbx:
            return  # 已切换,丢弃过期结果
        self._cachePut(path, md, images)
        if self._gl_view is not None:
            self._gl_view.setMesh(md.interleaved, md.submeshes, images,
                                  md.bbox_min, md.bbox_max)
            self._stack.setCurrentIndex(self._PAGE_GL)

    def _onParseFailed(self, path):
        if path != self._current_fbx:
            return
        self._current_fbx = None
        self._showFallback(self._fallback_icon)

    def _onGLFailed(self):
        self._gl_failed = True
        self._showFallback(self._fallback_icon)

    # ----------------------------------------------------------- 缓存(小 LRU)
    def _cacheGet(self, path):
        rec = self._cache.get(path)
        if not rec:
            return None
        mtime, md, images = rec
        try:
            if os.path.getmtime(path) != mtime:
                return None
        except OSError:
            return None
        try:
            self._cache_order.remove(path)
        except ValueError:
            pass
        self._cache_order.append(path)
        return md, images

    def _cachePut(self, path, md, images):
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None
        self._cache[path] = (mtime, md, images)
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
        self._stack.setCurrentIndex(self._PAGE_FALLBACK)

    def _applyFallbackPixmap(self):
        if not self._fallback_pixmap or self._fallback_pixmap.isNull():
            return
        w = max(1, self._image_label.width())
        h = max(1, self._image_label.height())
        self._image_label.setPixmap(
            self._fallback_pixmap.scaled(
                w, h, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
