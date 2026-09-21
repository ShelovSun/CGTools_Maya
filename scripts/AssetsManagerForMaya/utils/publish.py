#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ActionTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import datetime
import maya.cmds as cmds
import maya.mel as mel
import os
import re
import shutil
import uuid


class Publish(object):

    def __init__(self):
        pass

    @staticmethod
    def modClean():
        u"""
        1、清理无用的过渡 mesh 节点
        2、统一法线
        3、frozen/resetTransform
        4、清理顶点信息及无用的点、线、UV
        5、删除历史
        6、判断是否有重名的模型，有则提醒

        """
        for i in cmds.ls(type='mesh', noIntermediate=True):
            cmds.delete(i, ch=1)
            try:
                mesh = cmds.listRelatives(i, parent=True)[0]
                cmds.setAttr('{0}.tx'.format(mesh), lock=False)
                cmds.setAttr('{0}.ty'.format(mesh), lock=False)
                cmds.setAttr('{0}.tz'.format(mesh), lock=False)
                cmds.setAttr('{0}.rx'.format(mesh), lock=False)
                cmds.setAttr('{0}.ry'.format(mesh), lock=False)
                cmds.setAttr('{0}.rz'.format(mesh), lock=False)
                cmds.setAttr('{0}.sx'.format(mesh), lock=False)
                cmds.setAttr('{0}.sy'.format(mesh), lock=False)
                cmds.setAttr('{0}.sz'.format(mesh), lock=False)
                cmds.polyNormalPerVertex(mesh, ufn=1)
                cmds.polyNormal(mesh, normalMode=2, userNormalMode=0, ch=1)
                # cmds.polySoftEdge(mesh, angle=180, ch=True)
                cmds.makeIdentity(mesh, a=1, t=1, r=1, s=1, n=0, pn=1)
                cmds.makeIdentity(mesh, a=0, t=1, r=1, s=1)
                cmds.polyClean(mesh, ce=1, cv=1, cuv=1, fzn=1, ch=1)
                cmds.delete(mesh, ch=1)
                print('%s has been cleaned up.' % i)
            except:
                cmds.warning('More than one object matches name: %s' % cmds.listRelatives(i, parent=True)[0])

        cmds.select(clear=True)

    @staticmethod
    def removeUnloadReference():
        u"""
        移除没加载的 reference

        """
        file_name = cmds.file(query=True, sceneName=True)
        ref_list = cmds.file(file_name, query=True, reference=True)
        for i in ref_list:
            if not cmds.referenceQuery(i, isLoaded=True):
                cmds.file(i, removeReference=True)
                print('remove unload reference success')

    @staticmethod
    def removeUnusedShader():
        u"""
        移除无用的材质球

        """
        unused_shader = 'hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");'
        mel.eval(unused_shader)
        print('remove unused shader success')

    @staticmethod
    def removeAllNameSpace():
        u"""
        移除空间名

        """
        for i in range(10):
            namespace_list = cmds.namespaceInfo(listOnlyNamespaces=True)
            namespace_list.remove('UI')
            namespace_list.remove('shared')
            for j in namespace_list:
                cmds.namespace(force=True, mergeNamespaceWithRoot=True, removeNamespace=j)

    @staticmethod
    def removeAllDisplayLayer():
        u"""
        移除所有显示层

        """
        displayLayerList = cmds.ls(type='displayLayer')
        displayLayerList.remove('defaultLayer')
        if len(displayLayerList) > 0:
            cmds.delete(displayLayerList)
            print('%s remove success.' % displayLayerList)
        else:
            print('There are no displayLayer.')

    @staticmethod
    def removeAllAnimLayer():
        u"""
        移除所有动画层

        """
        animLayerList = cmds.ls(type='animLayer')
        if len(animLayerList) > 0:
            cmds.delete(animLayerList)
            print('%s remove success.' % animLayerList)
        else:
            print('There are no animLayer.')

    @staticmethod
    def removeAllRenderLayer():
        u"""
        移除所有渲染层
        """
        renderLayerList = cmds.ls(type='renderLayer')
        renderLayerList.remove('defaultRenderLayer')
        if len(renderLayerList) > 0:
            cmds.delete(renderLayerList)
            print('%s remove success.' % renderLayerList)
        else:
            print('There are no renderLayer.')

    @staticmethod
    def removeAllAOV():
        u"""
        移除所有的 AOV
        """
        redshiftAOV = cmds.ls(type='RedshiftAOV')
        aiAOV = cmds.ls(type='aiAOV')
        AOV = redshiftAOV + aiAOV
        if len(AOV) > 0:
            cmds.delete(AOV)
            print('%s remove success.' % AOV)
        else:
            print('There are no AOV.')

    @staticmethod
    def removeUnknownNodes():
        u"""
        移除未知的节点
        """
        unknown_nodes = cmds.ls(type=['unknown', 'unknownDag', 'unknownTransform'])
        if len(unknown_nodes) > 0:
            cmds.delete(unknown_nodes)
            print('%s remove success.' % unknown_nodes)
        else:
            print('There are no unknown node.')
        unknown_plugin = cmds.unknownPlugin(q=True, list=True)
        if unknown_plugin is not None:
            for i in unknown_plugin:
                cmds.unknownPlugin(i, remove=True)
                print('Unkown Plugin %s remove sucess.' % i)

        return

    @staticmethod
    def removeModelChangeError():
        """
        remove error
         Error: line 1: Cannot find procedure "look"
         Error: line 1: Cannot find procedure "onModelChange3dc".
         Error: line 1: Cannot find procedure "CgAbBlastPanelOptChangeCallback".
        """
        mel.eval('outlinerEditor -edit -selectCommand "" "outlinerPanel1";')
        for model_panel in cmds.getPanel(typ='modelPanel'):
            callback = cmds.modelEditor(model_panel, query=True, editorChanged=True)
            if callback == 'CgAbBlastPanelOptChangeCallback' or callback == 'onModelChange3dc':
                cmds.modelEditor(model_panel, edit=True, editorChanged='')
                print('Fix "onModelChange3dc"/"CgAbBlastPanelOptChangeCallback" Success!!!')
            else:
                print('There are no procedure errors in your scene!!!')

    @staticmethod
    def setModelPanelOptions(widthHeight=None):
        if widthHeight is None:
            widthHeight = [250, 250]
        window = cmds.window(title="capture_window", widthHeight=widthHeight)
        cmds.paneLayout()
        modelPanel = cmds.modelPanel()  # u"capture_modelPanel_%s" % str(uuid.uuid4()).split('-')[0]
        # if cmds.modelEditor(modelPanel, exists=True):
        #     return
        cmds.modelEditor(modelPanel, edit=True, allObjects=False)
        cmds.modelEditor(modelPanel, edit=True, grid=False)
        cmds.modelEditor(modelPanel, edit=True, dynamics=False)
        cmds.modelEditor(modelPanel, edit=True, activeOnly=False)
        cmds.modelEditor(modelPanel, edit=True, manipulators=False)
        cmds.modelEditor(modelPanel, edit=True, headsUpDisplay=False)
        cmds.modelEditor(modelPanel, edit=True, selectionHiliteDisplay=False)

        cmds.modelEditor(modelPanel, edit=True, polymeshes=True)
        cmds.modelEditor(modelPanel, edit=True, nurbsSurfaces=True)
        cmds.modelEditor(modelPanel, edit=True, subdivSurfaces=True)
        cmds.modelEditor(modelPanel, edit=True, displayTextures=True)
        cmds.modelEditor(modelPanel, edit=True, displayAppearance="smoothShaded")
        cmds.setFocus(modelPanel)
        # cmds.showWindow(window)

    def snapshot(self, path, imageName="thumbnail", frame=1, widthHeight=None,
                 imageFormat='png', need_createHistory=False):
        u"""
        截图并重命名(playblast会自动建立路径)
        """
        # print("=============",need_createHistory)
        self.setModelPanelOptions(widthHeight)
        if widthHeight is None:
            widthHeight = [250, 250]
        if need_createHistory:
            self.createHistory(path)
        else:
            pass
        cmds.playblast(frame=frame, percent=100, quality=100, framePadding=1, widthHeight=widthHeight, format='image',
                       compression=imageFormat,
                       showOrnaments=False, viewer=False, filename='%s/%s' % (path, imageName))
        newPath = '%s/%s.%s' % (path, imageName, imageFormat)
        if os.path.isfile(newPath):
            os.remove(newPath)
            os.rename('%s/%s.0.%s' % (path, imageName, imageFormat), '%s/%s.%s' % (path, imageName, imageFormat))
        else:
            os.rename('%s/%s.0.%s' % (path, imageName, imageFormat), '%s/%s.%s' % (path, imageName, imageFormat))
        return '%s/%s.%s' % (path, imageName, imageFormat)

    def publish_icon(self, src, dst, asset_name):
        # print("publish_icon:", src, dst, asset_name)
        self.makePath(dst)
        dst_file = os.path.join(dst, asset_name+".png")
        shutil.copy2(src, dst_file)

    def seqshot(self, actionPath, imageName="thumbnail", widthHeight=None):
        """

        :param widthHeight:
        :param actionPath:
        :param imageName:
        :return:
        """
        self.setModelPanelOptions(widthHeight)
        if widthHeight is None:
            widthHeight = [250, 250]
        if os.path.exists(actionPath):
            image_list = [actionPath + '/' + img for img in os.listdir(actionPath)]
            if image_list:
                for i in image_list:
                    os.remove(i)
        cmds.playblast(percent=100, quality=100, widthHeight=widthHeight, format='image', compression='jpg',
                       viewer=False, filename='%s/%s' % (actionPath, imageName))
        return

    @staticmethod
    def playblastGif(path, imageName):
        u"""
        拍屏并生成gif到

        """
        MYPREFSDIR = cmds.internalVar(userPrefDir=True)
        cdec = "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse"
        cmds.playblast(percent=100, quality=100, widthHeight=[160, 160], format='avi', viewer=False,
                       filename=MYPREFSDIR + 'ActionGif')
        # os.system(("D:/Project/Scripts/Tools/ffmpeg-N-102494-g2899fb61d2-win64-gpl-shared/bin/ffmpeg -i {0}ActionGif.avi -b:v 640k {0}ActionGif.gif").format(MYPREFSDIR))
        os.system((
            "D:/Project/Scripts/Tools/ffmpeg-N-102494-g2899fb61d2-win64-gpl-shared/bin/ffmpeg -i {0}ActionGif.avi -s 160x160 -vf {1} {0}ActionGif.gif").format(
            MYPREFSDIR, cdec))
        outputAvipath = path
        outputGifpath = path
        # os.system("D:/Project/Scripts/Tools/ffmpeg-N-102494-g2899fb61d2-win64-gpl-shared/bin/ffmpeg -i G:/xxx.avi -b:v 640k G:/xxx.gif")

    @staticmethod
    def createModAST():
        u"""
        创建 AST 组
        :return:
        """
        characterName = 'Saleem'
        projectName = 'WOE'
        cpAST = cmds.group(em=1, name='%s_%s_AST' % (characterName, projectName))
        geo_grp = cmds.group(em=1, name='Geo_C_001_GRP', parent=cpAST)
        rig_grp = cmds.group(em=1, name='Rig_C_001_GRP', parent=cpAST)
        mod_grp = cmds.group(em=1, name='%s_Mod_GRP' % characterName, parent=geo_grp)
        body_grp = cmds.group(em=1, name='%s_Body_GRP' % characterName, parent=mod_grp)
        cloth_grp = cmds.group(em=1, name='%s_Cloth_GRP' % characterName, parent=mod_grp)
        hair_grp = cmds.group(em=1, name='%s_Hair_GRP' % characterName, parent=mod_grp)
        ornaments_grp = cmds.group(em=1, name='%s_Ornaments_GRP' % characterName, parent=mod_grp)

    @staticmethod
    def setModelAttr(mesh):
        cmds.setAttr('{0}.castsShadows'.format(mesh), 1)
        cmds.setAttr('{0}.receiveShadows'.format(mesh), 1)
        cmds.setAttr('{0}.holdOut'.format(mesh), 0)
        cmds.setAttr('{0}.motionBlur'.format(mesh), 1)
        cmds.setAttr('{0}.primaryVisibility'.format(mesh), 1)
        cmds.setAttr('{0}.visibleInReflections'.format(mesh), 1)
        cmds.setAttr('{0}.visibleInRefractions'.format(mesh), 1)
        cmds.setAttr('{0}.smoothShading'.format(mesh), 1)
        cmds.setAttr('{0}.doubleSided'.format(mesh), 1)

    def repathTexture(self, path):
        u"""
        path: "Y:/Onemt/Marketing/WOE/Assets/Characters/YaSW/Texture"
        1、贴图复制到规范路径下
        2、重定向贴图路径到目标
        :return:
        """
        imageFileList = []
        imageFileNameList = []
        textureDict = {}
        for i in cmds.ls(type='file'):
            imageFilePath = cmds.getAttr('%s.fileTextureName' % i)
            imageFileList.append(imageFilePath)

        for i in set(imageFileList):
            if i.find('\\') != -1:
                i = i.replace('\\', '/')
            imageFileDir, imageFileName = os.path.split(i)
            imageFileNameList.append(imageFileName)
            textureDict[i] = imageFileName
            if len(imageFileNameList) == len(set(imageFileNameList)):
                if re.findall('\\d{4}', imageFileName):
                    for j in cmds.getFileList(folder=imageFileDir, filespec=re.sub('\\d{4}', '*', imageFileName)):
                        if imageFileDir != path and os.path.exists('%s/%s' % (imageFileDir, j)):
                            shutil.copy2('%s/%s' % (imageFileDir, j), path)
                        else:
                            cmds.warning('Please check path %s/%s!!!' % (imageFileDir, j))

                elif imageFileName.find('<UDIM>') != -1:
                    for j in cmds.getFileList(folder=imageFileDir, filespec=imageFileName.replace('<UDIM>', '*')):
                        if imageFileDir != path and os.path.exists('%s/%s' % (imageFileDir, j)):
                            shutil.copy2('%s/%s' % (imageFileDir, j), path)
                        else:
                            cmds.warning('Please check path %s/%s!!!' % (imageFileDir, j))

                elif imageFileName.find('u0_v0') != -1:
                    for j in cmds.getFileList(folder=imageFileDir, filespec=imageFileName.replace('u0_v0', 'u*_v*')):
                        if imageFileDir != path and os.path.exists('%s/%s' % (imageFileDir, j)):
                            shutil.copy2('%s/%s' % (imageFileDir, j), path)
                        else:
                            cmds.warning('Please check path %s/%s!!!' % (imageFileDir, j))

                elif os.path.split(i)[0] != path and os.path.exists(i):
                    shutil.copy2(i, path)
                else:
                    cmds.warning('Please check path %s!!!' % i)
            else:
                for j in set(textureDict.values()):
                    if textureDict.values().count(j) == 2:
                        for m, n in textureDict.items():
                            if n == j:
                                print(m)

                        cmds.warning('More than one %s in different path!!!' % j)
        # 重定向文件贴图路径
        for i in cmds.ls(type='file'):
            imageFilePath = cmds.getAttr('%s.fileTextureName' % i)
            imageFileDir, imageFileName = os.path.split(imageFilePath)
            cmds.setAttr('%s.fileTextureName' % i, '%s/%s' % (path, imageFileName), type='string')

        self.repathNormalMap(path)

    @staticmethod
    def create_folder(parent, path, folder_name, fixed_subdir=None, allow_existing=False):
        """按“新建文件夹”功能的规则创建一层目录。

        这个无弹窗入口供已经从其他控件取得文件夹名的功能复用，例如发布工具
        Scene 页签里手动输入的新类型。这样右键“新建文件夹”和发布工具不会各自
        维护一套不同的路径安全规则。

        Args:
            parent: 警告弹窗所属的 Qt 父窗口。
            path: 创建目录的根路径。
            folder_name: 只包含一层的文件夹名。
            fixed_subdir: 可选的固定子目录，例如 ``Scenes``。
            allow_existing: 目标文件夹已经存在时是否视为成功。

        Returns:
            bool: 目录存在或创建成功时返回 ``True``，否则返回 ``False``。
        """
        from my_vendor.Qt import QtWidgets

        folder_name = folder_name.strip()
        if not folder_name:
            QtWidgets.QMessageBox.warning(parent, u'提示', u'请输入文件夹名字')
            return False

        # 只允许一层文件夹名，防止使用 ../ 或绝对路径逃离指定的 Scenes 目录。
        invalid_chars = u'\\/:*?"<>|'
        if folder_name in (u'.', u'..') or any(char in folder_name for char in invalid_chars):
            QtWidgets.QMessageBox.warning(
                parent,
                u'提示',
                u'文件夹名不能包含 \\ / : * ? " < > | 等路径字符',
            )
            return False

        target_root = os.path.join(path, fixed_subdir) if fixed_subdir else path
        target_path = os.path.join(target_root, folder_name)
        if os.path.exists(target_path):
            if allow_existing and os.path.isdir(target_path):
                return True
            QtWidgets.QMessageBox.warning(parent, u'提示', u'文件夹已存在')
            return False

        try:
            os.makedirs(target_path)
        except OSError as error:
            QtWidgets.QMessageBox.warning(
                parent, u'提示', u'创建文件夹失败：{0}'.format(error)
            )
            return False
        return True

    @staticmethod
    def create_new_folder(parent, path, fixed_subdir=None):
        """创建新文件夹。

        Args:
            parent: 弹窗所属的 Qt 父窗口。
            path: 创建目录的根路径。
            fixed_subdir: 可选的固定子目录。指定后，弹窗会显示不可编辑的
                ``<fixed_subdir>\\`` 前缀，并且文件夹实际只会创建在该子目录下。

        Returns:
            str or None: 创建成功时返回新文件夹名，取消时返回 ``None``。
        """
        from my_vendor.Qt import QtCore
        from my_vendor.Qt import QtWidgets
        Dialog = QtWidgets.QDialog(parent)
        Dialog.resize(420, 105)
        Dialog.setWindowTitle(u"新建文件夹")

        label = QtWidgets.QLabel(Dialog)
        label.setText(u"新建文件夹名字：")

        folder_lineEdit = QtWidgets.QLineEdit(Dialog)
        folder_lineEdit.setPlaceholderText(u"请输入文件夹名字")
        bttnBox = QtWidgets.QDialogButtonBox(Dialog)
        bttnBox.setOrientation(QtCore.Qt.Horizontal)
        bttnBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.Cancel | QtWidgets.QDialogButtonBox.Ok
        )
        lay = QtWidgets.QGridLayout(Dialog)
        lay.setContentsMargins(10, 5, 10, 10)
        lay.addWidget(label, 0, 0, 1, 2)

        if fixed_subdir:
            # 这个 QLabel 是不可编辑的路径前缀，用户只能输入 Scenes 下的文件夹名。
            fixed_prefix_label = QtWidgets.QLabel(Dialog)
            fixed_prefix_label.setText(u"{0}\\".format(fixed_subdir))
            lay.addWidget(fixed_prefix_label, 1, 0, 1, 1)
            lay.addWidget(folder_lineEdit, 1, 1, 1, 1)
        else:
            # 保持其他调用者（如 Action）的原有用法不变。
            lay.addWidget(folder_lineEdit, 1, 0, 1, 2)

        lay.addWidget(bttnBox, 2, 0, 1, 2)

        created_folder = [None]

        def _addFolder():
            folder_name = folder_lineEdit.text().strip()
            if not Publish.create_folder(Dialog, path, folder_name, fixed_subdir=fixed_subdir):
                return False

            created_folder[0] = folder_name
            Dialog.accept()
            return True

        bttnBox.accepted.connect(_addFolder)
        bttnBox.rejected.connect(Dialog.reject)
        Dialog.exec_()
        return created_folder[0]

    @staticmethod
    def repathNormalMap(path):
        normalMapFileList = []
        normalMapFileNameList = []
        for i in cmds.ls(type=['RedshiftNormalMap', 'RedshiftSprite']):
            normalMapFilePath = cmds.getAttr('%s.tex0' % i)
            normalMapFileList.append(normalMapFilePath)

        for i in set(normalMapFileList):
            normalMapFileDir, normalMapFileName = os.path.split(i)
            if normalMapFileName.find('<UDIM>') != -1:
                udimMapList = cmds.getFileList(folder=normalMapFileDir,
                                               filespec=normalMapFileName.replace('<UDIM>', '*'))
                if udimMapList:
                    for udimMap in udimMapList:
                        if normalMapFileDir != path:
                            shutil.copy2('%s/%s' % (normalMapFileDir, udimMap), path)

            elif os.path.exists(i):
                if os.path.split(i)[0] != path:
                    shutil.copy2(i, path)

        for i in cmds.ls(type=['RedshiftNormalMap', 'RedshiftSprite']):
            normalMapFilePath = cmds.getAttr('%s.tex0' % i)
            cmds.setAttr('%s.tex0' % i, '%s/%s' % (path, normalMapFilePath.split('/')[(-1)]), type='string')

    def repathXGenData(self, path):
        u"""
        path: "Y:/Onemt/Marketing/WOE/Assets/Characters/YaSW/xgen/collections"
        1、判断新路径下是否已存在xgen数据，若有，则移动到历史文件夹内
        2、判断当前工程目录下是否有Collection文件夹
        3、复制collection文件夹，并重定向

        """
        import xgenm as xg
        for i in xg.palettes():
            oldDataPath = xg.getAttr('xgDataPath', i)
            if oldDataPath.find(';') != -1:
                coll_path = oldDataPath.split(';')[(-1)]
                coll_path = coll_path.replace('\\', '/')
            else:
                coll_path = os.path.join(xg.paletteRootPath(), i)
            if os.path.exists(coll_path):
                if coll_path != '%s/%s' % (path, i):
                    self.createHistory(path)

        for i in xg.palettes():
            oldDataPath = xg.getAttr('xgDataPath', i)
            if oldDataPath.find(';') != -1:
                coll_path = oldDataPath.split(';')[(-1)]
                coll_path = coll_path.replace('\\', '/')
            else:
                coll_path = os.path.join(xg.paletteRootPath(), i)
            if os.path.exists(coll_path):
                if coll_path != '%s/%s' % (path, i):
                    shutil.copytree(coll_path, '%s/%s' % (path, i))
                    oldDataPath = xg.getAttr('xgDataPath', i)
                    newDataPath = '%s;%s/%s' % (oldDataPath, path, i)
                    xg.setAttr('xgDataPath', '%s' % newDataPath, '%s' % i)
            else:
                cmds.warning('Can not find %s.' % coll_path)

    def saveXGenFile(self, characterName, projectName, path, type, suffix, mayaformat):
        """
        1、解父子关系_Hair_GRP，删除_AST
        2、保存
        :param characterName:
        :param projectName:
        :param path:
        :param type:
        :param suffix:
        :param mayaformat:
        :return:
        """
        if cmds.objExists('%s_Hair_GRP' % characterName):
            cmds.parent('%s_Hair_GRP' % characterName, world=True)
            cmds.delete('%s_%s_AST' % (characterName, projectName))
            self.removeUnusedShader()
            self.createHistory('%s/%s' % (path, type))
            xgenPath = '%s/%s/%s_%s.%s' % (path, type, characterName, suffix, mayaformat)
            cmds.file(rename=xgenPath)
            cmds.file(save=True, type='mayaAscii')
            return xgenPath
        else:
            print(u"save xgen file failed !!!")

    @staticmethod
    def createHistory(path):
        u"""
        1、判断路径下是否已有 history 文件夹
        2、如果路径下存在除 history 以外的文件，则全部移动到 history 下的当前时间文件夹内

        """
        fileList = cmds.getFileList(folder=path)
        try:
            fileList.remove('history')
            fileList.remove('Thumbs.db')
        except:
            pass

        if len(fileList) != 0:
            n = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            historyPath = os.path.join(path, 'history', n)
            if os.path.exists(historyPath) is False:
                os.makedirs(historyPath)
            for i in fileList:
                shutil.move('%s/%s' % (path, i), historyPath)
        else:
            pass

    def saveToServer(self, path, type, characterName, suffix, mayaformat='mayaAscii', createHistory=True):
        """
        保存maya文件
        :param path: "Y:/Onemt/Marketing/WOE/Assets/Characters"
        :param characterName: "Saleem"
        :param suffix: Mod
        :param mayaformat: "mayaAscii" or "mayaBinary"
        :param createHistory: bool
        :return:
        """
        savePath = self.makePath('%s/%s' % (path, type))
        if createHistory:
            self.createHistory(savePath)

        filePath = '%s/%s_%s.ma' % (savePath, characterName, suffix)
        if mayaformat == 'mayaBinary':
            filePath = '%s/%s_%s.mb' % (savePath, characterName, suffix)

        cmds.file(rename=filePath)
        cmds.file(save=True, type=mayaformat)
        return filePath

    @staticmethod
    def doDeleteRig():
        """
        清理绑定控制器
        :return:
        """
        cmds.select('Geometry')
        mel.eval('DeleteHistory;')
        try:
            cmds.select('All_Ctr')
            mel.eval('doDelete;')
        except:
            pass
        try:
            cmds.select('All_Ctr_GRP')
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
        try:
            cmds.select('Sim')
            mel.eval('doDelete;')
        except:
            pass

    @staticmethod
    def exportAlembic(start, end, name, path):
        jobArg = '-frameRange %s %s -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root %s -file %s' % (
            start, end, name, path)
        cmds.AbcExport(jobArg=jobArg)

    @staticmethod
    def exportFBX(bakeAni, start, end, path):
        melScript = 'FBXExportBakeComplexAnimation -v %s;\n        FBXExportBakeComplexStart -v %s;\n        ' \
                    'FBXExportBakeComplexEnd -v %s;\n        FBXExportBakeComplexStep -v 1;\n        ' \
                    'FBXExportBakeResampleAnimation  -v true;\n        FBXExportSmoothingGroups -v true;\n        ' \
                    'FBXExportSmoothMesh -v true;\n        FBXExportReferencedAssetsContent -v true;\n        ' \
                    'FBXExportShapes -v true;\n        FBXExportSkins -v true;\n        FBXExport -f "%s" -s;' % (
                        bakeAni, start, end, path)
        mel.eval(melScript)

    @staticmethod
    def pluginInfo(plugin):
        if cmds.pluginInfo(plugin, query=True, loaded=True):
            return True
        try:
            cmds.loadPlugin(plugin)
            return True
        except:
            return False

    @staticmethod
    def makePath(path):
        if not os.path.exists(path):
            os.makedirs(path)
        return path

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
            except:
                cmds.warning('Virus Kill Failed!')
                return
