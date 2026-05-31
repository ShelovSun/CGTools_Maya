# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'password.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(407, 113)
        self.gridLayout_2 = QGridLayout(Dialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 10, 5, 10)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        self.label.setFont(font)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)

        self.password_lineEdit = QLineEdit(Dialog)
        self.password_lineEdit.setObjectName(u"password_lineEdit")
        self.password_lineEdit.setClearButtonEnabled(True)

        self.gridLayout.addWidget(self.password_lineEdit, 1, 1, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.gridLayout.addWidget(self.buttonBox, 2, 1, 1, 1)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"*\u8bf7\u8f93\u5165\u7ba1\u7406\u5458\u5bc6\u7801\u4ee5\u83b7\u53d6\u4fee\u6539\u6743\u9650\uff1a", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Password", None))
    # retranslateUi

