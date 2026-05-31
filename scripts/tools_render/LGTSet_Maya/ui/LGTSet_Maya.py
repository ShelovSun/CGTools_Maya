# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'LGTSet_Maya.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(386, 537)
        font = QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        MainWindow.setFont(font)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_4 = QGridLayout(self.centralwidget)
        self.gridLayout_4.setSpacing(1)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(1, 1, 1, 1)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.ai_tab = QWidget()
        self.ai_tab.setObjectName(u"ai_tab")
        self.gridLayout_3 = QGridLayout(self.ai_tab)
        self.gridLayout_3.setSpacing(2)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(2, 10, 2, 2)
        self.tabWidget.addTab(self.ai_tab, "")
        self.rs_tab = QWidget()
        self.rs_tab.setObjectName(u"rs_tab")
        self.gridLayout = QGridLayout(self.rs_tab)
        self.gridLayout.setObjectName(u"gridLayout")
        self.tabWidget.addTab(self.rs_tab, "")
        self.vr_tab = QWidget()
        self.vr_tab.setObjectName(u"vr_tab")
        self.gridLayout_2 = QGridLayout(self.vr_tab)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.tabWidget.addTab(self.vr_tab, "")

        self.gridLayout_4.addWidget(self.tabWidget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.ai_tab), QCoreApplication.translate("MainWindow", u"Arnold", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.rs_tab), QCoreApplication.translate("MainWindow", u"RedShift", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.vr_tab), QCoreApplication.translate("MainWindow", u"VRay", None))
    # retranslateUi

