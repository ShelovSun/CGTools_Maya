#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import os, random, sys, socket, maya.OpenMayaUI as omui, maya.cmds as cmds,maya.mel as mel
from utils import jsonHelper,publish
# reload(publish)
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)

class ScenePubToolsUI(MayaQWidgetDockableMixin,QtWidgets.QMainWindow):

    def __init__(self,proj = 'None',type = 'None'):
        super(ScenePubToolsUI, self).__init__()
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.tempPath = ("{}/AssetsManagerIconTemp").format(os.environ.get('TEMP'))
        self.setWindowTitle('Scene Publish Tool ')
        self.scenePub = publish.Publish()
        self.proj = proj
        self.type = type
        self.init_ui()

    def init_ui(self):
        f = QtCore.QFile('%s/ui/scenePublish.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.ui.icon_label.setPixmap(QtGui.QPixmap('%s/icons/question.png' % self.scriptsPath))
        self.ui.render_bttn.setIcon(QtGui.QPixmap('%s/icons/shot.png' % self.scriptsPath))
        self.ui.Preview_label.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 rgba(35, 35, 35, 100),stop:1 rgba(35, 35, 35, 255));")
        self.ui.log_textBrowser.setStyleSheet("background-color:rgb(0,0,0)")
        self.update_proj()
        if self.proj != 'None':
            self.ui.publishProj_comb.setCurrentText(self.proj)
        else:
            self.ui.publishProj_comb.setCurrentIndex(0)
        self.update_type()
        if self.type != 'None':
            self.ui.publishType_comb.setCurrentText(self.type)
        else:
            self.ui.publishType_comb.setCurrentIndex(0)
        self.ui.Cancel_bttn.clicked.connect(self.closeWin)

        '''确认插件'''
        # if self.scenePub.pluginInfo('redshift4maya.mll') is False:
        #     QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
        #     return
        if self.scenePub.pluginInfo('AbcExport.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 AbcExport，请加载')
            return
        if self.scenePub.pluginInfo('AbcImport.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 AbcImport，请加载')
            return
        if self.scenePub.pluginInfo('gpuCache.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 gpuCache，请加载')
            return
        if self.scenePub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
            return
        '''检查文件'''
        assemblies = cmds.ls(assemblies=True)
        assemblies.remove('persp')
        assemblies.remove('top')
        assemblies.remove('front')
        assemblies.remove('side')
        currentProj = self.ui.publishProj_comb.currentText()
        currentType = self.ui.publishType_comb.currentText()
        if len(assemblies) != 1:
            QtWidgets.QMessageBox.warning(self, '警告', '大纲根目录下仅允许一个组，请检查')
            return
        if assemblies[0].find('|') != -1:
            QtWidgets.QMessageBox.warning(self, '警告', '文件内有重名，请检查')
            return
        path = '%s/%s/%s/%s' % (self.projectSetting()['rootPath'], currentProj, self.projectSetting()['scenesFolder'], currentType)
        self.ui.Note_label.setText((u"<h3>确定发布 {0} 到 \n{1} ？</h3>").format(assemblies[0], path))
        self.renderIcon()
        # self.ui.Yes_bttn.clicked.connect(lambda: self._modPublish(projectName, characterName, publishType, path))
        self.ui.Yes_bttn.clicked.connect(lambda: self._scenePublish(assemblies[0]))
        self.ui.render_bttn.clicked.connect(self.renderIcon)
        self.ui.publishProj_comb.currentIndexChanged.connect(self.proj_change)
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

    def update_proj(self):
        ''' 根据json，设置proj显示 '''
        self.ui.publishProj_comb.addItems(self.projectSetting()['projects'])

    def update_type(self):
        ''' 根据json，设置type显示 '''
        proj = self.ui.publishProj_comb.currentText()
        projcet_path = ('{0}/{1}/Scenes').format(self.projectSetting()['rootPath'], proj)
        directory = QtCore.QDir(projcet_path)
        type_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries, QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        self.ui.publishType_comb.addItems(type_list)

    def proj_change(self):
        ''' 项目修改触发：改type；改path '''
        projectName = cmds.ls('*_*_AST', type='transform')[0].split('_')[1]
        characterName = cmds.ls('*_*_AST', type='transform')[0].split('_')[0]
        publishType = self.ui.publishType_comb.currentText()
        path = str('%s/%s/%s/%s/%s/' % (
            self.projectSetting()['rootPath'], projectName, self.projectSetting()['assetFolder'], publishType,
            characterName))
        self.ui.Note_label.setText((u"<h3>确定发布 {} 到 \n{} ？</h3>").format(characterName, path))

    def type_change(self):
        ''' 类型修改触发：改path '''
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

    def _scenePublish(self,assemblies):
        '''
        发布场景
        '''
        scenePub = publish.Publish()
        if self.override_check(assemblies):
            type, project, path = self.getTypeAndProject()
            if type == 'Map':  # 关卡发布
                if len(cmds.ls('Terrain')) == 1:
                    texture_path = self.export_data(assemblies, 'Texture', False)
                    scenePub.repathTexture(str(('{0}').format(texture_path)))  # 地编的贴图重定向
                    icon_path = self.export_data(assemblies, 'MapIcon', False)
                    try:
                        scenePub.snapshot(icon_path, assemblies)  # 截图icon
                        loga = u"> 新icon已拍摄"
                    except:
                        loga = ""
                    ''' 如果没有CGT则创建CGT  '''
                    if not self.createMapForCGT(project, assemblies):
                        reply = QtWidgets.QMessageBox.question(self, '提示', 'CGT上已有重名资产，确定继续发布吗？',
                                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                        if reply == QtWidgets.QMessageBox.Yes:
                            logb = loga + u"\n> CGT上已有重名资产已覆盖"
                            pass
                        else:
                            return
                    else:
                        logb = loga + (u"\n> 已在CGT上建立资产：{0}").format(assemblies)
                    self.createMapImageForCGT(project, assemblies, "%s/%s.png" % (icon_path, assemblies))
                    asset_list, type_path = self.get_asset_list()
                    mod_path = ('{0}/{1}/{2}').format(type_path, assemblies, 'MapFile')
                    self.make_path(mod_path)
                    cmds.select(assemblies)
                    cmds.file(('{0}/{1}_map.ma').format(mod_path, assemblies), force=True, options='v=0;',
                              type='mayaAscii', pr=True, es=True)
                    cmds.select(clear=True)
                    logc = logb + (u"\n> map已保存：{0}_map").format(assemblies)
                    msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：",
                                                u"<h3>Map发布成功!\n查看log获取更多细节?</h3>")
                    msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
                    msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                    msg.setDetailedText(logc)
                    msg.exec_()
                else:
                    cmds.warning('Can not find Terrain or More than two Terrain')
                    return
            else: #非关卡发布
                texture_path = self.export_data(assemblies, 'Texture', False)
                scenePub.repathTexture(str(('{0}').format(texture_path)))
                icon_path = self.export_data(assemblies, 'Icon', False)
                try:
                    scenePub.snapshot(icon_path, assemblies)
                    loga = u"> 新icon已拍摄"
                except:
                    loga = ""
                ''' 2.如果没有CGT则创建CGT  '''
                if not self.createScenesForCGT(project, assemblies, type):
                    reply = QtWidgets.QMessageBox.question(self, '提示', 'CGT上已有重名资产任务，确定继续发布吗？',
                                                           QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                    if reply == QtWidgets.QMessageBox.Yes:
                        logb = loga + u"\n> CGT上已有重名资产已覆盖"
                        pass
                    else:
                        return
                else:
                    logb = loga + (u"\n> 已在CGT上建立资产：{0}").format(assemblies)
                self.createScenesImageForCGT(project, assemblies,  "%s/%s.png"%(icon_path,assemblies))
                self.export_mod(assemblies)
                logc = logb + (u"\n> {0}_mod 已发布").format(assemblies)
                self.export_fbx(assemblies)
                logd = logc + (u"\n> {0}.fbx 已发布").format(assemblies)
                self.export_port_Ai(assemblies)
                loge = logd + (u"\n> {0}_port 已发布").format(assemblies)
                self.export_AD(assemblies)
                logf = loge + (u"\n> {0}_AD 已发布").format(assemblies)
                msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information,u"提示：",u"<h3>组件发布成功!\n查看log获取更多细节?</h3>")
                msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
                msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
                msg.setDetailedText(logf)
                msg.exec_()

    def get_asset_list(self):
        '''根据type_item_userRole决定asset_list, type_path'''
        currentProj = self.ui.publishProj_comb.currentText()
        currentType = self.ui.publishType_comb.currentText()
        type_path = ('{0}/{1}/Scenes/{2}').format(self.projectSetting()['rootPath'], currentProj,currentType)
        directory = QtCore.QDir(type_path)
        asset_list = directory.entryList(QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries, QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        return (asset_list, type_path)

    def override_check(self, asset_name):
        asset_list, type_path = self.get_asset_list()
        if asset_name in asset_list:
            reply = QtWidgets.QMessageBox.question(self, u'提示', u'服务器上有重名资产，确定要覆盖吗？', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if reply == QtWidgets.QMessageBox.Yes:
                return True
            return False
        else:
            return True

    def export_data(self, asset_name, part, boolHistory):
        '''

        :param asset_name:
        :param type:
        :param boolHistory: 是否建立历史
        :return:
        '''
        asset_list, type_path = self.get_asset_list()
        current_type = self.ui.publishType_comb.currentText()
        # if current_type == 'Map':
        #     data_path = ('{0}/{1}/{2}/{3}').format(type_path, asset_name, 'Terrain', type)
        # else:
        data_path = ('{0}/{1}/{2}').format(type_path, asset_name, part)
        self.make_path(data_path)
        if boolHistory:
            self.scenePub.createHistory(data_path)
        return data_path

    def createScenesForCGT(self, proj_name, assets_name, assets_type):
        '''
        建立CGT
        '''
        sys.path.append('C:/CgTeamWork_v6.2/bin/base/')
        import cgtw2
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=TW_proj, module='scenes', filter_list=[['scenes.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            t_tw.info.create(db=TW_proj, module='scenes', sign_data_dict={'scenes.entity': assets_name, 'scenes.scenesassetstype': assets_type,'scenes.assetsnamecn':u"#自动创建"}, is_return_id=True)
            return True
        t_assets_id_list = t_tw.info.get_id(db=TW_proj, module='scenes',filter_list=[['scenes.entity', '=', assets_name]])
        try:
            t_tw.info.set_image(db=TW_proj, module='scenes', id_list=t_assets_id_list, field_sign='scenes.image',img_path= assets_icon)
        except:
            pass

    def createMapForCGT(self, proj_name, assets_name):
        '''
        建立CGT
        '''
        sys.path.append('C:/CgTeamWork_v6.2/bin/base/')
        import cgtw2
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=TW_proj, module='map', filter_list=[['map.entity', '=', assets_name]])
        if t_assets_id_list:
            return False
        else:
            t_tw.info.create(db=TW_proj, module='map', sign_data_dict={'map.entity': assets_name, 'map.type': 'Map','map.mapnamecn':u"#自动创建"}, is_return_id=True)
            return True

    def createScenesImageForCGT(self, proj_name, assets_name, assets_icon):
        '''
        CGT没有icon则发布icon
        '''
        import cgtw2
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=TW_proj, module='scenes',
                                            filter_list=[['scenes.entity', '=', assets_name]])
        try:
            t_tw.info.set_image(db=TW_proj, module='scenes', id_list=t_assets_id_list, field_sign='scenes.image',
                                img_path=assets_icon)
        except:
            pass

    def createMapImageForCGT(self, proj_name, assets_name, assets_icon):
        '''
        CGT没有icon则发布icon
        '''
        import cgtw2
        t_tw = cgtw2.tw()
        TW_proj = self.projectSetting()['projectdiction'][proj_name]
        t_assets_id_list = t_tw.info.get_id(db=TW_proj, module='map',
                                            filter_list=[['map.entity', '=', assets_name]])
        try:
            t_tw.info.set_image(db=TW_proj, module='map', id_list=t_assets_id_list, field_sign='map.image',
                                img_path=assets_icon)
        except:
            pass

    def createAssetsForCGT(self, proj_name, assets_name, assets_type):
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
            t_tw.info.create(db=projectdiction, module='asset', sign_data_dict={'asset.entity': assets_name, 'asset.assetstapy': assets_type,'asset.cn_name':u"#自动创建"}, is_return_id=True)
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
        if TW_dictionInfo[0]['asset.image']== "":
            t_tw.info.set_image(db=TW_proj, module='asset', id_list = t_asset_ids , field_sign='asset.image', img_path=assets_icon)
        else:
            print(u"已存在:", TW_dictionInfo[0]["asset.image"])

    def getTypeAndProject(self):
        project = self.ui.publishProj_comb.currentText()
        currentType = self.ui.publishType_comb.currentText()
        if currentType == []:
            type = 'Default'
            path = None
        else:
            type = str(currentType)
            path = '%s/%s/%s/%s' % (self.projectSetting()['rootPath'], project, self.projectSetting()['scenesFolder'], type)
        return (type, project, path)

    def export_GPU(self, asset_name):
        gpu_path = self.export_data(asset_name, 'GPU', True)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        create_gpuCache = (
            ' gpuCache -startTime 1 -endTime 1 -optimize -optimizationThreshold 40000 -writeMaterials -dataFormat ogawa -directory "{0}" -fileName "{1}_GPU" {1}; ').format(
            gpu_path, asset_name)
        mel.eval(create_gpuCache)
        return gpu_path

    def export_proxy_Rs(self, asset_name):
        '''

        :param asset_name:
        :return:
        '''
        ''' 检查插件'''
        if self.scenePub.pluginInfo('redshift4maya.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
            return
        if self.scenePub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
            return
        proxy_path = self.export_data(asset_name, 'Proxy', True)
        current_type = self.ui.scene_type_listWgt.currentItem().text()
        if current_type == 'Map':
            asset_name = 'Terrain'
        cmds.select(asset_name)
        cmds.rsProxy(sl=True, fp=('{0}/{1}_proxy.rs').format(proxy_path, asset_name))
        cmds.select(clear=True)
        return proxy_path

    def export_proxy_Ai(self, asset_name):
        '''

        :param asset_name:
        :return:
        '''
        ''' 检查插件'''
        if self.scenePub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
            return
        if self.scenePub.pluginInfo('mtoa.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 mtoa，请加载')
            return
        proxy_path = self.export_data(asset_name, 'Proxy', True)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        cmds.select(asset_name)
        cmds.file(('{0}/{1}_proxy.ass').format(proxy_path, asset_name),es=1,type="ASS Export")
        cmds.select(clear=True)
        return proxy_path

    def export_port_Ai(self, asset_name):
        '''
        发布port
        :param asset_name:
        :return:
        '''
        ''' 检查插件'''
        if self.scenePub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
            return
        if self.scenePub.pluginInfo('mtoa.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 mtoa，请加载')
            return
        self.port_path = self.export_data(asset_name, 'Port', True)
        gpu_path = self.export_GPU(asset_name)
        proxy_path = self.export_proxy_Ai(asset_name)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        self.gpu_file_path = ('{0}/{1}_GPU.abc').format(gpu_path, asset_name)
        self.proxy_file_path = ('{0}/{1}_proxy.ass').format(proxy_path, asset_name)
        if QtCore.QFileInfo(self.gpu_file_path).exists() and QtCore.QFileInfo(self.proxy_file_path).exists():
            current_type = self.ui.publishType_comb.currentText()
            if current_type != 'Scene':
                try:
                    cmds.delete(asset_name)
                except:
                    cmds.warning(('Can not delete {0}').format(asset_name))
                    return
            '''创建ass挂载到Gpu'''
            mel.eval('cmdArnoldCreateStandIn')
            new_name = cmds.rename(cmds.ls('aiStandIn*', type='transform')[0], ('{0}_ASS').format(asset_name))
            cmds.setAttr(('{0}.dso').format(cmds.ls(new_name+"Shape", type='aiStandIn')[0]),
                         self.proxy_file_path, type='string')
            container_name = cmds.container(addNode=new_name, type='dagContainer', ind=('history',
                                                                                        'channels'),
                                            includeHierarchyBelow=True, includeTransform=True, force=True)
            cmds.setAttr(('{0}.lodVisibility').format(container_name), 0)
            gpu_trans = cmds.createNode('transform', name=asset_name)
            gpu_node = cmds.createNode('gpuCache', name=('{0}Shape').format(asset_name), parent=gpu_trans)
            cmds.setAttr(('{0}.cacheFileName').format(gpu_node), self.gpu_file_path, type='string')
            cmds.setAttr(('{0}.cacheGeomPath').format(gpu_node), '|', type='string')
            cmds.setAttr(('{0}.primaryVisibility').format(gpu_node), 0)
            cmds.setAttr(('{0}.castsShadows').format(gpu_node), 0)
            cmds.setAttr(('{0}.receiveShadows').format(gpu_node), 0)
            cmds.parent(container_name, gpu_trans)
            cmds.select(gpu_trans)
            cmds.file(('{0}/{1}_port.ma').format(self.port_path, asset_name), force=True, options='v=0;',
                      type='mayaAscii', pr=True, es=True)
            cmds.delete(gpu_trans)
        else:
            cmds.warning(('Can not find {0} or {1}').format(self.gpu_file_path, self.proxy_file_path))

    def export_port_Rs(self, asset_name):
        '''

        :param asset_name:
        :return:
        '''
        ''' 检查插件'''
        if self.scenePub.pluginInfo('redshift4maya.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 Redshift，请安装并加载')
            return
        if self.scenePub.pluginInfo('sceneAssembly.mll') is False:
            QtWidgets.QMessageBox.warning(self, '警告', '未发现 sceneAssembly，请加载')
            return
        self.port_path = self.export_data(asset_name, 'Port', True)
        gpu_path = self.export_GPU(asset_name)
        proxy_path = self.export_proxy_Rs(asset_name)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        self.gpu_file_path = ('{0}/{1}_GPU.abc').format(gpu_path, asset_name)
        self.proxy_file_path = ('{0}/{1}_proxy.rs').format(proxy_path, asset_name)
        if QtCore.QFileInfo(self.gpu_file_path).exists() and QtCore.QFileInfo(self.proxy_file_path).exists():
            current_type = self.ui.publishType_comb.currentText()
            if current_type != 'Scene':
                try:
                    cmds.delete(asset_name)
                except:
                    cmds.warning(('Can not delete {0}').format(asset_name))
                    return
            '''创建Rs挂载到Gpu'''
            redshift_proxy = mel.eval('redshiftCreateProxy')
            new_name = cmds.rename(cmds.ls(redshift_proxy, type='transform')[0], ('{0}_RS').format(asset_name))
            cmds.setAttr(('{0}.fileName').format(cmds.ls(redshift_proxy, type='RedshiftProxyMesh')[0]), self.proxy_file_path, type='string')
            container_name = cmds.container(addNode=new_name, type='dagContainer', ind=('history',
                                                                                        'channels'), includeHierarchyBelow=True, includeTransform=True, force=True)
            cmds.setAttr(('{0}.lodVisibility').format(container_name), 0)
            gpu_trans = cmds.createNode('transform', name=asset_name)
            gpu_node = cmds.createNode('gpuCache', name=('{0}Shape').format(asset_name), parent=gpu_trans)
            cmds.setAttr(('{0}.cacheFileName').format(gpu_node), self.gpu_file_path, type='string')
            cmds.setAttr(('{0}.cacheGeomPath').format(gpu_node), '|', type='string')
            cmds.parent(container_name, gpu_trans)
            cmds.select(gpu_trans)
            cmds.file(('{0}/{1}_port.ma').format(self.port_path, asset_name), force=True, options='v=0;', type='mayaAscii', pr=True, es=True)
            cmds.delete(gpu_trans)
        else:
            cmds.warning(('Can not find {0} or {1}').format(self.gpu_file_path, self.proxy_file_path))

    def export_mod(self, asset_name):
        '''

        :param asset_name:
        :return:
        '''
        self.mod_path = self.export_data(asset_name, 'Mod', True)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        cmds.select(asset_name)
        cmds.file(('{0}/{1}_mod.ma').format(self.mod_path, asset_name), force=True, options='v=0;', type='mayaAscii', pr=True, es=True)
        cmds.select(clear=True)

    def export_AD(self, asset_name):
        '''

        :param asset_name:
        :return:
        '''
        AD_path = self.export_data(asset_name, 'Assembly', True)
        current_type = self.ui.publishType_comb.currentText()
        if current_type == 'Map':
            asset_name = 'Terrain'
        AD_name = cmds.assembly(name=('{0}_AD').format(asset_name), type='assemblyDefinition')
        port_file_path = ('{0}/{1}_port.ma').format(self.port_path, asset_name)
        mod_file_path = ('{0}/{1}_mod.ma').format(self.mod_path, asset_name)
        if QtCore.QFileInfo(self.gpu_file_path).exists() and QtCore.QFileInfo(port_file_path).exists() and QtCore.QFileInfo(mod_file_path).exists():
            # cmds.assembly(AD_name, edit=True, createRepresentation='Cache', repName=('{0}_GPU.abc').format(asset_name), input=self.gpu_file_path)
            cmds.assembly(AD_name, edit=True, createRepresentation='Scene', repName=('{0}_port.ma').format(asset_name), input=port_file_path)
            cmds.assembly(AD_name, edit=True, createRepresentation='Scene', repName=('{0}_mod.ma').format(asset_name), input=mod_file_path)
            cmds.assembly(AD_name, edit=True, activeLabel=('{0}_port.ma').format(asset_name))
            cmds.select(AD_name)
            cmds.file(('{0}/{1}.ma').format(AD_path, AD_name), force=True, options='v=0;', type='mayaAscii', pr=True, es=True)
            cmds.delete(AD_name)
        else:
            cmds.warning('Can not find mod/port/GPU')

    def export_fbx(self,asset_name):
        cmds.select(all=1)
        fbxFolderPath = self.export_data(asset_name, 'FBX', True)
        fbxPath = '%s/%s.fbx' % (fbxFolderPath, asset_name)
        self.scenePub.exportFBX(False, 1, 200, fbxPath)

    def export_data(self, asset_name, part, boolHistory):
        '''

        :param asset_name:
        :param type:
        :param boolHistory: 是否建立历史
        :return:
        '''
        asset_list, type_path = self.get_asset_list()
        # if current_type == 'Map':
        #     data_path = ('{0}/{1}/{2}/{3}').format(type_path, asset_name, 'Terrain', type)
        # else:
        data_path = ('{0}/{1}/{2}').format(type_path, asset_name, part)
        self.make_path(data_path)
        if boolHistory:
            self.scenePub.createHistory(data_path)
        return data_path

    def make_path(self, path):
        fileinfo = QtCore.QFileInfo(path)
        if fileinfo.exists() is False:
            mkpath = QtCore.QDir()
            mkpath.mkpath(path)

def showWindow(proj, type):
    global win
    try:
        win.close()
    except:
        pass

    win = ScenePubToolsUI(proj,type)
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()