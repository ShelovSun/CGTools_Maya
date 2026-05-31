#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置右键菜单

import os,sys,maya.OpenMayaUI as omui
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance
from maya.app.general.mayaMixin import MayaQWidgetBaseMixin, MayaQWidgetDockableMixin

# def maya_main_window():
#     main_window_ptr = omui.MQtUtil.mainWindow()
#     return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)
#
# class Mod_menu_UI(QtWidgets.QMainWindow):
#     def __init__(self, parent=None):
#         super(Mod_menu_UI, self).__init__()
#         self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
#         self.parent = parent
#         self.showMenu()

def showMenu():
    menu = QtWidgets.QMenu()
    action_action = QtWidgets.QAction('Action')
    menu.addAction(action_action)
    menu.exec_(QtGui.QCursor.pos())
    #     f = QtCore.QFile('%s/ui/mod_menu.ui' % self.scriptsPath)
    #     f.open(QtCore.QFile.ReadOnly)
    #     loader = QtUiTools.QUiLoader().load(f)
    #     self.ui = loader
    #     f.close()
    #     self.init_ui()
    #
    # def init_ui(self):
    #     # self.getStyleSheet()
    #     self.setCentralWidget(self.ui)
    #     self.ui.setWindowFlags(QtCore.Qt.FramelessWindowHint)


# def showWindow():
#     global win
#     try:
#         win.close()
#     except:
#         pass
#
#     win = Mod_menu_UI()
#     win.show()