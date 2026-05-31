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
from PySide2 import QtUiTools
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

from config import projectSetting, SMConfig
from utils import jsonHelper, publish, messageBox
from utils.am_database import AssetDatabaseManager
from widgets import am_main_optimized, faverWidget, previewWidget, am_pixmap


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

    def __init__(self, user="", password=""):
        super(AssetToolsUI, self).__init__()

        self.mayaMainWindow = maya_main_window()
        self.mayaMainWindow.setAcceptDrops(True)

        self.host = SMConfig().getPrefsValue("General/ip", "10.0.203.34")
        self.user = user
        self.password = password

        # 加载 UI
        f = QtCore.QFile('%s/ui/assetTools.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()

        self.Pub = publish.Publish()
        self.tab = "Assets"
        self.isList = False
        self.isAction = False
        self.isAttributeShow = True
        self.currentAssetData = {}
        self.ROOT = "Y:/MCCProject"
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

    def init_ui(self):
        """初始化 UI"""
        self.firstView()

        # 左侧边栏
        self.ui.project_comb.currentIndexChanged.connect(self.projectChanged)
        self.ui.type_listWgt.itemSelectionChanged.connect(self.typeChanged)
        self.ui.type_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.type_listWgt.customContextMenuRequested.connect(self.show_menu_type)

        self.ui.Favorites_listWgt = faverWidget.FavoritesQListWiget(tab="Asset")
        self.ui.type_splitter.addWidget(self.ui.Favorites_listWgt)
        self.ui.type_splitter.setSizes([300, 500])
        self.ui.Favorites_listWgt.itemSelectionChanged.connect(self.faveChanged)

        # 上侧工具栏
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
        self.ui.key_line.addAction(
            QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
            QtWidgets.QLineEdit.LeadingPosition
        )

        # 主界面 - 使用新的高性能组件
        self.ui_main_wgt = am_main_optimized.MainStackedWidget(
            db=self.ui.project_comb.currentText(),
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
        self.ui.verticalLayout_3.addWidget(self.ui_main_wgt)

        # 设置分割器
        self.ui.mainWindow_splitter.setSizes([120, 500, 300])
        self.ui.mainWindow_splitter.setStretchFactor(0, False)
        self.ui.mainWindow_splitter.setStretchFactor(1, True)
        self.ui.mainWindow_splitter.setStretchFactor(2, False)

        # 右侧属性栏
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
        """切换文件类型面板"""
        if self.file_type_expanded:
            self.ui.file_type_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.file_type_frame.setVisible(False)
            self.file_type_expanded = False
        else:
            self.ui.file_type_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.file_type_frame.setVisible(True)
            self.file_type_expanded = True

    def switch_clicked(self):
        """切换引用面板"""
        if self.switch_expanded:
            self.ui.switch_tbttn.setArrowType(QtCore.Qt.RightArrow)
            self.ui.switch_frame.setVisible(False)
            self.switch_expanded = False
        else:
            self.ui.switch_tbttn.setArrowType(QtCore.Qt.DownArrow)
            self.ui.switch_frame.setVisible(True)
            self.switch_expanded = True

    def rememberSettings(self):
        """保存设置"""
        settings = QtCore.QSettings('Assets', 'AssetsSettings')
        settings.setValue('isList', self.isList)
        settings.setValue('thumbSize', self.ui.itemSize_Slider.value())
        settings.setValue('project', self.ui.project_comb.currentIndex())
        settings.setValue('typ', self.ui.type_listWgt.currentRow())

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
        self.get_type()

        thumbSize, project, typ = self.readSettings()
        if thumbSize is not None:
            self.ui.itemSize_Slider.setValue(int(thumbSize))
        if project is not None:
            self.ui.project_comb.setCurrentIndex(int(project))
        else:
            self.ui.project_comb.setCurrentIndex(0)
        if typ is not None and typ != -1:
            self.ui.type_listWgt.setCurrentRow(int(typ))
        else:
            self.ui.type_listWgt.setCurrentRow(0)

    def get_project(self):
        """获取项目列表"""
        self.ui.project_comb.addItems(projectSetting()['projects'])

    def get_type(self):
        """获取类型列表"""
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

    def currentProject(self):
        """获取当前项目"""
        return str(self.ui.project_comb.currentText())

    def currentType(self):
        """获取当前类型"""
        items = self.ui.type_listWgt.selectedItems()
        return str(items[0].text()) if items else ""

    @staticmethod
    def currentDate():
        """获取当前日期"""
        return time.strftime('%Y%m%d', time.localtime())

    def currentAsset(self):
        """获取当前资产名"""
        return self.ui_main_wgt.currentAsset()

    def projectChanged(self):
        """项目改变"""
        self.rememberSettings()
        self._asset_cache = []  # 清空缓存
        self.show_asset()

    def typeChanged(self):
        """类型改变"""
        if self.ui.type_listWgt.currentRow() != -1:
            self.rememberSettings()
            self.show_asset()
            self.ui.Favorites_listWgt.setCurrentRow(-1)

    def faveChanged(self):
        """收藏改变"""
        if self.ui.Favorites_listWgt.currentRow() != -1:
            self.ui.type_listWgt.setCurrentRow(-1)
            self.ui_main_wgt.clear()
            if self.ui.Favorites_listWgt.currentRow() == 0:
                data = self.ui.Favorites_listWgt.get_favor_items()
            else:
                select = self.ui.Favorites_listWgt.selectedItems()[0].text()
                data = self.ui.Favorites_listWgt.get_tag_items(select)
            self.ui_main_wgt.setItemsList(data)
            self.ui_main_wgt.addItems(self.get_keywords())

    # ============ 数据查询优化 ============

    def show_asset(self, data=None):
        """显示资产 - 使用新的查询方式"""
        self.ui_main_wgt.clear()
        self._asset_cache = []

        # 显示加载提示
        self.infoMsg("info", "Loading...")

        # 使用优化的数据库查询
        project = self.currentProject()
        asset_type = self.currentType()
        keywords = self.get_keywords()

        if not project or not asset_type:
            return

        self._db_manager.queryAssets(project, asset_type, keywords)

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
        self.ui_main_wgt.resizeItem()
        self.infoMsg("info", f"加载到{total}个资产")

    # ============ 其他方法保持不变 ============

    def get_keywords(self):
        """获取关键词"""
        return [self.ui.key_line.text().strip()]

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
        """获取面板数据"""
        __project = str(self.ui.project_comb.currentText())
        __type = str(self.ui.type_listWgt.selectedItems()[0].text())
        __path = '%s/%s/%s/%s' % (
            self.ROOT, __project,
            projectSetting()['assetFolder'], __type
        )
        return __project, __type, __path

    def getCurrentItemsData(self):
        """获取当前选中项数据"""
        __item = self.ui_main_wgt.selectedItems()
        __fileType = self.ui.fileType_bttnGroup.checkedButton().text()
        __folder = self.__fileTypeFolderDict[__fileType]
        if not __item:
            return None
        return __item, __fileType, __folder

    def mainWightItemChanged(self):
        """主面板选择项改变"""
        currentSelected = self.ui_main_wgt.selectedItems()
        self.ui.preview.clear()

        if currentSelected:
            # 启用/禁用按钮
            rBttn_dict = {
                'mod': self.ui.mod_rBttn,
                'hi_rig': self.ui.hiRig_rBttn,
                'low_rig': self.ui.lowRig_rBttn,
                'all_rig': self.ui.allRig_rBttn,
                'render': self.ui.render_rBttn,
                'xgen': self.ui.xgen_rBttn,
                'AD': self.ui.ad_rBttn,
                'OAT': self.ui.oat_rBttn
            }

            for btn in rBttn_dict.values():
                btn.setEnabled(True)

            # 获取 item 数据
            if isinstance(currentSelected[0], QtWidgets.QTableWidgetItem):
                item_data = currentSelected[0].itemData()
            else:
                item_data = currentSelected[0].itemData()

            if item_data:
                self.ui.preview.setTitle(item_data[1], item_data[2])

                if not self.isAction:
                    self.ui.preview.setPreviewPixmap(item_data[7], "asset_ch")

                # 检查文件是否存在
                for ty, btn in rBttn_dict.items():
                    file_path = self.detailPath().get(ty, "")
                    if file_path and not QtCore.QFileInfo(file_path).exists():
                        btn.setEnabled(False)

                # 设置收藏和标签按钮状态
                # ... (保持原有逻辑)

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
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
        else:
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")

    def viewModeChanged(self):
        """切换视图模式"""
        keyWords = self.get_keywords()
        itemSize = self.ui.itemSize_Slider.value()

        if self.isList:
            # 切换到缩略图模式
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_list.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("表单显示")
            self.isList = False
            self.ui_main_wgt.setIsList(False)
            self.ui_main_wgt.setIconMode(itemSize, keyWords)
        else:
            # 切换到列表模式
            self.ui.displayThumb_bttn.setIcon(QtGui.QIcon('%s/icon/display_icon.png' % self.scriptsPath))
            self.ui.displayThumb_bttn.setToolTip("缩略图显示")
            self.isList = True
            self.ui_main_wgt.setIsList(True)
            self.ui_main_wgt.setListMode(keyWords)

        self.rememberSettings()

    def itemSizeSliderChanged(self):
        """滑块值改变"""
        itemSize = self.ui.itemSize_Slider.value()
        if self.isList:
            return
        else:
            self.ui_main_wgt.setItemSize(itemSize)
            self.ui_main_wgt.resizeItem()

    def itemSizeSliderReleased(self):
        """滑块释放"""
        itemSize = self.ui.itemSize_Slider.value()
        self.ui.itemSize_Slider.setToolTip(u"%s" % itemSize)
        self.rememberSettings()

    # ============ 右键菜单 ============

    def show_menu_type(self, point):
        """类型列表右键菜单"""
        currentItem = self.ui.type_listWgt.itemAt(point)
        menu = QtWidgets.QMenu(self.ui.type_listWgt)
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
        """添加文件夹"""
        project = self.ui.project_comb.currentText()
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
        """添加收藏"""
        currentSelected = self.ui_main_wgt.selectedItems()
        if currentSelected:
            # 获取实际的 item（ListItemOptimized 或 TableItem）
            item = currentSelected[0]
            if not item.isFavor():
                item.setFavor(True)
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/star.png' % self.scriptsPath))
            else:
                item.setFavor(False)
                self.ui.favor_bttn.setIcon(QtGui.QIcon('%s/icon/unStar.png' % self.scriptsPath))

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
            if lineEdit.text():
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

        bttnBox.accepted.connect(_addTag)
        bttnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()

    def backToMainWgt(self):
        """返回主面板"""
        self.ui.preview.clear()
        self.ui.preview.playerEnabled(False)
        self.isAction = False
        self.refresh_asset()
        self.ui.back_bttn.setEnabled(False)
        self.ui.itemSize_Slider.setEnabled(True)

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
        result = QtWidgets.QMessageBox.warning(
            self, u"警告",
            u"删除数据表的操作是不可逆的，但服务器文件夹还在，确定要删除吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if result == QtWidgets.QMessageBox.Yes:
            self.del_asset(self.currentProject(), self.currentAsset())
            self.show_asset()

    def del_asset(self, db, asset_name):
        """删除资产"""
        import psycopg2
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
        """添加资产 UI"""
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(300, 195)
        Dialog.setWindowTitle(u"Add Asset")
        font = QtGui.QFont("Microsoft YaHei UI", 10)
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
        messageBox.show_msg(self.ui.msg_icon_label, icon,
                           self.ui.msg_label, text)
