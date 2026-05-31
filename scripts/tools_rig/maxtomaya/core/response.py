#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob

import pymel.core as pm
import maya.cmds as cmds
from qtundo import undo
from rig.maxtomaya.ui.head import *
from rig.maxtomaya.ui.ui_main_window import ui_main_window
from rig.maxtomaya import max_to_maya
reload(max_to_maya)

class Response(QMainWindow):

    def __init__(self,parent=None):
        super(Response,self).__init__(parent)
        self.maya_win = parent
        self.setWindowTitle("max_to_maya")
        self.setupUI()
        self.getElems()
        self.setDefault()
        self.connection()
        self.resize(500, 500)

    def setupUI(self):
        self.ui_main_window = ui_main_window()
        self.setCentralWidget(self.ui_main_window)

    def getElems(self):
        self.cleanhi_pre_pushButton = self.ui_main_window.ui_maxtomaya_widget.main_Widget.cleanhi_pre_pushButton
        self.build_ac_pushButton = self.ui_main_window.ui_maxtomaya_widget.main_Widget.build_ac_pushButton
        self.cleanhi_post_pushButton=self.ui_main_window.ui_maxtomaya_widget.main_Widget.cleanhi_post_pushButton
        self.rig_check_pushButton = self.ui_main_window.ui_maxtomaya_widget.main_Widget.rig_check_pushButton

    def connection(self):
        #self.cleanhi_pre_pushButton.clicked.connect(lambda: self.add_to_list(way="reload",base=True,target=False))
        self.cleanhi_pre_pushButton.clicked.connect(self.cmd1)
        self.build_ac_pushButton.clicked.connect(self.cmd2)
        self.cleanhi_post_pushButton.clicked.connect(self.cmd3)
        self.rig_check_pushButton.clicked.connect(self.cmd4)

    def setDefault(self):
        pass

    @undo.qtundo
    def cmd1(self):
        max_to_maya.Organize_hierarchy()

    def cmd2(self):
        import AccCustomMapingNew
        AccCustomMapingNew.AccConvertFbx2Rig()

    @undo.qtundo
    def cmd3(self):
        max_to_maya.Organize_hierarchy_01()

    @undo.qtundo
    def cmd4(self):
        import rig.check.main.maya_load_win as maya_load_win
        reload(maya_load_win)
        ui = maya_load_win.MayaLoadWindow()
        ui.show()

if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    ui = Response()
    ui.show()
    sys.exit(app.exec_())