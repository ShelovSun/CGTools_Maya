#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.6 (tags/v3.8.6:db45529, Sep 23 2020, 15:37:30) [MSC v.1927 32 bit (Intel)]
# Embedded file name: E:\PyCharm\AssetsManager\v2.0.0\utils\publish.py
# Compiled at: 2020-11-10 16:20:39


import maya.cmds as cmds, maya.mel as mm, os, re, shutil, datetime


class Publish(object):

    def __init__(self):
        pass

    def modClean(self):
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
                cmds.setAttr(('{0}.tx').format(mesh), lock=False)
                cmds.setAttr(('{0}.ty').format(mesh), lock=False)
                cmds.setAttr(('{0}.tz').format(mesh), lock=False)
                cmds.setAttr(('{0}.rx').format(mesh), lock=False)
                cmds.setAttr(('{0}.ry').format(mesh), lock=False)
                cmds.setAttr(('{0}.rz').format(mesh), lock=False)
                cmds.setAttr(('{0}.sx').format(mesh), lock=False)
                cmds.setAttr(('{0}.sy').format(mesh), lock=False)
                cmds.setAttr(('{0}.sz').format(mesh), lock=False)
                cmds.polyNormalPerVertex(mesh, ufn=1)
                cmds.polyNormal(mesh, normalMode=2, userNormalMode=0, ch=1)
                # cmds.polySoftEdge(mesh, angle=180, ch=True) #软边显示
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
        mm.eval(unused_shader)
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
        :return:
        """
        mm.eval('outlinerEditor -edit -selectCommand "" "outlinerPanel1";')
        for model_panel in cmds.getPanel(typ='modelPanel'):
            callback = cmds.modelEditor(model_panel, query=True, editorChanged=True)
            if callback == 'CgAbBlastPanelOptChangeCallback' or callback == 'onModelChange3dc':
                cmds.modelEditor(model_panel, edit=True, editorChanged='')
                print('Fix "onModelChange3dc"/"CgAbBlastPanelOptChangeCallback" Success!!!')
            else:
                print('There are no procedure errors in your scene!!!')

    def snapshot(self, path, imageName):
        u"""
        截图并重命名

        """
        self.createHistory(path)
        cmds.playblast(frame=1, percent=100, quality=100, framePadding=1, widthHeight=[200, 200], format='image',
                       compression='png', showOrnaments=False, viewer=False, filename='%s/%s' % (path, imageName))
        os.rename('%s/%s.0.png' % (path, imageName), '%s/%s.png' % (path, imageName))

    def PlayblastGif(self, path, imageName):
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

    def repathTexture(self, path):
        u"""
        path: "Y:/Onemt/Marketing/WOE/Assets/Characters/YaSW/Texture"

        1、贴图复制到规范路径下
        2、重定向贴图路径
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

        for i in cmds.ls(type='file'):
            imageFilePath = cmds.getAttr('%s.fileTextureName' % i)
            cmds.setAttr('%s.fileTextureName' % i, '%s/%s' % (path, imageFilePath.split('/')[(-1)]), type='string')

        self.repathNormalMap(path)

    def repathNormalMap(self, path):
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
        if cmds.objExists('%s_Hair_GRP' % characterName):
            cmds.parent('%s_Hair_GRP' % characterName, world=True)
            cmds.delete('%s_%s_AST' % (characterName, projectName))
            self.removeUnusedShader()
            self.createHistory('%s/%s' % (path, type))
            cmds.file(rename='%s/%s/%s_%s.%s' % (path, type, characterName, suffix, mayaformat))
            cmds.file(save=True, type='mayaAscii')

    @staticmethod
    def createHistory(path):
        u"""
        1、判断路径下是否已有 history 文件夹
        2、如果路径下存在除 history 以外的文件，则全部移动到 history 下的当前时间文件夹内

        """
        fileList = cmds.getFileList(folder=path)
        try:
            fileList.remove('history')
        except:
            pass

        if len(fileList) != 0:
            n = datetime.datetime.now().strftime('%Y%m%d%H%M')
            historyPath = os.path.join(path, 'history', n)
            if os.path.exists(historyPath) is False:
                os.makedirs(historyPath)
            for i in fileList:
                shutil.move('%s/%s' % (path, i), historyPath)

    def saveToServer(self, path, type, characterName, suffix, mayaformat):
        """

        :param path: "Y:/Onemt/Marketing/WOE/Assets/Characters"
        :param characterName: "Saleem"
        :param type: "Mod"
        :param mayaformat: "ma"
        :return:
        """
        self.createHistory('%s/%s' % (path, type))
        cmds.file(rename='%s/%s/%s_%s.%s' % (path, type, characterName, suffix, mayaformat))
        cmds.file(save=True, type='mayaAscii')

    def exportAlembic(self, start, end, name, path):
        jobArg = '-frameRange %s %s -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root %s -file %s' % (
            start, end, name, path)
        cmds.AbcExport(jobArg=jobArg)

    def exportFBX(self, bakeAni, start, end, path):
        melScript = 'FBXExportBakeComplexAnimation -v %s;\n        FBXExportBakeComplexStart -v %s;\n        FBXExportBakeComplexEnd -v %s;\n        FBXExportBakeComplexStep -v 1;\n        FBXExportBakeResampleAnimation  -v true;\n        FBXExportSmoothingGroups -v true;\n        FBXExportSmoothMesh -v true;\n        FBXExportReferencedAssetsContent -v true;\n        FBXExportShapes -v true;\n        FBXExportSkins -v true;\n        FBXExport -f "%s" -s;' % (
        bakeAni, start, end, path)
        mm.eval(melScript)

    def pluginInfo(self, plugin):
        if cmds.pluginInfo(plugin, query=True, loaded=True):
            return True
        try:
            cmds.loadPlugin(plugin)
            return True
        except:
            return False

    def makePath(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
