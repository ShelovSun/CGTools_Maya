#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ShotsManagerMaya Created: 19/10/2020 by Sunxh<175702994@qq.com>
# log:大改QT


import maya.cmds as cmds
import os
import sys
from functools import partial

import psycopg2
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from utils import jsonHelper, publish, sequenceplayer, animation, pose, namespace
from widgets import myWidget

from config import projectSetting


class ShotsManagerMayaUI(QtWidgets.QMainWindow):
    tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
    # stages = ["ANI/AniFile", "SIM/SimABC", "REN/RenFile"]
    stages = ["ANI", "SIM", "REN"]

    def __init__(self, isSQL=True,
                 ROOT="Y:/MCCProject",
                 user="",
                 password=""):
        super(ShotsManagerMayaUI, self).__init__()
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')
        self.SYSTEMP = os.environ['TEMP'].replace('\\', '/') + '/'
        self.isSQL = isSQL
        self.host = projectSetting()["host"]
        self.user = user
        self.password = password
        self.Pub = publish.Publish()
        self.camera_name = 'camera*'
        self.camera_file_name = "Camera"
        self.assetList = []
        self.shot_list = []
        self.ui = None

        self.option_expanded = True
        self.namespace_expanded = True
        self.blender_expanded = True

        self.RootPath = self.projectSetting()['rootPath']
        self.sortReverse = True

        self.init_UI()

    def init_UI(self):
        ui = QtCore.QFile('%s/ui/ShotsManagerForMaya.ui' % self.scriptsPath)
        ui.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui)
        ui.close()
        self.setCentralWidget(self.ui)
        project, eps, sort = self.readSettings()
        # print(eps)
        self.getProject()

        try:
            self.ui.Project_ComboBox.setCurrentIndex(project)
        except:
            self.ui.Project_ComboBox.setCurrentIndex(0)
        if sort == "false":
            self.sortReverse = False
        self.get_database()
        self.getShot()
        # try:
        #     self.findIdea(eps)
        # except:
        #     self.ui.ani_idea_listWgt.setCurrentRow(0)
        # self.getStage()
        # self.getStyleSheet()

        '''上侧栏'''
        self.ui.Project_ComboBox.currentIndexChanged.connect(self.changeProject)
        self.ui.openFloder_btn.setIcon(QtGui.QIcon('%s/icon/folder_open.png' % self.scriptsPath))
        self.ui.openFloder_btn.clicked.connect(self.openFolder)
        # self.ui.setting_bttn.setIcon(QtGui.QIcon('%s/icon/setting.png' % self.scriptsPath))
        # self.ui.setting_bttn.clicked.connect(self.toolSetting_UI)
        # print("###########", self.ui.ani_idea_listWgt.currentItem().text())
        self.getPath()

        '''主界面栏'''
        self.ui.main_splitter.setSizes([300, 200, 300])
        self.ui.main_splitter.setStretchFactor(0, True)
        self.ui.main_splitter.setStretchFactor(1, True)
        self.ui.main_splitter.setStretchFactor(2, False)
        self.ui.shot_tableWgt.setColumnWidth(0, 65)
        self.ui.shot_tableWgt.setColumnWidth(1, 200)
        self.ui.shot_tableWgt.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.ui.shot_tableWgt.setColumnWidth(2, 180)
        self.getFile()
        self.ui.sort_bttn.setIcon(QtGui.QIcon('%s/icon/sort.png' % self.scriptsPath))
        self.ui.sort_bttn.clicked.connect(self.changeIdeaSort)
        self.ui.key_line.textChanged.connect(self.getIdea_TW)
        self.ui.key_line.addAction(QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
                                   QtWidgets.QLineEdit.LeadingPosition)
        self.ui.shot_tableWgt.itemSelectionChanged.connect(self.changeIdea)
        # self.ui.ani_idea_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.ui.ani_idea_listWgt.customContextMenuRequested.connect(self.show_menu_ani_idea_listWgt)
        # self.ui.stages_listWgt.currentItemChanged.connect(self.changeStage)
        # self.ui.ani_shot_listWgt.currentItemChanged.connect(self.changeShot)
        # self.ui.aniAST_listWgt.currentItemChanged.connect(self.changeFile)
        self.ui.aniAST_listWgt.itemSelectionChanged.connect(self.changeFile)
        self.ui.aniAST_listWgt.itemDoubleClicked.connect(self.openFile)
        self.ui.aniAST_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.aniAST_listWgt.customContextMenuRequested.connect(self.show_menu_aniAST_listWgt)

        '''右侧属性栏'''
        self.ui.Attr_splitter.setSizes([500, 500])
        self.ui.PreviewLabel = myWidget.PreviewLabel(self.ui.frams_lineEdit)
        self.ui.verticalLayout_Preview.addWidget(self.ui.PreviewLabel)
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

        '''下侧栏'''
        self.ui.autoName_bttn.clicked.connect(self.autoName)
        self.ui.add_shot_bttn.clicked.connect(self.addShot)
        # self.ui.add_version_bttn.clicked.connect(self.addVersion)
        self.ui.publishType_comb_ac.addItems(["Animation", "Pose"])
        self.ui.publishType_comb_ac.currentIndexChanged.connect(self.change_publishType)
        self.ui.Publish_bttn.clicked.connect(self.aniPublish)
        # self.ui.Publish_bttn.setStyleSheet("QPushButton{background: #00e6cf; color: #000000;}")

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

    def getStyleSheet(self):
        style_sheet_path = '%s/qss/dark.qss' % self.scriptsPath
        with open(style_sheet_path) as (file):
            str = file.read()
        self.setStyleSheet(str)

    @staticmethod
    def readSettings():
        settings = QtCore.QSettings('Ani_Tools', 'Ani_Tools_Settings')

        project = settings.value('project')
        eps = settings.value('eps')
        sort = settings.value('sort')

        return project, eps, sort

    def rememberSettings(self):
        settings = QtCore.QSettings('Ani_Tools', 'Ani_Tools_Settings')
        settings.setValue('project', self.ui.Project_ComboBox.currentIndex())
        if self.ui.shot_tableWgt.selectedItems():
            _eps = self.ui.shot_tableWgt.selectedItems()[1].text()
        settings.setValue('eps', _eps)
        settings.setValue('sort', self.sortReverse)

    def findIdea(self, tex):
        """
        根据创意名选中创意，并滚动条定位到创意
        :param tex: 创意全名
        :return:
        """
        for i in range(0, self.ui.ani_idea_listWgt.count()):
            if self.ui.ani_idea_listWgt.item(i).text() == tex:
                self.ui.ani_idea_listWgt.item(i).setSelected(True)
                self.ui.ani_idea_listWgt.scrollToItem(self.ui.ani_idea_listWgt.item(i))
                return

    def projectSetting(self):
        data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % self.scriptsPath)
        return data

    def toolSetting_UI(self):
        Dialog = QtWidgets.QDialog(self)
        Dialog.resize(390, 95)
        Dialog.setWindowTitle(u"Enter Super User Password")
        font = QtGui.QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        label = QtWidgets.QLabel(Dialog)
        label.setText(u"*请输入管理员密码以获取修改权限：")
        label.setFont(font)
        label2 = QtWidgets.QLabel(Dialog)
        label2.setText(u"Password")
        label2.setFont(font)
        password_lineEdit = QtWidgets.QLineEdit(Dialog)
        password_lineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        bttnBox = QtWidgets.QDialogButtonBox(Dialog)
        bttnBox.setOrientation(QtCore.Qt.Horizontal)
        bttnBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok)
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 0, 1, 2)
        lay.addWidget(label2, 1, 0, 1, 1)
        lay.addWidget(password_lineEdit, 1, 1, 1, 1)
        lay.addWidget(bttnBox, 2, 1, 1, 1)
        bttnBox.accepted.connect(self.toolSetting)
        bttnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()

    def toolSetting(self):
        password = self.password_lineEdit.text()
        jsonPath = '%s/config/projectSetting.json' % self.scriptsPath
        if password == "999999":
            if os.path.isfile(jsonPath):
                os.startfile(jsonPath)
            else:
                print(u"没有找到设置文件")
        else:
            QtWidgets.QMessageBox.warning(self, u'提示', u'密码错误')

    def _get_current_data(self):
        """
        得到面板信息
        :return: current_project, current_idea, current_stage
        """
        current_project = str(self.ui.Project_ComboBox.currentText())

        if self.ui.shot_tableWgt.selectedItems():
            current_date = str(self.ui.shot_tableWgt.selectedItems()[0].text())
            current_idea = str(self.ui.shot_tableWgt.selectedItems()[1].text())
            current_idea_zh = self.ui.shot_tableWgt.selectedItems()[2].text()
        # elif self.ui.ani_idea_listWgt.selectedItems():
        #     current_idea = str(self.ui.ani_idea_listWgt.selectedItems()[0].text().split("   /   ")[0])
        #     current_idea_zh = self.ui.ani_idea_listWgt.selectedItems()[0].text().split("   /   ")[1]
        else:
            current_date = "None"
            current_idea = "None"
            current_idea_zh = "None"
        current_stage = self.ui.task_tab.tabText(self.ui.task_tab.currentIndex())
        if current_stage == "动画":
            current_stage = "ANI/AniFile"
        elif current_stage == "解算":
            current_stage = "SIM/SimABC"
        else:
            current_stage = "REN/RenFile"
        path = self.ui.aniPath_label.text()

        return current_project, current_date, current_idea, current_idea_zh, current_stage, path

    def getProject(self):
        self.ui.Project_ComboBox.addItems(self.projectSetting()['projects'])

    def getShot(self):
        """根据项目从数据库获得集数显示"""
        keyword = self.ui.key_line.text()
        self.ui.shot_tableWgt.clearContents()
        data = self.shot_list
        row = 0
        for i in data:
            if i[1].lower().find(keyword.lower()) != -1 or (i[2] and i[2].find(keyword) != -1):
                self.ui.shot_tableWgt.insertRow(row)
                _item_date = QtWidgets.QTableWidgetItem(str(i[0]))
                _item_name = QtWidgets.QTableWidgetItem(str(i[1]))
                _item_ZhName = QtWidgets.QTableWidgetItem(str(i[2]))
                self.ui.shot_tableWgt.setItem(row, 0, _item_date)
                self.ui.shot_tableWgt.setItem(row, 1, _item_name)
                self.ui.shot_tableWgt.setItem(row, 2, _item_ZhName)
                row += 1
        self.ui.shot_tableWgt.sortItems(0, QtCore.Qt.DescendingOrder)
        # eps_list = []
        # for info in data:
        #     aa = "{0}_{1}".format(info[0], info[1]) + '   /   ' + info[2]
        #     eps_list.append(aa)
        # eps_list.sort(reverse=self.sortReverse)
        # self.ui.ani_idea_listWgt.clear()
        # for i in eps_list:
        #     if i.lower().find(keyword.lower()) != -1:
        #         item = QtWidgets.QListWidgetItem()
        #         item.setText(i)
        #         self.ui.ani_idea_listWgt.addItem(item)

    def get_database(self):
        """ 获取整表格数据SQL命令 """
        # print("获取shot数据")
        current_project = self.ui.Project_ComboBox.currentText()
        conn = None
        cur = None
        get_script = ''' 
            SELECT "shot.date", "shot.name", "shot.zh_name"
            FROM public."shot";
        '''
        try:
            conn = psycopg2.connect(database=current_project, user=self.user, password=self.password, host=self.host,
                                    port="5432")
            cur = conn.cursor()
            cur.execute(get_script)
            data = cur.fetchall()
            # print(data)
            self.shot_list = data
        except Exception as e:
            QtWidgets.QMessageBox.information(self, u"提醒", u"你尚未登录系统\n\n" + str(e))
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()

    def getIdea_TW(self):
        """根据项目从CGTeamWork获得集数显示"""
        print("getIdea_TW")
        import cgtw2
        t_tw = cgtw2.tw()
        current_project = self.ui.Project_ComboBox.currentText()
        keyword = self.ui.key_line.text()
        sortReverse = self.sortReverse
        TW_proj = self.projectSetting()['projectdiction'][current_project]
        t_eps_ids = t_tw.info.get_id(TW_proj, 'chuangyi', [])
        eps = t_tw.info.get(TW_proj, 'chuangyi', t_eps_ids,
                            ['chuangyi.creatdate', 'chuangyi.entity', 'chuangyi.chname'])
        eps_list = []
        for info in eps:
            aa = "{0}_{1}".format(info['chuangyi.creatdate'],
                                  info['chuangyi.entity']) + '   /   ' + info['chuangyi.chname']
            eps_list.append(aa)
        eps_list.sort(reverse=sortReverse)
        self.ui.ani_idea_listWgt.clear()
        for i in eps_list:
            if i.lower().find(keyword.lower()) != -1:
                item = QtWidgets.QListWidgetItem()
                item.setText(i)
                self.ui.ani_idea_listWgt.addItem(item)

    def getStage(self):
        """ 设置阶段 """
        # self.ui.stages_listWgt.addItems(self.stages)
        for i in self.stages:
            item = QtWidgets.QListWidgetItem()
            item.setText(str(i))
            icon = QtGui.QIcon()
            pixmap = myWidget.Pixmap('%s/icon/%s.png' % (self.scriptsPath, i))
            # pixmap.setColor(QtGui.QColor("#b3b3b3"))
            icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon)
            self.ui.stages_listWgt.addItem(item)
        self.ui.stages_listWgt.setCurrentRow(0)

    # def getShot(self):
    #     """ 设置卡号显示 """
    #     RootPath, current_project, current_idea, current_stage, current_shot = self._get_current_data()
    #     self.ui.ani_shot_listWgt.clear()
    #     shotPath = "{0}/{1}/Projects/{2}/{3}".format(RootPath, current_project, current_idea, current_stage)
    #     if QtCore.QFileInfo(shotPath).exists():
    #         dir = QtCore.QDir(shotPath)
    #         for shot in dir.entryList(QtCore.QDir.NoDotAndDotDot ^ QtCore.QDir.AllEntries):
    #             item = QtWidgets.QListWidgetItem()
    #             item.setText(shot)
    #             self.ui.ani_shot_listWgt.addItem(item)

    def getFile(self):
        """
        根据path 设置ma文件显示
        :return:
        """
        file_path = str(self.ui.aniPath_label.text())
        self.ui.aniAST_listWgt.clear()
        if QtCore.QFileInfo(file_path).exists():
            model = QtWidgets.QFileSystemModel()
            model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
            model.setRootPath(file_path)
            # self.ui.aniAST_listWgt.setModel(model)
            self.ui.aniAST_listWgt.setRootIndex(model.index(file_path))
            # dir = QtCore.QDir(file_path)
            # for file in dir.entryList(QtCore.QDir.NoDotAndDotDot ^ QtCore.QDir.AllEntries):
            #     if file.endswith('.ma') or file.endswith('.mb') or file.endswith('.fbx') or \
            #             file.endswith('.abc') or file.endswith('.anim') or file.endswith('.pose'):
            #         item = QtWidgets.QListWidgetItem()
            #         item.setText(file)
            #         self.ui.aniAST_listWgt.addItem(item)

    def changeIdeaSort(self):
        """
        改变创意排序
        :return:
        """
        # print(self.sortReverse)
        if self.sortReverse:
            self.sortReverse = False
            self.getIdea_TW()
        else:
            self.sortReverse = True
            self.getIdea_TW()
        self.rememberSettings()

    def getPath(self):
        """根据Project设置路径"""
        current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
        self.ui.aniPath_label.setText('{0}/{1}/Projects'.format(self.RootPath, current_project))
        if current_idea != "None":
            self.ui.aniPath_label.setText('{0}/{1}/Projects/{2}_{3}'.format(self.RootPath, current_project,
                                                                            current_date, current_idea))
            if current_stage != "None":
                self.ui.aniPath_label.setText('{0}/{1}/Projects/{2}_{3}/{4}'.format(self.projectSetting()['rootPath'],
                                                                                    current_project, current_date,
                                                                                    current_idea,
                                                                                    current_stage))

    def changeProject(self):
        """触发：更新path，更新idea，更新文件"""
        self.getPath()
        self.getIdea_TW()
        self.getFile()
        self.rememberSettings()

    def changeIdea(self):
        """切换创意触发：得到文件；设置Path"""
        self.ui.aniAST_listWgt.clear()
        current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
        if current_idea != "None":
            shot_path = '{0}/{1}/Projects/{2}_{3}/{4}'.format(self.RootPath, current_project, current_date,
                                                              current_idea, current_stage)
            self.ui.aniPath_label.setText(shot_path)
            self.getFile()
        self.ui.aniAST_listWgt.setCurrentRow(0)
        self.rememberSettings()

    def changeStage(self):
        """切换阶段触发：更新path；更新镜头，更新文件名"""
        current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
        shot_path = '{0}/{1}/Projects/{2}_{3}/{4}'.format(self.RootPath, current_project, current_date,
                                                          current_idea, current_stage)
        self.ui.aniPath_label.setText(shot_path)
        self.getFile()

    # def changeShot(self):
    #     """切换卡号触发：更新path；更新fbx文件名"""
    #     self.ui.aniAST_listWgt.clear()
    #     RootPath, current_project, current_idea, current_stage, current_shot = self._get_current_data()
    #     mafile_path = '{0}/{1}/Projects/{2}/{3}/{4}'.format(RootPath, current_project, current_idea, current_stage,
    #                                                         current_shot)
    #     self.ui.aniPath_label.setText(mafile_path)
    #     self.getFile()

    def changeFile(self):
        """ 切换动画文件触发：更新文件名，更新属性栏 """
        currentSelected = self.ui.aniAST_listWgt.selectedItems()
        if currentSelected:
            filename = str(self.ui.aniAST_listWgt.currentItem().text())
            self.ui.name_line.setText(filename)
            all_path = self.ui.aniPath_label.text()

            self.ui.PreviewLabel.clear()
            self.ui.title_label.clear()
            self.ui.frams_lineEdit.clear()
            self.ui.title_label.setText(filename)
            if filename.endswith('.pose'):
                icon_path = all_path + "/" + filename + "/thumbnail.jpg"
                # print(icon_path)
                self.ui.PreviewLabel.setPreviewPixmap(icon_path, "pose")
                self.ui.pose_percent_frame.setVisible(True)
                self.ui.apply_option_frame.setVisible(False)
                self.ui.action_apply_bttn.clicked.connect(self.applyPose)
            elif filename.endswith('.anim'):
                icon_path = all_path + "/" + filename + "/thumbnail.jpg"
                # print(icon_path)
                self.ui.PreviewLabel.setAnim(icon_path, "animation")
                anim = animation.Animation.fromPath(all_path + "/" + filename)
                self.ui.apply_option_lineEdit01.setText(str(anim.startFrame()))
                self.ui.apply_option_lineEdit02.setText(str(anim.endFrame()))
                self.ui.pose_percent_frame.setVisible(False)
                self.ui.apply_option_frame.setVisible(True)
                self.ui.action_apply_bttn.clicked.connect(self.applyAction)

    def change_publishType(self):
        """ 改变发布类型触发：改变文件名"""
        old_name = self.ui.name_line.text()
        suffix = self.get_suffix()
        new_name = old_name.rsplit(".")[0] + suffix
        self.ui.name_line.setText(new_name)

    def openFile(self):
        """
        打开文件
        :return:
        """
        file_name = str(self.ui.aniAST_listWgt.currentItem().text())
        if file_name.endswith(".ma") or file_name.endswith(".mb"):
            file_path = "{0}/{1}".format(self.ui.aniPath_label.text(), file_name)
        elif file_name.endswith(".anim") or file_name.endswith(".pose"):
            file_path = "{0}/{1}/maya_file.ma".format(self.ui.aniPath_label.text(), file_name)
        else:
            return
        cmds.file(file_path, o=True, f=True)

    def openFolder(self):
        FilePath = self.ui.aniPath_label.text()
        os.startfile(FilePath)

    def show_menu_ani_idea_listWgt(self, point):
        """
        ani_idea_listWgt 的右键菜单
        :param point:
        :return:
        """
        currentItem = self.ui.ani_idea_listWgt.itemAt(point)
        menu = QtWidgets.QMenu(self.ui.ani_idea_listWgt)
        if currentItem is not None:
            _list = self.find_link()
            for ls in _list:
                _path = "{0}/{1}/Assets/{2}/{3}/Rig/{3}_hi_rig.ma".format(self.RootPath, ls['project'], ls['type'],
                                                                          ls['role_name'])
                menu.addAction(self.add_action(_path))

            menu.exec_(QtGui.QCursor.pos())
        else:
            pass
        return

    def add_action(self, path):
        """使用Java闭包，否则triggered.connect的action只会认到最后一个action"""
        action = QtWidgets.QAction(path, self)
        action.setIcon(QtGui.QIcon("{}/icon/link.png".format(self.scriptsPath)))
        action.setData(path)
        action.triggered.connect(lambda: self.createRef(path))
        return action

    def find_link(self):
        current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
        import cgtw2
        t_tw = cgtw2.tw()

        TW_proj = self.projectSetting()['projectdiction'][current_project]
        t_link_id = t_tw.task.get_id(TW_proj, 'chuangyi', filter_list=[["chuangyi.chname", "=", current_idea_zh]])
        asset_link_id = t_tw.link.get_asset(TW_proj, 'chuangyi', module_type='entity', id=t_link_id[0])
        if not asset_link_id:
            asset_link_names = []
        else:
            asset_link_names = t_tw.info.get(TW_proj, 'asset', asset_link_id.keys(), ['asset.entity', 'asset.cn_name',
                                                                                      'asset.assetstapy'])
        assetList = []
        for a in asset_link_names:
            asset = {'role_name': a['asset.entity'], 'project': current_project, 'type': a['asset.assetstapy'],
                     'zh_name': a['asset.cn_name']}
            assetList.append(asset)

        return assetList

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

    def show_menu_aniAST_listWgt(self, point):
        """
        aniAST_listWgt 的右键菜单
        :param point:
        :return:
        """
        currentItem = self.ui.aniAST_listWgt.itemAt(point)
        menu = QtWidgets.QMenu(self.ui.aniAST_listWgt)
        show_action = QtWidgets.QAction('Show in Explorer', self)
        show_action.setIcon(QtGui.QIcon("{}/icon/folder_white.png".format(self.scriptsPath)))
        show_action.triggered.connect(partial(self.openFolder, '', currentItem))
        if currentItem is not None:
            open_action = QtWidgets.QAction('Open maya file', self)
            open_action.triggered.connect(self.openFile)

            menu.addAction(open_action)
            menu.addSeparator()
            menu.addAction(show_action)
            menu.exec_(QtGui.QCursor.pos())
        else:
            anim_publish_action = QtWidgets.QAction(u'发布动画资产', self)
            anim_publish_action.setIcon(QtGui.QIcon("{}/icon/publish.png".format(self.scriptsPath)))
            anim_publish_action.triggered.connect(lambda: self.aniPublish())

            menu.addAction(anim_publish_action)
            menu.addSeparator()
            menu.addAction(show_action)

            menu.exec_(QtGui.QCursor.pos())
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

    def applyAction(self):
        """
        应用动作
        :return:
        """
        select_controls = cmds.ls(sl=1) or []
        current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
        file_name = self.ui.aniAST_listWgt.selectedItems()[0].text()

        path = path + "/" + file_name
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

    def check_before_publish(self):
        """ 发布前检查 """
        mll_list = ['AbcExport.mll', 'AbcImport.mll', 'fbxmaya.mll']
        for mll in mll_list:
            if self.Pub.pluginInfo(mll) is False:
                QtWidgets.QMessageBox.warning(self, '警告', '未发现{}，请加载!'.format(mll))
                return

        self.Pub.removeUnknownNodes()
        self.Pub.removeModelChangeError()

    def aniPublish(self):
        """
        发布动作
        :return:
        """
        if self.check_before_publish() is False:
            return
        else:
            current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
            if current_project is None or current_idea is None:
                cmds.warning(u'请选择要发布的创意路径')
                return

            publishType = self.ui.publishType_comb_ac.currentText()
            ani_file_name = self.ui.name_line.text()
            ani_file_Path = self.Pub.makePath('{0}/{1}/Projects/{2}/{3}'.format(self.RootPath, current_project,
                                                                                current_idea, current_stage))

            _log = "log:"
            self.renderIcon()
            '''======================== 保存ma和动作库 ======================================='''
            if self.ui.maya_cBox.isChecked():
                controls = []
                selected_controls = cmds.ls(sl=1, type='transform')
                for selected_control in selected_controls:
                    if cmds.nodeType(cmds.listRelatives(selected_control, shapes=True)) == 'nurbsCurve':
                        controls.append(selected_control)
                if not controls:
                    QtWidgets.QMessageBox.warning(self, "Warning", u"请选择要导出的控制器")
                    return
                start = int(cmds.playbackOptions(query=True, minTime=True))
                end = int(cmds.playbackOptions(query=True, maxTime=True))

                ''' --------------------------------拍icon---------------------------------------- '''
                iconPath = str('%s/snapshot/thumbnail.jpg' % self.tempPath)
                sequencePath = self.tempPath + "/sequence"
                if publishType == "Animation":
                    self.Pub.seqshot(sequencePath, widthHeight=[288, 192])
                ''' ------------------------------发布动作库-------------------------------------- '''
                suffix = self.get_suffix()
                action_path = "{0}/{1}".format(ani_file_Path, ani_file_name)

                if os.path.exists(action_path):
                    reply = QtWidgets.QMessageBox.question(self, '提示', '路径上已有重名动画，确定还要继续发布吗？',
                                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        pass
                    else:
                        return
                try:
                    self.Pub.makePath(action_path)
                    if publishType == "Animation":
                        animation.saveAnim(path=action_path,
                                           objects=controls,
                                           time=(start, end),
                                           iconPath=iconPath,
                                           sequencePath=sequencePath,
                                           metadata={'description': ani_file_name})
                    else:
                        pose.savePose(path=action_path,
                                      objects=controls,
                                      iconPath=iconPath)
                    _log += u"动画{}已发布".format(ani_file_name)
                except Exception as e:
                    _log += u"动作{0}发布失败：{1}".format(ani_file_name, e)
                ''' ------------------------------保存maya-------------------------------------- '''
                try:
                    self.saveMaya('{0}/{1}.ma'.format(action_path, ani_file_name))
                    _log += u"\n> 动画档已保存"
                except Exception as e:
                    _log += u"\n> 动画档保存失败请检查%s" % e

            '''==================== 发布fbx ===================================='''
            if self.ui.FBX_cBox.isChecked():
                fbx_path = "{0}/{1}/Projects/{2}/ANI/AniFile/{3}".format(self.RootPath, current_project,
                                                                         current_idea, ani_file_name)
                try:
                    self.pubFBX(fbx_path)
                    _log += u"\n> FBX已发布"
                except Exception as e:
                    cmds.warning('AniFBX publish failed.')
                    _log += u"\n> FBX发布失败，请检查:%s" % e

            '''======================= 发布相机 ======================================'''
            if self.ui.Cam_cBox.isChecked():
                cam_path = "{0}/{1}/Projects/{2}/ANI/AniFile/{3}".format(self.RootPath, current_project,
                                                                         current_idea, ani_file_name)
                try:
                    self.pubCam(cam_path)
                    _log += u"\n> 相机已发布"
                except Exception as e:
                    cmds.warning('AniCamera publish failed:%s.' % e)
                    _log += u"\n> 相机发布失败请检查:%s" % e

            '''======================== 发布拍屏 ======================================'''
            if self.ui.Pb_cBox.isChecked():
                Pb_file_path = ani_file_Path.replace('.ma', '.mov').replace('AniFile', 'AniPlayblast')
                try:
                    self.pubPlayblast(Pb_file_path)
                    _log += u"\n> 拍屏已发布"
                except Exception as e:
                    cmds.warning('AniFBX publish failed.')
                    _log += u"\n> 拍屏发布失败:%s" % e

            self.getFile()
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                        u"<h3>动画档案发布成功!\n查看log获取更多细节?</h3>")
            msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
            msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            msg.setDetailedText(_log)
            msg.exec_()

    def renderIcon(self):
        """
        拍摄icon并显示在标签
        """
        local_icon_path = self.Pub.makePath(str('%s/snapshot' % self.tempPath))
        minTime = cmds.playbackOptions(query=True, minTime=True)  # cmds.currentTime(query=True)
        try:
            localicon = self.Pub.snapshot(local_icon_path, imageFormat='jpg', frame=minTime,
                                          widthHeight=[288, 192], need_createHistory=False)
            print("%s is snap shoted !!" % localicon)
        except Exception as e:
            print("Error : snapshot is stuck:%s" % e)

    def saveMaya(self, ma_file_Path):
        if QtCore.QFileInfo(ma_file_Path).exists():
            reply = QtWidgets.QMessageBox.question(self, '提示', '文件已存在，确定覆盖吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                cmds.file(rename=ma_file_Path)
                cmds.file(save=True, type='mayaAscii')
            else:
                return

    def pubFBX(self, FilePath):
        aniAST_list = cmds.ls('*:*_*_AST', type='transform')
        minTime = cmds.playbackOptions(query=True, minTime=True)
        maxTime = cmds.playbackOptions(query=True, maxTime=True)
        # FilePath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True).replace('/AniFile/','/AniFBX/')
        self.Pub.makePath(FilePath)
        for i in aniAST_list:
            aniFbxName = i.replace(':', '__')
            cmds.select(clear=True)
            cmds.select('{0}:Geometry'.format(i.split(':')[0]))
            try:
                cmds.select('{0}:DeformationSystem'.format(i.split(':')[0]), add=True)
            except Exception as e:
                cmds.warning('Can not find {0}:DeformationSystem:{1}'.format(i.split(':')[0], e))
            self.Pub.exportFBX(True, minTime, maxTime, '{0}/{1}.fbx'.format(FilePath, aniFbxName))
        cmds.select(clear=True)

    def pubCam(self, FilePath):
        if os.path.exists(FilePath) is False:
            os.makedirs(FilePath)
        camera = cmds.ls(self.camera_name, long=True, assemblies=True)
        if len(camera) != 1:
            cmds.confirmDialog(title='Confirm',
                               message=u'相机不存在 或者 不唯一！相机命名规范是: camera开头',
                               button=['Yes'],
                               defaultButton='Yes',
                               icon='warning')
            raise Exception("no camera be found")

        camera_name = cmds.ls(self.camera_name, long=True, assemblies=True)[0]
        camFileName = camera_name.split('|')[1]
        cmds.setAttr("%s.filmFit" % camFileName, 1)
        minTime = int(cmds.playbackOptions(query=True, minTime=True))
        maxTime = int(cmds.playbackOptions(query=True, maxTime=True))
        cam_name = "{}_{}_{}".format(self.camera_file_name, minTime, maxTime)
        self.Pub.exportAlembic(minTime, maxTime, camera_name, '{0}/{1}.abc'.format(FilePath, cam_name))
        cmds.select(camera_name)
        self.Pub.exportFBX(False, minTime, maxTime, '{0}/{1}.fbx'.format(FilePath, cam_name))

    def pubPlayblast(self, movPath):
        cam = cmds.ls(self.camera_name, assemblies=True)
        if cam:
            cmds.lookThru(cam[0])
            minTime = cmds.playbackOptions(query=True, minTime=True)
            maxTime = cmds.playbackOptions(query=True, maxTime=True)
            resolution_width = cmds.getAttr('defaultResolution.width')
            resolution_height = cmds.getAttr('defaultResolution.height')
            FilePath = movPath.rsplit("/", 1)[0]
            if os.path.exists(FilePath) is False:
                os.makedirs(FilePath)
            # ani_playblast_path, ani_playblast_dir = self.make_path(current_project, current_idea, current_idea_data, current_scene, 'AniPlayblast')
            # self.Pub.createHistory(ani_playblast_path)
            # self.create_heads_up()
            cmds.playblast(forceOverwrite=True, clearCache=True, startTime=minTime, endTime=maxTime, sequenceTime=0,
                           percent=100, quality=100, framePadding=4, widthHeight=[resolution_width, resolution_height],
                           format='qt', compression='H.264', showOrnaments=True, viewer=False, offScreen=True,
                           filename=movPath)
            # self.remove_heads_up()

    # def exportFBX(self, bakeAni, start, end, path):
    #     melScript = 'FBXExportBakeComplexAnimation -v %s;\n        FBXExportBakeComplexStart -v %s;\n        FBXExportBakeComplexEnd -v %s;\n        FBXExportBakeComplexStep -v 1;\n        FBXExportBakeResampleAnimation  -v true;\n        FBXExportSmoothingGroups -v true;\n        FBXExportSmoothMesh -v true;\n        FBXExportReferencedAssetsContent -v true;\n        FBXExportShapes -v true;\n        FBXExportSkins -v true;\n        FBXExport -f "%s" -s;' % (
    #         bakeAni, start, end, path)
    #     mel.eval(melScript)
    #
    # def exportAlembic(self, start, end, name, path):
    #     jobArg = '-frameRange %s %s -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root %s -file %s' % (
    #         start, end, name, path)
    #     cmds.AbcExport(jobArg=jobArg)

    # def search(self):
    #     """
    #     搜索
    #     """
    #     search_name = cmds.textFieldGrp('SearchUI', q=1, tx=1)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, allItems=True)
    #     cmds.textScrollList('IdeasFloderUI', e=True, ra=1)
    #     if search_name:
    #         for i in IdeaName:
    #             if re.search(search_name, i, re.IGNORECASE):
    #                 cmds.textScrollList('IdeasFloderUI', e=True, append=i, selectItem=i)
    #     else:
    #         self.ideaGet_TW()

    # def OffAllWindows(self):
    #     NormalWin = ['MayaWindow', 'CGpipelineTool']
    #     ViewWins = cmds.lsUI(windows=True)
    #     for ViewWin in ViewWins:
    #         if ViewWin not in NormalWin:
    #             cmds.deleteUI(ViewWin, window=True)
    #
    # def OffViewport(self):
    #     ToolSet = MYPREFSDIR + 'CGpipelineToolSet.txt'
    #     if os.path.isfile(ToolSet):
    #         o = open(ToolSet, 'r').read()
    #         oo = re.split(':', o)
    #         if oo[4] == 'True':
    #             panes = cmds.getPanel(type='modelPanel')
    #             for pane in panes:
    #                 attr = 'setRendererInModelPanel base_OpenGL_Renderer ' + pane + ';'
    #                 mel.eval(attr)

    # def SwitchToMaster(self):
    #     ToolSet = MYPREFSDIR + 'CGpipelineToolSet.txt'
    #     if os.path.isfile(ToolSet):
    #         o = open(ToolSet, 'r').read()
    #         oo = re.split(':', o)
    #         if oo[4] == 'True':
    #             cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
    #             cmds.setAttr('defaultRenderLayer.renderable', 0)
    #     else:
    #         cmds.editRenderLayerGlobals(currentRenderLayer='defaultRenderLayer')
    #         cmds.setAttr('defaultRenderLayer.renderable', 0)

    # def ShowNone(self):
    #     ToolSet = MYPREFSDIR + 'CGpipelineToolSet.txt'
    #     if os.path.isfile(ToolSet):
    #         o = open(ToolSet, 'r').read()
    #         oo = re.split(':', o)
    #         if oo[6] == 'True':
    #             mel.eval(
    #                 'modelEditor -e -allObjects 0 modelPanel4;updateShowMenu MayaWindow|formLayout1|viewPanes|modelPanel4|menu30|menuItem1572 modelPanel4 "modelPanel4" "Playblast Display";')
    #     else:
    #         mel.eval(
    #             'modelEditor -e -allObjects 0 modelPanel4;updateShowMenu MayaWindow|formLayout1|viewPanes|modelPanel4|menu30|menuItem1572 modelPanel4 "modelPanel4" "Playblast Display";')

    # def OpenMayaSet(self):
    #     self.OffViewport()
    #     cmds.editRenderLayerGlobals(enableAutoAdjustments=True)

    # def projectSet(self, *args):
    #     """
    #     切换项目触发--改path--写入txt--设置idea--清空文件名
    #     """
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSPATH + EPfiles + '/Projects/')
    #     f = open(MYPREFSDIR + 'EP.txt', 'w')
    #     f.write(EPfiles)
    #     f.close()
    #     self.ideaGet_TW()
    #     cmds.textScrollList('FileViewUI', e=True, ra=True)

    # def projectGet(self):
    #     """
    #     读取txt里的项目名
    #     """
    #     if os.path.isfile(MYPREFSDIR + 'EP.txt'):
    #         o = open(MYPREFSDIR + 'EP.txt', 'r').read()
    #         EPfiles = cmds.optionMenuGrp('EpUI', e=True, v=o)
    #         cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSPATH + o + '/Projects/')

    # def ideaSet(self):
    #     """
    #     切换创意触发--改path--改阶段为空--清空卡号
    #     """
    #     FilePaths = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0]
    #     cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSPATH + EPfiles + '/Projects/' + IdeaName)
    #     cmds.textScrollList('StagesFloderUI', e=True, selectItem='')
    #     cmds.textScrollList('ShotsFloderUI', e=True, ra=True, append=(''), selectItem='')

    # def ideaSet_TW(self):
    #     """
    #     切换创意触发--改path--改阶段为空--清空卡号
    #     """
    #     global PROJECTSPATH
    #     FilePaths = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaPaths = PROJECTSPATH + EPfiles + '/Projects/'
    #     TWIdeaEnName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0].split('   /    ')[0]
    #     IdeaFolder = os.listdir(IdeaPaths)
    #     for i in IdeaFolder:
    #         if i == TWIdeaEnName:
    #             cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSPATH + EPfiles + '/Projects/' + i)
    #         else:
    #             pass
    #     cmds.textScrollList('StagesFloderUI', e=True, selectItem='')
    #     cmds.textScrollList('ShotsFloderUI', e=True, ra=True, append=(''), selectItem='')
    #     self.MayaFiles()

    # def ideaGet(self):
    #     """
    #     根据项目名设置创意栏显示
    #     """
    #     FilePaths = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     if os.path.exists(FilePaths):
    #         IdeasFiles = os.listdir(FilePaths)
    #         cmds.textScrollList('IdeasFloderUI', e=True, ra=True)
    #         cmds.textScrollList('IdeasFloderUI', append=IdeasFiles, e=True)
    #     else:
    #         print(u'%s不存在！！！！！' % FilePaths)

    # def ideaGet_TW(self, *args):
    #     """
    #     根据CGTeamwork项目名设置创意栏显示
    #     """
    #     global PROJECTSPATH
    #     FilePaths = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaPaths = PROJECTSPATH + EPfiles + '/Projects/'
    #     AA = self.TW_infoEN()
    #     D = self.TW_info_dicENCN()
    #     ZZ = []
    #     if os.path.exists(IdeaPaths):
    #         cmds.textScrollList('IdeasFloderUI', e=True, ra=True)
    #         IdeasFiles = os.listdir(IdeaPaths)
    #         for i in IdeasFiles:
    #             # print(i)
    #             try:
    #                 idea = i.split('_')[1]
    #                 # idea = i
    #                 if idea in AA:
    #                     Z = i + '   /    ' + D[idea]
    #                 else:
    #                     Z = i
    #                 ZZ.append(Z)
    #             except:
    #                 print(u"%s 违反命名规范！" % i)
    #                 continue
    #         cmds.textScrollList('IdeasFloderUI', append=ZZ, e=True)
    #     else:
    #         print(u'%s不存在！！！！！' % FilePaths)

    # def TW_infoEN(self):
    #     import cgtw2
    #     t_tw = cgtw2.tw()
    #     projectdiction = self.projectSetting()['projectdiction']
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     TW_proj = projectdiction[EPfiles]
    #     t_eps_ids = t_tw.info.get_id(TW_proj, 'chuangyi', [])
    #     TW_dictionInfo = t_tw.info.get(TW_proj, 'chuangyi', t_eps_ids, ['chuangyi.entity', 'chuangyi.chname'])
    #     AA = []
    #     for info in TW_dictionInfo:
    #         A = info['chuangyi.entity']
    #         AA.append(A)
    #     return AA

    # def TW_info_dicENCN(self):
    #     import cgtw2
    #     t_tw = cgtw2.tw()
    #     projectdiction = self.projectSetting()['projectdiction']
    #     TW_proj = 'proj_ffa_0'
    #     t_eps_ids = t_tw.info.get_id(TW_proj, 'chuangyi', [])
    #     TW_dictionInfo = t_tw.info.get(TW_proj, 'chuangyi', t_eps_ids, ['chuangyi.entity', 'chuangyi.chname'])
    #     AA = []
    #     D = {}
    #     for info in TW_dictionInfo:
    #         A = info['chuangyi.entity']
    #         AA.append(A)
    #         B = info['chuangyi.chname']
    #         C = {A: B}
    #         D.update(C)
    #     return D

    # def stage(self):
    #     """
    #     切换阶段触发--改path
    #     """
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     FilePath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0]
    #     StagePath = cmds.textScrollList('StagesFloderUI', q=True, selectItem=True)[0]
    #     cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSPATH + EPfiles + '/Projects/' + IdeaName + StagePath)

    # def stageSet_TW(self):
    #     """
    #     切换阶段触发--改path
    #     """
    #     global PROJECTSPATH
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaPaths = PROJECTSPATH + EPfiles + '/Projects/'
    #     TWIdeaEnName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0].split('   /    ')[0]
    #     StagePath = cmds.textScrollList('StagesFloderUI', q=True, selectItem=True)[0]
    #     IdeaFolder = os.listdir(IdeaPaths)
    #     for i in IdeaFolder:
    #         if i == TWIdeaEnName:
    #             cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSPATH + EPfiles + '/Projects/' + i + StagePath)
    #         else:
    #             pass
    #     # cmds.textScrollList('ShotsFloderUI', e=True , ra=True , append=(''), selectItem='')
    #     self.getShot()
    #     self.MayaFiles()

    # def shotSet(self):
    #     '''
    #     切换卡号触发--改path
    #     '''
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     FilePath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0]
    #     StagePath = cmds.textScrollList('StagesFloderUI', q=True, selectItem=True)[0]
    #     ShotPath = cmds.textScrollList('ShotsFloderUI', q=True, selectItem=True)[0]
    #     cmds.textFieldGrp('MayaPathUI', e=True,
    #                       tx=PROJECTSPATH + EPfiles + '/Projects/' + IdeaName + StagePath + ShotPath)

    # def shotSet_TW(self):
    #     '''
    #     切换卡号触发--改path CGT版
    #     '''
    #     global PROJECTSPATH
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaPaths = PROJECTSPATH + EPfiles + '/Projects/'
    #     TWIdeaEnName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0].split('   /    ')[0]
    #     StagePath = cmds.textScrollList('StagesFloderUI', q=True, selectItem=True)[0]
    #     ShotPath = cmds.textScrollList('ShotsFloderUI', q=True, selectItem=True)[0]
    #     IdeaFolder = os.listdir(IdeaPaths)
    #     for i in IdeaFolder:
    #         if i == TWIdeaEnName:
    #             cmds.textFieldGrp('MayaPathUI', e=True,
    #                               tx=PROJECTSPATH + EPfiles + '/Projects/' + i + StagePath + ShotPath)
    #         else:
    #             pass
    #     self.MayaFiles()

    # def SetShotsIcon(self):
    #     FourName = cmds.textFieldGrp('FourUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     FilePaths = PROJECTSHOWPATH + EPfiles + '/'
    #     Files = os.listdir(FilePaths)
    #     for File in Files:
    #         if re.search(FourName, File):
    #             LGTicon = PROJECTSHOWPATH + EPfiles + '/' + File + '/lighting/icon/' + '__icon__.jpg'
    #             ANIicon = PROJECTSHOWPATH + EPfiles + '/' + File + '/anim/icon/' + '__icon__.jpg'
    #             if os.path.isfile(LGTicon):
    #                 cmds.picture('ShoticonUI', e=True, image=LGTicon, w=192)
    #                 break
    #             elif os.path.isfile(ANIicon):
    #                 cmds.picture('ShoticonUI', e=True, image=ANIicon, w=192)
    #                 break
    #             else:
    #                 cmds.picture('ShoticonUI', e=True, image=('{}icon/otherIcon/__icon__.jpg').format(self.scriptPath),
    #                              w=192)
    #                 break
    #         else:
    #             cmds.picture('ShoticonUI', e=True, image=('{}icon/otherIcon/__icon__.jpg').format(self.scriptPath),
    #                          w=192)

    # def SizeTime(self):
    #     STime = cmds.checkBox('SizeTimeUI', q=True, v=True)
    #     f = open(MYPREFSDIR + PROJECTNAME + 'ST.txt', 'w')
    #     f.write(str(STime))
    #     f.close()
    #
    # def SizeTimeSet(self):
    #     if os.path.isfile(MYPREFSDIR + PROJECTNAME + 'ST.txt'):
    #         o = open(MYPREFSDIR + PROJECTNAME + 'ST.txt', 'r').read()
    #         if o == 'True':
    #             cmds.checkBox('SizeTimeUI', e=True, v=True)
    #         else:
    #             cmds.checkBox('SizeTimeUI', e=True, v=False)

    # def Getshotsfloder(self):
    #     if os.path.isfile(('{}for_Maya/files/shotsfloder.txt').format(self.scriptPath)):
    #         floder = open(('{}for_Maya/files/shotsfloder.txt').format(self.scriptPath), 'r').read()
    #         cmds.textScrollList('ShotsfloderUI', append=floder, e=True, ra=True)

    # def File(self):
    #     cmds.textScrollList('FileViewUI', e=True, ra=True)
    #     FourName = cmds.textFieldGrp('FourUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     FilePaths = PROJECTSHOWPATH + EPfiles + '/'
    #     FloderName = cmds.textScrollList('ShotsfloderUI', q=True, si=True)
    #     Files = os.listdir(FilePaths)
    #     for File in Files:
    #         if re.search(FourName, File):
    #             cmds.textFieldGrp('MayaPathUI', e=True, tx=PROJECTSHOWPATH + EPfiles + '/' + File + '/' + FloderName[0])
    #             cmds.textFieldGrp('MayaShotUI', e=True, tx=File)

    # def MayaFiles(self):
    #     '''
    #     设置文件的ma档显示
    #     '''
    #     cmds.textScrollList('FileViewUI', e=True, ra=True)
    #     FilePath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)
    #     ShotPath = cmds.textScrollList('ShotsFloderUI', q=True, selectItem=True)
    #     if ShotPath:
    #         if os.path.exists(FilePath):
    #             AFiles = os.listdir(FilePath)
    #             # AFiles.sort()
    #             for AFile in AFiles:
    #                 if AFile.endswith('.ma') or AFile.endswith('.mb') or AFile.endswith('.fbx') or AFile.endswith(
    #                         '.abc'):
    #                     size = str(round(round(os.path.getsize(FilePath + '/' + AFile) / 1024, 3) / 1000, 3))
    #                     Mtime = time.localtime(os.stat('' + FilePath + '/' + AFile + '').st_ctime)
    #                     Ftime = str(Mtime[0]) + '-' + str(Mtime[1]).zfill(2) + '-' + str(Mtime[2]).zfill(2) + ' ' + str(
    #                         Mtime[3]).zfill(2) + ':' + str(Mtime[4]).zfill(2)
    #                     cmds.textScrollList('FileViewUI', e=True,
    #                                         append=AFile + '           ' + size + ' MB    ' + Ftime)

    # def OpenFileViewFile(self):
    #     self.OpenMayaFiles("FileViewUI", "MayaPathUI")

    # def OpenMayaFiles(self, UI, PathUI):
    #     SceneName = cmds.file(q=True, sceneName=True)
    #     LoadSet = ''
    #     FilePaths = cmds.textFieldGrp(PathUI, q=True, tx=True)
    #     AFilesPath = FilePaths
    #     AFilenames = cmds.textScrollList(UI, q=True, si=True)
    #     for AFilename in AFilenames:
    #         AF = re.split(' ', AFilename)
    #         AFliePath = AFilesPath + '/' + AF[0]
    #
    #     SceneName = cmds.file(q=True, sceneName=True)
    #     if SceneName != '':
    #         CheckSave = cmds.confirmDialog(title='Confirm', message='Do you want to save the current Maya?',
    #                                        button=['Yes', 'No', 'Cancel'], defaultButton='Yes', cancelButton='Cancel',
    #                                        dismissString='Cancel', icon='question')
    #         if CheckSave == 'Cancel':
    #             pass
    #         else:
    #             if CheckSave == 'Yes':
    #                 CurrentFile = cmds.file(q=True, sceneName=True)
    #                 if CurrentFile == '':
    #                     if LoadSet == 'load no references':
    #                         cmds.file(AFliePath, o=True, f=True, lnr=True)
    #                         cmds.renderThumbnailUpdate(False)
    #                         OpenMayaSet()
    #                     else:
    #                         cmds.file(AFliePath, o=True, f=True)
    #                         cmds.renderThumbnailUpdate(False)
    #                         OpenMayaSet()
    #                 else:
    #                     self.SwitchToMaster()
    #                     cmds.file(rename=CurrentFile)
    #                     cmds.file(s=True, type='mayaAscii')
    #                     if LoadSet == 'load no references':
    #                         cmds.file(AFliePath, o=True, f=True, lnr=True)
    #                         cmds.renderThumbnailUpdate(False)
    #                         OpenMayaSet()
    #                     else:
    #                         cmds.file(AFliePath, o=True, f=True)
    #                         cmds.renderThumbnailUpdate(False)
    #                         OpenMayaSet()
    #             if CheckSave == 'No':
    #                 if LoadSet == 'load no references':
    #                     cmds.file(AFliePath, o=True, f=True, lnr=True)
    #                     cmds.renderThumbnailUpdate(False)
    #                     OpenMayaSet()
    #                 else:
    #                     cmds.file(AFliePath, o=True, f=True)
    #                     cmds.renderThumbnailUpdate(False)
    #                     OpenMayaSet()
    #     elif LoadSet == 'load no references':
    #         cmds.file(AFliePath, o=True, f=True, lnr=True)
    #         cmds.renderThumbnailUpdate(False)
    #         OpenMayaSet()
    #     else:
    #         cmds.file(AFliePath, o=True, f=True)
    #         cmds.renderThumbnailUpdate(False)
    #         OpenMayaSet()

    # def OpenFiles(self, PATH=""):
    #     FilePath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     WOFilesPath = str(FilePath) + str(PATH)
    #     os.startfile(FilePath)

    # def GetRidOfVisonCopy(self, PA):
    #     FilePaths = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     a = re.split('/', FilePaths)
    #     FilePathsshot = a[0] + '/' + a[1] + '/' + a[2] + '/' + a[3] + '/' + a[4] + '/' + a[5] + '/'
    #     OFilesPath = FilePathsshot + PA
    #     WFilenames = cmds.textScrollList('FileViewUI', q=True, si=True)
    #     if WFilenames:
    #         for WFilename in WFilenames:
    #             OF = re.split(' ', WFilename)
    #             OFliePath = OF[0]
    #             OFlieName = OF[0][:-8] + '.ma'
    #             SourceFliePath = FilePaths + OFliePath
    #             CopyPath = OFilesPath + OFlieName
    #             cmds.sysFile(SourceFliePath, copy=CopyPath)
    #
    #     else:
    #         cmds.confirmDialog(title='Confirm', message='Please select at least one file!', button=['Yes'],
    #                            defaultButton='Yes', icon='warning')

    # def Referencein(self):
    #     FilePaths = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     WFilenames = cmds.textScrollList('FileViewUI', q=True, si=True)
    #     if WFilenames:
    #         for WFilename in WFilenames:
    #             Filename = re.split(' ', WFilename)
    #             cmds.file(FilePaths + Filename[0], r=True)
    #
    #     else:
    #         cmds.confirmDialog(title='Confirm', message='Please select at least one file!', button=['Yes'],
    #                            defaultButton='Yes', icon='warning')

    # def SetAuthor(self):
    #     EPName = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     FourName = cmds.textFieldGrp('FourUI', q=True, text=True)
    #     if FourName:
    #         nukefile = ('{0}txt/{1}.txt').format(self.scriptPath, EPName)
    #         if os.path.isfile(nukefile):
    #             fnukes = open(nukefile, 'r').readlines()
    #             for fnuke in fnukes:
    #                 cutfnuke = fnuke.split('|')
    #                 if re.search(FourName, cutfnuke[0]):
    #                     cmds.textFieldGrp('Author', e=True, text=str(cutfnuke[2]))
    #                     break
    #                 else:
    #                     cmds.textFieldGrp('Author', e=True, text='----')
    #
    #         else:
    #             cmds.textFieldGrp('Author', e=True, text='----')

    # def BackupCurrentShotList(self):
    #     PathListCurrent = []
    #     path = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     if path:
    #         FilePath = path + 'lighting'
    #         FilePathABC = path + 'alembic'
    #         CopyPath = FilePath.replace(PROJECTPLATE, LOCALPLATE)
    #         CopyPathABC = FilePathABC.replace(PROJECTPLATE, LOCALPLATE)
    #         if os.path.isdir(CopyPath):
    #             pass
    #         else:
    #             cmds.sysFile(CopyPath, makeDir=True)
    #         if os.path.isdir(CopyPathABC):
    #             pass
    #         else:
    #             cmds.sysFile(CopyPathABC, makeDir=True)
    #         PathListCurrent.append('robocopy ' + FilePath + ' ' + CopyPath + ' /E /w:3 /r:1 /XD history')
    #         PathListCurrent.append('robocopy ' + FilePathABC + ' ' + CopyPathABC + ' /E /w:3 /r:1 /XD history')
    #     return PathListCurrent

    # def WriteBatCurrent(self):
    #     Bat = 'C:/TEMP/' + PROJECTNAME + '_Current_BackupFiles.bat'
    #     if os.path.isfile(Bat):
    #         os.remove(Bat)
    #     Commends = BackupCurrentShotList()
    #     if Commends:
    #         for Commend in Commends:
    #             f = open(Bat, 'a')
    #             f.write(Commend + '\r\n')
    #             f.close()
    #
    #         if os.path.isfile(Bat):
    #             os.startfile(Bat)

    # def CurrentFile(self):
    #     SceneName = cmds.file(q=True, sceneName=True)
    #     if SceneName != '':
    #         SceneNameTBmayas = re.split('/', SceneName)
    #         MayePath = ('/').join(SceneNameTBmayas[0:5]) + '/'
    #         MayeName = SceneNameTBmayas[(-1)]
    #         EPName = SceneNameTBmayas[3]
    #         for SceneNameTBmaya in SceneNameTBmayas:
    #             if SceneNameTBmaya.endswith('.ma'):
    #                 SplitMayaPath = re.split(SceneNameTBmaya, SceneName)
    #                 SceneNameNumber = SceneNameNumber = SceneNameTBmayas[(-1)][:20]
    #                 SceneNameNumberCut = SceneNameNumber.split('-')
    #                 FourName = int(SceneNameNumberCut[1])
    #
    #         cmds.textFieldGrp('MayaPathSUI', e=True, tx=MayePath)
    #         cmds.textFieldGrp('MayaShotSUI', e=True, tx=SceneNameNumber)
    #         cmds.textFieldGrp('MayaPathCUI', e=True, tx=SplitMayaPath[0])
    #         cmds.textFieldButtonGrp('MayaNameSUI', e=True, tx=MayeName)
    #         cmds.optionMenuGrp('EpSUI', e=True, v=EPName)
    #         cmds.textFieldGrp('FourSUI', e=True, tx=FourName)

    # def MayaFileName(self):
    #     SceneName = cmds.file(q=True, sceneName=True)
    #     SceneNameTBmayas = re.split('/', SceneName)
    #     MayePath = ('/').join(SceneNameTBmayas[0:5]) + '/'
    #     MayaName = SceneNameTBmayas[(-1)]
    #     cmds.textFieldButtonGrp('MayaNameSUI', e=True, tx=MayaName)

    # def EPS(self):
    #     EPfiles = cmds.optionMenuGrp('EpSUI', q=True, v=True)
    #     cmds.textFieldGrp('MayaPathSUI', e=True, tx=PROJECTSHOWPATH + EPfiles + '/')
    #     cmds.textFieldGrp('MayaShotSUI', e=True, tx='')

    # def FileS(self):
    #     cmds.textScrollList('WorkFileViewSUI', e=True, ra=True)
    #     cmds.textScrollList('OkFileViewSUI', e=True, ra=True)
    #     cmds.textScrollList('AkFileViewSUI', e=True, ra=True)
    #     FourName = cmds.textFieldGrp('FourSUI', q=True, tx=True)
    #     EPfiles = cmds.optionMenuGrp('EpSUI', q=True, v=True)
    #     FilePaths = PROJECTSHOWPATH + EPfiles + '/'
    #     Files = os.listdir(FilePaths)
    #     for File in Files:
    #         if re.search(FourName, File):
    #             cmds.textFieldGrp('MayaPathSUI', e=True, tx=PROJECTSHOWPATH + EPfiles + '/' + File + '/')
    #             cmds.textFieldGrp('MayaShotSUI', e=True, tx=File)

    # def SaveNameSet(self):
    #     PATH = "FileViewUI"
    #     PATHB = "MayaNameSUI"
    #     AkFilenames = cmds.textScrollList(PATH, q=True, si=True)
    #     for AkFilename in AkFilenames:
    #         AkF = re.split(' ', AkFilename)
    #         cmds.textFieldButtonGrp(PATHB, e=True, tx=AkF[0])

    # def aniPublish(self,*args):
    #     ConfirmSave = 'no'
    #     global PROJECTSPATH
    #     MayaMainPath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)
    #     EPName = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0].split('   /    ')[0]
    #     ShotName = cmds.textScrollList('ShotsFloderUI', q=True , selectItem=True )[0]
    #     MayaName = cmds.textFieldButtonGrp('MayaNameSUI', q=True, tx=True)
    #     WFilesPath = MayaMainPath + '/'+MayaName
    #     #LocalWFilesPath = MayaMainPath.replace(PROJECTPLATE, LOCALPLATE) + MayaName
    #     if os.path.isdir(MayaMainPath.replace(PROJECTPLATE, LOCALPLATE)):
    #         pass
    #     else:
    #         cmds.sysFile(MayaMainPath.replace(PROJECTPLATE, LOCALPLATE), makeDir=True)
    #     if os.path.isfile(WFilesPath):
    #         CheckSaveFile = cmds.confirmDialog(title='Confirm', message=MayaName + '\n\nalready exists,do you want to override it?', button=['Yes', 'No', 'Cancel'], defaultButton='Yes', cancelButton='Cancel', dismissString='Cancel', icon='question')
    #         if CheckSaveFile == 'Cancel':
    #             pass
    #         else:
    #             if CheckSaveFile == 'Yes':
    #                 #OffAllWindows()
    #                 self.SwitchToMaster()
    #                 #SETStartFrame()
    #                 cmds.file(rename=WFilesPath)
    #                 cmds.file(save=True, type='mayaAscii')
    #                 #cmds.sysFile(WFilesPath, copy=LocalWFilesPath)
    #                 ConfirmSave = 'yes'
    #             if CheckSaveFile == 'No':
    #                 pass
    #     else:
    #         #OffAllWindows()
    #         self.SwitchToMaster()
    #         #SETStartFrame()
    #         cmds.file(rename=WFilesPath)
    #         cmds.file(save=True, type='mayaAscii')
    #         #cmds.sysFile(WFilesPath, copy=LocalWFilesPath)
    #         ConfirmSave = 'yes'
    #     if cmds.checkBox('Cam', q=True, v=True) == True:
    #         camPath = PROJECTSPATH + EPName+'/Projects/'+IdeaName+'/ANI/AniCamera/'+ShotName
    #         try:
    #             print ('aaa'+camPath)
    #             self.pubCam(camPath)
    #             #self.MayaFiles()
    #         except:
    #             print 'no cam'
    #     if cmds.checkBox('FBX', q=True, v=True) == True:
    #         fbxPath = PROJECTSPATH+EPName+'/Projects/'+IdeaName+'/ANI/AniFBX/'+ShotName
    #         try:
    #             print ('bbb'+fbxPath)
    #             self.pubFBX(fbxPath)
    #         except:
    #             print ('no fbx')
    #     if cmds.checkBox('Playblast', q=True, v=True) == True:
    #         # try:
    #         self.pubPlayblast()
    #         # except:
    #             # print 'no Playblast'
    #     if ConfirmSave == 'yes':
    #         cmds.confirmDialog(title='Confirm', message=u'保存 ' + MayaName + u' 成功！查看log了解更多细节', button=['Yes'], defaultButton='Yes', icon='information')
    #         self.MayaFiles()

    # def _get_curennt_data(self):
    #     Root = self.projectSetting()['rootPath']
    #     current_project = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     current_idea = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0].split('   /    ')[0]
    #     #current_idea_data = self.get_current_idea_data()
    #     current_shot = cmds.textScrollList('ShotsFloderUI', q=True , selectItem=True )[0]
    #     current_mayafile = cmds.textFieldButtonGrp('MayaNameSUI', q=True, tx=True)
    #     return (Root, current_project, current_idea, current_shot, current_mayafile)

    # def make_path(self, current_project, current_idea, current_idea_data, current_scene, dir_name):
    #     dir = '{0}_{1}_{2}'.format(current_project, current_idea, current_scene)
    #     path = '{0}/{1}/{2}/{3}/{4}/{5}/{6}'.format(self.projectSetting()['rootPath'], current_project, 'project',
    #                                                 current_idea_data, 'Ani', dir_name, dir)
    #     fileinfo = QtCore.QFileInfo(path)
    #     if fileinfo.exists() is False:
    #         ani_mkpath = QtCore.QDir()
    #         ani_mkpath.mkpath(path)
    #     return (path, dir)

    # def CurrentMayaPath(self):
    #     SceneName = cmds.file(q=True, sceneName=True)
    #     SceneNameTBmayas = re.split('/', SceneName)
    #     for SceneNameTBmaya in SceneNameTBmayas:
    #         if SceneNameTBmaya.endswith('.ma'):
    #             SplitMayaPath = re.split(SceneNameTBmaya, SceneName)
    #             cmds.textFieldGrp('MayaPathCUI', e=True, tx=SplitMayaPath[0])

    # def MayaNameABC(self, Need):
    #     MayaFileName()
    #     Shot = cmds.textFieldGrp('MayaShotUI', q=True, tx=True)
    #     MayaName = cmds.textFieldButtonGrp('MayaNameSUI', q=True, tx=True)
    #     MayeNameFs = MayaName.split('.')
    #     if Shot:
    #         NewMayaName = re.sub(MayeNameFs[0], Shot + '_ANI4ABC_' + Need, MayaName)
    #         cmds.textFieldButtonGrp('MayaNameSUI', e=True, tx=NewMayaName)

    # def path(self):
    #     EPName = cmds.optionMenuGrp('EpUI', q=True, v=True)
    #     IdeaName = cmds.textScrollList('IdeasFloderUI', q=True, selectItem=True)[0]
    #     StageName = cmds.textScrollList('StagesFloderUI', q=True, selectItem=True)[0]
    #     ShotName = cmds.textScrollList('ShotsFloderUI', q=True, selectItem=True)[0]
    #     FilePath = cmds.textFieldGrp('MayaPathUI', q=True, tx=True)

    def autoName(self):
        current_project, current_date, current_idea, current_idea_zh, current_stage, path = self._get_current_data()
        extension = self.get_suffix()
        if current_idea:
            self.ui.name_line.setText(current_idea + '_C1' + extension)
        else:
            cmds.confirmDialog(title='Error', message=u'请先设置保存到的文件夹！', button=['Yes'], defaultButton='Yes',
                               icon='information')

    def get_suffix(self):
        publish_type = self.ui.publishType_comb_ac.currentText()
        if publish_type == "Pose":
            suffix = ".pose"
        else:
            suffix = ".anim"
        return suffix

    def addVersion(self):
        MayaName = self.ui.name_line.text()
        suffix = self.get_suffix()

        MayeNameFs = MayaName.rsplit('.')[0]
        ma_file = MayeNameFs.split("_v")[0]
        version = MayeNameFs.split("_v")[1]
        Version_add = '%03d' % (int(version) + 1)
        MayeNameNew = ma_file + '_v' + str(Version_add) + suffix
        self.ui.name_line.setText(MayeNameNew)

    def addShot(self):
        MayaName = self.ui.name_line.text()

        MayeNamePer = MayaName.rsplit('_', 1)[0]
        MayeNameFs = MayaName.rsplit('.', 1)[0].rsplit('_C', 1)[-1]
        MayeNamePost = MayaName.rsplit('.', 1)[-1]

        # shot = MayeNameFs.split("C")[1]
        Version_add = int(MayeNameFs) + 1
        MayeNameNew = MayeNamePer + '_C' + str(Version_add) + '.' + MayeNamePost
        self.ui.name_line.setText(MayeNameNew)
        # FilePath = str(self.ui.aniPath_label.text())
        # if os.path.exists(FilePath):
        #     if FilePath.split('/')[-1] == '':
        #         ShotFolder = os.listdir(FilePath)
        #         num = str(len(ShotFolder) + 1)
        #         os.makedirs(FilePath + 'C' + num)
        #         self.getShot()
        #     else:
        #         newFilePath = FilePath.split('/C')[0]
        #         ShotFolder = os.listdir(newFilePath)
        #         num = str(len(ShotFolder) + 1)
        #         os.makedirs(newFilePath + '/C' + num)
        #         self.getShot()
        # else:
        #     print(FilePath + u"不存在")


app = None
if not QtWidgets.QApplication.instance():
    app = QtWidgets.QApplication(sys.argv)


def ShotsManager_Run():
    global win
    try:
        win.close()
    except:
        pass

    win = ShotsManagerMayaUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()
