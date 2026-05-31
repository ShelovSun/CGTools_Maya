#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created: 19/10/2020 by Sunxh<175702994@qq.com>
# log:

import maya.cmds as cmds, maya.mel as mel, sys, os, os.path, re, mtoa
scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')


class LGTSetToolsUI():

    VERSION = "3.0.5"

    def __init__(self, *args):
        # super(LGTSetToolsUI, self).__init__(parent)
        self.importFilesPath = ('{}/importFile/').format(scriptsPath)
        self.icoPath = ('{}/icon/').format(scriptsPath)
        self.Rs = Redshift()
        self.Ai = Arnold()
        self.init_ui()

    def init_ui(self,*args):
        Wins = 'LGTSetTool'
        if cmds.window(Wins, exists=True):
            cmds.deleteUI(Wins, window=True)
        cmds.window(Wins, title='RenderLayer Set Tool '+ self.VERSION)
        form = cmds.formLayout()
        cmds.columnLayout(form,adjustableColumn=True,bgc=[0.2,0.2,0.2],w=300,h=65)
        cmds.picture(image=self.icoPath + 'LayerTool.png',h=35)
        cmds.setParent('..')

        tabs = cmds.tabLayout(innerMarginWidth=0, innerMarginHeight=0)
        cmds.formLayout(form, edit=True,attachForm=((tabs, 'top', 65), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)))

        child1 = cmds.columnLayout(columnAttach=('both', 0), rowSpacing=0, columnWidth=300)
        cmds.scrollLayout()
        cmds.scriptJob(parent=Wins, event=['renderLayerManagerChange', 'GetAovs_Rs()'])
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        cmds.text(label='', align='left', h=6)
        cmds.button(label='Global Setting', bgc=[0.5, 0.22, 0.1], h=30, w=200, c='Global_Setting_RedShift()')
        cmds.button(label='Import CH_LGT', bgc=[0.36, 0.36, 0.36], h=30, w=200, c='ImportLighting("Rs_CH_LGT.ma")')
        cmds.separator(height=20, style='in', horizontal=True)
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.optionMenu('RsLayerNameUI', label='', w=80, cc=setCHANBGAOVs)
        cmds.menuItem(label='CH')
        cmds.menuItem(label='AN')
        cmds.menuItem(label='BG')
        cmds.textFieldGrp('CHRsNameUI', label='Name', text='GRP', cw2=[60, 100])
        cmds.setParent('..')
        cmds.scrollLayout('scrollLayout', w=100, h=30)
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.checkBox('COLUI', label='COL', v=True)
        cmds.checkBox('SDWUI', label='SDW', v=1)
        cmds.checkBox('ZLAUI', label='Z', v=False)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.button('Create Layers', bgc=[0.36, 0.36, 0.36], h=30, w=200, c='LayerCreator_Redshift()')
        cmds.rowColumnLayout(numberOfColumns=3,columnAlign=[1,'left'])
        cmds.textFieldGrp('OldNameUI', text='GRP', cw1=80)
        cmds.textFieldGrp('NewNameUI', label=u'==>', text='GRP', cw2=[25, 80])
        cmds.button(label='Rename Layer', bgc=[0, 0, 0], h=20, w=80, c=self.rename)
        cmds.setParent('..')
        cmds.separator(height=20, style='in', horizontal=True)
        cmds.text(label='Set AOVs:', align='left', h=18, fn='boldLabelFont')
        cmds.rowColumnLayout(numberOfColumns=4)
        cmds.checkBox('beautyUI', label='beauty', cc='setAovs_Rs()', v=False)
        cmds.checkBox('specularUI', label='specular', cc='setAovs_Rs()', v=False)
        cmds.checkBox('sssUI', label='sss', cc='setAovs_Rs()', v=False)
        cmds.checkBox('AOUI', label='AO', cc='setAovs_Rs()', v=False)
        cmds.checkBox('reflecUI', label='reflection', cc='setAovs_Rs()', v=False)
        cmds.checkBox('refracUI', label='refraction', cc='setAovs_Rs()', v=False)
        cmds.checkBox('NUI', label='N', cc='setAovs_Rs()', v=False)
        cmds.checkBox('PUI', label='P', cc='setAovs_Rs()', v=False)
        cmds.checkBox('ZUI', label='Z', cc='setAovs_Rs()', v=False)
        cmds.checkBox('CrytomatteUI', label='crytomatte', cc='setAovs_Rs()', v=0)
        cmds.checkBox('VolumeUI', label='Volume', cc='setAovs_Rs()', v=False)
        cmds.checkBox('GIUI', label='GI', cc='setAovs_Rs()', v=False)
        cmds.checkBox('SDWUI', label='shadows', cc='setAovs_Rs()', v=False)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')

        child2 = cmds.columnLayout(columnAttach=('both', 5), rowSpacing=1, columnWidth=300)
        cmds.scrollLayout()
        cmds.scriptJob(parent=Wins, event=['renderLayerManagerChange', 'GetAovs_Ai()'])
        cmds.scriptJob(parent=Wins, event=['renderLayerManagerChange', 'GetRayDepth()'])
        cmds.columnLayout(adjustableColumn=True, rowSpacing=2)
        cmds.text(label='', align='left', h=6)
        cmds.button(label='Global Setting', bgc=[0.1, 0.5, 0.1], h=30, w=200, c=self.Ai.globalSetting)
        cmds.button(label='Import CH_LGT', bgc=[0.36, 0.36, 0.36], h=30, w=200, c='ImportLighting("Ai_CH_LGT")')
        cmds.separator(height=20, style='in', horizontal=True)
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.optionMenu('AiLayerNameUI', label='', w=80, cc=setCHANBGAOVs)
        cmds.menuItem(label='CH')
        cmds.menuItem(label='AN')
        cmds.menuItem(label='BG')
        cmds.textFieldGrp('CHAiNameUI', label='Name', text='GRP', cw2=[60, 100])
        cmds.setParent('..')
        cmds.scrollLayout('scrollLayout', w=100, h=30)
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.checkBox('COLUI', label='COL', v=True)
        cmds.checkBox('SDWUI', label='SDW', v=1)
        cmds.checkBox('ZLAUI', label='Z', v=False)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.button('Create Layers', bgc=[0.36, 0.36, 0.36], h=30, w=200, c=self.Ai.layerCreator)
        cmds.separator(height=20, style='in', horizontal=True)
        cmds.intSliderGrp('RayDepthUI', field=True, label='Ray Depth', cw3=[60, 50, 20], cc='SetRayDepth()', minValue=0,
                          maxValue=16, value=0)
        cmds.text(label='Set AOVs:', align='left', h=18, fn='boldLabelFont')
        cmds.rowColumnLayout(numberOfColumns=4)
        cmds.checkBox('diffuseUI', label='diffuse', cc='setAovs_Ai()', v=False)
        cmds.checkBox('specularUI', label='specular', cc='setAovs_Ai()', v=False)
        cmds.checkBox('sssUI', label='sss', cc='setAovs_Ai()', v=False)
        cmds.checkBox('AOUI', label='AO', cc='setAovs_Ai()', v=False)
        cmds.checkBox('indirUI', label='indir', cc='setAovs_Ai()', v=False)
        cmds.checkBox('dirUI', label='dir', cc='setAovs_Ai()', v=False)
        cmds.checkBox('NUI', label='N', cc='setAovs_Ai()', v=False)
        cmds.checkBox('PUI', label='P', cc='setAovs_Ai()', v=False)
        cmds.checkBox('ZUI', label='Z', cc='setAovs_Ai()', v=False)
        cmds.checkBox('crypaUI', label='cryp_a', cc='setAovs_Ai()', v=False)
        cmds.checkBox('crypmUI', label='cryp_m', cc='setAovs_Ai()', v=False)
        cmds.checkBox('crypoUI', label='cryp_o', cc='setAovs_Ai()', v=False)
        cmds.setParent('..')
        cmds.rowColumnLayout(numberOfColumns=5)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        child3 = cmds.columnLayout(columnAttach=('both', 5), rowSpacing=1, columnWidth=300)
        cmds.text(label='Import LGT:', align='left', h=18, fn='boldLabelFont')
        cmds.scrollLayout(w=250, h=250)
        cmds.columnLayout(adjustableColumn=True, rs=2)
        OFiles = os.listdir(scriptsPath + '/importFile/LGT')
        cmds.textScrollList('EyesLGT', numberOfRows=8, showIndexedItem=4, w=250, h=500, a=OFiles,
                            dcc='ImportEYEsLighting()')
        cmds.text(label=' ', align='left', h=20, fn='boldLabelFont')
        cmds.tabLayout(tabs, edit=True, tabLabel=((child1, 'RedShift'), (child2, 'Arnold'), (child3, 'Lighting')),selectTab=child2)
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.showWindow(Wins)

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

    def rename(self,*args):
        oldName = cmds.textFieldGrp('OldNameUI', q=True, text=True)
        newName = cmds.textFieldGrp('NewNameUI', q=True, text=True)
        newNameUP = newName.upper()
        RLayers = cmds.listConnections('renderLayerManager.renderLayerId')
        RLayers.remove('defaultRenderLayer')
        for RLayer in RLayers:
            print (RLayer)
            RENewName = re.sub(oldName, newNameUP, RLayer)
            cmds.rename(RLayer, RENewName)


class Redshift():

    def Global_Setting_Rs(self):
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

    def CreatAovs_Rs(self):
        ExistAov = existAovs()
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

    def LayerCreator_Rs(self):
        CHNameint = cmds.textFieldGrp('CHRsNameUI', q=True, text=True)
        CHName = CHNameint.upper()
        LayerName = cmds.optionMenu('RsLayerNameUI', q=True, v=True)
        COLName = LayerName + '_' + CHName + '_COL'
        AOName = LayerName + '_' + CHName + '_AO'
        ZName = LayerName + '_' + CHName + '_DEPTH'
        SDWName = LayerName + '_' + CHName + '_SDW'
        if LayerName == 'CH':
            selectObjs = cmds.ls(sl=True)
            CreatAovs_Rs()
            if cmds.checkBox('COLUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=COLName)
                aaaa = getnewlayername(COLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet_Rs('Beauty', 1)
                LayerAovSet_Rs('Cryptomatte')
                LayerAovSet_Rs('Custom')
                LayerAovSet_Rs('SpecularLighting', 1)
                LayerAovSet_Rs('Refractions')
                LayerAovSet_Rs('SubSurfaceScatter')
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet_Rs('Custom')
        elif LayerName == 'AN':
            selectObjs = cmds.ls(sl=True)
            CreatAovs_Rs()
            if cmds.checkBox('COLUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=COLName)
                aaaa = getnewlayername(COLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('aiAO')
        elif LayerName == 'BG':
            selectObjs = cmds.ls(sl=True)
            CreatAovs_Rs()
            if cmds.checkBox('COLUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=COLName)
                aaaa = getnewlayername(COLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet_Rs('Beauty', 1)
                LayerAovSet_Rs('Cryptomatte')
                LayerAovSet_Rs('Custom')
                LayerAovSet_Rs('SpecularLighting', 1)
                LayerAovSet_Rs('Refractions')
                LayerAovSet_Rs('SubSurfaceScatter')
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet_Rs('Custom')

    def GetAovs_Rs(self):
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

    def setAovs_Rs(self):
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

    def LayerAovSet_Rs(self,aovname, allLight=0):
        cmds.editRenderLayerAdjustment('rsAov_' + aovname + '.enabled')
        cmds.setAttr('rsAov_' + aovname + '.enabled', 1)
        rsaovname = 'rsAov_' + aovname + '.allLightGroups'
        if cmds.objExists(rsaovname):
            cmds.setAttr('rsAov_' + aovname + '.allLightGroups', allLight)


class Arnold():

    def globalSetting(self,*args):
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
            cmds.confirmDialog(title='Warning!!', message='missing camRender!', button=['Yes'], defaultButton='Yes')
        mintime = cmds.playbackOptions(minTime=True, q=True)
        maxtime = cmds.playbackOptions(maxTime=True, q=True)
        cmds.setAttr('defaultRenderGlobals.startFrame', int(mintime))
        cmds.setAttr('defaultRenderGlobals.endFrame', int(maxtime))
        cmds.setAttr('defaultResolution.w', 1920)
        cmds.setAttr('defaultResolution.h', 1080)
        mel.eval('renderLayerEditorRenderable RenderLayerTab "defaultRenderLayer" "0";')
        cmds.setAttr('defaultArnoldRenderOptions.AASamples', 4)
        cmds.setAttr('defaultArnoldRenderOptions.GIDiffuseSamples', 2)
        cmds.setAttr('defaultArnoldRenderOptions.GISpecularSamples', 1)
        cmds.setAttr('defaultArnoldRenderOptions.GITransmissionSamples', 1)
        cmds.setAttr('defaultArnoldRenderOptions.GISssSamples', 0)
        cmds.setAttr('defaultArnoldRenderOptions.GIVolumeSamples', 0)
        cmds.setAttr('defaultArnoldRenderOptions.motion_blur_enable', 0)
        mel.eval('setAttr -type "string" defaultArnoldRenderOptions.aiUserOptions "parallel_node_init off";')

    def creatAovs(self,*args):
        ExistAov = existAovs()
        needAOVs = ['diffuse', 'sss', 'specular', 'aiAO', 'N', 'P', 'Z', 'indirect', 'direct', 'crypto_asset',
                    'crypto_material', 'crypto_object', 'motionvector']
        for nn in needAOVs:
            if nn not in ExistAov:
                mtoa.aovs.AOVInterface().addAOV(nn, aovType=None)
                cmds.setAttr('aiAOV_%s.enabled' % nn, 0)

        if cmds.objExists('_aov_cryptomatte') == False:
            cmds.shadingNode('cryptomatte', asShader=True, n='_aov_cryptomatte')
            mel.eval('connectAttr _aov_cryptomatte.outColor aiAOV_crypto_asset.defaultValue;')
            mel.eval('connectAttr _aov_cryptomatte.outColor aiAOV_crypto_material.defaultValue;')
            mel.eval('connectAttr _aov_cryptomatte.outColor aiAOV_crypto_object.defaultValue;')
        if cmds.objExists('aiAO_SG') == False:
            cmds.shadingNode('aiAmbientOcclusion', asShader=True, n='aiAO_SG')
            cmds.defaultNavigation(connectToExisting=True, source='aiAO_SG', destination='aiAOV_aiAO.defaultValue')
        setaiAOVFilter('1', 'N')
        setaiAOVFilter('2', 'P')
        setaiAOVFilter('3', 'Z')
        return

    def layerCreator(self,*args):
        CHNameint = cmds.textFieldGrp('CHAiNameUI', q=True, text=True)
        CHName = CHNameint.upper()
        LayerName = cmds.optionMenu('AiLayerNameUI', q=True, v=True)
        AMBName = LayerName + '_' + CHName + '_AMB'
        BTYName = LayerName + '_' + CHName + '_BTY'
        LABName = LayerName + '_' + CHName + '_UTI'
        MVName = LayerName + '_' + CHName + '_MV'
        KEYName = LayerName + '_' + CHName + '_KEY'
        AOName = LayerName + '_' + CHName + '_AO'
        RGBName = LayerName + '_' + CHName + '_MAT'
        FILLAName = LayerName + '_' + CHName + '_FILL_A'
        FILLBName = LayerName + '_' + CHName + '_FILL_B'
        FILLCName = LayerName + '_' + CHName + '_FILL_C'
        RIMRName = LayerName + '_' + CHName + '_RIM_A'
        RIMLName = LayerName + '_' + CHName + '_RIM_B'
        EYEName = LayerName + '_' + CHName + '_EYE_SP'
        ZName = LayerName + '_' + CHName + '_DEPTH'
        SDWName = LayerName + '_' + CHName + '_SDW'
        MASKName = LayerName + '_' + CHName + '_MASK'
        if LayerName == 'CH':
            selectObjs = cmds.ls(sl=True)
            self.creatAovs()
            if cmds.checkBox('AMBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=AMBName)
                aaaa = getnewlayername(AMBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('indirect')
                LayerAovSet('direct')
                LayerAovSet('diffuse')
                LayerAovSet('aiAO')
                LayerSampleSet('Sss', 3)
            if cmds.checkBox('BTYUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=BTYName)
                aaaa = getnewlayername(BTYName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerAovSet('aiAO')
                LayerSampleSet('Sss', 3)
            if cmds.checkBox('UTIUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=LABName)
                aaaa = getnewlayername(LABName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                if cmds.objExists('LAB_SG') == False:
                    cmds.shadingNode('aiStandardSurface', asShader=True, n='LAB_SG')
                    cmds.setAttr('LAB_SG.base', 1)
                    cmds.setAttr('LAB_SG.specular', 0)
                mel.eval('hookShaderOverride( "' + aaaa + '" , "", "LAB_SG");')
                LayerAovSet('N')
                LayerAovSet('P')
                LayerAovSet('Z')
                LayerAovSet('aiAO')
                LayerAovSet('motionvector')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MVUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=MVName)
                aaaa = getnewlayername(MVName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.motion_blur_enable')
                cmds.setAttr('defaultArnoldRenderOptions.motion_blur_enable', 1)
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
                if cmds.objExists('aiMV_SG') == False:
                    cmds.file(importFilesPath + 'aiMV_SG.mb', i=True)
                    mel.eval('hookShaderOverride( "' + aaaa + '" , "", "MV_SG");')
                else:
                    mel.eval('hookShaderOverride( "' + aaaa + '" , "", "MV_SG");')
            if cmds.checkBox('KEYUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=KEYName)
                aaaa = getnewlayername(KEYName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Sss', 3)
            if cmds.checkBox('RimAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RIMRName)
                aaaa = getnewlayername(RIMRName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Sss', 3)
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('RimBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RIMLName)
                aaaa = getnewlayername(RIMLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Sss', 3)
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLAName)
                aaaa = getnewlayername(FILLAName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Sss', 3)
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLBName)
                aaaa = getnewlayername(FILLBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Sss', 3)
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillCUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLCName)
                aaaa = getnewlayername(FILLCName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Sss', 3)
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('AOLAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=AOName)
                aaaa = getnewlayername(AOName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                cmds.hyperShade(assign='aiAO_SG')
                cmds.select(cl=True)
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MATUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RGBName)
                aaaa = getnewlayername(RGBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('crypto_object')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('EYEUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=EYEName)
                aaaa = getnewlayername(EYEName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MaskUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=MASKName)
                aaaa = getnewlayername(MASKName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Transmission', 2)
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('aiAO')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
        elif LayerName == 'AN':
            selectObjs = cmds.ls(sl=True)
            CreatAovs()
            if cmds.checkBox('AMBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=AMBName)
                aaaa = getnewlayername(AMBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerAovSet('aiAO')
            if cmds.checkBox('BTYUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=BTYName)
                aaaa = getnewlayername(BTYName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerAovSet('aiAO')
            if cmds.checkBox('UTIUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=LABName)
                aaaa = getnewlayername(LABName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                if cmds.objExists('LAB_SG') == False:
                    cmds.shadingNode('aiStandardSurface', asShader=True, n='LAB_SG')
                    cmds.setAttr('LAB_SG.base', 1)
                    cmds.setAttr('LAB_SG.specular', 0)
                mel.eval('hookShaderOverride( "' + aaaa + '" , "", "LAB_SG");')
                LayerAovSet('N')
                LayerAovSet('P')
                LayerAovSet('Z')
                LayerAovSet('aiAO')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MVUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=MVName)
                aaaa = getnewlayername(MVName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.motion_blur_enable')
                cmds.setAttr('defaultArnoldRenderOptions.motion_blur_enable', 1)
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
                if cmds.objExists('aiMV_SG') == False:
                    cmds.file(importFilesPath + 'aiMV_SG.mb', i=True)
                    mel.eval('hookShaderOverride( "' + aaaa + '" , "", "MV_SG");')
                else:
                    mel.eval('hookShaderOverride( "' + aaaa + '" , "", "MV_SG");')
            if cmds.checkBox('KEYUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=KEYName)
                aaaa = getnewlayername(KEYName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
            if cmds.checkBox('RimAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RIMRName)
                aaaa = getnewlayername(RIMRName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('RimBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RIMLName)
                aaaa = getnewlayername(RIMLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLAName)
                aaaa = getnewlayername(FILLAName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLBName)
                aaaa = getnewlayername(FILLBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillCUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLCName)
                aaaa = getnewlayername(FILLCName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('AOLAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=AOName)
                aaaa = getnewlayername(AOName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                cmds.hyperShade(assign='aiAO_SG')
                cmds.select(cl=True)
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MATUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RGBName)
                aaaa = getnewlayername(RGBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('crypto_object')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MaskUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=MASKName)
                aaaa = getnewlayername(MASKName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Transmission', 2)
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('aiAO')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
        elif LayerName == 'BG':
            selectObjs = cmds.ls(sl=True)
            CreatAovs()
            if cmds.checkBox('AMBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=AMBName)
                aaaa = getnewlayername(AMBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
            if cmds.checkBox('BTYUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=BTYName)
                aaaa = getnewlayername(BTYName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
            if cmds.checkBox('UTIUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=LABName)
                aaaa = getnewlayername(LABName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('N')
                LayerAovSet('P')
                LayerAovSet('Z')
                LayerAovSet('aiAO')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MVUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=MVName)
                aaaa = getnewlayername(MVName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.motion_blur_enable')
                cmds.setAttr('defaultArnoldRenderOptions.motion_blur_enable', 1)
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
                if cmds.objExists('aiMV_SG') == False:
                    cmds.file(importFilesPath + 'aiMV_SG.mb', i=True)
                    mel.eval('hookShaderOverride( "' + aaaa + '" , "", "MV_SG");')
                else:
                    mel.eval('hookShaderOverride( "' + aaaa + '" , "", "MV_SG");')
            if cmds.checkBox('KEYUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=KEYName)
                aaaa = getnewlayername(KEYName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
            if cmds.checkBox('RimAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RIMRName)
                aaaa = getnewlayername(RIMRName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('RimBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RIMLName)
                aaaa = getnewlayername(RIMLName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLAName)
                aaaa = getnewlayername(FILLAName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillBUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLBName)
                aaaa = getnewlayername(FILLBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('FillCUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=FILLCName)
                aaaa = getnewlayername(FILLCName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('sss')
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Diffuse', 1)
            if cmds.checkBox('AOLAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=AOName)
                aaaa = getnewlayername(AOName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                cmds.hyperShade(assign='aiAO_SG')
                cmds.select(cl=True)
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MATUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=RGBName)
                aaaa = getnewlayername(RGBName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                RayDepth_off(0)
                LayerAovSet('crypto_object')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('ZLAUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=ZName)
                aaaa = getnewlayername(ZName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                if cmds.objExists('aiDepth_SG') == False:
                    cmds.file(importFilesPath + 'aiDepth_SG.mb', i=True)
                    cmds.hyperShade(assign='aiDepth_SG')
                else:
                    cmds.hyperShade(assign='aiDepth_SG')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)
            if cmds.checkBox('MaskUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=MASKName)
                aaaa = getnewlayername(MASKName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('specular')
                LayerAovSet('diffuse')
                LayerSampleSet('Transmission', 2)
            if cmds.checkBox('SDWUI', q=True, v=True):
                cmds.select(selectObjs)
                cmds.createRenderLayer(noRecurse=True, name=SDWName)
                aaaa = getnewlayername(SDWName)
                cmds.editRenderLayerGlobals(currentRenderLayer=aaaa)
                LayerAovSet('aiAO')
                LayerSampleSet('Diffuse', 0)
                LayerSampleSet('Specular', 0)
                LayerSampleSet('Transmission', 0)

    def GetAovs_Ai():
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

    def setAovs_Ai():
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

    def RayDepth_off(rdv):
        cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.GITotalDepth')
        cmds.setAttr('defaultArnoldRenderOptions.GITotalDepth', rdv)

    def GetRayDepth():
        va = cmds.getAttr('defaultArnoldRenderOptions.GITotalDepth')
        cmds.intSliderGrp('RayDepthUI', e=True, v=va)

    def SetRayDepth():
        cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.GITotalDepth')
        aa = cmds.intSliderGrp('RayDepthUI', q=True, v=True)
        cmds.setAttr('defaultArnoldRenderOptions.GITotalDepth', aa)

    def LayerAovSet_Ai(aovname, enabled=1):
        cmds.editRenderLayerAdjustment('aiAOV_' + aovname + '.enabled')
        cmds.setAttr('aiAOV_' + aovname + '.enabled', enabled)

    def LayerSampleSet(aovname, value):
        cmds.editRenderLayerAdjustment('defaultArnoldRenderOptions.GI' + aovname + 'Samples')
        cmds.setAttr('defaultArnoldRenderOptions.GI' + aovname + 'Samples', value)

    def SetCompression(Comp):
        cmds.editRenderLayerAdjustment('defaultArnoldDriver.exrCompression')
        cmds.setAttr('defaultArnoldDriver.exrCompression', Comp)









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

def setaiAOVFilter(Num, Aov):
    try:
        cmds.disconnectAttr('aiAOVFilter' + Num + '.message', 'aiAOV_' + Aov + '.outputs[0].filter')
        cmds.connectAttr('defaultArnoldFilter.message', 'aiAOV_' + Aov + '.outputs[0].filter')
    except:
        pass

def existAovs():
    cc = []
    eAOVs = cmds.ls(type='aiAOV')
    for aov in eAOVs:
        d = aov.replace('aiAOV_', '')
        cc.append(d)
    return cc

def getnewlayername(name):
    BTYlayer = cmds.ls(name + '*')
    return BTYlayer[(len(BTYlayer) - 1)]

