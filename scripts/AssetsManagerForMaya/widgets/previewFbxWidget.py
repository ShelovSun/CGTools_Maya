#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
!!! 已废弃 / 请勿接入(DO NOT WIRE) !!!
本控件通过嵌入 Maya modelPanel + 把 FBX 临时导入「当前场景」来预览,会向用户的工作
场景添加节点/命名空间/相机,违反「预览不得改动当前场景」的硬性要求,已被用户否决。
现行方案是 widgets/previewGLWidget.py(纯 Python 解析 FBX + 自写 OpenGL,完全不碰场景)。
本文件仅作参考(其 _deriveFbxPath 路径推导被新控件复用),验收通过后应删除。
============================================================================

PreviewFbxWidget —— 资产 FBX 三维预览控件

作为 widgets/previewWidget.PreviewWidget 的 drop-in 替换：在 AssetsManager 右侧
预览区，选中资产时不再只显示静态 icon 图片，而是把该资产的 FBX 临时载入一个**嵌入式
Maya 视口(modelPanel)**，支持 alt+鼠标 旋转/缩放/平移。

为什么是这种实现：工具跑在 Maya 内部，要获得「真三维」交互，唯一可行的办法是嵌入真实的
Maya 视口；而 modelPanel 永远渲染「当前 Maya 场景」的 DAG，没有「只往某个面板加载外部
文件」的机制，所以必须把 FBX **临时导入当前场景**。FBX Python SDK 只能解析不能渲染，
故不采用。

为尽量不打扰美术，导入/清理遵循以下安全策略（详见各方法注释）：
  * 独立命名空间：导入到唯一命名空间(amFbxPrevNs<id>)，便于整体删除。
  * isolateSelect：只在本预览面板显示导入的节点，其它视口不受影响(isolateSelect 按面板生效)。
  * 屏蔽 undo：导入/删除前 undoInfo(stateWithoutFlush=False)，完成后恢复，不污染 undo 队列。
  * 恢复 modified 标记：导入/删除前后还原 cmds.file(modified=...)，不把美术场景标记为已修改。
  * 不动美术选择：临时 select 后还原原选择。
  * 专用相机：viewFit 框选用自建相机(amFbxPreviewCam<id>)，不动美术的 persp。
  * 自动清理：切换资产 / clear() / 关闭控件 / 场景 new|open(scriptJob) 时删除导入节点。
  * 去重 + 防抖：同一 FBX 不重复导入；选中变化用 ~200ms 防抖，避免快速切换时逐个导入
    (cmds.file 导入必须在主线程且阻塞，网络盘上尤其慢)。
  * 残留兜底：构造时清理上次会话遗留的 amFbxPrev* 前缀命名空间/相机/面板。

已知限制：
  * 实时 Maya 视口会接管鼠标，App 的 customContextMenuRequested 右键菜单在视口上可能被
    Maya 自身的右键/marking-menu 截走(v1 接受)。
  * cmds.file 导入只能主线程，单个大 FBX 仍会有可感知停顿(已用防抖+去重缓解)。

回退：把 sources/assetTools_optimized.py 里构造预览控件的那行从
PreviewFbxWidget 改回 previewWidget.PreviewWidget() 即可。
"""

import os
from contextlib import contextmanager

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

try:
    import maya.cmds as cmds
    _IN_MAYA = True
except Exception:
    cmds = None
    _IN_MAYA = False


# 唯一前缀：用于命名 + 跨会话清理遗留对象
_PANEL_PREFIX = "amFbxPreviewPanel"
_CAM_PREFIX = "amFbxPreviewCam"
_NS_PREFIX = "amFbxPrevNs"


class PreviewFbxWidget(QtWidgets.QWidget):
    """资产 FBX 三维预览控件（drop-in 替换 PreviewWidget）。

    对外暴露与 PreviewWidget 相同的接口：clear() / setTitle() /
    setPreviewPixmap() / playerEnabled()，故 assetTools_optimized 现有调用无需改动。
    """

    def __init__(self, isPlayer=True):
        super(PreviewFbxWidget, self).__init__()

        self.isPlayer = isPlayer

        # 资产 / Maya 侧状态
        self._name = None              # 由 setTitle 存下的资产名，用于拼 FBX 路径
        self._fallback_icon = ""       # 当前 icon 路径（FBX 缺失时回退显示）
        self._fallback_pixmap = None   # 缓存的回退原图，用于 resize 时重新缩放
        self._panel = None             # modelPanel 名
        self._cam = None               # 专用相机 transform 名
        self._namespace = None         # 本次导入所用命名空间
        self._imported_roots = []      # 本次导入的 DAG 顶层节点
        self._current_fbx = None       # 当前已显示的 FBX（去重用）
        self._panel_built = False
        self._script_jobs = []

        self._buildUI()

        # 选中变化防抖：避免在列表里快速切换时每个资产都触发一次(网络盘)导入
        self._load_timer = QtCore.QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.setInterval(200)
        self._load_timer.timeout.connect(self._loadPending)
        self._pending_fbx = None
        self._pending_icon = None

        # 清理上次会话/实例可能遗留的临时对象
        self._cleanupStale()

    # ------------------------------------------------------------------ UI
    def _buildUI(self):
        vLayout = QtWidgets.QVBoxLayout(self)
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)

        # page0 = 回退图片(QLabel)；page1 = 嵌入 Maya 视口的容器
        self._stack = QtWidgets.QStackedWidget(self)

        self._image_label = QtWidgets.QLabel()
        self._image_label.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        self._image_label.setStyleSheet(
            "background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, "
            "fx:0.5, fy:0.5, stop:0 rgba(35, 36, 39, 100), stop:1 rgba(35, 36, 39, 255));"
        )
        self._stack.addWidget(self._image_label)  # index 0

        unique = "%s%d" % (_PANEL_PREFIX, id(self))
        self._viewport = QtWidgets.QWidget()
        self._viewport.setObjectName(unique + "Container")
        self._viewport_layout = QtWidgets.QVBoxLayout(self._viewport)
        self._viewport_layout.setContentsMargins(0, 0, 0, 0)
        # Maya 用 setParent(objectName) 按 objectName 在 Qt 树中找到该 layout 并把
        # modelPanel 挂进去，所以这个 objectName 必须唯一且已设置。
        self._viewport_layout.setObjectName(unique + "Layout")
        self._stack.addWidget(self._viewport)  # index 1

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
        # 保持与 PreviewWidget 一致的近正方形比例（高度 = 宽 + 标题栏 45）
        self.setMaximumHeight(self.width() + 45)
        if self._stack.currentIndex() == 0 and self._fallback_pixmap:
            self._applyFallbackPixmap()
        super(PreviewFbxWidget, self).resizeEvent(e)

    def showEvent(self, e):
        super(PreviewFbxWidget, self).showEvent(e)

    def closeEvent(self, e):
        # 注意：嵌套子控件的 closeEvent 不一定触发（仅顶层窗口可靠），故清理不能只依赖这里——
        # 构造时的 _cleanupStale + scriptJob 父挂到 panel 共同兜底。
        self._teardown()
        super(PreviewFbxWidget, self).closeEvent(e)

    # ------------------------------------------------- 对外接口（drop-in）
    def setTitle(self, name, zh_name):
        self._name = str(name) if name is not None else None
        if zh_name is not None:
            self.title_label.setText(u"Name： " + str(name) + u"\n中文名： " + str(zh_name))
        else:
            self.title_label.setText(u"Name： " + str(name) + u"\n中文名： ")

    def setPreviewPixmap(self, path, _type=None):
        """收到 icon 路径时，派生出 FBX 路径并(防抖)加载。

        mainWightItemChanged 调用顺序是先 setTitle 后 setPreviewPixmap，故此处 self._name
        已就绪。这样保持 drop-in：mainWightItemChanged 无需改动。
        """
        self._fallback_icon = path or ""
        fbx = self._deriveFbxPath(path, self._name)
        self._scheduleLoad(fbx, path)

    def playerEnabled(self, value):
        # FBX 预览无图片序列播放器，保留空实现以兼容 PreviewWidget 接口
        pass

    def clear(self):
        self.title_label.clear()
        self._image_label.clear()
        self._fallback_pixmap = None
        self._fallback_icon = ""
        self._load_timer.stop()
        self._pending_fbx = None
        self._pending_icon = None
        self._clearCurrent()
        self._stack.setCurrentIndex(0)

    # ----------------------------------------------------------- 加载调度
    def _deriveFbxPath(self, icon_path, name):
        """由 icon 路径 + 资产名拼出 FBX 路径。

        约定同 assetTools_optimized.detailPath()：root = icon.split("Icon")[0]，
        例 icon=.../ZangJinQiangYu/Icon/ZangJinQiangYu.png →
            fbx =.../ZangJinQiangYu/FBX/ZangJinQiangYu.fbx
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
        """加载并显示 FBX；缺失则回退显示 icon 图。"""
        norm = fbx_path.replace("\\", "/") if fbx_path else ""

        # 已在显示同一个 FBX，跳过（去重）
        if norm and norm == self._current_fbx:
            return

        # 非 Maya 环境、无 FBX 或文件不存在 → 回退图片
        if not _IN_MAYA or not norm or not os.path.isfile(norm):
            self._clearCurrent()
            self._showFallback(fallback_icon)
            self._current_fbx = None
            return

        self._ensurePanel()
        self._clearCurrent()

        prev_sel = cmds.ls(sl=True, long=True) or []
        with self._sceneGuard():
            self._ensureFbxPlugin()
            ns = "%s%d" % (_NS_PREFIX, id(self))
            new_nodes = cmds.file(
                norm,
                i=True,
                type="FBX",
                ignoreVersion=True,
                returnNewNodes=True,
                mergeNamespacesOnClash=False,
                namespace=ns,
                preserveReferences=True,
            ) or []
            self._namespace = ns

            # 取 DAG 顶层节点用于 isolate / viewFit
            roots = cmds.ls(new_nodes, assemblies=True, long=True) or []
            if not roots:
                roots = cmds.ls("%s:*" % ns, assemblies=True, long=True) or []
            self._imported_roots = roots

            # 只在本面板显示导入的节点
            cmds.isolateSelect(self._panel, state=1)
            if roots:
                cmds.select(roots, r=True)
                cmds.isolateSelect(self._panel, loadSelected=True)
                cmds.viewFit(self._cam, animate=False)
            # 还原美术原本的选择
            if prev_sel:
                cmds.select(prev_sel, r=True)
            else:
                cmds.select(clear=True)

        self._current_fbx = norm
        self._stack.setCurrentWidget(self._viewport)

    # ------------------------------------------------------- Maya 视口构建
    def _ensurePanel(self):
        """惰性创建嵌入式 modelPanel + 专用相机（首次需要时）。"""
        if self._panel_built or not _IN_MAYA:
            return

        # 先让 page1 成为当前页，确保其 QWidget 已 realize，Maya 才能按 objectName 找到它
        self._stack.setCurrentWidget(self._viewport)

        with self._sceneGuard():
            panel = "%s%d" % (_PANEL_PREFIX, id(self))
            cmds.setParent(self._viewport_layout.objectName())
            if cmds.modelPanel(panel, exists=True):
                self._panel = panel
            else:
                self._panel = cmds.modelPanel(panel, label="FBX Preview", menuBarVisible=False)

            self._configEditor()

            cam = "%s%d" % (_CAM_PREFIX, id(self))
            if not cmds.objExists(cam):
                cam_t = cmds.camera()[0]
                cam = cmds.rename(cam_t, cam)
            self._cam = cam
            cmds.modelEditor(self._panel, edit=True, camera=self._cam)

        self._panel_built = True
        self._registerScriptJobs()

    def _configEditor(self):
        p = self._panel
        # 关掉无关显示，配合 isolateSelect 只显示导入资产
        cmds.modelEditor(p, edit=True, allObjects=False)
        cmds.modelEditor(p, edit=True, grid=False)
        cmds.modelEditor(p, edit=True, headsUpDisplay=False)
        cmds.modelEditor(p, edit=True, manipulators=False)
        cmds.modelEditor(p, edit=True, selectionHiliteDisplay=False)
        cmds.modelEditor(p, edit=True, dynamics=False)
        # 打开几何 + 平滑着色 + 贴图 + 默认灯光
        cmds.modelEditor(p, edit=True, polymeshes=True)
        cmds.modelEditor(p, edit=True, nurbsSurfaces=True)
        cmds.modelEditor(p, edit=True, subdivSurfaces=True)
        cmds.modelEditor(p, edit=True, displayAppearance="smoothShaded")
        cmds.modelEditor(p, edit=True, displayTextures=True)
        cmds.modelEditor(p, edit=True, displayLights="default")

    # ----------------------------------------------------------- 清理逻辑
    def _clearCurrent(self):
        """删除上次导入的节点（命名空间整体移除）。"""
        if not _IN_MAYA:
            self._namespace = None
            self._imported_roots = []
            self._current_fbx = None
            return

        ns = self._namespace
        with self._sceneGuard():
            try:
                if self._panel and cmds.modelPanel(self._panel, exists=True):
                    cmds.isolateSelect(self._panel, state=0)
            except Exception:
                pass
            try:
                if ns and cmds.namespace(exists=ns):
                    cmds.namespace(setNamespace=":")
                    cmds.namespace(removeNamespace=ns, deleteNamespaceContent=True)
            except Exception:
                pass

        self._namespace = None
        self._imported_roots = []
        self._current_fbx = None

    def _teardown(self):
        """彻底清理：删导入节点 + 相机 + 面板 + 杀 scriptJob。"""
        self._killScriptJobs()
        self._clearCurrent()
        if not _IN_MAYA:
            return
        with self._sceneGuard():
            try:
                if self._cam and cmds.objExists(self._cam):
                    cmds.delete(self._cam)
            except Exception:
                pass
            try:
                if self._panel and cmds.modelPanel(self._panel, exists=True):
                    cmds.deleteUI(self._panel, panel=True)
            except Exception:
                pass
        self._cam = None
        self._panel = None
        self._panel_built = False

    def _cleanupStale(self):
        """构造时清理上次会话遗留的 amFbxPrev* 临时对象（避免泄漏累积）。

        本实例的对象名都带 id(self)，此刻尚未创建，故这里删除的只会是历史遗留。
        """
        if not _IN_MAYA:
            return
        with self._sceneGuard():
            try:
                all_ns = cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True) or []
                cmds.namespace(setNamespace=":")
                for ns in all_ns:
                    leaf = ns.split(":")[-1]
                    if leaf.startswith(_NS_PREFIX) and cmds.namespace(exists=ns):
                        try:
                            cmds.namespace(removeNamespace=ns, deleteNamespaceContent=True)
                        except Exception:
                            pass
            except Exception:
                pass
            try:
                for cam in cmds.ls("%s*" % _CAM_PREFIX, long=True) or []:
                    if cmds.objExists(cam):
                        cmds.delete(cam)
            except Exception:
                pass
        try:
            for p in cmds.getPanel(type="modelPanel") or []:
                if p.startswith(_PANEL_PREFIX):
                    cmds.deleteUI(p, panel=True)
        except Exception:
            pass

    # -------------------------------------------------------- scriptJob
    def _registerScriptJobs(self):
        """场景 new/open 时复位预览（旧场景的临时节点已随之消失）。

        scriptJob 父挂到 modelPanel：面板被 deleteUI 时 Maya 自动杀掉这些 job，
        避免 widget 销毁后 job 仍回调到已删对象（见 [[assetmanager-dockable-fix]] 的 scriptJob 隐患）。
        """
        if not _IN_MAYA or not self._panel:
            return
        try:
            self._script_jobs.append(
                cmds.scriptJob(event=["SceneOpened", self._onSceneChanged], parent=self._panel)
            )
            self._script_jobs.append(
                cmds.scriptJob(event=["NewSceneOpened", self._onSceneChanged], parent=self._panel)
            )
        except Exception:
            pass

    def _killScriptJobs(self):
        if not _IN_MAYA:
            self._script_jobs = []
            return
        for j in self._script_jobs:
            try:
                cmds.scriptJob(kill=j, force=True)
            except Exception:
                pass
        self._script_jobs = []

    def _onSceneChanged(self):
        # 场景已切换：旧场景里的临时节点随之消失，这里只复位内部状态并清空预览。
        self._namespace = None
        self._imported_roots = []
        self._current_fbx = None
        try:
            if self._panel and cmds.modelPanel(self._panel, exists=True):
                cmds.isolateSelect(self._panel, state=1)  # 空 isolate 集 → 面板隐藏一切
        except Exception:
            pass
        try:
            self._stack.setCurrentIndex(0)
        except RuntimeError:
            # 控件已销毁（理论上 job 已随 panel 被杀，这里再兜一层）
            pass

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

    # ------------------------------------------------------------- 工具
    def _ensureFbxPlugin(self):
        try:
            if not cmds.pluginInfo("fbxmaya", query=True, loaded=True):
                cmds.loadPlugin("fbxmaya")
        except Exception:
            pass

    @contextmanager
    def _sceneGuard(self):
        """在屏蔽 undo、并最终恢复 undo 状态 + 场景 modified 标记 的上下文中执行。"""
        if not _IN_MAYA:
            yield
            return
        modified = cmds.file(query=True, modified=True)
        try:
            undo_state = cmds.undoInfo(query=True, state=True)
        except Exception:
            undo_state = True
        cmds.undoInfo(stateWithoutFlush=False)
        try:
            yield
        finally:
            try:
                cmds.undoInfo(stateWithoutFlush=undo_state)
            except Exception:
                pass
            try:
                cmds.file(modified=modified)
            except Exception:
                pass
