#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import os
from PySide2 import QtWidgets, QtGui

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_ani', '')


def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(u"Action Publish", menu)
    action_a.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_a.triggered.connect(command_a)

    action_b = QtWidgets.QAction(u"Spring Magic", menu)
    action_b.triggered.connect(command_b)

    action_c = QtWidgets.QAction(u"Studio Library", menu)
    action_c.setIcon(QtGui.QIcon("{}/tools_ani/StudioLibrary/icon/logo.png".format(scriptsPath)))
    action_c.triggered.connect(command_studio_library)

    action_d = QtWidgets.QAction(u"IK/FK Switcher", menu)
    action_d.setIcon(QtGui.QIcon("{}/tools_ani/IKFKSwitch/icon/ikfk.png".format(scriptsPath)))
    action_d.triggered.connect(command_d)

    action_e = QtWidgets.QAction(u"BroDynamics", menu)
    action_e.triggered.connect(command_e)

    action_f = QtWidgets.QAction(u"动作小工具", menu)
    action_f.triggered.connect(command_f)

    menu.addAction(action_a)
    menu.addAction(action_f)
    menu.addAction(action_b)
    menu.addAction(action_c)
    menu.addAction(action_d)
    menu.addAction(action_e)

    menu.exec_(QtGui.QCursor.pos())


def command_a():
    import tools_publish.PublishTools.PublishTool as RP
    RP.showWindow(3)


def command_b():  # 错误未解决
    file = r"%s/tools_ani/SpringMagic/springMagic.py" % scriptsPath
    exec(file)


def command_studio_library():
    import tools_ani.StudioLibrary.studiolibrary.main as SL
    SL.main()


def command_d():
    import tools_ani.IKFKSwitch.IKFKSwitch as IKFK
    IKFK.ikFkSwitch().createUi()


def command_e():
    import tools_ani.BroTools as BroTools
    BroTools.BroDynamics.BroDynamicsUI.initUI()

def command_f():
    import tools_ani.Ani_smallTools as SmallTools
    SmallTools.ShowUI().createUi()