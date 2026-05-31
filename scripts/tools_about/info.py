# -*- coding: utf-8 -*-

import maya.OpenMayaUI as omui
import os
import requests


from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from shiboken2 import wrapInstance


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)


class InfoUI(MayaQWidgetDockableMixin, QtWidgets.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(InfoUI, self).__init__(parent)
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        f = QtCore.QFile('%s/info.ui' % self.scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.ui.web_bttn.clicked.connect(self.web)
        with open('%s/log.txt' % self.scriptsPath, "r") as f:
            text = f.read()
        self.ui.textBrowser.setText(text)
        self.ui.buttonBox.accepted.connect(self.esc)
        self.ui.buttonBox.rejected.connect(self.esc)
        # self.ui.pix.setPixmap("%s/pix.png" % self.scriptsPath)
        url = 'http://10.0.203.40/upload/proj_ffa_0/00000000/55e219706f490cfdd722a05835b36166.png?token=9617E8E1-CACC-5DBC-826E-06965C0933E5'
        # url = "http://www.baidu.com/img/bdlogo.png"# 测试可以访问
        res = requests.get(url)
        pix = QtGui.QPixmap()
        pix.loadFromData(res.content)
        # print(pix)
        self.ui.pix.setPixmap(pix)

    def web(self):
        import webbrowser
        webbrowser.open_new_tab('https://space.bilibili.com/475139733')

    def esc(self):
        self.close()

    def show(self):
        MayaQWidgetDockableMixin.show(self, dockable=False, width=380, height=510)


def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = InfoUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()
