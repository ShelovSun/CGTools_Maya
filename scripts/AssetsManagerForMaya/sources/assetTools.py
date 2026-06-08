#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sceneTools_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import os
import shutil
import sys
import time

import psycopg2
from functools import partial
from config import projectSetting, SMConfig

import maya.OpenMayaUI as omui
import maya.cmds as cmds
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
from utils import jsonHelper, publish, messageBox, sequenceplayer, copy_thread
from widgets import am_main, faverWidget, previewWidget, am_pixmap, am_listItem


def maya_main_window():
    """接收拖入"""
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


class GetDataThread(QtCore.QThread):
    data_signals = QtCore.Signal(list)
    error_signals = QtCore.Signal(str)
    finish_signals = QtCore.Signal()

    def __init__(self, db, as_type, user, password, keywords, condition):
        super().__init__()
        self.db = db
        self.host = SMConfig().getPrefsValue("General/ip", "10.0.203.34")
        self.user = user
        self.password = password
        self._type = as_type
        self.keywords = keywords
        self.condition = condition
        print(self.db,
              self.host,
              self.user,
              self.password,
              self._type,
              self.keywords,
              self.condition)

    def run(self):
        """ 得到asset数据 """
        conn = None
        cur = None
        # get_script = '''
        #      SELECT "asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", "asset.mod_status",
        #      "asset.rig_artist", "asset.rig_status", "asset.icon", "asset.note"
        #      FROM public."asset"
        #      WHERE
        #      "asset.type" = '%s';
        #      ''' % self._type
        get_script = ''' 
             SELECT "asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", "asset.mod_status", 
             "asset.rig_artist", "asset.rig_status", "asset.icon", "asset.note"
             FROM public."asset"
             WHERE TRUE
             '''
        get_script = get_script + self.condition_script()
        try:
            conn = psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host,
                                    port="5432")
            cur = conn.cursor()
            cur.execute(get_script)
            while True:
                data = cur.fetchone()
                print(data)
                # image = QtGui.QImage(data[7])
                if data is None:
                    break
                self.data_signals.emit(data)
            self.finish_signals.emit()
        except Exception as e:
            self.error_signals.emit(e)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def condition_script(self):
        condition_script = ""
        condition = self.condition
        # print("搜索条件:", condition)
        ass_type = self._type
        keywords = self.keywords
        print("关键词:", keywords)
        if keywords:
            add_script = ""
            for k in keywords:
                add_script += '''OR ("asset.name" ILIKE '%{0}%'  escape '/' OR "asset.zh_name" ILIKE '%{0}%'  escape '/')'''.format(
                    k)
            condition_script += '''AND ({0})'''.format(add_script.replace("OR ", "", 1))
        if ass_type:
            condition_script += '''AND ("asset.type" = '%s')''' % ass_type
        return condition_script


class AssetToolsUI(QtWidgets.QWidget):
    MYPREFSDIR = cmds.internalVar(userPrefDir=True)  # Result: u'C:/Users/asus/Documents/maya/2019/prefs/'
    MAYADir = os.environ.get('MAYA_APP_DIR')  # Result: 'C:/Users/asus/Documents/maya'
    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')

    def __init__(self, user="", password=""):
        super(AssetToolsUI, self).__init__()
        self.mayaMainWindow = maya_main_window()
        self.mayaMainWindow.setAcceptDrops(True)

        self.host = SMConfig().getPrefsValue("General/ip", "10.0.203.34")
        self.user = user
        self.password = password

        f = QtCore.QFile('%s/ui/assetTools.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()

        self.Pub = publish.Publish()
        self.tab = "Assets"  # 路径下有s
        self.isList = False
        self.isAction = False
        self.isAttributeShow = True
        self.__items_dict = {}
        self.currentAssetData = {}
        self.ROOT = "Y:/MCCProject"
        # self.show_asset_list = []
        # self.__showedItemNum = 0
        # self.__updatedNum = 0
        self.progress = 0
        self.file_type_expanded = True
        self.switch_expanded = True
        self.step = 10
        self.__fileTypeFolderDict = {'mod': 'Mod',
                                     'render': 'Render',
                                     'all_rig': 'Rig',
                                     'hi_rig': 'Rig',
                                     'low_rig': 'Rig',
                                     'xgen': 'Xgen',
                                     'AD': 'Assembly',
                                     'OAT': 'Rig'}
        self.init_ui()
        self.show_asset()

    def init_ui(self):
        # print("init_ui")
        self.firstView()

        '''左侧边栏'''
        self.ui.project_comb.currentIndexChanged.connect(self.projectChanged)
        self.ui.type_listWgt.itemSelectionChanged.connect(self.typeChanged)
        self.ui.type_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.type_listWgt.customContextMenuRequested.connect(self.show_menu_type)

        self.ui.Favorites_listWgt = faverWidget.FavoritesQListWiget(tab="Asset")
        self.ui.type_splitter.addWidget(self.ui.Favorites_listWgt)
        self.ui.type_splitter.setSizes([300, 500])
        self.ui.Favorites_listWgt.itemSelectionChanged.connect(self.faveChanged)

        '''上侧小按钮栏'''
        self.ui.back_bttn.setIcon(QtGui.QIcon('%s/icon/back.png' % self.scriptsPath))
        self.ui.back_bttn.clicked.connect(self.backToMainWgt)
        self.ui.add_bttn.setIcon(QtGui.QIcon('%s/icon/add.png' % self.scriptsPath))
        self.ui.add_bttn.clicked.connect(self.add_asset_ui)
        self.get_viewThumbnail_btn()
        self.ui.displayThumb_bttn.clicked.connect(self.viewModeChanged)
        self.ui.itemSize_Slider.valueChanged.connect(self.itemSizeSliderChanged)
        self.ui.itemSize_Slider.setToolTip(str(self.ui.itemSize_Slider.value()))
        self.ui.itemSize_Slider.sliderReleased.connect(self.itemSizeSliderReleased)
        self.ui.download_Bttn.setIcon(QtGui.QPixmap('%s/icon/download.png' % self.scriptsPath))
        self.ui.download_Bttn.clicked.connect(self.download_asset)
        self.ui.refresh_Bttn.setIcon(QtGui.QPixmap('%s/icon/refresh.png' % self.scriptsPath))
        self.ui.refresh_Bttn.clicked.connect(self.refresh_asset)
        self.ui.key_line.returnPressed.connect(self.search_asset)
        self.ui.key_line.addAction(QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
                                   QtWidgets.QLineEdit.LeadingPosition)

        '''主界面栏'''
        self.ui_main_wgt = am_main.MainStackedWidget(tab="Asset", db=self.ui.project_comb.currentText(),
                                                     user=self.user, password=self.password,
                                                     islist=self.isList)
        self.ui_main_wgt.setItemsWidget(self)
        self.ui_main_wgt.dragLeaveSignal_connect(self.mainWgtItemDragLeaved)
        self.ui_main_wgt.itemSelectionChanged_connect(self.mainWightItemChanged)
        self.ui_main_wgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui_main_wgt.customContextMenuRequested.connect(self.show_menu)
        self.ui.verticalLayout_3.addWidget(self.ui_main_wgt)

        self.ui.mainWindow_splitter.setSizes([120, 500, 300])
        self.ui.mainWindow_splitter.setStretchFactor(0, False)
        self.ui.mainWindow_splitter.setStretchFactor(1, True)
        self.ui.mainWindow_splitter.setStretchFactor(2, False)

        '''右侧属性栏'''
        # self.ui.attr_splitter.setSizes([750, 500])
        self.ui.attr_splitter.setStretchFactor(1, False)
        self.ui.upload_Bttn.setIcon(QtGui.QIcon('%s/icon/cloud_upload.png' % self.scriptsPath))
        self.ui.upload_Bttn.clicked.connect(self.addTagUI)
        self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
        self.ui.favor_bttn.clicked.connect(self.addFavor)
        self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
        self.ui.tag_bttn.clicked.connect(self.addTagUI)
        self.ui.preview = previewWidget.PreviewWidget()
        self.ui.preview_vLayout.addWidget(self.ui.preview)
        self.ui.preview.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.preview.customContextMenuRequested.connect(self.show_menu_Preview_label)
        self.ui.preview.playerEnabled(True)

        self.ui.file_type_tbttn.clicked.connect(self.file_type_clicked)
        self.ui.exportFbx_bttn.clicked.connect(self.exportFbx)

        self.ui.switch_tbttn.clicked.connect(self.switch_clicked)
        self.ui.asset_ref_switch_bttn.clicked.connect(self.copyKey)

    def file_type_clicked(self):
        if self.file_type_expanded:
            self.ui.file_type_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.file_type_frame.setVisible(False)
            self.file_type_expanded = False
        else:
            self.ui.file_type_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.file_type_frame.setVisible(True)
            self.file_type_expanded = True

    def switch_clicked(self):
        if self.switch_expanded:
            self.ui.switch_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.switch_frame.setVisible(False)
            self.switch_expanded = False
        else:
            self.ui.switch_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.switch_frame.setVisible(True)
            self.switch_expanded = True

    def rememberSettings(self):
        """ 写入QSettings数据 """
        settings = QtCore.QSettings('Assets', 'AssetsSettings')
        settings.setValue('isList', self.isList)
        settings.setValue('thumbSize', self.ui.itemSize_Slider.value())
        settings.setValue('project', self.ui.project_comb.currentIndex())
        settings.setValue('typ', self.ui.type_listWgt.currentRow())

    def readSettings(self):
        """ 读取QSettings数据 """
        settings = QtCore.QSettings('Assets', 'AssetsSettings')
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
        """ 初显示 """
        self.get_project()
        self.get_type()

        thumbSize, project, typ = self.readSettings()
        # print(thumbSize, project, typ, self.isList)
        if thumbSize is not None:
            self.ui.itemSize_Slider.setValue(thumbSize)
        if project is not None:
            self.ui.project_comb.setCurrentIndex(project)
        else:
            self.ui.project_comb.setCurrentIndex(0)
        if typ is not None and typ != -1:
            self.ui.type_listWgt.setCurrentRow(typ)
        else:
            self.ui.type_listWgt.setCurrentRow(0)

    def set_ROOT(self, root):
        """ 设置ROOT """
        self.ROOT = root

    def get_project(self):
        """ 根据json设置 projects 显示 """
        self.ui.project_comb.addItems(projectSetting()['projects'])

    def get_type(self):
        """ 根据json设置type显示 """
        self.ui.type_listWgt.clear()
        for i in projectSetting()['type']:
            item = QtWidgets.QListWidgetItem()
            item.setText(str(i))
            icon = QtGui.QIcon()
            pixmap = am_pixmap.Pixmap('%s/icon/folder.svg' % self.scriptsPath)
            pixmap.setColor(QtGui.QColor("#b3b3b3"))
            icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon)
            self.ui.type_listWgt.addItem(item)
        # return projectSetting()['type']

    # ========================== 获取当前信息 ==================================================
    def currentProject(self):
        """ 当前项目 """
        return str(self.ui.project_comb.currentText())

    def currentType(self):
        """ 当前类型 """
        return str(self.ui.type_listWgt.selectedItems()[0].text())

    @staticmethod
    def currentDate():
        """ 获取当前时间 """
        return time.strftime('%Y%m%d', time.localtime())

    def currentAsset(self):
        return self.ui_main_wgt.currentAsset()

    def projectChanged(self):
        """ 切项目 """
        # print("project Changed !")
        self.rememberSettings()
        self.listWidgetAddItems(self.getItemsList())
        return str(self.ui.project_comb.currentText())

    def typeChanged(self):
        """ 切类型 """
        # print("type Changed !", self.ui.type_listWgt.currentRow())
        if self.ui.type_listWgt.currentRow() != -1:
            self.rememberSettings()
            self.show_asset()
            # self.listWidgetAddItems(self.getItemsList())
            self.ui.Favorites_listWgt.setCurrentRow(-1)
            return str(self.ui.type_listWgt.selectedItems()[0].text())

    def faveChanged(self):
        """ 切喜好 """
        if self.ui.Favorites_listWgt.currentRow() != -1:
            self.ui.type_listWgt.setCurrentRow(-1)
            if self.ui.Favorites_listWgt.currentRow() == 0:
                self.ui_main_wgt.clear()
                data = self.ui.Favorites_listWgt.get_favor_items()
                self.listWidgetAddItems(data)
            else:
                self.ui_main_wgt.clear()
                select = self.ui.Favorites_listWgt.selectedItems()[0].text()
                data = self.ui.Favorites_listWgt.get_tag_items(select)
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
            addFolder_action.setIcon(QtGui.QIcon("%s/icon/folderPlus.png" % self.scriptsPath))
            addFolder_action.triggered.connect(self._add_folder)

            menu.addAction(addFolder_action)

            menu.exec_(QtGui.QCursor.pos())
        return

    def _add_folder(self):
        """
        新建type文件夹
        """
        project = self.ui.proj_comb.currentText()
        path = '{0}/{1}/Scenes'.format(self.ROOT, project)
        res = self.Pub.create_new_folder(self, path)
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
        currentSelected = self.ui_main_wgt.selectedItems()
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

            currentSelected = self.ui_main_wgt.selectedItems()
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

    def backToMainWgt(self):
        """
        返回主面板
        """
        self.ui.preview.clear()
        self.ui.preview.playerEnabled(False)
        self.isAction = False
        self.refresh_asset()
        self.ui.back_bttn.setEnabled(False)
        self.ui.itemSize_Slider.setEnabled(True)

    # ================================== 数据操作 ==============================================
    def add_asset_ui(self):
        """ 创建任务 """
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(300, 195)
        Dialog.setWindowTitle(u"Add Asset")
        font = QtGui.QFont(u"Microsoft YaHei UI", 10)
        Dialog.setFont(font)

        label = QtWidgets.QLabel(Dialog)
        label.setText(u"创建一个新资产：")

        proj_comb = QtWidgets.QComboBox(Dialog)
        proj_comb.addItems(projectSetting()["projects"])
        type_comb = QtWidgets.QComboBox(Dialog)
        type_comb.addItems(projectSetting()['type'])
        name_line = QtWidgets.QLineEdit(Dialog)
        name_line.setPlaceholderText("asset name")
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
            mod_artist = str(self.user)
            asset_type = type_comb.currentText()
            self.add_asset(db, date, name, zh_name, mod_artist, asset_type)
            self.make_dirs(db, asset_type, name)
            Dialog.close()

        btnBox.accepted.connect(lambda: _add_asset())
        btnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()
        return

    def add_asset(self, db, date, name, zh_name, mod_artist, _type):
        """ 新增资产 """
        icon = "Y:/MCCProject/{0}/Assets/{1}/{2}/Icon/{2}.png".format(db, _type, name)
        insert_script = '''
            INSERT INTO public.asset ("asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", 
            "asset.mod_status", "asset.icon", "asset.type") 
            VALUES 
            ('%s'::bigint, '%s'::text, '%s'::text, '%s'::text, '未开始'::text, 
            '%s'::text, '%s'::text)
            returning asset."asset.name";
        ''' % (date, name, zh_name, mod_artist, icon, _type)
        print(insert_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
            cur = conn.cursor()
            cur.execute(insert_script)
            conn.commit()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, u"警告：", str(e))
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def delete_asset(self):
        """ 删除镜头 """
        result = QtWidgets.QMessageBox.warning(self, u"警告",
                                               u"删除数据表的操作是不可逆的，但服务器文件夹还在，确定要删除吗？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.Yes:
            self.del_asset(self.currentProject(), self.currentAsset())
            self.show_asset()

    def del_asset(self, db, asset_name):
        """ 删除资产 """
        delete_script = '''
            DELETE FROM public.asset
            WHERE
            "asset.name" = '%s';''' % asset_name
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

    @staticmethod
    def make_dirs(db, asset_type, asset_name):
        """ 创建路径 """
        path = "Y:/MCCProject/{0}/Assets/{1}/{2}".format(db, asset_type, asset_name)
        if not os.path.exists(path):
            os.makedirs(path)

        int_folder_dict = ["/Action", "/Design", "/FBX", "/Icon", "/Image", "/Mod", "/Original", "/Rig", "/Texture"]

        task_path = []
        for task_folder in int_folder_dict:
            _path = path + task_folder
            task_path.append(_path)

        for p in task_path:
            if not os.path.exists(p):
                os.makedirs(p)

    def get_viewThumbnail_btn(self):
        """
        displayThumb_bttn  的初显示状态
        """
        if self.isList:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
        else:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")

    def viewModeChanged(self):
        """
        切换  缩略图/表单  显示
        """
        # print("viewThumbnail Changed !")
        isAction = self.isAction
        keyWords = self.get_keywords()
        itemSize = self.ui.itemSize_Slider.value()

        if self.isList:
            '''如果list则切换icon显示'''
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
            self.isList = False
            self.ui_main_wgt.setIsList(self.isList)
            self.ui_main_wgt.setIconMode(itemSize, keyWords)
        else:
            '''否则切换list显示'''
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")
            self.isList = True
            self.ui_main_wgt.setIsList(self.isList)
            self.ui_main_wgt.setListMode(keyWords)
        self.show_asset()
        self.rememberSettings()

    def itemSizeSliderChanged(self):
        print("itemSizeSlider Changed !")
        itemSize = self.ui.itemSize_Slider.value()
        if self.isList:
            return
        else:
            self.ui_main_wgt.setItemSize(itemSize)
            self.ui_main_wgt.resizeItem()

    def itemSizeSliderReleased(self):
        print("itemSizeSlider Released !")
        itemSize = self.ui.itemSize_Slider.value()
        self.ui.itemSize_Slider.setToolTip(u"%s" % itemSize)
        self.rememberSettings()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print("按压")
        try:
            self.ui_main_wgt._table_wgt.user_menu.close()
        except:
            pass
        try:
            self.ui_main_wgt._table_wgt.note_menu.close()
        except:
            pass

    def download_asset(self):
        """
        下载资产到本地
        """
        download_root = QtWidgets.QFileDialog.getExistingDirectory(self, u"选择一个根目录存放下载的资产")
        if download_root != "":
            __project, __type, __path = self.getPanelsData()
            currentSelected = self.ui_main_wgt.selectedItems()
            if currentSelected:
                data = currentSelected[0].itemData()
                org_path = data['icon_path'].split("/Icon")[0]
                download_path = "%s/%s/Assets/%s/%s" % (download_root, __project, __type, data['role_name'])
                if os.path.exists(download_path):  # 如果有就删除
                    try:
                        shutil.rmtree(download_path)
                    except:
                        QtWidgets.QMessageBox.warning(self, u"提示：", u"无法删除已有资产 ！ 请确定没被程序占用后再试")
                        return
                # self.allNum = 0.00
                # self.copyedNum = 0.00
                # self.download_percent = u"下载：1 % "
                # self.countNum(org_path)
                # self.progress = QtWidgets.QProgressDialog(self)
                # self.progress.setWindowTitle(u"请稍等")
                # self.progress.setLabelText(u"正在操作...")
                # self.progress.setCancelButtonText(u"取消")
                # self.progress.setRange(0, 100)
                # self.progress.show()
                # try:
                # self.copytree(org_path, download_path)
                # self.showProgressDialog()
                # QtWidgets.QMessageBox.information(self, u"提示：", u"下载完成 ！")
                cmds.waitCursor(state=True)
                thread = copy_thread.CopyThread(org_path, download_path)
                # thread.update_num.connect(self.update_progress)
                thread.step_signal.connect(self.update_progress)
                thread.file_signal.connect(self.showProgressDialog)
                # self.infoMsg("info", self.download_percent)
                thread.start()

                # except Exception as e:
                #     QtWidgets.QMessageBox.warning(self, u"提示：", u"下载失败:{}".format(e))
            else:
                pass

    def update_progress(self, val):
        self.progress = val

    # def copytree(self, src, dst, symlinks=False, ignore=None):
    #     if not os.path.exists(dst):
    #         os.makedirs(dst)
    #         shutil.copystat(src, dst)
    #     lst = os.listdir(src)
    #     if ignore:
    #         excl = ignore(src, lst)
    #         lst = [x for x in lst if x not in excl]
    #     for item in lst:
    #         s = os.path.join(src, item)
    #         d = os.path.join(dst, item)
    #         if symlinks and os.path.islink(s):
    #             if os.path.lexists(d):
    #                 os.remove(d)
    #             os.symlink(os.readlink(s), d)
    #             try:
    #                 st = os.lstat(s)
    #                 mode = stat.S_IMODE(st.st_mode)
    #                 os.lchmod(d, mode)
    #             except:
    #                 pass  # lchmod not available
    #         elif os.path.isdir(s):
    #             self.copytree(s, d, symlinks, ignore)
    #         else:
    #             shutil.copy2(s, d)
    #             self.copyedNum += 1
    #             print(self.copyedNum)
    #             self.progress.setValue(self.copyedNum)
    #             if self.progress.wasCanceled():
    #                 break
    # self.download_percent = u"下载完成：%s " % int(self.copyedNum / self.allNum * 100) + "%"
    # time.sleep(0.5)
    # self.infoMsg("info", self.download_percent)

    # thread = myWidget.MyThread()
    # thread.signal.connect(lambda: self.infoMsg("info", self.download_percent))
    # thread.start()

    def countNum(self, src):
        fileList = os.listdir(src)
        for filename in fileList:
            pathTmp = os.path.join(src, filename)
            if os.path.isdir(pathTmp):
                self.countNum(pathTmp)
            elif os.path.isfile(pathTmp):
                self.allNum += 1

    def show_asset(self, data=None):
        """ 刷新数据，展示资产 """
        print("展示数据", self.user, self.password)
        # self.listWidgetAddItems(self.getItemsList())
        self.ui_main_wgt.clear()
        self.load_worker = GetDataThread(self.currentProject(), self.currentType(), self.user, self.password,
                                         self.get_keywords(), "")
        self.load_worker.data_signals.connect(self.display_data)
        self.load_worker.error_signals.connect(self.display_error)
        self.load_worker.finish_signals.connect(self.display_finish)
        self.load_worker.start()

        # keyWords = self.get_keywords()
        # if data is None:
        #     data = self._database
        # self.main_wgt.setItemsList(data)
        # self.main_wgt.setIsList(self.isList)
        # if not self.isList:  # 如果是图标
        #     # self.main_wgt.addItems()
        #     self.main_wgt.setItemSize(self.itemSize_Slider.value())
        #     self.main_wgt.show_icon(keyWords)
        #     self.main_wgt.resizeItem()
        # else:  # 如果是表格
        #     self.main_wgt.show_table(keyWords)
        # self.asset_num_label.setText(f"共加载 {len(data)} 个资产")

    def display_data(self, data):
        """ 加载数据 """
        self.ui_main_wgt.addItem(data)

    def display_error(self, e):
        """ 加载数据错误 """
        QtWidgets.QMessageBox.warning(self, u"提醒", u"你尚未登录ShotManager系统\n\n" + str(e))

    def display_finish(self):
        """ 加载数据完成 """
        self.ui_main_wgt.resizeItem()
        self.infoMsg("info", f"加载到{self.ui_main_wgt.itemCount()}个资产")

    def showProgressDialog(self, file):
        print("progress....")
        progress = QtWidgets.QProgressDialog(self)
        progress.setWindowTitle(u"请稍等")
        progress.setLabelText(file)
        progress.setCancelButtonText(u"取消")
        # progress.setRange(0, self.allNum)
        progress.setValue(self.progress)
        progress.setMinimumDuration(0)
        if progress.wasCanceled():
            QtWidgets.QMessageBox.warning(self, u"提示", u"操作中断")

    def refresh_asset(self):
        """ 刷新 """
        # print("refresh asset !")
        # self.__showedItemNum = 0
        if not self.isAction:
            self.listWidgetAddItems(self.getItemsList())
        else:
            self.update_action()

    def get_keywords(self):
        """
        :return: [] list of keyword
        """
        print("搜索：", self.ui.key_line.text())
        # keywords = []
        # kkk = self.ui.key_line.text()
        # for key in kkk.split(","):
        #     keywords.append(key)
        return [self.ui.key_line.text().strip()]

    def search_asset(self):
        """ 搜索 """
        print("search asset !")
        self.show_asset()
        # __project, __type, __path = self.getPanelsData()
        # self.infoMsg("info", "Loading...")
        # self.update_asset_thread.start()
        # self.listWidgetAddItems()

        # if not self.ui.searchAll_cBox.isChecked():
        #     self.listWidgetAddItems()
        # else:
        #     list = []
        #     for p in self.projectSetting()['projects']:
        #         for t in self.projectSetting()['type']:
        #             list.extend(self.getItemsDict(p, t))
        #     self.listWidgetAddItems(list)

    # def projectSetting(self):
    #     data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % self.scriptsPath)
    #     return data

    def getPanelsData(self):
        """
        获取当前面板信息
        :return: __project, __type, __path
        """
        __project = str(self.ui.project_comb.currentText())
        __type = str(self.ui.type_listWgt.selectedItems()[0].text())
        __path = '%s/%s/%s/%s' % (self.ROOT,
                                  __project,
                                  projectSetting()['assetFolder'],
                                  __type)
        return __project, __type, __path

    def getCurrentItemsData(self):
        """
        获取当前图标信息
        :return:__item, __fileType, __folder
        """
        __item = self.ui_main_wgt.selectedItems()
        __fileType = self.ui.fileType_bttnGroup.checkedButton().text()
        __folder = self.__fileTypeFolderDict[__fileType]
        if not __item:
            return
        return __item, __fileType, __folder

    def loadingGif(self):
        """
        加载loading gif图片
        :return:
        """
        # print("loadingGif()")
        self.loadingWgt = QtWidgets.QWidget(self.ui_main_wgt)
        lay = QtWidgets.QHBoxLayout()
        print(self.ui_main_wgt.height(), self.ui_main_wgt.width())
        lay.setContentsMargins(self.ui_main_wgt.height() / 2, self.ui_main_wgt.width() / 2, 0, 0)
        self.loadingWgt.setLayout(lay)
        label = QtWidgets.QLabel()
        mov = QtGui.QMovie('%s/icon/loading.gif' % self.scriptsPath)
        mov.start()
        label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        label.setMovie(mov)
        lay.addWidget(label)
        self.loadingWgt.show()

    def eventFilter(self, receiver, event):
        self.receiver = receiver
        self.mouse_button = QtWidgets.QApplication.mouseButtons()
        if event.type() == QtCore.QEvent.Enter:
            self.drag_drop_happened()
            return True
        elif event.type() == QtCore.QEvent.Leave:
            self.remove_maya_eventFilter()
            return True
        return False

    def mainWgtItemDragLeaved(self):
        self.install_maya_eventFilter()

    def install_maya_eventFilter(self):
        print("install maya event filter !")
        self.mayaMainWindow.installEventFilter(self)

    def remove_maya_eventFilter(self):
        print("remove maya event filter !")
        self.mayaMainWindow.removeEventFilter(self)

    def drag_drop_happened(self):
        """
        拖入触发
        :return:
        """
        # print("drag_drop_happened")
        menu = QtWidgets.QMenu(self.mayaMainWindow)
        action_a = QtWidgets.QAction(u"Import...", menu)
        action_a.triggered.connect(self.importFile)
        action_b = QtWidgets.QAction(u"Create Reference...", menu)
        action_b.triggered.connect(self.createRef)
        menu.addAction(action_a)
        menu.addAction(action_b)
        menu.popup(QtGui.QCursor.pos())
        self.remove_maya_eventFilter()

    # def mainWightSizeChanged(self):
    #     print("mainWightSizeChanged !")
    #     # if self.__showedItemNum < self.ui_main_wgt.count() and self.__showedItemNum != 0 :
    #     self.__update_visible_icon()
    #
    # def mainWightWheeled(self):
    #     print("mainWight Wheel !")
    #     # if self.__showedItemNum < self.ui_main_wgt.count():
    #     self.__update_visible_icon()

    # def mainScrollBarValueChanged(self):
    #     print("main ScrollBar ValueChanged to %s!"%self.ui_main_wgt.verticalScrollBar().value())
    #     # if self.__showedItemNum < self.ui_main_wgt.count():
    #     self.__update_visible_icon()

    # def getItemsList(self,keyWords=u""):
    #     """
    #     从CGTW获取图标text列表
    #     :param keyWords:
    #     :return: textList
    #     """
    #     type, project, path = self.getPanelsData()
    #     itemsList = list_items._listItems_CGT('Assets', project, type, 'asset',
    #                                           'asset.maya', 'asset.assetstapy',
    #                                           'asset.entity', 'asset.cn_name', keyWords)
    #     return itemsList

    def getItemsList(self):
        """
        获取数据列表
        :return:[item list]
        """
        # print("count Items")
        __tab = self.tab
        # if _project and _type:
        #     __project, __type = _project, _type
        # else:
        __project, __type, __path = self.getPanelsData()

        # asset_list = [] # 全项目，没太大用暂时不考虑
        # if self.isCGTW:
        #     for _p in self.projectSetting()['projects']:
        #         for _t in self.projectSetting()['type']:
        #             asset_list.extend(self.ui_main_wgt.getItemsDictFromCGTW(__tab, _p, _t))
        #     return asset_list

        # if self.isSQL:
        #     return self.get_database(__project, __type)
        # else:
        #     return self.getItemsListFromPath(self.ROOT, __tab, __project, __type)

    def get_database(self, _project, _type):
        """ 得到asset数据 """
        conn = None
        cur = None
        get_script = ''' 
             SELECT "asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", "asset.mod_status", 
             "asset.rig_artist", "asset.rig_status", "asset.icon", "asset.note"
             FROM public."asset"
             WHERE
             "asset.type" = '%s';
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

    def get_scene_database(self, _type, keyword=""):
        """ 得到scene数据 """
        conn = None
        cur = None
        get_script = ''' 
             SELECT "scene.date", "scene.name", "scene.zh_name", "scene.artist", "scene.status", "scene.icon" 
             FROM public."scene"
             WHERE
             "asset.type" = '%s';
             ''' % _type
        try:
            conn = psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host,
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

    def getItemsListFromCGTW(self, __tab, __project, __type):
        """
        从CGTW获取item列表
        :return: [{'role_name': xx, 'project': xx, 'type': xx, 'zh_name': xx, 'icon_path': xx}]
        """
        import cgtw2
        t_tw = cgtw2.tw()
        token = t_tw.login.token()
        __items_dict = []
        asset, assetmaya, assetstapy, entity, cn_name, image = self.get_CGTW_entity(__tab, __type)

        path = '{0}/{1}/{2}/{3}'.format(self.projectSetting()['rootPath'], __project, __tab, __type)
        TW_proj = str(self.projectSetting()['projectdiction'][__project])
        t_asset_ids = t_tw.info.get_id(TW_proj, asset, [[assetmaya, '=', u"完成"], 'and', [assetstapy, '=', __type]])
        TW_dictionInfo = t_tw.info.get(TW_proj, asset, t_asset_ids, [entity, cn_name, image])
        for info in TW_dictionInfo:
            icon_path = '{0}/{1}/Icon/{1}.png'.format(path, info[entity])
            # if info[image] != "":
            #     icon_url = 'http://10.0.203.40%s?token=%s' % (json.loads(info[image])[0].get("max"), token)
            # else:
            #     icon_url = ""
            bbb = {'role_name': info[entity], 'project': __project, 'type': __type, 'mod_status': 0, 'rig_status': 0,
                   'mod_artist': u'谢豫闽', 'rig_artist': u'谢豫闽', 'zh_name': info[cn_name], 'icon_path': icon_path,
                   'date': '20230213'}
            __items_dict.append(bbb)

        return __items_dict

    @staticmethod
    def get_CGTW_entity(_tab, _type):
        """ 获取对应字段 """
        if _tab == 'Assets':
            return 'asset', 'asset.maya', 'asset.assetstapy', 'asset.entity', 'asset.cn_name', 'asset.image'
        elif _tab == 'Scenes':
            if _type != "Map":
                return 'scenes', 'scenes.maya', 'scenes.scenesassetstype', 'scenes.entity', 'scenes.assetsnamecn', \
                    'scenes.image'
            else:
                return 'map', 'map.maya', 'map.type', 'map.entity', 'map.mapnamecn', 'map.image'

    @staticmethod
    def getItemsListFromPath(__root, __tab, __project, __type):
        """
        从路径获取列表，少了中文名默认为“”
        :return: [{'role_name': xx, 'project': xx, 'type': xx, 'zh_name': '', 'icon_path': xx}]
        """
        # print("getItemsDictFromPath")
        __items_dict = []
        __path = '{0}/{1}/{2}/{3}'.format(__root, __project, __tab, __type)
        _dir = QtCore.QDir(__path)
        for role_name in _dir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot):
            icon_path = '{0}/{1}/Icon/{1}.png'.format(__path, role_name)
            zn_name = ""
            bbb = {'role_name': role_name, 'project': __project, 'type': __type,
                   'zh_name': zn_name, 'icon_path': icon_path}
            __items_dict.append(bbb)

        return __items_dict

    # def update_asset(self):
    #     """
    #     更新资产的多线程
    #     """
    #     __project, __type, __path = self.getPanelsData()
    #     if os.path.exists(__path):
    #         self.infoMsg("info", "Loading...")
    #         self.update_asset_thread.start()
    #     else:
    #         self.ui_main_wgt.clear()

    def update_action(self):
        """
        更新动作库的多线程
        :return:
        """
        currentSelected = self.ui_main_wgt.selectedItems()
        if currentSelected:
            self.currentAssetData = currentSelected[0].itemData()
        item_data = self.currentAssetData
        __project, __type, __path = self.getPanelsData()
        if os.path.exists(__path):
            # update_action_thread = myWidget.MyThread()
            # update_action_thread.signal.connect(lambda: self.listWidgetAddActionItems(item_data))
            self.infoMsg("info", "Loading...")
            # update_action_thread.start()
        else:
            self.ui_main_wgt.clear()

    def listWidgetAddItems(self, update_new_list=None):
        """
        根据CGT资产数据，设置主面板item显示
        :param update_new_list: 重新计算的数据
        :return:
        """
        # print("listWidgetAddItems Asset")
        self.ui_main_wgt.clear()
        # self.ui.preview.clear()
        self.isAction = False

        start_time = time.time()

        if update_new_list:  # 如果更新列表
            self.ui_main_wgt.setItemsList(update_new_list)

        keyWords = self.get_keywords()
        self.ui_main_wgt.setIsList(self.isList)
        self.ui_main_wgt.addItems(keyWords[0])
        # if len(keyWords) == 1:  # 根据关键字加载
        #     self.ui_main_wgt.addItems(keyWords[0])
        # else:
        #     for key in keyWords:
        #         self.ui_main_wgt.addItems(key, add=True)

        self.ui_main_wgt.setItemSize(self.ui.itemSize_Slider.value())
        self.ui_main_wgt.resizeItem()

        end_time = time.time()
        self.infoMsg("info", "%s items" % (self.ui_main_wgt.itemCount()) +
                     '   Cost :  %.2f' % (end_time - start_time) + ' sec')

    # def __update_visible_icon(self):
    #     '''弃用动态更新icon'''
    #     # print("__update_visible_icon")
    #     if self.isList:
    #         return
    #     else:
    #         starttime = time.time()
    #         self.__updatedNum = self.ui_main_wgt.updateIcons()
    #         self.ui_main_wgt.setIconMode()  # 不整理一下会大小乱掉
    #         endtime = time.time()
    #         self.infoMsg("info", "%s/%s items" % (self.__updatedNum, self.ui_main_wgt.count()) +
    #                      '   Cost :  %.2f' % (endtime - starttime) + ' sec')

    # self.ui_main_wgt._sizeSignal.connect(self.mainWightSizeChanged)  # 放这里只在item数量多时触发sizeChanged一次
    #  不知道为什么开始的计算窗体width总是640，所以触发一下

    # ==============测试view model失败===================================
    # if is_list:
    #     model = myWidget.MyListModel(tex=itemsList, icon=[], showNum = len(itemsList))
    #     self._viewList()
    # else:
    #     model = myWidget.MyListModel(itemsDict=self.getItemsListDict(keyWords), allNum = len(self.getItemsListDict(keyWords)))
    #     self.ui_main_wgt.setModel(model)
    #     #================文件夹显示==================================
    #     # model = QtWidgets.QFileSystemModel()
    #     # model.setRootPath(u"Y:/MCCProject/FFA/Assets/Props")
    #     # self.ui_main_wgt.setModel(model)
    #     # self.ui_main_wgt.setRootIndex(model.index(u"Y:/MCCProject/FFA/Assets/Props",int = 1))
    #     self._viewThumb()
    #
    # endtime = time.time()
    # messageBox.show_msg(self.ui.msg_icon_label,'info',
    #                     self.ui.msg_label,'Completed !  '+'   Path :  '+path+'        Total :  '+
    #                     str(len(self.getItemsListDict(keyWords)))+'        Cost :  '+ str(endtime-starttime)+' sec')
    # ===============ListWgt==========================================
    # if is_list:
    #     list_items._listWidgetAddItems_list(self.ui_main_wgt, __project, __type)
    # else:
    #     list_items._listWidgetAddItems_icon(self.ui_main_wgt, __project, __type)
    # role_name = list.split('   /   ')[0]
    # item = QtWidgets.QListWidgetItem()
    # item_data = {'role_name': role_name, 'project': project, 'type': type}
    # item.setData(QtCore.Qt.UserRole, item_data)
    # item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    # if is_list:
    #     item.setText(list)
    # else:
    #     item.setText(list.replace('   /   ','\n'))
    #     # item.setToolTip(list.replace('   /   ', '\n'))
    #     icon = QtGui.QIcon()
    #     icon.addPixmap(QtGui.QPixmap("%s/icon/blank_ch.png" % self.scriptsPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    #     item.setIcon(icon)
    # self.ui_main_wgt.addItem(item)
    # self.get_viewThumbnail()

    # def isItemVisible(self, item):
    #     """
    #     Return the visual rect for the item. 返回显示在矩形中的item
    #     :type item: QtWidgets.QTreeWidgetItem
    #     :rtype: bool
    #     """
    #     height = self.ui_main_wgt.height()
    #     itemRect = self.ui_main_wgt.visualItemRect(item) #QtCore.QRect(坐标x, 坐标y, 宽度, 高度)
    #     scrollBarY = self.ui_main_wgt.verticalScrollBar().value()
    #     itemSize = self.ui.itemSize_Slider.value()
    #     y = height + scrollBarY - itemRect.y()
    #     return y >= scrollBarY and y <= scrollBarY + height + itemSize

    # def updateItemVisibleIcon(self):
    #     """
    #     动态更新可见的icon
    #     :return:
    #     """
    # print("updateItemVisibleIcon:",self.__showedItemNum)
    # width = self.ui_main_wgt.width()
    # scrollBarY = self.ui_main_wgt.verticalScrollBar().value()
    # itemSize = self.ui.itemSize_Slider.value()
    # keyWords = self.ui.key_line.text()
    # column = width//itemSize
    # row = (height + scrollBarY)//itemSize
    # if self.isList:
    #     pass
    # else:
    #     self.update_icon_thread = myWidget.MyThread()
    #     self.update_icon_thread._signal.connect(self.__update_visible_icon)
    #     self.infoMsg("info", "Loading...")
    #     self.update_icon_thread.start()
    #     self.update_icon_thread.finished.connect(self._viewThumb)

    # ===============model/view框架更新==============================================
    # model = myWidget.MyListModel(itemsDict=self.getItemsListDict(keyWords), allNum=len(self.getItemsListDict(keyWords)))
    # model.removeRows(0,2)
    # model.insertRows(0,2)
    # self.ui_main_wgt.setModel(model)
    # self.__showedItemNum = column*row

    #     if self.isList:
    #         pass
    #     else:
    #         listDict = self.getItemsListDict()
    #         self.update_icon_thread = myWidget.MyThread()
    #         self.update_icon_thread._signal.connect(lambda: _updateItemVisibleIcon())
    #         self.update_icon_thread.start()
    #         def _updateItemVisibleIcon():
    #             for i in range(self.ui_main_wgt.count()):
    #                 item = self.ui_main_wgt.item(i)
    #                 if self.isItemVisible(item):
    #                     icon = QtGui.QIcon()
    #                     icon_path = listDict[item.text()]
    #                     pixmap = QtGui.QPixmap(icon_path)
    #                     icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
    #                     item.setIcon(icon)
    #         self.update_icon_thread.finished.connect(self._viewThumb)

    # def countItemsIndexStart(self):
    #     itemSize = self.ui.itemSize_Slider.value()
    #     return self.ui_main_wgt.countItemsIndexStart(itemSize)
    #
    # def countItemsIndexEnd(self):
    #     itemSize = self.ui.itemSize_Slider.value()
    #     return  self.ui_main_wgt.countItemsIndexEnd(itemSize)

    #
    # def listWidgetAddItems(self):
    #     """
    #     根据type，project，从文件夹获取主面板item显示
    #     :return:
    #     """
    #     listWgt = self.ui_main_wgt
    #     listWgt.clear()
    #     __project, __type, __path = self.getPanelsData()
    #     keyWords = self.ui.key_line.text()
    #     is_list = self.isList
    #     dir = QtCore.QDir(__path)
    #     if is_list:
    #         for role_name in dir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot):
    #             role_rig_dir = QtCore.QDir(('{0}/{1}/{2}').format(__path, role_name, self.projectSetting()['modelFolder']))
    #             if role_rig_dir.entryList(['*_mod.ma', '*_OAT.ma', '*_AD.ma', '*_mod.max'], QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot) and role_name.lower().find(keyWords) != -1:
    #                 item_data = {'role_name': role_name,'project': __project,'type': type}
    #                 item = QtWidgets.QListWidgetItem()
    #                 item.setText(('{0}').format(role_name))
    #                 item.setData(QtCore.Qt.UserRole, item_data)
    #                 item.setTextAlignment(QtCore.Qt.AlignLeft)
    #                 listWgt.addItem(item)
    #     else:
    #         for role_name in dir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot):
    #             role_rig_dir = QtCore.QDir(('{0}/{1}/{2}').format(__path, role_name, self.projectSetting()['modelFolder']))
    #             if role_rig_dir.entryList(['*_mod.ma', '*_OAT.ma', '*_AD.ma', '*_mod.max'], QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot) and role_name.lower().find(keyWords) != -1:
    #                 icon_path = ('{0}/{1}/{2}/{1}.png').format(__path, role_name, self.projectSetting()['iconFolder'])
    #                 if QtCore.QFileInfo(icon_path).exists() is False:
    #                     icon_path = "%s/icon/Default.png" %self.scriptsPath
    #                 item_data = {'role_name': role_name,'project': __project,'type': type}
    #                 itemSize = self.ui.itemSize_Slider.value()
    #                 item = QtWidgets.QListWidgetItem()
    #                 item.setText(('{0}').format(role_name))
    #                 item.setData(QtCore.Qt.UserRole, item_data)
    #                 icon = QtGui.QIcon()
    #                 pixmap = QtGui.QPixmap(icon_path)
    #                 icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
    #                 item.setIcon(icon)
    #                 listWgt.setIconSize(QtCore.QSize(itemSize, itemSize))
    #                 item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
    #                 listWgt.addItem(item)

    def listWidgetAddActionItems(self, item_data):
        """
        根据选择item，添加主面板Action显示
        :param item_data:
        :return:
        """
        selectedPath = '{0}/{1}/Assets/{2}/{3}'.format(self.ROOT, item_data['project'],
                                                       item_data['type'], item_data['role_name'])
        preview_dir = QtCore.QDir('{0}/Action/ActionFile'.format(selectedPath))
        self.ui.back_bttn.setEnabled(True)
        self.ui.itemSize_Slider.setEnabled(False)
        self.ui_main_wgt.clear()
        self.isAction = True
        start_time = time.time()
        for i in preview_dir.entryList(['*.ma'], QtCore.QDir.Files | QtCore.QDir.NoDotAndDotDot):
            item = QtWidgets.QListWidgetItem()
            text = i.split('/')[(-1)].split('.')[0].split('_')[(-1)]
            item.setText(text)
            if self.isList:
                self.ui_main_wgt.setViewMode(QtWidgets.QListView.ListMode)
                item.setSizeHint(QtCore.QSize(22, 22))
                self.ui_main_wgt.setGridSize(QtCore.QSize(200, 25))
                self.ui_main_wgt.setSpacing(1)
                item.setData(QtCore.Qt.UserRole, item_data)
                self.ui_main_wgt.addItem(item)
            else:
                item.setSizeHint(QtCore.QSize(160, 180))
                self.ui_main_wgt.setGridSize(QtCore.QSize(162, 190))
                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignBottom)
                widget2 = QtWidgets.QWidget()
                widget2.setMaximumSize(QtCore.QSize(160, 160))
                lay = QtWidgets.QHBoxLayout()
                lay.setContentsMargins(0, 0, 0, 0)
                widget2.setLayout(lay)
                label = QtWidgets.QLabel()
                label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
                movPath = '%s/Action/Preview/%s' % (selectedPath, i.replace('.ma', '.gif'))
                if os.path.isfile(movPath):
                    mov = QtGui.QMovie(movPath)
                    # mov.start()
                    label.setMovie(mov)
                else:
                    icon_path = "%s/icon/Default_action.png" % self.scriptsPath
                    pixmap = QtGui.QPixmap(icon_path)
                    label.setPixmap(pixmap)
                lay.addWidget(label)
                item.setData(QtCore.Qt.UserRole, item_data)
                self.ui_main_wgt.addItem(item)
                self.ui_main_wgt.setItemWidget(item, widget2)
        end_time = time.time()
        self.ui.msg_label.setText('Completed !  ' + '   Path :  ' + selectedPath + 'Action        Total :  ' + str(
            self.ui_main_wgt.count()) + '        Cost :  ' + str(end_time - start_time) + ' sec')

    def mainWightItemChanged(self):
        """
        改变item触发：改变rBttn显示,改变标题显示，改变预览显示
        :return:
        """
        currentSelected = self.ui_main_wgt.selectedItems()
        # print(currentSelected[0])
        self.ui.preview.clear()
        if currentSelected:
            rBttn_dict = {'mod': 'self.ui.mod_rBttn',
                          'hi_rig': 'self.ui.hiRig_rBttn',
                          'low_rig': 'self.ui.lowRig_rBttn',
                          'all_rig': 'self.ui.allRig_rBttn',
                          'render': 'self.ui.render_rBttn',
                          'xgen': 'self.ui.xgen_rBttn',
                          'AD': 'self.ui.ad_rBttn',
                          'OAT': 'self.ui.oat_rBttn'}
            eval(rBttn_dict['mod']).setEnabled(True)
            eval(rBttn_dict['hi_rig']).setEnabled(True)
            eval(rBttn_dict['low_rig']).setEnabled(True)
            eval(rBttn_dict['all_rig']).setEnabled(True)
            eval(rBttn_dict['render']).setEnabled(True)
            eval(rBttn_dict['xgen']).setEnabled(True)
            eval(rBttn_dict['AD']).setEnabled(True)
            eval(rBttn_dict['OAT']).setEnabled(True)
            item_data = currentSelected[0].itemData()
            # print(item_data[7])

            '''########## 根据item_data设置预览窗口显示 ##################################################'''
            self.ui.preview.setTitle(item_data[1], item_data[2])

            if not self.isAction:
                self.ui.preview.setPreviewPixmap(item_data[7], "asset_ch")
            else:
                self.ui.preview.playerEnabled(True)
                self.ui.PreviewLabel.setAnim(item_data['icon_path'], "animation")

            '''########## 根据detailPath文件是否存在，设置rBttn_dict是否可用 ##############################'''
            # print(rBttn_dict)
            for ty in rBttn_dict.keys():
                # print(self.detailPath())
                file_info = QtCore.QFileInfo(self.detailPath()[ty])
                if file_info.exists() is False:
                    eval(rBttn_dict[ty]).setEnabled(False)

            '''########## 设置喜好和标签 #################################################################'''
            if not currentSelected[0].isFavor():
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
            else:
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))

            if not currentSelected[0].isTag():
                self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
            else:
                self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/tag.png' % self.scriptsPath))
        else:
            pass

    def show_menu(self, point):
        """
        main_listWgt 的右键菜单
        :param point:
        :return:
        """
        currentItem = self.ui_main_wgt.selectedItems()
        # print("$$$$$$$$$$$$$", currentItem)
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

            self.checkDir('Action', currentItem[0], action_action)  # 检查Action是否为空，决定action_action是否可用

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
            modPublish_action.triggered.connect(lambda: __modPublish())

            def __modPublish():
                import tools_publish.PublishTools.PublishTool as PT
                PT.showWindow(tab=0)

            rigPublish_action = QtWidgets.QAction(u'发布绑定资产', self)
            rigPublish_action.setIcon(QtGui.QIcon("{}/icon/publish.png".format(self.scriptsPath)))
            rigPublish_action.triggered.connect(lambda: __rigPublish())

            def __rigPublish():
                import tools_publish.PublishTools.PublishTool as PT
                PT.showWindow(tab=1)

            refresh_action = QtWidgets.QAction(u'刷新', self)
            refresh_action.setIcon(QtGui.QIcon("{}/icon/refresh.png".format(self.scriptsPath)))
            refresh_action.triggered.connect(self.refresh_asset)

            menu.addAction(modPublish_action)
            menu.addAction(rigPublish_action)
            menu.addSeparator()
            menu.addAction(refresh_action)

            menu.exec_(QtGui.QCursor.pos())
        return

    def openDir(self, _type, item):
        """
        'Show in Explorer'打开文件夹
        :param _type: 例Action
        :param item:
        """
        hi_rig_path = self.detailPath()['hi_rig']
        folder_path = hi_rig_path.split('Rig')[0]
        folder_path = '{0}/{1}'.format(folder_path, _type)
        folder_info = QtCore.QFileInfo(folder_path)
        if folder_info.exists():
            QtGui.QDesktopServices.openUrl(folder_path)
        else:
            self.infoMsg('warning', 'Can not find {0}'.format(folder_path))

    def checkDir(self, _type, item, action):
        """
        检查选择item的路径下是否为空，决定右键菜单显示是否可用
        :param _type: 例Action
        :param item:
        :param action:
        :return:
        """
        item_data = item.itemData()
        # print(item_data)
        folder_path = item_data[7].split("Icon")[0]
        folder_path = '{0}/{1}'.format(folder_path, _type)
        # print(folder_path)
        folder_info = QtCore.QFileInfo(folder_path)
        if folder_info.exists():
            action.setEnabled(True)
        else:
            action.setEnabled(False)

    def applyAction(self):
        """运用动作库"""
        pass

    def importFile(self):
        """ 根据选择的FileType，导入选择的item文件 """
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
            print(__item, __fileType, __folder)
        except Exception:
            self.infoMsg('warning', 'Please select Character!!!')
            return

        # if len(__item) != 1:
        #     self.infoMsg('warning', 'Please select one file!!!')
        #     return
        item_data = __item[0].itemData()
        file_path = self.detailPath()[__fileType]
        file_info = QtCore.QFileInfo(file_path)
        if file_info.exists():
            rpr = '%s_%s' % (item_data[1], __fileType)
            cmds.file(file_path, i=True, type='mayaAscii', mergeNamespacesOnClash=False, renamingPrefix=rpr,
                      ignoreVersion=True, options='v=0;',
                      preserveReferences=True, importFrameRate=True, importTimeRange='override')
        else:
            self.infoMsg('warning', 'Can not find {0}'.format(file_path))

    def importAction(self):
        currentSelected = self.ui_main_wgt.selectedItems()
        item_data = currentSelected[0].itemData()
        actionpath = '{0}/{1}/Assets/{2}/{3}/Action/ActionFile/{3}'.format(self.ROOT,
                                                                           item_data['project'],
                                                                           item_data['type'],
                                                                           item_data['role_name']) + "_" + \
                     currentSelected[0].text() + ".ma"
        file_info = QtCore.QFileInfo(actionpath)
        if file_info.exists():
            cmds.file(actionpath, i=True, type='mayaAscii', mergeNamespacesOnClash=False, ignoreVersion=True,
                      options='v=0;',
                      preserveReferences=True, importFrameRate=True, importTimeRange='override')
        else:
            self.infoMsg('warning', 'Can not find {0}'.format(actionpath))

    def exportFbx(self):
        """ export Fbx"""
        __project, __type, __path = self.getPanelsData()
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            self.infoMsg('warning', 'Please select Character!!!')
            return

        if __fileType != 'hi_rig':
            cmds.warning('Please select hi_rig!')
            return
        cmds.file(new=True, force=True)
        for item in __item:
            item_data = item.itemData()
            file_info = QtCore.QFileInfo(self.detailPath()[__fileType])
            if file_info.exists() and __type != 'Sets':
                cmds.file(self.detailPath()[__fileType], i=True, type='mayaAscii', mergeNamespacesOnClash=False,
                          renamingPrefix='%s_%s' % (item_data['role_name'], __fileType),
                          ignoreVersion=True, options='v=0', preserveReferences=True)
                if cmds.objExists('Geo_C_001_GRP') and cmds.objExists('DeformationSystem'):
                    cmds.select(clear=True)
                    cmds.select('Geo_C_001_GRP')
                    cmds.select('DeformationSystem', add=True)
                    path = self.detailPath()['hi_rig'].split('/Rig/')[0]
                    fbxFolderPath = '%s/%s' % (path, 'FBX')
                    self.Pub.makePath(fbxFolderPath)
                    self.Pub.createHistory(fbxFolderPath)
                    fbxPath = '%s/%s.fbx' % (fbxFolderPath, item_data['role_name'])
                    self.Pub.exportFBX(False, 1, 200, fbxPath)
                    cmds.file(new=True, force=True)
                else:
                    self.infoMsg('warning',
                                 '%s: Can not find Geo_C_001_GRP or DeformationSystem, Please Check!' % item_data[
                                     'role_name'])

    def detailPath(self):
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            self.infoMsg('warning', 'Please select Character!!!')
            return
        for item in __item:
            item_data = item.itemData()
            detailPaths = {'hi_rig': "{0}/Rig/{1}_hi_rig.ma".format(item_data[7].split("Icon")[0], item_data[1]),
                           'all_rig': "{0}/Rig/{1}_all_rig.ma".format(item_data[7].split("Icon")[0], item_data[1]),
                           'low_rig': "{0}/Rig/{1}_low_rig.ma".format(item_data[7].split("Icon")[0], item_data[1]),
                           'render': "{0}/Render/{1}_render.ma".format(item_data[7].split("Icon")[0], item_data[1]),
                           'mod': "{0}/Mod/{1}_mod.ma".format(item_data[7].split("Icon")[0], item_data[1]),
                           'xgen': '{0}/Xgen/{1}_xgen.ma'.format(item_data[7].split("Icon")[0], item_data[1]),
                           'icon': item_data[7],
                           'AD': '{0}/Assembly/{1}_AD.ma'.format(item_data[7].split("Icon")[0], item_data[1]),
                           'OAT': '{0}/Rig/{1}_OAT.ma'.format(item_data[7].split("Icon")[0], item_data[1])}
            return detailPaths

    def createRef(self):
        """
        创建Reference
        :return:
        """
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
            file_info = QtCore.QFileInfo(self.detailPath()[__fileType])
            if file_info.exists() and __type != 'Sets':
                nameSpace = '{0}_{1}'.format(item_data[1], __fileType)
                cmds.file(self.detailPath()[__fileType], reference=True, type='mayaAscii', ignoreVersion=True,
                          groupLocator=True, options='v=0;', mergeNamespacesOnClash=False, namespace=nameSpace)
            elif file_info.exists() and __type == 'Sets':
                assembly_name = cmds.assembly(name=item_data[1], type='assemblyReference')
                cmds.setAttr('{0}.definition'.format(assembly_name), self.detailPath()[__fileType], type='string')
            else:
                self.infoMsg('warning', 'Can not find {0}'.format(self.detailPath()[__fileType]))

    def __replace_ref(self):
        """
        替换角色Reference
        :return:
        """
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
        new_asset_path = self.detailPath()[__fileType]
        # print(new_asset_path)
        new_namespace = new_asset_path.split("/")[-1].split(".ma")[0]

        # mel.eval('file -loadReference {0} -type "mayaAscii" -options "v=0;" {1};'.format(selectRef,new_asset_path))# €错误似乎太长
        cmds.file(new_asset_path,
                  loadReference=selectRef,
                  options="v=0;")
        # cmds.namespace(rename=[namespace, new_namespace])

    def minimizeAttributeWin(self):
        """
        属性栏最小化
        """
        if self.isAttributeShow:
            self.ui.arrow_Bttn.setIcon(QtGui.QPixmap('%s/icon/arrowSingleRight.png' % self.scriptsPath))
            self.ui.arrow_Bttn.clicked.connect(lambda: minimize())

            def minimize():
                self.ui.mainWindow_splitter.setSizes([120, 500, 0])
                self.isAttributeShow = False
        else:
            self.ui.arrow_Bttn.setIcon(QtGui.QPixmap('%s/icon/arrowSingleLeft.png' % self.scriptsPath))
            self.ui.arrow_Bttn.clicked.connect(lambda: maximize())

            def maximize():
                self.ui.mainWindow_splitter.setSizes([120, 500, 300])
                self.isAttributeShow = True

    def show_menu_Preview_label(self, point):
        """
        Preview窗口的右键菜单
        :param point:
        :return:
        """
        currentItem = self.ui_main_wgt.selectedItems()
        menu = QtWidgets.QMenu(self.ui_main_wgt)
        if currentItem[0] is not None:
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

            self.checkDir('Action', currentItem[0], action_action)  # 检查Action是否为空，决定action_action是否可用

            action_action.triggered.connect(self.update_action)
            show_action.triggered.connect(partial(self.openDir, '', currentItem[0]))
            imp_action.triggered.connect(self.importFile)
            impa_action.triggered.connect(self.importAction)
            ref_action.triggered.connect(self.createRef)
            icon_action.triggered.connect(partial(self.refreshIcon, currentItem[0]))
            apply_action.triggered.connect(self.applyAction)

            menu.exec_(QtGui.QCursor.pos())

    def refreshIcon(self, item):
        """  重渲染icon并更新预览  """
        print("refresh icon", item.itemData())
        icon_path = item.itemData()[7]
        if os.path.isfile(icon_path):
            os.remove(icon_path)
        path = icon_path.rsplit("/", 1)[0]
        image = icon_path.split("/")[-1].split(".")[0]
        try:
            capture.show_capture_screen(self)
        except Exception as e:
            print("Error : show capture screen is stuck:%s" % e)
        # self.Pub.snapshot(path=path, imageName=image)
        # item.setIcon(icon_path)
        # self.ui.preview.setPreviewPixmap(icon_path)

    #
    # def playerSet(self):
    #     """播放器设置"""
    #     player = sequenceplayer.Player()
    #     player.setPlayButtonState(self.ui.Play_toolBttn)
    #     '''播放'''
    #     self.ui.Play_toolBttn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
    #     self.ui.Play_toolBttn.clicked.connect(lambda: player.play(100, self.ui.Play_toolBttn))
    #     '''起始帧'''
    #     self.ui.firstFrame_toolBttn.setIcon(
    #         QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))
    #     self.ui.firstFrame_toolBttn.clicked.connect(player.firstFrame)
    #     '''上一帧'''
    #     self.ui.prevFrame_toolBttn.setIcon(
    #         QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
    #     self.ui.prevFrame_toolBttn.clicked.connect(player.prevFrame)
    #     '''下一帧'''
    #     self.ui.nextFrame_toolBttn.setIcon(
    #         QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
    #     self.ui.nextFrame_toolBttn.clicked.connect(player.nextFrame)
    #     '''结束帧'''
    #     self.ui.lastFrame_toolBttn.setIcon(
    #         QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
    #     self.ui.lastFrame_toolBttn.clicked.connect(player.lastFrame)
    #
    # def __playerEnabled(self, value):
    #     self.ui.Play_toolBttn.setEnabled(value)
    #     self.ui.firstFrame_toolBttn.setEnabled(value)
    #     self.ui.prevFrame_toolBttn.setEnabled(value)
    #     self.ui.nextFrame_toolBttn.setEnabled(value)
    #     self.ui.lastFrame_toolBttn.setEnabled(value)

    def __create_AR_ref(self):
        selected_items = self.ui.scene_main_listWgt.selectedItems()
        if not selected_items:
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

    def __switchRef(self):
        """
        切换 Reference
        :return:
        """
        ref_list = []
        asset_all = self.ui.asset_all_rBttn.isChecked()
        asset_switch_type = self.ui.asset_switch_type_comb.currentText()
        if asset_all:
            all_ref = cmds.ls(references=True)
        else:
            all_ref = cmds.ls(selection=True)
        for i in all_ref:
            if cmds.referenceQuery(i, isLoaded=True):
                ref_list.append(cmds.referenceQuery(i, f=True))

        for i in set(ref_list):
            if i.find(asset_switch_type) == -1:
                unresolved_name = cmds.referenceQuery(i, filename=True, withoutCopyNumber=True)
                role_name = '{0}_{1}.ma'.format(os.path.split(unresolved_name)[(-1)].split('_')[0], asset_switch_type)
                new_path = os.path.join(os.path.split(unresolved_name)[0], role_name)
                if os.path.exists(new_path):
                    ref_node = cmds.referenceQuery(i, referenceNode=True)
                    cmds.file(new_path, loadReference=ref_node, type='mayaAscii', options='v=0;')
                else:
                    self.infoMsg('warning', 'Can not find {0}'.format(new_path))

    def __getAssetsExportPath(self):
        assetsExportPath = cmds.fileDialog2(fileMode=2, dialogStyle=2)[0]
        self.ui.assetsExportPath_line.setText(str(assetsExportPath))

    def __assetsExport(self):
        import shutil
        folder_path = self.ui.assetsExportPath_line.text()
        if not os.path.exists(folder_path):
            self.infoMsg('warning', 'Please check your path!!!')
            return
        try:
            __item, __fileType, __folder = self.getCurrentItemsData()
        except:
            self.infoMsg('warning', 'Please select Character!!!')
            return

        for item in __item:
            item_data = item.itemData()
            file_list = [self.detailPath()['hi_rig'], self.detailPath()['mod'], self.detailPath()['icon']]
            for i in file_list:
                if os.path.exists(i):
                    new_path = '%s%s' % (folder_path, os.path.dirname(i).split(':')[1])
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                    shutil.copy2(i, new_path)
                else:
                    self.infoMsg('warning', 'Can not find %s' % i)

            if self.ui.assetsTextureExport_cBox.isChecked():
                texture_folder = '%s/Texture/' % self.detailPath()['mod'].split('/Mod/')[0]
                new_texture_path = '%s%s' % (folder_path, texture_folder.split(':')[1])
                if os.path.exists(new_texture_path):
                    shutil.rmtree(new_texture_path)
                shutil.copytree(texture_folder, new_texture_path)

    def infoMsg(self, icon, text):
        """
        消息栏
        :param icon: "warning", "info", "error"
        :param text: str
        """
        messageBox.show_msg(self.ui.msg_icon_label, icon,
                            self.ui.msg_label, text)

    @staticmethod
    def copyKey():
        """ 拷贝帧命令 """
        minTime = cmds.playbackOptions(query=True, minTime=True)
        maxTime = cmds.playbackOptions(query=True, maxTime=True)
        sel_ctrls = cmds.ls(sl=1)
        for sel_ctrl in sel_ctrls:
            if len(sel_ctrl.split(":")) == 1:  # 如果没有空间名
                ctrl_name = sel_ctrl
                cmds.copyKey(sel_ctrl, time=(minTime, maxTime))
                aniAST_list = cmds.ls('*:*_*_AST', type='transform')
                for aniAST in aniAST_list:
                    asset_name = aniAST.split(":")[0]
                    past_ctrl = "{0}:{1}".format(asset_name, ctrl_name)
                    try:
                        cmds.pasteKey(past_ctrl)
                    except:
                        print(u"场景里没有找到这个控制器：{}".format(past_ctrl))
            else:  # 如果带空间名
                sel_asset = sel_ctrl.split(":")[0]
                ctrl_name = sel_ctrl.split(":")[1]
                cmds.copyKey(sel_ctrl, time=(minTime, maxTime))
                aniAST_list = cmds.ls('*:*_*_AST', type='transform')
                for aniAST in aniAST_list:
                    asset_name = aniAST.split(":")[0]
                    if asset_name != sel_asset:  # 排除同一个资产
                        past_ctrl = "{0}:{1}".format(asset_name, ctrl_name)
                        try:
                            cmds.pasteKey(past_ctrl)
                        except:
                            print(u"场景里没有找到这个控制器：{}".format(past_ctrl))
