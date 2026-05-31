#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import os, sys, socket, maya.OpenMayaUI as omui, maya.cmds as cmds,maya.mel as mel
from utils import jsonHelper,publish
reload(publish)
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)

class RigPubToolsUI(MayaQWidgetDockableMixin,QtWidgets.QMainWindow):

    def __init__(self):
        super(RigPubToolsUI, self).__init__()
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.tempPath = ("{}/AssetsManagerIconTemp").format(os.environ.get('TEMP'))
        self.setWindowTitle('Rig Publish Tool ')
        self.rigPub= publish.Publish()
        self.init_ui()

    def init_ui(self):
        f = QtCore.QFile('%s/ui/rigPublish.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.ui.icon_label.setPixmap(QtGui.QPixmap('%s/icons/question.png' % self.scriptsPath))
        self.ui.render_bttn.setIcon(QtGui.QPixmap('%s/icons/render.png' % self.scriptsPath))
        self.ui.Preview_label.setStyleSheet(
            "background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(35, 35, 35, 100),  stop:1 rgba(35, 35, 35, 255));")
        modPub = publish.Publish()
        self.update_type()
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
            path = str('%s/%s/%s/%s/%s' % (self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType, characterName))
            self.rigPub.makePath(path)
        else:
            QtWidgets.QMessageBox.warning(self, 'Warning',
                                          'Can not find *_*_AST, or more than one *_*_AST, please check!!!')
            return

        self.ui.Note_label.setText((u"<h3>确定发布 {} 到 \n{} ？</h3>").format(characterName, path))
        self.renderIcon()
        # self.ui.Yes_bttn.clicked.connect(lambda: self._modPublish(projectName, characterName, publishType, path))
        self.ui.Yes_bttn.clicked.connect(self._rigPublish)
        self.ui.Cancel_bttn.clicked.connect(self.closeWin)
        self.ui.render_bttn.clicked.connect(self.renderIcon)
        self.ui.publishType_comb.currentIndexChanged.connect(self.type_change)

    def renderIcon(self):
        '''拍摄icon并显示在标签'''
        modPub = publish.Publish()
        localiconpath = modPub.makePath(str('%s/snapshot' %self.tempPath))
        # localicon = "%s/snapShotTemp.png" %localiconpath
        try:
            modPub.snapshot(localiconpath, "snapShotTemp", need_createHistory = False)
            localicon = "%s/snapShotTemp.png" % localiconpath
            print("%s is snapshoted !!"%localicon)
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
        path = str('%s/%s/%s/%s/%s/' % (
            self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType,
            characterName))
        self.ui.Note_label.setText((u"<h3>确定发布 {} 到 \n{} ？</h3>").format(characterName, path))

    def closeWin(self):
        self.close()

    def projectSetting(self):
        data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % self.scriptsPath)
        return data

    def _rigPublish(self):
        '''
        发布绑定
        '''
        projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
        characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
        publishType = self.ui.publishType_comb.currentText()
        path = str('%s/%s/%s/%s/%s/' % (
            self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType,
            characterName))
        ''' 不存在icon则拍屏icon '''
        self.rigPub.makePath(str('%s/%s' % (path, self.projectSetting()['iconFolder'])))
        iconpath = str('%s/%s/%s.png' % (path, self.projectSetting()['iconFolder'], characterName))
        try:
            self.rigPub.snapshot(str('%s/%s' % (path, self.projectSetting()['iconFolder'])), characterName)
            print("new icon is snapshoted !!")
            loga = u"> 新icon图标已发布"
        except:
            loga = " "
        '''  没有CGT则建立CGT '''
        if not self.createAssetsForCGT(projectName, characterName, publishType, iconpath):
            reply = QtWidgets.QMessageBox.question(self, '提示', 'CGT上有重名资产，确定要继续吗？',
                                                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logb = loga + u"\n> CGT上已有重名资产已覆盖"
                pass
            else:
                return
        else:
            logb = loga + (u"\n> 已在CGT上建立资产：{0}").format(characterName)
        '''icon发布上CGT'''
        try:
            self.createImageForCGT(projectName, characterName, iconpath)
            print("icon is published !!")
        except:
            print("icon is not published !!")
        ''' 检查模型属性 '''
        for mesh in cmds.listRelatives('Geometry', ad=1, fullPath=True, type='mesh'):
            cmds.setAttr(('{0}.castsShadows').format(mesh), 1)
            cmds.setAttr(('{0}.receiveShadows').format(mesh), 1)
            cmds.setAttr(('{0}.holdOut').format(mesh), 0)
            cmds.setAttr(('{0}.motionBlur').format(mesh), 1)
            cmds.setAttr(('{0}.primaryVisibility').format(mesh), 1)
            cmds.setAttr(('{0}.visibleInReflections').format(mesh), 1)
            cmds.setAttr(('{0}.visibleInRefractions').format(mesh), 1)
            cmds.setAttr(('{0}.smoothShading').format(mesh), 1)
            cmds.setAttr(('{0}.doubleSided').format(mesh), 1)
        ''' 清理 '''
        self.virusCheck()
        self.rigPub.removeAllNameSpace()
        self.rigPub.removeAllDisplayLayer()
        self.rigPub.removeUnknownNodes()
        self.rigPub.removeUnusedShader()
        self.rigPub.removeModelChangeError()
        logc = logb + u"\n> 文件已清理"
        '''  保存all rig档案'''
        self.rigPub.makePath(str('%s/%s' % (path, self.projectSetting()['rigFolder'])))
        self.rigPub.saveToServer(path, self.projectSetting()['rigFolder'], characterName,
                                 self.projectSetting()['rigFileAll'], self.projectSetting()['mayaFormat'])
        logd = logc + u"\n> all rig已发布"
        hiRigFilePath = '%s/%s/%s_%s.%s' % (
        path, self.projectSetting()['rigFolder'], characterName, self.projectSetting()['rigFileHi'],
        self.projectSetting()['mayaFormat'])
        allRigFilePath = '%s/%s/%s_%s.%s' % (
        path, self.projectSetting()['rigFolder'], characterName, self.projectSetting()['rigFileAll'],
        self.projectSetting()['mayaFormat'])
        ''' 保存hi rig档案'''
        cmds.file(newFile=True, force=True)
        cmds.file(allRigFilePath, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
        if cmds.objExists(('{0}_XGen_GRP').format(characterName)):
            cmds.delete(('{0}_XGen_GRP').format(characterName))
        if cmds.objExists(('{0}_Sim_GRP').format(characterName)):
            cmds.delete(('{0}_Sim_GRP').format(characterName))
        if cmds.objExists(('{0}_HairPoly_GRP').format(characterName)):
            cmds.setAttr(('{0}_HairPoly_GRP.visibility').format(characterName), 1)
        cmds.file(rename=hiRigFilePath)
        cmds.file(save=True, type='mayaAscii')
        loge = logd + u"\n> hi rig已发布"
        ''' fbx发布'''
        self.fbxExport(path, characterName)
        logf = loge + u"\n> fbx已发布"
        ''' 保存render档案'''
        cmds.file(newFile=True, force=True)
        cmds.file(allRigFilePath, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
        cmds.select(cmds.ls(type='mesh'))
        cmds.delete(constructionHistory=True)
        cmds.select(clear=True)
        try:
            sets_list = cmds.lsThroughFilter('defaultSetFilter')
            sets_list.remove('defaultObjectSet')
            sets_list.remove('defaultLightSet')
            if sets_list != []:
                cmds.delete(sets_list)
            cmds.delete('DeformationSystem')
            cmds.delete('other')
        except:
            cmds.warning('Check your Rig Sets or DeformationSystem')

        self.rigPub.removeUnknownNodes()
        self.rigPub.removeUnusedShader()
        self.rigPub.makePath(str('%s/%s' % (path, self.projectSetting()['renderFolder'])))
        self.rigPub.saveToServer(path, self.projectSetting()['renderFolder'], characterName,
                                 self.projectSetting()['renderFile'], self.projectSetting()['mayaFormat'])
        logg = logf + u"\n> Render档已发布"
        ''' 不存在则发布mod '''
        modFile_path = '%s/%s/%s/%s/%s' % (
        path, self.projectSetting()['modelFolder'], characterName, self.projectSetting()['modelFile'],
        self.projectSetting()['mayaFormat'])
        if not os.path.exists(modFile_path):
            self.rigPub.makePath(str('%s/%s' % (path, self.projectSetting()['modelFolder'])))
            cmds.select(clear=True)
            cmds.select('Geometry')
            mel.eval('DeleteHistory;')
            try:
                cmds.select('All_Ctr')
                mel.eval('doDelete;')
            except:
                pass
            try:
                cmds.select('DeformationSystem')
                mel.eval('doDelete;')
            except:
                pass
            try:
                cmds.select('Other')
                mel.eval('doDelete;')
            except:
                pass
            self.rigPub.saveToServer(path, self.projectSetting()['modelFolder'], characterName,
                                     self.projectSetting()['modelFile'], self.projectSetting()['mayaFormat'])
            logh = logg + u"\n> mod档已发布"
        else:
            logh = logg
        cmds.file(newFile=True, force=True)
        cmds.file(allRigFilePath, open=True, type='mayaAscii', ignoreVersion=True, options='v=0', force=True)
        msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：", u"<h3>Rig发布成功!\n查看log获取更多细节?</h3>")
        msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        msg.setDetailedText(logh)
        msg.exec_()

    def createAssetsForCGT(self, proj_name,  assets_name, assets_type, assets_icon):
        '''
        建立CGT
        '''
        sys.path.append('C:/CgTeamWork_v6.2/bin/base/')
        import cgtw2
        t_tw = cgtw2.tw()
        projectdiction = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=projectdiction, module='asset', filter_list=[['asset.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            #t_tw.info.create(db='proj_ffa_0', module='asset', sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type, 'asset.zhizuoren': autor, 'asset.zichanguishu': proj_name}, is_return_id=True)
            t_tw.info.create(db=projectdiction, module='asset', sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type,  'asset.cn_name':u"#自动创建"}, is_return_id=True)
            return True

    def createImageForCGT(self,proj_name, assets_name, assets_icon):
        '''
        CGT没有icon则发布icon
        '''
        import cgtw2
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_asset_ids = t_tw.info.get_id(db=TW_proj, module='asset', filter_list=[['asset.entity', '=', assets_name]])
        TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.image'])
        if TW_dictionInfo[0]["asset.image"] == "":
            t_tw.info.set_image(db=TW_proj, module='asset', id_list=t_asset_ids, field_sign='asset.image',img_path=assets_icon)
        else:
            print(u"已存在:", TW_dictionInfo[0]["asset.image"])

    def get_user_name(self):
        '''
        对照json获取制作人名字
        '''
        host_name = socket.gethostname()
        ip = socket.gethostbyname(host_name)
        scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        scriptsPath = scriptsPath.replace('\\', '/')
        scriptsPath = scriptsPath.replace('sources', 'config')
        data = jsonHelper.readDictFromFile('%s/userAddress.json' % scriptsPath)
        try:
            user_name = data[ip]
        except:
            user_name = str(ip)

        return user_name

    def virusCheck(self):
        script_node = cmds.ls(type='script')
        virus_list = []
        for i in script_node:
            if i.find('_gene') != -1:
                virus_list.append(i)

        if virus_list:
            try:
                cmds.delete('*vaccine_gene*')
                cmds.delete('*breed_gene*')
            except:
                cmds.warning('Virus Kill Failed!')
                return

    def fbxExport(self, path, characterName):
        cmds.select(clear=True)
        cmds.select('Geometry')
        cmds.select('DeformationSystem', add=True)
        fbxFolderPath = '%s/%s' % (path, 'FBX')
        self.rigPub.makePath(fbxFolderPath)
        self.rigPub.createHistory(fbxFolderPath)
        fbxPath = '%s/%s.fbx' % (fbxFolderPath, characterName)
        self.rigPub.exportFBX(False, 1, 200, fbxPath)

def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = RigPubToolsUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()