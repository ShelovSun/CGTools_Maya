# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'int.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(441, 514)
        self.verticalLayout_3 = QVBoxLayout(Form)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(2, 2, 2, 2)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_3 = QGroupBox(Form)
        self.groupBox_3.setObjectName(u"groupBox_3")
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(5, 5, 5, 5)
        self.ai_global_setting_pbttn = QPushButton(self.groupBox_3)
        self.ai_global_setting_pbttn.setObjectName(u"ai_global_setting_pbttn")
        font = QFont()
        font.setFamily(u"Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.ai_global_setting_pbttn.setFont(font)
        self.ai_global_setting_pbttn.setStyleSheet(u"background-color: rgb(0, 126, 129);")

        self.verticalLayout_2.addWidget(self.ai_global_setting_pbttn)

        self.ai_import_ch_lgt_pbttn = QPushButton(self.groupBox_3)
        self.ai_import_ch_lgt_pbttn.setObjectName(u"ai_import_ch_lgt_pbttn")
        self.ai_import_ch_lgt_pbttn.setFont(font)

        self.verticalLayout_2.addWidget(self.ai_import_ch_lgt_pbttn)


        self.verticalLayout.addWidget(self.groupBox_3)

        self.line = QFrame(Form)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.groupBox = QGroupBox(Form)
        self.groupBox.setObjectName(u"groupBox")
        font1 = QFont()
        font1.setFamily(u"Microsoft YaHei UI")
        font1.setPointSize(10)
        self.groupBox.setFont(font1)
        self.groupBox.setStyleSheet(u"border-color: rgb(0, 0, 0);\n"
"alternate-background-color: rgb(0, 0, 255);")
        self.groupBox.setFlat(False)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.ai_create_layers_pbttn = QPushButton(self.groupBox)
        self.ai_create_layers_pbttn.setObjectName(u"ai_create_layers_pbttn")
        self.ai_create_layers_pbttn.setFont(font)
        self.ai_create_layers_pbttn.setStyleSheet(u"background-color: rgb(0, 126, 129);")

        self.gridLayout.addWidget(self.ai_create_layers_pbttn, 2, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ai_layer_combox_01 = QComboBox(self.groupBox)
        self.ai_layer_combox_01.setObjectName(u"ai_layer_combox_01")
        self.ai_layer_combox_01.setStyleSheet(u"background-color: rgb(0, 0, 0);")

        self.horizontalLayout.addWidget(self.ai_layer_combox_01)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)
        self.label_2.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.horizontalLayout.addWidget(self.label_2)

        self.ai_layername_lineEdit = QLineEdit(self.groupBox)
        self.ai_layername_lineEdit.setObjectName(u"ai_layername_lineEdit")
        self.ai_layername_lineEdit.setStyleSheet(u"background-color: rgb(0, 0, 0);")
        self.ai_layername_lineEdit.setClearButtonEnabled(True)

        self.horizontalLayout.addWidget(self.ai_layername_lineEdit)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)
        self.label_3.setStyleSheet(u"color: rgb(0, 0, 0);")

        self.horizontalLayout.addWidget(self.label_3)

        self.ai_layer_combox_02 = QComboBox(self.groupBox)
        self.ai_layer_combox_02.setObjectName(u"ai_layer_combox_02")
        self.ai_layer_combox_02.setStyleSheet(u"background-color: rgb(0, 0, 0);")

        self.horizontalLayout.addWidget(self.ai_layer_combox_02)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.lineEdit_2 = QLineEdit(self.groupBox)
        self.lineEdit_2.setObjectName(u"lineEdit_2")
        self.lineEdit_2.setStyleSheet(u"background-color: rgb(0, 0, 0);")

        self.horizontalLayout_2.addWidget(self.lineEdit_2)

        self.label_5 = QLabel(self.groupBox)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_2.addWidget(self.label_5)

        self.lineEdit_3 = QLineEdit(self.groupBox)
        self.lineEdit_3.setObjectName(u"lineEdit_3")
        self.lineEdit_3.setStyleSheet(u"background-color: rgb(0, 0, 0);")

        self.horizontalLayout_2.addWidget(self.lineEdit_3)

        self.pushButton_4 = QPushButton(self.groupBox)
        self.pushButton_4.setObjectName(u"pushButton_4")

        self.horizontalLayout_2.addWidget(self.pushButton_4)


        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 1)


        self.verticalLayout.addWidget(self.groupBox)

        self.line_2 = QFrame(Form)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.HLine)
        self.line_2.setFrameShadow(QFrame.Sunken)

        self.verticalLayout.addWidget(self.line_2)

        self.aovs_groupBox = QGroupBox(Form)
        self.aovs_groupBox.setObjectName(u"aovs_groupBox")
        self.gridLayout_2 = QGridLayout(self.aovs_groupBox)
        self.gridLayout_2.setSpacing(5)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self.AO = QCheckBox(self.aovs_groupBox)
        self.AO.setObjectName(u"AO")
        self.AO.setCheckable(True)
        self.AO.setChecked(False)

        self.gridLayout_2.addWidget(self.AO, 2, 0, 1, 1)

        self.specular = QCheckBox(self.aovs_groupBox)
        self.specular.setObjectName(u"specular")

        self.gridLayout_2.addWidget(self.specular, 2, 1, 1, 1)

        self.sss = QCheckBox(self.aovs_groupBox)
        self.sss.setObjectName(u"sss")

        self.gridLayout_2.addWidget(self.sss, 0, 2, 1, 1)

        self.direct = QCheckBox(self.aovs_groupBox)
        self.direct.setObjectName(u"direct")

        self.gridLayout_2.addWidget(self.direct, 4, 2, 1, 1)

        self.Z = QCheckBox(self.aovs_groupBox)
        self.Z.setObjectName(u"Z")

        self.gridLayout_2.addWidget(self.Z, 3, 1, 1, 1)

        self.N = QCheckBox(self.aovs_groupBox)
        self.N.setObjectName(u"N")

        self.gridLayout_2.addWidget(self.N, 2, 2, 1, 1)

        self.crypto_asset = QCheckBox(self.aovs_groupBox)
        self.crypto_asset.setObjectName(u"crypto_asset")

        self.gridLayout_2.addWidget(self.crypto_asset, 3, 2, 1, 1)

        self.diffuse = QCheckBox(self.aovs_groupBox)
        self.diffuse.setObjectName(u"diffuse")
        self.diffuse.setChecked(False)

        self.gridLayout_2.addWidget(self.diffuse, 0, 1, 1, 1)

        self.crypto_material = QCheckBox(self.aovs_groupBox)
        self.crypto_material.setObjectName(u"crypto_material")

        self.gridLayout_2.addWidget(self.crypto_material, 4, 0, 1, 1)

        self.P = QCheckBox(self.aovs_groupBox)
        self.P.setObjectName(u"P")

        self.gridLayout_2.addWidget(self.P, 3, 0, 1, 1)

        self.indirect = QCheckBox(self.aovs_groupBox)
        self.indirect.setObjectName(u"indirect")

        self.gridLayout_2.addWidget(self.indirect, 5, 0, 1, 1)

        self.RGBA = QCheckBox(self.aovs_groupBox)
        self.RGBA.setObjectName(u"RGBA")
        self.RGBA.setChecked(False)

        self.gridLayout_2.addWidget(self.RGBA, 0, 0, 1, 1)

        self.crypto_object = QCheckBox(self.aovs_groupBox)
        self.crypto_object.setObjectName(u"crypto_object")

        self.gridLayout_2.addWidget(self.crypto_object, 4, 1, 1, 1)


        self.verticalLayout.addWidget(self.aovs_groupBox)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.verticalLayout_3.addLayout(self.verticalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("Form", u"01.Global", None))
        self.ai_global_setting_pbttn.setText(QCoreApplication.translate("Form", u"Global Setting", None))
        self.ai_import_ch_lgt_pbttn.setText(QCoreApplication.translate("Form", u"Import CH_LGT", None))
        self.groupBox.setTitle(QCoreApplication.translate("Form", u"02.Creat Layers:", None))
        self.ai_create_layers_pbttn.setText(QCoreApplication.translate("Form", u"Create Layers", None))
        self.label_4.setText(QCoreApplication.translate("Form", u"Layer Name:", None))
        self.label_2.setText(QCoreApplication.translate("Form", u"_", None))
        self.ai_layername_lineEdit.setText(QCoreApplication.translate("Form", u"GRP", None))
        self.label_3.setText(QCoreApplication.translate("Form", u"_", None))
        self.lineEdit_2.setText("")
        self.lineEdit_2.setPlaceholderText(QCoreApplication.translate("Form", u"old_name", None))
        self.label_5.setText(QCoreApplication.translate("Form", u">>>>>", None))
        self.lineEdit_3.setText("")
        self.lineEdit_3.setPlaceholderText(QCoreApplication.translate("Form", u"new_name", None))
        self.pushButton_4.setText(QCoreApplication.translate("Form", u"ReName", None))
        self.aovs_groupBox.setTitle(QCoreApplication.translate("Form", u"03.Creat AOVs:", None))
        self.AO.setText(QCoreApplication.translate("Form", u"AO", None))
        self.specular.setText(QCoreApplication.translate("Form", u"specular", None))
        self.sss.setText(QCoreApplication.translate("Form", u"sss", None))
        self.direct.setText(QCoreApplication.translate("Form", u"direct", None))
        self.Z.setText(QCoreApplication.translate("Form", u"Z", None))
        self.N.setText(QCoreApplication.translate("Form", u"N", None))
        self.crypto_asset.setText(QCoreApplication.translate("Form", u"crypto_asset", None))
        self.diffuse.setText(QCoreApplication.translate("Form", u"diffuse", None))
        self.crypto_material.setText(QCoreApplication.translate("Form", u"crypto_material", None))
        self.P.setText(QCoreApplication.translate("Form", u"P", None))
        self.indirect.setText(QCoreApplication.translate("Form", u"indirect", None))
        self.RGBA.setText(QCoreApplication.translate("Form", u"RGBA", None))
        self.crypto_object.setText(QCoreApplication.translate("Form", u"crypto_object", None))
    # retranslateUi

