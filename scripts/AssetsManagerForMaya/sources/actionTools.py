#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ActionTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import maya.cmds as cmds
import os
import shutil
import time

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from utils import jsonHelper, publish, messageBox, sequenceplayer, animation, pose, namespace
from sources import assetTools
from widgets import imagesequence, myWidget


# reload(animation)


class ActionToolsUI(QtWidgets.QWidget):
    ThreadPool = QtCore.QThreadPool()
    TEMPDIR = "{}AssetsManagerTemp".format(cmds.internalVar(userTmpDir=True))
    MYPREFSDIR = cmds.internalVar(userPrefDir=True)
    # Result: u'C:/Users/asus/Documents/maya/2019/prefs/'
    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')

    def __init__(self):
        super(ActionToolsUI, self).__init__()
        cmds.selectPref(tso=1)
        self.actionPub = publish.Publish()
        self.ui = None
        self.isList = False
        self.__showedItemNum = 0
        self.__updatedNum = 0
        self.DEF_SPACING = 8
        self.DEFAULT_FPS = 30
        self.LOG = ""

        f = QtCore.QFile('%s/ui/actionTools.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()

        self.ROOT = "Y:/MCCProject"
        self.ACTION_PATH = self.ROOT + "/StudioLibrary_Ani"
        self._imageSequence = None
        self._current_fram = 0
        self.readSettings()

        self.option_expanded = True
        self.namespace_expanded = True
        self.blender_expanded = True
        self.other_expanded = True

        # self.init_ui_thread = myWidget.MyThread()
        # self.init_ui_thread.signal.connect(lambda: self.init_ui())
        # self.init_ui_thread.start()
        # self.init_ui_thread.finished.connect(lambda: self.listWidgetAddItems())

        # self._worker = myWidget.ImageWorker()
        # self._worker.setAutoDelete(False)
        # self._worker.signals.triggered.connect(self._thumbnailFromImage)
        # self._workerStarted = False

    def init_ui(self):
        self.regExp = QtCore.QRegExp('^\\w+$')
        self.validator = QtGui.QRegExpValidator(self.regExp, self)

        '''风格外观初设置'''
        self.get_proj()
        thumbSize, project, typ = self.readSettings()
        # print(thumbSize, project, typ)
        if thumbSize is not None:
            self.ui.itemSize_Slider.setValue(thumbSize)
        if project is not None:
            self.ui.proj_comb.setCurrentIndex(project)
        else:
            self.ui.proj_comb.setCurrentIndex(0)
        self.get_typ()
        if typ is not None and typ != -1:
            self.ui.type_listWgt.setCurrentRow(typ)
        else:
            self.ui.type_listWgt.setCurrentRow(0)

        '''左侧边栏'''
        self.ui.proj_comb.currentIndexChanged.connect(self.projChanged)
        # self.ui.type_listWgt = myWidget.TypeQListWiget()
        self.ui.type_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.type_listWgt.customContextMenuRequested.connect(self.show_menu_type)

        self.ui.type_listWgt.itemSelectionChanged.connect(self.typeChanged)

        self.ui.Favorites_listWgt = myWidget.FavoritesQListWiget(tab="Action")
        self.ui.type_splitter.addWidget(self.ui.Favorites_listWgt)
        self.ui.type_splitter.setSizes([500, 300])
        # self.ui.add_folder_Bttn.setIcon(QtGui.QIcon('%s/icon/folderPlus.png' % self.scriptsPath))
        # self.ui.add_folder_Bttn.clicked.connect(self._add_folder)
        # self.ui.add_tag_Bttn.setIcon(QtGui.QIcon('%s/icon/tagPlus.png' % self.scriptsPath))
        # self.ui.add_tag_Bttn.clicked.connect(self._add_folder)

        '''上侧小按钮栏'''
        self.get_viewThumbnail_bttn()
        self.ui.displayThumb_bttn.clicked.connect(self.viewThumbnailChanged)
        self.ui.itemSize_Slider.valueChanged.connect(self.itemSizeSliderChanged)
        self.ui.itemSize_Slider.setToolTip(u"%s" % self.ui.itemSize_Slider.value())
        self.ui.itemSize_Slider.sliderReleased.connect(self.itemSizeSliderReleased)
        self.ui.download_Bttn.setIcon(QtGui.QPixmap('%s/icon/download.png' % self.scriptsPath))
        # self.ui.download_Bttn.clicked.connect(self.download_asset)
        self.ui.refresh_Bttn.setIcon(QtGui.QPixmap('%s/icon/refresh.png' % self.scriptsPath))
        self.ui.refresh_Bttn.clicked.connect(self.refresh_asset)
        self.ui.key_line.returnPressed.connect(self.search_asset)
        self.ui.key_line.addAction(QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
                                   QtWidgets.QLineEdit.LeadingPosition)

        '''主界面栏'''
        self.ui.main_listWgt = myWidget.MainQListWidget(tab="Action")
        self.ui.verticalLayout_main.addWidget(self.ui.main_listWgt)

        self.ui.main_listWgt.itemSelectionChanged.connect(self.mainWightItemChanged)
        self.ui.main_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.main_listWgt.customContextMenuRequested.connect(self.show_menu)

        self.ui.mainWindow_splitter.setSizes([120, 500, 300])
        self.ui.mainWindow_splitter.setStretchFactor(0, False)
        self.ui.mainWindow_splitter.setStretchFactor(1, True)
        self.ui.mainWindow_splitter.setStretchFactor(2, False)

        '''右侧属性栏'''
        self.ui.attr_splitter.setSizes([330, 1])
        self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
        self.ui.favor_bttn.clicked.connect(self.addFavor)
        self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
        self.ui.tag_bttn.clicked.connect(self.addTag_UI)

        self.ui.PreviewLabel = myWidget.PreviewLabel(self.ui.frams_lineEdit)
        self.ui.verticalLayout_Preview.addWidget(self.ui.PreviewLabel)
        self.ui.PreviewLabel.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.PreviewLabel.customContextMenuRequested.connect(self.show_menu_preview)
        self.playerSet()

        self.ui.option_tbttn.clicked.connect(self.option_clicked)
        self.ui.apply_option_combox.addItems(['replace', 'replace all', 'insert', 'merge'])
        self.ui.pose_percent_frame.setVisible(False)
        self.ui.apply_option_frame.setVisible(False)
        self.ui.posePercentSlider.valueChanged.connect(self.posePercentSliderChanged)
        self.ui.posePercentLineEdit.editingFinished.connect(self.posePercentEditChanged)
        self.ui.posePercentLineEdit.setText("0")

        self.ui.namespace_tbttn.clicked.connect(self.namespace_clicked)
        self.getNamespace()
        self.ui.namespace_rBtn_01.toggled.connect(self.getNamespace)
        self.ui.namespace_rBtn_02.toggled.connect(self.getNamespace)
        self.ui.namespace_rBtn_03.toggled.connect(self.getNamespace)

        self.ui.blender_tbttn.clicked.connect(self.blender_clicked)

        self.ui.other_tbttn.clicked.connect(self.other_clicked)
        self.ui.copyKey_bttn.clicked.connect(self.copyKey)

        # self.ui.actionPublish_bttn.clicked.connect(self._saveAnim)
        # self.ui.actionPublish_bttn.setStyleSheet("QPushButton{background: #b0e600; color: #000000;}")

    def _blendEditChanged(self, *args):
        """ Triggered when the user changes the blend edit value."""
        blend = int(self.ui.blendEdit.text())
        self.item().loadFromCurrentValues(
            blend=blend,
            batchMode=False,
            showBlendMessage=True,
            clearSelection=False,
        )

    def projectSetting(self):
        data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % self.scriptsPath)
        return data

    def rememberSettings(self):
        """ 记忆窗口设置 """
        settings = QtCore.QSettings('Action', 'ActionSettings')
        settings.setValue('isList', self.isList)
        settings.setValue('thumbSize', self.ui.itemSize_Slider.value())
        settings.setValue('project', self.ui.proj_comb.currentIndex())
        settings.setValue('typ', self.ui.type_listWgt.currentRow())

    def readSettings(self):
        """ 读取QSettings数据 """
        settings = QtCore.QSettings('Action', 'ActionSettings')
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

    def set_ROOT(self, root):
        """ 设置ROOT """
        self.ROOT = root

    def get_proj(self):
        # print("update_project")
        self.ui.proj_comb.addItems(self.projectSetting()['projects'])
        return

    def get_typ(self):
        """ 根据选择的proj读取type文件夹 """
        # print("update_type")
        self.ui.type_listWgt.clear()
        project = self.ui.proj_comb.currentText()
        projcet_path = '{0}/{1}'.format(self.ACTION_PATH, project)
        directory = QtCore.QDir(projcet_path)
        type_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.Dirs,
                                        QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        # print(projcet_path)
        for i in type_list:
            item = QtWidgets.QListWidgetItem()
            item.setText(str(i))
            icon = QtGui.QIcon()
            pixmap = myWidget.Pixmap('%s/icon/folder.svg' % self.scriptsPath)
            pixmap.setColor(QtGui.QColor("#b3b3b3"))
            icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon)
            self.ui.type_listWgt.addItem(item)
        return type_list

    def projChanged(self):
        self.rememberSettings()
        self.get_typ()
        return str(self.ui.proj_comb.currentText())

    def typeChanged(self):
        # print(self.ui.type_listWgt.currentRow())
        self.rememberSettings()
        self.update_asset()
        return str(self.ui.type_listWgt.selectedItems()[0].text())

    def faveChanged(self):
        """ 切喜好 """
        if self.ui.Favorites_listWgt.currentRow() != -1:
            self.ui.type_listWgt.setCurrentRow(-1)
            if self.ui.Favorites_listWgt.currentRow() == 0:
                self.ui.main_listWgt.clear()
                data = self.ui.Favorites_listWgt.get_favor_items()
                self.listWidgetAddItems(data)
            else:
                self.ui.main_listWgt.clear()
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
            addFolder_action.setIcon(QtGui.QIcon("{}/icon/folderPlus.png".format(self.scriptsPath)))
            addFolder_action.triggered.connect(self._add_folder)

            menu.addAction(addFolder_action)

            menu.exec_(QtGui.QCursor.pos())
        return

    def _add_folder(self):
        """
        新建type文件夹
        """
        project = self.ui.proj_comb.currentText()
        path = '{0}/{1}'.format(self.ACTION_PATH, project)
        res = self.actionPub.create_new_folder(self, path)
        _item = QtWidgets.QListWidgetItem(res)
        self.ui.type_listWgt.addItem(_item)
        self.ui.type_listWgt.setCurrentItem(_item)

    def addFavor(self):
        """
        添加最爱
        :return:
        """
        currentSelected = self.ui.main_listWgt.selectedItems()
        if currentSelected:
            if not currentSelected[0].isFavor():
                currentSelected[0].setFavor(True)
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))
            else:
                currentSelected[0].setFavor(False)
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))

    def addTag_UI(self):
        """
        添加标签UI
        :return:
        """
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(300, 95)
        Dialog.setWindowTitle(u"Create Tag")

        label = QtWidgets.QLabel(Dialog)
        label.setText(u"新建一个标签或选择已有的标签：")

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

            currentSelected = self.ui.main_listWgt.selectedItems()
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

    def get_viewThumbnail_bttn(self):
        """
        displayThumb_bttn  的初显示状态
        """
        if self.isList:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
        else:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")

    def viewThumbnailChanged(self):
        """
        切换  缩略图/表单  显示
        """
        self.__showedItemNum = 0
        if self.isList:
            '''如果list则切换icon显示'''
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")
            self.isList = False
            self.ui.main_listWgt.setIsList(self.isList)
            self.ui.main_listWgt.setIconMode()
        else:
            '''否则切换list显示'''
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
            self.isList = True
            self.ui.main_listWgt.setIsList(self.isList)
            self.ui.main_listWgt.setListMode()
        self.rememberSettings()

    def itemSizeSliderChanged(self):
        print("itemSizeSlider Changed !")
        itemSize = self.ui.itemSize_Slider.value()
        if self.isList:
            return
        else:
            self.ui.main_listWgt.setItemSize(itemSize)
            self.ui.main_listWgt.setMode()

    def itemSizeSliderReleased(self):
        print("itemSizeSlider Released !")
        itemSize = self.ui.itemSize_Slider.value()
        self.ui.itemSize_Slider.setToolTip(u"%s" % itemSize)
        self.rememberSettings()

    def refresh_asset(self):
        self.listWidgetAddItems()

    def get_keywords(self):
        """
        :return: [] list of keyword
        """
        keywords = []
        kkk = self.ui.key_line.text()
        for key in kkk.split(","):
            keywords.append(key)
        return keywords

    def search_asset(self):
        """  """
        self.update_asset()

    def update_asset(self):
        """根据type，project，设置主面板item显示"""
        # print("update_scene_asset()")
        type, project, path = self.getTypeAndProject()
        # print(path)
        if os.path.exists(str(path)):
            self.updateScenethread = myWidget.MyThread()
            self.updateScenethread.signal.connect(lambda: self.listWidgetAddItems())
            self.infoMsg("info", "Loading...")
            self.updateScenethread.start()  # 不能在切换tab快速响应，卡到加载完成才会切换tab，未解决
        else:
            self.ui.main_listWgt.clear()

    def getItemsDict(self):
        """
        从当前面板路径获取字典
        :return:[{'role_name': xx,
                'project': xx,
                'type': xx,
                'zh_name': xx,
                'icon_path': xx}]
        """
        __items_dict = []
        type, project, path = self.getTypeAndProject()
        dir = QtCore.QDir(path)
        for role_name in dir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot):
            icon_path = "%s/%s/thumbnail.jpg" % (path, role_name)
            # print(icon_path)
            zh_name = self.get_CNname("%s/%s/pose.json" % (path, role_name))
            bbb = {'role_name': role_name, 'project': project, 'type': type,
                   'zh_name': zh_name, 'icon_path': icon_path}
            __items_dict.append(bbb)

        return __items_dict

    def listWidgetAddItems(self):
        self.ui.main_listWgt.clear()
        keyWords = self.get_keywords()[0]
        start_time = time.time()

        self.ui.main_listWgt.setItemsdict(self.getItemsDict())
        self.ui.main_listWgt.setIsList(self.isList)
        self.ui.main_listWgt.setItemSize(self.ui.itemSize_Slider.value())
        self.ui.main_listWgt.addItems(keyWords)
        self.ui.main_listWgt.setMode()

        end_time = time.time()
        self.infoMsg("info", "%s items" % (self.ui.main_listWgt.count()) +
                     '   Cost :  %.2f' % (end_time - start_time) + ' sec')

    def mainWightItemChanged(self):
        """
        改变item触发：改变标题显示，改变预览显示，改变选项
        :return:
        """
        # print("mainWightItemChanged")
        currentSelected = self.ui.main_listWgt.selectedItems()
        if currentSelected:
            self.ui.PreviewLabel.clear()
            self.ui.title_label.clear()
            self.ui.frams_lineEdit.clear()
            item_data = currentSelected[0].itemData()
            print(item_data['icon_path'])
            self.ui.title_label.setText(u"Name： " + item_data['role_name'] + u"\n中文名： " + item_data['zh_name'])
            if item_data['role_name'].endswith('.pose'):
                self.ui.PreviewLabel.setPreviewPixmap(item_data['icon_path'], "pose")
                self.ui.pose_percent_frame.setVisible(True)
                self.ui.apply_option_frame.setVisible(False)
                self.ui.action_apply_bttn.clicked.connect(self.applyPose)
            elif item_data['role_name'].endswith('.anim'):
                self.ui.PreviewLabel.setAnim(item_data['icon_path'], "action")
                anim = animation.Animation.fromPath(item_data['icon_path'].replace('/thumbnail.jpg', ''))
                self.ui.apply_option_lineEdit01.setText(str(anim.startFrame()))
                self.ui.apply_option_lineEdit02.setText(str(anim.endFrame()))
                self.ui.pose_percent_frame.setVisible(False)
                self.ui.apply_option_frame.setVisible(True)
                self.ui.action_apply_bttn.clicked.connect(self.applyAction)

            self.getNamespace()
            '''########## 设置喜好和标签 #################################################################'''
            if not currentSelected[0].isFavor():
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))
            else:
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))

            if not currentSelected[0].isTag():
                self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/unTag.png' % self.scriptsPath))
            else:
                self.ui.tag_bttn.setIcon(QtGui.QIcon('%s/icon/tag.png' % self.scriptsPath))

    def get_CNname(self, path):
        data = jsonHelper.readDictFromFile(path)
        try:
            return data['metadata']['description']
        except:
            return ""

    def _play(self, path):
        """ Start playing the image sequence movie."""
        movie = None
        if os.path.isfile(path) and path.lower().endswith(".gif"):
            pass
            # self.__playGif(path)
        elif os.path.isdir(path):
            movie = imagesequence.ImageSequence(path)
            movie.frameChanged.connect(self.__frameChanged)
            self._imageSequence = movie
        if movie:
            movie.start()

    def __frameChanged(self, frame=None):
        """ Triggered when the movie object updates to the given frame."""
        isAppRunning = bool(QtWidgets.QApplication.instance())
        if not isAppRunning:
            return
        if self._imageSequence is not None:
            pixmap = self._imageSequence.currentPixmap()
            fn = self._imageSequence.currentFrameNumber()
            fc = self._imageSequence.frameCount()
            try:
                self.ui.PreviewLabel.setPixmap(pixmap)
                self.ui.frams_lineEdit.setText(str(fn) + " / " + str(fc))
            except Exception as e:
                print(e)

    def getTypeAndProject(self):
        project = self.ui.proj_comb.currentText()
        try:
            type = self.ui.type_listWgt.selectedItems()[0].text()
        except:
            type = ""
        path = '%s/%s/%s' % (self.ACTION_PATH, project, type)
        return type, project, path

    def listWidgetAddMovItems(self, path):
        """
        将gif显示在Action预览面板
        """
        self.ui.PreviewLabel.clear()
        preview_dir = QtCore.QDir((path))
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
            self.player.movie.setFileName('%s/%s' % (path, i))
            self.player.total_frame = self.player.movie.frameCount()
            print("total_frame:", self.player.total_frame)
            # mov = QtGui.QMovie('%s/%s' % (path, i))
            # mov.start()

            # label.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            # label.setMovie(self.player.movie)
            # lay.addWidget(label)
            # self.ui.iconDisplay_listWgt.addItem(item)
            # self.ui.iconDisplay_listWgt.setItemWidget(item, widget2)
            # mov.stop()
            self.ui.PreviewLabel.setScaledContents(True)
            self.ui.PreviewLabel.setMovie(self.player.movie)
            self.player.play(100, self.ui.Play_toolBttn)

    def show_menu(self, point):
        """
        main_listWgt 右键菜单
        :param point:
        :return:
        """
        currentItem = self.ui.main_listWgt.itemAt(point)
        # currentItem = self.ui.main_listWgt.selectedItems()[0]
        menu = QtWidgets.QMenu(self.ui.main_listWgt)
        if currentItem is not None:
            show_action = QtWidgets.QAction('Show in Explorer', self)
            show_action.setIcon(QtGui.QIcon("{}/icon/folder_white.png".format(self.scriptsPath)))
            show_action.triggered.connect(self.openDir)
            menu.addAction(show_action)

            menu.addSeparator()

            apply_action = QtWidgets.QAction('Apply Action', self)
            apply_action.triggered.connect(self.applyAction)
            menu.addAction(apply_action)

            menu.addSeparator()

            asset_path = self.findLinkedAsset()
            for ass in asset_path:
                menu.addAction(self.add_action(ass))

            menu.exec_(QtGui.QCursor.pos())
        else:
            publish_action = QtWidgets.QAction(u'发布动作库', self)
            publish_action.setIcon(QtGui.QIcon("{}/icon/publish.png".format(self.scriptsPath)))
            publish_action.triggered.connect(self.actionPublish)

            refresh_action = QtWidgets.QAction(u'刷新', self)
            refresh_action.setIcon(QtGui.QIcon("{}/icon/refresh.png".format(self.scriptsPath)))
            refresh_action.triggered.connect(self.refresh_asset)

            menu.addAction(publish_action)
            menu.addSeparator()
            menu.addAction(refresh_action)

            menu.exec_(QtGui.QCursor.pos())
        return

    def add_action(self, path):
        """使用Java闭包，否则triggered.connect的action只会认到最后一个action"""
        action = QtWidgets.QAction(path, self)
        action.setIcon(QtGui.QIcon("{}/icon/link.png".format(self.scriptsPath)))
        action.setData(path)
        action.triggered.connect(lambda: self.createRef(path))
        return action

    def findLinkedAsset(self):
        currentSelected = self.ui.main_listWgt.selectedItems()
        if currentSelected:
            item_data = currentSelected[0].itemData()
            anim = animation.Animation.fromPath(item_data['icon_path'].replace('/thumbnail.jpg', ''))
            asset_path = anim.assetPath()
            return asset_path
            # project = asset_path.split("/")[2]
            # typ = asset_path.split("/")[4]
            # role = asset_path[0].split("/")[5]
            # settings = QtCore.QSettings('Assets', 'AssetsSettings')
            # settings.setValue('project', 3)
            # self.parent().parent().parent().setCurrentIndex(0)
            # self.ui.key_line.setText(role)

    def createRef(self, path):
        """
        创建Reference
        :return:
        """
        # print(path)
        try:
            nameSpace = path.rsplit("/", 1)[1].split(".ma")[0]
            cmds.file(path, reference=True, type='mayaAscii', ignoreVersion=True,
                      groupLocator=True, options='v=0;', mergeNamespacesOnClash=False, namespace=nameSpace)
        except Exception as e:
            cmds.warning(u"导入失败:%s" % e)

    def openDir(self):
        """ 右键打开文件夹 """
        currentSelected = self.ui.main_listWgt.selectedItems()
        item_data = currentSelected[0].itemData()
        folder_path = os.path.dirname(item_data['icon_path'].replace('thumbnail.jpg', ''))
        folder_info = QtCore.QFileInfo(folder_path)
        if folder_info.exists():
            QtGui.QDesktopServices.openUrl(folder_path)
        else:
            cmds.warning('Can not find {0}'.format(folder_path))

    @staticmethod
    def actionPublish():
        from tools_publish.PublishTools import PublishTool
        PublishTool.showWindow(3)

    def _saveAnim(self):
        controls = cmds.ls(sl=1)
        animation.saveAnim(path="F:/rrr/eee.anim",
                           objects=controls,
                           time=(1, 20),
                           metadata={'description': 'Example anim'})

    def clearWidgetItems(self):
        self.ui.PreviewLabel.clear()
        self.mov.stop()

    def addFavor(self):
        """
        添加最爱
        :return:
        """
        currentSelected = self.ui.main_listWgt.selectedItems()
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

            currentSelected = self.ui.main_listWgt.selectedItems()
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

    def playerSet(self):
        player = sequenceplayer.Player()
        player.setPlayButtonState(self.ui.Play_toolBttn)
        '''播放'''
        self.ui.Play_toolBttn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        self.ui.Play_toolBttn.clicked.connect(lambda: player._play(self.ui.Play_toolBttn, self._imageSequence))
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
        '''显示帧数'''
        # self.setFrame()

    def show_menu_preview(self):
        """
        预览窗口的右键菜单
        :return:
        """
        actionPath = r'%s\ActionTools\ActionGif' % self.TEMPDIR
        pop = QtWidgets.QMenu(self.ui.PreviewLabel)
        shot = QtWidgets.QAction('Open Local SnapShot', self)
        pop.addAction(shot)
        shot.triggered.connect(lambda: os.startfile(actionPath))
        pop.exec_(QtGui.QCursor.pos())

    def iconRender(self):
        """
        渲染触发：录制gif并展示在预览窗口
        """
        # sys.path.append('%s/imageio'%self.scriptsPath.replace("AssetsManagerForMaya","lib"))
        # import imageio
        # sys.path.append(self.scriptsPath.replace("AssetsManagerForMaya", "lib"))
        # import imageio
        actionPath = r'%s\ActionTools\ActionGif' % self.TEMPDIR
        # print(actionPath)
        self.actionPub.makePath(actionPath)
        image_list = [actionPath + '/' + img for img in os.listdir(actionPath)]
        if image_list:
            for i in image_list:
                os.remove(i)
        cmds.playblast(percent=100, quality=100, widthHeight=[160, 160], format='image', compression='jpg',
                       viewer=False, filename='%s/ActionGif' % actionPath)
        # os.system(r"%s/jpg2gif.exe"%self.scriptsPath) #封装成exe可以，但是不能传参
        os.system("python %s/sources/jpg2gif.py" % self.scriptsPath)
        # import jpg2gif
        # jpg2gif.aaaa()
        # path = r'%sActionGif' % MYPREFSDIR
        # path = path.replace('/','\\')
        # image_list = [path + '\\' + img for img in os.listdir(path)]
        # frames = []
        # for image in image_list:
        #     print(image)
        #     frames.append(imageio.imread(image))
        # imageio.mimsave("%sActionGif.gif"%MYPREFSDIR , frames, 'GIF', duration=0.033333333333333)
        # cmds.playblast(percent=100, quality=100, widthHeight=[160, 160], format='avi', viewer=False,filename=MYPREFSDIR + 'ActionGif')
        # cmds.playblast(percent=100, quality=100, widthHeight=[160, 160], format='qt', compression='H.264', viewer=False,
        #                filename=MYPREFSDIR + 'ActionGif')

        # cdec = "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        # ffmpeg = "%s/ffmpeg-N-102494-g2899fb61d2-win64-gpl-shared/bin/ffmpeg" %self.scriptsPath.replace("AssetsManagerForMaya","Tools")
        # os.system(("{2} -y -r 30 -i {0}ActionGif.avi -s 160x160 -vf {1} {0}ActionGif.gif").format(self.MYPREFSDIR, cdec, ffmpeg))
        self.listWidgetAddMovItems(r'%s\ActionTools' % MYPREFSDIR)

    # def __actionPublish(self):
    #     log = "log:"
    #     if len(cmds.ls('*_*_AST', type='transform')) == 1 or 2:
    #         projectName = cmds.ls('*:*_*_AST', type='transform')[0].split(':')[1].split('_')[-2]
    #         characterName = cmds.ls('*:*_*_AST', type='transform')[0].split(':')[1].split('_')[-3]
    #         if projectName not in self.projectSetting()['projects']:
    #             cmds.warning('Check your projects name!!!')
    #             return
    #         publishType = self.ui.publishType_comb.currentText()
    #         path = str('%s/%s/%s/%s/%s/Action' % (self.ROOT,
    #                                               projectName,
    #                                               self.projectSetting()['assetFolder'],
    #                                               publishType,
    #                                               characterName))
    #         actionName = self.ui.simpleRig_name_line.text()
    #         self.actionPub.makePath(path)
    #     else:
    #         cmds.warning('Can not find *_*_AST, or more than one *_*_AST, please check!!!')
    #         return
    #     self.virusCheck()
    #     '''保存ma'''
    #     self.actionPub.makePath(str('%s/%s' % (path, self.projectSetting()['actionFileFolder'])))
    #     try:
    #         self.saveToServer(path,
    #                           self.projectSetting()['actionFileFolder'],
    #                           characterName,
    #                           actionName,
    #                           self.projectSetting()['mayaFormat'])
    #         log += u"> {}.ma已保存成功".format(actionName)
    #     except Exception as e:
    #         log += u"ma保存失败，请检查文件:%s" % e
    #     self.fbxExport(path, characterName, actionName)
    #     log += u"\n> FBX发布成功"
    #     try:
    #         self.iconPublish(path, characterName)
    #         log += u"\n> icon发布成功"
    #     except Exception as e:
    #         log += u"\n> icon发布失败:%s" % e
    #     msg = QtWidgets.QMessageBox()
    #     msg.setText(u"提示：")
    #     msg.setInformativeText(u"Action发布成功!\n查看log获取更多细节?")
    #     msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
    #     msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
    #     msg.setDetailedText(log)
    #     msg.exec_()

    @staticmethod
    def virusCheck():
        script_node = cmds.ls(type='script')
        virus_list = []
        for i in script_node:
            if i.find('_gene') != -1:
                virus_list.append(i)

        if virus_list:
            try:
                cmds.delete('*vaccine_gene*')
                cmds.delete('*breed_gene*')
            except Exception as e:
                cmds.warning('Virus Kill Failed!')
                return

    def posePercentSliderChanged(self):
        """
        改变pose合成比例
        :return:
        """
        value = self.ui.posePercentSlider.value()
        self.ui.posePercentLineEdit.setText(str(value))
        self.applyPose()

    def posePercentEditChanged(self):
        value = self.ui.posePercentLineEdit.text()
        self.ui.posePercentSlider.setValue(int(value))
        self.applyPose()

    def iconPublish(self, path, characterName):
        """
        发布icon，（没有录制不发布还未成功）
        """
        if self.ui.PreviewLabel.movie() is not None:
            actionName = self.ui.simpleRig_name_line.text()
            orgPath = r'%s/ActionTools/ActionGif.gif' % os.environ.get('TEMP')
            org_rename_path = r'%s/ActionTools/%s_%s.gif' % (os.environ.get('TEMP'), characterName, actionName)
            newPath = path + '/Preview/'
            if os.path.exists(orgPath):
                shutil.copy(orgPath, org_rename_path)
                shutil.copy(org_rename_path, newPath)
                print(u'拷贝ActionGif成功')
                # os.rename('%s/ActionGif.gif'%(newPath),'%s/%s_%s.gif'%(newPath,characterName,actionName))
                self.LOG = self.LOG + u"\n> icon发布成功"
            else:
                self.LOG = self.LOG + u"\n> Action.gif 不存在！icon发布失败"
        else:
            self.LOG = self.LOG + u"\n> Action.gif 不存在！icon发布失败"

    def fbxExport(self, path, characterName, actionName):
        minTime = cmds.playbackOptions(query=True, minTime=True)
        maxTime = cmds.playbackOptions(query=True, maxTime=True)
        cmds.select(clear=True)
        cmds.select('*:Geometry')
        cmds.select('*:DeformationSystem', add=True)
        fbxFolderPath = '%s/%s' % (path, 'ActionFBX')
        self.actionPub.makePath(fbxFolderPath)
        # self.actionPub.createHistory(fbxFolderPath)
        fbxPath = '%s/%s_%s.fbx' % (fbxFolderPath, characterName, actionName)
        self.actionPub.exportFBX(True, minTime, maxTime, fbxPath)
        # QtWidgets.QMessageBox.information(self, '提示', 'FBX发布成功')

    # def saveToServer(self, path, type, characterName, suffix, mayaformat):
    #     """ 保存maya """
    #     mayaPath = '%s/%s/maya_file.ma' % (path, type, characterName, suffix, mayaformat)
    #     if os.path.isfile(mayaPath):
    #         reply = QtWidgets.QMessageBox.question(self, '提示', '动作已存在，确定要替换吗？',
    #                                                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    #         if reply == QtWidgets.QMessageBox.Yes:
    #             cmds.file(rename='%s/%s/%s_%s.%s' % (path, type, characterName, suffix, mayaformat))
    #             cmds.file(save=True, type='mayaAscii')
    #         else:
    #             return
    # QtWidgets.QMessageBox.information(self, '提示', '动作发布成功')

    def option_clicked(self):
        if self.option_expanded:
            self.ui.option_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.options_frame.setVisible(False)
            self.option_expanded = False
        else:
            self.ui.option_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.options_frame.setVisible(True)
            self.option_expanded = True

    def namespace_clicked(self):
        if self.namespace_expanded:
            self.ui.namespace_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.namespace_frame_2.setVisible(False)
            self.namespace_expanded = False
        else:
            self.ui.namespace_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.namespace_frame_2.setVisible(True)
            self.namespace_expanded = True

    def blender_clicked(self):
        if self.blender_expanded:
            self.ui.blender_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.pose_percent_frame_2.setVisible(False)
            self.blender_expanded = False
        else:
            self.ui.blender_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.pose_percent_frame_2.setVisible(True)
            self.blender_expanded = True

    def other_clicked(self):
        if self.other_expanded:
            self.ui.other_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.other_frame.setVisible(False)
            self.other_expanded = False
        else:
            self.ui.other_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.other_frame.setVisible(True)
            self.other_expanded = True

    def getNamespaceFromFile(self):
        namespaces = []
        currentSelected = self.ui.main_listWgt.selectedItems()
        if currentSelected:
            item_data = currentSelected[0].itemData()
            anim = animation.Animation.fromPath(item_data['icon_path'].replace('/thumbnail.jpg', ''))
            namespaces += anim.namespace()
            return namespaces

    def getNamespace(self):
        _namespaces = []
        self.ui.reference_combox.clear()
        _type = self.ui.namespace_bttnGroup.checkedButton().text()
        if _type == "From file":
            _namespaces = self.getNamespaceFromFile()
            print(_namespaces)
        elif _type == "From selection":
            _namespaces = namespace.getFromSelection()
        elif _type == "Use custom":
            _namespaces = namespace.getAll()

        self.ui.reference_combox.addItems(_namespaces)
        return _namespaces

    def applyAction(self):
        """
        应用动作
        :return:
        """
        select_controls = cmds.ls(sl=1) or []

        _item = self.ui.main_listWgt.selectedItems()
        if not _item:
            return
        path = _item[0].itemData()['icon_path'].replace('/thumbnail.jpg', '')
        option = self.ui.apply_option_combox.currentText()
        namespaces = self.ui.reference_combox.currentText()
        isConnect = self.ui.connect_cBox.isChecked()
        isCurrentTime = self.ui.currentTime_cBox.isChecked()
        start = int(self.ui.apply_option_lineEdit01.text())
        end = int(self.ui.apply_option_lineEdit02.text())
        anim = animation.Animation.fromPath(path)
        anim.load(objects=select_controls,
                  namespaces=[namespaces],
                  option=option,
                  startFrame=None,  # cmds.currentTime(query=True),
                  sourceTime=(start, end),
                  connect=isConnect,
                  currentTime=isCurrentTime)

    def applyPose(self):
        """
        应用pose
        :return:
        """
        controls = []
        select_controls = cmds.ls(sl=1, type='transform')
        for select_control in select_controls:
            if cmds.nodeType(cmds.listRelatives(select_control, shapes=True)) == 'nurbsCurve':
                controls.append(select_control)
        blend_percent = self.ui.posePercentSlider.value()
        _item = self.ui.main_listWgt.selectedItems()
        path = _item[0].itemData()["icon_path"].replace('/thumbnail.jpg', '/pose.json')
        pose.loadPose(path, objects=controls, blend=blend_percent)

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

    def infoMsg(self, icon, text):
        """
        消息栏
        :param icon:
        :param text:
        """
        messageBox.show_msg(self.ui.msg_icon_label, icon,
                            self.ui.msg_label, text)
