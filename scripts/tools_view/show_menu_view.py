#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import maya.cmds as cmds
import os

import maya.mel as mel
from PySide2 import QtWidgets, QtGui

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_view', '')


def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(u"UDIM贴图显示", menu)
    # action_a.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_a.triggered.connect(command_a)

    # action_b = QtWidgets.QAction(u"修复渲染层")
    # action_b.triggered.connect(command_b)

    action_c = QtWidgets.QAction(u"只显示模型和曲线", menu)
    action_c.triggered.connect(command_setModelPanelOptions)

    menu.addAction(action_a)
    # menu.addAction(action_b)
    menu.addAction(action_c)

    menu.exec_(QtGui.QCursor.pos())


def command_a():
    mel.eval("string $sel[] = `ls -type file`;for ($a in $sel){generateUvTilePreview $a;}")


def command_setModelPanelOptions():
    currentPanel = cmds.getPanel(withFocus=True)
    currentPanelType = cmds.getPanel(typeOf=currentPanel)

    if currentPanelType in ['modelPanel']:
        cmds.modelEditor(currentPanel, edit=True, allObjects=False)
        cmds.modelEditor(currentPanel, edit=True, polymeshes=True)
        cmds.modelEditor(currentPanel, edit=True, nurbsSurfaces=True)
        cmds.modelEditor(currentPanel, edit=True, nurbsCurves=True)
    # for i in ['-controllers', '-cv', '-hulls', '-subdivSurfaces', '-planes', '-lights', '-cameras', '-imagePlane',
    #           '-joints', '-ikHandles', '-deformers', '-dynamics', '-particleInstancers', '-fluids', '-hairSystems',
    #           '-follicles', '-nCloths', '-nParticles', '-nRigids', '-dynamicConstraints', '-locators', '-dimensions',
    #           '-pivots', '-handles', '-textures', '-strokes', '-motionTrails', '-pluginShapes', '-clipGhosts',
    #           '-greasePencils', '-pluginObjects']:
    #     try:
    #         mel.eval("modelEditor -e %s false modelPanel4;" % i)
    #     except:
    #         pass
    # for n in ['-nurbsCurves', '-polymeshes', '-nurbsSurfaces']:
    #     try:
    #         mel.eval("modelEditor -e %s true modelPanel4;" % n)
    #     except:
    #         pass

