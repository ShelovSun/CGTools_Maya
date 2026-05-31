#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import os

from PySide2.QtCore import QFile, Qt
from PySide2.QtWidgets import QMainWindow, QTableWidgetItem
from PySide2 import QtUiTools
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QMainWindow)


class UI(MayaQWidgetDockableMixin, QMainWindow):
    VERSION = "1.0.1"
    scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')

    def __init__(self,  parent=maya_main_window()):
        super(UI, self).__init__(parent)
        self.setWindowTitle(u"资产重命名工具" + self.VERSION)
        self.ui = None

        self.show_ui()

    def show_ui(self):
        f = QFile('%s/ui/renameMat.ui' % self.scriptsPath)
        f.open(QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)

        # self.move(2000, 120)

        self.ui.list_wgt.setColumnWidth(0, 30)
        self.ui.list_wgt.setColumnWidth(1, 200)
        self.ui.list_wgt.setColumnWidth(2, 250)
        self.ui.list_wgt.setColumnWidth(3, 250)
        self.ui.list_wgt.setColumnWidth(4, 250)

        self.getInfo()
        self.ui.buttonBox.accepted.connect(self.rename)
        self.ui.buttonBox.rejected.connect(self.esc)

    def getInfo(self):
        new_name_list = []
        try:
            cmds.select('Geometry')
        except:
            cmds.warning(u"没有找到Geometry组模型")
        sl_mesh = cmds.ls(dag=1, sl=1, type="mesh")
        row = 0

        for mesh in sl_mesh:
            shadingGrps = cmds.listConnections(mesh, type='shadingEngine')
            if shadingGrps:
                sgs = list(set(shadingGrps))
                for sg in sgs:
                    shaders = cmds.ls(cmds.listConnections(sg), materials=1)
                    self.ui.list_wgt.insertRow(row)
                    check = QTableWidgetItem()
                    check.setCheckState(Qt.Checked)
                    # print(mesh, shadingGrps, shaders)
                    for i in range(97, 123):
                        new_name = "MI_" + mesh.replace('Shape', "") + "_" + chr(i)
                        if new_name in new_name_list:
                            new_name = "MI_" + mesh.replace('Shape', "") + "_" + chr(i+1)
                        else:
                            new_name_list.append(new_name)
                            break
                    self.ui.list_wgt.setItem(row, 0, check)
                    self.ui.list_wgt.setItem(row, 1, QTableWidgetItem(mesh))
                    self.ui.list_wgt.setItem(row, 2, QTableWidgetItem(sg))
                    self.ui.list_wgt.setItem(row, 3, QTableWidgetItem(shaders[0]))
                    self.ui.list_wgt.setItem(row, 4, QTableWidgetItem(new_name))
                row += 1

    def rename(self):
        """ """
        # print("rename")
        for i in range(0, self.ui.list_wgt.rowCount()):
            old = self.ui.list_wgt.item(i, 3).text()
            new = self.ui.list_wgt.item(i, 4).text()
            # print(old, new)
            try:
                cmds.rename(old, new)
            except:
                pass
        self.show_ui()
        self.getInfo()

    def esc(self):
        self.close()

    def show(self):
        dockable = False
        MayaQWidgetDockableMixin.show(self, dockable=dockable, floating=False, width=1100, height=500)  # area='right',
        # cmds.workspaceControl('myCustomWorkspaceControl', q=True, floating=True)


def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = UI()
    win.setAttribute(Qt.WA_DeleteOnClose)
    win.show()
    # cmds.workspaceControl('myCustomWorkspaceControl', e=True, floating=False)


