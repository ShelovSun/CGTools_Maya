#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ShotsManagerMaya Created: 19/10/2020 by Sunxh<175702994@qq.com>
# log:大改QT


import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import sys
from functools import partial

from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from utils import jsonHelper, publish, sequenceplayer, animation
from widgets import myWidget

if 'C:\\CgTeamWork_v6.2\\bin\\base' not in sys.path:
    sys.path.append('C:\\CgTeamWork_v6.2\\bin\\base')


try:
    import cgtw2
    t_tw = cgtw2.tw()

    login = t_tw.login.is_login()
    if not login:
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：", u"<h3>请先登入CGTeamWork !</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.exec_()
except:
    msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                u"<h3>请先登入CGTeamWork !  并且安装在C盘标准目录下!</h3>")
    msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
    msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
    msg.exec_()


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)


class ShotsManagerMayaUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    VERSION = "3.0.1"

    def __init__(self):
        super(ShotsManagerMayaUI, self).__init__()
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.SYSTEMP = os.environ['TEMP'].replace('\\', '/') + '/'
        self.Pub = publish.Publish()
        self.RootPath = self.projectSetting()['rootPath']
        self.sortReverse = True
        ui = QtCore.QFile('%s/ui/ShotsManagerForMaya.ui' % self.scriptsPath)
        ui.open(QtCore.QFile.ReadOnly)
        self.ui = QtUiTools.QUiLoader().load(ui)
        ui.close()
        self.init_UI()

    def init_UI(self):
        self.setCentralWidget(self.ui)
        self.setWindowTitle('ShotsManager ' + self.VERSION)
        pos, size, project, eps, sort = self.readSettings()

        if pos is not None and size is not None:
            self.resize(size)
            self.move(pos)
        else:
            self.resize(1200, 600)
            self.move(2000, 120)

        if sort == "false":
            self.sortReverse = False

        self.getProject()
        if project is not None:
            self.ui.Project_ComboBox.setCurrentIndex(project)
        else:
            self.ui.Project_ComboBox.setCurrentIndex(0)
        self.getIdea_TW()
        if eps is not None:
            self.ui.ani_idea_listWgt.setCurrentRow(eps)
        else:
            self.ui.ani_idea_listWgt.setCurrentRow(0)

        self.getStyleSheet()

        '''上侧栏'''
        self.ui.Project_ComboBox.currentIndexChanged.connect(self.changeProject)
        self.ui.openFloder_bttn.clicked.connect(self.openFolder)
        self.ui.setting_bttn.setIcon(QtGui.QIcon('%s/icon/setting.png' % self.scriptsPath))
        self.ui.setting_bttn.clicked.connect(self.toolSetting_UI)

        '''主界面栏'''
        self.ui.main_splitter.setSizes([50, 50, 50, 300])
        self.getStage()
        # self.getShot()
        self.getPath()
        self.getFile()
        self.ui.sort_bttn.setIcon(QtGui.QIcon('%s/icon/sort.png' % self.scriptsPath))
        self.ui.sort_bttn.clicked.connect(self.changeIdeaSort)
        self.ui.key_line.textChanged.connect(self.getIdea_TW)
        self.ui.key_line.addAction(QtGui.QIcon('%s/icon/search.png' % self.scriptsPath),
                                   QtWidgets.QLineEdit.LeadingPosition)
        self.ui.ani_idea_listWgt.currentItemChanged.connect(self.changeIdea)
        self.ui.stages_listWgt.currentItemChanged.connect(self.changeStage)
        # self.ui.ani_shot_listWgt.currentItemChanged.connect(self.changeShot)
        self.ui.aniAST_listWgt.currentItemChanged.connect(self.changeFile)
        self.ui.aniAST_listWgt.itemDoubleClicked.connect(self.openFile)
        self.ui.aniAST_listWgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.ui.aniAST_listWgt.customContextMenuRequested.connect(self.show_menu)

        '''右侧属性栏'''
        self.ui.Preview_label = myWidget.PreviewLabel(self.ui.frams_lineEdit)
        self.ui.verticalLayout_Preview.addWidget(self.ui.Preview_label)
        self.ui.Attr_splitter.setSizes([500, 500])
        self.playerSet()

        self.ui.apply_option_combox.addItems(['replace', 'replace all', 'insert', 'merge'])
        self.ui.pose_percent_groupBox.setVisible(False)
        self.ui.apply_option_groupBox.setVisible(False)
        '''下侧栏'''
        self.ui.autoName_bttn.clicked.connect(self.autoName)
        self.ui.add_shot_bttn.clicked.connect(self.addShot)
        self.ui.add_version_bttn.clicked.connect(self.addVersion)
        self.ui.Publish_bttn.clicked.connect(self.aniPublish)
        self.ui.Publish_bttn.setStyleSheet("QPushButton{background: #00e6cf; color: #000000;}")

    def getStyleSheet(self):
        style_sheet_path = '%s/qss/dark.qss' % self.scriptsPath
        with open(style_sheet_path) as (file):
            str = file.read()
        self.setStyleSheet(str)

    @staticmethod
    def readSettings():
        settings = QtCore.QSettings('Ani_Tools', 'Ani_Tools_Settings')
        pos = settings.value('pos')
        size = settings.value('size')
        project = settings.value('project')
        eps = settings.value('eps')
        sort = settings.value('sort')

        return pos, size, project, eps, sort

    def rememberSettings(self):
        settings = QtCore.QSettings('Ani_Tools', 'Ani_Tools_Settings')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
        settings.setValue('project', self.ui.Project_ComboBox.currentIndex())
        settings.setValue('eps', self.ui.ani_idea_listWgt.currentRow())
        settings.setValue('sort', self.sortReverse)

    def closeEvent(self, event):
        self.rememberSettings()

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

        if self.ui.ani_idea_listWgt.currentItem():
            current_idea = str(self.ui.ani_idea_listWgt.currentItem().text().split("   /   ")[0])
        else:
            current_idea = "None"
        current_stage = self.ui.stages_listWgt.currentItem().text()

        return current_project, current_idea, current_stage

    def getProject(self):
        self.ui.Project_ComboBox.addItems(self.projectSetting()['projects'])

    def getIdea_TW(self):
        """根据CGT和项目获得集数显示"""
        current_project = self.ui.Project_ComboBox.currentText()
        keyword = self.ui.key_line.text()
        sortReverse = self.sortReverse
        TW_proj = self.projectSetting()['projectdiction'][current_project]
        t_eps_ids = t_tw.info.get_id(TW_proj, 'chuangyi', [])
        eps = t_tw.info.get(TW_proj, 'chuangyi', t_eps_ids,
                            ['chuangyi.creatdate', 'chuangyi.entity', 'chuangyi.chname'])
        epslist = []
        for info in eps:
            aa = "{0}_{1}".format(info['chuangyi.creatdate'],
                                  info['chuangyi.entity']) + '   /   ' + info['chuangyi.chname']
            epslist.append(aa)
        epslist.sort(reverse=sortReverse)
        self.ui.ani_idea_listWgt.clear()
        for i in epslist:
            if i.lower().find(keyword.lower()) != -1:
                item = QtWidgets.QListWidgetItem()
                item.setText(i)
                self.ui.ani_idea_listWgt.addItem(item)

    def getStage(self):
        """ 设置阶段 """
        self.ui.stages_listWgt.addItems(self.projectSetting()['stages'])  # 设置阶段显示
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
            # model = QtWidgets.QFileSystemModel()
            # model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)
            # model.setRootPath(file_path)
            # self.ui.aniAST_listWgt.setModel(model)
            dir = QtCore.QDir(file_path)
            for file in dir.entryList(QtCore.QDir.NoDotAndDotDot ^ QtCore.QDir.AllEntries):
                if file.endswith('.ma') or file.endswith('.mb') or file.endswith('.fbx') or \
                        file.endswith('.abc') or file.endswith('.anim') or file.endswith('.pose'):
                    item = QtWidgets.QListWidgetItem()
                    item.setText(file)
                    self.ui.aniAST_listWgt.addItem(item)

    def changeIdeaSort(self):
        """
        改变创意排序
        :return:
        """
        if self.sortReverse:
            self.sortReverse = False
            self.getIdea_TW()
        else:
            self.sortReverse = True
            self.getIdea_TW()

    def getPath(self):
        """根据Project设置路径"""
        current_project, current_idea, current_stage = self._get_current_data()
        self.ui.aniPath_label.setText('{0}/{1}/Projects'.format(self.RootPath, current_project))
        if current_idea != "None":
            self.ui.aniPath_label.setText('{0}/{1}/Projects/{2}'.format(self.RootPath, current_project, current_idea))
            if current_stage != "None":
                self.ui.aniPath_label.setText('{0}/{1}/Projects/{2}/{3}'.format(self.projectSetting()['rootPath'],
                                                                                current_project,
                                                                                current_idea,
                                                                                current_stage))

    def changeProject(self):
        """触发：更新path，更新idea，更新文件"""
        self.getPath()
        self.getIdea_TW()
        self.getFile()

    def changeIdea(self):
        """切换创意触发：得到文件；设置Path"""
        self.ui.aniAST_listWgt.clear()
        current_project, current_idea, current_stage = self._get_current_data()
        if current_idea != "None":
            shot_path = '{0}/{1}/Projects/{2}/{3}'.format(self.RootPath, current_project,
                                                          current_idea, current_stage)
            self.ui.aniPath_label.setText(shot_path)
            self.getFile()
        self.ui.aniAST_listWgt.setCurrentRow(0)

    def changeStage(self):
        """切换阶段触发：更新path；更新镜头，更新文件名"""
        current_project, current_idea, current_stage = self._get_current_data()
        shot_path = '{0}/{1}/Projects/{2}/{3}'.format(self.RootPath, current_project,
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
        """ 切换动画文件触发：更新path """
        filename = str(self.ui.aniAST_listWgt.currentItem().text())
        self.ui.name_line.setText(filename)

    def openFile(self):
        file_name = str(self.ui.aniAST_listWgt.currentItem().text())
        file_path = "{0}/{1}".format(self.ui.aniPath_label.text(), file_name)
        cmds.file(file_path, o=True, f=True)

    def openFolder(self):
        FilePath = self.ui.aniPath_label.text()
        os.startfile(FilePath)

    def show_menu(self, point):
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

            if currentItem.text().endswith('.anim'):
                open_action.triggered.connect(self.openFile)
            else:
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

    def check_before_publish(self):
        """ 发布前检查 """
        mll_list = ['AbcExport.mll', 'AbcImport.mll', 'fbxmaya.mll']
        for mll in mll_list:
            if self.Pub.pluginInfo(mll) is False:
                QtWidgets.QMessageBox.warning(self, '警告', '未发现{}，请加载!'.format(mll))
                return

        self.Pub.removeUnknownNodes()
        self.Pub.removeModelChangeError()

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

    def aniPublish(self):
        """
        发布动作
        :return:
        """
        if self.check_before_publish() is False:
            return
        else:
            current_project, current_idea, current_stage = self._get_current_data()
            _log = "log:"
            ani_file_name = self.ui.name_line.text()
            if current_project is None or current_idea is None:
                cmds.warning(u'请选择要发布的文件路径')
                return
            ani_file_Path = '{0}/{1}/Projects/{2}/{3}/{4}'.format(self.RootPath, current_project, current_idea,
                                                                  current_stage, ani_file_name)

            '''======= 保存ma ======================================='''
            if self.ui.maya_cBox.isChecked():
                try:
                    self.saveMaya(ani_file_Path)
                    _log += u"\n> 动画档已发布"
                except Exception as e:
                    _log += u"\n> 动画档发布失败请检查"
                ''' ===============拍icon=============================================== '''
                iconPath = str('%s/snapshot/thumbnail.jpg' % self.tempPath)
                sequencePath = self.tempPath + "/sequence"
                if publishType == "Animation":
                    self.Pub.seqshot(sequencePath)
                ''' ===============发布动作库=============================================== '''
                try:
                    self.Pub.makePath(ani_file_Path)
                    animation.saveAnim(path=ani_file_Path,
                                       objects=controls,
                                       time=(start, end),
                                       iconPath=iconPath,
                                       sequencePath=sequencePath,
                                       metadata={'description': u'%s' % characterCHName})
                    _log += u"动作{}已发布".format(actionName)
                except Exception as e:
                    _log += u"动作{0}发布失败：{1}".format(actionName, e)
            '''======== 发布相机 ======================================'''
            if self.ui.Cam_cBox.isChecked():
                camera = cmds.ls('Cam_*', assemblies=True)
                if len(camera) != 1:
                    cmds.confirmDialog(title='Confirm',
                                       message=u'Camera 不存在 或者 不唯一！Camera命名规范:Cam_*',
                                       button=['Yes'],
                                       defaultButton='Yes',
                                       icon='information')
                cam_path = "{0}/{1}/Projects/{2}/ANI/AniCamera".format(self.RootPath, current_project, current_idea)
                try:
                    self.pubCam(cam_path)
                    _log += u"\n> 相机已发布"
                except Exception as e:
                    cmds.warning('AniCamera publish failed.')
                    _log += u"\n> 相机发布失败请检查"

            '''========== 发布fbx ===================================='''
            if self.ui.FBX_cBox.isChecked():
                fbx_path = "{0}/{1}/Projects/{2}/ANI/AniFBX".format(self.RootPath, current_project, current_idea)

                try:
                    self.pubFBX(fbx_path)
                    _log += u"\n> FBX已发布"
                except Exception as e:
                    cmds.warning('AniFBX publish failed.')
                    _log += u"\n> FBX发布失败，请检查"

            '''========= 发布拍屏 ======================================'''
            if self.ui.Pb_cBox.isChecked():
                Pb_file_path = ani_file_Path.replace('.ma', '.mov').replace('AniFile', 'AniPlayblast')
                try:
                    self.pubPlayblast(Pb_file_path)
                    _log += u"\n> 拍屏已发布"
                except Exception as e:
                    cmds.warning('AniFBX publish failed.')
                    _log += u"\n> 拍屏发布失败"

            self.getFile()
            msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                        u"<h3>动画档案发布成功!\n查看log获取更多细节?</h3>")
            msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
            msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            msg.setDetailedText(_log)
            msg.exec_()

    def saveMaya(self, ani_file_Path):
        if QtCore.QFileInfo(ani_file_Path).exists():
            reply = QtWidgets.QMessageBox.question(self, '提示', '文件已存在，确定覆盖吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                cmds.file(rename=ani_file_Path)
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
                cmds.warning('Can not find {0}:DeformationSystem'.format(i.split(':')[0]))
            self.Pub.exportFBX(True, minTime, maxTime, '{0}/{1}.fbx'.format(FilePath, aniFbxName))
        cmds.select(clear=True)

    def pubCam(self, FilePath):
        if os.path.exists(FilePath) is False:
            os.makedirs(FilePath)
        if len(cmds.ls('Cam_*', long=True, assemblies=True)) == 1:
            camera_name = cmds.ls('Cam_*', long=True, assemblies=True)[0]
            camFileName = camera_name.split('|')[1]
            cmds.setAttr("%s.filmFit" % camFileName, 1)
            minTime = cmds.playbackOptions(query=True, minTime=True)
            maxTime = cmds.playbackOptions(query=True, maxTime=True)
            self.Pub.exportAlembic(minTime, maxTime, camera_name, '{0}/{1}.abc'.format(FilePath, camFileName))
            cmds.select(camera_name)
            self.Pub.exportFBX(False, minTime, maxTime, '{0}/{1}.fbx'.format(FilePath, camFileName))

    def pubPlayblast(self, movPath):
        cam = cmds.ls('Cam_*', assemblies=True)
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
        current_project, current_idea, current_stage = self._get_current_data()
        if current_idea:
            self.ui.name_line.setText(current_idea + '_C1' + '_v001.ma')
        else:
            cmds.confirmDialog(title='Error', message=u'请先设置保存到的文件夹！', button=['Yes'], defaultButton='Yes',
                               icon='information')

    def addVersion(self):
        MayaName = self.ui.name_line.text()
        MayeNameFs = MayaName.split('.ma')[0]
        ma_file = MayeNameFs.split("_v")[0]
        version = MayeNameFs.split("_v")[1]
        Version_add = '%03d' % (int(version) + 1)
        MayeNameNew = ma_file + '_v' + str(Version_add) + '.ma'
        self.ui.name_line.setText(MayeNameNew)

    def addShot(self):
        MayaName = self.ui.name_line.text()
        MayeNamePer = MayaName.split('_')[0] + '_' + MayaName.split('_')[1]
        MayeNameFs = MayaName.split('_')[2]
        MayeNamePost = MayaName.split('_')[-1]

        shot = MayeNameFs.split("C")[1]
        Version_add = int(shot) + 1
        MayeNameNew = MayeNamePer + '_C' + str(Version_add) + '_' + MayeNamePost
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
