#!/usr/bin/env python
# -*- coding: utf-8 -*-
# assetTools_optimized.py - 优化版本
# 使用新的高性能组件和异步加载

import os
import time
from functools import partial

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from config import projectSetting, SMConfig
from utils import jsonHelper, publish, messageBox
from utils.am_database import AssetDatabaseManager
from widgets import am_main_optimized, faverWidget, previewWidget, previewGLWidget, am_pixmap

# 左侧目录树里“全部目录”顶层节点的标记(选中它=横跨 asset+scene 搜索全部类型)。
# 与独立版 am_main.py 的 ALL_ROLE 同一做法(int(Qt.UserRole)+5)。
ALL_ROLE = int(QtCore.Qt.UserRole) + 5


def maya_main_window():
    """获取 Maya 主窗口"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


class AssetToolsUI(QtWidgets.QWidget):
    """
    优化后的资产管理工具 UI
    使用新的高性能组件
    """

    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')

    def __init__(self, user="", password="", **kwargs):
        # **kwargs 兼容旧调用点（如 toolSetting 里传 isCGTW=/ROOT=），避免参数不符报错
        super(AssetToolsUI, self).__init__()

        self.mayaMainWindow = maya_main_window()
        self.mayaMainWindow.setAcceptDrops(True)

        self.host = SMConfig().getPrefsValue("General/ip", "10.0.203.34")
        self.user = user
        self.password = password

        # 构建 UI（原 ui/assetTools.ui，改为代码构建，控件直接挂在 self 上）
        self.setupUi()

        self.Pub = publish.Publish()
        self.tab = "Assets"
        self.isList = False
        self.isAction = False
        self.isAttributeShow = True
        self.currentAssetData = {}
        self.ROOT = kwargs.get("ROOT") or "Y:/MCCProject"
        self.progress = 0
        self.file_type_expanded = True
        self.switch_expanded = True

        self.__fileTypeFolderDict = {
            'mod': 'Mod', 'render': 'Render', 'all_rig': 'Rig',
            'hi_rig': 'Rig', 'low_rig': 'Rig', 'xgen': 'Xgen',
            'AD': 'Assembly', 'OAT': 'Rig'
        }

        # 数据库管理器
        self._db_manager = AssetDatabaseManager(user, password, self.host)
        self._db_manager.assetsReady.connect(self._onAssetsBatchReady)
        self._db_manager.assetRowReady.connect(self._onAssetRowReady)
        self._db_manager.queryError.connect(self._onQueryError)
        self._db_manager.queryFinished.connect(self._onQueryFinished)

        # 缓存的资产数据
        self._asset_cache = []

        self.init_ui()
        self.show_asset()

    def setupUi(self):
        """构建资产管理控件（原 ui/assetTools.ui，改为代码构建）"""

        def _set_size_policy(widget, h, v):
            sp = QtWidgets.QSizePolicy(h, v)
            sp.setHorizontalStretch(0)
            sp.setVerticalStretch(0)
            sp.setHeightForWidth(widget.sizePolicy().hasHeightForWidth())
            widget.setSizePolicy(sp)

        def _font(size=10, bold=False, family=u"Microsoft YaHei UI"):
            f = QtGui.QFont()
            f.setFamily(family)
            f.setPointSize(size)
            if bold:
                f.setBold(True)
                f.setWeight(75)
            return f

        self.setWindowTitle(u"Form")
        self.setFont(_font())

        gridLayout_2 = QtWidgets.QGridLayout(self)
        gridLayout_2.setContentsMargins(0, 0, 0, 0)
        gridLayout_2.setSpacing(0)

        # ============ 顶部消息栏 ============
        msg_Layout = QtWidgets.QHBoxLayout()
        msg_Layout.setSpacing(10)

        self.msg_icon_label = QtWidgets.QLabel()
        _set_size_policy(self.msg_icon_label, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.msg_icon_label.setMinimumSize(QtCore.QSize(15, 15))
        self.msg_icon_label.setMaximumSize(QtCore.QSize(15, 15))
        self.msg_icon_label.setScaledContents(True)
        msg_Layout.addWidget(self.msg_icon_label)

        self.msg_label = QtWidgets.QLabel()
        _set_size_policy(self.msg_label, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.msg_label.setMinimumSize(QtCore.QSize(0, 15))
        self.msg_label.setMaximumSize(QtCore.QSize(150000, 15))
        self.msg_label.setFont(_font(size=8))
        self.msg_label.setScaledContents(True)
        msg_Layout.addWidget(self.msg_label)

        msg_Layout.addItem(QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        # ============ 主分割器（左/中/右三栏） ============
        self.mainWindow_splitter = QtWidgets.QSplitter()
        self.mainWindow_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.mainWindow_splitter.setHandleWidth(2)
        self.mainWindow_splitter.setChildrenCollapsible(False)

        # ---- 左栏：项目下拉 + 类型列表 ----
        layoutWidget = QtWidgets.QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout(layoutWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)  # layoutWidget 容器:布局边距置 0(同 uic)
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

        horizontalLayout_3 = QtWidgets.QHBoxLayout()
        horizontalLayout_3.setSpacing(6)
        horizontalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        horizontalLayout_3.setContentsMargins(-1, 2, -1, 2)

        self.label_2 = QtWidgets.QLabel()
        self.label_2.setMinimumSize(QtCore.QSize(30, 0))
        self.label_2.setMaximumSize(QtCore.QSize(30, 16777215))
        self.label_2.setFont(_font())
        self.label_2.setText(u"项目:")
        horizontalLayout_3.addWidget(self.label_2)

        self.project_comb = QtWidgets.QComboBox()
        _set_size_policy(self.project_comb, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.project_comb.setMinimumSize(QtCore.QSize(50, 25))
        self.project_comb.setMaximumSize(QtCore.QSize(200, 25))
        self.project_comb.setFont(_font(bold=True))
        horizontalLayout_3.addWidget(self.project_comb, 0, QtCore.Qt.AlignLeft)

        self.verticalLayout.addLayout(horizontalLayout_3)

        self.type_splitter = QtWidgets.QSplitter()
        self.type_splitter.setOrientation(QtCore.Qt.Vertical)
        self.type_splitter.setHandleWidth(3)

        # 目录树：全部目录 > Assets/Scenes > 各类型（asset 与 scene 合一浏览）
        self.type_treeWidget = QtWidgets.QTreeWidget()
        _set_size_policy(self.type_treeWidget, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.type_treeWidget.setMinimumSize(QtCore.QSize(50, 50))
        self.type_treeWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.type_treeWidget.header().setVisible(False)
        self.type_treeWidget.setExpandsOnDoubleClick(True)
        self.type_splitter.addWidget(self.type_treeWidget)

        self.verticalLayout.addWidget(self.type_splitter)
        self.mainWindow_splitter.addWidget(layoutWidget)

        # ---- 中栏：工具栏（主视图在 init_ui 里追加进 verticalLayout_3） ----
        layoutWidget_2 = QtWidgets.QWidget()
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(layoutWidget_2)
        self.verticalLayout_3.setSpacing(3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)

        horizontalLayout = QtWidgets.QHBoxLayout()
        horizontalLayout.setSpacing(2)

        self.back_bttn = QtWidgets.QPushButton()
        self.back_bttn.setEnabled(False)
        _set_size_policy(self.back_bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.back_bttn.setMinimumSize(QtCore.QSize(25, 25))
        self.back_bttn.setMaximumSize(QtCore.QSize(25, 25))
        self.back_bttn.setFont(_font(size=3))
        self.back_bttn.setToolTip(u"后退")
        self.back_bttn.setIconSize(QtCore.QSize(22, 22))
        self.back_bttn.setCheckable(False)
        self.back_bttn.setDefault(False)
        self.back_bttn.setFlat(True)
        horizontalLayout.addWidget(self.back_bttn)

        self.add_bttn = QtWidgets.QPushButton()
        _set_size_policy(self.add_bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.add_bttn.setMinimumSize(QtCore.QSize(25, 25))
        self.add_bttn.setMaximumSize(QtCore.QSize(25, 25))
        self.add_bttn.setIconSize(QtCore.QSize(22, 22))
        self.add_bttn.setAutoExclusive(True)
        self.add_bttn.setFlat(True)
        horizontalLayout.addWidget(self.add_bttn)

        self.displayThumb_bttn = QtWidgets.QPushButton()
        _set_size_policy(self.displayThumb_bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.displayThumb_bttn.setMinimumSize(QtCore.QSize(25, 25))
        self.displayThumb_bttn.setMaximumSize(QtCore.QSize(25, 25))
        self.displayThumb_bttn.setFont(_font(size=3))
        self.displayThumb_bttn.setIconSize(QtCore.QSize(22, 22))
        self.displayThumb_bttn.setCheckable(False)
        self.displayThumb_bttn.setAutoRepeat(False)
        self.displayThumb_bttn.setAutoExclusive(True)
        self.displayThumb_bttn.setFlat(True)
        horizontalLayout.addWidget(self.displayThumb_bttn)

        self.itemSize_Slider = QtWidgets.QSlider()
        self.itemSize_Slider.setMaximumSize(QtCore.QSize(150, 16777215))
        self.itemSize_Slider.setFont(_font(size=3))
        self.itemSize_Slider.setToolTip(u"缩放图标")
        self.itemSize_Slider.setMinimum(10)
        self.itemSize_Slider.setMaximum(200)
        self.itemSize_Slider.setValue(120)
        self.itemSize_Slider.setOrientation(QtCore.Qt.Horizontal)
        horizontalLayout.addWidget(self.itemSize_Slider)

        self.download_Bttn = QtWidgets.QPushButton()
        _set_size_policy(self.download_Bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.download_Bttn.setMinimumSize(QtCore.QSize(25, 25))
        self.download_Bttn.setMaximumSize(QtCore.QSize(25, 25))
        self.download_Bttn.setFont(_font(size=3))
        self.download_Bttn.setToolTip(u"下载资产到本地")
        self.download_Bttn.setIconSize(QtCore.QSize(22, 22))
        self.download_Bttn.setFlat(True)
        horizontalLayout.addWidget(self.download_Bttn)

        self.refresh_Bttn = QtWidgets.QPushButton()
        _set_size_policy(self.refresh_Bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.refresh_Bttn.setMinimumSize(QtCore.QSize(25, 25))
        self.refresh_Bttn.setMaximumSize(QtCore.QSize(25, 25))
        self.refresh_Bttn.setFont(_font(size=3))
        self.refresh_Bttn.setToolTip(u"刷新")
        self.refresh_Bttn.setIconSize(QtCore.QSize(22, 22))
        self.refresh_Bttn.setFlat(True)
        horizontalLayout.addWidget(self.refresh_Bttn)

        horizontalLayout.addItem(QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.key_line = QtWidgets.QLineEdit()
        self.key_line.setMinimumSize(QtCore.QSize(25, 25))
        self.key_line.setMaximumSize(QtCore.QSize(16777215, 25))
        self.key_line.setFont(_font())
        self.key_line.setPlaceholderText(u"Search...")
        self.key_line.setClearButtonEnabled(True)
        horizontalLayout.addWidget(self.key_line, 1)

        self.searchAll_cBox = QtWidgets.QCheckBox()
        self.searchAll_cBox.setMinimumSize(QtCore.QSize(13, 0))
        self.searchAll_cBox.setFont(_font())
        self.searchAll_cBox.setToolTip(u"全项目搜索")
        self.searchAll_cBox.setChecked(False)
        horizontalLayout.addWidget(self.searchAll_cBox)

        self.verticalLayout_3.addLayout(horizontalLayout)
        self.mainWindow_splitter.addWidget(layoutWidget_2)

        # ---- 右栏：预览 / 属性 分割器 ----
        self.attr_splitter = QtWidgets.QSplitter()
        _set_size_policy(self.attr_splitter, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.attr_splitter.setFont(_font())
        self.attr_splitter.setOrientation(QtCore.Qt.Vertical)
        self.attr_splitter.setHandleWidth(3)

        # 上半：收藏/标签/上传按钮 + 预览框（预览控件在 init_ui 里加入 preview_vLayout）
        layoutWidget_3 = QtWidgets.QWidget()
        self.Attr_up_vLayout = QtWidgets.QVBoxLayout(layoutWidget_3)
        self.Attr_up_vLayout.setSpacing(2)
        self.Attr_up_vLayout.setContentsMargins(0, 0, 0, 0)

        horizontalLayout_6 = QtWidgets.QHBoxLayout()
        horizontalLayout_6.addItem(QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.upload_Bttn = QtWidgets.QPushButton()
        _set_size_policy(self.upload_Bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.upload_Bttn.setMaximumSize(QtCore.QSize(21, 25))
        self.upload_Bttn.setIconSize(QtCore.QSize(20, 15))
        self.upload_Bttn.setFlat(True)
        horizontalLayout_6.addWidget(self.upload_Bttn)

        self.capture_Bttn = QtWidgets.QPushButton()
        _set_size_policy(self.capture_Bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.capture_Bttn.setMaximumSize(QtCore.QSize(21, 25))
        self.capture_Bttn.setIconSize(QtCore.QSize(20, 15))
        self.capture_Bttn.setFlat(True)
        horizontalLayout_6.addWidget(self.capture_Bttn)

        self.tag_bttn = QtWidgets.QPushButton()
        _set_size_policy(self.tag_bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.tag_bttn.setMaximumSize(QtCore.QSize(18, 25))
        self.tag_bttn.setToolTip(u"添加标签")
        self.tag_bttn.setIconSize(QtCore.QSize(15, 15))
        self.tag_bttn.setFlat(True)
        horizontalLayout_6.addWidget(self.tag_bttn)

        self.favor_bttn = QtWidgets.QPushButton()
        _set_size_policy(self.favor_bttn, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.favor_bttn.setMaximumSize(QtCore.QSize(18, 25))
        self.favor_bttn.setFont(_font())
        self.favor_bttn.setToolTip(u"添加收藏")
        self.favor_bttn.setIconSize(QtCore.QSize(15, 15))
        self.favor_bttn.setFlat(True)
        horizontalLayout_6.addWidget(self.favor_bttn)

        self.Attr_up_vLayout.addLayout(horizontalLayout_6)

        self.Preview_frame = QtWidgets.QFrame()
        _set_size_policy(self.Preview_frame, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.Preview_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.Preview_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        verticalLayout_8 = QtWidgets.QVBoxLayout(self.Preview_frame)
        verticalLayout_8.setSpacing(0)
        verticalLayout_8.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.preview_vLayout = QtWidgets.QVBoxLayout()
        verticalLayout_8.addLayout(self.preview_vLayout)
        self.Attr_up_vLayout.addWidget(self.Preview_frame)

        self.attr_splitter.addWidget(layoutWidget_3)

        # 下半：File Type 面板 + Reference Switch 面板
        layoutWidget_4 = QtWidgets.QWidget()
        self.Attr_down_vLayout = QtWidgets.QVBoxLayout(layoutWidget_4)
        self.Attr_down_vLayout.setSpacing(3)
        self.Attr_down_vLayout.setContentsMargins(0, 0, 0, 0)
        self.Attr_down_vLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)

        verticalLayout_10 = QtWidgets.QVBoxLayout()
        verticalLayout_10.setSpacing(2)

        self.file_type_tbttn = QtWidgets.QToolButton()
        _set_size_policy(self.file_type_tbttn, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.file_type_tbttn.setMaximumSize(QtCore.QSize(16777215, 18))
        self.file_type_tbttn.setFont(_font(size=9))
        self.file_type_tbttn.setStyleSheet(
            u"background-color: rgb(100, 100, 100);\ncolor: rgb(200, 200, 200);")
        self.file_type_tbttn.setText(u"File Type")
        self.file_type_tbttn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.file_type_tbttn.setAutoRaise(True)
        self.file_type_tbttn.setArrowType(QtCore.Qt.DownArrow)
        verticalLayout_10.addWidget(self.file_type_tbttn)

        self.file_type_frame = QtWidgets.QFrame()
        _set_size_policy(self.file_type_frame, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.file_type_frame.setMaximumSize(QtCore.QSize(16777215, 180))
        self.file_type_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.file_type_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        verticalLayout_11 = QtWidgets.QVBoxLayout(self.file_type_frame)
        verticalLayout_11.setSpacing(0)
        verticalLayout_11.setContentsMargins(2, 2, 2, 2)

        self.fileType_groupBox = QtWidgets.QGroupBox()
        _set_size_policy(self.fileType_groupBox, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.fileType_groupBox.setMaximumSize(QtCore.QSize(16777215, 100))
        self.fileType_groupBox.setFont(_font())
        self.fileType_groupBox.setTitle(u"")
        self.fileType_groupBox.setAlignment(
            QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.fileType_groupBox.setFlat(True)
        gridLayout_4 = QtWidgets.QGridLayout(self.fileType_groupBox)
        gridLayout_4.setContentsMargins(50, 0, 0, 0)
        gridLayout_4.setSpacing(0)

        # 文件类型单选按钮组（getCurrentItemsData() 依赖 self.fileType_bttnGroup）
        self.fileType_bttnGroup = QtWidgets.QButtonGroup(self)

        self.mod_rBttn = QtWidgets.QRadioButton()
        self.mod_rBttn.setText(u"mod")
        self.fileType_bttnGroup.addButton(self.mod_rBttn)
        gridLayout_4.addWidget(self.mod_rBttn, 0, 0)

        self.render_rBttn = QtWidgets.QRadioButton()
        self.render_rBttn.setText(u"render")
        self.fileType_bttnGroup.addButton(self.render_rBttn)
        gridLayout_4.addWidget(self.render_rBttn, 0, 1)

        self.allRig_rBttn = QtWidgets.QRadioButton()
        self.allRig_rBttn.setText(u"all_rig")
        self.fileType_bttnGroup.addButton(self.allRig_rBttn)
        gridLayout_4.addWidget(self.allRig_rBttn, 1, 0)

        self.hiRig_rBttn = QtWidgets.QRadioButton()
        self.hiRig_rBttn.setText(u"hi_rig")
        self.hiRig_rBttn.setChecked(True)
        self.fileType_bttnGroup.addButton(self.hiRig_rBttn)
        gridLayout_4.addWidget(self.hiRig_rBttn, 1, 1)

        self.lowRig_rBttn = QtWidgets.QRadioButton()
        self.lowRig_rBttn.setText(u"low_rig")
        self.fileType_bttnGroup.addButton(self.lowRig_rBttn)
        gridLayout_4.addWidget(self.lowRig_rBttn, 2, 0)

        self.xgen_rBttn = QtWidgets.QRadioButton()
        self.xgen_rBttn.setText(u"xgen")
        self.fileType_bttnGroup.addButton(self.xgen_rBttn)
        gridLayout_4.addWidget(self.xgen_rBttn, 2, 1)

        self.ad_rBttn = QtWidgets.QRadioButton()
        self.ad_rBttn.setText(u"AD")
        self.fileType_bttnGroup.addButton(self.ad_rBttn)
        gridLayout_4.addWidget(self.ad_rBttn, 3, 0)

        self.oat_rBttn = QtWidgets.QRadioButton()
        self.oat_rBttn.setText(u"OAT")
        self.fileType_bttnGroup.addButton(self.oat_rBttn)
        gridLayout_4.addWidget(self.oat_rBttn, 3, 1)

        verticalLayout_11.addWidget(self.fileType_groupBox)

        self.exportFbx_bttn = QtWidgets.QPushButton()
        _set_size_policy(self.exportFbx_bttn, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.exportFbx_bttn.setMinimumSize(QtCore.QSize(0, 25))
        self.exportFbx_bttn.setMaximumSize(QtCore.QSize(16777215, 25))
        self.exportFbx_bttn.setFont(_font(size=9))
        self.exportFbx_bttn.setText(u"ExportFBX")
        self.exportFbx_bttn.setCheckable(False)
        self.exportFbx_bttn.setAutoExclusive(False)
        verticalLayout_11.addWidget(self.exportFbx_bttn)

        verticalLayout_10.addWidget(self.file_type_frame)
        self.Attr_down_vLayout.addLayout(verticalLayout_10)

        verticalLayout_2 = QtWidgets.QVBoxLayout()

        self.switch_tbttn = QtWidgets.QToolButton()
        _set_size_policy(self.switch_tbttn, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.switch_tbttn.setMaximumSize(QtCore.QSize(16777215, 18))
        self.switch_tbttn.setFont(_font(size=9))
        self.switch_tbttn.setStyleSheet(
            u"background-color: rgb(100, 100, 100);\ncolor: rgb(200, 200, 200);")
        self.switch_tbttn.setText(u"Reference Switch")
        self.switch_tbttn.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.switch_tbttn.setAutoRaise(True)
        self.switch_tbttn.setArrowType(QtCore.Qt.DownArrow)
        verticalLayout_2.addWidget(self.switch_tbttn)

        self.switch_frame = QtWidgets.QFrame()
        _set_size_policy(self.switch_frame, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.switch_frame.setMaximumSize(QtCore.QSize(16777215, 60))
        self.switch_frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.switch_frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        verticalLayout_5 = QtWidgets.QVBoxLayout(self.switch_frame)
        verticalLayout_5.setSpacing(2)
        verticalLayout_5.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        verticalLayout_5.setContentsMargins(2, 2, 2, 2)

        horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.asset_all_rBttn = QtWidgets.QRadioButton()
        self.asset_all_rBttn.setText(u"All")
        self.asset_all_rBttn.setChecked(True)
        horizontalLayout_4.addWidget(self.asset_all_rBttn, 0, QtCore.Qt.AlignHCenter)
        self.asset_selected_rBttn = QtWidgets.QRadioButton()
        self.asset_selected_rBttn.setText(u"Selected")
        horizontalLayout_4.addWidget(self.asset_selected_rBttn, 0, QtCore.Qt.AlignLeft)
        verticalLayout_5.addLayout(horizontalLayout_4)

        horizontalLayout_5 = QtWidgets.QHBoxLayout()
        horizontalLayout_5.setSpacing(5)
        self.asset_switch_type_comb = QtWidgets.QComboBox()
        self.asset_switch_type_comb.setMinimumSize(QtCore.QSize(0, 24))
        self.asset_switch_type_comb.setMaximumSize(QtCore.QSize(16777215, 25))
        self.asset_switch_type_comb.setStyleSheet(u"background-color: rgb(43, 43, 43);")
        self.asset_switch_type_comb.addItem(u"all_rig")
        self.asset_switch_type_comb.addItem(u"hi_rig")
        self.asset_switch_type_comb.addItem(u"low_rig")
        horizontalLayout_5.addWidget(self.asset_switch_type_comb, 1)

        self.asset_ref_switch_bttn = QtWidgets.QPushButton()
        _set_size_policy(self.asset_ref_switch_bttn, QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        self.asset_ref_switch_bttn.setMaximumSize(QtCore.QSize(110, 25))
        self.asset_ref_switch_bttn.setFont(_font(family=u"SimSun"))
        self.asset_ref_switch_bttn.setStyleSheet(u"background-color: rgb(93, 93, 93);")
        self.asset_ref_switch_bttn.setText(u"Switch")
        horizontalLayout_5.addWidget(self.asset_ref_switch_bttn, 1)

        verticalLayout_5.addLayout(horizontalLayout_5)
        verticalLayout_2.addWidget(self.switch_frame)
        self.Attr_down_vLayout.addLayout(verticalLayout_2)

        self.Attr_down_vLayout.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))

        self.attr_splitter.addWidget(layoutWidget_4)
        self.mainWindow_splitter.addWidget(self.attr_splitter)

        # ============ 组装顶层布局 ============
        gridLayout_2.addWidget(self.mainWindow_splitter, 0, 0, 1, 1)
        gridLayout_2.addLayout(msg_Layout, 1, 0, 1, 1)

    def init_ui(self):
        """初始化 UI"""
        self.firstView()

        # 左侧边栏
        self.project_comb.currentIndexChanged.connect(self.projectChanged)
        self.type_treeWidget.itemSelectionChanged.connect(self.typeChanged)
        self.type_treeWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.type_treeWidget.customContextMenuRequested.connect(self.show_menu_type)

        self.Favorites_listWgt = faverWidget.FavoritesQListWiget(tab="Asset")
        self.type_splitter.addWidget(self.Favorites_listWgt)
        self.type_splitter.setSizes([500, 500])
        self.Favorites_listWgt.itemSelectionChanged.connect(self.faveChanged)

        # 上侧工具栏
        self.back_bttn.setIcon(QtGui.QIcon('%s/icon/back.png' % self.scriptsPath))
        self.back_bttn.clicked.connect(self.backToMainWgt)
        self.add_bttn.setIcon(QtGui.QIcon('%s/icon/add.png' % self.scriptsPath))
        self.add_bttn.clicked.connect(self.add_asset_ui)
        self.get_viewThumbnail_btn()
        self.displayThumb_bttn.clicked.connect(self.viewModeChanged)
        self.itemSize_Slider.valueChanged.connect(self.itemSizeSliderChanged)
        self.itemSize_Slider.setToolTip(str(self.itemSize_Slider.value()))
        self.itemSize_Slider.sliderReleased.connect(self.itemSizeSliderReleased)
        self.download_Bttn.setIcon(QtGui.QPixmap('%s/icon/download.png' % self.scriptsPath))
        self.download_Bttn.clicked.connect(self.download_asset)
        self.refresh_Bttn.setIcon(QtGui.QPixmap('%s/icon/refresh.png' % self.scriptsPath))
        self.refresh_Bttn.clicked.connect(self.refresh_asset)
        self.key_line.returnPressed.connect(self.search_asset)
        self.key_line.addAction(
            QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
            QtWidgets.QLineEdit.LeadingPosition
        )

        # 主界面 - 使用新的高性能组件
        self.ui_main_wgt = am_main_optimized.MainStackedWidget(
            db=self.project_comb.currentText(),
            tab="Asset",
            user=self.user,
            password=self.password,
            islist=self.isList
        )
        self.ui_main_wgt.setItemsWidget(self)
        self.ui_main_wgt.dragLeaveSignal_connect(self.mainWgtItemDragLeaved)
        self.ui_main_wgt.itemSelectionChanged_connect(self.mainWightItemChanged)
        self.ui_main_wgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui_main_wgt.customContextMenuRequested.connect(self.show_menu)
        self.verticalLayout_3.addWidget(self.ui_main_wgt)

        # 应用滑块当前值作为初始缩略图尺寸。
        # firstView() 在本控件创建之前就把滑块设成了上次保存的 thumbSize，但那时
        # ui_main_wgt 还不存在、valueChanged 也未连接，故初值不会传入视图——
        # 不补这一步，首次打开图标恒为默认 120，不随滑块。须在 show_asset() 流式
        # 加载条目之前设好，使新建条目即采用正确尺寸。
        self.ui_main_wgt.setItemSize(self.itemSize_Slider.value())

        # 设置分割器
        self.mainWindow_splitter.setSizes([200, 500, 300])
        self.mainWindow_splitter.setStretchFactor(0, False)
        self.mainWindow_splitter.setStretchFactor(1, True)
        self.mainWindow_splitter.setStretchFactor(2, False)

        # 右侧属性栏
        self.attr_splitter.setStretchFactor(1, False)
        self.attr_splitter.setSizes([300, 500])
        self.upload_Bttn.setIcon(QtGui.QIcon('%s/icon/cloud_upload.png' % self.scriptsPath))
        self.upload_Bttn.clicked.connect(self.addTagUI)
        self.capture_Bttn.setIcon(QtGui.QIcon('%s/icon/capture.png' % self.scriptsPath))
        self.capture_Bttn.clicked.connect(self.captureThumbnail)
        self.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
        self.favor_bttn.clicked.connect(self.addFavor)
        self.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
        self.tag_bttn.clicked.connect(self.addTagUI)
        # FBX 三维预览(纯 Python 解析 + 自写 OpenGL,完全不碰 Maya 场景)。
        # 回退:改回 previewWidget.PreviewWidget() 即恢复原 icon 图片预览。
        self.preview = previewGLWidget.PreviewGLWidget()
        self.preview_vLayout.addWidget(self.preview)
        self.preview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.preview.customContextMenuRequested.connect(self.show_menu_Preview_label)
        self.preview.playerEnabled(True)

        self.file_type_tbttn.clicked.connect(self.file_type_clicked)
        self.exportFbx_bttn.clicked.connect(self.exportFbx)
        self.switch_tbttn.clicked.connect(self.switch_clicked)
        self.asset_ref_switch_bttn.clicked.connect(self.copyKey)

    def file_type_clicked(self):
        """切换文件类型面板"""
        if self.file_type_expanded:
            self.file_type_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.file_type_frame.setVisible(False)
            self.file_type_expanded = False
        else:
            self.file_type_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.file_type_frame.setVisible(True)
            self.file_type_expanded = True

    def switch_clicked(self):
        """切换引用面板"""
        if self.switch_expanded:
            self.switch_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.switch_frame.setVisible(False)
            self.switch_expanded = False
        else:
            self.switch_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.switch_frame.setVisible(True)
            self.switch_expanded = True

    def rememberSettings(self):
        """保存设置"""
        settings = QtCore.QSettings('Assets', 'AssetsSettings')
        settings.setValue('isList', self.isList)
        settings.setValue('thumbSize', self.itemSize_Slider.value())
        settings.setValue('project', self.project_comb.currentIndex())
        # 树没有 row 概念，改存选中节点的 "tab|type" 文本
        tab, _type = self.current_type()
        settings.setValue('typ', "{0}|{1}".format(tab or "", _type or ""))

    def readSettings(self):
        """读取设置"""
        settings = QtCore.QSettings('Assets', 'AssetsSettings')
        isList = settings.value('isList')
        thumbSize = settings.value('thumbSize')
        project = settings.value('project')
        typ = settings.value('typ')

        if isList is not None:
            self.isList = (isList == 'true')
        return thumbSize, project, typ

    def firstView(self):
        """首次显示"""
        self.get_project()

        thumbSize, project, typ = self.readSettings()
        if thumbSize is not None:
            self.itemSize_Slider.setValue(int(thumbSize))
        if project is not None:
            self.project_comb.setCurrentIndex(int(project))
        else:
            self.project_comb.setCurrentIndex(0)

        # 项目定好后再建树（scene 类型随项目扫盘不同），最后恢复上次选中的节点。
        # 此处仍在 init_ui 里连接 itemSelectionChanged 之前，setCurrentItem 不会触发
        # typeChanged；首帧加载由 __init__ 末尾的 show_asset() 负责。
        self.get_type()
        self._restore_tree_selection(typ)

    def get_project(self):
        """获取项目列表"""
        self.project_comb.addItems(projectSetting()['DataBase'])

    def get_type(self):
        """构建左侧目录树：全部目录 > Assets/Scenes > 各类型。

        类型来自磁盘扫描 {ROOT}/{db}/{Assets|Scenes} 的子目录（子目录名即 DB 里
        asset.type / scene.type 的真实值，作为 SQL 过滤值）；Assets 扫不到时回退
        ['Characters','Props']。默认选中项记在 self._default_tree_item。
        """
        self.type_treeWidget.clear()
        db = self.currentProject()

        def _folder_icon():
            icon = QtGui.QIcon()
            pix = am_pixmap.Pixmap('%s/icon/folder.svg' % self.scriptsPath)
            pix.setColor(QtGui.QColor("#b3b3b3"))
            icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            return icon

        # 顶层“全部目录”节点（选中=横跨 asset+scene 全部类型，跑 UNION，最慢，不作默认）
        all_item = QtWidgets.QTreeWidgetItem()
        all_item.setText(0, u"全部目录")
        all_item.setData(0, ALL_ROLE, True)
        all_item.setIcon(0, _folder_icon())
        self.type_treeWidget.addTopLevelItem(all_item)

        assets_item = None
        default_item = None
        for tab in ["Assets", "Scenes"]:
            tab_item = QtWidgets.QTreeWidgetItem()
            tab_item.setText(0, tab)
            tab_item.setIcon(0, _folder_icon())
            all_item.addChild(tab_item)
            if tab == "Assets":
                assets_item = tab_item
            for _type in self._scan_types(db, tab):
                type_item = QtWidgets.QTreeWidgetItem()
                type_item.setText(0, _type)
                type_item.setIcon(0, _folder_icon())
                tab_item.addChild(type_item)
                if tab == "Assets" and _type == "Characters":
                    default_item = type_item
            tab_item.setExpanded(True)
        all_item.setExpanded(True)

        # 默认优先 Assets/Characters；退而选 Assets 首个类型 -> Assets 节点 -> 全部目录
        if default_item is None and assets_item is not None and assets_item.childCount() > 0:
            default_item = assets_item.child(0)
        if default_item is None:
            default_item = assets_item if assets_item is not None else all_item
        self._default_tree_item = default_item

    def _scan_types(self, db, tab):
        """扫描 {ROOT}/{db}/{tab} 的子目录作为类型；Assets 扫不到时回退 Characters/Props。"""
        folder = '{0}/{1}/{2}'.format(self.ROOT, db, tab)
        types = []
        if os.path.isdir(folder):
            try:
                types = sorted(d for d in os.listdir(folder)
                               if os.path.isdir(os.path.join(folder, d)))
            except OSError:
                types = []
        if not types and tab == "Assets":
            types = ["Characters", "Props"]
        return types

    def currentProject(self):
        """获取当前项目"""
        return str(self.project_comb.currentText())

    def current_type(self):
        """返回当前选中的检索范围 (tab, type)：
        ("All", None)              -> 全部目录，横跨 asset+scene 全部类型
        ("Assets"/"Scenes", None)  -> 选中某个 tab 节点，该表全部类型
        ("Assets"/"Scenes", 类型)  -> 选中具体类型
        (None, None)               -> 无有效选中
        """
        items = self.type_treeWidget.selectedItems()
        if not items:
            return None, None
        item = items[0]
        if item.data(0, ALL_ROLE):
            return "All", None
        parent = item.parent()
        if parent is None:
            return None, None
        if parent.data(0, ALL_ROLE):        # tab 节点（全部目录的直接子节点）
            return item.text(0), None
        return parent.text(0), item.text(0)  # 具体类型（parent 是 tab 节点）

    def currentType(self):
        """获取当前类型名（兼容旧调用点；选中 tab/全部目录时为空串）"""
        return self.current_type()[1] or ""

    def currentTab(self):
        """获取当前 tab（Assets/Scenes/All）；无选中时回退 self.tab。"""
        tab = self.current_type()[0]
        return tab if tab else getattr(self, "tab", "Assets")

    def _find_tree_item(self, tab, _type):
        """在目录树里找 (tab, type) 对应节点；_type 为空表示 tab 节点本身。"""
        root = self.type_treeWidget.topLevelItem(0)  # 全部目录
        if root is None:
            return None
        if tab == "All":
            return root
        for i in range(root.childCount()):
            tab_item = root.child(i)
            if tab_item.text(0) != tab:
                continue
            if not _type:
                return tab_item
            for j in range(tab_item.childCount()):
                if tab_item.child(j).text(0) == _type:
                    return tab_item.child(j)
        return None

    def _restore_tree_selection(self, typ):
        """按保存的 'tab|type' 文本恢复树选中；找不到回退默认节点(Assets/Characters)。"""
        target = None
        if typ and isinstance(typ, str) and "|" in typ:
            tab, _type = typ.split("|", 1)
            target = self._find_tree_item(tab, _type)
        if target is None:
            target = getattr(self, "_default_tree_item", None)
        if target is not None:
            self.type_treeWidget.setCurrentItem(target)

    @staticmethod
    def currentDate():
        """获取当前日期"""
        return time.strftime('%Y%m%d', time.localtime())

    def currentAsset(self):
        """获取当前资产名"""
        return self.ui_main_wgt.currentAsset()

    def projectChanged(self):
        """项目改变 -> 重建目录树（scene 类型随项目扫盘不同）再刷新展示"""
        self._asset_cache = []
        # get_type() 已 clear 树，_restore_tree_selection 的 setCurrentItem 必触发
        # typeChanged -> show_asset，无需在此再手动刷新。
        self.get_type()
        self._restore_tree_selection(None)
        self.rememberSettings()

    def typeChanged(self):
        """类型/tab 切换 -> 刷新展示（右侧面板在 show_asset 里按 tab 同步）"""
        tab = self.current_type()[0]
        if tab is None:
            return
        self.tab = tab
        self.rememberSettings()
        self.show_asset()
        self.Favorites_listWgt.setCurrentRow(-1)

    def faveChanged(self):
        """收藏改变"""
        if self.Favorites_listWgt.currentRow() != -1:
            self.type_treeWidget.clearSelection()
            self.ui_main_wgt.clear()
            if self.Favorites_listWgt.currentRow() == 0:
                data = self.Favorites_listWgt.get_favor_items()
            else:
                select = self.Favorites_listWgt.selectedItems()[0].text()
                data = self.Favorites_listWgt.get_tag_items(select)
            # 收藏 JSON 不存在时 readFaveDict 返回 {}、标签缺失时 get_tag_items 返回 None，
            # 直接喂给视图会在 addItems 里 for 迭代 None 报错——统一兜底成空列表。
            if not isinstance(data, list):
                data = []
            self.ui_main_wgt.setItemsList(data)
            self.ui_main_wgt.addItems(self.get_keywords())

    # ============ 数据查询优化 ============

    def show_asset(self, data=None):
        """显示资产/场景 - 按左侧目录选中范围 (tab, type) 分派查询"""
        self.ui_main_wgt.clear()
        self._asset_cache = []

        # 显示加载提示
        self.infoMsg("info", "Loading...")

        project = self.currentProject()
        tab, _type = self.current_type()
        keywords = self.get_keywords()
        if not project or tab is None:
            return

        self.tab = tab
        # 右侧属性面板按 tab 同步（scene 隐藏 asset 专属面板；混排时具体行由 mainWightItemChanged 再细分）
        self._apply_attr_panel(tab)
        if tab == "All":
            self._db_manager.queryAll(project, keywords)
        elif tab == "Scenes":
            self._db_manager.queryScenes(project, _type, keywords)
        else:  # Assets
            self._db_manager.queryAssets(project, _type, keywords)

    def _onAssetRowReady(self, row):
        """单行数据准备好 - 流式添加到列表"""
        self._asset_cache.append(row)
        # 可以在这里选择是否实时添加，为了性能建议批量添加
        # self.ui_main_wgt.addItem(row)

    def _onAssetsBatchReady(self, batch):
        """一批数据准备好"""
        # 批量添加到显示
        for row in batch:
            self.ui_main_wgt.addItem(row)

    def _onQueryError(self, error):
        """查询错误"""
        QtWidgets.QMessageBox.warning(
            self, u"提醒",
            u"你尚未登录ShotManager系统\n\n" + str(error)
        )
        self.infoMsg("error", str(error))

    def _onQueryFinished(self, total):
        """查询完成"""
        # 把完整数据交给视图，使图标/列表模式切换、关键字过滤可基于缓存重建
        # （流式加载是逐批 addItem 进视图的，视图内部的 _items_list 此前为空）
        self.ui_main_wgt.setItemsList(self._asset_cache)
        self.ui_main_wgt.resizeItem()
        self.infoMsg("info", f"加载到{total}个资产")

    # ============ 其他方法保持不变 ============

    def get_keywords(self):
        """获取关键词"""
        return [self.key_line.text().strip()]

    def search_asset(self):
        """搜索资产"""
        self.show_asset()

    def refresh_asset(self):
        """刷新资产"""
        self._asset_cache = []
        if not self.isAction:
            self.show_asset()
        else:
            self.update_action()

    def getPanelsData(self):
        """获取面板数据（路径按当前 tab 取 Assets/Scenes）"""
        __project = str(self.project_comb.currentText())
        tab, __type = self.current_type()
        __type = __type or ""
        folder = "Scenes" if tab == "Scenes" else "Assets"
        __path = '%s/%s/%s/%s' % (self.ROOT, __project, folder, __type)
        return __project, __type, __path

    def getCurrentItemsData(self):
        """获取当前选中项数据"""
        __item = self.ui_main_wgt.selectedItems()
        __fileType = self.fileType_bttnGroup.checkedButton().text()
        __folder = self.__fileTypeFolderDict[__fileType]
        if not __item:
            return None
        return __item, __fileType, __folder

    def mainWightItemChanged(self):
        """主面板选择项改变：按选中项归属表(asset/scene)切换右侧面板与预览。"""
        currentSelected = self.ui_main_wgt.selectedItems()
        self.preview.clear()
        if not currentSelected:
            return

        table = self._row_table_of_selected()
        self._apply_attr_panel(table)

        item = currentSelected[0]
        item_data = item.itemData()
        if not item_data:
            return

        # 预览标题 + 缩略图（asset/scene 用不同角标 key）
        self.preview.setTitle(item_data[1], item_data[2])
        if not self.isAction:
            icon_key = "scene" if table == "Scenes" else "asset_ch"
            self.preview.setPreviewPixmap(item_data[7], icon_key)

        if table == "Scenes":
            # scene 右侧已隐藏 File Type/Reference（简化占位），不做文件类型存在性检查
            self._sync_favor_tag_icon(item)
            return

        # ---- asset：按文件是否存在启用/禁用文件类型单选按钮 ----
        rBttn_dict = {
            'mod': self.mod_rBttn, 'hi_rig': self.hiRig_rBttn,
            'low_rig': self.lowRig_rBttn, 'all_rig': self.allRig_rBttn,
            'render': self.render_rBttn, 'xgen': self.xgen_rBttn,
            'AD': self.ad_rBttn, 'OAT': self.oat_rBttn
        }
        for btn in rBttn_dict.values():
            btn.setEnabled(True)
        for ty, btn in rBttn_dict.items():
            file_path = self.detailPath().get(ty, "")
            if file_path and not QtCore.QFileInfo(file_path).exists():
                btn.setEnabled(False)
        self._sync_favor_tag_icon(item)

    def _row_table_of_selected(self):
        """由选中项 icon 路径(itemData[7]) 判归属表：/Scenes/->Scenes、/Assets/->Assets；
        判不了回退当前 tab(self.tab)。用于全部目录/混排视图下区分某行属于哪张表。"""
        try:
            selected = self.ui_main_wgt.selectedItems()
            data = selected[0].itemData() if selected else None
            icon = data[7] if data and len(data) > 7 else ""
            if "/Scenes/" in str(icon):
                return "Scenes"
            if "/Assets/" in str(icon):
                return "Assets"
        except (IndexError, AttributeError, TypeError):
            pass
        return getattr(self, "tab", "Assets")

    def _apply_attr_panel(self, table):
        """asset/scene 右侧属性面板切换：scene 隐藏 asset 专属的 File Type / Reference
        Switch 面板（简化占位），只保留预览+标题；asset 显示折叠头，内容区遵循各自的
        展开状态（file_type_expanded / switch_expanded），不覆盖用户手动折叠。"""
        is_asset = (table != "Scenes")
        self.file_type_tbttn.setVisible(is_asset)
        self.switch_tbttn.setVisible(is_asset)
        self.file_type_frame.setVisible(is_asset and self.file_type_expanded)
        self.switch_frame.setVisible(is_asset and self.switch_expanded)

    def _sync_favor_tag_icon(self, item):
        """同步收藏/标签按钮图标到当前选中项的实际状态（以本地 JSON 为准）。"""
        try:
            favor_icon = 'star.png' if item.isFavor() else 'unStar.png'
            self.favor_bttn.setIcon(QtGui.QIcon('%s/icon/%s' % (self.scriptsPath, favor_icon)))
            tag_icon = 'tag.png' if item.isTag() else 'unTag.png'
            self.tag_bttn.setIcon(QtGui.QIcon('%s/icon/%s' % (self.scriptsPath, tag_icon)))
        except Exception:
            pass

    def detailPath(self):
        """获取文件路径"""
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            return {}

        for item in __item:
            item_data = item.itemData()
            base_path = item_data[7].split("Icon")[0] if len(item_data) > 7 else ""
            name = item_data[1] if len(item_data) > 1 else ""

            return {
                'hi_rig': "{0}/Rig/{1}_hi_rig.ma".format(base_path, name),
                'all_rig': "{0}/Rig/{1}_all_rig.ma".format(base_path, name),
                'low_rig': "{0}/Rig/{1}_low_rig.ma".format(base_path, name),
                'render': "{0}/Render/{1}_render.ma".format(base_path, name),
                'mod': "{0}/Mod/{1}_mod.ma".format(base_path, name),
                'xgen': '{0}/Xgen/{1}_xgen.ma'.format(base_path, name),
                'icon': item_data[7] if len(item_data) > 7 else "",
                'AD': '{0}/Assembly/{1}_AD.ma'.format(base_path, name),
                'OAT': '{0}/Rig/{1}_OAT.ma'.format(base_path, name)
            }
        return {}

    # ============ 视图模式切换 ============

    def get_viewThumbnail_btn(self):
        """获取视图按钮状态"""
        if self.isList:
            self.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.displayThumb_bttn.setToolTip("缩略图显示")
        else:
            self.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.displayThumb_bttn.setToolTip("表单显示")

    def viewModeChanged(self):
        """切换视图模式"""
        keyWords = self.get_keywords()
        itemSize = self.itemSize_Slider.value()

        if self.isList:
            # 切换到缩略图模式
            self.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.displayThumb_bttn.setToolTip("表单显示")
            self.isList = False
            self.ui_main_wgt.setIsList(False)
            self.ui_main_wgt.setIconMode(itemSize, keyWords)
        else:
            # 切换到列表模式
            self.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.displayThumb_bttn.setToolTip("缩略图显示")
            self.isList = True
            self.ui_main_wgt.setIsList(True)
            self.ui_main_wgt.setListMode(keyWords)

        self.rememberSettings()

    def itemSizeSliderChanged(self):
        """滑块值改变"""
        itemSize = self.itemSize_Slider.value()
        if self.isList:
            return
        else:
            self.ui_main_wgt.setItemSize(itemSize)
            self.ui_main_wgt.resizeItem()

    def itemSizeSliderReleased(self):
        """滑块释放"""
        itemSize = self.itemSize_Slider.value()
        self.itemSize_Slider.setToolTip(u"%s" % itemSize)
        self.rememberSettings()

    # ============ 右键菜单 ============

    def show_menu_type(self, point):
        """目录树右键菜单：空白处右键 -> 新建文件夹"""
        currentItem = self.type_treeWidget.itemAt(point)
        menu = QtWidgets.QMenu(self.type_treeWidget)
        if currentItem is None:
            addFolder_action = QtWidgets.QAction(u'新建文件夹', self)
            addFolder_action.setIcon(QtGui.QIcon("%s/icon/folderPlus.png" % self.scriptsPath))
            addFolder_action.triggered.connect(self._add_folder)
            menu.addAction(addFolder_action)
            menu.exec_(QtGui.QCursor.pos())

    def show_menu(self, point):
        """主面板右键菜单"""
        currentItem = self.ui_main_wgt.selectedItems()
        menu = QtWidgets.QMenu(self.ui_main_wgt)

        if currentItem:
            action_action = QtWidgets.QAction('Action', self)
            show_action = QtWidgets.QAction('Show in Explorer', self)
            show_action.setIcon(QtGui.QIcon("{}/icon/folder_white.png".format(self.scriptsPath)))
            imp_action = QtWidgets.QAction('Import...', self)
            impa_action = QtWidgets.QAction('Import Action...', self)
            ref_action = QtWidgets.QAction('Create Reference...', self)
            rep_action = QtWidgets.QAction('Replace Selected Reference', self)
            del_action = QtWidgets.QAction(u'删除...', self)
            apply_action = QtWidgets.QAction('Apply Action', self)

            if self.isAction:
                menu.addAction(apply_action)
                menu.addAction(show_action)
                menu.addAction(impa_action)
            else:
                menu.addAction(action_action)
                menu.addSeparator()
                menu.addAction(show_action)
                menu.addSeparator()
                menu.addAction(imp_action)
                menu.addAction(ref_action)
                menu.addAction(rep_action)
                menu.addAction(del_action)

            self.checkDir('Action', currentItem[0], action_action)

            action_action.triggered.connect(self.update_action)
            show_action.triggered.connect(partial(self.openDir, '', currentItem[0]))
            imp_action.triggered.connect(self.importFile)
            impa_action.triggered.connect(self.importAction)
            ref_action.triggered.connect(self.createRef)
            rep_action.triggered.connect(self.__replace_ref)
            del_action.triggered.connect(self.delete_asset)
            apply_action.triggered.connect(self.applyAction)

            menu.exec_(QtGui.QCursor.pos())
        else:
            modPublish_action = QtWidgets.QAction(u'发布模型资产', self)
            modPublish_action.setIcon(QtGui.QIcon("{}/icon/publish.png".format(self.scriptsPath)))
            modPublish_action.triggered.connect(lambda: self._showPublishTool(0))

            rigPublish_action = QtWidgets.QAction(u'发布绑定资产', self)
            rigPublish_action.setIcon(QtGui.QIcon("{}/icon/publish.png".format(self.scriptsPath)))
            rigPublish_action.triggered.connect(lambda: self._showPublishTool(1))

            refresh_action = QtWidgets.QAction(u'刷新', self)
            refresh_action.setIcon(QtGui.QIcon("{}/icon/refresh.png".format(self.scriptsPath)))
            refresh_action.triggered.connect(self.refresh_asset)

            menu.addAction(modPublish_action)
            menu.addAction(rigPublish_action)
            menu.addSeparator()
            menu.addAction(refresh_action)
            menu.exec_(QtGui.QCursor.pos())

    def _showPublishTool(self, tab):
        """打开发布工具"""
        import tools_publish.PublishTools.PublishTool as PT
        PT.showWindow(tab=tab)

    def show_menu_Preview_label(self, point):
        """预览窗口右键菜单"""
        currentItem = self.ui_main_wgt.selectedItems()
        if not currentItem:
            return

        menu = QtWidgets.QMenu(self.ui_main_wgt)
        action_action = QtWidgets.QAction('Action', self)
        show_action = QtWidgets.QAction('Show in Explorer', self)
        show_action.setIcon(QtGui.QIcon("{}/icon/folder_white.png".format(self.scriptsPath)))
        imp_action = QtWidgets.QAction('Import', self)
        impa_action = QtWidgets.QAction('Import Action', self)
        ref_action = QtWidgets.QAction('Create Reference', self)
        apply_action = QtWidgets.QAction('Apply Action', self)
        icon_action = QtWidgets.QAction('RePublish Icon', self)
        icon_action.setIcon(QtGui.QIcon("{}/icon/shot.png".format(self.scriptsPath)))

        if self.isAction:
            menu.addAction(apply_action)
            menu.addAction(show_action)
            menu.addAction(impa_action)
        else:
            menu.addAction(action_action)
            menu.addAction(show_action)
            menu.addAction(imp_action)
            menu.addAction(ref_action)
            menu.addSeparator()
            menu.addAction(icon_action)

        self.checkDir('Action', currentItem[0], action_action)

        action_action.triggered.connect(self.update_action)
        show_action.triggered.connect(partial(self.openDir, '', currentItem[0]))
        imp_action.triggered.connect(self.importFile)
        impa_action.triggered.connect(self.importAction)
        ref_action.triggered.connect(self.createRef)
        apply_action.triggered.connect(self.applyAction)

        menu.exec_(QtGui.QCursor.pos())

    # ============ 其他方法 ============

    def _add_folder(self):
        """在当前 tab（Assets/Scenes）目录下新建一个类型文件夹，然后重建目录树并选中它。"""
        project = self.project_comb.currentText()
        tab = self.currentTab()
        if tab == "All":
            tab = "Assets"
        path = '{0}/{1}/{2}'.format(self.ROOT, project, tab)
        res = self.Pub.create_new_folder(self, path)
        if res:
            self.get_type()
            target = self._find_tree_item(tab, res)
            if target is not None:
                self.type_treeWidget.setCurrentItem(target)

    def captureThumbnail(self):
        """屏幕截图 -> 覆盖为当前资产的 icon -> (图标模式下)刷新该图标。

        复用 PublishTools 的交互式截图：框选后在工具栏点“确定”/回车/双击，
        capture.ToolBar.ok_do_it() 会把截图存到
        %APPDATA%/AssetsManagerIconTemp/snapshot/thumbnail.png 并回调 self.set_thumbnail()。
        """
        currentSelected = self.ui_main_wgt.selectedItems()
        if not currentSelected:
            self.infoMsg('warning', u'请先选中一个资产')
            return
        item = currentSelected[0]
        item_data = item.itemData()
        if not item_data or len(item_data) <= 7 or not item_data[7]:
            self.infoMsg('warning', u'当前资产没有有效的 icon 路径')
            return

        # 记下截图目标(icon 路径 + 条目)，供异步回调 set_thumbnail 使用；
        # 截图过程中即使改变选择，也以点截图时选中的资产为准。
        self._capture_icon_path = item_data[7]
        self._capture_item = item

        try:
            from tools_publish.PublishTools import capture
            capture.show_capture_screen(self)
        except Exception as e:
            self.infoMsg('error', u'截图启动失败: %s' % e)

    def set_thumbnail(self):
        """截图完成回调(capture.ToolBar 通过 ScreenShot.send_back 调用)：
        把临时截图覆盖到资产 icon 并刷新显示。
        """
        icon_path = getattr(self, "_capture_icon_path", "")
        if not icon_path:
            return
        # 与 capture.ToolBar 的保存位置保持一致
        snapshot = "{}/AssetsManagerIconTemp/snapshot/thumbnail.png".format(os.environ.get('APPDATA'))
        pixmap = QtGui.QPixmap(snapshot)
        if pixmap.isNull():
            self.infoMsg('error', u'读取截图失败')
            return

        icon_dir = os.path.dirname(icon_path)
        if icon_dir and not os.path.exists(icon_dir):
            os.makedirs(icon_dir)
        if not pixmap.save(icon_path, "PNG"):
            self.infoMsg('error', u'icon 保存失败: %s' % icon_path)
            return

        self._refreshAssetIcon(icon_path, getattr(self, "_capture_item", None))
        self.infoMsg('info', u'已更新 icon: %s' % os.path.basename(icon_path))

    def _refreshAssetIcon(self, icon_path, item):
        """icon 文件被覆盖后刷新显示：失效缩略图缓存 + (图标模式下)复位条目并重载。"""
        # 路径不变、内容已变，必须把旧 pixmap 从缓存剔除，否则一直读旧图
        try:
            from widgets.am_thumbnail_loader import ThumbnailWorker
            ThumbnailWorker.removeCachedPixmap(icon_path)
        except Exception:
            pass

        # 仅图标(微缩图)模式需要刷新主视图里的缩略图；列表模式不显示 icon
        if not self.isList and item is not None and hasattr(item, "resetThumbnail"):
            try:
                item.resetThumbnail()        # 复位 loaded/loading 标志，允许重新请求
                item._thumbnail_pixmap = None
                item._pixmap_scaled = None
                item._pixmap_scaled_key = None
                item.loadThumbnail()         # 重新异步加载(缓存已失效->从磁盘读新图)
                item._repaintHost()
            except Exception:
                pass

    def addFavor(self):
        """添加收藏"""
        currentSelected = self.ui_main_wgt.selectedItems()
        if currentSelected:
            # 获取实际的 item（ListItemOptimized 或 TableItem）
            item = currentSelected[0]
            if not item.isFavor():
                item.setFavor(True)
                self.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))
            else:
                item.setFavor(False)
                self.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))

    def addTagUI(self):
        """添加标签 UI"""
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(300, 95)
        Dialog.setWindowTitle(u"Create Tag")

        label = QtWidgets.QLabel(Dialog)
        label.setText(u"新建一个标签或选择已有标签：")

        lineEdit = QtWidgets.QLineEdit(Dialog)
        comb = QtWidgets.QComboBox(Dialog)
        bttnBox = QtWidgets.QDialogButtonBox(Dialog)
        bttnBox.setOrientation(QtCore.Qt.Horizontal)
        bttnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        tag_list = self.Favorites_listWgt.readTagDict().keys()
        comb.addItems(tag_list)
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 1, 1, 2)
        lay.addWidget(lineEdit, 1, 1, 1, 1)
        lay.addWidget(comb, 2, 1, 1, 1)
        lay.addWidget(bttnBox, 3, 1, 1, 1)

        def _addTag():
            tag = comb.currentText()
            if lineEdit.text():
                tag = lineEdit.text()

            currentSelected = self.ui_main_wgt.selectedItems()
            if currentSelected:
                currentSelected[0].setTag(tag)
                if tag == "":
                    self.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
                else:
                    self.tag_bttn.setIcon(QtGui.QIcon('%s/icon/tag.png' % self.scriptsPath))
                    _item = QtWidgets.QListWidgetItem(tag)
                    _icon = QtGui.QIcon(QtGui.QPixmap('%s/icon/tag.png' % self.scriptsPath))
                    _item.setIcon(_icon)
                    self.Favorites_listWgt.addItem(_item)
            Dialog.close()

        bttnBox.accepted.connect(_addTag)
        bttnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()

    def backToMainWgt(self):
        """返回主面板"""
        self.preview.clear()
        self.preview.playerEnabled(False)
        self.isAction = False
        self.refresh_asset()
        self.back_bttn.setEnabled(False)
        self.itemSize_Slider.setEnabled(True)

    def update_action(self):
        """更新动作库"""
        currentSelected = self.ui_main_wgt.selectedItems()
        if currentSelected:
            self.currentAssetData = currentSelected[0].itemData()
        # 动作库显示逻辑...
        pass

    def mainWgtItemDragLeaved(self):
        """拖拽离开主面板"""
        self.install_maya_eventFilter()

    def install_maya_eventFilter(self):
        """安装 Maya 事件过滤器"""
        print("install maya event filter!")
        self.mayaMainWindow.installEventFilter(self)

    def remove_maya_eventFilter(self):
        """移除 Maya 事件过滤器"""
        print("remove maya event filter!")
        self.mayaMainWindow.removeEventFilter(self)

    def eventFilter(self, receiver, event):
        """事件过滤"""
        self.receiver = receiver
        self.mouse_button = QtWidgets.QApplication.mouseButtons()
        if event.type() == QtCore.QEvent.Enter:
            self.drag_drop_happened()
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.remove_maya_eventFilter()
            return True
        return False

    def drag_drop_happened(self):
        """拖拽发生"""
        menu = QtWidgets.QMenu(self.mayaMainWindow)
        action_a = QtWidgets.QAction(u"Import...", menu)
        action_a.triggered.connect(self.importFile)
        action_b = QtWidgets.QAction(u"Create Reference...", menu)
        action_b.triggered.connect(self.createRef)
        menu.addAction(action_a)
        menu.addAction(action_b)
        menu.popup(QtGui.QCursor.pos())
        self.remove_maya_eventFilter()

    # ============ 文件操作 ============

    def openDir(self, _type, item):
        """打开文件夹"""
        paths = self.detailPath()
        if not paths:
            return
        hi_rig_path = paths.get('hi_rig', '')
        if not hi_rig_path:
            return
        folder_path = hi_rig_path.split('Rig')[0]
        if _type:
            folder_path = '{0}/{1}'.format(folder_path, _type)
        if QtCore.QFileInfo(folder_path).exists():
            QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(folder_path))
        else:
            self.infoMsg('warning', 'Can not find {0}'.format(folder_path))

    def checkDir(self, _type, item, action):
        """检查目录是否存在"""
        item_data = item.itemData()
        if len(item_data) <= 7:
            return
        folder_path = item_data[7].split("Icon")[0]
        folder_path = '{0}/{1}'.format(folder_path, _type)
        action.setEnabled(QtCore.QFileInfo(folder_path).exists())

    def importFile(self):
        """导入文件"""
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            self.infoMsg('warning', 'Please select Character!!!')
            return

        for item in __item:
            item_data = item.itemData()
            file_path = self.detailPath().get(__fileType, "")
            if QtCore.QFileInfo(file_path).exists():
                rpr = '%s_%s' % (item_data[1], __fileType)
                cmds.file(file_path, i=True, type='mayaAscii',
                         mergeNamespacesOnClash=False, renamingPrefix=rpr,
                         ignoreVersion=True, options='v=0;',
                         preserveReferences=True, importFrameRate=True,
                         importTimeRange='override')
            else:
                self.infoMsg('warning', 'Can not find {0}'.format(file_path))

    def importAction(self):
        """导入动作"""
        currentSelected = self.ui_main_wgt.selectedItems()
        if not currentSelected:
            return
        item_data = currentSelected[0].itemData()
        # 动作库导入逻辑...
        pass

    def createRef(self):
        """创建引用"""
        __project, __type, __path = self.getPanelsData()
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            self.infoMsg('warning', 'Please select Character!!!')
            return

        if __type == 'Sets':
            __fileType = 'AD'

        for item in __item:
            item_data = item.itemData()
            file_path = self.detailPath().get(__fileType, "")
            if not QtCore.QFileInfo(file_path).exists():
                self.infoMsg('warning', 'Can not find {0}'.format(file_path))
                continue

            if __type == 'Sets':
                assembly_name = cmds.assembly(name=item_data[1], type='assemblyReference')
                cmds.setAttr('{0}.definition'.format(assembly_name), file_path, type='string')
            else:
                nameSpace = '{0}_{1}'.format(item_data[1], __fileType)
                cmds.file(file_path, reference=True, type='mayaAscii',
                         ignoreVersion=True, groupLocator=True,
                         options='v=0;', mergeNamespacesOnClash=False,
                         namespace=nameSpace)

    def __replace_ref(self):
        """替换引用"""
        try:
            select = cmds.ls(sl=1)[0]
            namespace = select.split(":")[0]
        except:
            self.infoMsg('warning', u'请选中需要被替换的资产')
            return

        selectRef = "%sRN" % namespace

        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            self.infoMsg('warning', 'Please select Character!!!')
            return

        new_asset_path = self.detailPath().get(__fileType, "")
        if not new_asset_path:
            return

        new_namespace = new_asset_path.split("/")[-1].split(".ma")[0]

        cmds.file(new_asset_path, loadReference=selectRef, options="v=0;")

    def delete_asset(self):
        """删除资产"""
        print("Deleting asset...")
        result = QtWidgets.QMessageBox.warning(
            self, u"警告",
            u"删除数据表的操作是不可逆的，但服务器文件夹还在，确定要删除吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if result == QtWidgets.QMessageBox.Yes:
            if self._row_table_of_selected() == "Scenes":
                self.del_scene(self.currentProject(), self.currentAsset())
            else:
                self.del_asset(self.currentProject(), self.currentAsset())
            self.show_asset()

    def del_asset(self, db, asset_name):
        """删除资产"""
        import psycopg2
        print("Deleting asset: %s from database: %s" % (asset_name, db))
        delete_script = '''
            DELETE FROM public.asset
            WHERE "asset.name" = '%s';
        ''' % asset_name
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(
                database=db, user=self.user,
                password=self.password, host=self.host, port="5432"
            )
            cur = conn.cursor()
            cur.execute(delete_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告：", str(e))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def add_asset_ui(self):
        """添加资产/场景 UI（按当前 tab 决定写 asset 还是 scene 表、建对应目录）"""
        tab = self.currentTab()
        if tab == "All":
            tab = "Assets"
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(300, 195)
        Dialog.setWindowTitle(u"Add Scene" if tab == "Scenes" else u"Add Asset")
        font = QtGui.QFont("Microsoft YaHei UI", 10)
        Dialog.setFont(font)

        label = QtWidgets.QLabel(Dialog)
        label.setText(u"创建一个新资产：")

        proj_comb = QtWidgets.QComboBox(Dialog)
        proj_comb.addItems(projectSetting()["DataBase"])
        proj_comb.setCurrentText(self.currentProject())
        type_comb = QtWidgets.QComboBox(Dialog)
        type_comb.addItems(self._scan_types(self.currentProject(), tab))
        _cur_type = self.current_type()[1]
        if _cur_type:
            type_comb.setCurrentText(_cur_type)
        name_line = QtWidgets.QLineEdit(Dialog)
        name_line.setPlaceholderText("name")
        zh_name_line = QtWidgets.QLineEdit(Dialog)
        zh_name_line.setPlaceholderText(u"中文名")

        btnBox = QtWidgets.QDialogButtonBox(Dialog)
        btnBox.setOrientation(QtCore.Qt.Horizontal)
        btnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 1, 1, 2)
        lay.addWidget(proj_comb, 1, 1, 1, 1)
        lay.addWidget(type_comb, 2, 1, 1, 1)
        lay.addWidget(name_line, 3, 1, 1, 1)
        lay.addWidget(zh_name_line, 4, 1, 1, 1)
        lay.addWidget(btnBox, 5, 1, 1, 1)

        def _add_asset():
            db = proj_comb.currentText()
            date = self.currentDate()
            name = name_line.text()
            zh_name = zh_name_line.text()
            artist = str(self.user)
            _type = type_comb.currentText()
            if tab == "Scenes":
                self.add_scene(db, date, name, zh_name, artist, _type)
                self.make_scene_dirs(db, _type, name)
            else:
                self.add_asset(db, date, name, zh_name, artist, _type)
                self.make_dirs(db, _type, name)
            self.show_asset()
            Dialog.close()

        btnBox.accepted.connect(_add_asset)
        btnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()

    def add_asset(self, db, date, name, zh_name, mod_artist, _type):
        """添加资产到数据库"""
        import psycopg2
        icon = "Y:/MCCProject/{0}/Assets/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.asset ("asset.date", "asset.name", "asset.zh_name",
                "asset.mod_artist", "asset.mod_status", "asset.icon", "asset.type")
            VALUES ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text,
                '未开始'::text, '%s'::text, '%s'::text)
            returning asset."asset.name";
        ''' % (date, name, zh_name, mod_artist, icon, _type)

        conn = None
        cur = None
        try:
            conn = psycopg2.connect(
                database=db, user=self.user,
                password=self.password, host=self.host, port="5432"
            )
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告：", str(e))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    @staticmethod
    def make_dirs(db, asset_type, asset_name):
        """创建目录"""
        path = "Y:/MCCProject/{0}/Assets/{1}/{2}".format(db, asset_type, asset_name)
        if not os.path.exists(path):
            os.makedirs(path)

        folders = ["/Action", "/Design", "/FBX", "/Icon", "/Image",
                   "/Mod", "/Original", "/Rig", "/Texture"]
        for folder in folders:
            folder_path = path + folder
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

    @staticmethod
    def make_scene_dirs(db, _type, name):
        """创建 scene 目录结构（与 sceneTools.make_dirs 一致）"""
        path = "Y:/MCCProject/{0}/Scenes/{1}/{2}".format(db, _type, name)
        if not os.path.exists(path):
            os.makedirs(path)
        for sub in ["/Assembly", "/FBX", "/GPU", "/Icon", "/Mod",
                    "/Original", "/Port", "/Proxy", "/Texture"]:
            sub_path = path + sub
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)

    def add_scene(self, db, date, name, zh_name, artist, _type):
        """新增场景到 public.scene"""
        import psycopg2
        icon = "Y:/MCCProject/{0}/Scenes/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.scene ("scene.date", "scene.name", "scene.zh_name", "scene.artist",
                "scene.status", "scene.icon", "scene.type")
            VALUES ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text,
                '未开始'::text, '%s'::text, '%s'::text)
            returning scene."scene.name";
        ''' % (date, name, zh_name, artist, icon, _type)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(
                database=db, user=self.user,
                password=self.password, host=self.host, port="5432"
            )
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告：", str(e))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def del_scene(self, db, scene_name):
        """删除场景"""
        import psycopg2
        delete_script = '''
            DELETE FROM public.scene
            WHERE "scene.name" = '%s';
        ''' % scene_name
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(
                database=db, user=self.user,
                password=self.password, host=self.host, port="5432"
            )
            cur = conn.cursor()
            cur.execute(delete_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告：", str(e))
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def download_asset(self):
        """下载资产"""
        # 下载逻辑...
        pass

    def exportFbx(self):
        """导出 FBX"""
        # 导出逻辑...
        pass

    def copyKey(self):
        """拷贝关键帧"""
        # 拷贝逻辑...
        pass

    def applyAction(self):
        """应用动作"""
        pass

    def infoMsg(self, icon, text):
        """显示消息"""
        messageBox.show_msg(self.msg_icon_label, icon,
                           self.msg_label, text)
