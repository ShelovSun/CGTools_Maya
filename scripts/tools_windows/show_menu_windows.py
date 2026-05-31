#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import maya.cmds as cmds
import os
import sys

from PySide2 import QtWidgets, QtGui

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_windows', '')

userPrefDir = cmds.internalVar(userPrefDir=True)  # Result: u'C:/Users/asus/Documents/maya/2020/prefs/' #
moduleDir = os.environ.get("MAYA_MODULE_PATH")
sysTempDir = os.environ.get('TEMP')  # Result: 'C:\\Users\\asus\\AppData\\Local\\Temp' #
mayaPluginDir = os.environ.get("MAYA_PLUG_IN_PATH")
mayaScriptDir = os.environ.get("MAYA_SCRIPT_PATH")
mayaAppDir = os.environ.get("MAYA_APP_DIR")  # Result: 'C:/Users/asus/Documents/maya' #
PythonDir = os.environ.get("PYTHONPATH")
AssetsManagerIconTempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))


def showMenu():
    # print("show")
    # cmds.popupMenu(mm=True,b=1)
    # cmds.menuItem(rp='N', label=u'Export camRender', c='command_a()')
    # cmds.menuItem(rp='S', label=u'Import camRender', c='command_a()')
    # cmds.menuItem(label=u'1-1000', c='command_a()')
    # cmds.menuItem(label=u'1-10000', c='command_a()')
    # cmds.menuItem(label=u'10-10000', c='command_a()')
    # cmds.menuItem(label=u'1-100000', c='command_a()')
    # cmds.menuItem(label=u'100-1000000', c='command_a()')
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(u"打开 Render Temp 文件夹", menu)
    # action_a.setIcon(QtGui.QIcon("{}/icons/publish.png".format(scriptsPath)))
    action_a.triggered.connect(OpenWorkSpaceImageTemp)

    action_b = QtWidgets.QAction(u"打开 maya 配置文件夹", menu)
    action_b.triggered.connect(lambda: openDir(userPrefDir))

    action_c = QtWidgets.QAction(u"打开 Mod 文件夹", menu)
    action_c.triggered.connect(lambda: openDir(moduleDir.split(";")[0]))

    action_d = QtWidgets.QAction(u"打开 工具 Temp 文件夹", menu)
    action_d.triggered.connect(lambda: openDir(AssetsManagerIconTempPath))

    menu.addAction(action_a)
    menu.addAction(action_b)
    menu.addAction(action_c)
    menu.addAction(action_d)

    menu.exec_(QtGui.QCursor.pos())


def OpenWorkSpaceImageTemp():
    renderLayerNow = cmds.editRenderLayerGlobals(currentRenderLayer=True, q=True)
    temp = cmds.workspace(expandName='images')
    if os.path.isdir(temp):
        if os.path.isdir(temp + "/tmp"):
            temp = temp + "/tmp"
            if renderLayerNow != "defaultRenderLayer" and os.path.isdir(temp + renderLayerNow):
                temp = temp + renderLayerNow
        # print(temp)
        os.startfile(temp)
    else:
        cmds.error(u"工程路径:{}不存在！".format(temp))
    return temp


def openDir(temp):
    print(temp)
    if os.path.isdir(temp):
        os.startfile(temp)
    else:
        cmds.error(u"路径:{}不存在！".format(temp))
    return temp


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


def __print_sys_path():
    for i in sys.path:
        print(i)


def __print_pythonpath():
    for i in os.environ["PYTHONPATH"].split(";"):
        print(i)
