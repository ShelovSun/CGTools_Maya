#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import os, maya.cmds as cmds
from PySide2 import  QtWidgets, QtGui
scriptsPath=os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/mod', '')

def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)),"Mod Publish",menu)
    # action_a.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_a.triggered.connect(command_a)

    action_d = QtWidgets.QAction("Scene Publish",menu)
    action_d.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_d.triggered.connect(command_d)

    action_b = QtWidgets.QAction("Material Manager",menu)
    action_b.triggered.connect(command_b)

    action_c = QtWidgets.QAction("braid Maker",menu)
    action_c.triggered.connect(command_c)

    menu.addAction(action_a)
    menu.addAction(action_d)
    menu.addAction(action_b)
    menu.addAction(action_c)

    menu.exec_(QtGui.QCursor.pos())

def command_a():
    import Mod_Publish_Tool.modPublishTool as MP
    MP.showWindow()
def command_b():
    import DW_MaterialManager.UI as UI
    UI.UI()
def command_c():
    import maya.mel as mel
    modScriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
    mel_script = (
        '$s = `getenv "MAYA_PLUG_IN_PATH" `;\n        $s = $s + ";{0}/BraidMaker";\n        putenv "MAYA_PLUG_IN_PATH" $s').format(
        modScriptsPath)
    mel.eval(mel_script)
    try:
        if not cmds.pluginInfo('braidMaker', q=1, loaded=1):
            cmds.loadPlugin('braidMaker')
        cmds.braidMaker()
    except:
        cmds.warning('Can not load braidMaker!')
def command_d():
    import Scene_Publish_Tool.scenePublishTool as SP
    SP.showWindow()