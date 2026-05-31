#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

# import os
# import random, sys, socket, maya.cmds as cmds#, xgenm as xg
# from utils import jsonHelper, publish
# from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
# from shiboken2 import wrapInstance

# class ModToolsUI(QtWidgets.QMainWindow):
#
#     def __init__(self):
#         super(ModToolsUI, self).__init__()
#         self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')
#         self.tempPath = ("{}/AssetsManagerIconTemp").format(os.environ.get('TEMP'))
#         self.init_ui()
#
#     def init_ui(self):
#         f = QtCore.QFile('%s/ui/modTools.ui' % self.scriptsPath)
#         f.open(QtCore.QFile.ReadOnly)
#         loader = QtUiTools.QUiLoader().load(f)
#         self.ui = loader
#         f.close()
#         self.setCentralWidget(self.ui)
#         self.ui.modGRP_listWgt.addItems(self.modSetting()['ModGroup'].keys())
#         self.ui.modGRP_listWgt.setCurrentRow(0)
#         self.ui.modGRP_listWgt.currentItemChanged.connect(self.listWgtAddItems)
#         self.assetName()
#         self.ui.randomName_bttn.clicked.connect(self.randomName)
#         self.ui.rename_bttn.clicked.connect(self.rename)
#         self.ui.modClear_bttn.clicked.connect(self.modClear)
#         self.ui.remapTextureFile_bttn.clicked.connect(self.getTextureNewPath)
#         self.ui.remapTexture_bttn.clicked.connect(self.remapTexture)
#         self.ui.modPublish_bttn.clicked.connect(self.modPublish)
#         self.ui.modPublish_bttn.setStyleSheet("QPushButton{background: #b0e600; color: #000000;}")
#         self.ui.redshift_bttn.clicked.connect(self.redshift_setAttr)
#         self.ui.arnold_bttn.clicked.connect(self.arnold_setAttr)
#         self.ui.braidMaker_bttn.clicked.connect(self.braidMaker)
#         self.ui.colorSpace_bttn.clicked.connect(self.colorSpace)
#         self.ui.modRename_bttn.clicked.connect(self.modRename)
#         self.ui.materialID_bttn.clicked.connect(self.materialID)
#         self.ui.materialManager_bttn.clicked.connect(self.materialManager)
#
#     def modSetting(self):
#         data = jsonHelper.readDictFromFile('%s/config/modSetting.json' % self.scriptsPath)
#         return data
#
#     def projectSetting(self):
#         data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % self.scriptsPath)
#         return data
#
#     def listWgtAddItems(self):
#         self.ui.modName_listWgt.clear()
#         customItem = QtWidgets.QListWidgetItem()
#         customItem.setText('-- Custom --')
#         customItem.setTextColor(QtGui.QColor(125, 125, 125, 255))
#         customItem.setFlags(customItem.flags() | QtCore.Qt.ItemIsEditable)
#         self.ui.modName_listWgt.insertItem(0, customItem)
#         self.ui.modName_listWgt.setCurrentRow(0)
#         currentItem = self.ui.modGRP_listWgt.currentItem().text()
#         self.ui.modName_listWgt.addItems(self.modSetting()['ModGroup'][currentItem])
#
#     def assetName(self):
#         if len(cmds.ls('*_*_AST')) == 1:
#             self.ui.characterName_line.setText(cmds.ls('*_*_AST')[0].split('_')[0])
#
#     def randomName(self):
#         currentSex = self.ui.man_rBttn.isChecked()
#         if currentSex:
#             num = len(self.modSetting()['CharacterName']['Man']) - 1
#             randomNum = random.randint(0, num)
#             self.ui.characterName_line.setText(self.modSetting()['CharacterName']['Man'][randomNum])
#         else:
#             num = len(self.modSetting()['CharacterName']['Woman']) - 1
#             randomNum = random.randint(0, num)
#             self.ui.characterName_line.setText(self.modSetting()['CharacterName']['Woman'][randomNum])
#
#     def rename(self):
#         characterName = self.ui.characterName_line.text()
#         currentModGRPName = self.ui.modGRP_listWgt.selectedItems()[0].text()
#         projectName = self.ui.projectName_line.text()
#         currentModName = self.ui.modName_listWgt.selectedItems()[0].text()
#         if characterName == '' or currentModGRPName == '-- Custom --' or currentModGRPName == '' or currentModName == '-- Custom --' or currentModName == '':
#             cmds.warning('Please check your name!!!')
#             return
#         selectedList = cmds.ls(selection=True)
#         if not selectedList:
#             cmds.warning('Nothing was selected, please check!!!')
#             return
#         Type_GRP, XGen_GRP, Scalp_GRP = self.createEmptyGRP(characterName, currentModGRPName,projectName)
#         if currentModGRPName == 'HairColl':
#             self.renameCore(characterName, currentModName, selectedList, 'xgmPalette', XGen_GRP)
#         elif currentModGRPName == 'HairDesc':
#             self.renameCore(characterName, currentModName, selectedList, 'xgmDescription', XGen_GRP)
#         elif currentModGRPName == 'HairScalp':
#             self.renameCore(characterName, currentModName, selectedList, 'mesh', Scalp_GRP)
#         else:
#             self.renameCore(characterName, currentModName, selectedList, 'mesh', Type_GRP)
#
#     def renameCore(self, characterName, currentModName, selectedList, nodeType, GRPName):
#         xgenPath = '%sxgen/collections' % xg.getProjectPath()
#         for i in selectedList:
#             if nodeType == 'xgmPalette':
#                 if cmds.nodeType(i) != 'xgmPalette':
#                     cmds.warning('Please select XGen Collections!!!')
#                     return
#                 suffix = 'Coll'
#             elif nodeType == 'xgmDescription':
#                 if cmds.listRelatives(i, children=True, type='xgmDescription') is None:
#                     cmds.warning('Please select XGen Descriptions!!!')
#                     return
#                 suffix = 'Desc'
#             elif nodeType == 'mesh' and GRPName.find('Scalp') != -1:
#                 if cmds.listRelatives(i, children=True, type='mesh') is None:
#                     cmds.warning('Please select Polygons!!!')
#                     return
#                 suffix = 'Scalp'
#             elif nodeType == 'mesh' and GRPName.find('Scalp') == -1:
#                 if cmds.listRelatives(i, children=True, type='mesh') is None:
#                     cmds.warning('Please select Polygons!!!')
#                     return
#                 suffix = 'Geo'
#
#         for i in range(len(selectedList)):
#             if nodeType == 'xgmPalette':
#                 collDescPath = '%s/%s' % (xgenPath, selectedList[i])
#             elif nodeType == 'xgmDescription':
#                 collDescPath = '%s/%s/%s' % (xgenPath, xg.palette(str(selectedList[i])), selectedList[i])
#             else:
#                 collDescPath = ''
#             if collDescPath != '' and os.path.exists(collDescPath):
#                 self.renameCoreCore(characterName, currentModName, suffix, selectedList, nodeType, GRPName, i)
#             elif collDescPath == '':
#                 self.renameCoreCore(characterName, currentModName, suffix, selectedList, nodeType, GRPName, i)
#             else:
#                 cmds.warning('Can not find %s, please check your project path!!!' % collDescPath)
#
#         return
#
#     def renameCoreCore(self, characterName, currentModName, suffix, selectedList, nodeType, GRPName, i):
#         if len(selectedList) == 1:
#             newName = '%s_%s_%s' % (characterName, currentModName, suffix)
#         else:
#             newName = '%s_%s%02i_%s' % (characterName, currentModName, i + 1, suffix)
#         if cmds.objExists(newName):
#             cmds.warning('%s already exists, please give another name!!!' % newName)
#         else:
#             m = xg.geometryPatches(selectedList[i])
#             if m:
#                 desc = str(cmds.listRelatives(m[0], parent=True)[0])
#                 coll = xg.palette(desc)
#                 descPath = xg.descriptionPath(coll, desc)
#                 collPath = xg.palettePath(coll)
#                 cmds.rename(selectedList[i], newName)
#                 for root, dirs, files in os.walk(collPath):
#                     for file in files:
#                         if file.find(selectedList[i]) != -1:
#                             newScalpName = file.replace(selectedList[i], newName)
#                             scalpPath = root.replace('\\', '/')
#                             os.rename('%s/%s' % (scalpPath, file), '%s/%s' % (scalpPath, newScalpName))
#
#                 print (
#                  selectedList[i], newName)
#                 if nodeType != 'xgmDescription':
#                     cmds.parent(newName, GRPName)
#                 try:
#                     xg.fixPatchNames(coll)
#                 except:
#                     pass
#
#             elif nodeType == 'xgmPalette':
#                 oldDataPath = xg.getAttr('xgDataPath', str(selectedList[i]))
#                 newDataPath = oldDataPath.replace(str(selectedList[i]), str(newName))
#                 print (newDataPath)
#                 xg.setAttr('xgDataPath', newDataPath, str(selectedList[i]))
#                 cmds.rename(selectedList[i], newName)
#                 cmds.parent(newName, GRPName)
#             else:
#                 cmds.rename(selectedList[i], newName)
#                 if nodeType != 'xgmDescription':
#                     if cmds.listRelatives(newName, parent=True) is None or cmds.listRelatives(newName, parent=True)[0] != GRPName:
#                         cmds.parent(newName, GRPName)
#         return
#
#     def createEmptyGRP(self, characterName, currentModGRPName,projectName):
#         AST = '%s_%s_AST' % (characterName,projectName)
#         Geo_C_001_GRP = 'Geometry'
#         Mod_GRP = '%s_Mod_GRP' % characterName
#         if cmds.objExists(AST) is False:
#             cmds.group(em=1, name=AST)
#         if cmds.objExists('Geometry') is False:
#             cmds.group(em=1, name='Geometry', parent=AST)
#         if cmds.objExists(Mod_GRP) is False:
#             cmds.group(em=1, name=Mod_GRP, parent=Geo_C_001_GRP)
#         if currentModGRPName.find('Hair') != -1:
#             currentModGRPName = 'Hair'
#             Type_GRP = '%s_%s_GRP' % (characterName, currentModGRPName)
#             if cmds.objExists(Type_GRP) is False:
#                 cmds.group(em=1, name=Type_GRP, parent=Mod_GRP)
#             XGen_GRP = '%s_XGen_GRP' % characterName
#             Scalp_GRP = '%s_Scalp_GRP' % characterName
#             if cmds.objExists(XGen_GRP) is False:
#                 cmds.group(em=1, name=XGen_GRP, parent=Type_GRP)
#             if cmds.objExists(Scalp_GRP) is False:
#                 cmds.group(em=1, name=Scalp_GRP, parent=Type_GRP)
#         else:
#             Type_GRP = '%s_%s_GRP' % (characterName, currentModGRPName)
#             if cmds.objExists(Type_GRP) is False:
#                 cmds.group(em=1, name=Type_GRP, parent=Mod_GRP)
#             XGen_GRP = '%s_XGen_GRP' % characterName
#             Scalp_GRP = '%s_Scalp_GRP' % characterName
#         return Type_GRP, XGen_GRP, Scalp_GRP
#
#     def getTextureNewPath(self):
#         texturePath = cmds.fileDialog2(fileMode=3, dialogStyle=2)[0]
#         self.ui.remapTexture_line.setText(str(texturePath))
#
#     def remapTexture(self):
#         texturePath = self.ui.remapTexture_line.text()
#         if os.path.exists(texturePath):
#             modPub = publish.Publish()
#             modPub.repathTexture(str(texturePath))
#         else:
#             cmds.warning('Please check your path!!!')
#
#     def modClear(self):
#         modPub = publish.Publish()
#         if self.ui.unknown_cBox.isChecked():
#             modPub.removeUnknownNodes()
#         if self.ui.namespace_cBox.isChecked():
#             modPub.removeAllNameSpace()
#         if self.ui.displayLayer_cBox.isChecked():
#             modPub.removeAllDisplayLayer()
#         if self.ui.unloadRef_cBox.isChecked():
#             modPub.removeUnloadReference()
#         if self.ui.unusedShader_cBox.isChecked():
#             modPub.removeUnusedShader()
#         if self.ui.modClean_cBox.isChecked():
#             modPub.modClean()
#         if self.ui.procedureError_cBox.isChecked():
#             modPub.removeModelChangeError()
#
#     def redshift_setAttr(self):
#         import maya.mel as mel
#         mel.eval(('source "{0}/sources/redshift_assistant.mel"').format(self.scriptsPath))
#
#     def arnold_setAttr(self):
#         import maya.mel as mel
#         mel.eval(('source "{0}/sources/arnold_assistant.mel"').format(self.scriptsPath))
#
#     def modRename(self):
#         import maya.mel as mel
#         mel.eval(('source "{0}/sources/cometRename.mel"').format(self.scriptsPath))
#         mel.eval('cometRename')
#
#     def braidMaker(self):
#         import maya.mel as mel
#         modScriptsPath = self.scriptsPath.replace('AssetsManagerForMaya', 'mod')
#         mel_script = ('$s = `getenv "MAYA_PLUG_IN_PATH" `;\n        $s = $s + ";{0}/BraidMaker";\n        putenv "MAYA_PLUG_IN_PATH" $s').format(modScriptsPath)
#         mel.eval(mel_script)
#         try:
#             if not cmds.pluginInfo('braidMaker', q=1, loaded=1):
#                 cmds.loadPlugin('braidMaker')
#             cmds.braidMaker()
#         except:
#             cmds.warning('Can not load braidMaker!')
#
#     def colorSpace(self):
#         m = cmds.ls(type='file')
#         for i in m:
#             n = cmds.getAttr('%s.fileTextureName' % i)
#             if n.find('_f0') != -1 or n.find('_Roughness') != -1 or n.find('_Displacement') != -1 or n.find('_Metallic') != -1 or n.find('_IOR') != -1 or n.find('Opacity') != -1 or n.find('Normal') != -1 or n.find('Glossiness') != -1:
#                 cmds.setAttr('%s.colorSpace' % i, 'Raw', type='string')
#                 cmds.setAttr('%s.alphaIsLuminance' % i, 1)
#                 cmds.setAttr('%s.ignoreColorSpaceFileRules' % i, 1)
#                 print cmds.getAttr('%s.colorSpace' % i, type=1)
#                 print cmds.getAttr('%s.alphaIsLuminance' % i)
#
#     def materialID(self):
#         from sources import shaderHelper
#         # reload(shaderHelper)
#         shaderHelper.showWindow()
#
#     def materialManager(self):
#         modScriptsPath = self.scriptsPath.replace('AssetsManagerForMaya', 'mod')
#         sys.path.append(modScriptsPath)
#         from DW_MaterialManager import UI
#         # reload(UI)
#         UI.UI()
#
#     def modPublish(self):
#         modScriptsPath = self.scriptsPath.replace('AssetsManagerForMaya', 'mod')
#         sys.path.append(modScriptsPath)
#         from Mod_Publish_Tool import modPublishTool
#         # reload(modPublishTool)
#         modPublishTool.showWindow()
#
#     def _modPublishUI(self):
#         modPub = publish.Publish()
#         ''' 检查插件'''
#         # if modPub.pluginInfo('redshift4maya.mll') is False:
#         # QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
#         # return
#         if modPub.pluginInfo('AbcExport.mll') is False:
#             QtWidgets.QMessageBox.warning(self, '警告', '未发现 AbcExport，请加载')
#             return
#         if modPub.pluginInfo('AbcImport.mll') is False:
#             QtWidgets.QMessageBox.warning(self, '警告', '未发现 AbcImport，请加载')
#             return
#         ''' 列出资产有且只有一个，建立path '''
#         if len(cmds.ls('*_*_AST', type='transform')) == 1:
#             projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
#             characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
#             if projectName not in self.projectSetting()['projects']:
#                 QtWidgets.QMessageBox.warning(self, 'Warning','Check your projects name!!!')
#                 return
#             publishType = self.ui.publishType_comb.currentText()
#             path = str('%s/%s/%s/%s/%s/' % (self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType,characterName))
#         else:
#             QtWidgets.QMessageBox.warning(self, 'Warning','Can not find *_*_AST, or more than one *_*_AST, please check!!!')
#             return
#         '''列出publish UI'''
#         self.pubui = QtUiTools.QUiLoader().load('%s/ui/modPublish.ui' % self.scriptsPath)
#         self.pubui.show()
#         self.pubui.icon_label.setPixmap(QtGui.QPixmap('%s/icon/question.png' % self.scriptsPath))
#         self.pubui.Note_label.setText((u"<h3>确定发布 {} 到 {} ？</h3>").format(characterName, path))
#         self.pubui.render_bttn.setIcon(QtGui.QPixmap('%s/icon/render.png' % self.scriptsPath))
#         self.pubui.Preview_label.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(35, 35, 35, 100),  stop:1 rgba(35, 35, 35, 255));")
#         '''拍摄icon并显示在标签'''
#         localiconpath = modPub.makePath(str('%s/snapshot' %self.tempPath))
#         # localicon = "%s/snapShotTemp.png" %localiconpath
#         try:
#             modPub.snapshot(localiconpath, "snapShotTemp", need_createHistory = False)
#             localicon = "%s/snapShotTemp.png" % localiconpath
#             print("%s is snapshoted !!"%localicon)
#             self.pubui.Preview_label.setPixmap(QtGui.QPixmap(localicon))
#         except:
#             print("Error : snapshot is stuck !!")
#         # if QtCore.QFileInfo(localicon).exists() is False:
#         #     self.pubui.Preview_label.setPixmap(QtGui.QPixmap('%s/snapshot/snapShotTemp.png' % self.tempPath))
#         # else:
#         #     pass
#         self.pubui.render_bttn.clicked.connect(modPub.snapshot(localiconpath, "snapShotTemp"))
#         self.pubui.Yes_bttn.clicked.connect(self.checkTextures("Yeeeeeeeeeeeeeeeeeeeees"))
#
#         # self.pubui.Yes_bttn.clicked.connect(self.modPublish(projectName,characterName,publishType,path))
#         # self.pubui.Cancel_bttn.clicked.connect(self.pubui.close())
#         # msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Question, u"提示：",
#         #                             (u"<h3>确定发布 {} 到 {} ？</h3>").format(characterName, path),
#         #                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
#         # msg.setInformativeText(u"同时发布：")
#         # cb = QtWidgets.QCheckBox("Textures", msg)
#         # cb.setChecked(True)
#         # cb2 = QtWidgets.QCheckBox("Xgen", msg)
#         # cb2.setChecked(False)
#         # msg.setCheckBox(cb)
#         # msg.setCheckBox(cb2)
#         # cb2.move(100,0)
#         # yes_bttn = msg.button(QtWidgets.QMessageBox.Yes)
#         # msg.setDefaultButton(yes_bttn)
#         # msg.resize(5000,5000)
#         # msg.exec_()
#         # cb.stateChanged.connect(self.checkTextures(cb))
#         # cb2.stateChanged.connect(self.checkTextures(cb2))
#         # if msg.clickedButton() == yes_bttn:
#         #     msg.buttonClicked.connect(self.modPublish(projectName,characterName,publishType,path))
#         # else:
#         #     pass
#
#     def checkTextures(self,cb):
#         print(cb)
#
#     def _modPublish(self,projectName,characterName,publishType,path):
#         """
#         发布模型
#         """
#         modPub = publish.Publish()
#         modPub.makePath(path)
#         ''' 如果没有CGT则创建CGT  '''
#         if not self.createAssetsForCGT(projectName, self.get_user_name(), characterName, publishType):
#             reply = QtWidgets.QMessageBox.question(self, '提示', 'CGT上已有重名资产，确定继续发布吗？', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
#             if reply == QtWidgets.QMessageBox.Yes:
#                 loga = u"> CGT上已有重名资产已覆盖"
#                 pass
#             else:
#                 return
#         else:
#             loga=(u"> 已在CGT上建立资产：{0}").format(characterName)
#         ''' 清理  '''
#         modPub.removeAllNameSpace()
#         modPub.removeAllDisplayLayer()
#         modPub.removeUnknownNodes()
#         modPub.removeUnusedShader()
#         modPub.removeAllAOV()
#         modPub.removeAllAnimLayer()
#         modPub.removeAllRenderLayer()
#         modPub.modClean()
#         logb = loga + u"\n> 文件已清理"
#         ''' 复制xgen，texture并重定向 '''
#         if self.ui.xgen_cBox.isChecked():
#             try:
#                 modPub.makePath(str('%s/xgen/collections' % path))
#                 modPub.repathXGenData(str('%s/xgen/collections' % path))
#                 logc = logb + u"\n> Xgen已发布"
#             except:
#                 logc = logb + u"\n> Xgen发布失败请检查"
#         else:
#             logc = logb
#         if self.ui.textures_cBox.isChecked():
#             try:
#                 modPub.makePath(str('%s/Texture' % path))
#                 modPub.repathTexture(str('%s/Texture' % path))
#                 logd = logc + u"\n> Texture已发布"
#             except:
#                 logd = logc + u"\n> Texture发布失败请检查"
#         else:
#             logd = logc
#         ''' 不存在icon则拍屏icon '''
#         modPub.makePath(str('%s/%s' % (path, self.projectSetting()['iconFolder'])))
#         iconpath = str('%s/%s/%s.png' % (path, self.projectSetting()['iconFolder'], characterName))
#         # if os.path.exists(iconpath) is False:
#         try:
#             modPub.snapshot(str('%s/%s' % (path, self.projectSetting()['iconFolder'])), characterName)
#             print("new icon is snapshoted !!")
#             try:
#                 self.createImageForCGT(projectName,characterName,iconpath)
#                 print("icon is published !!")
#             except:
#                 print("icon is not published !!")
#             loge = logd + u"\n> 新icon图标已发布"
#         except:
#             loge = logd
#         ''' 保存mod文件 '''
#         modPub.makePath(str('%s/%s' % (path, self.projectSetting()['modelFolder'])))
#         modPub.saveToServer(path, self.projectSetting()['modelFolder'], characterName, self.projectSetting()['modelFile'], self.projectSetting()['mayaFormat'])
#         logf = loge + u"\n> Mod发布成功"
#         '''  保存xgen文件'''
#         if self.ui.xgen_cBox.isChecked():
#             modPub.makePath(str('%s/%s' % (path, self.projectSetting()['xgenFileFolder'])))
#             modPub.saveXGenFile(characterName, projectName, path, self.projectSetting()['xgenFileFolder'], self.projectSetting()['xgenFile'], self.projectSetting()['mayaFormat'])
#         #cmds.file(force=True, new=True)
#         msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：", u"<h3>组件发布成功!\n查看log获取更多细节?</h3>")
#         msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
#         msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
#         msg.setDetailedText(logf)
#         msg.exec_()
#
#     def publishCheckBox(self, checkBox, pushBttn):
#         if checkBox.isChecked():
#             pushBttn.setEnabled(True)
#         else:
#             pushBttn.setEnabled(False)
#
#     def createAssetsForCGT(self, proj_name, autor, assets_name, assets_type):
#         """
#         建立CGT
#         """
#         sys.path.append('C:/CgTeamWork_v6.2/bin/base/')
#         import cgtw2
#         t_tw = cgtw2.tw()
#         projectdiction = self.projectSetting()['projectdiction'][proj_name]
#         t_assets_id_list = t_tw.info.get_id(db=projectdiction, module='asset', filter_list=[['asset.entity', '=', assets_name]])
#         if t_assets_id_list:
#             return False
#         else:
#             #t_tw.info.create(db='proj_ffa_0', module='asset', sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type, 'asset.zhizuoren': autor, 'asset.zichanguishu': proj_name}, is_return_id=True)
#             t_tw.info.create(db=projectdiction, module='asset', sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type,'asset.cn_name':u"#自动创建"}, is_return_id=True)
#             return True
#
#     def createImageForCGT(self,proj_name, assets_name, assets_icon):
#         """
#         CGT没有icon则发布icon
#         """
#         import cgtw2
#         t_tw = cgtw2.tw()
#         TW_proj = self.projectSetting()['projectdiction'][proj_name]
#         t_asset_ids = t_tw.info.get_id(db=TW_proj, module='asset', filter_list=[['asset.entity', '=', assets_name]])
#         TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.image'])
#         if TW_dictionInfo[0]['asset.image']== "":
#             t_tw.info.set_image(db=TW_proj, module='asset', id_list = t_asset_ids , field_sign='asset.image', img_path=assets_icon)
#         else:
#             print(u"已存在:", TW_dictionInfo[0]["asset.image"])
#
#     def get_user_name(self):
#         """
#         对照json获取制作人名字
#         """
#         host_name = socket.gethostname()
#         ip = socket.gethostbyname(host_name)
#         data = jsonHelper.readDictFromFile('%s/config/userAddress.json' % self.scriptsPath)
#         try:
#             user_name = data[ip]
#         except:
#             user_name = str(ip)
#
#         return user_name


# def showWindow():
#     global win
#     try:
#         win.close()
#     except:
#         pass
#
#     win = ModToolsUI()
#     win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
#     win.show()