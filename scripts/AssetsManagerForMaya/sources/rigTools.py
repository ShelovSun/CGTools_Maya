#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rigTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import maya.cmds as cmds
import maya.mel as mm
import os
import re
import socket
import sys

from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from utils import jsonHelper, publish


class RigToolsUI(QtWidgets.QMainWindow):

    def __init__(self):
        super(RigToolsUI, self).__init__()
        cmds.selectPref(tso=1)
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')
        self.tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
        self.rigPub = publish.Publish()
        self.init_ui()

    def init_ui(self):
        f = QtCore.QFile('%s/ui/rigTools.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.regExp = QtCore.QRegExp('^\\w+$')
        self.validator = QtGui.QRegExpValidator(self.regExp, self)
        self.ui.simpleRig_name_line.setValidator(self.validator)
        # self.ui.publishType_comb.addItems(self.projectSetting()['type'])
        self.ui.rigPublish_bttn.clicked.connect(self.rigPublish)
        self.ui.rigPublish_bttn.setStyleSheet("QPushButton{background: #b0e600; color: #000000;}")
        self.ui.rigCtrl_bttn.clicked.connect(self.faceRig)
        self.ui.pointJoint_bttn.clicked.connect(self.addPointJoint)
        self.rigCtrlPresetName()
        self.rigCtrlDefaultName()
        self.ui.rigCtrlDefaultName_listWgt.itemActivated.connect(self.currentSelectedItem)
        self.ui.rigCtrlDefaultName_listWgt.itemSelectionChanged.connect(self.currentSelectedItem)
        self.ui.rename_bttn.clicked.connect(self.rigCtrlRename)
        self.ui.faceCtrl_bttn.clicked.connect(self.createFaceCtrl)
        self.ui.ctrlToPoint_bttn.clicked.connect(self.ctrlToPoint)
        self.ui.simpleCtr_bttn.clicked.connect(self.create_simpleCtr)
        self.ui.simpleSkin_bttn.clicked.connect(self.create_simpleSkin)
        self.ui.setDriver_bttn.clicked.connect(self.setDriverKey)
        self.ui.fixFace_bttn.clicked.connect(self.faceFix)
        self.ui.fixFaceOfWrap_bttn.clicked.connect(self.faceFixForWrap)
        self.ui.assignShader_bttn.clicked.connect(self.assignShader)

    def projectSetting(self):
        data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % self.scriptsPath)
        return data

    def rigPublish(self):
        rigScriptsPath = self.scriptsPath.replace('AssetsManagerForMaya', 'rig')
        sys.path.append(rigScriptsPath)
        from Rig_Publish_Tool import rigPublishTool
        reload(rigPublishTool)
        rigPublishTool.showWindow()

    def _rigPublish(self):
        '''
        发布绑定
        '''
        ''' 列出资产'''
        if len(cmds.ls('*_*_AST', type='transform')) == 1:
            projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
            characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
            if projectName not in self.projectSetting()['projects']:
                cmds.warning('Check your projects name!!!')
                return
            publishType = "Props"# self.ui.publishType_comb.currentText()
            path = str('%s/%s/%s/%s/%s' % (self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType, characterName))
            self.rigPub.makePath(path)
        else:
            cmds.warning('Can not find *_*_AST, or more than one *_*_AST, please check!!!')
            return
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
        if not self.createAssetsForCGT(projectName, self.get_user_name(), characterName, publishType, iconpath):
            reply = QtWidgets.QMessageBox.question(self, '提示', 'CGT上有重名资产，确定要继续吗？', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                logb = loga + u"\n> CGT上已有重名资产已覆盖"
                pass
            else:
                return
        else:
            logb=loga + (u"\n> 已在CGT上建立资产：{0}").format(characterName)
        '''icon发布上CGT'''
        try:
            self.createImageForCGT(projectName,characterName,iconpath)
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
        self.rigPub.saveToServer(path, self.projectSetting()['rigFolder'], characterName, self.projectSetting()['rigFileAll'], self.projectSetting()['mayaFormat'])
        logd = logc + u"\n> all rig已发布"
        hiRigFilePath = '%s/%s/%s_%s.%s' % (path, self.projectSetting()['rigFolder'], characterName, self.projectSetting()['rigFileHi'], self.projectSetting()['mayaFormat'])
        allRigFilePath = '%s/%s/%s_%s.%s' % (path, self.projectSetting()['rigFolder'], characterName, self.projectSetting()['rigFileAll'], self.projectSetting()['mayaFormat'])
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
        self.rigPub.saveToServer(path, self.projectSetting()['renderFolder'], characterName, self.projectSetting()['renderFile'], self.projectSetting()['mayaFormat'])
        logg = logf + u"\n> Render档已发布"
        ''' 不存在则发布mod '''
        modFile_path = '%s/%s/%s/%s/%s' % (path, self.projectSetting()['modelFolder'], characterName, self.projectSetting()['modelFile'], self.projectSetting()['mayaFormat'])
        if not os.path.exists(modFile_path):
            self.rigPub.makePath(str('%s/%s' % (path, self.projectSetting()['modelFolder'])))
            self.rigPub.saveToServer(path, self.projectSetting()['modelFolder'], characterName, self.projectSetting()['modelFile'], self.projectSetting()['mayaFormat'])
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

    def createAssetsForCGT(self, proj_name, autor, assets_name, assets_type, assets_icon):
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

    def rigCtrlData(self):
        scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        scriptsPath = scriptsPath.replace('\\', '/')
        scriptsPath = scriptsPath.replace('sources', 'config')
        data = jsonHelper.readDictFromFile('%s/rigCtrl.json' % scriptsPath)
        return data

    def createRigCtrl(self, type):
        degree = self.rigCtrlData()[type]['degree']
        points = self.rigCtrlData()[type]['points']
        rigCtrl = cmds.curve(name='rigCtrl#', degree=degree, point=points)
        return rigCtrl

    def faceRig(self):
        sel = cmds.ls(orderedSelection=True)
        if cmds.objExists('rigCtrl_Exp') is False:
            cmds.expression(name='rigCtrl_Exp')
        exp_str = cmds.expression('rigCtrl_Exp', query=True, string=True)
        for i in sel:
            surfAttach, pointPos = self.createMuscleSurfAttach(i)
            rigCtrl = self.createRigCtrl('ball02')
            cmds.setAttr('%s.t' % rigCtrl, pointPos[0], pointPos[1], pointPos[2], type='double3')
            cmds.makeIdentity(rigCtrl, apply=True, translate=True, rotate=True, scale=True, normal=0, pn=True)
            ctrl_Con = cmds.group(rigCtrl, name=rigCtrl + '_CON')
            ctrl_Grp = cmds.group(ctrl_Con, name=rigCtrl + '_GRP')
            cmds.pointConstraint(surfAttach, ctrl_Grp, maintainOffset=True, weight=1)
            rigCtrl = cmds.rename(rigCtrl, rigCtrl + '_Ctr')
            conExp = '\n\n%s.translateX = -%s.translateX;\n%s.translateY = -%s.translateY;\n%s.translateZ = -%s.translateZ;' % (ctrl_Con, rigCtrl, ctrl_Con, rigCtrl, ctrl_Con, rigCtrl)
            if exp_str.find(conExp) == -1:
                exp_str += conExp

        cmds.expression('rigCtrl_Exp', edit=True, string=exp_str)
        self.rigCtrlDefaultName()

    def addPointJoint(self):
        sel = cmds.ls(orderedSelection=True)
        for i in sel:
            surfAttach, pointPos = self.createMuscleSurfAttach(i)
            cmds.select(clear=True)
            jointName = cmds.joint(p=pointPos)
            cmds.pointConstraint(surfAttach, jointName, maintainOffset=True, weight=1)

    def createMuscleSurfAttach(self, point):
        edges = cmds.polyInfo(point, ve=1)[0]
        edges = edges.split()
        cmds.select('%s.e[%s]' % (point.split('.')[0], edges[2]))
        cmds.select('%s.e[%s]' % (point.split('.')[0], edges[4]), add=1)
        pointPos = cmds.pointPosition(point)
        mm.eval('cMuscleSurfAttachSetup();')
        surfAttach = cmds.ls(sl=1)
        surfAttachShape = cmds.listRelatives(surfAttach, c=1, type='cMuscleSurfAttach')[0]
        cmds.setAttr('%s.uLoc' % surfAttachShape, 0)
        cmds.setAttr('%s.vLoc' % surfAttachShape, 0)
        transform = cmds.xform(surfAttach, q=1, t=1, ws=1)
        if pointPos != transform:
            cmds.setAttr('%s.uLoc' % surfAttachShape, 1)
            cmds.setAttr('%s.vLoc' % surfAttachShape, 0)
            transform = cmds.xform(surfAttach, q=1, t=1, ws=1)
        if pointPos != transform:
            cmds.setAttr('%s.uLoc' % surfAttachShape, 0)
            cmds.setAttr('%s.vLoc' % surfAttachShape, 1)
            transform = cmds.xform(surfAttach, q=1, t=1, ws=1)
        if pointPos != transform:
            cmds.setAttr('%s.uLoc' % surfAttachShape, 1)
            cmds.setAttr('%s.vLoc' % surfAttachShape, 1)
            transform = cmds.xform(surfAttach, q=1, t=1, ws=1)
        return (surfAttach, pointPos)

    def rigCtrlPresetName(self):
        self.ui.rigCtrlPresetName_listWgt.clear()
        customItem = QtWidgets.QListWidgetItem()
        customItem.setText('-- Custom --')
        customItem.setTextColor(QtGui.QColor(125, 125, 125, 255))
        customItem.setFlags(customItem.flags() | QtCore.Qt.ItemIsEditable)
        self.ui.rigCtrlPresetName_listWgt.insertItem(0, customItem)
        self.ui.rigCtrlPresetName_listWgt.addItems(self.rigCtrlData()['rigCtrlName']['ctrlName'])

    def rigCtrlDefaultName(self):
        self.ui.rigCtrlDefaultName_listWgt.clear()
        for i in cmds.ls(type='cMuscleSurfAttach'):
            surfAttach = cmds.listRelatives(i, p=1)[0]
            pointCon = cmds.listConnections('%s.t' % surfAttach, source=0, type='pointConstraint')
            if pointCon is not None:
                rigCtrl_Grp = cmds.listConnections('%s.constraintTranslateX' % pointCon[0], source=0, type='transform')
                cmds.select(rigCtrl_Grp, hi=1)
                rigCtrl_shape = cmds.ls(sl=1, type='nurbsCurve')
                if rigCtrl_shape != []:
                    rigCtrl_Ctr = cmds.listRelatives(rigCtrl_shape, p=1)[0]
                    self.ui.rigCtrlDefaultName_listWgt.addItem(rigCtrl_Ctr)
                cmds.select(clear=True)

        return

    def currentSelectedItem(self):
        m = self.ui.rigCtrlDefaultName_listWgt.selectedItems()
        cmds.select(clear=True)
        for i in m:
            cmds.select('%s' % i.text(), add=True)

    def rigCtrlRename(self):
        rigCtrl_prefix = self.ui.rigCtrlPrefix_line.text()
        rigCtrl_defaultName = self.ui.rigCtrlDefaultName_listWgt.selectedItems()
        rigCtrl_presetName = self.ui.rigCtrlPresetName_listWgt.selectedItems()
        if rigCtrl_prefix == '' or rigCtrl_defaultName == [] or rigCtrl_presetName == []:
            cmds.warning('Please select items and give a prefix!!!')
            return
        if len(rigCtrl_defaultName) != len(rigCtrl_presetName):
            cmds.warning('The number of defaultName and presetName should be the same!!!')
            return
        for i in range(len(rigCtrl_defaultName)):
            presetName = '%s_%s' % (rigCtrl_prefix, rigCtrl_presetName[i].text())
            con = cmds.listRelatives(rigCtrl_defaultName[i].text(), parent=True)[0]
            grp = cmds.listRelatives(con, parent=True)[0]
            point_con = cmds.listRelatives(grp, children=True, type='pointConstraint')[0]
            cmds.rename(rigCtrl_defaultName[i].text(), '%s_%s' % (presetName, 'Ctr'))
            cmds.rename(con, '%s_%s' % (presetName, 'CON'))
            cmds.rename(grp, '%s_%s' % (presetName, 'GRP'))
            cmds.rename(point_con, point_con.replace(grp, '%s_%s' % (presetName, 'GRP')))

        self.rigCtrlDefaultName()

    def setDriverKey(self):
        if len(cmds.ls(sl=1)) != 1:
            cmds.warning('Please select one polygon!!!')
            return
        if len(cmds.ls('*_HeadBS_GRP')) != 1:
            cmds.warning('Please check *_HeadBS_GRP!!!')
            return
        if len(cmds.ls('*_BrowsD_L_Ctr')) != 1:
            cmds.warning('Please check your face Ctr!!!')
            return
        driver_prefix = cmds.ls('*_BrowsD_L_Ctr')[0][:-13]
        sel = cmds.ls(sl=1)[0]
        for i in cmds.listRelatives(cmds.ls('*_HeadBS_GRP'), c=1):
            cmds.duplicate(i, name='%s_new' % i)

        cmds.select(cmds.listRelatives(cmds.ls('*_HeadBS_GRP'), c=1))
        cmds.select(sel, add=1)
        blendNode = cmds.blendShape(name='%s_Head_BlendShape' % driver_prefix, automatic=True)[0]
        scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        scriptsPath = scriptsPath.replace('\\', '/')
        scriptsPath = scriptsPath.replace('sources', 'config')
        f = open(('{0}/{1}').format(scriptsPath, 'connectDriver.txt'))
        melScript = f.read()
        f.close()
        melScript = melScript.replace('defaultPrefix', driver_prefix)
        melScript = melScript.replace('defaultFaceBlendShape', blendNode)
        mm.eval(melScript)
        cmds.select(clear=True)

    def faceFix(self):
        sel_poly = cmds.ls(sl=1)
        listShape = cmds.listRelatives(sel_poly[0], s=True)[0]
        skinCluster = cmds.listConnections(listShape, type='skinCluster')[0]
        blendNode = cmds.listConnections(skinCluster, type='blendShape')
        if blendNode is None:
            if cmds.objExists('ExpressionBlendshapes'):
                blendNode = [
                 'ExpressionBlendshapes']
            else:
                cmds.warning('Can not find ExpressionBlendshapes!!!')
        aliasAttr_list = cmds.aliasAttr(blendNode[0], q=1)
        m = []
        for i in range(len(aliasAttr_list)):
            if i % 2 != 0:
                m.append(int(re.findall('\\d+', aliasAttr_list[i])[0]))

        cmds.undoInfo(openChunk=True)
        if blendNode[0] != 'ExpressionBlendshapes':
            cmds.blendShape(blendNode[0], edit=True, t=(sel_poly[0], max(m) + 1, sel_poly[1], 1))
            cmds.setAttr('%s.%s' % (blendNode[0], sel_poly[1]), 1)
        else:
            cmds.blendShape(blendNode[0], edit=True, t=(sel_poly[1], max(m) + 1, sel_poly[0], 1))
            cmds.setAttr('%s.%s' % (blendNode[0], sel_poly[0]), 1)
        headBS_grp = cmds.ls('*_HeadBS_GRP')
        allFaceExp = cmds.listRelatives(headBS_grp[0], c=1)
        faceExp = []
        for i in allFaceExp:
            if i.endswith('_new'):
                cmds.delete(i)
            else:
                faceExp.append(i)

        for i in faceExp:
            faceTrans = cmds.getAttr('%s.t' % i)[0]
            cmds.setAttr('%s.%s' % (blendNode[0], i), 1)
            cmds.delete(i)
            if blendNode[0] != 'ExpressionBlendshapes':
                cmds.duplicate(sel_poly[0], rr=1, name=i)
            else:
                cmds.duplicate(sel_poly[1], rr=1, name=i)
            cmds.setAttr('%s.translateX' % i, l=0)
            cmds.setAttr('%s.translateY' % i, l=0)
            cmds.setAttr('%s.translateZ' % i, l=0)
            cmds.setAttr('%s.t' % i, faceTrans[0], faceTrans[1], faceTrans[2], type='double3')
            cmds.parent(i, headBS_grp)
            cmds.setAttr('%s.%s' % (blendNode[0], i), 0)

        if blendNode[0] != 'ExpressionBlendshapes':
            dupHead = cmds.duplicate(sel_poly[0], rr=1)
            newSkinCluster = self.copyWeights(skinCluster, sel_poly[0], dupHead[0])
            cmds.delete(sel_poly[0], ch=1)
            n = self.copyWeights(newSkinCluster, dupHead[0], sel_poly[0])
            cmds.delete(dupHead[0])
            cmds.delete(sel_poly[1])
            cmds.select(sel_poly[0])
            self.setDriverKey()
        cmds.undoInfo(closeChunk=True)
        return

    def faceFixForWrap(self):
        sel_poly = cmds.ls(sl=1)
        if len(sel_poly) != 3:
            cmds.warning('Please select three polygons.')
            return
        listShape = cmds.listRelatives(sel_poly[0], s=True)[0]
        blendNode = cmds.listConnections(listShape, type='blendShape')
        aliasAttr_list = cmds.aliasAttr(blendNode[0], q=1)
        m = []
        for i in range(len(aliasAttr_list)):
            if i % 2 != 0:
                m.append(int(re.findall('\\d+', aliasAttr_list[i])[0]))

        cmds.undoInfo(openChunk=True)
        cmds.blendShape(blendNode[0], edit=True, t=(sel_poly[0], max(m) + 1, sel_poly[1], 1))
        cmds.setAttr('%s.%s' % (blendNode[0], sel_poly[1]), 1)
        cmds.select([sel_poly[2], sel_poly[0]], r=True)
        mm.eval('CreateWrap;')
        headBS_grp = cmds.ls('*_HeadBS_GRP')
        allFaceExp = cmds.listRelatives(headBS_grp[0], c=1)
        faceExp = []
        for i in allFaceExp:
            if i.endswith('_new'):
                cmds.delete(i)
            else:
                faceExp.append(i)

        for i in faceExp:
            faceTrans = cmds.getAttr('%s.t' % i)[0]
            cmds.setAttr('%s.%s' % (blendNode[0], i), 1)
            cmds.delete(i)
            cmds.duplicate(sel_poly[2], rr=1, name=i)
            cmds.setAttr('%s.translateX' % i, l=0)
            cmds.setAttr('%s.translateY' % i, l=0)
            cmds.setAttr('%s.translateZ' % i, l=0)
            cmds.setAttr('%s.t' % i, faceTrans[0], faceTrans[1], faceTrans[2], type='double3')
            cmds.parent(i, headBS_grp)
            cmds.setAttr('%s.%s' % (blendNode[0], i), 0)

        cmds.delete([sel_poly[0], sel_poly[1]])
        cmds.select(faceExp)
        cmds.select(sel_poly[2], add=True)
        cmds.blendShape(automatic=True, name='CustomName_Head_BlendShape')
        cmds.undoInfo(closeChunk=True)
        cmds.select(clear=True)

    def copyWeights(self, skinCluster, oldPoly, newPoly):
        skinJoint = cmds.skinCluster(skinCluster, q=True, influence=True)
        cmds.select(skinJoint)
        cmds.select(newPoly, add=True)
        newSkinCluster = cmds.skinCluster(bindMethod=0, normalizeWeights=1, weightDistribution=0, mi=15, omi=True, tsb=True, rui=True)
        cmds.copySkinWeights(oldPoly, newPoly, noMirror=True, surfaceAssociation='closestPoint', influenceAssociation='closestJoint')
        return newSkinCluster

    def createFaceCtrl(self):
        faceCtrl_prefix = self.ui.faceCtrlPrefix_line.text()
        if faceCtrl_prefix == '':
            cmds.warning('Please give a prefix!!!')
            return
        scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        scriptsPath = scriptsPath.replace('\\', '/')
        scriptsPath = scriptsPath.replace('sources', 'config')
        f = open(('{0}/{1}').format(scriptsPath, 'faceControl.txt'))
        melScript = f.read()
        f.close()
        melScript = melScript.replace('defaultPrefix', faceCtrl_prefix)
        mm.eval(melScript)
        cmds.select(clear=True)

    def ctrlToPoint(self):
        points = cmds.ls(os=1, fl=1, type='float3')
        curves = cmds.ls(os=1, fl=1, type='transform')
        if len(points) == 0 or len(points) != len(curves):
            cmds.warning('Please check your selection.')
            return
        if cmds.objExists('faceCtrl_Exp') is False:
            cmds.expression(name='faceCtrl_Exp')
        exp_str = cmds.expression('faceCtrl_Exp', query=True, string=True)
        curves_CON = cmds.listRelatives(curves, p=1)
        curves_GRP = cmds.listRelatives(cmds.listRelatives(curves, p=1), p=1)
        cmds.undoInfo(openChunk=True)
        for i in range(len(points)):
            surfAttach, pos = self.createMuscleSurfAttach(points[i])
            cmds.move(pos[0], pos[1], pos[2], curves_GRP[i], rpr=True)
            cmds.pointConstraint(surfAttach, curves_GRP[i], maintainOffset=True, weight=1)
            conExp = '\n\n%s.translateX = -%s.translateX;\n%s.translateY = -%s.translateY;\n%s.translateZ = -%s.translateZ;' % (
             curves_CON[i], curves[i], curves_CON[i], curves[i], curves_CON[i], curves[i])
            if exp_str.find(conExp) == -1:
                exp_str += conExp

        cmds.expression('faceCtrl_Exp', edit=True, string=exp_str)
        cmds.undoInfo(closeChunk=True)

    def assignShader(self):
        sel = cmds.ls(sl=1)
        m = cmds.listRelatives(sel[0], c=1, noIntermediate=1, type='mesh')
        for i in m:
            if cmds.getAttr('%s.intermediateObject' % i) is False:
                sg = cmds.listConnections(i, scn=1, s=0, type='shadingEngine')
                if len(sg) == 1:
                    cmds.sets(sel[1], e=1, forceElement=sg[0])
                else:
                    cmds.warning('More than one material!!!')

    def create_simpleCtr(self):
        characterName = self.ui.simpleRig_name_line.text()
        if not characterName:
            cmds.warning('Please give a name!')
            return
        selected_list = cmds.ls(sl=1)
        AST = '%s_Project_AST' % characterName
        Mod_GRP = '%s_Mod_GRP' % characterName
        if cmds.objExists(AST) is False:
            cmds.group(em=1, name=AST)
            cmds.group(em=1, name='Geometry', parent=AST)
            cmds.group(em=1, name='DeformationSystem', parent=AST)
            cmds.group(em=1, name=Mod_GRP, parent='Geometry')
            cmds.group(em=1, name='DeformationSystem', parent='DeformationSystem')
            cmds.group(em=1, name='%s_Ctr01_GRP' % characterName, parent='DeformationSystem')
            cmds.group(em=1, name='%s_Ctr01_Sc' % characterName, parent='%s_Ctr01_GRP' % characterName)
            cmds.circle(r=10, name='%s_Ctr01' % characterName, nr=(0, 1, 0), ch=0)
            cmds.parent('%s_Ctr01' % characterName, '%s_Ctr01_Sc' % characterName)
            cmds.group(em=1, name='%s_Ctr02_GRP' % characterName, parent='%s_Ctr01' % characterName)
            cmds.group(em=1, name='%s_Ctr02_Sc' % characterName, parent='%s_Ctr02_GRP' % characterName)
            cmds.circle(r=8, name='%s_Ctr02' % characterName, nr=(0, 1, 0), ch=0)
            cmds.parent('%s_Ctr02' % characterName, '%s_Ctr02_Sc' % characterName)
            cmds.group(em=1, name='%s_Ctr03_GRP' % characterName, parent='%s_Ctr02' % characterName)
            cmds.group(em=1, name='%s_Ctr03_Sc' % characterName, parent='%s_Ctr03_GRP' % characterName)
            cmds.circle(r=4, name='%s_Ctr03' % characterName, nr=(0, 1, 0), ch=0)
            cmds.parent('%s_Ctr03' % characterName, '%s_Ctr03_Sc' % characterName)
        cmds.select('DeformationSystem')
        cmds.joint(name='%s_root_jnt' % characterName)
        cmds.select(clear=True)
        for i in selected_list:
            cmds.parent(i, Mod_GRP)

    def create_simpleSkin(self):
        AST = cmds.ls('*_*_AST')
        if AST:
            characterName = AST[0].split('_')[0]
            curve_list = cmds.ls(type=['nurbsCurve', 'mesh'])
            cmds.select(curve_list)
            cmds.pickWalk(d='up')
            cmds.makeIdentity(a=1, t=1, r=1, s=1, n=0, pn=1)
            cmds.select('%s_root_jnt' % characterName)
            cmds.select('%s_Mod_GRP' % characterName, add=True)
            mm.eval('SmoothBindSkin;')
            cmds.parentConstraint('%s_Ctr03' % characterName, '%s_root_jnt' % characterName, mo=1, weight=1, targetList=0)
            cmds.scaleConstraint('%s_Ctr03' % characterName, '%s_root_jnt' % characterName, mo=1, weight=1, targetList=0)


def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = RigToolsUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()