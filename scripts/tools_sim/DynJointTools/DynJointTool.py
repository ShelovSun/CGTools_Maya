#!/usr/bin/env python
# -*- coding: utf-8 -*-
""""""
import maya.OpenMayaUI as apiUI, shiboken2, maya.cmds as cmds, maya.mel as mm, PySide2.QtGui as qg, PySide2.QtCore as qc, PySide2.QtWidgets as qw, random, sys

def getMayaWindow():
    OOO00OOO00O0OOOO0 = apiUI.MQtUtil.mainWindow()
    if OOO00OOO00O0OOOO0 is not None:
        return shiboken2.wrapInstance(long(OOO00OOO00O0OOOO0), qw.QMainWindow)
    else:
        return


class DynJointToolWidget(qw.QWidget):

    def __init__(O0000O0O000000OOO, parent=None):
        super(DynJointToolWidget, O0000O0O000000OOO).__init__(parent=parent)
        O0000O0O000000OOO.setWindowFlags(qc.Qt.Window)
        O0000O0O000000OOO.setObjectName('DynJointTool')
        O0000O0O000000OOO.setWindowTitle('DynJointTool ©GuanYJ')
        O0000O0O000000OOO.setLayout(qw.QVBoxLayout())
        O0000O0O000000OOO.layout().setContentsMargins(5, 5, 5, 5)
        O0000O0O000000OOO.layout().setSpacing(5)
        O0000O0O000000OOO.layout().setAlignment(qc.Qt.AlignTop)
        O000OOO00000O00OO = qw.QLabel('Name:')
        O0000O0O000000OOO.name_line = qw.QLineEdit()
        O0000O0O000000OOO.name_bttn = qw.QPushButton('Create')
        O000OOO00000O00OO.setFixedWidth(35)
        O0000O0O000000OOO.name_line.setEnabled(True)
        O0000O0O000000OOO.name_bttn.setFixedWidth(40)
        O00O000O000000O00 = qw.QHBoxLayout()
        O00O000O000000O00.addWidget(O000OOO00000O00OO)
        O00O000O000000O00.addWidget(O0000O0O000000OOO.name_line)
        O00O000O000000O00.addWidget(O0000O0O000000OOO.name_bttn)
        O0000O0O000000OOO.layout().addLayout(O00O000O000000O00)
        OO0000O0OO0O00O00 = qw.QFrame()
        OOOOOOOOO00OO0000 = qw.QHBoxLayout()
        OOOOOOOOO00OO0000.setContentsMargins(0, 0, 0, 0)
        OO0000O0OO0O00O00.setLayout(OOOOOOOOO00OO0000)
        OOOO00OOOO000O0OO = qw.QHBoxLayout()
        O0O000O0O0OOOO00O = qw.QVBoxLayout()
        O0000OOO000O0OO00 = qw.QVBoxLayout()
        OOO00O0OOO0OOOOOO = qw.QLabel('HairSys')
        OO0O00OOO0O0O0O0O = qw.QLabel('Nucleus')
        O0000O0O000000OOO.hairSys_listWidget = qw.QListWidget()
        O0000O0O000000OOO.nucleus_listWidget = qw.QListWidget()
        OOO00O0OOO0OOOOOO.setAlignment(qc.Qt.AlignCenter)
        OO0O00OOO0O0O0O0O.setAlignment(qc.Qt.AlignCenter)
        O0000O0O000000OOO.hairSys_listWidget.setSelectionMode(qw.QAbstractItemView.ExtendedSelection)
        O0000O0O000000OOO.nucleus_listWidget.setSelectionMode(qw.QAbstractItemView.ExtendedSelection)
        O0O000O0O0OOOO00O.addWidget(OOO00O0OOO0OOOOOO)
        O0O000O0O0OOOO00O.addWidget(O0000O0O000000OOO.hairSys_listWidget)
        O0000OOO000O0OO00.addWidget(OO0O00OOO0O0O0O0O)
        O0000OOO000O0OO00.addWidget(O0000O0O000000OOO.nucleus_listWidget)
        OOOOOOOOO00OO0000.addLayout(O0O000O0O0OOOO00O)
        OOOOOOOOO00OO0000.addLayout(O0000OOO000O0OO00)
        O0000O0O000000OOO.layout().addWidget(OO0000O0OO0O00O00)
        OOO0OO0O0OOOO000O = qw.QPushButton('Add Nucleus')
        O0O0O00OO00OO0OOO = qw.QPushButton('Delete Nucleus')
        OOO0OO0O0OOOO000O.setFixedHeight(40)
        O0O0O00OO00OO0OOO.setFixedHeight(40)
        O0O000OO0OOO00000 = qw.QHBoxLayout()
        O0O000OO0OOO00000.addWidget(OOO0OO0O0OOOO000O)
        O0O000OO0OOO00000.addWidget(O0O0O00OO00OO0OOO)
        O0000O0O000000OOO.layout().addLayout(O0O000OO0OOO00000)
        O00OOOO00OOOOOOO0 = qw.QPushButton('Bake')
        OOOO0OO0O0OO00O00 = qw.QPushButton('UnBake')
        O00OOOO00OOOOOOO0.setFixedHeight(40)
        OOOO0OO0O0OO00O00.setFixedHeight(40)
        OOO0O0O00OO00000O = qw.QHBoxLayout()
        OOO0O0O00OO00000O.addWidget(O00OOOO00OOOOOOO0)
        OOO0O0O00OO00000O.addWidget(OOOO0OO0O0OO00O00)
        O0000O0O000000OOO.layout().addLayout(OOO0O0O00OO00000O)
        O0000O0O000000OOO.getHairSystems()
        O0000O0O000000OOO.getHairNucleus()
        O0000O0O000000OOO.hairSys_listWidget.itemActivated.connect(O0000O0O000000OOO.currentHairSystem)
        O0000O0O000000OOO.hairSys_listWidget.itemSelectionChanged.connect(O0000O0O000000OOO.currentHairSystem)
        O0000O0O000000OOO.nucleus_listWidget.itemActivated.connect(O0000O0O000000OOO.currentHairNucleus)
        O0000O0O000000OOO.nucleus_listWidget.itemSelectionChanged.connect(O0000O0O000000OOO.currentHairNucleus)
        O0000O0O000000OOO.name_bttn.clicked.connect(O0000O0O000000OOO.createDynHairSys)
        O0O0O00OO00OO0OOO.clicked.connect(O0000O0O000000OOO.delNucleus)
        OOO0OO0O0OOOO000O.clicked.connect(O0000O0O000000OOO.addNucleus)
        O00OOOO00OOOOOOO0.clicked.connect(O0000O0O000000OOO.bake)
        OOOO0OO0O0OO00O00.clicked.connect(O0000O0O000000OOO.unDoBake)

    def createDynHairSys(O0000OO0O00O00OO0):
        OO0OO0O00O000OO00 = O0000OO0O00O00OO0.getScale()
        if cmds.objExists(O0000OO0O00O00OO0.hairSysName()):
            cmds.warning('Please give a another name!!!')
            return
        OO0OO00000OO0OOOO = cmds.ls(sl=True, type='joint')
        if OO0OO00000OO0OOOO == []:
            cmds.warning('Please select joints')
            return
        if cmds.objExists('nucleus1'):
            cmds.rename('nucleus1', 'gyj_template_nucleus')
        OOOOOO000OOO0OO0O = []
        for O00OOO0O000O0OO00 in OO0OO00000OO0OOOO:
            OOOO000OOOOOOOO0O = []
            OO00O0OOO000OO0O0 = O00OOO0O000O0OO00
            cmds.select(OO00O0OOO000OO0O0, hi=1)
            OO0000O000OO00OOO = cmds.ls(sl=True, type='joint')
            O00000OO0OO0OO0OO = OO0000O000OO00OOO[(-1)]
            cmds.select(O00OOO0O000O0OO00, hi=1)
            O0OOO000OO0O0OO00 = cmds.ls(sl=True)
            cmds.select(cl=True)
            for OO000OOOO0OOOO0O0 in O0OOO000OO0O0OO00:
                OOOO000OOOOOOOO0O.append(OO000OOOO0OOOO0O0)
                if OO000OOOO0OOOO0O0 == O00000OO0OO0OO0OO:
                    break

            cmds.select(O0000OO0O00O00OO0.jointEndAndStart(OO00O0OOO000OO0O0, O00000OO0OO0OO0OO, '_drv_jnt'))
            O0O00OOO0O0O0O0O0 = cmds.ls(sl=True)
            cmds.select(cl=True)
            O00OOO00O0O000OO0 = O0O00OOO0O0O0O0O0[0]
            OO0O0OOOOO00O000O = cmds.circle(name='%s_dyn_root_ctrl' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]), nr=(0,
                                                                                                                               0,
                                                                                                                               1), c=(0,
                                                                                                                                      0,
                                                                                                                                      0), sw=360, r=2, ch=0)[0]
            cmds.setAttr('%s.scaleX' % OO0O0OOOOO00O000O, OO0OO0O00O000OO00)
            cmds.setAttr('%s.scaleY' % OO0O0OOOOO00O000O, OO0OO0O00O000OO00)
            cmds.setAttr('%s.scaleZ' % OO0O0OOOOO00O000O, OO0OO0O00O000OO00)
            cmds.setAttr('%s.rotateY' % OO0O0OOOOO00O000O, 90)
            cmds.makeIdentity(OO0O0OOOOO00O000O, apply=True, t=0, r=1, s=1, n=0, pn=1)
            OO000OOOO0OOO00OO = cmds.group(name='%s_grp' % OO0O0OOOOO00O000O)
            O0000OO0O00O00OO0.getCtrlPos(O00OOO00O0O000OO0, OO000OOOO0OOO00OO)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='bakeCtrlVisb', at='long', min=0, max=1, dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='aniCtrlVisb', at='long', min=0, max=1, dv=1, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='dynJoint', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='drvJoint', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='bakeJoint', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='drvCtrl', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='bakeCtrl', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='baseCurve', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='dynCurve', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='hairFol', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='hairSys', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='hairNuc', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='skinJoint', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='dynIk', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='bakeLoc', at='float', dv=0, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='drvCtrlCons', at='long', min=0, max=1, dv=1, h=0, k=0)
            cmds.addAttr(OO0O0OOOOO00O000O, longName='aniCtrlCons', at='long', min=0, max=1, dv=0, h=0, k=0)
            O0000OOOOOO0000OO = '%s_baseCurve' % O0O00OOO0O0O0O0O0[0]
            OO00O00O0OOOO0O00 = 'base'
            O0O00O0O0000000O0 = []
            for OO000OOOO0OOOO0O0 in O0O00OOO0O0O0O0O0:
                O00OOOO000OOO00O0 = cmds.xform(OO000OOOO0OOOO0O0, q=1, ws=1, t=1)
                OOOO0O00O00O00OOO = (O00OOOO000OOO00O0[0], O00OOOO000OOO00O0[1], O00OOOO000OOO00O0[2])
                O0O00O0O0000000O0.append(OOOO0O00O00O00OOO)
                try:
                    cmds.addAttr(OO000OOOO0OOOO0O0, longName='driveJoint%d' % (O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0) + 1), at='float', dv=0, h=0, k=0)
                except:
                    pass

                cmds.connectAttr('%s.drvJoint' % OO0O0OOOOO00O000O, '%s.driveJoint%d' % (OO000OOOO0OOOO0O0, O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0) + 1))

            OO0O0OO00O0O0OOO0 = cmds.curve(n=O0000OOOOOO0000OO, d=3, ep=O0O00O0O0000000O0)
            cmds.rebuildCurve(OO0O0OO00O0O0OOO0, rt=0, s=len(O0O00OOO0O0O0O0O0) - 1)
            for OO000OOOO0OOOO0O0 in O0O00OOO0O0O0O0O0:
                O0OOOO0O0O0000OO0 = cmds.xform(OO000OOOO0OOOO0O0, q=1, t=1, ws=1)
                cmds.select('%s.ep[%d]' % (OO0O0OO00O0O0OOO0, O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0)))
                O000OO0O000000000 = cmds.ls(sl=True)
                cmds.xform(O000OO0O000000000, t=(O0OOOO0O0O0000OO0[0], O0OOOO0O0O0000OO0[1], O0OOOO0O0O0000OO0[2]))
                cmds.select(cl=True)

            try:
                cmds.addAttr(OO0O0OO00O0O0OOO0, longName='baseCurve', at='float', dv=0, h=0, k=0)
            except:
                pass

            cmds.connectAttr('%s.baseCurve' % OO0O0OOOOO00O000O, '%s.baseCurve' % OO0O0OO00O0O0OOO0)
            cmds.select(OO0O0OO00O0O0OOO0)
            try:
                cmds.select(O0000OO0O00O00OO0.hairSysName(), add=True)
            except:
                pass

            mm.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
            OOO0OOOO00OOO0O00 = cmds.ls(sl=True)
            OOOOO0O00O0OO00OO = cmds.listRelatives(OOO0OOOO00OOO0O00, p=True)
            OO000000O0000O0OO = cmds.rename(OOOOO0O00O0OO00OO, O0000OO0O00O00OO0.hairSysName(), ignoreShape=False)
            OOO0OOOO00OOO0O00 = cmds.listRelatives(OO000000O0000O0OO, c=True)
            OOO0OOOO00OOO0O00 = cmds.rename(OOO0OOOO00OOO0O00, O0000OO0O00O00OO0.hairSysName() + 'Shape')
            try:
                cmds.addAttr(OO000000O0000O0OO, longName='hairSys', at='float', dv=0, h=0, k=0)
            except:
                pass

            try:
                cmds.connectAttr('%s.hairSys' % OO0O0OOOOO00O000O, '%s.hairSys' % OO000000O0000O0OO)
            except:
                pass

            OO000O00000OOO000 = cmds.listConnections(OOO0OOOO00OOO0O00, s=0, d=1)
            for OO000OOOO0OOOO0O0 in OO000O00000OOO000:
                if cmds.objectType(OO000OOOO0OOOO0O0, isType='nucleus'):
                    O00OOOOO00OO00000 = OO000OOOO0OOOO0O0

            O00OOOOO00OO00000 = cmds.rename(O00OOOOO00OO00000, '%s_nucleus' % O0000OO0O00O00OO0.hairSysName())
            try:
                cmds.addAttr(O00OOOOO00OO00000, longName='hairSysNuc', at='float', dv=0, h=0, k=0)
            except:
                pass

            cmds.select(cl=True)
            O00OO000O000OOO0O = cmds.listRelatives(OO0O0OO00O0O0OOO0, p=True)[0]
            OOOO000O00OOO0O00 = cmds.rename(O00OO000O000OOO0O, '%s_hair_fol' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]))
            try:
                cmds.addAttr(OOOO000O00OOO0O00, longName='hairFol', at='float', dv=0, h=0, k=0)
            except:
                pass

            cmds.connectAttr('%s.hairFol' % OO0O0OOOOO00O000O, '%s.hairFol' % OOOO000O00OOO0O00)
            OO00OO00OO000O0O0 = cmds.listRelatives(OOOO000O00OOO0O00, s=True)[0]
            O0OO0O00OO0O0O000 = cmds.listConnections(OO00OO00OO000O0O0, s=0, d=1)
            for OO000OOOO0OOOO0O0 in O0OO0O00OO0O0O000:
                O000OOO0O00OOO000 = cmds.listRelatives(OO000OOOO0OOOO0O0, s=True)
                if cmds.objectType(O000OOO0O00OOO000, isType='nurbsCurve'):
                    OOOOOO00O00O0O000 = cmds.rename(OO000OOOO0OOOO0O0, '%s_dyn_curve' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]))
                    try:
                        cmds.addAttr(OOOOOO00O00O0O000, longName='dynCurve', at='float', dv=0, h=0, k=0)
                    except:
                        pass

                    cmds.connectAttr('%s.dynCurve' % OO0O0OOOOO00O000O, '%s.dynCurve' % OOOOOO00O00O0O000)

            if OO00O00O0OOOO0O00 == 'noAttach':
                cmds.setAttr('%s.pointLock' % OO00OO00OO000O0O0, 0)
            else:
                if OO00O00O0OOOO0O00 == 'base':
                    cmds.setAttr('%s.pointLock' % OO00OO00OO000O0O0, 1)
                else:
                    if OO00O00O0OOOO0O00 == 'tip':
                        cmds.setAttr('%s.pointLock' % OO00OO00OO000O0O0, 2)
                    else:
                        if OO00O00O0OOOO0O00 == 'bothEnd':
                            cmds.setAttr('%s.pointLock' % OO00OO00OO000O0O0, 3)
                        O00OOOOO0O00O0O00 = cmds.listRelatives(OOOO000O00OOO0O00, p=True)
                        O00OOOOO0O00O0O00 = cmds.rename(O00OOOOO0O00O0O00, '%s_fol_grp' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]))
                        O00O0OOO00O00000O = cmds.listRelatives(OOOOOO00O00O0O000, p=True)
                        O00O0OOO00O00000O = cmds.rename(O00O0OOO00O00000O, '%s_dynCrv_grp' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]))
                        cmds.skinCluster(O0O00OOO0O0O0O0O0, OO0O0OO00O0O0OOO0, tsb=True, n='%s_dynHiar_skinCluster' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]))
                        cmds.select(O0000OO0O00O00OO0.jointEndAndStart(OO00O0OOO000OO0O0, O00000OO0OO0OO0OO, '_dyn_jnt'))
                        O0O000OO000OO0000 = cmds.ls(sl=True)
                        cmds.select(cl=True)
                        for OO000OOOO0OOOO0O0 in O0O000OO000OO0000:
                            try:
                                cmds.addAttr(OO000OOOO0OOOO0O0, longName='dynJnt%d' % (O0O000OO000OO0000.index(OO000OOOO0OOOO0O0) + 1), at='float', dv=0, h=0, k=0)
                            except:
                                pass

                            cmds.connectAttr('%s.dynJoint' % OO0O0OOOOO00O000O, '%s.dynJnt%d' % (OO000OOOO0OOOO0O0, O0O000OO000OO0000.index(OO000OOOO0OOOO0O0) + 1))

                        cmds.select(O0000OO0O00O00OO0.jointEndAndStart(OO00O0OOO000OO0O0, O00000OO0OO0OO0OO, '_bake_jnt'))
                        OOO00O00OOO00OOOO = cmds.ls(sl=True)
                        cmds.select(cl=True)
                        O0000O0OO0O0O0OO0 = []
                        O0O0OO0OO0OO0000O = []
                        for OO000OOOO0OOOO0O0 in OOO00O00OOO00OOOO:
                            OOO0OO00OOO0O0O00 = O0000OO0O00O00OO0.createCtrl('%s_bake_ctrl' % O0000OO0O00O00OO0.getPrexName(OO000OOOO0OOOO0O0), O0000OO0O00O00OO0.getScale() * 0.5, 'bakeCtrl%d' % (OOO00O00OOO00OOOO.index(OO000OOOO0OOOO0O0) + 1))[1]
                            O0000OO0O00O00OO0.getCtrlPos(OO000OOOO0OOOO0O0, OOO0OO00OOO0O0O00)
                            OO00OOOOO0OO0OO0O = cmds.listRelatives(OOO0OO00OOO0O0O00, c=True)
                            cmds.connectAttr('%s.bakeCtrl' % OO0O0OOOOO00O000O, '%s.bakeCtrl%d' % (OO00OOOOO0OO0OO0O[0], OOO00O00OOO00OOOO.index(OO000OOOO0OOOO0O0) + 1))
                            cmds.parentConstraint(OO00OOOOO0OO0OO0O, OO000OOOO0OOOO0O0, mo=True)
                            try:
                                cmds.addAttr(OO000OOOO0OOOO0O0, longName='bakeJnt%d' % (OOO00O00OOO00OOOO.index(OO000OOOO0OOOO0O0) + 1), at='float', dv=0, h=0, k=0)
                            except:
                                pass

                            cmds.connectAttr('%s.bakeJoint' % OO0O0OOOOO00O000O, '%s.bakeJnt%d' % (OO000OOOO0OOOO0O0, OOO00O00OOO00OOOO.index(OO000OOOO0OOOO0O0) + 1))
                            O0000O0OO0O0O0OO0.append(OO00OOOOO0OO0OO0O)
                            O0O0OO0OO0OO0000O.append(OOO0OO00OOO0O0O00)

                        O0000O0OO0O0O0OO0.pop()
                        O0000O0OO0O0O0OO0.reverse()
                        O0O0OO0OO0OO0000O.reverse()
                        for OO000OOOO0OOOO0O0, O00O0OO0O00OO00O0 in zip(O0000O0OO0O0O0OO0, O0O0OO0OO0OO0000O):
                            cmds.parent(O00O0OO0O00OO00O0, OO000OOOO0OOOO0O0)
                            if OO000OOOO0OOOO0O0 == O0000O0OO0O0O0OO0[(-1)]:
                                continue

                        O00OO000OOO0O0OOO = cmds.ikHandle(name='%s_ikSpline' % O0000OO0O00O00OO0.getPrexName(O0O00OOO0O0O0O0O0[0]), sol='ikSplineSolver', sj=O0O000OO000OO0000[0], ee=O0O000OO000OO0000[(-1)], c=OOOOOO00O00O0O000, ccv=False, pcv=False, see=0, fj=1)[0]
                        cmds.addAttr(O00OO000OOO0O0OOO, longName='aniIk', at='float', dv=0, h=0, k=0)
                        cmds.setAttr('%s.ikBlend' % O00OO000OOO0O0OOO, 1)
                        O0OO0O0000O00OOO0 = []
                        O0O0OO00000O00O00 = []
                        OO0O0O000O0O00OOO = []
                        O0O000OOOO0000OO0 = O0000OO0O00O00OO0.createCtrl('%s_ctrl' % O0000OO0O00O00OO0.getPrexName(O00OOO00O0O000OO0), O0000OO0O00O00OO0.getScale(), 'aniCtrl1')[1]
                        O0000OO0O00O00OO0.getCtrlPos(O00OOO00O0O000OO0, O0O000OOOO0000OO0)
                        O00OOOOOO000O00OO = cmds.listRelatives(O0O000OOOO0000OO0, c=True)
                        cmds.connectAttr('%s.drvCtrl' % OO0O0OOOOO00O000O, '%s.aniCtrl1' % O00OOOOOO000O00OO[0])
                        for OO000OOOO0OOOO0O0 in O0O00OOO0O0O0O0O0:
                            if OO000OOOO0OOOO0O0 != O00OOO00O0O000OO0:
                                O000O000O0O0O0000 = O0000OO0O00O00OO0.createCtrl('%s_ctrl' % O0000OO0O00O00OO0.getPrexName(OO000OOOO0OOOO0O0), O0000OO0O00O00OO0.getScale(), 'aniCtrl%d' % (O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0) + 1))[1]
                                O0000OO0O00O00OO0.getCtrlPos(OO000OOOO0OOOO0O0, O000O000O0O0O0000)
                                O00OO0OO00OOOOOO0 = cmds.listRelatives(O000O000O0O0O0000, c=True)
                                cmds.connectAttr('%s.drvCtrl' % OO0O0OOOOO00O000O, '%s.aniCtrl%d' % (O00OO0OO00OOOOOO0[0], O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0) + 1))
                                if O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0) == 1:
                                    cmds.parent(O000O000O0O0O0000, O00OOOOOO000O00OO)
                                OOOOO0000OOO0O00O = cmds.ikHandle(n='%s_ikHandle' % OO000OOOO0OOOO0O0, sj=O0O00OOO0O0O0O0O0[(O0O00OOO0O0O0O0O0.index(OO000OOOO0OOOO0O0) - 1)], ee=OO000OOOO0OOOO0O0)[0]
                                cmds.parentConstraint(O00OO0OO00OOOOOO0, OOOOO0000OOO0O00O, mo=True)
                                if OO000OOOO0OOOO0O0 == O0O00OOO0O0O0O0O0[(-1)]:
                                    pass
                                O0O0OO00000O00O00.append(O000O000O0O0O0000)
                                O0OO0O0000O00OOO0.append(O00OO0OO00OOOOOO0)
                                OO0O0O000O0O00OOO.append(OOOOO0000OOO0O00O)

                        O0OO0O0000O00OOO0.pop()
                        O0OO0O0000O00OOO0.reverse()
                        O0O0OO00000O00O00.reverse()
                        for OO000OOOO0OOOO0O0, O00O0OO0O00OO00O0 in zip(O0OO0O0000O00OOO0, O0O0OO00000O00O00):
                            cmds.parent(O00O0OO0O00OO00O0, OO000OOOO0OOOO0O0)
                            if OO000OOOO0OOOO0O0 == O0OO0O0000O00OOO0[(-1)]:
                                continue

                    cmds.setAttr('%s.ikBlend' % O00OO000OOO0O0OOO, 1)
                    OO00OOOOOOO0OO000 = []
                    O0O00O0O0000O00O0 = []
                    for OO000OOOO0OOOO0O0, O00O0OO0O00OO00O0 in zip(O0O000OO000OO0000, O0O00OOO0O0O0O0O0):
                        O00O0000O0O00OOOO = cmds.spaceLocator(name='%s_bake_loc' % O0000OO0O00O00OO0.getPrexName(OO000OOOO0OOOO0O0), p=(0,
                                                                                                                                        0,
                                                                                                                                        0))
                        OOOOO00OO0O000000 = cmds.group(O00O0000O0O00OOOO, name='%s_bake_loc_grp' % O0000OO0O00O00OO0.getPrexName(OO000OOOO0OOOO0O0))
                        OO00OOOOOOO0OO000.append(O00O0000O0O00OOOO)
                        O0O00O0O0000O00O0.append(OOOOO00OO0O000000)
                        O0000OO0O00O00OO0.getCtrlPos(O00O0OO0O00OO00O0, OOOOO00OO0O000000)
                        cmds.connectAttr('%s.rx' % OO000OOOO0OOOO0O0, '%s.rx' % O00O0000O0O00OOOO[0])
                        cmds.connectAttr('%s.ry' % OO000OOOO0OOOO0O0, '%s.ry' % O00O0000O0O00OOOO[0])
                        cmds.connectAttr('%s.rz' % OO000OOOO0OOOO0O0, '%s.rz' % O00O0000O0O00OOOO[0])
                        cmds.pointConstraint(OO000OOOO0OOOO0O0, OOOOO00OO0O000000, mo=True)
                        try:
                            cmds.addAttr(O00O0000O0O00OOOO, longName='bakeLocator%d' % (O0O000OO000OO0000.index(OO000OOOO0OOOO0O0) + 1), at='float', dv=0, h=0, k=0)
                        except:
                            pass

                        cmds.connectAttr('%s.bakeLoc' % OO0O0OOOOO00O000O, '%s.bakeLocator%d' % (O00O0000O0O00OOOO[0], O0O000OO000OO0000.index(OO000OOOO0OOOO0O0) + 1))

                for OO000OOOO0OOOO0O0, O00O0OO0O00OO00O0, OOOO00O00O0OOO000 in zip(OOO00O00OOO00OOOO, O0O000OO000OO0000, OOOO000OOOOOOOO0O):
                    OOOOOO0000O0OO00O = cmds.orientConstraint(OO000OOOO0OOOO0O0, O00O0OO0O00OO00O0, OOOO00O00O0OOO000, mo=True)[0]
                    O000O0OOOOOOO0OO0 = cmds.pointConstraint(OO000OOOO0OOOO0O0, O00O0OO0O00OO00O0, OOOO00O00O0OOO000, mo=True)[0]
                    cmds.connectAttr('%s.aniCtrlCons' % OO0O0OOOOO00O000O, '%s.%sW0' % (OOOOOO0000O0OO00O, OO000OOOO0OOOO0O0))
                    cmds.connectAttr('%s.aniCtrlCons' % OO0O0OOOOO00O000O, '%s.%sW0' % (O000O0OOOOOOO0OO0, OO000OOOO0OOOO0O0))
                    cmds.connectAttr('%s.drvCtrlCons' % OO0O0OOOOO00O000O, '%s.%sW1' % (OOOOOO0000O0OO00O, O00O0OO0O00OO00O0))
                    cmds.connectAttr('%s.drvCtrlCons' % OO0O0OOOOO00O000O, '%s.%sW1' % (O000O0OOOOOOO0OO0, O00O0OO0O00OO00O0))

            O000000OO00OOO00O = cmds.group(OO0O0O000O0O00OOO, O00OO000OOO0O0OOO, name='%s_ikHandle_all_grp' % O0000OO0O00O00OO0.getPrexName(OO00O0OOO000OO0O0))
            OOOOO00OO0O00O0OO = cmds.group(OO000000O0000O0OO, O00OOOOO0O00O0O00, O00OOOOO00OO00000, O00O0OOO00O00000O, name='%s_dynSys_all_grp' % O0000OO0O00O00OO0.getPrexName(OO00O0OOO000OO0O0))
            O0O00OO00O00OOOO0 = cmds.group(O0O00O0O0000O00O0, name='%s_bakeLoc_all_grp' % O0000OO0O00O00OO0.getPrexName(OO00O0OOO000OO0O0))
            O00O00OOO0OO0OO0O = cmds.group(O0O000OO000OO0000[0], O00OOO00O0O000OO0, OOO00O00OOO00OOOO[0], name='%s_dynSys_jnt_all_grp' % O0000OO0O00O00OO0.getPrexName(OO00O0OOO000OO0O0))
            O0O00O00OO00OOOO0 = cmds.group(O0O000OOOO0000OO0, O0O0OO0OO0OO0000O[(-1)], name='%s_dynSys_ctrl_all_grp' % O0000OO0O00O00OO0.getPrexName(OO00O0OOO000OO0O0))
            O0OOO00O0OOOOOO0O = cmds.group(OOOOO00OO0O00O0OO, O0O00OO00O00OOOO0, O000000OO00OOO00O, name='%s_dyn_misc_grp' % O0000OO0O00O00OO0.getPrexName(OO00O0OOO000OO0O0))
            cmds.connectAttr('%s.bakeCtrlVisb' % OO0O0OOOOO00O000O, '%s.v' % O0O0OO0OO0OO0000O[(-1)])
            cmds.connectAttr('%s.aniCtrlVisb' % OO0O0OOOOO00O000O, '%s.v' % O0O000OOOO0000OO0)
            cmds.setAttr('%s.v' % O0OOO00O0OOOOOO0O, 0)
            cmds.setAttr('%s.v' % O00O00OOO0OO0OO0O, 0)
            cmds.parent(O00O00OOO0OO0OO0O, O0O00O00OO00OOOO0, OO0O0OOOOO00O000O)
            cmds.parent(O0OOO00O0OOOOOO0O, OO000OOOO0OOO00OO)
            OOOOOO000OOO0OO0O.append(OO0O0OOOOO00O000O)
            cmds.select(cl=True)

        OO0O0OOOO0O0OO000 = O0000OO0O00O00OO0.text_curves(O0000OO0O00O00OO0.hairSysName() + 'Ctrl')
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='startFrame', at='float', dv=1, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='simulationMethod', at='enum', en='Off:Static:Dynamic_Follicles_Only:All_Follicles', dv=1, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='startCurveAttract', at='float', min=0, dv=0.5, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='damp', at='float', min=0, dv=0.5, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='spaceScale', at='float', min=0.0001, dv=0.2, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='mass', at='float', min=0, dv=1, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='gravity', at='float', dv=9.8, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='stiffness', at='float', min=0, dv=0.15, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='drag', at='float', min=0, dv=0.05, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='friction', at='float', min=0, dv=0.5, h=0, k=1)
        cmds.addAttr(OO0O0OOOO0O0OO000, longName='dynRootCtrlList', dt='string', h=0, k=0)
        cmds.setAttr(OO0O0OOOO0O0OO000 + '.dynRootCtrlList', OOOOOO000OOO0OO0O, type='string')
        try:
            cmds.connectAttr('%s.startFrame' % OO0O0OOOO0O0OO000, '%s.startFrame' % O00OOOOO00OO00000, force=True)
            cmds.connectAttr('%s.simulationMethod' % OO0O0OOOO0O0OO000, '%s.simulationMethod' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.stiffness' % OO0O0OOOO0O0OO000, '%s.stiffness' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.damp' % OO0O0OOOO0O0OO000, '%s.damp' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.drag' % OO0O0OOOO0O0OO000, '%s.drag' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.friction' % OO0O0OOOO0O0OO000, '%s.friction' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.mass' % OO0O0OOOO0O0OO000, '%s.mass' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.startCurveAttract' % OO0O0OOOO0O0OO000, '%s.startCurveAttract' % OOO0OOOO00OOO0O00, force=True)
            cmds.connectAttr('%s.gravity' % OO0O0OOOO0O0OO000, '%s.gravity' % O00OOOOO00OO00000, force=True)
            cmds.connectAttr('%s.spaceScale' % OO0O0OOOO0O0OO000, '%s.spaceScale' % O00OOOOO00OO00000, force=True)
            O0000OO0O00O00OO0.connectFollicles(OO0O0OOOO0O0OO000)
        except:
            pass

        if cmds.objExists('guanyj_template_nucleus'):
            cmds.rename('guanyj_template_nucleus', 'nucleus1')
        O0000OO0O00O00OO0.getHairSystems()
        O0000OO0O00O00OO0.getHairNucleus()
        O0000OO0O00O00OO0.connectFollicles()

    def getHairSystems(O0OO0O0OOO000O00O):
        O0OO0O0OOO000O00O.hairSys_listWidget.clear()
        O000O0OOO00OOOO00 = cmds.ls(type='nucleus')
        O0000O00O00O0O0OO = cmds.ls(type='hairSystem')
        for OOO0OOOO0OOO0OOOO in O000O0OOO00OOOO00:
            OO0OO00OO0000O00O = cmds.listConnections(OOO0OOOO0OOO0OOOO, destination=True, shapes=True, type='hairSystem')
            if OO0OO00OO0000O00O:
                OO0OO00OO0000O00O = set(OO0OO00OO0000O00O)
                OOOOOOOO0O00OOOO0 = random.randint(0, 100)
                OOO00O00OOOO0O0O0 = random.randint(50, 255)
                OO0O00OOOOOO00O00 = random.randint(0, 255)
                for OOOO0O0O0OO0O0OOO in OO0OO00OO0000O00O:
                    O0000O00O00O0O0OO.remove(OOOO0O0O0OO0O0OOO)
                    O0OO0O0OOO000O00O.simMethodCheckBox(O0OO0O0OOO000O00O.hairSys_listWidget, 'simulationMethod', 3, 1, '%s_cb' % OOOO0O0O0OO0O0OOO, OOOO0O0O0OO0O0OOO, OOOOOOOO0O00OOOO0, OOO00O00OOOO0O0O0, OO0O00OOOOOO00O00)

        O0OO0O0OOO000O00O.hairSys_listWidget.sortItems()
        if O0000O00O00O0O0OO != []:
            OOOOOOOO0O00OOOO0 = 255
            OOO00O00OOOO0O0O0 = 0
            OO0O00OOOOOO00O00 = 0
            for OOOO0O0O0OO0O0OOO in O0000O00O00O0O0OO:
                O0OO0O0OOO000O00O.simMethodCheckBox(O0OO0O0OOO000O00O.hairSys_listWidget, 'simulationMethod', 3, 1, '%s_cb' % OOOO0O0O0OO0O0OOO, OOOO0O0O0OO0O0OOO, OOOOOOOO0O00OOOO0, OOO00O00OOOO0O0O0, OO0O00OOOOOO00O00)

    def simMethodCheckBox(O0O0OOO0000OO0OO0, OOO00O0OOOO0OOO00, OOO00O0000OO000O0, O0O0OOOOOOOO0O000, O0OO00O0O000OOO0O, OOOOOO0O0O000000O, O00OOOO0O0OOOOO0O, OO00OO0OO00O0O00O, O0OO000O0O00OO0OO, OO00O0OO000O0OO00):
        OO0O0O00O0OOOO000 = qw.QListWidgetItem()
        OO0000000OOO00O00 = qg.QBrush(qg.QColor(OO00OO0OO00O0O00O, O0OO000O0O00OO0OO, OO00O0OO000O0OO00, 80))
        OO0000000OOO00O00.setStyle(qc.Qt.SolidPattern)
        OO0O0O00O0OOOO000.setBackground(OO0000000OOO00O00)
        OOOOOO0O0O000000O = qw.QCheckBox()
        OOOOOO0O0O000000O.setFixedWidth(20)
        OOOOO0OOO00OOO0O0 = cmds.getAttr('%s.%s' % (O00OOOO0O0OOOOO0O, OOO00O0000OO000O0))
        if OOOOO0OOO00OOO0O0 == O0O0OOOOOOOO0O000:
            OOOOOO0O0O000000O.setCheckState(qc.Qt.Checked)
        else:
            OOOOOO0O0O000000O.setCheckState(qc.Qt.Unchecked)
        OOO00OOOOOOO0OO0O = cmds.listConnections('%s.%s' % (O00OOOO0O0OOOOO0O, OOO00O0000OO000O0), destination=False)
        O0OOOOO0OO000O0O0 = cmds.getAttr('%s.%s' % (O00OOOO0O0OOOOO0O, OOO00O0000OO000O0), lock=True)
        if OOO00OOOOOOO0OO0O or O0OOOOO0OO000O0O0:
            OOOOOO0O0O000000O.setEnabled(False)
        OO0O0O00O0OOOO000.setText('      %s' % O00OOOO0O0OOOOO0O)
        OOO00O0OOOO0OOO00.addItem(OO0O0O00O0OOOO000)
        OOO00O0OOOO0OOO00.setItemWidget(OO0O0O00O0OOOO000, OOOOOO0O0O000000O)
        OOOOOO0O0O000000O.stateChanged.connect(lambda : O0O0OOO0000OO0OO0.simMethodCheckBoxChange(OOOOOO0O0O000000O, OOO00O0000OO000O0, O0O0OOOOOOOO0O000, O0OO00O0O000OOO0O, O00OOOO0O0OOOOO0O))

    def simMethodCheckBoxChange(OO00O0OOOOO00OOOO, O0000OOOOO0000OOO, O00000O0OOOOO00O0, OO0O0OO000000000O, O00O0OOOO0OOOO0O0, O0OO0OO0O0O000OOO):
        O000000O0O00000O0 = O0000OOOOO0000OOO.isChecked()
        if O000000O0O00000O0:
            cmds.setAttr('%s.%s' % (O0OO0OO0O0O000OOO, O00000O0OOOOO00O0), OO0O0OO000000000O)
        else:
            cmds.setAttr('%s.%s' % (O0OO0OO0O0O000OOO, O00000O0OOOOO00O0), O00O0OOOO0OOOO0O0)

    def currentHairSystem(O0OO00OOO00O0OO0O):
        OO0O0O0OO00OOOO0O = O0OO00OOO00O0OO0O.hairSys_listWidget.selectedItems()
        cmds.select(clear=True)
        for OO0O0000OO0OOO000 in OO0O0O0OO00OOOO0O:
            cmds.select('%s' % OO0O0000OO0OOO000.text(), add=True)

        O0OO00OOO00O0OO0O.nucleus_listWidget.clearSelection()

    def getHairNucleus(OOO0OO00OOO00O0O0):
        OOO0OO00OOO00O0O0.nucleus_listWidget.clear()
        O000O00OO0O0O0O0O = cmds.ls(type='nucleus')
        OOOO00O0O0O0O00O0 = O0O0O00OOOOO00O0O = OO0OO0000OO000O00 = 43
        for O0000000OOO0OO0O0 in O000O00OO0O0O0O0O:
            OOO0OO00OOO00O0O0.simMethodCheckBox(OOO0OO00OOO00O0O0.nucleus_listWidget, 'enable', 1, 0, '%s_cb' % O0000000OOO0OO0O0, O0000000OOO0OO0O0, OOOO00O0O0O0O00O0, O0O0O00OOOOO00O0O, OO0OO0000OO000O00)

    def currentHairNucleus(OO0OO00OOO0O0OO0O):
        O0O0O0OO00OOO0O0O = OO0OO00OOO0O0OO0O.nucleus_listWidget.selectedItems()
        cmds.select(clear=True)
        for O0000OOOO0OOO0OO0 in O0O0O0OO00OOO0O0O:
            cmds.select('%s' % O0000OOOO0OOO0OO0.text(), add=True)

        OO0OO00OOO0O0OO0O.hairSys_listWidget.clearSelection()

    def addNucleus(OOO0000O0O00O0OO0):
        OO0O000O00O0O00OO = OOO0000O0O00O0OO0.hairSys_listWidget.selectedItems()
        cmds.select(clear=True)
        cmds.select('%s' % OO0O000O00O0O00OO[0].text())
        if cmds.listConnections(OO0O000O00O0O00OO[0].text(), type='nucleus') is None:
            try:
                OOOOOO0O00000000O = 'assignNSolver "";'
                mm.eval(OOOOOO0O00000000O)
            except:
                pass

            OO0O0O0O0O00O0O00 = cmds.rename(cmds.ls(sl=1)[0], OO0O000O00O0O00OO[0].text()[:-5] + '_nucleus')
            OO000OO0OOOOO0000 = cmds.listRelatives(OO0O000O00O0O00OO[0].text(), parent=True)
            cmds.parent(OO0O0O0O0O00O0O00, cmds.listRelatives(OO000OO0OOOOO0000[0], parent=True, fullPath=True))
            try:
                cmds.connectAttr('%sCtrl.startFrame' % OO0O000O00O0O00OO[0].text()[:-5], '%s.startFrame' % OO0O0O0O0O00O0O00)
                cmds.connectAttr('%sCtrl.gravity' % OO0O000O00O0O00OO[0].text()[:-5], '%s.gravity' % OO0O0O0O0O00O0O00)
                cmds.connectAttr('%sCtrl.spaceScale' % OO0O000O00O0O00OO[0].text()[:-5], '%s.spaceScale' % OO0O0O0O0O00O0O00)
            except:
                cmds.warning('Can not find %sCtrl' % OO0O000O00O0O00OO[0].text()[:-5])

            if len(OO0O000O00O0O00OO) >= 2:
                OO0000O00000000OO = 'assignNSolver "%s";' % OO0O0O0O0O00O0O00
                for O000OOO00O0OOO00O in OO0O000O00O0O00OO[1:]:
                    cmds.select('%s' % O000OOO00O0OOO00O.text())
                    if cmds.listConnections(O000OOO00O0OOO00O.text(), type='nucleus') is None:
                        try:
                            mm.eval(OO0000O00000000OO)
                        except:
                            pass

                    else:
                        cmds.warning('%s has nucleus, please check!!!' % O000OOO00O0OOO00O.text())

        else:
            cmds.warning('%s has nucleus, please check!!!' % OO0O000O00O0O00OO[0].text())
        OOO0000O0O00O0OO0.getHairSystems()
        OOO0000O0O00O0OO0.getHairNucleus()
        return

    def delNucleus(O0O0O0O0O0OOOOO0O):
        O0O0O0OOO0OOO0O00 = O0O0O0O0O0OOOOO0O.hairSys_listWidget.selectedItems()
        cmds.select(clear=True)
        O0O0OO0OOOO00000O = []
        for OO00OO0OO00OOO0OO in O0O0O0OOO0OOO0O00:
            OO00000OO0000O000 = cmds.listConnections('%s' % OO00OO0OO00OOO0OO.text(), type='nucleus')
            try:
                O0O0OO0OOOO00000O += OO00000OO0000O000
            except:
                cmds.warning('The nucleus of %s cannot found!' % OO00OO0OO00OOO0OO.text())

        cmds.delete([ OO0OO0OO0000O0O0O for OO0OO0OO0000O0O0O in set(O0O0OO0OOOO00000O) ])
        O0O0O0O0O0OOOOO0O.getHairSystems()
        O0O0O0O0O0OOOOO0O.getHairNucleus()

    def bake(OOOOO0OOO0OO0OO0O):
        OOOO0OO00OOOOOOO0 = cmds.playbackOptions(query=True, min=True)
        OOOO000OOO0OO0OOO = cmds.playbackOptions(query=True, max=True)
        OOO000O00O00OOOOO = []
        O0O0OOO0OOOOO0O00 = []
        O0000O000OO0OOO0O = cmds.ls(sl=True)
        for OOOO000OOO0O0OOOO in O0000O000OO0OOO0O:
            OO0000O0O00O0O000 = cmds.getAttr('%s.dynRootCtrlList' % OOOO000OOO0O0OOOO)
            OO0000O0O00O0O000 = OO0000O0O00O0O000[3:][:-2]
            O0000000OOOO00000 = OO0000O0O00O0O000.split("', u'")
            for O00OO0OOOOO00OO0O in O0000000OOOO00000:
                if OOOO000OOO0O0OOOO.find(':') != -1:
                    OO0O00OO00OOO00OO = OOOO000OOO0O0OOOO.rsplit(':', 1)[0]
                    O00OO0OOOOO00OO0O = '%s:%s' % (OO0O00OO00OOO00OO, O00OO0OOOOO00OO0O)
                cmds.setAttr('%s.simulationMethod' % OOOO000OOO0O0OOOO, 3)
                OOO0O0O0OOO00O0OO = cmds.getAttr('%s.drvCtrlCons' % O00OO0OOOOO00OO0O)
                if OOO0O0O0OOO00O0OO == 1:
                    OO0000000OOOOOO00 = cmds.listConnections('%s.bakeLoc' % O00OO0OOOOO00OO0O)
                    for OOO0OO0OO0OO0O00O in OO0000000OOOOOO00:
                        OOO000O00O00OOOOO.append(OOO0OO0OO0OO0O00O)

                    O0OO0O00O0O00OO0O = cmds.listConnections('%s.bakeCtrl' % O00OO0OOOOO00OO0O)
                    for O0O000OO0OOOO00OO in O0OO0O00O0O00OO0O:
                        O0O0OOO0OOOOO0O00.append(O0O000OO0OOOO00OO)

        if OOO000O00O00OOOOO != []:
            cmds.bakeResults(OOO000O00O00OOOOO, simulation=True, t=(OOOO0OO00OOOOOOO0, OOOO000OOO0OO0OOO), sampleBy=1, disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False, removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, minimizeRotation=True, at=('rx',
                                                                                                                                                                                                                                                                                                    'ry',
                                                                                                                                                                                                                                                                                                    'rz'))
        for O00OO0OOOOO00OO0O, OOO0OO0OO0OO0O00O in zip(OOO000O00O00OOOOO, O0O0OOO0OOOOO0O00):
            cmds.copyKey(O00OO0OOOOO00OO0O, time=(OOOO0OO00OOOOOOO0, OOOO000OOO0OO0OOO), at=('rx',
                                                                                             'ry',
                                                                                             'rz'), option='curve')
            cmds.pasteKey(OOO0OO0OO0OO0O00O, option='replaceCompletely', at=('rx',
                                                                             'ry',
                                                                             'rz'))

        for OOOO000OOO0O0OOOO in O0000O000OO0OOO0O:
            OO0000O0O00O0O000 = cmds.getAttr('%s.dynRootCtrlList' % OOOO000OOO0O0OOOO)
            OO0000O0O00O0O000 = OO0000O0O00O0O000[3:][:-2]
            O0000000OOOO00000 = OO0000O0O00O0O000.split("', u'")
            for O00OO0OOOOO00OO0O in O0000000OOOO00000:
                if OOOO000OOO0O0OOOO.find(':') != -1:
                    OO0O00OO00OOO00OO = OOOO000OOO0O0OOOO.rsplit(':', 1)[0]
                    O00OO0OOOOO00OO0O = '%s:%s' % (OO0O00OO00OOO00OO, O00OO0OOOOO00OO0O)
                cmds.setAttr('%s.bakeCtrlVisb' % O00OO0OOOOO00OO0O, 1)
                cmds.setAttr('%s.aniCtrlVisb' % O00OO0OOOOO00OO0O, 0)
                cmds.setAttr('%s.drvCtrlCons' % O00OO0OOOOO00OO0O, 0)
                cmds.setAttr('%s.aniCtrlCons' % O00OO0OOOOO00OO0O, 1)
                cmds.setAttr('%s.simulationMethod' % OOOO000OOO0O0OOOO, 1)

    def unDoBake(OO00OO00OOO00O00O):
        O0O0OO0OOOO000O0O = []
        OOO0OO0OO00OOOOO0 = []
        O0O0O0OO0O0OOOOO0 = cmds.ls(sl=True)
        for OOOOO0OOO0000OOOO in O0O0O0OO0O0OOOOO0:
            O0OO00O0O0O0OO000 = cmds.getAttr('%s.dynRootCtrlList' % OOOOO0OOO0000OOOO)
            O0OO00O0O0O0OO000 = O0OO00O0O0O0OO000[3:][:-2]
            O00000OO00OOO0O00 = O0OO00O0O0O0OO000.split("', u'")
            for O0OO00OOOO0O00OO0 in O00000OO00OOO0O00:
                if OOOOO0OOO0000OOOO.find(':') != -1:
                    OOO00O000O00O0000 = OOOOO0OOO0000OOOO.rsplit(':', 1)[0]
                    O0OO00OOOO0O00OO0 = '%s:%s' % (OOO00O000O00O0000, O0OO00OOOO0O00OO0)
                O0OOOO00O0O00OO00 = cmds.getAttr('%s.drvCtrlCons' % O0OO00OOOO0O00OO0)
                if O0OOOO00O0O00OO00 == 0:
                    O0O000000O0OO0OO0 = cmds.listConnections('%s.bakeLoc' % O0OO00OOOO0O00OO0)
                    for OOOO0O00O0OOOO0OO in O0O000000O0OO0OO0:
                        O0O0OO0OOOO000O0O.append(OOOO0O00O0OOOO0OO)

                    O000OOO00OO0000OO = cmds.listConnections('%s.dynJoint' % O0OO00OOOO0O00OO0)
                    for O0O0O000OO0OOOOO0 in O000OOO00OO0000OO:
                        OOO0OO0OO00OOOOO0.append(O0O0O000OO0OOOOO0)

        for O0OO00OOOO0O00OO0, OOOO0O00O0OOOO0OO in zip(OOO0OO0OO00OOOOO0, O0O0OO0OOOO000O0O):
            OO0O00OO0O000OOOO = cmds.listConnections(OOOO0O00O0OOOO0OO, s=1, type='animCurveTA')
            cmds.delete(OO0O00OO0O000OOOO)
            OO00OO00OOO00O00O.getCtrlPos(O0OO00OOOO0O00OO0, OOOO0O00O0OOOO0OO)
            cmds.setAttr('%s.tx' % OOOO0O00O0OOOO0OO, 0)
            cmds.setAttr('%s.ty' % OOOO0O00O0OOOO0OO, 0)
            cmds.setAttr('%s.tz' % OOOO0O00O0OOOO0OO, 0)
            cmds.connectAttr('%s.rx' % O0OO00OOOO0O00OO0, '%s.rx' % OOOO0O00O0OOOO0OO)
            cmds.connectAttr('%s.ry' % O0OO00OOOO0O00OO0, '%s.ry' % OOOO0O00O0OOOO0OO)
            cmds.connectAttr('%s.rz' % O0OO00OOOO0O00OO0, '%s.rz' % OOOO0O00O0OOOO0OO)

        for OOOOO0OOO0000OOOO in O0O0O0OO0O0OOOOO0:
            O0OO00O0O0O0OO000 = cmds.getAttr('%s.dynRootCtrlList' % OOOOO0OOO0000OOOO)
            O0OO00O0O0O0OO000 = O0OO00O0O0O0OO000[3:][:-2]
            O00000OO00OOO0O00 = O0OO00O0O0O0OO000.split("', u'")
            for O0OO00OOOO0O00OO0 in O00000OO00OOO0O00:
                if OOOOO0OOO0000OOOO.find(':') != -1:
                    OOO00O000O00O0000 = OOOOO0OOO0000OOOO.rsplit(':', 1)[0]
                    O0OO00OOOO0O00OO0 = '%s:%s' % (OOO00O000O00O0000, O0OO00OOOO0O00OO0)
                cmds.setAttr('%s.bakeCtrlVisb' % O0OO00OOOO0O00OO0, 0)
                cmds.setAttr('%s.aniCtrlVisb' % O0OO00OOOO0O00OO0, 1)
                cmds.setAttr('%s.drvCtrlCons' % O0OO00OOOO0O00OO0, 1)
                cmds.setAttr('%s.aniCtrlCons' % O0OO00OOOO0O00OO0, 0)
                cmds.setAttr('%s.simulationMethod' % OOOOO0OOO0000OOOO, 3)

    def text_curves(O0OOO0O000OO0OOO0, OOO00OO000OOOOOOO):
        OOO0OOO000OO0O000 = cmds.textCurves(ch=False, f='Segoe UI|sz:200|sl:n|st:100', t=OOO00OO000OOOOOOO)
        cmds.select(OOO0OOO000OO0O000[0], hi=True)
        cmds.select(cmds.ls(sl=True, type='nurbsCurve'))
        cmds.pickWalk(d='up')
        cmds.parent(w=True)
        cmds.makeIdentity(apply=True, t=True, r=True, s=True, n=0, pn=1)
        O0OO00O000OOOO0O0 = cmds.ls(sl=True)
        cmds.select(O0OO00O000OOOO0O0[1:])
        cmds.pickWalk(d='down')
        cmds.select(O0OO00O000OOOO0O0[0], tgl=1)
        cmds.parent(r=True, s=True)
        cmds.delete(O0OO00O000OOOO0O0[1:], OOO0OOO000OO0O000[0])
        O00O0OO00OOO000O0 = cmds.rename(O0OO00O000OOOO0O0[0], OOO00OO000OOOOOOO)
        return O00O0OO00OOO000O0

    def collideProc(O00OO0OOO0O00O00O):
        O0OOOO0O0OOOOOOOO = O00OO0OOO0O00O00O.ui.collideHairSysComboBox.currentIndex()
        O0000OOO0O0O0OOOO = str(O00OO0OOO0O00O00O.ui.collideHairSysComboBox.itemText(O0OOOO0O0OOOOOOOO)) + '_nucleus'
        if cmds.objExists(O0000OOO0O0O0OOOO):
            OO00OOO0O0O00OO00 = cmds.ls(sl=True)
            for OO00000OOO0O000O0 in OO00OOO0O0O00OO00:
                OOO00O0O0O0OO00O0 = cmds.listRelatives(OO00000OOO0O000O0, s=True)[0]
                if OO00000OOO0O000O0.find(':') == -1:
                    O00O000O0O0O00OO0 = OO00000OOO0O000O0
                else:
                    O00O000O0O0O00OO0 = OO00000OOO0O000O0.split(':')[(-1)]
                if cmds.objectType(OOO00O0O0O0OO00O0, isType='mesh'):
                    cmds.select(OO00000OOO0O000O0, O0000OOO0O0O0OOOO)
                    mm.eval('makePassiveCollider;')
                    mm.eval('assignNSolver"' + O0000OOO0O0O0OOOO + '"')
                    OOO00O0O0O000OOOO = cmds.ls(sl=True)
                    O0O000OOOOOOO0OO0 = cmds.listRelatives(OOO00O0O0O000OOOO, p=True)
                    O0O000OOOOOOO0OO0 = cmds.rename(O0O000OOOOOOO0OO0, '%s_%s_nRigid_mesh' % (O0000OOO0O0O0OOOO, O00O000O0O0O00OO0))

    def delCollide(OO000O0000OOO00OO):
        O00O0OO00O00OO0OO = cmds.ls(sl=True)
        OOOOO00OO0OOOO0OO = OO000O0000OOO00OO.ui.collideHairSysComboBox.currentIndex()
        O0000O0O0OOOOO000 = str(OO000O0000OOO00OO.ui.collideHairSysComboBox.itemText(OOOOO00OO0OOOO0OO)) + '_nucleus'
        OO0OOOOOOO0O00O00 = set(cmds.listConnections(O0000O0O0OOOOO000, t='nRigid'))
        for OOOOOO00O00000O00 in OO0OOOOOOO0O00O00:
            if O00O0OO00O00OO0OO != []:
                for OO00000O0OO000O00 in O00O0OO00O00OO0OO:
                    if OO00000O0OO000O00.find(':') == -1:
                        O000OO00000O0O0O0 = OO00000O0OO000O00
                    else:
                        O000OO00000O0O0O0 = OO00000O0OO000O00.split(':')[(-1)]
                    O0OO0O000OOOOOOO0 = '%s_%s_nRigid_mesh' % (O0000O0O0OOOOO000, O000OO00000O0O0O0)
                    try:
                        cmds.delete(O0OO0O000OOOOOOO0)
                    except:
                        print 'There are no objects match name %s.\n' % O0OO0O000OOOOOOO0

            else:
                cmds.delete(OOOOOO00O00000O00)

    def changeSys(O0OOO0OOO0OO000O0):
        if O0OOO0OOO0OO000O0.hairSysName() != '':
            O0O0O0O00O0OOO000 = O0OOO0OOO0OO000O0.hairSysName()
        OO0O0000OOOO0OOO0 = cmds.ls(sl=True)
        OOO0O0O00000O00OO = O0OOO0OOO0OO000O0.ui.hairSysChangeComboBox.currentIndex()
        O0O0000O00000OO00 = str(O0OOO0OOO0OO000O0.ui.hairSysChangeComboBox.itemText(OOO0O0O00000O00OO))
        OO00OO0O00OO0OO00 = str(O0OOO0OOO0OO000O0.ui.hairSysChangeComboBox.itemText(OOO0O0O00000O00OO)) + 'Shape'
        if OO0O0000OOOO0OOO0 != []:
            for O00OO00OOO00O0O00 in OO0O0000OOOO0OOO0:
                OOOO0O0O0O00OOO00 = O00OO00OOO00O0O00.split('_dyn_root_ctrl')[0]
                OO0O0O00O00O00OOO = '%s_hair_fol' % OOOO0O0O0O00OOO00
                OO0OO00O00OOOO0O0 = cmds.listRelatives(OO0O0O00O00O00OOO, p=True)[0]
                OOO00O000O00O0OO0 = '%s_dyn_curve' % OOOO0O0O0O00OOO00
                O0O0000OO0O0OO00O = cmds.listRelatives(OOO00O000O00O0OO0, p=True)[0]
                cmds.select(OO0O0O00O00O00OOO)
                OOOO0O00OOO0O0OOO = 'assignHairSystem %s' % OO00OO0O00OO0OO00
                mm.eval(OOOO0O00OOO0O0OOO)
                if cmds.listRelatives(OOO00O000O00O0OO0, p=True)[0] != O0O0000OO0O0OO00O:
                    cmds.parent(OOO00O000O00O0OO0, O0O0000OO0O0OO00O)
                if cmds.listRelatives(OO0O0O00O00O00OOO, p=True)[0] != OO0OO00O00OOOO0O0:
                    cmds.parent(OO0O0O00O00O00OOO, OO0OO00O00OOOO0O0)
                OOO0O00OOOO00OOO0 = O0O0000O00000OO00 + 'Follicles'
                OOOOOO00OOOO0OOOO = cmds.listRelatives(OOO0O00OOOO00OOO0, c=True)
                OO0O0O0OO0OOO00O0 = O0O0000O00000OO00 + 'OutputCurves'
                OOOO00OOOOO0OOOOO = cmds.listRelatives(OO0O0O0OO0OOO00O0, c=True)
                if OOOOOO00OOOO0OOOO == None:
                    cmds.delete(OOO0O00OOOO00OOO0)
                if OOOO00OOOOO0OOOOO == None:
                    cmds.delete(OO0O0O0OO0OOO00O0)
                cmds.select(cl=1)

        return

    def getJntPos(O0OOO00OO000O00O0, O0000O00000OO0OOO, O0OOOOO0OO00O0OOO):
        if cmds.objExists(O0000O00000OO0OOO):
            O00OO0OOOOOO0O00O = cmds.xform(O0000O00000OO0OOO, q=1, t=1, ws=1)
            O0O00O0OO000000O0 = cmds.xform(O0000O00000OO0OOO, q=1, ro=1, ws=1)
            if not cmds.objExists(O0OOOOO0OO00O0OOO):
                O0O00O0OO00OO0OOO = cmds.joint(n=O0OOOOO0OO00O0OOO, p=(0, 0, 0))
                cmds.xform(O0OOOOO0OO00O0OOO, t=(O00OO0OOOOOO0O00O[0], O00OO0OOOOOO0O00O[1], O00OO0OOOOOO0O00O[2]), ro=(O0O00O0OO000000O0[0], O0O00O0OO000000O0[1], O0O00O0OO000000O0[2]))
                cmds.makeIdentity(O0O00O0OO00OO0OOO, apply=True, t=1, r=1, s=1, n=0, pn=1)
                return O0O00O0OO00OO0OOO

    def jointEndAndStart(O000O0OOOO00OO00O, OO00O0O000OOOO0O0, OO00000O0000O000O, O0O00OO0O000OO0O0):
        O0OO0OOO000000OOO = []
        if cmds.objectType(OO00O0O000OOOO0O0, isType='joint') == True and cmds.objectType(OO00000O0000O000O, isType='joint') == True:
            cmds.select(OO00O0O000OOOO0O0, hi=1)
            O00O00OOO00O00OO0 = cmds.ls(sl=True)
            cmds.select(cl=True)
            for OO0OO0OOOOO0OOOOO in O00O00OOO00O00OO0:
                O0OO0OOO000000OOO.append(O000O0OOOO00OO00O.getJntPos(OO0OO0OOOOO0OOOOO, '%s%s' % (O000O0OOOO00OO00O.getPrexName(OO0OO0OOOOO0OOOOO), O0O00OO0O000OO0O0)))
                cmds.select(cl=True)
                if OO0OO0OOOOO0OOOOO == OO00000O0000O000O:
                    break

        else:
            print 'Please select two joint objects.\n'
        for OOO0O0O00OOO00O00 in O0OO0OOO000000OOO:
            if OOO0O0O00OOO00O00 != O0OO0OOO000000OOO[0]:
                cmds.parent(OOO0O0O00OOO00O00, O0OO0OOO000000OOO[(O0OO0OOO000000OOO.index(OOO0O0O00OOO00O00) - 1)])
                if OOO0O0O00OOO00O00 == O0OO0OOO000000OOO[(-1)]:
                    break

        return O0OO0OOO000000OOO

    def createCtrl(O0O0O0O0O0O00OO00, OOO000OO0OOO00000, O0OOOOO0O0OO00OO0, O0OO00000OO00O00O):
        OO00OO000OO00O0O0 = cmds.curve(name=OOO000OO0OOO00000, d=1, p=[(-1, 1, -1), (1, 1, -1), (1, 1, 1), (-1, 1, 1), (-1, -1, 1), (-1, -1, -1), (-1, 1, -1), (-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (1, 1, -1), (1, -1, -1), (1, -1, 1), (1, -1, -1), (-1, -1, -1)], k=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        O000000O0OO0O0OO0 = cmds.group(OO00OO000OO00O0O0, n='%s_grp' % OOO000OO0OOO00000)
        cmds.setAttr('%s.scaleX' % O000000O0OO0O0OO0, O0OOOOO0O0OO00OO0)
        cmds.setAttr('%s.scaleY' % O000000O0OO0O0OO0, O0OOOOO0O0OO00OO0)
        cmds.setAttr('%s.scaleZ' % O000000O0OO0O0OO0, O0OOOOO0O0OO00OO0)
        cmds.makeIdentity(O000000O0OO0O0OO0, apply=True, t=0, r=0, s=1, n=0, pn=1)
        cmds.addAttr(OO00OO000OO00O0O0, longName=O0OO00000OO00O00O, at='float', dv=0, h=0, k=0)
        O000OO0OOOOOOOO0O = [OO00OO000OO00O0O0, O000000O0OO0O0OO0]
        return O000OO0OOOOOOOO0O

    def getCtrlPos(OO000OO0O00OOO0O0, OO0O00000O0OO0O0O, OO0O0O0O000000000):
        if cmds.objExists(OO0O00000O0OO0O0O):
            O00O0OO00OOO000OO = cmds.xform(OO0O00000O0OO0O0O, q=1, t=1, ws=1)
            O0OO0OOO00OOO0OO0 = cmds.xform(OO0O00000O0OO0O0O, q=1, ro=1, ws=1)
        cmds.xform(OO0O0O0O000000000, t=(O00O0OO00OOO000OO[0], O00O0OO00OOO000OO[1], O00O0OO00OOO000OO[2]), ro=(O0OO0OOO00OOO0OO0[0], O0OO0OOO00OOO0OO0[1], O0OO0OOO00OOO0OO0[2]))

    def getPrexName(OOO000000000OOOO0, OO00O00OO0OO000OO):
        if OO00O00OO0OO000OO.partition(':') > 2:
            O000OO0O00OO00O0O = OO00O00OO0OO000OO.split(':')[(-1)]
        else:
            O000OO0O00OO00O0O = OO00O00OO0OO000OO
        return O000OO0O00OO00O0O

    def hairSysName(O0O0O000000OOOO0O):
        if str(O0O0O000000OOOO0O.name_line.text()) != '':
            O00O000OOOOOOOOO0 = str(O0O0O000000OOOO0O.name_line.text()) + '_Dyn'
        else:
            O00O000OOOOOOOOO0 = 'DefaultName'
        return O00O000OOOOOOOOO0

    def hairSysList(O0000000OO0O00O0O):
        O0OO00000O00O0000 = []
        O00000OOO000OO000 = cmds.ls(type='hairSystem')
        for O00OO0OOOOOO0OO00 in O00000OOO000OO000:
            O0OO00000O00O0000.append(O00OO0OOOOOO0OO00.split('Shape')[0])

        return O0OO00000O00O0000

    def allPrexName(OOO0O000O00OO0OOO):
        OOOO000O00O0OO0O0 = OOO0O000O00OO0OOO.name_line.text()
        return OOOO000O00O0OO0O0

    def refreshHairSysList(OO0OO0O0OOOOOO00O):
        O0O0000O0O0O0O0O0 = OO0OO0O0OOOOOO00O.ui.hairSysComboBox.currentIndex()
        if str(OO0OO0O0OOOOOO00O.ui.hairSysComboBox.itemText(O0O0000O0O0O0O0O0)) == '':
            OO0OO0O0OOOOOO00O.ui.hairSysComboBox.clear()
            OO0OO0O0OOOOOO00O.ui.hairSysComboBox.addItems(OO0OO0O0OOOOOO00O.hairSysList())
        else:
            OO0OO0O0OOOOOO00O.ui.hairSysComboBox.clear()
            OO0OO0O0OOOOOO00O.ui.hairSysComboBox.addItems(OO0OO0O0OOOOOO00O.hairSysList())
            OO0OO0O0OOOOOO00O.ui.hairSysComboBox.setCurrentIndex(O0O0000O0O0O0O0O0)
        OO0000OO0O0OO0O00 = OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.currentIndex()
        if str(OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.itemText(O0O0000O0O0O0O0O0)) == '':
            OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.clear()
            OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.addItems(OO0OO0O0OOOOOO00O.hairSysList())
        else:
            OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.clear()
            OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.addItems(OO0OO0O0OOOOOO00O.hairSysList())
            OO0OO0O0OOOOOO00O.ui.hairSysChangeComboBox.setCurrentIndex(OO0000OO0O0OO0O00)
        OO0OO0O0OOOOOO00O.ui.collideHairSysComboBox.clear()
        OO0OO0O0OOOOOO00O.ui.collideHairSysComboBox.addItems(OO0OO0O0OOOOOO00O.hairSysList())

    def getScale(O0000OOO0O0O000O0):
        OO0O0OO00O0OOOOO0 = 2
        return OO0O0OO00O0OOOOO0

    def signelOfRadioF(OO00O000OOOO0O00O):
        OO00O000OOOO0O00O.ui.startDoubleSpinBox.setEnabled(False)
        OO00O000OOOO0O00O.ui.endDoubleSpinBox.setEnabled(False)

    def signelOfRadioT(OOOO00OOO00OO0000):
        OOOO00OOO00OO0000.ui.startDoubleSpinBox.setEnabled(True)
        OOOO00OOO00OO0000.ui.endDoubleSpinBox.setEnabled(True)

    def startFrame(OOOO000O000O0OO0O):
        if OOOO000O000O0OO0O.ui.timeSliderRadioButton.isChecked():
            OO0OO0O00O000O0OO = cmds.playbackOptions(q=1, min=1)
        elif OOOO000O000O0OO0O.ui.startEndRadioButton.isChecked():
            OO0OO0O00O000O0OO = OOOO000O000O0OO0O.ui.startDoubleSpinBox.value()
        return int(OO0OO0O00O000O0OO)

    def endFrame(OOOOO000000000000):
        if OOOOO000000000000.ui.timeSliderRadioButton.isChecked():
            OOOO0000O0O00O00O = cmds.playbackOptions(q=1, max=1)
        elif OOOOO000000000000.ui.startEndRadioButton.isChecked():
            OOOO0000O0O00O00O = OOOOO000000000000.ui.endDoubleSpinBox.value()
        return int(OOOO0000O0O00O00O)

    def connectFollicles(OOO0OO000OOOO0O00, OO0O0O00OOOOO00O0):
        O0OOOO0000OO000O0 = list(set(cmds.listConnections(OO0O0O00OOOOO00O0, shapes=1, type='hairSystem')))[0]
        OO00O0OOO0OO00O0O = list(set(cmds.listConnections(O0OOOO0000OO000O0, shapes=1, type='follicle')))
        for O00O0OO000O00000O in OO00O0OOO0OO00O0O:
            OO00O000OOO0O0OO0 = cmds.createNode('addDoubleLinear', name='%s_addDL' % O00O0OO000O00000O)
            cmds.setAttr('%s.input2' % OO00O000OOO0O0OO0, -1)
            cmds.connectAttr('%s.simulationMethod' % OO0O0O00OOOOO00O0, '%s.input1' % OO00O000OOO0O0OO0, force=1)
            cmds.connectAttr('%s.output' % OO00O000OOO0O0OO0, '%s.simulationMethod' % O00O0OO000O00000O, force=1)


def main():
    try:
        OO000O0000OOO0OOO = qw.QApplication(sys.argv)
    except RuntimeError:
        OO000O0000OOO0OOO = qc.QCoreApplication.instance()

    OOO0O00O0O00OO0O0 = DynJointToolWidget(parent=getMayaWindow())
    OOO0O00O0O00OO0O0.show()
    sys.exit()


if __name__ == '__main__':
    main()