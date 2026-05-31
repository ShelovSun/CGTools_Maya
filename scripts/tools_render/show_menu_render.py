#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import maya.mel as mel
import os

from PySide2 import QtWidgets, QtGui

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_render', '')


def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction("LGTSetTool", menu)
    action_a.setIcon(QtGui.QIcon("{}/icons/light.png".format(scriptsPath)))
    action_a.triggered.connect(command_a)

    action_b = QtWidgets.QAction("Submit Job To Deadline", menu)
    action_b.setIcon(QtGui.QIcon("{}/icons/Submit.png".format(scriptsPath)))
    action_b.triggered.connect(command_b)

    action_c = QtWidgets.QAction("修复渲染层", menu)
    action_c.triggered.connect(command_c)
    menu.addAction(action_a)
    menu.addAction(action_b)
    menu.addAction(action_c)

    menu.exec_(QtGui.QCursor.pos())


def command_a():
    import tools_render.LGTSet_Maya.LGTSetTool as LS
    LS.showWindow()


def command_b():
    mel.eval('SubmitJobToDeadline')


def command_c():
    pass
