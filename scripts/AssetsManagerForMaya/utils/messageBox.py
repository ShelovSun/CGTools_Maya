#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sceneTools_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
import os
import maya.cmds as cmds
from PySide2 import QtGui, QtWidgets

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('utils', '')


def show_msg(msg_icon, icon, msg_tex, tex):
    msg_icon.clear()
    msg_icon.setPixmap(QtGui.QPixmap("%s/icon/%s.png" % (scriptsPath, icon)))
    msg_tex.clear()
    msg_tex.setText(tex)
    if icon == "warning":
        cmds.warning(tex)
    else:
        print(tex)


def show_msg_box(parent, tex):
    QtWidgets.QMessageBox.warning(parent, tex)


def aaa(tex):
    msg = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Information, u"提示：", tex)
    msg.setStandardButtons(QtWidgets.QMessageBox.Cancel)
    msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
    msg.exec_()
