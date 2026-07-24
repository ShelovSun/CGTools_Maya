#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Shelov<175702994@qq.com>
# log: 添加mini模式

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import json
from config import projectSetting, sm_Temp, am_Temp, SMConfig

import psycopg2

from PySide2 import QtUiTools
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from my_mutils.scriptjob import ScriptJob
from my_vendor.Qt import QtCore
from my_vendor.Qt import QtGui
from my_vendor.Qt import QtWidgets
import shiboken2
from shiboken2 import wrapInstance
from sources import assetTools_optimized as assetTools  #, sceneTools, actionTools, ShotsManager_Maya, rigTools, modTools#, xgenTools#, list_items（scene 已并入 asset 资产库，Scene tab 移除）
from utils import jsonHelper


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


# 固定的控件名：稳定名是 workspaceControl 跨会话持久化（记住停靠）的前提。
# 复用同一实例后同一时刻只有一个窗口，无需再用 uuid 防重名。
OBJECT_NAME = 'assetsManagerMainWindow'
WORKSPACE_CONTROL = OBJECT_NAME + 'WorkspaceControl'  # Maya 自动生成的 workspaceControl 名

_mayaCloseScriptJob = None
win = None  # 当前活动的窗口实例，供 mayaClosedEvent 在 Maya 退出时保存设置


def enableMayaClosedEvent():
    """
    Create a Maya script job to trigger on the event "quitApplication".
    Enable the Maya closed event to save the library settings on close
    :rtype: None
    """
    global _mayaCloseScriptJob
    if not _mayaCloseScriptJob:
        event = ['quitApplication', mayaClosedEvent]
        try:
            _mayaCloseScriptJob = ScriptJob(event=event)
            print("Maya close event enabled")
        except NameError as error:
            print(error)


def disableMayaClosedEvent():
    """Disable the maya closed event."""
    global _mayaCloseScriptJob
    if _mayaCloseScriptJob:
        _mayaCloseScriptJob.kill()
        _mayaCloseScriptJob = None
        print("Maya close event disabled")


def mayaClosedEvent():
    """
    Maya 退出时触发：保存当前活动窗口的设置。
    注意要保存的是已存在的实例 win，而不是 AssetsManagerUI() 新建的临时实例
    （新建实例保存的是默认状态，等于没保存）。
    :rtype: None
    """
    print("close")
    global win
    try:
        if win is not None:
            win.rememberSettings()
    except Exception as e:
        print(e)


class AssetsManagerUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):

    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
    MYPREFSDIR = cmds.internalVar(userPrefDir=True)  # Result: u'C:/Users/asus/Documents/maya/2019/prefs/'
    MAYADir = os.environ.get('MAYA_APP_DIR')  # Result: 'C:/Users/asus/Documents/maya'
    SM_SETTING_JSON = "{}/setting.json".format(sm_Temp())  # 旧版的把登录设置在这里
    VERSION = "5.0.1"
    user_list = list(projectSetting()["user_list"].values())

    def __init__(self, parent=maya_main_window()):
        super(AssetsManagerUI, self).__init__(parent)

        self._isLoaded = False  # 首次 showEvent 恢复几何用（仿 StudioLibrary）
        self.mayaMainWindow = maya_main_window()
        self.mayaMainWindow.setAcceptDrops(True)

        self.setObjectName(OBJECT_NAME)  # 固定名，供 workspaceControl 跨会话持久化

        self.setWindowTitle('Asset Manager ' + self.VERSION)
        self.setWindowIcon(QtGui.QIcon('%s/icon/blank_ch.png' % self.scriptsPath))

        self.isMini = False
        self.readSettings()

        self.host = SMConfig().getPrefsValue("General/ip", "10.0.203.34")
        try:  # 优先读取am_maya自己的登录设置，读取失败再读取SMConfig的设置（兼容之前版本的登录设置）
            self.user = self.readLoginSetting()['user']
            self.password = self.readLoginSetting()['password']
        except Exception as e:
            self.user = SMConfig().getPrefsValue("Info/user", "")
            self.password = SMConfig().getPrefsValue("Info/password", "")

        self.font = QtGui.QFont()
        self.font.setFamily(u"Microsoft YaHei UI")
        self.font.setPointSize(10)

        # self.miniSearchThread = myWidget.MyThread()
        # self.miniSearchThread.signal.connect(self._miniSearch)

        if self.isMini:
            self.init_ui_mini()
        else:
            self.init_ui()

        # cmds.workspaceControl(name , e=1, cc = self.closeEvent())

    def init_ui(self):
        """主程序外观界面（原 ui/AssetsManager.ui，改为代码构建）"""
        self.setupMainUi()
        # 解除 mini 模式对窗口尺寸的固定约束，恢复主界面可自由缩放
        self.setMinimumSize(QtCore.QSize(0, 0))
        self.setMaximumSize(QtCore.QSize(16777215, 16777215))  # QWIDGETSIZE_MAX
        '''风格外观'''
        # 默认尺寸；已保存的几何在 show() 之后由 _restoreGeometry() 恢复
        # （此处 workspaceControl 尚未创建，move/resize 会被随后的 show 覆盖丢失）。
        self.resize(950, 600)
        _, _, tab = self.readSettings()

        if tab is not None:
            self.tabWidget.setCurrentIndex(tab)
        else:
            self.tabWidget.setCurrentIndex(0)
        # self.getStyleSheet()
        '''角标栏'''
        self.login_bttn = QtWidgets.QPushButton(self)
        self.login_bttn.setIcon(QtGui.QIcon("%s/icon/user.png" % self.scriptsPath))
        self.login_bttn.setMinimumWidth(100)
        self.login_bttn.setFont(self.font)
        self.setting_bttn = QtWidgets.QPushButton()
        self.setting_bttn.setIcon(QtGui.QIcon('%s/icon/setting.png' % self.scriptsPath))
        self.setting_bttn.setFlat(True)
        self.setting_bttn.clicked.connect(self.toolSetting_UI)
        user_menu = QtWidgets.QMenu(self)
        action_c = QtWidgets.QAction(u"登录", self)
        action_c.triggered.connect(self.login_UI)
        action_a = QtWidgets.QAction(u"退出登录", self)
        action_a.triggered.connect(self.user_out)
        action_b = QtWidgets.QAction(u"修改密码", self)
        action_b.triggered.connect(self.reset_password)
        user_menu.addAction(action_c)
        user_menu.addSeparator()
        user_menu.addAction(action_a)
        user_menu.addAction(action_b)
        self.login_bttn.setMenu(user_menu)

        hLayout = QtWidgets.QHBoxLayout()
        hLayout.setContentsMargins(0, 3, 10, 0)
        hLayout.addWidget(self.login_bttn)
        hLayout.addWidget(self.setting_bttn)
        Frame = QtWidgets.QFrame(self)
        Frame.setLayout(hLayout)
        self.tabWidget.setCornerWidget(Frame, corner=QtCore.Qt.TopRightCorner)

        shrink_btn = QtWidgets.QPushButton()
        shrink_btn.setIcon(QtGui.QIcon('%s/icon/shrink.png' % self.scriptsPath))
        shrink_btn.setFlat(True)
        shrink_btn.setMaximumSize(QtCore.QSize(11, 11))
        shrink_btn.clicked.connect(self.shrinkWin)
        self.tabWidget.setCornerWidget(shrink_btn, corner=QtCore.Qt.TopLeftCorner)

        if self.user != "" and self.password != "":
            self.login_bttn.setText(self.user)
        else:
            self.login_bttn.setText(u"未登录")

        # self.tabWidget.setTabIcon(0, QtGui.QPixmap('%s/icon/miniSetting.png' % self.scriptsPath))  # 可以的但并不好看
        self.tabChanged()
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # name = self.workspaceControlName()
        # print(name)# None

    def setupMainUi(self):
        """构建主界面控件"""
        centralwidget = QtWidgets.QWidget()
        centralwidget.setMinimumSize(QtCore.QSize(300, 40))
        gridLayout_10 = QtWidgets.QGridLayout(centralwidget)
        gridLayout_10.setContentsMargins(0, 0, 0, 0)
        gridLayout_10.setSpacing(0)
        gridLayout_2 = QtWidgets.QGridLayout()
        # 原 .ui 仅设置 topMargin=0，其余边距沿用默认（-1 表示默认）。
        gridLayout_2.setContentsMargins(-1, 0, -1, -1)
        gridLayout_2.setSpacing(0)

        self.tabWidget = QtWidgets.QTabWidget(centralwidget)
        font = QtGui.QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        self.tabWidget.setFont(font)
        self.tabWidget.setTabPosition(QtWidgets.QTabWidget.North)
        self.tabWidget.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.tabWidget.setUsesScrollButtons(True)
        self.tabWidget.setDocumentMode(False)
        self.tabWidget.setTabsClosable(False)

        # asset_page（唯一显式设置 sizePolicy 的标签页）
        self.asset_page = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.asset_page.sizePolicy().hasHeightForWidth())
        self.asset_page.setSizePolicy(sizePolicy)
        gridLayout_4 = QtWidgets.QGridLayout(self.asset_page)
        gridLayout_4.setContentsMargins(2, 3, 2, 0)
        gridLayout_4.setSpacing(0)
        self.tabWidget.addTab(self.asset_page, u"Asset")

        gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        gridLayout_10.addLayout(gridLayout_2, 0, 0, 1, 1)
        self.setCentralWidget(centralwidget)

    def init_ui_mini(self):
        """mini 搜索条外观界面（原 ui/AssetsManager_mini.ui，改为代码构建）"""
        self.setupMiniUi()
        '''风格外观'''
        # 位置在 show() 之后由 _restoreGeometry() 恢复（此处 workspaceControl 尚未创建）
        self.setFixedHeight(41)
        self.setMinimumWidth(200)
        self.resize(350, 41)
        self._resizeFloatingWindow(350, 41)
        self.key_line.addAction(QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
                                QtWidgets.QLineEdit.LeadingPosition)
        self.shrink_bttn.setIcon(QtGui.QIcon('%s/icon/shrink.png' % self.scriptsPath))
        self.shrink_bttn.clicked.connect(self.shrinkWin)
        self.miniSetting_bttn.setIcon(QtGui.QIcon('%s/icon/miniSetting.png' % self.scriptsPath))
        # self.miniSetting_bttn.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.miniSetting_bttn.customContextMenuRequested.connect(self.miniSetting_UI)

        self.setting_menu = QtWidgets.QMenu()
        self.action_a = QtWidgets.QAction(u"Assets", self)
        self.action_a.setCheckable(True)
        self.action_a.setChecked(True)
        self.action_b = QtWidgets.QAction(u"Scenes", self)
        self.action_b.setCheckable(True)
        self.action_b.setChecked(True)
        self.setting_menu.addAction(self.action_a)
        self.setting_menu.addAction(self.action_b)
        self.miniSetting_bttn.setMenu(self.setting_menu)

        self.key_line.returnPressed.connect(self.miniSearch)

    def setupMiniUi(self):
        """构建 mini 搜索条控件"""
        centralwidget = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(centralwidget.sizePolicy().hasHeightForWidth())
        centralwidget.setSizePolicy(sizePolicy)
        # 高度固定 40，宽度可自由拉伸（不再锁死 350），让窗口能横向延展
        centralwidget.setMinimumSize(QtCore.QSize(200, 40))
        centralwidget.setMaximumSize(QtCore.QSize(16777215, 40))

        verticalLayout_2 = QtWidgets.QVBoxLayout(centralwidget)
        verticalLayout_2.setSpacing(0)
        verticalLayout_2.setContentsMargins(1, 1, 1, 0)
        verticalLayout = QtWidgets.QVBoxLayout()
        verticalLayout.setSpacing(0)
        horizontalLayout = QtWidgets.QHBoxLayout()

        self.shrink_bttn = QtWidgets.QPushButton(centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.shrink_bttn.sizePolicy().hasHeightForWidth())
        self.shrink_bttn.setSizePolicy(sizePolicy)
        self.shrink_bttn.setMaximumSize(QtCore.QSize(12, 12))
        self.shrink_bttn.setText("")
        self.shrink_bttn.setIconSize(QtCore.QSize(12, 12))
        self.shrink_bttn.setFlat(True)
        horizontalLayout.addWidget(self.shrink_bttn)

        spacerItem = QtWidgets.QSpacerItem(
            20, 13, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum
        )
        horizontalLayout.addItem(spacerItem)

        self.miniSetting_bttn = QtWidgets.QPushButton(centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.miniSetting_bttn.sizePolicy().hasHeightForWidth())
        self.miniSetting_bttn.setSizePolicy(sizePolicy)
        self.miniSetting_bttn.setMinimumSize(QtCore.QSize(12, 12))
        self.miniSetting_bttn.setMaximumSize(QtCore.QSize(12, 12))
        self.miniSetting_bttn.setText("")
        self.miniSetting_bttn.setIconSize(QtCore.QSize(12, 12))
        self.miniSetting_bttn.setFlat(True)
        horizontalLayout.addWidget(self.miniSetting_bttn)

        verticalLayout.addLayout(horizontalLayout)

        self.key_line = QtWidgets.QLineEdit(centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.key_line.sizePolicy().hasHeightForWidth())
        self.key_line.setSizePolicy(sizePolicy)
        # 高度固定 25，宽度随窗口拉伸延展（不再锁死 350）
        self.key_line.setMinimumSize(QtCore.QSize(25, 25))
        self.key_line.setMaximumSize(QtCore.QSize(16777215, 25))
        self.key_line.setPlaceholderText(u"Search...")
        self.key_line.setClearButtonEnabled(True)
        verticalLayout.addWidget(self.key_line)

        verticalLayout_2.addLayout(verticalLayout)
        self.setCentralWidget(centralwidget)

    def _resizeFloatingWindow(self, width, height):
        """浮动(workspaceControl)模式下，把承载窗口收缩/放大到指定尺寸"""
        name = self.workspaceControlName()
        if not name:
            return  # workspaceControl 尚未创建（如首次 show 之前），无需处理
        try:
            if not cmds.workspaceControl(name, q=True, exists=True):
                return
            if not cmds.workspaceControl(name, q=True, floating=True):
                return  # 停靠状态不处理
        except Exception as e:
            print(e)
            return
        # 部分 Maya 版本的 workspaceControl 支持 resize 编辑标志，失败也无妨
        try:
            cmds.workspaceControl(name, e=True, resizeWidth=int(width), resizeHeight=int(height))
        except Exception:
            pass
        # 直接收缩/放大承载 workspaceControl 的顶层浮动窗口
        try:
            top = self.window()
            if top is not None:
                top.resize(int(width), int(height))
        except Exception as e:
            print(e)

    def _restoreGeometry(self):
        """workspaceControl 创建后恢复窗口几何（必须在 show() 之后调用）。
        停靠状态由 workspaceControl 自行管理，此处不恢复。"""
        if not self.isFloating():
            return
        pos, size, _ = self.readSettings()
        win = self.window()
        if win is None:
            return
        # 尺寸（mini 高度固定，不恢复尺寸）
        if not self.isMini and size is not None:
            try:
                self._resizeFloatingWindow(size.width(), size.height())
            except Exception as e:
                print(e)
        # 位置：带屏幕越界防御，避免窗口跑到不可见区域
        if pos is not None:
            try:
                vg = QtWidgets.QApplication.desktop().geometry()  # 多屏联合矩形
                x, y = pos.x(), pos.y()
                if vg.left() <= x <= vg.right() - 50 and vg.top() <= y <= vg.bottom() - 30:
                    win.move(pos)
            except Exception as e:
                print(e)

    def rememberSettings(self):
        """ 写入QSettings数据（含停靠/浮动状态，供跨重启恢复） """
        settings = QtCore.QSettings('AssetsManager', 'AssetsManagerSettings')
        floating = self.isFloating()
        settings.setValue('floating', floating)
        if floating:
            # 浮动时保存几何：停靠时 window()==self、pos 是内嵌控件坐标(≈0,0)，无意义
            win = self.window()
            settings.setValue('pos', win.pos())
            if not self.isMini:
                settings.setValue('size', win.size())
        else:
            # 停靠时尽力记住停靠边（Maya 无查询命令，用 Qt dockWidgetArea 兜底）
            area = self._currentDockArea()
            if area:
                settings.setValue('dockArea', area)
        if not self.isMini:
            settings.setValue('tab', self.tabWidget.currentIndex())
        settings.setValue('isMini', self.isMini)

    def _currentDockArea(self):
        """尽力返回当前停靠边 'left'/'right'/'top'/'bottom'，查不到返回 None。
        Maya workspaceControl 无直接查询 dock 区域的命令，用 Qt 的 dockWidgetArea 兜底。"""
        try:
            control = self.parent()  # workspaceControl 的 QWidget
            if control is None:
                return None
            return {
                QtCore.Qt.LeftDockWidgetArea: 'left',
                QtCore.Qt.RightDockWidgetArea: 'right',
                QtCore.Qt.TopDockWidgetArea: 'top',
                QtCore.Qt.BottomDockWidgetArea: 'bottom',
            }.get(self.mayaMainWindow.dockWidgetArea(control))
        except Exception:
            return None

    def readSettings(self):
        """ 读取QSettings数据 """
        settings = QtCore.QSettings('AssetsManager', 'AssetsManagerSettings')
        pos = settings.value('pos')
        size = settings.value('size')
        tab = settings.value('tab')
        isMini = settings.value('isMini')

        if isMini is not None:
            if isMini == 'true':
                self.isMini = True
            else:
                self.isMini = False
        return pos, size, tab

    def readLoginSetting(self):
        """ 读取am_maya自己的登录设置 """
        if os.path.isfile(self.SM_SETTING_JSON):
            f = open(self.SM_SETTING_JSON, 'r')
            setting_data = json.loads(f.read())
            f.close()
        else:
            setting_data = {}
        return setting_data

    def rememberLoginSettings(self):
        """ 记录am_maya自己的登录设置 """
        data = {"user": self.user, "password": self.password}
        f = open(self.SM_SETTING_JSON, 'w')
        f.write(json.dumps(data))
        f.close()

    def login_UI(self):
        """ 登录 """
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(390, 95)
        Dialog.setWindowTitle(u"Enter User Password")
        font = QtGui.QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        label = QtWidgets.QLabel(Dialog)
        label.setText(u"用户名：")
        label.setFont(font)
        label2 = QtWidgets.QLabel(Dialog)
        label2.setText(u"密码：")
        label2.setFont(font)
        name_comboBox = QtWidgets.QComboBox(Dialog)
        userList = []
        for i in self.user_list:
            userList += i
        name_comboBox.addItems(userList)
        password_lineEdit = QtWidgets.QLineEdit(Dialog)
        password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        bttnbox = QtWidgets.QDialogButtonBox(Dialog)
        bttnbox.setOrientation(QtCore.Qt.Horizontal)
        bttnbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addWidget(name_comboBox, 0, 1, 1, 2)
        lay.addWidget(label2, 1, 0, 1, 1)
        lay.addWidget(password_lineEdit, 1, 1, 1, 1)
        remember_checkBox = QtWidgets.QCheckBox(Dialog)
        remember_checkBox.setText(u"记住密码")
        lay.addWidget(remember_checkBox, 2, 0, 1, 1)
        lay.addWidget(bttnbox, 3, 1, 1, 1)

        def _login():
            self.user = name_comboBox.currentText()
            self.password = password_lineEdit.text()
            self.login_bttn.setText(self.user)
            self.tabChanged()
            if remember_checkBox.isChecked():
                self.rememberLoginSettings()
            Dialog.close()

        bttnbox.accepted.connect(lambda: _login())
        bttnbox.rejected.connect(Dialog.reject)
        Dialog.exec_()

    def user_out(self):
        """ 退出登录 """
        self.user = ""
        self.password = ""
        self.rememberLoginSettings()
        self.login_bttn.setText(u"未登录")

    def reset_password(self):
        """ 修改密码 """
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(390, 95)
        Dialog.setWindowTitle(u"Enter User Password")
        font = QtGui.QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        label = QtWidgets.QLabel(Dialog)
        label.setText(u"旧密码：")
        label.setFont(font)
        label2 = QtWidgets.QLabel(Dialog)
        label2.setText(u"新密码：")
        label2.setFont(font)
        old_password_lineEdit = QtWidgets.QLineEdit(Dialog)
        old_password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        new_password_lineEdit = QtWidgets.QLineEdit(Dialog)
        new_password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        bttnbox = QtWidgets.QDialogButtonBox(Dialog)
        bttnbox.setOrientation(QtCore.Qt.Horizontal)
        bttnbox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addWidget(old_password_lineEdit, 0, 1, 1, 2)
        lay.addWidget(label2, 1, 0, 1, 1)
        lay.addWidget(new_password_lineEdit, 1, 1, 1, 1)
        lay.addWidget(bttnbox, 3, 1, 1, 1)

        def _reset():
            user = self.user
            old = old_password_lineEdit.text()
            new = new_password_lineEdit.text()
            conn = None
            cur = None
            try:
                conn = psycopg2.connect(database="postgres", user=user, password=old, host=self.host, port="5432")
                cur = conn.cursor()
                cur.execute('''ALTER USER %s WITH PASSWORD '%s';''' % (user, new))
                conn.commit()
            except Exception as e:
                self.print_msg(e)
            finally:
                if cur is not None:
                    cur.close()
                if conn is not None:
                    conn.close()
            Dialog.close()

        bttnbox.accepted.connect(lambda: _reset())
        bttnbox.rejected.connect(Dialog.reject)
        Dialog.exec_()

    def tabChanged(self):
        """
        切换tab
        :return:
        """
        if self.tabWidget.currentIndex() == 0 and self.asset_page.layout().count() == 0:
            self.asset = assetTools.AssetToolsUI(user=self.user, password=self.password)
            # AssetToolsUI 现已是控件本身（原 self.asset.ui 改为代码构建后直接挂在 self 上）
            self.asset_page.layout().addWidget(self.asset)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # 点击主窗空白处时，关闭表格视图里弹出的制作人/中文名面板
        try:
            self.asset.ui_main_wgt.closeMenus()
        except Exception:
            pass

    def getStyleSheet(self):
        style_sheet_path = '%s/qss/maya.qss' % self.scriptsPath
        with open(style_sheet_path) as (file):
            str = file.read()
        self.setStyleSheet(str)

    def shrinkWin(self):
        """切换mini窗口"""
        # 旧的 self.hide()/self.hide() 现改为隐藏当前中心控件；
        # setCentralWidget 会替换并销毁旧的中心控件，这里仅做切换前的防御性隐藏。
        if self.isMini:
            self.rememberSettings()
            try:
                self.centralWidget().hide()
            except:
                pass
            self.init_ui()
            self.isMini = False
        else:
            self.rememberSettings()
            try:
                self.centralWidget().hide()
            except:
                pass
            self.init_ui_mini()
            self.isMini = True

    def toolSetting_UI(self):
        """工具设置"""
        toolsJson = '%s/config/projectSetting.json' % self.scriptsPath
        tempJson = '%s/projectSetting.json' % am_Temp()
        f = QtCore.QFile('%s/ui/setting.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        f.close()
        loader.show()
        loader.path_Btn.clicked.connect(lambda: setPath())

        def setPath():
            """ 设置根目录 """
            path = QtWidgets.QFileDialog.getExistingDirectory(loader, u"选择一个根目录")
            if path != "":
                loader.lineEdit.setText(path)

        loader.set_bttn.clicked.connect(lambda: setTool())

        def setTool():
            """ 设定 """
            print(loader.lineEdit.text())
            for i in range(self.asset_page.layout().count()):
                self.asset_page.layout().itemAt(i).widget().deleteLater()
            self.asset_page.layout().addWidget(assetTools.AssetToolsUI(isCGTW=False,
                                                                          ROOT=loader.lineEdit.text()))
            loader.close()

        loader.reset_bttn.clicked.connect(lambda: reset())
        loader.esc_bttn.clicked.connect(lambda: loader.close())

        def reset():
            """ 重置 """
            data = jsonHelper.readDictFromFile(toolsJson)
            jsonHelper.writeDictToFile(tempJson, data)
            loader.lineEdit.setText(data['rootPath'])

    def miniSetting_UI(self):
        """
        mini工具设置
        """
        menu = QtWidgets.QMenu(self)
        action_a = QtWidgets.QAction(u"Assets", self)
        action_a.setCheckable(True)
        action_b = QtWidgets.QAction(u"Scenes", self)
        action_b.setCheckable(True)
        menu.addAction(action_a)
        menu.addAction(action_b)
        menu.popup(QtCore.QPoint(self.x() + 350, self.y() + 30))

    def miniSearch(self):
        """ mini搜索 """
        self.miniSearchThread.start()

    def _miniSearch(self):
        keyWords = self.key_line.text()
        self.menu = QtWidgets.QMenu()
        self.menu.setStyleSheet("QMenu{background-color: rgb(35, 35, 35);}" +
                                "QMenu:selected{background: #b0e600; color: #000000;}")
        founded_result = []
        if self.action_a.isChecked():
            for proj in self.projectSetting()['projects']:
                for type in self.projectSetting()['type']:
                    aaa = self.List._listItems_CGT('Assets', str(proj), str(type), 'asset', 'asset.maya',
                                                   'asset.assetstapy', 'asset.entity', 'asset.cn_name', keyWords)
                    if aaa:  # 为空说明没有搜索结果
                        founded_result.append("found something")
                        actionA = QtWidgets.QAction(
                            "::::::::::::::::::::::  Assets > {0} > {1}  ::::::::::::::::::::::".format(proj, type),
                            self.mainLayout)
                        actionA.setDisabled(True)
                        self.menu.addAction(actionA)
                        for a in aaa:
                            action_name = a.split("   /   ")[0]
                            path = '{0}/{1}/Assets/{2}/{3}'.format(self.projectSetting()['rootPath'], proj, type,
                                                                   action_name)
                            self.menu.addAction(self.addAction(a, path))
        if self.action_b.isChecked():
            for proj in self.projectSetting()['projects']:
                projcet_path = '{0}/{1}/{2}'.format(self.projectSetting()['rootPath'], proj, 'Scenes')
                directory = QtCore.QDir(projcet_path)
                type_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries,
                                                QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
                for type in type_list:
                    bbb = self.List._listItems_CGT('Scenes', str(proj), str(type), 'scenes', 'scenes.maya',
                                                   'scenes.scenesassetstype', 'scenes.entity', 'scenes.assetsnamecn',
                                                   keyWords)
                    if bbb:  # 为空说明没有搜索结果
                        founded_result.append("found something")
                        actionB = QtWidgets.QAction(
                            ":::::::::::::::::::::::::  Scenes > {0} > {1}  :::::::::::::::::::::::::".format(proj,
                                                                                                              type),
                            self.mainLayout)
                        actionB.setDisabled(True)
                        self.menu.addAction(actionB)
                        for b in bbb:
                            action_name = b.split("   /   ")[0]
                            path = '{0}/{1}/Scenes/{2}/{3}'.format(self.projectSetting()['rootPath'], proj, type,
                                                                   action_name)
                            self.menu.addAction(self.addAction(b, path))

        if not founded_result:  #
            actionB = QtWidgets.QAction(u" >_< Oooops... Nothing found ！ ", self.mainLayout)
            self.menu.addAction(actionB)
        self.menu.exec_(QtCore.QPoint(self.x(), self.y() + 70))

    def addAction(self, ZhEn_name, path):
        """使用Java闭包，否则triggered.connect的action只会认到最后一个action"""
        action = QtWidgets.QAction(ZhEn_name, self.mainLayout)
        action.setData(path)
        action.triggered.connect(lambda: self.createRef_mini(action))
        return action

    def createRef_mini(self, action):
        """mini面板创建Ref"""
        path = QtWidgets.QAction.data(action)
        # print(path)
        tab = path.split("/")[3]
        action_name = path.split("/")[-1]
        if tab == "Assets":
            file_path = "{0}/Rig/{1}_hi_rig.ma".format(path, action_name)
            print(file_path)
            if os.path.exists(file_path):
                nameSpace = '{0}_hi_rig'.format(action_name)
                cmds.file(file_path, reference=True, type='mayaAscii', ignoreVersion=True, groupLocator=True,
                          options='v=0;', mergeNamespacesOnClash=False, namespace=nameSpace)
        else:
            file_path = "{0}/Assembly/{1}_AD.ma".format(path, action_name)
            if os.path.exists(file_path):
                slectAD = cmds.ls(sl=1, type='assemblyReference')
                if not slectAD:
                    assembly_name = cmds.assembly(name=action_name, type='assemblyReference')
                    cmds.setAttr('{0}.definition'.format(assembly_name), file_path, type='string')
                else:
                    for slt in slectAD:
                        cmds.setAttr('{0}.definition'.format(slt), file_path, type='string')

    def workspaceControlName(self):
        """
        Return the workspaceControl name for the widget.
        :rtype: str or None
        """
        if self.isDockable() and self.parent():
            return self.parent().objectName()
        else:
            return None

    def isDocked(self):
        return not self.isFloating()

    def isFloating(self):
        workspace_control_name = self.workspaceControlName()
        if workspace_control_name:
            try:
                return cmds.workspaceControl(workspace_control_name, q=True, floating=True)  # bool
            except AttributeError:
                cmds.warning("cmds.workspaceControl is not supported!")
        return True

    def window(self):
        """停靠时返回自身，浮动时返回 workspaceControl 顶层宿主窗口。
        用于保存/恢复正确的窗口位置与尺寸（仿 StudioLibrary.MayaLibraryWindow）。
        dockable 模式下 self 只是被嵌进 workspaceControl 的内嵌控件，
        self.pos()/self.move() 作用在内嵌控件上，不是真正的浮动窗口位置。"""
        if self.isDocked():
            return self
        return QtWidgets.QMainWindow.window(self)

    def floatingChanged(self, isFloating):
        print("floatingChanged")
        print(self.workspaceControlName())
        # cmds.workspaceControl(self.workspaceControlName(), e=1, cc=self.closeEvent())
        # print(self.isFloating())
        # if self.isFloating() == True:
        #     print("isFloating")
        # else:
        #     print(self.isFloating())

    def closeEvent(self, event):
        print("=====close event=======")
        self.rememberSettings()
        try:
            # actionTools.ActionToolsUI().destroy()
            # ShotsManager_Maya.ShotsManagerMayaUI().rememberSettings()  # 不行
            # disableMayaClosedEvent()
            self.mayaMainWindow.removeEventFilter(self)
            # sceneTools.SceneToolsUI().remove_maya_eventfilter()
        except Exception as e:
            print(e)

    def destroy(self):
        print("destroy")

    def dockCloseEventTriggered(self):
        """workspaceControl(停靠面板)关闭时由 MayaQWidgetDockableMixin 触发。
        dockable 下 QMainWindow.closeEvent 不可靠，用这里保存设置（浮动几何）。"""
        try:
            self.rememberSettings()
        except Exception as e:
            print(e)

    def showEvent(self, event):
        """首次显示时（此时 workspaceControl 已就绪）恢复浮动几何，仿 StudioLibrary。
        停靠场景由 workspaceControl 自行恢复，_restoreGeometry 内已按 isFloating 守卫。"""
        super(AssetsManagerUI, self).showEvent(event)
        if not getattr(self, '_isLoaded', False):
            self._isLoaded = True
            self._restoreGeometry()

    def show(self, **kwargs):
        """
        以可停靠窗口方式显示（仿 StudioLibrary.MayaLibraryWindow.show）。
        默认 dockable=True，这样才会创建 workspaceControl、窗口才能停靠；
        传 dockable=False 可显示为浮动独立窗口。

        关于关闭保存：dockable=True 时窗口挂在 workspaceControl 下，
        QMainWindow.closeEvent 不一定触发，保存改由 dockCloseEventTriggered
        与 Maya 退出事件 mayaClosedEvent 负责；几何恢复在首次 showEvent 里执行。
        """
        kwargs.setdefault('dockable', True)
        MayaQWidgetDockableMixin.show(self, **kwargs)
        self.raise_()


def showWindow():
    """
    显示 AssetsManager：复用同一实例、不销毁 workspaceControl，让 Maya 原生
    记住窗口状态（对齐 StudioLibrary）。

    - 同一 Maya 会话内关掉再开：保持上次的位置/大小/停靠（复用实例 + 恢复已有控件）。
    - 跨重启 Maya：停靠布局不恢复（不使用 uiScript，避免它与 QMainWindow 配合
      在浮动切换时把内嵌内容 reparent 到画不出来的白屏状态）；浮动位置/大小由
      QSettings 在首次 showEvent 恢复。
    """
    global win

    # 复用实例：仅当不存在或底层 C++ 对象已销毁时才新建（否则保持原窗口状态）
    need_new = win is None or not shiboken2.isValid(win)
    if need_new:
        # 注册 Maya 退出事件，用于退出时保存设置（closeEvent 不可靠）
        enableMayaClosedEvent()
        # 若存在上一次遗留的 workspaceControl（如重载模块后 win 丢失但控件仍在），
        # 先清掉，避免新实例游离、旧空控件残留。
        try:
            if cmds.workspaceControl(WORKSPACE_CONTROL, q=True, exists=True):
                cmds.deleteUI(WORKSPACE_CONTROL)
        except Exception:
            pass
        win = AssetsManagerUI()

    if (not need_new) and cmds.workspaceControl(WORKSPACE_CONTROL, q=True, exists=True):
        # win 仍有效且控件还在：同一会话内重开，恢复显示并保持原停靠/位置/大小
        cmds.workspaceControl(WORKSPACE_CONTROL, e=True, restore=True)
    else:
        win.show(dockable=True)
