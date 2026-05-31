#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import os,sys,pymel.core as pm,maya.cmds as cmds,maya.mel as mel
from PySide2 import  QtWidgets, QtCore, QtGui
scriptsPath=os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_sim', '')

def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(u"解算助手",menu)
    # action_a.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_a.triggered.connect(command_a)

    action_b = QtWidgets.QAction(u"Dyn Joint Tools",menu)
    action_b.triggered.connect(command_b)


    menu.addAction(action_a)
    menu.addAction(action_b)


    menu.exec_(QtGui.QCursor.pos())

def command_a():
    file = "%s\\tools_sim\simTool.py" % scriptsPath
    exec(file)

def command_b():
    import tools_sim.DynJointTools.DynJointTool as DJ
    DJ.main()

