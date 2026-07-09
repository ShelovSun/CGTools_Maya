#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sceneTools_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import os
import time
import psycopg2

from functools import partial
from config import projectSetting

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel
from PySide2 import QtUiTools
from my_vendor.Qt import QtCore
from my_vendor.Qt import QtGui
from my_vendor.Qt import QtWidgets
from shiboken2 import wrapInstance
from utils import publish, messageBox
# from sources import assetTools
from widgets import faverWidget, am_main, previewWidget, am_pixmap

# import importlib
# importlib.reload(previewWidget)


def maya_main_window():
    """接收拖入用"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


class SceneToolsUI(QtWidgets.QWidget):
    MYPREFSDIR = cmds.internalVar(userPrefDir=True)
    # Result: u'C:/Users/asus/Documents/maya/2020/prefs/'
    tempPath = "{}AssetsManagerTemp".format(cmds.internalVar(userTmpDir=True))
    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')

    def __init__(self, isSQL=True,
                 ROOT="Y:/MCCProject",
                 user="",
                 password=""):
        super(SceneToolsUI, self).__init__()
        self.mayaMainWindow = maya_main_window()
        self.mayaMainWindow.setAcceptDrops(True)
        self.isSQL = isSQL
        self.host = projectSetting()["host"]
        self.user = user
        self.password = password

        f = QtCore.QFile('%s/ui/sceneTools.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()

        # 控件即界面：把 .ui 加载出的界面挂到自身，使 SceneToolsUI 本身即完整控件，
        # tabChanged 里可直接 addWidget(self.scene)（与 AssetToolsUI 一致）
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setContentsMargins(0, 0, 0, 0)
        _layout.addWidget(self.ui)

        self.asset_item_userRole = QtCore.Qt.UserRole
        # self.type_item_userRole = QtCore.Qt.UserRole + 1
        self.scenePub = publish.Publish()

        self.ROOT = ROOT

        self.isList = False
        self.group_component_expanded = True
        self.ar_switch_expanded = True

        # self.init_ui_thread = myWidget.MyThread()
        # self.init_ui_thread.signal.connect(self.init_ui)
        # self.init_ui_thread.start()
        # self.init_ui_thread.finished.connect(lambda: self.listWidgetAddItems(self.getItems()))

        self.init_ui()
        self.show_asset()

    def init_ui(self):
        # self.setCentralWidget(self.ui)
        self.firstView()

        '''左侧边栏'''
        self.ui.project_comb.currentIndexChanged.connect(self.projectChanged)
        self.ui.type_listWgt.itemSelectionChanged.connect(self.typeChanged)
        self.ui.type_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.type_listWgt.customContextMenuRequested.connect(self.show_menu_type)

        self.ui.Favorites_listWgt = faverWidget.FavoritesQListWiget(tab="Scene")
        self.ui.type_splitter.addWidget(self.ui.Favorites_listWgt)
        self.ui.type_splitter.setSizes([500, 300])
        self.ui.Favorites_listWgt.itemSelectionChanged.connect(self.faveChanged)

        '''上侧小按钮栏'''
        self.ui.add_bttn.setIcon(QtGui.QIcon('%s/icon/add.png' % self.scriptsPath))
        self.ui.add_bttn.clicked.connect(self.add_asset_ui)
        self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
        self.ui.displayThumb_bttn.clicked.connect(self.viewModeChanged)
        self.ui.itemSize_Slider.valueChanged.connect(self.itemSizeSliderChanged)
        self.ui.itemSize_Slider.setToolTip(u"%s" % self.ui.itemSize_Slider.value())
        self.ui.itemSize_Slider.sliderReleased.connect(self.rememberSettings)
        self.ui.download_Bttn.setIcon(QtGui.QPixmap('%s/icon/download.png' % self.scriptsPath))
        self.ui.download_Bttn.clicked.connect(self.download_asset)
        self.ui.refresh_Bttn.setIcon(QtGui.QPixmap('%s/icon/refresh.png' % self.scriptsPath))
        self.ui.refresh_Bttn.clicked.connect(self.refresh_asset)
        self.ui.key_line.returnPressed.connect(self.search_scene)
        self.ui.key_line.addAction(QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
                                   QtWidgets.QLineEdit.LeadingPosition)
        '''主界面栏'''
        self.ui.main_wgt = am_main.MainStackedWidget(tab="Scene", db=self.ui.project_comb.currentText(),
                                                           user=self.user, password=self.password,
                                                           islist=self.isList)
        self.ui.main_verticalLayout.addWidget(self.ui.main_wgt)
        self.ui.main_wgt.dragLeaveSignal_connect(self.mainWgtItemDragLeaved)
        self.ui.main_wgt.itemSelectionChanged_connect(self.mainWidgetItemChanged)
        self.ui.main_wgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.main_wgt.customContextMenuRequested.connect(self.show_menu)

        self.ui.mainWindow_splitter.setSizes([120, 500, 300])
        self.ui.mainWindow_splitter.setStretchFactor(0, False)
        self.ui.mainWindow_splitter.setStretchFactor(1, True)
        self.ui.mainWindow_splitter.setStretchFactor(2, False)

        '''右侧属性栏'''
        # self.ui.attr_splitter.setSizes([750, 500])
        self.ui.attr_splitter.setStretchFactor(1, False)
        self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
        self.ui.favor_bttn.clicked.connect(self.addFavor)
        self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
        self.ui.tag_bttn.clicked.connect(self.addTagUI)

        self.ui.preview = previewWidget.PreviewWidget(isPlayer=False)
        self.ui.preview_vLayout.addWidget(self.ui.preview)
        self.ui.preview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.preview.customContextMenuRequested.connect(self.show_menu_Preview)

        self.ui.group_component_tbttn.clicked.connect(self.group_component_clicked)
        self.ui.scene_int_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.scene_int_listWgt.customContextMenuRequested.connect(self.show_menu_int)
        self.ui.scene_int_listWgt.setStyleSheet("QListWidget:item:selected{background-color: rgb(65, 77, 88);}" +
                                                "QListWidget{background-color:rgb(43,43,43);}")
        self.ui.ar_switch_tbttn.clicked.connect(self.ar_switch_clicked)
        self.ui.assembly_bttn.clicked.connect(self.assembly_switch)
        # self.ui.scene_publish_bttn.setIcon(QtGui.QIcon('%s/icon/publish.png' % self.scriptsPath))
        # self.ui.scene_publish_bttn.clicked.connect(self.__scenePublish)

    def group_component_clicked(self):
        if self.group_component_expanded:
            self.ui.group_component_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.scene_int_frame.setVisible(False)
            self.group_component_expanded = False
        else:
            self.ui.group_component_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.scene_int_frame.setVisible(True)
            self.group_component_expanded = True

    def ar_switch_clicked(self):
        if self.ar_switch_expanded:
            self.ui.ar_switch_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.ar_switch_frame.setVisible(False)
            self.ar_switch_expanded = False
        else:
            self.ui.ar_switch_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.ar_switch_frame.setVisible(True)
            self.ar_switch_expanded = True

    # =================================  设置  =======================================================
    def projectSetting(self):
        """
        通用设置。历史遗留：原来读 self.scriptsPath 下的 config/projectSetting.json，
        但该文件并不存在（jsonHelper 返回 None → 'projects' 触发 TypeError）。
        统一委托给模块级 config.projectSetting()（读 Y:/MCCTools 下的 commonSetting.json，
        与 __init__ 里 self.host = projectSetting()['host'] 属同一数据源）。
        :return: dict | None
        """
        # 注意：此处裸名 projectSetting 解析到模块级 from config import projectSetting，
        # 不会递归调用本方法（类命名空间不参与方法体的名字查找）。
        return projectSetting()

    def rememberSettings(self):
        """ 记忆窗口设置 """
        settings = QtCore.QSettings('Scene', 'SceneSettings')
        settings.setValue('isList', self.isList)
        settings.setValue('thumbSize', self.ui.itemSize_Slider.value())
        settings.setValue('project', self.ui.project_comb.currentIndex())
        settings.setValue('typ', self.ui.type_listWgt.currentRow())

    def readSettings(self):
        """ 读取QSettings数据 """
        settings = QtCore.QSettings('Scene', 'SceneSettings')
        isList = settings.value('isList')
        thumbSize = settings.value('thumbSize')
        project = settings.value('project')
        typ = settings.value('typ')
        if isList is not None:
            if isList == 'true':
                self.isList = True
            else:
                self.isList = False

        return thumbSize, project, typ

    def firstView(self):
        """ 风格外观初设置 """
        self.get_proj()
        thumbSize, project, typ = self.readSettings()
        # print(thumbSize, project, typ)
        if thumbSize is not None:
            self.ui.itemSize_Slider.setValue(thumbSize)

        if project is not None:
            self.ui.project_comb.setCurrentIndex(project)
        else:
            self.ui.project_comb.setCurrentIndex(0)

        self.get_type()

        if typ is not None and typ != -1:
            self.ui.type_listWgt.setCurrentRow(typ)
        else:
            self.ui.type_listWgt.setCurrentRow(0)

    def set_ROOT(self, root):
        """ 设置ROOT """
        self.ROOT = root

    def get_proj(self):
        """ 根据json，设置 projects 显示 """
        # print("update_project")
        self.ui.project_comb.addItems(self.projectSetting()['DataBase'])

    def get_typesList(self):
        project = self.ui.project_comb.currentText()
        pj_path = '{0}/{1}/{2}'.format(self.ROOT, project, 'Scenes')
        directory = QtCore.QDir(pj_path)
        type_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Dirs,
                                        QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        return type_list

    def get_type(self):
        """ 根据选择的project读取type文件夹 """
        # print("update_type")
        self.ui.type_listWgt.clear()
        type_list = self.get_typesList()
        for i in type_list:
            item = QtWidgets.QListWidgetItem()
            item.setText(str(i))
            icon = QtGui.QIcon()
            pix = am_pixmap.Pixmap('%s/icon/folder.svg' % self.scriptsPath)
            if i == 'Map':
                pix.setColor(QtGui.QColor("#beff69"))
            else:
                pix.setColor(QtGui.QColor("#b3b3b3"))
            icon.addPixmap(pix, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon)
            # item.setData(self.type_item_userRole, '{0}/{1}'.format(pj_path, i))
            self.ui.type_listWgt.addItem(item)

    def projectChanged(self):
        """ 切项目 """
        # print("project Changed !")
        self.rememberSettings()
        # self.__showedItemNum = 0
        self.get_type()

    def typeChanged(self):
        """ 切类型 """
        if self.ui.type_listWgt.currentRow() != -1:
            self.rememberSettings()
            self.listWidgetAddItems(self.getItems())
            print("哈哈哈哈")
            self.ui.Favorites_listWgt.setCurrentRow(-1)

    def faveChanged(self):
        """ 切喜好 """
        if self.ui.Favorites_listWgt.currentRow() != -1:
            self.ui.type_listWgt.setCurrentRow(-1)
            self.ui.main_wgt.clear()
            if self.ui.Favorites_listWgt.currentRow() == 0:
                self.ui.main_wgt.clear()
                data = self.ui.Favorites_listWgt.get_favor_items()
                print(data)
                self.listWidgetAddItems(data)
            else:
                self.ui.main_wgt.clear()
                select = self.ui.Favorites_listWgt.selectedItems()[0].text()
                data = self.ui.Favorites_listWgt.get_tag_items(select)
                print(data)
                self.listWidgetAddItems(data)

    def show_menu_type(self, point):
        """
        type_listWgt 右键菜单
        :param point:
        :return:
        """
        currentItem = self.ui.type_listWgt.itemAt(point)
        menu = QtWidgets.QMenu(self.ui.type_listWgt)
        if currentItem is not None:
            return
        else:
            addFolder_action = QtWidgets.QAction(u'新建文件夹', self)
            addFolder_action.setIcon(QtGui.QIcon("{}/icon/folderPlus.png".format(self.scriptsPath)))
            addFolder_action.triggered.connect(self._add_folder)

            menu.addAction(addFolder_action)

            menu.exec_(QtGui.QCursor.pos())
        return

    def _add_folder(self):
        """
        新建type文件夹
        """
        project = self.ui.project_comb.currentText()
        path = '{0}/{1}/Scenes'.format(self.ROOT, project)
        res = self.scenePub.create_new_folder(self, path)
        if res:
            _item = QtWidgets.QListWidgetItem(res)
            _pixmap = am_pixmap.Pixmap('%s/icon/folder.svg' % self.scriptsPath)
            _pixmap.setColor(QtGui.QColor("#b3b3b3"))
            _icon = QtGui.QIcon()
            _icon.addPixmap(_pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            _item.setIcon(_icon)
            self.ui.type_listWgt.addItem(_item)
            self.ui.type_listWgt.setCurrentItem(_item)

    def addFavor(self):
        """
        添加最爱
        :return:
        """
        currentSelected = self.ui.main_wgt.selectedItems()
        if currentSelected:
            if not currentSelected[0].isFavor():
                currentSelected[0].setFavor(True)
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))
            else:
                currentSelected[0].setFavor(False)
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))

    def addTagUI(self):
        """
        添加标签UI
        :return:
        """
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
        tag_list = self.ui.Favorites_listWgt.readTagDict().keys()
        comb.addItems(tag_list)
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 1, 1, 2)
        lay.addWidget(lineEdit, 1, 1, 1, 1)
        lay.addWidget(comb, 2, 1, 1, 1)
        lay.addWidget(bttnBox, 3, 1, 1, 1)

        def _addTag():
            tag = comb.currentText()
            if lineEdit.text() != "":
                tag = lineEdit.text()

            currentSelected = self.ui.main_wgt.selectedItems()
            if currentSelected:
                currentSelected[0].setTag(tag)
                if tag == "":
                    self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
                else:
                    self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/tag.png' % self.scriptsPath))
                    _item = QtWidgets.QListWidgetItem(tag)
                    _icon = QtGui.QIcon(QtGui.QPixmap('%s/icon/tag.png' % self.scriptsPath))
                    _item.setIcon(_icon)
                    self.ui.Favorites_listWgt.addItem(_item)
            Dialog.close()

        bttnBox.accepted.connect(lambda: _addTag())
        bttnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()
        return

    # ========================== 获取当前信息 ==================================================
    def currentProject(self):
        return str(self.ui.project_comb.currentText())

    def currentType(self):
        return str(self.ui.type_listWgt.selectedItems()[0].text())

    def currentAsset(self):
        return self.ui.main_wgt.currentAsset()

    @staticmethod
    def currentDate():
        """ 获取当前时间 """
        return time.strftime('%Y%m%d', time.localtime())

    def getPanelsData(self):
        """获取当前面板信息
        :return: __project, __type, __path
        """
        __project, __type, __path = "", "", ""
        try:
            __project = str(self.ui.project_comb.currentText())
            __type = str(self.ui.type_listWgt.selectedItems()[0].text())
            __path = '%s/%s/%s/%s' % (self.ROOT,
                                      __project,
                                      self.projectSetting()['scenesFolder'],
                                      __type)
        except:
            pass
        return __project, __type, __path

    def loadingText(self, text):
        """ 弃用了，会多加一个item """
        self.ui.main_wgt.clear()
        item = QtWidgets.QListWidgetItem()
        item.setText(text)
        self.ui.main_wgt.addItem(item)
        messageBox.show_msg(self.ui.msg_icon_label, 'info',
                            self.ui.msg_label, text)

    def get_viewThumbnail_bttn(self):
        """ displayThumb_bttn  的初显示状态 """
        if self.isList:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
        else:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")

    def viewModeChanged(self):
        """ 切换  缩略图/表单  显示 """
        keyWords = self.get_keywords()
        itemSize = self.ui.itemSize_Slider.value()
        if self.isList:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")
            # self.listWidgetAddItems()
            self.isList = False
            self.ui.main_wgt.setIsList(self.isList)
            self.ui.main_wgt.setIconMode(itemSize, keyWords)
        else:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
            # self.listWidgetAddItems()
            self.isList = True
            self.ui.main_wgt.setIsList(self.isList)
            self.ui.main_wgt.setListMode(keyWords)
        self.rememberSettings()

    def itemSizeSliderChanged(self):
        """ 根据Slider调整显示大小 """
        itemSize = self.ui.itemSize_Slider.value()
        if self.isList:
            return
        else:
            self.ui.main_wgt.setItemSize(itemSize)
            self.ui.main_wgt.setMode()

    def itemSizeSliderReleased(self):
        itemSize = self.ui.itemSize_Slider.value()
        self.ui.itemSize_Slider.setToolTip(u"%s" % itemSize)
        self.rememberSettings()
        # if self.__showedItemNum < self.ui.main_wgt.count():
        #     self.__update_visible_icon()

    def download_asset(self):
        """
        下载资产到本地
        """
        t_tw = cgtw2.tw()
        type, project, path = self.getTypeAndProject()
        TW_proj = self.projectSetting()['projectdiction'][project]
        t_asset_ids = t_tw.info.get_id(TW_proj, 'scenes',
                                       [['scenes.maya', '=', u"完成"], 'and', ['scenes.scenesassetstype', '=', type]])
        TW_dictionInfo = t_tw.info.get(TW_proj, 'scenes', t_asset_ids,
                                       ['scenes.entity', 'scenes.image', 'scenes.assetsnamecn'])
        for id in TW_dictionInfo:
            ids = [id['id']]
            localPath = "{0}/{1}/Scenes/{2}".format(self.tempPath, project, type)
            self.scenePub.makePath(localPath)
            try:
                downloadInfo = t_tw.info.download_image(TW_proj, 'scenes', ids, 'scenes.image', is_small=False,
                                                        local_dir=localPath)
                rename = downloadInfo[0]['scenes.image'][0].rsplit("/", 1)[0] + "/" + id['scenes.entity'] + ".png"
                if os.path.exists(rename):
                    print(u"%s已经存在！" % rename)
                else:
                    os.rename(downloadInfo[0]['scenes.image'][0], rename)
            except Exception as e:
                print(u"下载%s失败！" % id['scenes.entity'])
        self.listWidgetAddItems_CGT_Fast(self.ui.main_wgt, project, type, keyWords="")

    def refresh_asset(self):
        """ 刷新 """
        # print("refresh_Bttn clicked")
        # self.__showedItemNum = 0
        self.listWidgetAddItems(self.getItems())

    def get_keywords(self):
        """
        :return: [] list of keyword
        """
        keywords = []
        kkk = self.ui.key_line.text()
        for key in kkk.split(","):
            keywords.append(key)
        return keywords

    def search_scene(self):
        """ 搜索 """
        self.listWidgetAddItems()
        # __project, __type, __path = self.getPanelsData()
        # if os.path.exists(str(__path)):
        #     if not self.ui.searchAll_cBox.isChecked():
        #         updateSceneThread = myWidget.MyThread()
        #         updateSceneThread.signal.connect(lambda: self.listWidgetAddItems())
        #         self.infoMsg("info", "Loading...")
        #         updateSceneThread.start()
        #     else:
        #         for i in self.projectSetting()['projects']:
        #             updateSceneThread = myWidget.MyThread()
        #             updateSceneThread.signal.connect(lambda: self.listWidgetAddItems(proj=i))
        #             self.infoMsg("info", "Loading...")
        #             updateSceneThread.start()
        # else:
        #     self.ui.main_wgt.clear()

    # def update_asset(self):
    #     """ 根据type，project，设置主面板item显示 """
    # print("update_scene_asset()")
    # __project, __type, __path = self.getPanelsData()
    # if os.path.exists(str(__path)):
    #     self.updateScenethread = myWidget.MyThread()
    #     self.updateScenethread.signal.connect(lambda: self.listWidgetAddItems(self.getItems()))
    #     self.infoMsg("info", "Loading...")
    #     self.updateScenethread.start()  # 不能在切换tab快速响应，卡到加载完成才会切换tab，未解决
    # else:
    #     self.ui.main_wgt.clear()
    # =====================================  数据展示  =============================================
    def show_asset(self):
        """ 刷新数据，展示资产 """
        self.listWidgetAddItems(self.getItems())

    def getItems(self):
        """
        获取字典
        :return:（'date', 'name', 'zh_name', '', '', '', '', 'icon_path'）
        """
        if self.isSQL:
            aa = self.get_database(self.currentProject(), self.currentType())
            print(aa)
            return aa
        else:
            return self.ui.main_wgt.getItemsDictFromPath(self.ROOT, "Scenes", self.currentProject(), self.currentType())

    def get_database(self, _project, _type):
        """ 得到 scene 数据的SQL """
        conn = None
        cur = None
        get_script = ''' 
                 SELECT "scene.date", "scene.name", "scene.zh_name", "scene.artist", "scene.status", 
                 "scene.artist", "scene.status", "scene.icon", "scene.note"
                 FROM public."scene"
                 WHERE
                 "scene.type" = '%s';
                 ''' % _type
        try:
            conn = psycopg2.connect(database=_project, user=self.user, password=self.password, host=self.host,
                                    port="5432")
            cur = conn.cursor()
            cur.execute(get_script)
            data = cur.fetchall()
            # print(data)
            return data
        except Exception as e:
            print(e)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def listWidgetAddItems(self, update_new_list=None):
        """
        根据type，project，读取CGT资产数据库，设置主面板item显示
        """
        # print("listWidgetAddItems Scene", dict)
        self.ui.main_wgt.clear()
        # self.ui.preview.clear()
        # self.ui.scene_title_label.clear()
        is_list = self.isList

        start_time = time.time()
        if update_new_list is not None:
            self.ui.main_wgt.setItemsList(update_new_list)

        keyWords = self.get_keywords()
        self.ui.main_wgt.setIsList(is_list)
        self.ui.main_wgt.addItems(keyWords[0])

        self.ui.main_wgt.setItemSize(self.ui.itemSize_Slider.value())
        self.ui.main_wgt.resizeItem()
        # if len(self.get_keywords()) == 1:
        #     keyWords = self.get_keywords()[0]
        #     self.ui.main_wgt.addItems(keyWords)
        # else:
        #     for k in self.get_keywords():
        #         self.ui.main_wgt.addItems(k, add=True)

        # self.ui.main_wgt.setMode()
        end_time = time.time()
        self.infoMsg("info", "%s items" % (self.ui.main_wgt.itemCount()) +
                     '   Cost :  %.2f' % (end_time - start_time) + ' sec')

    def update_asset_int(self, modPath, name):
        """ 获取组件内展示 """
        __project, __type, __path = self.getPanelsData()
        self.ui.scene_int_listWgt.clear()
        directory = QtCore.QDir(modPath)
        itemGRP = QtWidgets.QListWidgetItem()
        itemGRP_data = {'role_name': name, 'project': __project, 'type': __type}
        itemGRP.setText(name)
        iconGRP = QtGui.QIcon()
        iconGRP.addPixmap(QtGui.QPixmap('%s/icon/folder_open.png' % self.scriptsPath), QtGui.QIcon.Normal,
                          QtGui.QIcon.Off)
        itemGRP.setIcon(iconGRP)
        itemGRP.setData(self.asset_item_userRole, itemGRP_data)
        self.ui.scene_int_listWgt.addItem(itemGRP)
        int_list = directory.entryList(['*.ma'], QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries,
                                       QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        for i in int_list:
            if "_GRP_" not in i:
                part_name = i.split("_mod")[0]
                item = QtWidgets.QListWidgetItem()
                item_data = {'role_name': part_name, 'project': __project, 'type': __type}
                item.setText(part_name)
                item.setIcon(QtGui.QIcon(QtGui.QPixmap('%s/icon/maya_open.png' % self.scriptsPath)))
                item.setData(self.asset_item_userRole, item_data)
                self.ui.scene_int_listWgt.addItem(item)
        self.ui.scene_int_listWgt.setCurrentItem(itemGRP)

    def mainWidgetItemChanged(self):
        """
        改变item触发：改变属性显示, 改变预览显示, 改变标题显示，改变scene_int_listWgt显示
        """
        currentSelected = self.ui.main_wgt.selectedItems()
        self.ui.preview.clear()
        # self.ui.scene_title_label.clear()
        if currentSelected:
            item_data = currentSelected[0].itemData()
            # print(item_data)
            modPath = '{}/Mod'.format(item_data[7].split("/Icon/")[0])

            '''######## 根据item_data设置预览窗口显示 ###################################################'''
            if currentSelected[0].text().endswith("_GRP"):
                self.ui.preview.setPreviewPixmap(item_data[7], "scenes")
            else:
                self.ui.preview.setPreviewPixmap(item_data[7], "scene")
            self.ui.preview.setTitle(item_data[1], item_data[2])
            # self.ui.scene_title_label.setText(
            #     u"Name：  " + item_data[1] + u"\n中文名： " + item_data[2])

            self.update_asset_int(modPath, item_data[1])

            '''########## 设置喜好和标签 #################################################################'''
            if not currentSelected[0].isFavor():
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
            else:
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))

            if not currentSelected[0].isTag():
                self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
            else:
                self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/tag.png' % self.scriptsPath))

    # def __update_visible_icon(self):
    #     self.__updatedNum = 0
    #     if self.isList:
    #         pass
    #     else:
    #         starttime = time.time()
    #         point_num = self.countItemsNum()
    #         if point_num <= self.ui.main_wgt.count():
    #             num = point_num
    #         else:
    #             num = self.ui.main_wgt.count()
    #         updatedItemNum, showedItemNum = list_items._update_visibleIcons(self.ui.main_wgt,
    #                                                                         self.__showedItemNum, num)
    #         self.__showedItemNum = showedItemNum
    #         self.__updatedNum = updatedItemNum
    #         self._viewThumb()  # 不整理一下会大小乱掉
    #         endtime = time.time()
    #         self.infoMsg("info", "%s/%s items" % (self.__updatedNum, self.ui.main_wgt.count()) +
    #                      '   Cost :  %.2f' % (endtime - starttime) + ' sec')

    # def countItemsNum(self):
    #     itemSize = self.ui.itemSize_Slider.value()
    #     width = self.ui.main_wgt.width()
    #     scrollBarY = self.ui.main_wgt.verticalScrollBar().value()
    #     height = self.ui.main_wgt.height() + scrollBarY
    #     column = width // (itemSize + self.DEF_SPACING)
    #     row = height / (itemSize + self.DEF_SPACING + 40) + 1
    #     return column * row

    # def mainWightSizeChanged(self):
    #     # print("mainWightSizeChanged !")
    #     if self.__showedItemNum < self.ui.main_wgt.count() and self.__showedItemNum != 0:
    #         self.__update_visible_icon()
    #
    # def mainWightWheeled(self):
    #     # print("mainWightWheel !")
    #     if self.__showedItemNum < self.ui.main_wgt.count():
    #         self.__update_visible_icon()
    #
    # def mainScrollBarValueChanged(self):
    #     if self.__showedItemNum < self.ui.main_wgt.count():
    #         self.__update_visible_icon()

    def eventFilter(self, receiver, event):
        if event.type() == QtCore.QEvent.Enter:
            self.drag_drop_happened()
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.remove_maya_eventfilter()
            return True
        return False

    def mainWgtItemDragLeaved(self):
        self.install_maya_eventfilter()

    def install_maya_eventfilter(self):
        self.mayaMainWindow.installEventFilter(self)

    def remove_maya_eventfilter(self):
        self.mayaMainWindow.removeEventFilter(self)

    def drag_drop_happened(self):
        """拖入触发"""
        # print("drag_drop_happened")
        menu = QtWidgets.QMenu(self.mayaMainWindow)
        action_a = QtWidgets.QAction(u"Import...", menu)
        action_a.triggered.connect(self.import_mod)
        action_b = QtWidgets.QAction(u"Create Reference...", menu)
        action_b.triggered.connect(self.create_AR_ref)
        menu.addAction(action_a)
        menu.addAction(action_b)
        menu.popup(QtGui.QCursor.pos())
        self.remove_maya_eventfilter()

    def detailPath(self):
        __project, __type, __path = self.getPanelsData()
        item_data = self.ui.main_wgt.selectedItems()[0].itemData()
        item_part_data = self.ui.scene_int_listWgt.currentItem().data(self.asset_item_userRole)
        # print(item_data, item_part_data)
        if __type != "Map":
            detailPaths = {
                'Assembly': '{0}/Assembly/{1}_AD.ma'.format(item_data[7].split('/Icon/')[0],
                                                            item_part_data['role_name']),
                'Icon': item_data[7],
                'GPU': '{0}/GPU/{1}_GPU.abc'.format(item_data[7].split('/Icon/')[0],
                                                    item_part_data['role_name']),
                'Mod': '{0}/Mod/{1}_mod.ma'.format(item_data[7].split('/Icon/')[0],
                                                   item_part_data['role_name'])}
        else:
            detailPaths = {
                'Assembly': '{0}/Assembly/{1}_AD.ma'.format(item_data[7].split('/Icon/')[0],
                                                            item_data[1]),
                'Icon': item_data[7],
                'GPU': '{0}/GPU/{1}_GPU.abc'.format(item_data[7].split('/Icon/')[0],
                                                    item_data[1]),
                'Mod': '{0}/MapFile/{1}_map.ma'.format(item_data[7].split('/Icon/')[0],
                                                       item_data[1])}
        return detailPaths

    def show_menu(self, point):
        """右键菜单"""
        __project, __type, __path = self.getPanelsData()
        currentItem = self.ui.main_wgt.itemAt(point)
        menu = QtWidgets.QMenu(self.ui.main_wgt)
        if currentItem is not None:
            mod_action = QtWidgets.QAction('Show in Explorer', self)
            mod_action.setIcon(QtGui.QIcon("{}/icon/folder_white.png".format(self.scriptsPath)))
            importMod = QtWidgets.QAction('Import...', self)
            RefMod = QtWidgets.QAction('Create Reference...', self)
            RepMod = QtWidgets.QAction('Replace Selected Reference', self)
            del_action = QtWidgets.QAction(u'删除...', self)

            menu.addAction(mod_action)
            menu.addSeparator()
            menu.addAction(importMod)
            if __type != "Map" and "_GRP" not in currentItem.text():
                menu.addAction(RefMod)
                menu.addAction(RepMod)
            menu.addAction(del_action)

            mod_action.triggered.connect(partial(self.openDir, 'Mod', currentItem))
            importMod.triggered.connect(self.import_mod)
            RefMod.triggered.connect(self.create_AR_ref)
            RepMod.triggered.connect(self.replace_AR_ref)
            del_action.triggered.connect(self.delete_scene)
            menu.exec_(QtGui.QCursor.pos())
        else:
            scenePublish_action = QtWidgets.QAction(u'发布场景静态资产到这里', self)
            scenePublish_action.setIcon(QtGui.QIcon("{}/icon/publish.png".format(self.scriptsPath)))
            scenePublish_action.triggered.connect(self.__scenePublish)
            refresh_action = QtWidgets.QAction(u'刷新', self)
            refresh_action.setIcon(QtGui.QIcon("{}/icon/refresh.png".format(self.scriptsPath)))
            refresh_action.triggered.connect(self.refresh_asset)

            menu.addAction(scenePublish_action)
            menu.addSeparator()
            menu.addAction(refresh_action)
            menu.exec_(QtGui.QCursor.pos())
        return

    def show_menu_Preview(self, point):
        """Preview_label 右键菜单"""
        __project, __type, __path = self.getPanelsData()
        currentItem = self.ui.main_wgt.selectedItems()[0]
        menu = QtWidgets.QMenu(self.ui.main_wgt)
        if currentItem is not None:
            mod_action = QtWidgets.QAction('Show in Explorer', self)
            mod_action.setIcon(QtGui.QIcon("{}/icon/folder_white.png".format(self.scriptsPath)))
            importMod = QtWidgets.QAction('Import', self)
            RefMod = QtWidgets.QAction('Create Reference', self)
            RepMod = QtWidgets.QAction('Replace Selected Reference', self)
            menu.addAction(mod_action)
            menu.addAction(importMod)
            if __type != "Map" and "_GRP" not in currentItem.text():
                menu.addAction(RefMod)
                menu.addAction(RepMod)
            mod_action.triggered.connect(partial(self.openDir, 'Mod', currentItem))
            importMod.triggered.connect(self.import_mod)
            RefMod.triggered.connect(self.create_AR_ref)
            RepMod.triggered.connect(self.replace_AR_ref)
            menu.exec_(QtGui.QCursor.pos())

    def show_menu_int(self, point):
        """int右键菜单"""
        __project, __type, __path = self.getPanelsData()
        currentItem = self.ui.scene_int_listWgt.itemAt(point)
        if currentItem is not None:
            pop = QtWidgets.QMenu(self.ui.main_wgt)
            importMod = QtWidgets.QAction('Import', self)
            RefMod = QtWidgets.QAction('Create Reference', self)
            RepMod = QtWidgets.QAction('Replace Selected Reference', self)
            pop.addAction(importMod)
            if __type != "Map" and "_GRP" not in currentItem.text():
                pop.addAction(RefMod)
                pop.addAction(RepMod)
            importMod.triggered.connect(self.import_mod)
            RefMod.triggered.connect(self.create_AR_ref)
            RepMod.triggered.connect(self.replace_AR_ref)
            pop.exec_(QtGui.QCursor.pos())
        return

    def openDir(self, type, item):
        """右键打开文件夹"""
        mod_file_path = self.detailPath()['Mod'].split("Mod")[0]
        folder_path = os.path.dirname(mod_file_path)
        folder_info = QtCore.QFileInfo(folder_path)
        if folder_info.exists():
            QtGui.QDesktopServices.openUrl(folder_path)
        else:
            cmds.warning('Can not find {0}'.format(folder_path))

    def create_AD_ref(self):
        """
        创建AD
        :return:
        """
        selected_items = self.ui.main_wgt.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            current_type = self.ui.type_listWgt.currentItem().text()
            if current_type == 'Map':
                asset_name = 'Terrain'
                ad_file_path = self.detailPath()['Assembly']
                interim_file_path = ad_file_path.replace('/Assembly/', '/Interim/')
                interim_file_path = interim_file_path.replace('_AD.ma', '_interim.ma')
                cmds.file(interim_file_path, i=True, type='mayaAscii', mergeNamespacesOnClash=False, ignoreVersion=True,
                          options='v=0', preserveReferences=True)
            else:
                asset_name = item.text()
                # print (asset_name)
                AD_name = cmds.assembly(name='{0}_AD'.format(asset_name), type='assemblyDefinition')
                # port_file_path = item.data(self.asset_item_userRole)['Port']
                port_file_path = item.data(self.asset_item_userRole)
                # print (port_file_path)
                mod_file_path = self.detailPath()['Mod']
                gpu_file_path = self.detailPath()['GPU']
                if QtCore.QFileInfo(gpu_file_path).exists() and QtCore.QFileInfo(
                        port_file_path).exists() and QtCore.QFileInfo(mod_file_path).exists():
                    cmds.assembly(AD_name, edit=True, createRepresentation='Cache',
                                  repName='{0}_GPU.abc'.format(asset_name), input=gpu_file_path)
                    cmds.assembly(AD_name, edit=True, createRepresentation='Scene',
                                  repName='{0}_port.ma'.format(asset_name), input=port_file_path)
                    cmds.assembly(AD_name, edit=True, createRepresentation='Scene',
                                  repName='{0}_mod.ma'.format(asset_name), input=mod_file_path)
                    cmds.assembly(AD_name, edit=True, activeLabel='{0}_GPU.abc'.format(asset_name))
                    cmds.select(AD_name)
                else:
                    cmds.warning('Can not find mod/port/GPU')

    def create_AR_ref(self):
        """
        创建AR
        :return:
        """
        selected_items = self.ui.scene_int_listWgt.selectedItems()
        if not selected_items:
            return
        if self.scenePub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
            return
        for item in selected_items:
            item_data = item.data(self.asset_item_userRole)
            assembly_info = QtCore.QFileInfo(self.detailPath()['Assembly'])
            if assembly_info.exists():
                assembly_name = cmds.assembly(name=item_data['role_name'], type='assemblyReference')
                cmds.setAttr('{0}.definition'.format(assembly_name), self.detailPath()['Assembly'], type='string')
            else:
                QtWidgets.QMessageBox.warning(self, '警告', '未发现 AD 文件')
                return

    def replace_AR_ref(self):
        """
        替换AR
        :return:
        """
        selected_items = self.ui.scene_int_listWgt.selectedItems()
        if not selected_items:
            return
        selected_AD = cmds.ls(sl=1, type='assemblyReference')
        if not selected_AD:
            cmds.warning(u'请在场景中至少选择一个AR物体')
        else:
            for slt in selected_AD:
                # print(slt, selected_items[0].text())
                cmds.setAttr('{0}.definition'.format(slt), self.detailPath()['Assembly'], type='string')
                mel.eval('AEassemblyChangeAttrNamespace "{0}.repNamespace""{1}";'.format(slt, selected_items[0].text()))
                cmds.rename(slt, selected_items[0].text())

    def import_mod(self):
        """ 打开mod """
        if self.ui.main_wgt.currentItem() is None:
            return
        else:
            mod_info = QtCore.QFileInfo(self.detailPath()['Mod'])
            if mod_info.exists():
                cmds.file(self.detailPath()['Mod'], i=True, type='mayaAscii', mergeNamespacesOnClash=False,
                          ignoreVersion=True, options='v=0', preserveReferences=True)
            else:
                QtWidgets.QMessageBox.warning(self, '警告', '未发现 Mod 文件')
                return
            return

    # =================================  数据库操作 ===============================================
    def add_asset_ui(self):
        """ 创建资产 """
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(300, 195)
        Dialog.setWindowTitle(u"Add Scene")
        font = QtGui.QFont(u"Microsoft YaHei UI", 10)
        Dialog.setFont(font)

        label = QtWidgets.QLabel(Dialog)
        label.setText(u"创建一个新资产：")

        proj_comb = QtWidgets.QComboBox(Dialog)
        proj_comb.addItems(projectSetting()["projects"])
        type_comb = QtWidgets.QComboBox(Dialog)
        type_comb.addItems(self.get_typesList())
        try:
            type_comb.setCurrentText(self.currentType())
        except:
            pass
        name_line = QtWidgets.QLineEdit(Dialog)
        name_line.setPlaceholderText("scene name")
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
            mod_artist = self.user
            _type = type_comb.currentText()
            self.add_scene(db, date, name, zh_name, mod_artist, _type)
            self.show_asset()
            self.make_dirs(db, _type, name)
            Dialog.close()

        btnBox.accepted.connect(lambda: _add_asset())
        btnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()
        return

    def add_scene(self, db, date, name, zh_name, artist, _type):
        """ 新增场景 """
        icon = "Y:/MCCProject/{0}/Scenes/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.scene ("scene.date", "scene.name", "scene.zh_name", "scene.artist", "scene.status", 
            "scene.icon", "scene.type") 
            VALUES 
            ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text, '未开始'::text, '%s'::text, '%s'::text)
            returning scene."scene.name";
        ''' % (date, name, zh_name, artist, icon, _type)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告", str(e))
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    @staticmethod
    def make_dirs(db, _type, name):
        """ 创建路径 """
        path = "Y:/MCCProject/{0}/Scenes/{1}/{2}".format(db, _type, name)
        if not os.path.exists(path):
            os.makedirs(path)
        sub_folder = ["/Assembly", "/FBX", "/GPU", "/Icon", "/Mod", "/Mod", "/Original", "/Port", "/Proxy",
                      "/Texture"]
        for sub in sub_folder:
            sub_path = path + sub
            if not os.path.exists(sub_path):
                os.makedirs(sub_path)
        return True

    def delete_scene(self):
        """ 删除场景 """
        result = QtWidgets.QMessageBox.warning(self, u"警告",
                                               u"删除数据表的操作是不可逆的，但服务器文件夹还在，确定要删除吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.del_scene(self.currentProject(), self.currentAsset())
            self.show_asset()

    def del_scene(self, db, scene_name):
        """ 删除场景 """
        delete_script = '''
            DELETE FROM public.scene
            WHERE
            "scene.name" = '%s';''' % scene_name
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(delete_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告：", str(e))
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def assembly_switch(self):
        # print("idlfkodmo")
        assembly_all = self.ui.assembly_all_rBttn.isChecked()
        assembly_type = self.ui.assembly_type_comb.currentText()
        if assembly_all:
            assembly_ref_list = cmds.ls(type='assemblyReference')
        else:
            assembly_ref_list = cmds.ls(selection=True, type='assemblyReference')
        for i in assembly_ref_list:
            assembly_path = cmds.getAttr('{}.definition'.format(i))
            if assembly_type == u'实体模型':
                tx = cmds.getAttr('{}.translateX'.format(i))
                ty = cmds.getAttr('{}.translateY'.format(i))
                tz = cmds.getAttr('{}.translateZ'.format(i))
                rx = cmds.getAttr('{}.rotateX'.format(i))
                ry = cmds.getAttr('{}.rotateY'.format(i))
                rz = cmds.getAttr('{}.rotateZ'.format(i))
                sx = cmds.getAttr('{}.scaleX'.format(i))
                sy = cmds.getAttr('{}.scaleY'.format(i))
                sz = cmds.getAttr('{}.scaleZ'.format(i))
                cmds.setAttr('{}.visibility'.format(i), 0)
                mod_path = assembly_path.replace("Assembly", "Mod").replace("_AD.ma", "_mod.ma")
                mod_name = assembly_path.rsplit("/", 1)[1].rsplit("_", 1)[0]
                file = cmds.file(mod_path, reference=True, type='mayaAscii', ignoreVersion=True,
                                 namespace='{0}_mod'.format(i))
                node = cmds.referenceQuery(file, namespace=True) + ":" + mod_name
                cmds.setAttr('{}.translateX'.format(node), tx)
                cmds.setAttr('{}.translateY'.format(node), ty)
                cmds.setAttr('{}.translateZ'.format(node), tz)
                cmds.setAttr('{}.rotateX'.format(node), rx)
                cmds.setAttr('{}.rotateY'.format(node), ry)
                cmds.setAttr('{}.rotateZ'.format(node), rz)
                cmds.setAttr('{}.scaleX'.format(node), sx)
                cmds.setAttr('{}.scaleY'.format(node), sy)
                cmds.setAttr('{}.scaleZ'.format(node), sz)
            listRepresentations = cmds.assembly(i, query=True, listRepresentations=True)
            for rep in listRepresentations:
                # if assembly_type == 'GPU' and rep.find('.abc') != -1:
                #     cmds.assembly(i, edit=True, activeLabel=rep)
                if assembly_type == 'Port' and rep.find('_port.ma') != -1:
                    cmds.assembly(i, edit=True, activeLabel=rep)
                elif assembly_type == 'Mod' and rep.find('_mod.ma') != -1:
                    cmds.assembly(i, edit=True, activeLabel=rep)

    def __scenePublish(self):
        __project, __type, __path = self.getPanelsData()
        from tools_publish.PublishTools import PublishTool
        PublishTool.showWindow(2, __project, __type)

    def infoMsg(self, icon, text):
        """
        消息栏
        :param icon: "warning", "info", "error"
        :param text: str
        """
        messageBox.show_msg(self.ui.msg_icon_label, icon,
                            self.ui.msg_label, text)
