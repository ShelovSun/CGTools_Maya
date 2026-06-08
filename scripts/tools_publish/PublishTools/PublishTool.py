#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
import os

import psycopg2
import time
import json
from . import capture

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance
from utils import jsonHelper, publish, sequenceplayer, pose, animation
from config import projectSetting, SMConfig
from widgets import imagesequence

# reload(publish)
# reload(pose)

# cgteamwork_path = 'C:\\CgTeamWork_v6.2\\bin\\base'
# if cgteamwork_path not in sys.path:
#     sys.path.append(cgteamwork_path)
# try:
#     import cgtw2
# except:
#     pass


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


class MyThread(QtCore.QThread):

    signal = QtCore.Signal()

    def __init__(self):
        super(MyThread, self).__init__()

    def run(self):
        self.signal.emit()


class LogModel(QtCore.QAbstractItemModel):

    def __init__(self, root, parent=None):
        super(LogModel, self).__init__(parent)
        self._rootNode = root
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        return 1

    def data(self, index, role):
        if not index.isValid():
            return None
        node = index.internalPointer()
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            if index.column() == 0:
                return node.name()
        if role == QtCore.Qt.DecorationRole:
            if index.column() == 0:
                typeInfo = node.typeInfo()
                if typeInfo == "Node":
                    return QtGui.QIcon(QtGui.QPixmap('%s/icon/unchecked.png' % self.scriptsPath))
                if typeInfo == "Failed":
                    return QtGui.QIcon(QtGui.QPixmap('%s/icon/failed.png' % self.scriptsPath))
                if typeInfo == "Succeed":
                    return QtGui.QIcon(QtGui.QPixmap('%s/icon/succeed.png' % self.scriptsPath))

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if index.isValid():
            if role == QtCore.Qt.EditRole:
                node = index.internalPointer()
                node.setName(value)
                return True
        return False

    def flags(self, index):
        return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)

    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node
        return self._rootNode

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginInsertRows(parent, position, position + rows - 1)
        for row in range(rows):
            childCount = parentNode.childCount()
            childNode = Node("untitled" + str(childCount))
            success = parentNode.insertChild(position, childNode)
        self.endInsertRows()
        return success

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        parentNode = self.getNode(parent)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for row in range(rows):
            success = parentNode.removeChild(position)
        self.endRemoveRows()
        return success


class Node(object):

    def __init__(self, name, parent=None):
        self._name = name
        self._children = []
        self._parent = parent
        if parent is not None:
            parent.addChild(self)

    def typeInfo(self):
        return "Node"

    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if position < 0 or position > len(self._children):
            return False
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        if position < 0 or position > len(self._children):
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def name(self):
        return self._name

    def setName(self, name):
        self._name = name

    def child(self, row):
        return self._children[row]

    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent

    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)


class FailedNode(Node):
    def __init__(self, name, parent=None):
        super(FailedNode, self).__init__(name, parent)

    def typeInfo(self):
        return "Failed"


class SucceedNode(Node):
    def __init__(self, name, parent=None):
        super(SucceedNode, self).__init__(name, parent)

    def typeInfo(self):
        return "Succeed"


class AnimationTransferError(Exception):
    """Base class for exceptions in this module."""
    pass


class Log(QtCore.QThread):
    def __init__(self, wgt, top, text, pix, parent=None):
        super(Log, self).__init__(parent)
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.wgt = wgt
        self.top = top
        self.text = text
        self.pix = pix

    def run(self):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, self.text)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('%s/icon/%s.png' % (self.scriptsPath, self.pix)),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(0, icon)

        if not self.top:
            self.wgt.addTopLevelItem(item)
        else:
            self.top.setExpanded(True)
            self.top.addChild(item)
        return item


class PubToolsUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    VERSION = "2.0.2"
    Pub = publish.Publish()
    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
    tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('APPDATA'))  # cmds.internalVar(userTmpDir=True)
    sm_temp = "{}/ShotManagerTemp".format(os.environ.get('APPDATA'))
    SM_SETTING_JSON = "{}/setting.json".format(sm_temp)
    ThreadPool = QtCore.QThreadPool()
    ROOT = "Y:/MCCProject/StudioLibrary_Ani"

    def __init__(self, tab=0, _project=None, _type=None, parent=maya_main_window()):
        super(PubToolsUI, self).__init__(parent)
        self.setWindowTitle('Publish Tool ' + self.VERSION)
        self.setWindowIcon(QtGui.QIcon('%s/icon/publish.png' % self.scriptsPath))
        self.ui = None
        self.resize(780, 500)
        self.project = _project
        self.type = _type
        try:
            self.user = self.readLoginSetting()['user']
            self.password = self.readLoginSetting()['password']
        except Exception as e:
            print(e)
            self.user = SMConfig().getPrefsValue("Info/user", "")
            self.password = SMConfig().getPrefsValue("Info/password", "")

        self.host = projectSetting()["host"]
        self._timer = None
        self._log = ""
        self._imageSequence = None
        self.assemblies = []
        self.port_path = ''
        self.gpu_file_path = ''
        self.proxy_file_path = ''

        self.init_ui_thread = MyThread()
        self.init_ui_thread.signal.connect(self.init_ui)
        self.init_ui_thread.start()
        self.init_ui_thread.finished.connect(lambda: self.setTab(tab))

    def init_ui(self):
        # print("init_ui")
        f = QtCore.QFile('%s/ui/PublishTool.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        ''' model '''
        self.ui.log_progressBar.setVisible(False)
        self.ui.icon_label.setPixmap(QtGui.QPixmap('%s/icon/question.png' % self.scriptsPath))
        self.ui.render_bttn.setIcon(QtGui.QPixmap('%s/icon/shot.png' % self.scriptsPath))
        self.ui.render_bttn.clicked.connect(lambda: self.renderIcon(self.ui.Preview_label))
        self.ui.capture_btn.setIcon(QtGui.QPixmap('%s/icon/capture.png' % self.scriptsPath))
        self.ui.capture_btn.clicked.connect(lambda: self.capture_screen())
        self.ui.publishType_comb.currentIndexChanged.connect(lambda: self.type_changed('mod'))
        self.ui.Yes_bttn.clicked.connect(self.yes_bttn_clicked)
        ''' rig '''
        self.ui.render_bttn_rig.setIcon(QtGui.QPixmap('%s/icon/shot.png' % self.scriptsPath))
        self.ui.render_bttn_rig.clicked.connect(lambda: self.renderIcon(self.ui.Preview_label_rig))
        self.ui.capture_btn_rig.setIcon(QtGui.QPixmap('%s/icon/capture.png' % self.scriptsPath))
        self.ui.capture_btn_rig.clicked.connect(lambda: self.capture_screen())
        self.ui.publishType_comb_rig.currentIndexChanged.connect(lambda: self.type_changed('rig'))
        ''' sc '''
        self.ui.render_bttn_sc.setIcon(QtGui.QPixmap('%s/icon/shot.png' % self.scriptsPath))
        self.ui.render_bttn_sc.clicked.connect(lambda: self.renderIcon(self.ui.Preview_label_sc))
        self.ui.capture_btn_sc.setIcon(QtGui.QPixmap('%s/icon/capture.png' % self.scriptsPath))
        self.ui.capture_btn_sc.clicked.connect(lambda: self.capture_screen())
        self.ui.publishType_comb_sc.currentIndexChanged.connect(lambda: self.type_changed('scene'))
        ''' ac '''
        self.ui.render_bttn_ac.setIcon(QtGui.QPixmap('%s/icon/render.png' % self.scriptsPath))
        self.ui.render_bttn_ac.clicked.connect(self.renderIcon_ac)
        # self.ui.publishType_comb_ac.currentIndexChanged.connect(lambda: self.type_changed_ac())

        sty = "background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(" \
              "35, 35, 35, 100),  stop:1 rgba(35, 35, 35, 255)); "
        self.ui.Preview_label.setStyleSheet(sty)
        self.ui.Preview_label_rig.setStyleSheet(sty)
        self.ui.Preview_label_sc.setStyleSheet(sty)
        self.ui.Preview_label_ac.setStyleSheet(sty)

        self.playerSet()

        now_time = time.strftime('%Y%m%d%H%M', time.localtime())
        self.ui.logName_lineEdit.setText('Comment' + now_time + ':')
        # self.ui.splitter.setSizes([120, 500])
        # self.ui.splitter.setStretchFactor(0, False)
        # self.ui.splitter.setStretchFactor(1, True)
        self.ui.Cancel_bttn.clicked.connect(self.closeWin)

    def readLoginSetting(self):
        """ """
        if os.path.isfile(self.SM_SETTING_JSON):
            f = open(self.SM_SETTING_JSON, 'r')
            setting_data = json.loads(f.read())
            f.close()
        else:
            setting_data = {}
        return setting_data

    def setTab(self, tab):
        """ 设置Tab """
        self.ui.Pub_Tab.setCurrentIndex(tab)
        self.ui.Pub_Tab.currentChanged.connect(self.tabChanged)
        self.tabChanged()

    def tabChanged(self):
        """
        切换tab触发
        :return:
        """
        if self.ui.Pub_Tab.currentIndex() == 0:  # Model===============================================================
            if self.check_mod():
                projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_mod()
                self.update_type(projectName, 'Assets', self.ui.publishType_comb)
                self.ui.Title_label.setText(u"<h3>确定发布 {} 到 \n{} ？</h3>".format(characterName, path))
                # self.ui.publishType_comb.currentIndexChanged.connect(lambda: self.type_changed('mod'))
                # self.ui.Yes_bttn.setEnabled(True)
                self.renderIcon(self.ui.Preview_label)
                # self.log_Mag()
                # self._log_show()
            else:
                self.ui.Yes_bttn.setEnabled(False)

        elif self.ui.Pub_Tab.currentIndex() == 1:  # Rig===============================================================
            if self.check_rig():
                projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_rig()
                self.ui.Title_label.setText(u"<h3>确定发布 {} 到 \n{} ？</h3>".format(characterName, path))
                # self.ui.publishType_comb_rig.currentIndexChanged.connect(lambda: self.type_changed('rig'))
                # self.ui.Yes_bttn.setEnabled(True)
                #
                self.renderIcon(self.ui.Preview_label_rig)
            else:
                self.ui.Yes_bttn.setEnabled(False)

        elif self.ui.Pub_Tab.currentIndex() == 2:  # Scene=============================================================
            print(self.project, self.type)
            self.update_proj(self.ui.publishProj_comb)
            if self.project:
                self.ui.publishProj_comb.setCurrentText(self.project)
            else:
                self.ui.publishProj_comb.setCurrentIndex(0)

            projectName = self.ui.publishProj_comb.currentText()
            self.update_type(projectName, 'Scenes', self.ui.publishType_comb_sc)
            self.ui.publishProj_comb.currentIndexChanged.connect(lambda: self.proj_changed_sc())
            if self.type:
                print(self.type)
                self.ui.publishType_comb_sc.setCurrentText(self.type)
            else:
                self.ui.publishType_comb_sc.setCurrentIndex(0)

            # self.ui.publishType_comb_sc.currentIndexChanged.connect(lambda: self.type_changed('scene'))
            if self.check_sc():
                self.isYesEnable_sc()
                self.renderIcon(self.ui.Preview_label_sc)
            else:
                self.ui.Yes_bttn.setEnabled(False)

        elif self.ui.Pub_Tab.currentIndex() == 3:  # Action============================================================
            self.update_proj(self.ui.publishProj_comb_ac)
            # self.update_type_ac()
            if self.check_ac():
                self.update_Title_ac()
                # self.update_time_slider_state()
                self.isYesEnable_ac()
                self.isFBXEnable_ac()
                # self.ui.Yes_bttn.clicked.connect(self._actionPublish)
                self.renderIcon_ac()
            else:
                self.ui.Yes_bttn.setEnabled(False)
            self.ui.name_lineEdit_ac.textChanged.connect(lambda: self.name_changed_ac())
            self.ui.name_lineEdit_action.textChanged.connect(lambda: self.name_changed_ac())
            # self.ui.publishType_comb_ac.currentIndexChanged.connect(lambda: self.type_changed_ac())
            self.ui.time_slider_rBttn.clicked.connect(self._setTimeRange)
            self.ui.start_end_rbttn.clicked.connect(self._setTimeRange)

    def closeEvent(self, event):
        try:
            self._imageSequence.stop()
        except:
            pass

    def closeWin(self):
        self.close()

    def playerSet(self):
        """ 播放器设置 """
        player = sequenceplayer.Player()
        player.setPlayButtonState(self.ui.Play_toolBttn)
        '''播放'''
        self.ui.Play_toolBttn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaStop))
        self.ui.Play_toolBttn.clicked.connect(lambda: player.play(100, self.ui.Play_toolBttn))
        '''起始帧'''
        self.ui.firstFrame_toolBttn.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))
        self.ui.firstFrame_toolBttn.clicked.connect(player.firstFrame)
        '''上一帧'''
        self.ui.prevFrame_toolBttn.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
        self.ui.prevFrame_toolBttn.clicked.connect(player.prevFrame)
        '''下一帧'''
        self.ui.nextFrame_toolBttn.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        self.ui.nextFrame_toolBttn.clicked.connect(player.nextFrame)
        '''结束帧'''
        self.ui.lastFrame_toolBttn.setIcon(
            QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
        self.ui.lastFrame_toolBttn.clicked.connect(player.lastFrame)

    def update_proj(self, wgt):
        """ 根据json，设置proj显示 """
        wgt.addItems(self.projectSetting()['projects'])

    def update_type(self, proj, Assets_or_Scenes, wgt):
        """ model/rig/scene面板根据项目，设置type显示 """
        wgt.clear()
        wgt.addItems([u"**"])
        projcet_path = '{0}/{1}/{2}'.format(self.projectSetting()['rootPath'], proj, Assets_or_Scenes)
        directory = QtCore.QDir(projcet_path)
        type_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries,
                                        QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        wgt.addItems(type_list)
        wgt.setCurrentIndex(0)

    # def update_type_ac(self):
    #     self.ui.publishType_comb_ac.clear()
    #     self.ui.publishType_comb_ac.addItems([u"**", "Pose", "Animation"])

    def proj_changed_sc(self):
        """
        :return:
        """
        projectName = self.ui.publishProj_comb.currentText()
        self.update_type(projectName, 'Scenes', self.ui.publishType_comb_sc)
        self.check_sc()

    def type_changed(self, tab):
        """
        改变类型触发：修改标题 ，确定Yes是否可用，挂载Yes（放这里才会只挂一遍）
        """
        if tab == "mod":
            projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_mod()
            if publishType == u"**":
                self.ui.Yes_bttn.setEnabled(False)
            else:
                self.ui.Yes_bttn.setEnabled(True)

        elif tab == "rig":
            projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_rig()
            if publishType == u"**":
                self.ui.Yes_bttn.setEnabled(False)
            else:
                self.ui.Yes_bttn.setEnabled(True)
                # self.ui.Yes_bttn.clicked.connect(self._rigPublish)
        elif tab == "scene":
            projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_sc()
            self.check_sc()
            self.isYesEnable_sc()
            # self.ui.Yes_bttn.clicked.connect(lambda: self._scenePublish())
        self.ui.Title_label.setText(u"<h3>确定发布 {} 到 \n{} ？</h3>".format(characterName, path))

    def name_changed_ac(self):
        self.update_Title_ac()
        self.isYesEnable_ac()
        self.isFBXEnable_ac()

    def type_changed_ac(self):
        """ 改变ac类型触发：锁定time range；锁定fbx；锁定Yes；修改标题"""
        # self.update_time_slider_state()
        self.isYesEnable_ac()
        self.isFBXEnable_ac()
        self.update_Title_ac()

    def projectSetting(self):
        data = jsonHelper.readDictFromFile('%s/AssetsManagerForMaya/config/projectSetting.json'
                                           % self.scriptsPath.replace("tools_publish/PublishTools", ""))
        return data

    def check_abc_mll(self):
        if self.Pub.pluginInfo('AbcExport.mll') is False:
            QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 AbcExport，请加载')
            return False
        if self.Pub.pluginInfo('AbcImport.mll') is False:
            QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 AbcImport，请加载')
            return False
        return True

    def check_assembly_mll(self):
        if self.Pub.pluginInfo('gpuCache.mll') is False:
            QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 gpuCache，请加载')
            return False
        if self.Pub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 sceneAssembly，请加载')
            return False
        if self.Pub.pluginInfo('mtoa.mll') is False:
            QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 mtoa，请加载')
            return False
        return True

    # def override_check(self, asset_name):
    #     """ 检查服务器上是否有同名资产 """
    #     asset_list, type_path = self.get_asset_list()
    #     if asset_name in asset_list:
    #         reply = QtWidgets.QMessageBox.question(self, u'提示', u'服务器上有重名资产，确定要覆盖吗？',
    #                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    #         if reply == QtWidgets.QMessageBox.Yes:
    #             return True
    #         return False
    #     else:
    #         return True

    def check_mod(self):
        """ 检查mod并设置UI显示 """
        print("check_mod")
        if len(cmds.ls('*_*_AST', type='transform')) == 1:
            projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[-2]
            if projectName not in self.projectSetting()['projects']:
                QtWidgets.QMessageBox.warning(self, 'Warning', u'请检查项目名是否正确!!!')
                return False
            characterName = cmds.ls('*_*_AST', type='transform')[0].rsplit('_',2)[0]
            self.ui.proj_lineEdit.setText(projectName)
            self.ui.name_lineEdit.setText(characterName)
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'找不到_AST或_AST不唯一,请检查!!!')
            return False
        return True

    def check_rig(self):
        """ 检查rig并设置UI显示"""
        print("check_rig")
        if len(cmds.ls('*_*_AST', type='transform')) == 1:
            projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[-2]
            if projectName not in self.projectSetting()['projects']:
                QtWidgets.QMessageBox.warning(self, 'Warning', '请检查项目名是否正确!!!')
                return False
            # characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]  # 改命名规则
            characterName = cmds.ls('*_*_AST', type='transform')[0].rsplit('_',2)[0]
            self.ui.proj_lineEdit_rig.setText(projectName)
            self.ui.name_lineEdit_rig.setText(characterName)
            self.update_type(projectName, 'Assets', self.ui.publishType_comb_rig)
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'找不到_AST或_AST不唯一,请检查!!!')
            return False
        return True

    def check_sc(self):
        """检查sc资产是否符合发布规范，并设置UI显示"""
        print("check_sc")
        if not self.check_assembly_mll():
            return None

        assemblies = cmds.ls(assemblies=True)
        assemblies.remove('persp')
        assemblies.remove('top')
        assemblies.remove('front')
        assemblies.remove('side')
        if not assemblies:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'找不到assemblies,请检查!!!')
            return None

        self.ui.name_lineEdit_sc.setText(assemblies[0])
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_sc()

        if publishType == "Map":  # 地图发布
            if len(assemblies) != 1:
                QtWidgets.QMessageBox.warning(self, u'警告', u'发布Map大纲根目录下仅允许一个组，请检查')
                return None
            if assemblies[0].find('|') != -1:
                QtWidgets.QMessageBox.warning(self, u'警告', u'文件内有重名，请检查')
                return None
            self.ui.Title_label.setText(u"<h3>确定发布关卡 {0} 到 \n{1} ？</h3>".format(assemblies[0], path))
            self.assemblies = assemblies
            return "isMAP"

        else:  # 非MAP
            if len(assemblies) != 1:  # ====================多组件发布
                self.ui.name_lineEdit_sc.setText(assemblies[0].rsplit("_", 1)[0] + "_GRP")
                text = ""
                for assemblie in assemblies:
                    if assemblie.find('|') != -1:
                        QtWidgets.QMessageBox.warning(self, u'警告', u'文件内有重名，请检查')
                        return None
                    text = text + " , " + assemblie
                self.ui.Title_label.setText(u"确定发布多组件：\n{0} \n到 {1} ？".format(text.split(" , ", 1)[1], path))
                self.assemblies = assemblies
                return "isGRP"

            else:  # ==================================单组件发布
                if assemblies[0].find('|') != -1:
                    QtWidgets.QMessageBox.warning(self, u'警告', u'文件内有重名，请检查')
                    return None
                self.ui.Title_label.setText(u"<h3>确定发布 {0} 到 \n{1} ？</h3>".format(assemblies[0], path))
                self.assemblies = assemblies
                return "isSC"

    def check_ac(self):
        """ 检查action资产是否符合发布规范，并设置UI显示

        以当前选中的物体（控制器或模型）所属的角色作为要发布的资产，
        而不是固定取场景里第一个 reference。
        """
        selection = cmds.ls(sl=True, long=True) or []
        if not selection:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'请至少选择一个物体（选中要发布的角色身上的任意物体）')
            return False

        # 从选中的物体反查它所属的 reference，即要发布的角色
        try:
            assetRef = cmds.referenceQuery(selection[0], referenceNode=True)
        except RuntimeError:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'选中的物体不是引用进来的角色,请选中要发布的角色身上的物体!!!')
            return False

        assetPath = cmds.referenceQuery(assetRef, filename=True)
        projectName = assetPath.split('/')[2]
        characterName = assetPath.split('/')[5]
        if projectName not in self.projectSetting()['projects']:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'请检查资产的项目名是否正确!!!')
            return False
        self.ui.publishProj_comb_ac.setCurrentText(projectName)
        self.ui.name_lineEdit_ac.setText(characterName)

        if not self.validateAnimLayers():
            return False
        self._setTimeRange()

        return True

    def _setTimeRange(self):
        """
        自动设置起始帧/结束帧
        :return:
        """
        if self.ui.time_slider_rBttn.isChecked():
            self.ui.start_lineEdit.setEnabled(False)
            self.ui.start_lineEdit.setText(str(int(cmds.playbackOptions(query=True, minTime=True))))
            self.ui.end_lineEdit.setEnabled(False)
            self.ui.end_lineEdit.setText(str(int(cmds.playbackOptions(query=True, maxTime=True))))
        if self.ui.start_end_rbttn.isChecked():
            self.ui.start_lineEdit.setEnabled(True)
            self.ui.end_lineEdit.setEnabled(True)

    def get_publishInfo_mod(self):
        projectName = self.ui.proj_lineEdit.text()
        characterName = self.ui.name_lineEdit.text()
        publishType = self.ui.publishType_comb.currentText()
        characterCHName = self.ui.CHname_lineEdit.text()
        path = str('%s/%s/%s/%s/%s/' % (self.projectSetting()['rootPath'],
                                        projectName,
                                        self.projectSetting()['assetFolder'],
                                        publishType,
                                        characterName))
        return projectName, characterName, characterCHName, publishType, path

    def get_publishInfo_rig(self):
        projectName = self.ui.proj_lineEdit_rig.text()
        characterName = self.ui.name_lineEdit_rig.text()
        publishType = self.ui.publishType_comb_rig.currentText()
        characterCHName = self.ui.CHname_lineEdit_rig.text()
        path = str('%s/%s/%s/%s/%s/' % (self.projectSetting()['rootPath'],
                                        projectName,
                                        self.projectSetting()['assetFolder'],
                                        publishType,
                                        characterName))
        return projectName, characterName, characterCHName, publishType, path

    def get_publishInfo_sc(self):
        projectName = self.ui.publishProj_comb.currentText()
        characterName = self.ui.name_lineEdit_sc.text()
        publishType = self.ui.publishType_comb_sc.currentText()
        characterCHName = self.ui.CHname_lineEdit_sc.text()
        path = '%s/%s/%s/%s' % (self.projectSetting()['rootPath'],
                                projectName,
                                self.projectSetting()['scenesFolder'],
                                publishType)
        return projectName, characterName, characterCHName, publishType, path

    def get_publishInfo_ac(self):
        # publish_path = ""
        projectName = self.ui.publishProj_comb_ac.currentText()
        characterName = self.ui.name_lineEdit_ac.text()
        actionName = self.ui.name_lineEdit_action.text()
        # publishType = self.ui.publishType_comb_ac.currentText()
        # if publishType == "Pose":
        #     publish_path = "{0}/{1}/{2}/{2}_{3}.pose".format(self.ROOT, projectName, characterName, actionName)
        # elif publishType == "Animation":
        #     publish_path = "{0}/{1}/{2}/{2}_{3}.anim".format(self.ROOT, projectName, characterName, actionName)
        # 范例：Y:\MCCProject\StudioLibrary_Ani\IM\BossQ\BossQ_AK_walk.anim
        path = '%s/%s/%s/%s/%s/%s' % (self.projectSetting()['rootPath'],
                                projectName,
                                self.projectSetting()['assetFolder'],
                                "Characters",
                                characterName,
                                self.projectSetting()['actionFolder'])
        start = int(self.ui.start_lineEdit.text())
        end = int(self.ui.end_lineEdit.text())
        if start >= end:
            QtWidgets.QMessageBox.warning(self, "Warning", u"结束帧请大于起始帧")
            return
        # actionCHName = self.ui.CHname_lineEdit_ac.text()

        return projectName, characterName, actionName, path, start, end

    def update_Title_ac(self):
        """ ac栏更新标题 """
        projectName, characterName, actionName, path, start, end = self.get_publishInfo_ac()
        # projectName, characterName, actionCHName, actionName, publishType, path, start, end = self.get_publishInfo_ac()
        self.ui.Title_label.setText(u"<h3>确定发布 {0} 到 \n{1} ？</h3>".format(characterName + '_' + actionName,
                                                                          path))

    def update_time_slider_state(self):
        # _type = self.ui.publishType_comb_ac.currentText()
        # if _type == u"**" or _type == "Pose":
        #     self.ui.time_slider_rBttn.setEnabled(False)
        #     self.ui.start_end_rbttn.setEnabled(False)
        # elif _type == "Animation":
        self.ui.time_slider_rBttn.setEnabled(True)
        self.ui.start_end_rbttn.setEnabled(True)

    def isYesEnable_sc(self):
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_sc()
        if publishType == u"**":
            self.ui.Yes_bttn.setEnabled(False)
        else:
            self.ui.Yes_bttn.setEnabled(True)

    def isYesEnable_ac(self):
        projectName, characterName, actionName, path, start, end = self.get_publishInfo_ac()
        # projectName, characterName, actionCHName, actionName, type, path, start, end = self.get_publishInfo_ac()

        if type == u"**" or actionName == "" or characterName == "":
            self.ui.Yes_bttn.setEnabled(False)
        else:
            self.ui.Yes_bttn.setEnabled(True)

    def isFBXEnable_ac(self):
        projectName, characterName, actionName, path, start, end = self.get_publishInfo_ac()
        # projectName, characterName, actionCHName, actionName, type, path, start, end = self.get_publishInfo_ac()
        if type == u"**" or type == "Pose":
            self.ui.fbx_cBox_4.setEnabled(False)
        else:
            self.ui.fbx_cBox_4.setEnabled(True)

    def renderIcon_ac(self):
        """
        判断渲染什么icon
        :return:
        """
        # type = self.ui.publishType_comb_ac.currentText()
        # if type == u"**" or type == "Pose":
        #     self.renderIcon(self.ui.Preview_label_ac, imageFormat='jpg')
        # elif type == "Animation":
        self.renderSeq(self.ui.Preview_label_ac)

    def renderIcon(self, wgt, imageFormat='png'):
        """
        拍摄 icon 并显示在 self.ui.Preview_label
        """
        localiconpath = self.Pub.makePath(str('%s/snapshot' % self.tempPath))
        wgt.clear()
        try:
            localicon = self.Pub.snapshot(localiconpath, imageFormat=imageFormat, frame=cmds.currentTime(query=True),
                                          need_createHistory=False)
            print("%s is snap shot !!" % localicon)
            wgt.setPixmap(QtGui.QPixmap(localicon))
        except Exception as e:
            print("Error : snapshot is stuck:%s" % e)

    def renderSeq(self, wgt):
        """
        渲染序列并显示在标签
        """
        # print("render Seq")
        actionPath = self.Pub.makePath(r'%s\sequence' % self.tempPath)
        wgt.clear()
        try:
            self.Pub.seqshot(actionPath)
            print("%s is seq shot !!" % actionPath)
            self.play(actionPath)
        except Exception as e:
            print("Error : seq shot is stuck:%s" % e)
        # # os.system(r"%s/jpg2gif.exe"%self.scriptsPath) #封装成exe可以，但是不能传参
        # try:
        #     result = os.system("python %s/sources/jpg2gif.py" %self.scriptsPath)
        #     print(result)
        # except Exception as e:
        #     print(e)
        # wgt.setPixmap(QtGui.QPixmap("%s/sequence"))

        # self.__playSeq(r'%s\sequence' % self.tempPath)

    def capture_screen(self):
        """ 调用截图icon """
        try:
            capture.show_capture_screen(self)
        except Exception as e:
            print("Error : show capture screen is stuck:%s" % e)

    def set_thumbnail(self):
        # print("通信到Publish")
        localIconPath = str('%s/snapshot/thumbnail.png' % self.tempPath)
        if self.ui.Pub_Tab.currentIndex() == 0:  # Model===============================================================
            wgt = self.ui.Preview_label
        elif self.ui.Pub_Tab.currentIndex() == 1:  # Rig===============================================================
            wgt = self.ui.Preview_label_rig
        elif self.ui.Pub_Tab.currentIndex() == 2:  # Scene=============================================================
            wgt = self.ui.Preview_label_sc
        wgt.clear()
        wgt.setPixmap(QtGui.QPixmap(localIconPath))

    def play(self, path):
        """Start playing the image sequence movie."""
        movie = None
        if os.path.isfile(path) and path.lower().endswith(".gif"):
            self.__playGif(path)
        elif os.path.isdir(path):
            movie = imagesequence.ImageSequence(path)
            movie.frameChanged.connect(self.__frameChanged)
            self._imageSequence = movie
        if movie:
            movie.start()

    def __frameChanged(self, frame=None):
        """Triggered when the movie object updates to the given frame."""
        if self._imageSequence:
            pixmap = self._imageSequence.currentPixmap()
            if self.ui.Preview_label_ac:
                self.ui.Preview_label_ac.setPixmap(pixmap)

    def __playGif(self, path):
        """
        将gif显示在Action预览面板
        """
        player = sequenceplayer.Player()
        self.ui.Preview_label_ac.clear()
        preview_dir = QtCore.QDir(path)
        for i in preview_dir.entryList(['ActionGif.gif'], QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot):
            # item = QtWidgets.QListWidgetItem()
            # item.setSizeHint(QtCore.QSize(150, 180))
            # text = i.split('/')[(-1)].split('.')[0].split('_')[(-1)]
            # item.setText(text)
            # item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
            # widget2 = QtWidgets.QWidget()
            # lay = QtWidgets.QHBoxLayout()
            # lay.setContentsMargins(0, 0, 0, 0)
            # widget2.setLayout(lay)
            # label = QtWidgets.QLabel()
            player.movie.setFileName('%s/%s' % (path, i))
            # player.total_frame = player.movie.frameCount()
            # print("total_frame:", player.total_frame)
            # mov = QtGui.QMovie('%s/%s' % (path, i))
            # mov.start()

            # label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            # label.setMovie(self.player.movie)
            # lay.addWidget(label)
            # self.ui.iconDisplay_listWgt.addItem(item)
            # self.ui.iconDisplay_listWgt.setItemWidget(item, widget2)
            # mov.stop()
            # self.ui.Preview_label_ac.setScaledContents(True)
            self.ui.Preview_label_ac.setMovie(player.movie)
            player.play(100, self.ui.Play_toolBttn)

    # def _log(self, treeWgt, top, text, pix):
    #     self.log_thread = myWidget.MyThread()
    #     self.log_thread._signal.connect(lambda: self.__log(treeWgt, top, text, pix))
    #     self.log_thread.start()

    # def reset(self):
    #     """
    #     Stop and reset the current frame to 0.
    #
    #     :rtype: None
    #     """
    #     if not self._timer:
    #         self._timer = QtCore.QTimer(self.parent())
    #         self._timer.setSingleShot(False)
    #         self._timer.timeout.connect(self._update_log)
    #     self._timer.stop()
    #
    # def start(self):
    #     self.reset()
    #     if self._timer:
    #         self._timer.start(1000.0 / self._fps)
    #
    #
    # def _log_show(self, top, text, pix):
    #     # print("__log")
    #     item = QtWidgets.QTreeWidgetItem()
    #     item.setText(0, text)
    #     icon = QtGui.QIcon()
    #     icon.addPixmap(QtGui.QPixmap('%s/icon/%s.png' % (self.scriptsPath,pix)),
    #                    QtGui.QIcon.Normal, QtGui.QIcon.Off)
    #     item.setIcon(0, icon)
    #
    #     def __log_additem(top):
    #         if not top:
    #             self.ui.log_treeWgt.addTopLevelItem(item)
    #         else:
    #             top.setExpanded(True)
    #             top.addChild(item)
    #     self._log += "\n%s"%text
    #     return

    # def log_Mag(self):
    #     print("nooooooooooooooooooooooooddddddddddddddd")
    #     rootNode = Node("Hips")
    #     childNode0 = FailedNode(u"建立CGTW", rootNode)
    #     childNode1 = Node("RightPirateLeg_END", childNode0)
    #
    #     childNode2 = SucceedNode("LeftFemur", rootNode)
    #     childNode3 = Node("LeftTibia", childNode2)
    #     childNode4 = Node("LeftFoot", childNode3)
    #     childNode5 = SucceedNode("LeftFoot_END", childNode4)
    #
    #     self.model = LogModel(rootNode)
    #
    #     self.ui.log_treeView.setModel(self.model)
    #     self.ui.log_treeView.expandAll()
    #
    # def modifyModel(self):
    #     print("modifyModel")

    def logMsg(self, top, text, pix):
        self._log += u"\n> {0}".format(text)
        item = Log(self.ui.log_treeWgt, top, text, pix).run()
        return item

    def yes_bttn_clicked(self):
        tab = self.ui.Pub_Tab.currentIndex()
        if tab == 0:
            self._modPublish()
        elif tab == 1:
            self._rigPublish()
        elif tab == 2:
            self._scenePublish()
        elif tab == 3:
            self._actionPublish()

    def _modPublish(self):
        """
        发布模型
        """
        self.ui.log_treeWgt.clear()
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_mod()
        note = self.ui.info_lineEdit.text()
        Pub = publish.Publish()
        Pub.makePath(path)
        self.ui.log_progressBar.setVisible(True)
        self._log = "log:"
        self.ui.log_treeWgt.clear()
        # rightPirateLeg = self.model.index(0, 0, QtCore.QModelIndex())
        ''' ===========================检查===================================  '''
        if publishType == u"**":
            QtWidgets.QMessageBox.warning(self, 'Warning', u'请确定正确的类型 !')
            return
        ''' =========================== 没有数据库则创建数据 ===================================  '''
        if not self.createAssetsForSQL(projectName, characterName, characterCHName, publishType, note):
            reply = QtWidgets.QMessageBox.question(self, u'提示', u'数据库里有重名资产，确定继续发布吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logCGTW = self.logMsg(None, u"数据库上已有重名资产,成功覆盖", "succeed")
            else:
                self.logMsg(None, u"数据库上已有重名资产,不覆盖", "failed")
                return
        else:
            logCGTW = self.logMsg(None, u"已在数据库上建立新资产：{0}".format(characterName), "succeed")
        self.ui.log_progressBar.setValue(10)
        '''======================== 数据库直接通过 ==================================================='''
        if self.ui.approved_cBox.isChecked():
            try:
                self.approvedForSQL('asset', projectName, characterName, "asset.mod_status")
                self.logMsg(logCGTW, u"数据库状态已完成", "succeed")
            except Exception as e:
                self.logMsg(logCGTW, u"数据库状态已完成失败：%s" % e, "failed")
        # ''' ========================发布note================================================= '''
        # if self.ui.info_lineEdit.text() != "":
        #     try:
        #         self.createNoteForCGT('asset', projectName, characterName)
        #         self.logMsg(logCGTW, u"备注已发布", "succeed")
        #     except Exception as e:
        #         self.logMsg(logCGTW, u"备注发布失败：%s" % e, "failed")
        # self.ui.log_progressBar.setValue(15)
        ''' ============================ 清理文件 =============================================== '''
        try:
            self.modClean()
            self.logMsg(None, u"文件已清理", "succeed")
        except Exception as e:
            self.logMsg(None, u"文件清理失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(30)
        ''' ============================ 发布texture ==================================== '''
        if self.ui.textures_cBox.isChecked():
            try:
                Pub.makePath(str('%s/Texture' % path))
                Pub.repathTexture(str('%s/Texture' % path))
                self.logMsg(None, u"成功发布Texture", "succeed")
            except Exception as e:
                self.logMsg(None, u"Texture发布失败请检查:%s" % e, "failed")
        self.ui.log_progressBar.setValue(40)
        ''' =============================== 发布icon ======================================== '''
        if self.ui.icon_cBox.isChecked():
            try:
                src = str('%s/snapshot/thumbnail.png' % self.tempPath)
                dst = str('%s/%s' % (path, self.projectSetting()['iconFolder']))
                Pub.publish_icon(src, dst, characterName)
                # icon_path = Pub.snapshot(str('%s/%s' % (path, self.projectSetting()['iconFolder'])), characterName)
                # self.createImageForCGT('asset', projectName, characterName, icon_path)
                # self.createTask(projectName, characterName, icon_path)
                self.logMsg(None, u"发布Icon成功", "succeed")
            except Exception as e:
                self.logMsg(None, u"发布Icon失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(50)
        ''' ============================= 保存mod文件 ============================================ '''
        try:
            modFile = Pub.saveToServer(path, self.projectSetting()['modelFolder'], characterName,
                                       suffix=self.projectSetting()['modelFile'])
            self.logMsg(None, u"保存mod成功", "succeed")
        except Exception as e:
            self.logMsg(None, u"保存mod失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(90)
        ''' ============================== 发布xgen ==================================== '''
        if self.ui.xgen_cBox.isChecked():
            collectionsPath = "%sXgen/collections" % path
            try:
                Pub.makePath(str(collectionsPath))
                Pub.repathXGenData(str(collectionsPath))
                xgenFile = Pub.saveXGenFile(characterName, projectName, path, self.projectSetting()['xgenFileFolder'],
                                            self.projectSetting()['xgenFile'], self.projectSetting()['mayaFormat'])
                cmds.file(newFile=True, force=True)
                cmds.file(modFile, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
                self.logMsg(None, u"发布Xgen成功", "succeed")
            except Exception as e:
                self.logMsg(None, u"Xgen发布失败请检查:%s" % e, "failed")
        self.ui.log_progressBar.setValue(100)
        # cmds.file(force=True, new=True)
        ''' =============== END =========================================== '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                    u"<h3>组件发布完成!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(self._log)
        msg.exec_()
        self.ui.log_progressBar.setVisible(False)

    def _rigPublish(self):
        """
        发布绑定
        """
        print("_rigPublish")
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_rig()
        note = self.ui.info_lineEdit.text()
        Pub = publish.Publish()
        self._log = "log:"
        self.ui.log_treeWgt.clear()
        self.ui.log_progressBar.setVisible(True)
        ''' ============ 检查 ============================================= '''
        if publishType == u"**":
            QtWidgets.QMessageBox.warning(self, 'Warning', u'请确定正确的类型 !')
            return
        ''' ============ 没有数据库则建立数据 ============================================= '''
        # id = self.createAssetsForCGT(projectName, characterName, characterCHName, publishType)
        if not self.createRigAssetsForSQL(projectName, characterName, characterCHName, publishType, note):
            reply = QtWidgets.QMessageBox.question(self, u'提示', u'数据库里有重名资产，确定要继续吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logCGTW = self.logMsg(None, u"数据库里已有重名资产,成功覆盖", "succeed")
            else:
                self.logMsg(None, u"数据库里已有重名资产,不覆盖", "failed")
                return
        else:
            logCGTW = self.logMsg(None, u"已在数据库里建立资产：{0}".format(characterName), "succeed")
        self.ui.log_progressBar.setValue(10)
        cmds.waitCursor(state=True)
        ''' ================= 数据库里直接通过 =================================================== '''
        if self.ui.approved_cBox_2.isChecked():
            try:
                self.approvedForSQL('asset', projectName, characterName, "asset.rig_status")
                self.logMsg(logCGTW, u"数据库里已通过", "succeed")
            except Exception as e:
                self.logMsg(logCGTW, u"数据库里通过失败：%s" % e, "failed")
        # ''' ================ 发布note ================================================= '''
        # if self.ui.info_lineEdit.text() != "":
        #     try:
        #         self.createNoteForCGT('asset', projectName, characterName)
        #         self.logMsg(logCGTW, u"备注已发布", "succeed")
        #     except Exception as e:
        #         self.logMsg(logCGTW, u"备注发布失败：%s" % e, "failed")
        # self.ui.log_progressBar.setValue(15)
        ''' =============== 不存在icon则拍屏icon ========================================= '''
        if self.ui.icon_cBox_rig.isChecked():
            try:
                src = str('%s/snapshot/thumbnail.png' % self.tempPath)
                dst = str('%s/%s' % (path, self.projectSetting()['iconFolder']))
                Pub.publish_icon(src, dst, characterName)
                # icon_path = Pub.snapshot(str('%s/%s' % (path, self.projectSetting()['iconFolder'])), characterName)
                # self.createImageForCGT('asset', projectName, characterName, icon_path)
                # self.createTask(projectName, characterName, icon_path)
                self.logMsg(None, u"发布Icon成功", "succeed")
            except Exception as e:
                self.logMsg(None, u"发布Icon失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(20)
        ''' =============== 检查模型属性 =================================================== '''
        for mesh in cmds.listRelatives('Geometry', ad=1, fullPath=True, type='mesh'):
            Pub.setModelAttr(mesh)
        self.ui.log_progressBar.setValue(30)
        ''' ================== 清理 ============================================================ '''
        try:
            self.rigClean()
            self.logMsg(None, u"文件已清理", "succeed")
        except Exception as e:
            self.logMsg(None, u"文件清理失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(40)
        ''' ============== 复制Xgen ========================================================= '''
        if self.ui.xgen_cBox_2.isChecked():
            try:
                Pub.makePath(str('%s/xgen/collections' % path))
                Pub.repathXGenData(str('%s/xgen/collections' % path))
                self.logMsg(None, u"Xgen已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"Xgen发布失败请检查:%s" % e, "failed")
        self.ui.log_progressBar.setValue(50)
        ''' ============== 复制texture并重定向 ============================================== '''
        if self.ui.textures_cBox_2.isChecked():
            try:
                Pub.makePath(str('%s/Texture' % path))
                Pub.repathTexture(str('%s/Texture' % path))
                self.logMsg(None, u"Texture已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"Texture发布失败请检查:%s" % e, "failed")
        self.ui.log_progressBar.setValue(60)
        ''' ==================== 保存all rig档案 ============================================ '''
        try:
            allRigFile = Pub.saveToServer(path, self.projectSetting()['rigFolder'], characterName,
                                          suffix=self.projectSetting()['rigFileAll'])
            self.logMsg(None, u"all rig已发布", "succeed")
        except Exception as e:
            self.logMsg(None, u"all rig发布失败:%s" % e, "failed")
            QtWidgets.QMessageBox.warning(self, u"警告：", u"<h3>Rig发布出错，终止进程！</h3>")
            self.ui.log_progressBar.setVisible(False)
            cmds.waitCursor(state=False)
            return
        self.ui.log_progressBar.setValue(70)
        ''' ================ 保存hi rig档案 ================================================== '''
        try:
            # cmds.file(newFile=True, force=True)
            # cmds.file(allRigFile, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
            if cmds.objExists('{0}_XGen_GRP'.format(characterName)):
                cmds.delete('{0}_XGen_GRP'.format(characterName))
            if cmds.objExists('{0}_Sim_GRP'.format(characterName)):
                cmds.delete('{0}_Sim_GRP'.format(characterName))
            if cmds.objExists('{0}_HairPoly_GRP'.format(characterName)):
                cmds.setAttr('{0}_HairPoly_GRP.visibility'.format(characterName), 1)
            try:
                cmds.select('Sim')
                mel.eval('doDelete;')
            except:
                pass
            hiRigFile = Pub.saveToServer(path, self.projectSetting()['rigFolder'], characterName,
                                         suffix=self.projectSetting()['rigFileHi'],
                                         createHistory=False)
            self.logMsg(None, u"hi rig已发布", "succeed")
        except Exception as e:
            self.logMsg(None, u"hi rig发布失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(80)
        ''' ================ fbx发布 ============================================================ '''
        if self.ui.fbx_cBox_2.isChecked():
            try:
                self.rig_fbx_export(path, characterName)
                self.logMsg(None, u"fbx已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"fbx发布失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(85)
        ''' ================= 保存render档案 ===================================================== '''
        try:
            cmds.file(newFile=True, force=True)
            cmds.file(allRigFile, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
            cmds.select(cmds.ls(type='mesh'))
            cmds.delete(constructionHistory=True)
            cmds.select(clear=True)
            try:
                sets_list = cmds.lsThroughFilter('defaultSetFilter')
                sets_list.remove('defaultObjectSet')
                sets_list.remove('defaultLightSet')
                if sets_list:
                    cmds.delete(sets_list)
                cmds.delete('DeformationSystem')
                cmds.delete('other')
            except Exception as e:
                cmds.warning('Check your Rig Sets or DeformationSystem:%s' % e)
            Pub.removeUnknownNodes()
            Pub.removeUnusedShader()
            renderFile = Pub.saveToServer(path, self.projectSetting()['renderFolder'], characterName,
                                          suffix=self.projectSetting()['renderFile'])
            self.logMsg(None, u"Render档已发布", "succeed")
        except Exception as e:
            self.logMsg(None, u"Render档发布失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(90)
        ''' =============== 不存在则发布mod ===================================================== '''
        modFile = '%s/Mod/%s_mod.ma' % (path, characterName)
        if not os.path.exists(modFile):
            try:
                # Pub.makePath(str('%s/%s' % (path, self.projectSetting()['modelFolder'])))
                cmds.select(clear=True)
                Pub.doDeleteRig()
                Pub.saveToServer(path, self.projectSetting()['modelFolder'], characterName,
                                 suffix=self.projectSetting()['modelFile'])
                self.logMsg(None, u"mod档不存在，已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"mod档不存在，但发布失败: %s" % e, "failed")
        self.ui.log_progressBar.setValue(95)
        ''' ================= 重开 =================================================== '''
        cmds.file(newFile=True, force=True)
        cmds.file(allRigFile, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
        self.ui.log_progressBar.setValue(100)
        cmds.waitCursor(state=False)
        ''' =============== END ===============================================  '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                    u"<h3>Rig发布完成!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(self._log)
        msg.exec_()
        self.ui.log_progressBar.setVisible(False)

    def _scenePublish(self):
        res = self.check_sc()
        assemblies = self.assemblies
        if res == "isMAP":
            self._scenePublish_Map(assemblies[0])
        elif res == "isGRP":
            self._scenePublish_GRP(assemblies)
        elif res == "isSC":
            self._scenePublish_Single(assemblies[0])

    def _scenePublish_Map(self, assemblies):
        """
        发布Map场景组件
        """
        print("_scenePublish_Map")
        Pub = publish.Publish()
        self._log = "log:"
        self.ui.log_treeWgt.clear()
        self.ui.log_progressBar.setVisible(True)
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_sc()
        note = self.ui.info_lineEdit.text()
        ''' ====================== 检查 =================================================== '''
        if len(cmds.ls('Terrain')) != 1:
            cmds.warning(u'Can not find Terrain or More than two Terrain !')
            return
        ''' ============ 没有数据库则创建数据 =================================================== '''
        if not self.add_scene(projectName, assemblies, characterCHName, publishType, note):
            reply = QtWidgets.QMessageBox.question(self, u'提示', u'数据库里已有重名资产，确定继续发布吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logCGTW = self.logMsg(None, u"数据库里已有重名资产，已覆盖", "succeed")
            else:
                self.logMsg(None, u"数据库上已有重名资产，不覆盖", "failed")
                return
        else:
            logCGTW = self.logMsg(None, u"已在数据库上建立资产：{0}".format(assemblies), "succeed")
        self.ui.log_progressBar.setValue(10)
        ''' ================= 数据库直接通过 =================================================== '''
        if self.ui.approved_cBox_sc.isChecked():
            try:
                if self.approvedForSQL('scene', projectName, characterName, "scene.status"):
                    self.logMsg(logCGTW, u"数据库上已通过", "succeed")
                else:
                    self.logMsg(logCGTW, u"数据库上通过失败", "failed")
            except Exception as e:
                self.logMsg(logCGTW, u"数据库上通过失败：%s" % e, "failed")
        # ''' ================ 发布note ================================================= '''
        # if self.ui.info_lineEdit.text() != "":
        #     try:
        #         self.createNoteForCGT('map', projectName, characterName)
        #         self.logMsg(logCGTW, u"备注已发布", "succeed")
        #     except Exception as e:
        #         self.logMsg(logCGTW, u"备注发布失败：%s" % e, "failed")
        # self.ui.log_progressBar.setValue(15)
        ''' ============ 发布icon ================================================================= '''
        if self.ui.icon_cBox_sc.isChecked():
            icon_path = self.export_data(assemblies, 'MapIcon', False)
            try:
                src = str('%s/snapshot/thumbnail.png' % self.tempPath)
                Pub.publish_icon(src, icon_path, assemblies)
                # Pub.snapshot(icon_path, assemblies)
                # self.createImageForCGT('map', projectName, assemblies, "%s/%s.png" % (icon_path, assemblies))
                self.logMsg(None, u"新icon已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"icon发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(20)
        ''' =========== 发布texture ================================================================== '''
        if self.ui.textures_cBox_sc.isChecked():
            try:
                texture_path = self.export_data(assemblies, 'Texture', False)
                Pub.repathTexture(str('{0}'.format(texture_path)))
                self.logMsg(None, u"Texture发布成功", "succeed")
            except Exception as e:
                self.logMsg(None, u"Texture发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(30)
        ''' ============ 发布地图 ================================================================= '''
        try:
            mod_path = '{0}/{1}/{2}'.format(path, assemblies, 'MapFile')
            Pub.makePath(mod_path)
            cmds.select(assemblies)
            cmds.file('{0}/{1}_map.ma'.format(mod_path, assemblies), force=True, options='v=0;',
                      type='mayaAscii', preserveReferences=True, exportSelected=True)
            cmds.select(clear=True)
            self.logMsg(None, u"map已保存：{0}_map".format(assemblies), "succeed")
        except Exception as e:
            self.logMsg(None, u"map保存失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(100)
        ''' =============== END =============================================== '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                    u"提示：", u"<h3>Map发布完成!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(self._log)
        msg.exec_()
        self.ui.log_progressBar.setVisible(False)

    def _scenePublish_GRP(self, assemblies):
        """
        发布多场景组件
        """
        print("scenePublish_GRP")
        Pub = publish.Publish()
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_sc()
        note = self.ui.info_lineEdit.text()
        grp_name = assemblies[0].rsplit("_", 1)[0] + "_GRP"
        self._log = "log:"
        self.ui.log_treeWgt.clear()
        self.ui.log_progressBar.setVisible(True)
        ''' =============== 没有数据库则创建数据 =============================================== '''
        if not self.add_scene(projectName, grp_name, characterCHName, publishType, note):
            reply = QtWidgets.QMessageBox.question(self, u'提示', u'数据库里已有重名资产，确定继续发布吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logCGTW = self.logMsg(None, u"数据库里已有重名资产", "succeed")
            else:
                self.logMsg(None, u"数据库上已有重名资产，不覆盖", "failed")
                return
        else:
            logCGTW = self.logMsg(None, u"已在数据库上建立资产：{0}".format(grp_name), "succeed")
        self.ui.log_progressBar.setValue(10)
        ''' ================= 数据库直接通过 =================================================== '''
        if self.ui.approved_cBox_sc.isChecked():
            try:
                if self.approvedForSQL('scenes', projectName, characterName, "scene.status"):
                    self.logMsg(logCGTW, u"数据库上已通过", "succeed")
                else:
                    self.logMsg(logCGTW, u"数据库上通过失败", "failed")
            except Exception as e:
                self.logMsg(logCGTW, u"数据库上通过失败：%s" % e, "failed")
        # ''' ================发布note================================================= '''
        # if self.ui.info_lineEdit.text() != "":
        #     try:
        #         self.createNoteForCGT('scenes', projectName, characterName)
        #         self.logMsg(logCGTW, u"备注已发布", "succeed")
        #     except Exception as e:
        #         self.logMsg(logCGTW, u"备注发布失败：%s" % e, "failed")
        # self.ui.log_progressBar.setValue(15)
        ''' ===============发布icon=============================================== '''
        if self.ui.icon_cBox_sc.isChecked():
            icon_path = self.export_data(grp_name, 'Icon', False)
            try:
                src = str('%s/snapshot/thumbnail.png' % self.tempPath)
                Pub.publish_icon(src, icon_path, assemblies)
                # Pub.snapshot(icon_path, grp_name)
                # self.createImageForCGT('scenes', projectName, grp_name, "%s/%s.png" % (icon_path, grp_name))
                self.logMsg(logCGTW, u"icon已发布", "succeed")
            except Exception as e:
                self.logMsg(logCGTW, u"icon发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(30)
        ''' ===============发布贴图=============================================== '''
        if self.ui.textures_cBox_sc.isChecked():
            try:
                # Pub.makePath(str('%s/Texture' % path))
                # Pub.repathTexture(str('%s/Texture' % path))
                texture_path = self.export_data(grp_name, 'Texture', False)
                Pub.repathTexture(str('{0}'.format(texture_path)))
                self.logMsg(None, u"Texture已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"Texture发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(50)
        ''' ===============发布组件=============================================== '''
        mod_path = self.export_data(grp_name, 'Mod', False)
        cmds.file('{0}/{1}_mod.ma'.format(mod_path, grp_name),
                  force=True,
                  options='v=0;',
                  type='mayaAscii',
                  pr=True,
                  ea=True)
        for assemblie in assemblies:
            cmds.setAttr("{}.translateX".format(assemblie), 0)
            cmds.setAttr("{}.translateY".format(assemblie), 0)
            cmds.setAttr("{}.translateZ".format(assemblie), 0)
            try:
                self.export_mod(grp_name, assemblie, False)
                self.logMsg(None, u"{}_mod 已发布".format(assemblie), "succeed")
            except Exception as e:
                self.logMsg(None, u"_mod发布失败：%s" % e, "failed")
            try:
                self.export_port_Ai(grp_name, assemblie, False)
                self.logMsg(None, u"{}_port 已发布".format(assemblie), "succeed")
            except Exception as e:
                self.logMsg(None, u"_port发布失败：%s" % e, "failed")
            try:
                self.export_AD(grp_name, assemblie, False)
                self.logMsg(None, u"{}_AD 已发布".format(assemblie), "succeed")
            except Exception as e:
                self.logMsg(None, u"_AD发布失败：%s" % e, "failed")
            try:
                self.sc_fbx_export(grp_name, assemblie, False)
                self.logMsg(None, u"{}.fbx 已发布".format(assemblie), "succeed")
            except Exception as e:
                self.logMsg(None, u".fbx发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(100)
        ''' ===============END=============================================== '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                    u"<h3>组件发布成功!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(self._log)
        msg.exec_()
        self.ui.log_progressBar.setVisible(False)

    def _scenePublish_Single(self, assemblies):
        """
        发布单个场景组件
        """
        print("_scenePublish_Single")
        Pub = publish.Publish()
        projectName, characterName, characterCHName, publishType, path = self.get_publishInfo_sc()
        note = self.ui.info_lineEdit.text()
        self._log = "log:"
        self.ui.log_treeWgt.clear()
        self.ui.log_progressBar.setVisible(True)

        ''' =============== 没有数据库则创建数据 =============================================== '''
        if not self.add_scene(projectName, assemblies, characterCHName, publishType, note):
            reply = QtWidgets.QMessageBox.question(self, '提示', u'数据库里已有重名资产，确定继续发布吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logCGTW = self.logMsg(None, u"数据库里已有重名资产", "succeed")
            else:
                self.logMsg(None, u"数据库上已有重名资产，不覆盖", "failed")
                return
        else:
            logCGTW = self.logMsg(None, u"已在数据库上建立资产：{0}".format(assemblies), "succeed")
        self.ui.log_progressBar.setValue(10)

        ''' ================= 数据库直接通过 =================================================== '''
        if self.ui.approved_cBox_sc.isChecked():
            try:
                if self.approvedForSQL('scenes', projectName, characterName, "scene.status"):
                    self.logMsg(logCGTW, u"数据库上已通过", "succeed")
                else:
                    self.logMsg(logCGTW, u"数据库上通过失败", "failed")
            except Exception as e:
                self.logMsg(logCGTW, u"数据库上通过失败：%s" % e, "failed")

        # ''' ================ 发布note ================================================= '''
        # if self.ui.info_lineEdit.text() != "":
        #     try:
        #         self.createNoteForCGT('scenes', projectName, characterName)
        #         self.logMsg(logCGTW, u"备注已发布", "succeed")
        #     except Exception as e:
        #         self.logMsg(logCGTW, u"备注发布失败：%s" % e, "failed")
        # self.ui.log_progressBar.setValue(15)

        ''' =============== 发布icon =============================================== '''
        if self.ui.icon_cBox_sc.isChecked():
            icon_path = self.export_data(assemblies, 'Icon', False)
            try:
                src = str('%s/snapshot/thumbnail.png' % self.tempPath)
                Pub.publish_icon(src, icon_path, assemblies)
                # Pub.snapshot(icon_path, assemblies)
                # self.createImageForCGT('scenes', projectName, assemblies, "%s/%s.png" % (icon_path, assemblies))
                self.logMsg(None, u"新icon已拍摄", "succeed")
            except Exception as e:
                self.logMsg(None, u"icon发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(30)

        ''' =============== 发布贴图 =============================================== '''
        if self.ui.textures_cBox_sc.isChecked():
            try:
                texture_path = self.export_data(assemblies, 'Texture', False)
                Pub.repathTexture(str('{0}'.format(texture_path)))
                self.logMsg(None, u"Texture已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"Texture发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(50)

        ''' =============== 发布组件 =============================================== '''
        try:  # ----------- mod
            self.export_mod(assemblies, assemblies)
            self.logMsg(None, u"{0}_mod 已发布".format(assemblies), "succeed")
        except Exception as e:
            self.logMsg(None, u"_mod发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(60)
        try:  # ----------- port
            self.export_port_Ai(assemblies, assemblies)
            self.logMsg(None, u"{0}_port 已发布".format(assemblies), "succeed")
        except Exception as e:
            self.logMsg(None, u"_port发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(70)
        try:  # ----------- AD
            self.export_AD(assemblies, assemblies)
            self.logMsg(None, u"{0}_AD 已发布".format(assemblies), "succeed")
        except Exception as e:
            self.logMsg(None, u"_AD发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(80)
        try:
            self.sc_fbx_export(assemblies, assemblies)
            self.logMsg(None, u"{0}.fbx 已发布".format(assemblies), "succeed")
        except Exception as e:
            self.logMsg(None, u".fbx发布失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(100)

        ''' =============== END =============================================== '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,
                                    u"提示：", u"<h3>组件发布完成!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(self._log)
        msg.exec_()
        self.ui.log_progressBar.setVisible(False)

    def _actionPublish(self):
        """
        动作库发布
        :return:
        """
        projectName, characterName, actionName, path, start, end = self.get_publishInfo_ac()
        # projectName, characterName, CHName, actionName, publishType, path, start, end = self.get_publishInfo_ac()
        self._log = "log:"
        self.ui.log_treeWgt.clear()
        self.ui.log_progressBar.setVisible(True)
        ''' =============== 检查 =============================================== '''
        if actionName == u"**":
            QtWidgets.QMessageBox.warning(self, 'Warning', u'请设置正确的动作名，比如：Run !')
            return
        # if publishType == u"**":
        #     QtWidgets.QMessageBox.warning(self, 'Warning', u'请选择一个类型 !')
        #     return
        if start >= end:
            QtWidgets.QMessageBox.warning(self, "Warning", u"结束帧请大于起始帧")
            self.ui.log_progressBar.setVisible(False)
            return
        # 控制器或模型都允许，只要选中了角色身上的物体即可
        controls = cmds.ls(sl=1, type='transform') or []
        if not controls:
            QtWidgets.QMessageBox.warning(self, "Warning", u"请至少选择一个物体")
            self.ui.log_progressBar.setVisible(False)
            return
        ''' =============== 拍icon =============================================== '''
        # iconPath = str('%s/snapshot/thumbnail.jpg' % self.tempPath)
        # sequencePath = self.tempPath + "/sequence"
        # if publishType == "Animation":
        #     self.Pub.seqshot(sequencePath)
        ''' =============== 发布动作库 =============================================== '''
        # try:
        #     self.Pub.makePath(path)
        #     if publishType == "Animation":
        #         animation.saveAnim(path=path,
        #                            objects=controls,
        #                            time=(start, end),
        #                            iconPath=iconPath,
        #                            sequencePath=sequencePath,
        #                            metadata={'description': u'%s' % CHName})
        #     else:
        #         pose.savePose(path=path,
        #                       objects=controls,
        #                       iconPath=iconPath,
        #                       metadata={'description': u'%s' % CHName})
        #     self.logMsg(None, u"动作{}已发布".format(actionName), "succeed")
        # except Exception as e:
        #     self.logMsg(None, u"动作{0}发布失败：{1}".format(actionName, e), "failed")
        self.ui.log_progressBar.setValue(50)
        ''' =============== 保存maya档 =============================================== '''
        try:
            filePath = '%s/%s_%s.ma' % (path, characterName, actionName)
            cmds.file(rename=filePath)
            cmds.file(save=True, type='mayaAscii')
            self.logMsg(None, u"maya保存成功", "succeed")
        except Exception as e:
            self.logMsg(None, u"maya保存失败：%s" % e, "failed")
        self.ui.log_progressBar.setValue(80)
        ''' =============== 发布fbx =============================================== '''
        if self.ui.fbx_cBox_4.isChecked():
            # if publishType == "Animation":
            try:
                filePath = '%s/%s_%s.fbx' % (path, characterName, actionName)
                self.ani_fbx_export(filePath, start, end)
                self.logMsg(None, u"fbx已发布", "succeed")
            except Exception as e:
                self.logMsg(None, u"fbx发布失败:%s" % e, "failed")
        self.ui.log_progressBar.setValue(100)
        ''' =============== END =============================================== '''
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                    u"<h3>组件发布成功!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(self._log)
        msg.exec_()
        self.ui.log_progressBar.setVisible(False)

    # def _______actionPublish(self, path, time=None, sampleBy=1, fileType="",
    #                          bakeConnected=True):
    #     """
    #     Save all animation data from the objects set on the Anim object.
    #
    #     :type path: str
    #     :type time: (int, int) or None
    #     :type sampleBy: int
    #     :type fileType: str
    #     :type bakeConnected: bool
    #
    #     :rtype: None
    #     """
    #     objects = list(self.objects().keys())
    #
    #     fileType = "mayaBinary"
    #     MIN_TIME_LIMIT = -10000
    #     MAX_TIME_LIMIT = 100000
    #     FIX_SAVE_ANIM_REFERENCE_LOCKED_ERROR = True
    #
    #     if not time:
    #         time = mutils.selectedObjectsFrameRange(objects)
    #     start, end = time
    #
    #     # Check selected animation layers
    #     self.validateAnimLayers()
    #
    #     # Check frame range
    #     if start is None or end is None:
    #         msg = "Please specify a start and end frame!"
    #         raise AnimationTransferError(msg)
    #
    #     if start >= end:
    #         msg = "The start frame cannot be greater than or equal to the end frame!"
    #         raise AnimationTransferError(msg)
    #
    #     # Check if animation exists
    #     if mutils.getDurationFromNodes(objects or []) <= 0:
    #         msg = "No animation was found on the specified object/s! " \
    #               "Please create a pose instead!"
    #         raise AnimationTransferError(msg)
    #
    #     self.setMetadata("endFrame", end)
    #     self.setMetadata("startFrame", start)
    #
    #     end += 1
    #     validCurves = []
    #     deleteObjects = []
    #
    #     msg = u"Animation.save(path={0}, time={1}, bakeConnections={2}, sampleBy={3})"
    #     msg = msg.format(path, str(time), str(bakeConnected), str(sampleBy))
    #     # logger.debug(msg)
    #
    #     try:
    #         if bakeConnected:
    #             cmds.undoInfo(openChunk=True)
    #             mutils.bakeConnected(objects, time=(start, end), sampleBy=sampleBy)
    #
    #         for name in objects:
    #             if cmds.copyKey(name, time=(start, end), includeUpperBound=False, option="keys"):
    #
    #                 # Might return more than one object when duplicating shapes or blendshapes
    #                 transform, = cmds.duplicate(name, name="CURVE", parentOnly=True)
    #
    #                 if not FIX_SAVE_ANIM_REFERENCE_LOCKED_ERROR:
    #                     mutils.disconnectAll(transform)
    #
    #                 deleteObjects.append(transform)
    #                 cmds.pasteKey(transform)
    #
    #                 attrs = cmds.listAttr(transform, unlocked=True, keyable=True) or []
    #                 attrs = list(set(attrs) - {'translate', 'rotate', 'scale'})
    #
    #                 for attr in attrs:
    #                     dstAttr = mutils.Attribute(transform, attr)
    #                     dstCurve = dstAttr.animCurve()
    #
    #                     if dstCurve:
    #
    #                         dstCurve = cmds.rename(dstCurve, "CURVE")
    #                         deleteObjects.append(dstCurve)
    #
    #                         srcAttr = mutils.Attribute(name, attr)
    #                         srcCurve = srcAttr.animCurve()
    #
    #                         if srcCurve:
    #                             preInfinity = cmds.getAttr(srcCurve + ".preInfinity")
    #                             postInfinity = cmds.getAttr(srcCurve + ".postInfinity")
    #                             curveColor = cmds.getAttr(srcCurve + ".curveColor")
    #                             useCurveColor = cmds.getAttr(srcCurve + ".useCurveColor")
    #
    #                             cmds.setAttr(dstCurve + ".preInfinity", preInfinity)
    #                             cmds.setAttr(dstCurve + ".postInfinity", postInfinity)
    #                             cmds.setAttr(dstCurve + ".curveColor", *curveColor[0])
    #                             cmds.setAttr(dstCurve + ".useCurveColor", useCurveColor)
    #
    #                         if cmds.keyframe(dstCurve, query=True, time=(start, end), keyframeCount=True):
    #                             self.setAnimCurve(name, attr, dstCurve)
    #                             cmds.cutKey(dstCurve, time=(MIN_TIME_LIMIT, start - 1))
    #                             cmds.cutKey(dstCurve, time=(end + 1, MAX_TIME_LIMIT))
    #                             validCurves.append(dstCurve)
    #
    #         fileName = "animation.ma"
    #         if fileType == "mayaBinary":
    #             fileName = "animation.mb"
    #
    #         mayaPath = os.path.join(path, fileName)
    #         posePath = os.path.join(path, "pose.json")
    #         mutils.Pose.save(self, posePath)
    #
    #         if validCurves:
    #             cmds.select(validCurves)
    #             # logger.info("Saving animation: %s" % mayaPath)
    #             cmds.file(mayaPath, force=True, options='v=0', type=fileType, uiConfiguration=False,
    #                       exportSelected=True)
    #             self.cleanMayaFile(mayaPath)
    #
    #     finally:
    #         if bakeConnected:
    #             # HACK! Undo all baked connections. :)
    #             cmds.undoInfo(closeChunk=True)
    #             cmds.undo()
    #         elif deleteObjects:
    #             cmds.delete(deleteObjects)
    #
    #     self.setPath(path)

    def validateAnimLayers(self):
        """
        Check if the selected animation layer can be exported.
        :raise: AnimationTransferError
        """
        if cmds.about(q=True, batch=True):
            return

        animLayers = mel.eval('$gSelectedAnimLayers=$gSelectedAnimLayers')

        # Check if more than one animation layer has been selected.
        if len(animLayers) > 1:
            QtWidgets.QMessageBox.warning(self, 'Warning', u'只能有一个动画层,请检查!!!')
            return False

        # Check if the selected animation layer is locked
        if len(animLayers) == 1:
            if cmds.animLayer(animLayers[0], query=True, lock=True):
                QtWidgets.QMessageBox.warning(self, 'Warning', u'动画层已被锁定,请检查!!!')
                return False
        return True

    def get_asset_list(self):
        """
        根据 project,type 得到 asset_list, type_path
        """
        currentProj = self.ui.publishProj_comb.currentText()
        currentType = self.ui.publishType_comb_sc.currentText()
        type_path = '{0}/{1}/Scenes/{2}'.format(self.projectSetting()['rootPath'], currentProj, currentType)
        directory = QtCore.QDir(type_path)
        asset_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries,
                                         QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        return asset_list, type_path

    def export_data(self, asset_name, part, boolHistory):
        """
        导出设置，建立data_path
        :param asset_name: 资产名字
        :param part: 环节
        :param boolHistory: 是否建立历史
        :return:
        """
        asset_list, type_path = self.get_asset_list()
        # if current_type == 'Map':
        #     data_path = ('{0}/{1}/{2}/{3}').format(type_path, asset_name, 'Terrain', type)
        # else:
        data_path = '{0}/{1}/{2}'.format(type_path, asset_name, part)
        self.Pub.makePath(data_path)
        if boolHistory:
            self.Pub.createHistory(data_path)
        return data_path

    @staticmethod
    def modClean():
        Pub = publish.Publish()
        Pub.removeAllNameSpace()
        Pub.removeAllDisplayLayer()
        Pub.removeUnknownNodes()
        Pub.removeUnusedShader()
        Pub.removeAllAOV()
        Pub.removeAllAnimLayer()
        Pub.removeAllRenderLayer()
        Pub.modClean()

    @staticmethod
    def rigClean():
        Pub = publish.Publish()
        Pub.virusCheck()
        Pub.removeAllNameSpace()
        Pub.removeAllDisplayLayer()
        Pub.removeUnknownNodes()
        Pub.removeUnusedShader()
        Pub.removeModelChangeError()

    @staticmethod
    def currentDate():
        """ 当前时间 """
        return time.strftime('%Y%m%d', time.localtime())

    def createAssetsForSQL(self, proj_name, assets_name, assets_zh_name, assets_type, note):
        return self.add_asset(proj_name, assets_name, assets_zh_name, assets_type, note)

    def add_asset(self, db, name, zh_name, _type, note):
        """ 新增资产 """
        date = self.currentDate()
        icon = "Y:/MCCProject/{0}/Assets/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.asset ("asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", 
            "asset.mod_status", "asset.icon", "asset.type", "asset.note") 
            VALUES 
            ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text, '未开始'::text, 
            '%s'::text, '%s'::text, '%s'::text)
            returning asset."asset.name";
        ''' % (date, name, zh_name, self.user, icon, _type, note)
        print(insert_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
            return True
        except Exception as e:
            cmds.warning(e)
            return False
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def createRigAssetsForSQL(self, proj_name, assets_name, assets_zh_name, assets_type, note):
        return self.add_rig_asset(proj_name, assets_name, assets_zh_name, assets_type, note)

    def add_rig_asset(self, db, name, zh_name, _type, note):
        """ 新增资产 """
        date = self.currentDate()
        icon = "Y:/MCCProject/{0}/Assets/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.asset ("asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", "asset.mod_status",
            "asset.rig_artist", "asset.rig_status", "asset.icon", "asset.type", "asset.note") 
            VALUES 
            ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text, '已完成'::text, 
            '%s'::text, '未开始'::text, '%s'::text, '%s'::text, '%s'::text)
            returning asset."asset.name";
        ''' % (date, name, zh_name, self.user, self.user, icon, _type, note)
        print(insert_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
            return True
        except Exception as e:
            cmds.warning(e)
            return False
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def add_scene(self, db, name, zh_name, _type, note):
        """ 新增场景 """
        date = self.currentDate()
        icon = "Y:/MCCProject/{0}/Scenes/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.scene ("scene.date", "scene.name", "scene.zh_name", "scene.artist", "scene.status", 
            "scene.icon", "scene.type", "scene.note") 
            VALUES 
            ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text, '未开始'::text, '%s'::text, '%s'::text, '%s'::text)
            returning scene."scene.name";
        ''' % (date, name, zh_name, self.user, icon, _type, note)
        print(insert_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
            return True
        except Exception as e:
            cmds.warning(e)
            return False
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def createAssetsForCGT(self, proj_name, assets_name, assets_CHname, assets_type):
        """
        建立CGT
        :param proj_name:
        :param assets_name:
        :param assets_CHname:
        :param assets_type:
        :return:
        """
        t_tw = cgtw2.tw()
        projectdiction = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=projectdiction,
                                            module='asset',
                                            filter_list=[['asset.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            infoID = t_tw.info.create(db=projectdiction,
                                      module='asset',
                                      sign_data_dict={'asset.entity': assets_name,
                                                      'asset.assetstapy': assets_type,
                                                      'asset.cn_name': assets_CHname},
                                      is_return_id=True)
            return infoID

    def createScenesForCGT(self, proj_name, assets_name, assets_CHname, assets_type):
        """
        建立CGT
        """
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=TW_proj,
                                            module='scenes',
                                            filter_list=[['scenes.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            infoID = t_tw.info.create(db=TW_proj, module='scenes',
                                      sign_data_dict={'scenes.entity': assets_name,
                                                      'scenes.scenesassetstype': assets_type,
                                                      'scenes.assetsnamecn': assets_CHname},
                                      is_return_id=True)
            return infoID

    def createMapForCGT(self, proj_name, assets_name, assets_CHname):
        """
        建立CGT——MAP
        """
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=TW_proj,
                                            module='map',
                                            filter_list=[['map.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            infoID = t_tw.info.create(db=TW_proj,
                                      module='map',
                                      sign_data_dict={'map.entity': assets_name,
                                                      'map.type': 'Map',
                                                      'map.mapnamecn': assets_CHname},
                                      is_return_id=True)
            return infoID

    def createNoteForCGT(self, module, proj, assets_name):
        """
        发布NOTE
        :param module:
        :param proj:
        :param assets_name:
        :return:
        """
        # print("_notePublish")
        t_tw = cgtw2.tw()
        projectdiction = self.projectSetting()['projectdiction'][proj]
        text = self.ui.info_lineEdit.text()
        if module == 'asset':
            entity = 'asset.entity'
        elif module == 'scenes':
            entity = 'scenes.entity'
        elif module == 'map':
            entity = 'map.entity'
        t_id_list = t_tw.task.get_id(projectdiction,
                                     module=module,
                                     filter_list=[[entity, '=', assets_name]])
        t_tw.note.create(db=projectdiction,
                         module=module,
                         module_type='task',
                         link_id_list=t_id_list,
                         text=text)

    def createImageForCGT(self, module, proj_name, assets_name, assets_icon):
        """
        CGT没有icon则发布icon
        """
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        if module == 'asset':
            entity = 'asset.entity'
            image = 'asset.image'
        elif module == 'scenes':
            entity = 'scenes.entity'
            image = 'scenes.image'
        elif module == 'map':
            entity = 'map.entity'
            image = 'map.image'
        t_asset_ids = t_tw.info.get_id(db=TW_proj,
                                       module=module,
                                       filter_list=[[entity, '=', assets_name]])
        TW_dictionInfo = t_tw.info.get(TW_proj, module, t_asset_ids, [entity, image])
        if TW_dictionInfo[0][image] == "":
            t_tw.info.set_image(db=TW_proj,
                                module=module,
                                id_list=t_asset_ids,
                                field_sign=image,
                                img_path=assets_icon)
        else:
            print(u"已存在:", TW_dictionInfo[0][image])

    def approvedForSQL(self, module, db, asset_name, key):
        if module == 'asset':
            update_script = '''
                UPDATE public.asset SET
                "%s" = "已完成"
                WHERE
                "asset.name" = '%s';
            ''' % (key, asset_name)
        else:
            update_script = '''
                UPDATE public.scene SET
                "%s" = "已完成"
                WHERE
                "scene.name" = '%s';
            ''' % (key, asset_name)
        # print(update_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(update_script)
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def approvedForCGT(self, module, proj_name, assets_name):
        """
        直接通过
        """
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]

        if module == 'scenes':
            entity = 'scenes.entity'
            approve = 'scenes.maya'
        elif module == 'map':
            entity = 'map.entity'
            approve = 'map.maya'
        else:
            entity = 'asset.entity'
            approve = 'asset.maya'

        id = t_tw.info.get_id(db=TW_proj,
                              module=module,
                              filter_list=[[entity, '=', assets_name]])
        result = t_tw.info.set(db=TW_proj, module=module, id_list=id, sign_data_dict={approve: u'完成'})
        return result

    def createTask(self, proj_name, assets_name, assets_icon):
        """
        发布任务并提交icon审核
        :param proj_name:
        :param assets_name:
        :param assets_icon:
        :return:
        """
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        ids = t_tw.info.get_id(db=TW_proj, module='asset', filter_list=[['asset.entity', '=', assets_name]])
        t_pipeline_id_list = t_tw.pipeline.get_id(TW_proj,
                                                  filter_list=[['module', '=', 'asset'], 'and', ['entity', '=', 'Mod']])
        t_flow_list = t_tw.flow.get_data(TW_proj, t_pipeline_id_list)
        for _flow in t_flow_list:
            _pipeline_id = _flow['pipeline_id']
            _flow_id = _flow['flow_id']
            _pipeline_name = _flow['pipeline_name']
            t_res = t_tw.task.create(TW_proj, 'asset', ids[0], _pipeline_id, _pipeline_name, _flow_id, True)
            t_tw.task.submit(TW_proj, 'asset', t_res, [assets_icon])

    def export_GPU(self, grp_name, asset_name, history=True):
        """
        发布GPU
        :param grp_name:
        :param history:
        :param asset_name:
        :return:
        """
        gpu_path = self.export_data(grp_name, 'GPU', history)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        create_gpuCache = (
            'gpuCache -startTime 1 -endTime 1 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat '
            'ogawa -directory "{0}" -fileName "{1}_GPU" {1}; ').format(gpu_path, asset_name)
        mel.eval(create_gpuCache)
        return gpu_path

    def export_proxy_Rs(self, asset_name):
        """
        发布RS
        :param asset_name:
        :return:
        """
        # ''' 检查插件'''
        # if self.Pub.pluginInfo('redshift4maya.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
        #     return
        # if self.Pub.pluginInfo('sceneAssembly.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
        #     return
        proxy_path = self.export_data(asset_name, 'Proxy', True)
        current_type = self.ui.scene_type_listWgt.currentItem().text()
        if current_type == 'Map':
            asset_name = 'Terrain'
        cmds.select(asset_name)
        cmds.rsProxy(sl=True, fp='{0}/{1}_proxy.rs'.format(proxy_path, asset_name))
        cmds.select(clear=True)
        return proxy_path

    def export_proxy_Ai(self, grp_name, asset_name, history=True):
        """
        发布ASS
        :param history:
        :param grp_name:
        :param asset_name:
        :return:
        """
        # ''' 检查插件'''
        # if self.Pub.pluginInfo('sceneAssembly.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 sceneAssembly，请加载')
        #     raise Exception(u"未发现 sceneAssembly")
        # if self.Pub.pluginInfo('mtoa.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, u'警告', u'未发现 mtoa，请加载')
        #     raise Exception(u"未发现 mtoa")
        proxy_path = self.export_data(grp_name, 'Proxy', history)
        # current_type = self.ui.publishType_comb_sc.currentText()
        # if current_type == 'Map':
        #     asset_name = 'Terrain'
        cmds.select(asset_name)
        cmds.file('{0}/{1}_proxy.ass'.format(proxy_path, asset_name), es=1, type="ASS Export")
        cmds.select(clear=True)
        return proxy_path

    def export_port_Ai(self, grp_name, asset_name, history=True):
        """
        发布 Arnold--port
        :param grp_name: 组名字（单组件就是资产名字）
        :param asset_name: 资产名字
        :param history:
        :return:
        """
        ''' 检查插件'''
        self.port_path = self.export_data(grp_name, 'Port', history)
        '''发布GPU，Proxy，'''
        gpu_path = self.export_GPU(grp_name, asset_name, history)
        proxy_path = self.export_proxy_Ai(grp_name, asset_name, history)
        # current_type = self.ui.publishType_comb_sc.currentText()
        # if current_type == 'Map':
        #     asset_name = 'Terrain'
        self.gpu_file_path = '{0}/{1}_GPU.abc'.format(gpu_path, asset_name)
        self.proxy_file_path = '{0}/{1}_proxy.ass'.format(proxy_path, asset_name)
        if QtCore.QFileInfo(self.gpu_file_path).exists() and QtCore.QFileInfo(self.proxy_file_path).exists():
            # current_type = self.ui.publishType_comb_sc.currentText()
            # if current_type != 'Scene':
            #     try:
            #         cmds.delete(asset_name)
            #     except:
            #         cmds.warning('Can not delete {0}'.format(asset_name))

            '''创建ass挂载到Gpu'''
            mel.eval('cmdArnoldCreateStandIn')
            new_name = cmds.rename(cmds.ls('aiStandIn*', type='transform')[0], '{0}_ASS'.format(asset_name))
            cmds.setAttr('{0}.dso'.format(cmds.ls(new_name + "Shape", type='aiStandIn')[0]),
                         self.proxy_file_path, type='string')
            container_name = cmds.container(addNode=new_name, type='dagContainer', ind=('history', 'channels'),
                                            includeHierarchyBelow=True, includeTransform=True, force=True)
            # cmds.setAttr(('{0}.lodVisibility').format(container_name), 0) #新版本Ai会渲染不出来
            gpu_trans = cmds.createNode('transform', name=asset_name)

            gpu_node = cmds.createNode('gpuCache', name='{0}Shape'.format(asset_name), parent=gpu_trans)
            cmds.setAttr('{0}.cacheFileName'.format(gpu_node), self.gpu_file_path, type='string')
            cmds.setAttr('{0}.cacheGeomPath'.format(gpu_node), '|', type='string')
            cmds.setAttr('{0}.primaryVisibility'.format(gpu_node), 0)
            cmds.setAttr('{0}.castsShadows'.format(gpu_node), 0)
            cmds.setAttr('{0}.receiveShadows'.format(gpu_node), 0)
            cmds.setAttr('{0}.aiVisibleInDiffuseReflection'.format(gpu_node), 0)
            cmds.setAttr('{0}.aiVisibleInSpecularReflection'.format(gpu_node), 0)
            cmds.setAttr('{0}.aiVisibleInDiffuseTransmission'.format(gpu_node), 0)
            cmds.setAttr('{0}.aiVisibleInSpecularTransmission'.format(gpu_node), 0)
            cmds.setAttr('{0}.aiVisibleInVolume'.format(gpu_node), 0)
            cmds.setAttr('{0}.aiSelfShadows'.format(gpu_node), 0)
            cmds.parent(container_name, gpu_trans)
            cmds.select(gpu_trans)

            cmds.file('{0}/{1}_port.ma'.format(self.port_path, asset_name), force=True, options='v=0;',
                      type='mayaAscii', pr=True, es=True)
            cmds.delete(gpu_trans)
        else:
            cmds.warning('Can not find {0} or {1}'.format(self.gpu_file_path, self.proxy_file_path))
            raise Exception('Can not find {0} or {1}'.format(self.gpu_file_path, self.proxy_file_path))

    def export_port_Rs(self, grp_name, asset_name):
        """
        发布Redshift--port
        :param grp_name:
        :param asset_name:
        :return:
        """
        # ''' 检查插件'''
        # if self.Pub.pluginInfo('redshift4maya.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
        #     return
        # if self.Pub.pluginInfo('sceneAssembly.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
        #     return
        self.port_path = self.export_data(grp_name, 'Port', True)
        gpu_path = self.export_GPU(asset_name)
        proxy_path = self.export_proxy_Rs(asset_name)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        self.gpu_file_path = '{0}/{1}_GPU.abc'.format(gpu_path, asset_name)
        self.proxy_file_path = '{0}/{1}_proxy.rs'.format(proxy_path, asset_name)
        if QtCore.QFileInfo(self.gpu_file_path).exists() and QtCore.QFileInfo(self.proxy_file_path).exists():
            current_type = self.ui.publishType_comb.currentText()
            if current_type != 'Scene':
                try:
                    cmds.delete(asset_name)
                except:
                    cmds.warning('Can not delete {0}'.format(asset_name))
                    return
            '''创建Rs挂载到Gpu'''
            redshift_proxy = mel.eval('redshiftCreateProxy')
            new_name = cmds.rename(cmds.ls(redshift_proxy, type='transform')[0], '{0}_RS'.format(asset_name))
            cmds.setAttr('{0}.fileName'.format(cmds.ls(redshift_proxy, type='RedshiftProxyMesh')[0]),
                         self.proxy_file_path, type='string')
            container_name = cmds.container(addNode=new_name, type='dagContainer', ind=('history', 'channels'),
                                            includeHierarchyBelow=True, includeTransform=True, force=True)
            cmds.setAttr('{0}.lodVisibility'.format(container_name), 0)
            gpu_trans = cmds.createNode('transform', name=asset_name)
            gpu_node = cmds.createNode('gpuCache', name='{0}Shape'.format(asset_name), parent=gpu_trans)
            cmds.setAttr('{0}.cacheFileName'.format(gpu_node), self.gpu_file_path, type='string')
            cmds.setAttr('{0}.cacheGeomPath'.format(gpu_node), '|', type='string')
            cmds.parent(container_name, gpu_trans)
            cmds.select(gpu_trans)
            cmds.file('{0}/{1}_port.ma'.format(self.port_path, asset_name), force=True, options='v=0;',
                      type='mayaAscii', pr=True, es=True)
            cmds.delete(gpu_trans)
        else:
            cmds.warning('Can not find {0} or {1}'.format(self.gpu_file_path, self.proxy_file_path))

    def export_mod(self, grp_name, asset_name, history=True):
        """
        发布模型ma
        :param grp_name:
        :param history:
        :param asset_name:
        :return:
        """
        self.mod_path = self.export_data(grp_name, 'Mod', history)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        cmds.select(asset_name)
        cmds.file('{0}/{1}_mod.ma'.format(self.mod_path, asset_name), force=True, options='v=0;', type='mayaAscii',
                  pr=True, es=True)
        cmds.select(clear=True)

    def export_AD(self, grp_name, asset_name, history=True):
        """
        发布 Assembly Definition
        :param history:
        :param grp_name:
        :param asset_name:
        :return:
        """
        AD_path = self.export_data(grp_name, 'Assembly', history)
        # current_type = self.ui.publishType_comb.currentText()
        # if current_type == 'Map':
        #     asset_name = 'Terrain'
        AD_name = cmds.assembly(name='{0}_AD'.format(asset_name), type='assemblyDefinition')
        port_file_path = '{0}/{1}_port.ma'.format(self.port_path, asset_name)
        mod_file_path = '{0}/{1}_mod.ma'.format(self.mod_path, asset_name)
        if QtCore.QFileInfo(self.gpu_file_path).exists() and QtCore.QFileInfo(port_file_path).exists() \
                and QtCore.QFileInfo(mod_file_path).exists():
            # cmds.assembly(AD_name, edit=True, createRepresentation='Cache', repName=('{0}_GPU.abc').format(asset_name), input=self.gpu_file_path)
            cmds.assembly(AD_name, edit=True, createRepresentation='Scene', repName='{0}_port.ma'.format(asset_name),
                          input=port_file_path)
            cmds.assembly(AD_name, edit=True, createRepresentation='Scene', repName='{0}_mod.ma'.format(asset_name),
                          input=mod_file_path)
            cmds.assembly(AD_name, edit=True, activeLabel='{0}_port.ma'.format(asset_name))
            cmds.select(AD_name)
            cmds.file('{0}/{1}.ma'.format(AD_path, AD_name), force=True, options='v=0;', type='mayaAscii', pr=True,
                      es=True)
            cmds.delete(AD_name)
        else:
            cmds.warning('Can not find mod/port/GPU')
            raise Exception('Can not find mod/port/GPU')

    def rig_fbx_export(self, path, characterName):
        """发布绑定fbx"""
        cmds.select(clear=True)
        fbxFolderPath = '%s/%s' % (path, 'FBX')
        self.Pub.makePath(fbxFolderPath)
        self.Pub.createHistory(fbxFolderPath)
        geometry_list = cmds.listRelatives("Geometry", allDescendents=False, fullPath=False)
        if len(geometry_list) == 1 and geometry_list[0].endswith("_AST"):
            geo_list = cmds.listRelatives(geometry_list[0], allDescendents=False, fullPath=False)
            if 'common' not in geo_list:
                cmds.select('Geometry')
                cmds.select('DeformationSystem', add=True)
                fbxPath = '%s/%s.fbx' % (fbxFolderPath, characterName)
                self.Pub.exportFBX(False, 1, 200, fbxPath)
            else:
                geo_list.remove('common')
                for sl in geo_list:
                    cmds.select(sl)
                    cmds.select('common', add=True)
                    cmds.select('DeformationSystem', add=True)
                    fbxPath = '%s/%s_%s.fbx' % (fbxFolderPath, characterName, sl)
                    self.Pub.exportFBX(False, 1, 200, fbxPath)
        else:
            if 'common' not in geometry_list:
                cmds.select('Geometry')
                cmds.select('DeformationSystem', add=True)
                fbxPath = '%s/%s.fbx' % (fbxFolderPath, characterName)
                self.Pub.exportFBX(False, 1, 200, fbxPath)
            else:
                geometry_list.remove('common')
                for sl in geometry_list:
                    cmds.select(sl)
                    cmds.select('common', add=True)
                    cmds.select('DeformationSystem', add=True)
                    fbxPath = '%s/%s_%s.fbx' % (fbxFolderPath, characterName, sl)
                    self.Pub.exportFBX(False, 1, 200, fbxPath)

    def sc_fbx_export(self, grp_name, asset_name, history=True):
        """发布静态资产fbx"""
        cmds.select(all=1)
        fbxFolderPath = self.export_data(grp_name, 'FBX', history)
        self.Pub.makePath(fbxFolderPath)
        self.Pub.createHistory(fbxFolderPath)
        fbxPath = '%s/%s.fbx' % (fbxFolderPath, asset_name)
        self.Pub.exportFBX(False, 1, 200, fbxPath)

    def ani_fbx_export(self, fbxPath, start, end):
        """发布动画fbx

        根据当前选择的物体（控制器或模型）推断角色所在的命名空间，
        再选中该角色的 ``<namespace>:DeformationSystem`` 骨骼组，
        最后调用 ``exportFBX`` 导出带烘焙动画的 fbx。
        """
        print("开始导出动画fbx", fbxPath, start, end)

        # 1. 从当前选择推断角色命名空间
        selection = cmds.ls(sl=True, long=True) or []
        if not selection:
            raise RuntimeError(u"请先选择角色身上的任意物体（控制器或模型）后再导出fbx")

        namespaces = []
        for node in selection:
            leaf = node.split('|')[-1]      # 去掉 DAG 路径，只保留带命名空间的节点名
            ns = leaf.rpartition(':')[0]    # 命名空间（兼容嵌套），无命名空间时为空串
            if ns and ns not in namespaces:
                namespaces.append(ns)

        if not namespaces:
            raise RuntimeError(u"选中的物体没有命名空间，无法确定是哪个角色，请确认选中的是引用进来的角色")
        if len(namespaces) > 1:
            cmds.warning(u"选择里包含多个角色 {0}，本次只导出第一个：{1}".format(namespaces, namespaces[0]))
        namespace = namespaces[0]

        # 2. 选中该角色的骨骼组 <namespace>:DeformationSystem
        deformGrp = '{0}:DeformationSystem'.format(namespace)
        if not cmds.objExists(deformGrp):
            raise RuntimeError(u"找不到角色 {0} 的骨骼组：{1}".format(namespace, deformGrp))

        cmds.select(deformGrp, replace=True)
        print(u"导出角色：{0}  骨骼组：{1}".format(namespace, deformGrp))

        # 3. 导出 fbx（exportFBX 内部用 FBXExport -s 导出当前选择及其层级）
        try:
            self.Pub.exportFBX(True, start, end, fbxPath)
        finally:
            # 还原用户的原始选择
            cmds.select(clear=True)
            if selection:
                cmds.select(selection)


def showWindow(tab=0, _project=None, _type=None):
    global win
    try:
        win.close()
    except:
        pass

    win = PubToolsUI(tab, _project, _type)
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()#dockable=False, width=780, height=500)#maya2020窗口不能前置未解决
