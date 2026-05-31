#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os
import sys

# reload(publish)
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance
from utils import jsonHelper, publish


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)


class ModPubToolsUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):

    def __init__(self):
        super(ModPubToolsUI, self).__init__()
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
        self.setWindowTitle('Mod Publish Tool ')
        self.init_ui()

    def init_ui(self):
        f = QtCore.QFile('%s/ui/modPublish.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.ui.icon_label.setPixmap(QtGui.QPixmap('%s/icons/question.png' % self.scriptsPath))
        self.ui.render_bttn.setIcon(QtGui.QPixmap('%s/icons/shot.png' % self.scriptsPath))
        self.ui.Preview_label.setStyleSheet(
            "background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(35, 35, 35, 100),  stop:1 rgba(35, 35, 35, 255));")
        modPub = publish.Publish()
        self.update_type()
        self.ui.Cancel_bttn.clicked.connect(self.closeWin)
        ''' 检查插件'''
        # if modPub.pluginInfo('redshift4maya.mll') is False:
        # QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
        # return
        if modPub.pluginInfo('AbcExport.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 AbcExport，请加载')
            return
        if modPub.pluginInfo('AbcImport.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 AbcImport，请加载')
            return
        ''' 列出资产有且只有一个，建立path '''
        if len(cmds.ls('*_*_AST', type='transform')) == 1:
            projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
            characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
            if projectName not in self.projectSetting()['projects']:
                QtWidgets.QMessageBox.warning(self, 'Warning', 'Check your projects name!!!')
                return
            publishType = self.ui.publishType_comb.currentText()
            path = str('%s/%s/%s/%s/%s/' % (
                self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType,
                characterName))
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning',
                                          'Can not find *_*_AST, or more than one *_*_AST, please check!!!')
            return

        self.ui.Note_label.setText((u"<h3>确定发布 {} 到 \n{} ？</h3>").format(characterName, path))
        self.renderIcon()
        # self.ui.Yes_bttn.clicked.connect(lambda: self._modPublish(projectName, characterName, publishType, path))
        self.ui.Yes_bttn.clicked.connect(self._modPublish)
        self.ui.render_bttn.clicked.connect(self.renderIcon)
        self.ui.publishType_comb.currentIndexChanged.connect(self.type_change)

    def renderIcon(self):
        '''拍摄icon并显示在标签'''
        modPub = publish.Publish()
        localiconpath = modPub.makePath(str('%s/snapshot' % self.tempPath))
        # localicon = "%s/snapShotTemp.png" %localiconpath
        try:
            modPub.snapshot(localiconpath, "snapShotTemp", need_createHistory=False)
            localicon = "%s/snapShotTemp.png" % localiconpath
            print("%s is snapshoted !!" % localicon)
            self.ui.Preview_label.setPixmap(QtGui.QPixmap(localicon))
        except:
            print("Error : snapshot is stuck !!")
            self.ui.Preview_label.clear()

    def update_type(self):
        ''' 根据json，设置type显示 '''
        self.ui.publishType_comb.addItems(self.projectSetting()['type'])

    def type_change(self):
        ''' 列出资产有且只有一个，建立path '''
        projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
        characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
        publishType = self.ui.publishType_comb.currentText()
        path = str('%s/%s/%s/%s/%s/' % (self.projectSetting()['rootPath'], projectName,
                                        self.projectSetting()['assetFolder'], publishType,
                                        characterName))
        self.ui.Note_label.setText((u"<h3>确定发布 {} 到 \n{} ？</h3>").format(characterName, path))

    def closeWin(self):
        self.close()

    def projectSetting(self):
        data = jsonHelper.readDictFromFile(
            '%s/AssetsManagerForMaya/config/projectSetting.json' % self.scriptsPath.replace(
                "tools_model/Mod_Publish_Tool", ""))
        return data

    def _modPublish(self):
        '''
        发布模型
        '''
        modPub = publish.Publish()
        projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
        characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
        publishType = self.ui.publishType_comb.currentText()
        path = str('%s/%s/%s/%s/%s/' % (
            self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType,
            characterName))
        modPub.makePath(path)
        log = ""
        ''' 如果没有CGT则创建CGT  '''
        if not self.createAssetsForCGT(projectName, characterName, publishType):
            reply = QtWidgets.QMessageBox.question(self, '提示', 'CGT上已有重名资产，确定继续发布吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                log = log + u"> CGT上已有重名资产已覆盖"
                pass
            else:
                return
        else:
            log = log + (u"> 已在CGT上建立资产：{0}").format(characterName)
        ''' 清理  '''
        modPub.removeAllNameSpace()
        modPub.removeAllDisplayLayer()
        modPub.removeUnknownNodes()
        modPub.removeUnusedShader()
        modPub.removeAllAOV()
        modPub.removeAllAnimLayer()
        modPub.removeAllRenderLayer()
        modPub.modClean()
        log = log + u"\n> 文件已清理"
        ''' 复制xgen，texture并重定向 '''
        if self.ui.xgen_cBox.isChecked():
            try:
                modPub.makePath(str('%s/xgen/collections' % path))
                modPub.repathXGenData(str('%s/xgen/collections' % path))
                log = log + u"\n> Xgen已发布"
            except:
                log = log + u"\n> Xgen发布失败请检查"
        else:
            log = log
        if self.ui.textures_cBox.isChecked():
            try:
                modPub.makePath(str('%s/Texture' % path))
                modPub.repathTexture(str('%s/Texture' % path))
                log = log + u"\n> Texture已发布"
            except:
                log = log + u"\n> Texture发布失败请检查"
        else:
            log = log
        ''' 不存在icon则拍屏icon '''
        modPub.makePath(str('%s/%s' % (path, self.projectSetting()['iconFolder'])))
        iconpath = str('%s/%s/%s.png' % (path, self.projectSetting()['iconFolder'], characterName))
        # if os.path.exists(iconpath) is False:
        try:
            modPub.snapshot(str('%s/%s' % (path, self.projectSetting()['iconFolder'])), characterName)
            print("new icon is snapshoted !!")
            try:
                self.createImageForCGT(projectName, characterName, iconpath)
                self.createTask(projectName, characterName, iconpath)
                print("icon is published !!")
            except:
                print("icon is not published !!")
            log = log + u"\n> 新icon图标已发布"
        except:
            log = log
        ''' 保存mod文件 '''
        modPub.makePath(str('%s/%s' % (path, self.projectSetting()['modelFolder'])))
        modPub.saveToServer(path, self.projectSetting()['modelFolder'], characterName,
                            self.projectSetting()['modelFile'], self.projectSetting()['mayaFormat'])
        log = log + u"\n> Mod发布成功"
        '''  保存xgen文件'''
        if self.ui.xgen_cBox.isChecked():
            modPub.makePath(str('%s/%s' % (path, self.projectSetting()['xgenFileFolder'])))
            modPub.saveXGenFile(characterName, projectName, path, self.projectSetting()['xgenFileFolder'],
                                self.projectSetting()['xgenFile'], self.projectSetting()['mayaFormat'])
        # cmds.file(force=True, new=True)
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：", u"<h3>组件发布成功!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(log)
        msg.exec_()

    def createAssetsForCGT(self, proj_name, assets_name, assets_type):
        '''
        建立CGT
        '''
        sys.path.append('C:/CgTeamWork_v6.2/bin/base/')
        import cgtw2
        t_tw = cgtw2.tw()
        projectdiction = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=projectdiction, module='asset',
                                            filter_list=[['asset.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            # t_tw.info.create(db='proj_ffa_0', module='asset', sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type, 'asset.zhizuoren': autor, 'asset.zichanguishu': proj_name}, is_return_id=True)
            infoID = t_tw.info.create(db=projectdiction, module='asset',
                                      sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type,
                                                      'asset.cn_name': u"#自动创建"}, is_return_id=True)
            return True

    def createImageForCGT(self, proj_name, assets_name, assets_icon):
        '''
        CGT没有icon则发布icon
        '''
        import cgtw2
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_asset_ids = t_tw.info.get_id(db=TW_proj, module='asset', filter_list=[['asset.entity', '=', assets_name]])
        TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.image'])
        if TW_dictionInfo[0]['asset.image'] == "":
            t_tw.info.set_image(db=TW_proj, module='asset', id_list=t_asset_ids, field_sign='asset.image',
                                img_path=assets_icon)
        else:
            print(u"已存在:", TW_dictionInfo[0]["asset.image"])

    def createTask(self, proj_name, assets_name, assets_icon):
        '''
        发布任务并提交icon审核
        :param proj_name:
        :param assets_name:
        :param assets_icon:
        :return:
        '''
        import cgtw2
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


def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = ModPubToolsUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()
