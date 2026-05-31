#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created: 19/10/2020 by Sunxh<175702994@qq.com>
# log:

import maya.cmds as cmds, maya.mel as mel, sys, os, os.path, re, mtoa, maya.OpenMayaUI as omui
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin
from shiboken2 import wrapInstance
scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')

def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)

class LGTSetToolsUI(MayaQWidgetDockableMixin,QtWidgets.QMainWindow):

    VERSION = "3.0.0"

    def __init__(self,parent=maya_main_window()):
        super(LGTSetToolsUI, self).__init__(parent)
        self.setWindowTitle('Light Set Tool ' + self.VERSION)
        self.importFilesPath = ('{}/importFile/').format(scriptsPath)
        self.icoPath = ('{}/icon/').format(scriptsPath)
        self.init_ui()

    def init_ui(self):
        f = QtCore.QFile('%s/ui/LGTSet_Maya.ui' % scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.resize(380, 500)
        self.ui.tabWidget.setTabIcon(0, QtGui.QIcon(QtGui.QPixmap('%s/icon/arnold-logo.png' % scriptsPath)))
        self.ui.ai_tab.layout().addWidget(Arnold())
        self.ui.tabWidget.setTabIcon(1, QtGui.QIcon(QtGui.QPixmap('%s/icon/redshift-logo.png' % scriptsPath)))
        self.ui.tabWidget.setTabIcon(2, QtGui.QIcon(QtGui.QPixmap('%s/icon/vray-logo.png' % scriptsPath)))

    def ImportLighting(self,file):
        lGT = {'Rs_CH_LGT.ma': 'Rs_CH_LGT', 'SKBT_CH_LGT.ma': 'LgtRg_Mstr_Ctrl'}
        LGTFile =self.importFilesPath + file
        if cmds.objExists(lGT[file]):
            cmds.confirmDialog(title='Confirm', message=lGT[file] + ' already exists !', button=['Yes'],
                               defaultButton='Yes', icon='warning')
        elif os.path.exists(LGTFile):
            cmds.file(LGTFile, reference=True, namespace='Rs_CH_LGT')

    def ImportEYEsLighting(self):
        Filename = cmds.textScrollList('EyesLGT', q=True, si=True)
        OF = re.split('.ma', Filename[0])
        LGTFile = 'M:/SKBT/MEL/CGCGXM/CGXM_SKBT_MEL/importFile/LGT/' + Filename[0]
        Circlename = cmds.ls(sl=True)
        if cmds.objExists(Filename[0]):
            cmds.confirmDialog(title='Confirm', message=Filename[0] + ' already exists !', button=['Yes'],
                               defaultButton='Yes', icon='warning')
        elif os.path.exists(LGTFile):
            if Circlename:
                cmds.file(LGTFile, i=True)
                cmds.parentConstraint(Circlename, OF[0], w=True, mo=0)
            else:
                cmds.confirmDialog(title='Confirm', message='Select at least one Curves !!', button=['Yes'],
                                   defaultButton='Yes', icon='warning')

    def rename(self):
        oldName = cmds.textFieldGrp('OldNameUI', q=True, text=True)
        newName = cmds.textFieldGrp('NewNameUI', q=True, text=True)
        newNameUP = newName.upper()
        RLayers = cmds.listConnections('renderLayerManager.renderLayerId')
        RLayers.remove('defaultRenderLayer')
        for RLayer in RLayers:
            print (RLayer)
            RENewName = re.sub(oldName, newNameUP, RLayer)
            cmds.rename(RLayer, RENewName)


class Redshift:
    """
    RedShift:
    """
    def Global_Setting(self):
        mel.eval('unifiedRenderGlobalsWindow;')
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'redshift', type='string')
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', '<Scene>/<RenderLayer>/<RenderLayer>', type='string')
        cmds.setAttr('redshiftOptions.imageFormat', 1)
        cmds.setAttr('redshiftOptions.exrForceMultilayer', 1)
        cmds.setAttr('redshiftOptions.exrMultipart', 1)
        cmds.setAttr('defaultRenderGlobals.animation', 1)
        sceneName = cmds.file(q=True, sceneName=True)
        if cmds.objExists('camRender'):
            cmds.setAttr('camRenderShape.depthOfField', 0)
            cmds.setAttr('camRenderShape.shutterAngle', 180)
            cmds.setAttr('camRenderShape' + '.renderable', 1)
            mel.eval('updateMayaSoftwareCameraControl;')
        else:
            cmds.confirmDialog(title='Warning!!', message='missing camRender!', button=['Yes'], defaultButton='Yes')
        mintime = cmds.playbackOptions(minTime=True, q=True)
        maxtime = cmds.playbackOptions(maxTime=True, q=True)
        cmds.setAttr('defaultRenderGlobals.startFrame', int(mintime))
        cmds.setAttr('defaultRenderGlobals.endFrame', int(maxtime))
        cmds.setAttr('redshiftOptions.aovGlobalEnableMode', 1)

    def CreatAovs(self):
        ExistAov = self.existAovs()
        needAOVs = ['Beauty', 'Cryptomatte', 'Custom', 'Depth', 'Normals', 'Reflections', 'Refractions', 'Shadows',
                    'Sub Surface Scatter', 'Global Illumination', 'Specular Lighting', 'Volume Lighting',
                    'World Position']
        for nn in needAOVs:
            if nn not in ExistAov:
                n = 'redshiftCreateAov("%s");' % nn
                mel.eval(n)
                mel.eval('redshiftUpdateActiveAovList();')
                cmds.setAttr('rsAov_%s.enabled' % nn, 0)

        if cmds.objExists('rsAO_SG') == False:
            cmds.shadingNode('RedshiftAmbientOcclusion', asShader=True, n='rsAO_SG')
            cmds.setAttr('rsAO_SG.numSamples', 1024)
        if cmds.objExists('rsAov_Custom.name'):
            cmds.setAttr('rsAov_Custom.name', 'AO', type='string')
            cmds.defaultNavigation(connectToExisting=True, source='rsAO_SG',
                                   destination='rsAov_Custom.defaultShader')

    def LayerCreator(self):
        CHNameint = cmds.textFieldGrp('CHRsNameUI', q=True, text=True)
        CHName = CHNameint.upper()
        LayerName = cmds.optionMenu('RsLayerNameUI', q=True, v=True)
        COLName = LayerName + '_' + CHName + '_COL'
        AOName = LayerName + '_' + CHName + '_AO'
        ZName = LayerName + '_' + CHName + '_DEPTH'
        SDWName = LayerName + '_' + CHName + '_SDW'
        if LayerName == 'CH':
            selectObjs = cmds.ls(sl=True)
            self.CreatAovs_Rs()
            if cmds.checkBox('COLUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=COLName)
                aaaa = getnewlayername(COLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                self.LayerAovSet_Rs('Beauty', 1)
                self.LayerAovSet_Rs('Cryptomatte')
                self.LayerAovSet_Rs('Custom')
                self.LayerAovSet_Rs('SpecularLighting', 1)
                self.LayerAovSet_Rs('Refractions')
                self.LayerAovSet_Rs('SubSurfaceScatter')
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                self.LayerAovSet_Rs('Custom')
        elif LayerName == 'AN':
            selectObjs = cmds.ls(sl=True)
            self.CreatAovs_Rs()
            if cmds.checkBox('COLUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=COLName)
                aaaa = getnewlayername(COLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                self.LayerAovSet('specular')
                self.LayerAovSet('diffuse')
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                self.LayerAovSet('aiAO')
        elif LayerName == 'BG':
            selectObjs = cmds.ls(sl=True)
            self.CreatAovs_Rs()
            if cmds.checkBox('COLUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=COLName)
                aaaa = getnewlayername(COLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                self.LayerAovSet_Rs('Beauty', 1)
                self.LayerAovSet_Rs('Cryptomatte')
                self.LayerAovSet_Rs('Custom')
                self.LayerAovSet_Rs('SpecularLighting', 1)
                self.LayerAovSet_Rs('Refractions')
                self.LayerAovSet_Rs('SubSurfaceScatter')
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                self.LayerAovSet_Rs('Custom')

    def GetAovs(self):
        hh = {'Beauty': 'beautyUI', 'SpecularLighting': 'specularUI', 'SubSurfaceScatter': 'sssUI', 'Custom': 'AOUI',
              'Reflections': 'reflecUI',
              'Refractions': 'refracUI', 'Normals': 'NUI', 'WorldPosition': 'PUI', 'Depth': 'ZUI',
              'Cryptomatte': 'CrytomatteUI', 'VolumeLighting': 'VolumeUI', 'GlobalIllumination': 'GIUI',
              'Shadows': 'SDWUI'}
        a = cmds.ls(type='RedshiftAOV')
        for b in a:
            try:
                en = cmds.getAttr(b + '.enabled')
                cmds.checkBox(hh[b.split('_')[1]], e=True, v=en)
            except:
                pass

    def setAovs(self):
        hh2 = {'beautyUI': 'Beauty', 'specularUI': 'SpecularLighting', 'sssUI': 'SubSurfaceScatter', 'AOUI': 'Custom',
               'reflecUI': 'Reflections', 'refracUI': 'Refractions', 'NUI': 'Normals', 'PUI': 'WorldPosition',
               'ZUI': 'Depth', 'CrytomatteUI': 'Cryptomatte', 'VolumeUI': 'VolumeLighting',
               'GIUI': 'GlobalIllumination', 'SDWUI': 'Shadows'}
        for h in hh2.keys():
            cd = cmds.checkBox(h, q=True, v=True)
            if cd == True:
                try:
                    cmds.editRenderLayerAdjustment('rsAov_' + hh2[h] + '.enabled')
                    cmds.setAttr('rsAov_' + hh2[h] + '.enabled', 1)
                except:
                    pass

            else:
                try:
                    cmds.editRenderLayerAdjustment('rsAov_' + hh2[h] + '.enabled')
                    cmds.setAttr('rsAov_' + hh2[h] + '.enabled', 0)
                except:
                    pass

    def LayerAovSet(self, aovname, allLight=0):
        cmds.editRenderLayerAdjustment('rsAov_' + aovname + '.enabled')
        cmds.setAttr('rsAov_' + aovname + '.enabled', 1)
        aovLGname = 'rsAov_' + aovname + '.allLightGroups'
        if cmds.objExists(aovLGname):
            cmds.setAttr('rsAov_' + aovname + '.allLightGroups', allLight)


class Arnold(QtWidgets.QMainWindow):
    """
    Arnold:
    """
    allAovs = ['RGBA','diffuse','sss','AO','specular','N','P','Z',
               'crypto_asset','crypto_material','crypto_object',
               'direct','indirect']

    def __init__(self):
        super(Arnold, self).__init__()
        f = QtCore.QFile('%s/ui/int.ui' % scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.ui.ai_layer_combox_01.addItems(['CH','AN','BG'])
        self.ui.ai_layer_combox_02.addItems(['COL', 'SDW'])
        self.gridLayout = QtWidgets.QGridLayout(self.ui.aovs_groupBox)
        # for nn in self.allAovs:
        #     self.cBox = QtWidgets.QCheckBox(self)
        #     self.cBox.setObjectName(nn)
        #     self.cBox.setText(nn)
            # self.ui.gridLayout.addWidget(self.cBox)
        self.getAovsUI()
        print(self.isAovsChecked())
        self.ui.ai_layer_combox_01.currentTextChanged.connect(self.layerNameChanged)
        self.ui.ai_layer_combox_02.currentTextChanged.connect(self.layerNameChanged)
        self.ui.ai_global_setting_pbttn.clicked.connect(self.globalSetting)
        self.ui.ai_create_layers_pbttn.clicked.connect(self.createLayers)

    def isAovsChecked(self):
        checkedAovs = []
        print(self.ui.RGBA.isChecked())
        print(QtWidgets.QCheckBox(self.ui.aovs_groupBox,'RGBA').isChecked())
        for nn in self.allAovs:
            cBox = QtWidgets.QCheckBox("self.ui."+nn)
            print(cBox.text())
            # print(cBox.isChecked())
            if cBox.isChecked():
                print("yess")
                checkedAovs.append(cBox.text())
            else:
                print("no")
        return checkedAovs

    def getLayerName(self):
        layerName = self.ui.ai_layer_combox_01.currentText()
        chName = self.ui.ai_layername_lineEdit.text().upper()
        layerPass = self.ui.ai_layer_combox_02.currentText()
        return layerName, chName, layerPass

    def globalSetting(self):
        if not self.isArnoldLoaded():
            cmds.confirmDialog(title='Warning!!', message=u'找不到Arnold !', button=['Yes'], defaultButton='Yes')
        mel.eval('unifiedRenderGlobalsWindow;')
        cmds.setAttr('defaultRenderGlobals.currentRenderer', 'arnold', type='string')
        cmds.setAttr('defaultArnoldDriver.halfPrecision', 1)
        cmds.setAttr('defaultArnoldDriver.exrTiled', 0)
        cmds.setAttr('defaultArnoldDriver.autocrop', 1)
        cmds.setAttr('defaultArnoldDriver.mergeAOVs', 1)
        mel.eval('setMayaSoftwareFrameExt("name.#.ext", 0)')
        cmds.setAttr('defaultRenderGlobals.imageFilePrefix', '<Scene>/<RenderLayer>/<RenderLayer>', type='string')
        if cmds.objExists('camRender'):
            cmds.setAttr('camRenderShape.depthOfField', 0)
            cmds.setAttr('camRenderShape.shutterAngle', 180)
            cmds.setAttr('camRenderShape' + '.renderable', 1)
            mel.eval('updateMayaSoftwareCameraControl;')
        else:
            cmds.confirmDialog(title='Warning!!', message=u'找不到相机 !', button=['Yes'], defaultButton='Yes')
        mintime, maxtime = cmds.playbackOptions(minTime=True, q=True),cmds.playbackOptions(maxTime=True, q=True)
        cmds.setAttr('defaultRenderGlobals.startFrame', int(mintime))
        cmds.setAttr('defaultRenderGlobals.endFrame', int(maxtime))
        cmds.setAttr('defaultResolution.w', 1920)
        cmds.setAttr('defaultResolution.h', 1280)
        mel.eval('renderLayerEditorRenderable RenderLayerTab "defaultRenderLayer" "0";')
        cmds.setAttr('defaultArnoldRenderOptions.AASamples', 4)
        cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseSamples', 2)
        cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', 1)
        cmds.setAttr('defaultArnoldRenderOptions.GITransmissionSamples', 1)
        cmds.setAttr('defaultArnoldRenderOptions.GISssSamples', 0)
        cmds.setAttr('defaultArnoldRenderOptions.GIVolumeSamples', 0)
        cmds.setAttr('defaultArnoldRenderOptions.motion_blur_enable', 0)
        mel.eval('setAttr -type "string" defaultArnoldRenderOptions.aiUserOptions "parallel_node_init off";')

    def isArnoldLoaded(self):
        if cmds.pluginInfo('mtoa.mll', query=True, loaded=True):
            return True
        else:
            try:
                cmds.loadPlugin('mtoa.mll')
                return True
            except:
                return False

    def layerNameChanged(self):
        self.getAovsUI()

    def getAovsUI(self):
        layerName, chName, layerPass = self.getLayerName()
        if layerName == 'CH':
            if layerPass == "COL":
                self.ui.RGBA.setChecked(True)
                self.ui.diffuse.setChecked(True)
                self.ui.sss.setChecked(True)
            if layerPass == "SDW":
                pass
        elif layerName == 'AN':
            if layerPass == "COL":
                pass
            if layerPass == "SDW":
                pass
        elif layerName == 'BG':
            if layerPass == "COL":
                pass
            if layerPass == "SDW":
                pass

    def existAovs(self):
        """
        :return:已存在的Aovs
        """
        cc = []
        eAOVs = cmds.ls(type='aiAOV')
        for aov in eAOVs:
            d = aov.replace('aiAOV_', '')
            cc.append(d)
        return cc

    def createAovs(self):
        """
        创建Aovs
        :return:
        """
        ExistAovs = self.existAovs()
        needAOVs = ['diffuse', 'sss', 'specular', 'aiAO', 'N', 'P',
                    'Z', 'indirect', 'direct', 'crypto_asset',
                    'crypto_material', 'crypto_object', 'RGBA']
        for needAOV in needAOVs:
            if needAOV not in ExistAovs:
                mtoa.aovs.AOVInterface().addAOV(needAOV, aovType=None)
                cmds.setAttr('aiAOV_%s.enabled'%needAOV, 0)

        if cmds.objExists('_aov_cryptomatte') == False:
            cmds.shadingNode('cryptomatte', asShader=True, n='_aov_cryptomatte')
            mel.eval('connectAttr _aov_cryptomatte.outColor aiAOV_crypto_asset.defaultValue;')
            mel.eval('connectAttr _aov_cryptomatte.outColor aiAOV_crypto_material.defaultValue;')
            mel.eval('connectAttr _aov_cryptomatte.outColor aiAOV_crypto_object.defaultValue;')
        if cmds.objExists('aiAO_SG') == False:
            cmds.shadingNode('aiAmbientOcclusion', asShader=True, n='aiAO_SG')
            cmds.defaultNavigation(connectToExisting=True, source='aiAO_SG', destination='aiAOV_aiAO.defaultValue')
        self.setAOVFilter('1', 'N')
        self.setAOVFilter('2', 'P')
        self.setAOVFilter('3', 'Z')
        return

    def setAOVFilter(self, Num, Aov):
        """

        :param Num:
        :param Aov:
        :return:
        """
        try:
            cmds.disconnectAttr('aiAOVFilter' + Num + '.message', 'aiAOV_' + Aov + '.outputs[0].filter')
            cmds.connectAttr('defaultArnoldFilter.message', 'aiAOV_' + Aov + '.outputs[0].filter')
        except:
            pass

    def createLayers(self):
        """
        创建图层
        :param layerName: CH_
        :param chName: GRP
        :param layerPass: _COL
        :return:
        """
        layerName, chName, layerPass = self.getLayerName()
        layerName_all = layerName + '_' + chName + '_' + layerPass
        selectObjs = cmds.ls(sl=True)
        self.createAovs()
        cmds.select(selectObjs)
        try:
            aovs = self.ui.AOVs_bttnGroup.checkedButton().text()
            print(aovs)
        except:
            aovs = []
        cmds.createRenderLayer(noRecurse=True, name=layerName_all)
        cmds.editRenderLayerGlobals(currentRenderLayer=layerName_all)
        for aov in aovs:
            self.setLayerAov(aov, 1, 1)

    def setLayerAov(self, aovname, enabled=1, allLight=0):
        """
        设置图层AOV
        :param aovname:
        :param enabled:
        :param allLight:
        :return:
        """
        cmds.editRenderLayerAdjustment('aiAOV_' + aovname + '.enabled')
        cmds.setAttr('aiAOV_' + aovname + '.enabled', enabled)
        aovLGname = 'aiAOV_' + aovname + '.lightGroups'
        if cmds.objExists(aovLGname):
            cmds.setAttr(aovLGname, allLight)

    def getAovs(self):
        hh = {'diffuse': 'diffuseUI', 'specular': 'specularUI', 'sss': 'sssUI', 'aiAO': 'AOUI', 'indirect': 'indirUI',
              'direct': 'dirUI', 'N': 'NUI', 'P': 'PUI', 'Z': 'ZUI', 'crypto_asset': 'crypaUI',
              'crypto_material': 'crypmUI', 'crypto_object': 'crypoUI'}
        a = mtoa.aovs.getAOVNodes(names=True)
        for b in a:
            try:
                en = cmds.getAttr(b[1] + '.enabled')
                cmds.checkBox(hh[b[0]], e=True, v=en)
            except:
                pass

    def setAovs(self):
        hh2 = {'diffuseUI': 'diffuse', 'specularUI': 'specular', 'sssUI': 'sss', 'AOUI': 'aiAO', 'indirUI': 'indirect',
               'dirUI': 'direct', 'NUI': 'N', 'PUI': 'P', 'ZUI': 'Z', 'crypaUI': 'crypto_asset',
               'crypmUI': 'crypto_material', 'crypoUI': 'crypto_object'}
        for h in hh2.keys():
            cd = cmds.checkBox(h, q=True, v=True)
            if cd == True:
                try:
                    cmds.editRenderLayerAdjustment('aiAOV_' + hh2[h] + '.enabled')
                    cmds.setAttr('aiAOV_' + hh2[h] + '.enabled', 1)
                except:
                    pass

            else:
                try:
                    cmds.editRenderLayerAdjustment('aiAOV_' + hh2[h] + '.enabled')
                    cmds.setAttr('aiAOV_' + hh2[h] + '.enabled', 0)
                except:
                    pass

    def rayDepth_off(rdv):
        cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.GITotalDepth')
        cmds.setAttr('defaultArnoldRenderOptions.GITotalDepth', rdv)

    def getRayDepth(self):
        va = cmds.getAttr('defaultArnoldRenderOptions.GITotalDepth')
        cmds.intSliderGrp('RayDepthUI', e=True, v=va)

    def setRayDepth(self):
        cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.GITotalDepth')
        aa = cmds.intSliderGrp('RayDepthUI', q=True, v=True)
        cmds.setAttr('defaultArnoldRenderOptions.GITotalDepth', aa)

    def layerSampleSet(aovname, value):
        cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.GI' + aovname + 'Samples')
        cmds.setAttr('defaultArnoldRenderOptions.GI' + aovname + 'Samples', value)

    def setCompression(Comp):
        cmds.editRenderLayerAdjustment('defaultArnoldDriver.exrCompression')
        cmds.setAttr('defaultArnoldDriver.exrCompression', Comp)

    def setDGmode(self):
        mel.eval('int $mode = `optionVar - q "evaluationMode"`;if ($mode != 1) {optionVar -iv "evaluationMode" 1;}')


def setCHANBGAOVs(AOVs):
    if AOVs == 'CH':
        cmds.checkBox('COLUI', e=True, v=True)
        cmds.checkBox('SDWUI', e=True, v=True)
        cmds.checkBox('ZLAUI', e=True, v=False)
    elif AOVs == 'AN':
        cmds.checkBox('COLUI', e=True, v=True)
        cmds.checkBox('SDWUI', e=True, v=True)
        cmds.checkBox('ZLAUI', e=True, v=False)
    elif AOVs == 'BG':
        cmds.checkBox('AMBUI', e=True, v=True)
        cmds.checkBox('BTYUI', e=True, v=True)
        cmds.checkBox('UTIUI', e=True, v=True)
        cmds.checkBox('MVUI', e=True, v=True)
        cmds.checkBox('KEYUI', e=True, v=True)
        cmds.checkBox('RimAUI', e=True, v=False)
        cmds.checkBox('RimBUI', e=True, v=False)
        cmds.checkBox('FillAUI', e=True, v=False)
        cmds.checkBox('FillBUI', e=True, v=False)
        cmds.checkBox('AOLAUI', e=True, v=False)
        cmds.checkBox('MATUI', e=True, v=False)
        cmds.checkBox('EYEUI', e=True, v=False)
        cmds.checkBox('FillCUI', e=True, v=False)
        cmds.checkBox('ZLAUI', e=True, v=False)
        cmds.checkBox('SDWUI', e=True, v=False)
        cmds.checkBox('MaskUI', e=True, v=False)


def getnewlayername(name):
    BTYlayer = cmds.ls(name + '*')
    return BTYlayer[(len(BTYlayer) - 1)]


def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = LGTSetToolsUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()
