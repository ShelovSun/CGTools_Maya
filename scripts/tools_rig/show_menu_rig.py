#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import maya.mel as mel
import os
import sys

from PySide2 import QtWidgets, QtGui

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_rig', '')
sys.path.append(scriptsPath)
sys.path.append(r"%s\lib" % scriptsPath)
sys.path.append(r"%s\tools_rig\shapes\SHAPES\scripts" % scriptsPath)


def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(u"Rig Publish", menu)
    action_a.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_a.triggered.connect(command_a)

    action_b = QtWidgets.QAction(u"check", menu)
    action_b.triggered.connect(command_b)

    action_c = QtWidgets.QAction(u"Advanced Skeleton", menu)
    action_c.setIcon(
        QtGui.QIcon(r"{}/tools_rig/AdvancedSkeleton/AdvancedSkeleton5Files/icons/asLogo_32.png".format(scriptsPath)))
    action_c.triggered.connect(command_c)

    action_d = QtWidgets.QAction(u"Max To Maya", menu)
    action_d.triggered.connect(command_d)

    action_e = QtWidgets.QAction(u"Copy Weights(ml)", menu)
    action_e.triggered.connect(command_e)

    action_f = QtWidgets.QAction(u"Batch Copy Weights", menu)
    action_f.triggered.connect(command_f)

    action_g = QtWidgets.QAction(u"Control Maker", menu)
    action_g.triggered.connect(command_g)

    action_h = QtWidgets.QAction(u"Riggest Controllers", menu)
    action_h.triggered.connect(command_h)

    action_i = QtWidgets.QAction(u"NgSkinTool", menu)
    action_i.setIcon(
        QtGui.QIcon(r"{}/tools_rig/ngskintools/Contents/icons/ngSkinTools2ShelfIcon.png".format(scriptsPath)))
    action_i.triggered.connect(command_i)

    action_j = QtWidgets.QAction(u"SHAPES", menu)
    action_j.triggered.connect(command_j)

    menu.addAction(action_a)
    menu.addAction(action_b)
    menu.addSeparator()
    menu.addAction(action_c)
    menu.addAction(action_d)
    menu.addSeparator()
    menu.addAction(action_e)
    menu.addAction(action_f)
    menu.addAction(action_g)
    menu.addAction(action_h)
    menu.addAction(action_i)
    menu.addAction(action_j)

    menu.exec_(QtGui.QCursor.pos())


def command_a():
    import Rig_Publish_Tool.rigPublishTool as RP
    RP.showWindow()


def command_b():
    import tools_rig.check.main.maya_load_win as maya_load_win
    ui = maya_load_win.MayaLoadWindow()
    ui.show()


def command_c():
    import tools_rig.AdvancedSkeleton.AdvancedSkeleton as AdvancedSkeleton
    adv = AdvancedSkeleton.ADV()
    adv.run_adv()


def command_d():
    import maxtomaya.main.maya_load_win as maya_load_win
    ui = maya_load_win.MayaLoadWindow()
    ui.show()


def command_e():
    import tools_ani.ml_tools.ml_copySkin as ml_copySkin
    ml_copySkin.ui()


def command_f():
    import tools_rig.batch_copyskin.main.maya_load_win as maya_load_win
    ui = maya_load_win.MayaLoadWindow()
    ui.show()


def command_g():
    Path = "%s/tools_rig/curveUtil/for_Maya" % scriptsPath
    mel_script = (
        '$s = `getenv "MAYA_SCRIPT_PATH" `;\n        $s = $s + ";{0}";\n        putenv "MAYA_SCRIPT_PATH" $s').format(
        Path)
    mel.eval(mel_script)
    mel.eval('controlMaker;')


def command_h():
    Path = "%s/tools_rig/curveUtil/for_Maya" % scriptsPath
    mel_script = (
        '$s = `getenv "MAYA_SCRIPT_PATH" `;\n        $s = $s + ";{0}";\n        putenv "MAYA_SCRIPT_PATH" $s').format(
        Path)
    mel.eval(mel_script)
    mel.eval('Riggest_controllers;')


def command_i():
    sys.path.append(r"%s\tools_rig\ngskintools\Contents\scripts" % scriptsPath)
    import ngSkinTools2
    ngSkinTools2.open_ui()


def command_j():
    Path = "%s/tools_rig/SHAPES/SHAPES/for_Maya" % scriptsPath
    mel_script = (
        '$s = `getenv "MAYA_SCRIPT_PATH" `;\n        $s = $s + ";{0}";\n        putenv "MAYA_SCRIPT_PATH" $s').format(
        Path)
    mel.eval(mel_script)
    mel.eval('SHAPES;')
