# -*- coding: utf-8 -*-
"""
author：GuanYJ

"""
import PySide2.QtCore as qc
import PySide2.QtGui as qg
import PySide2.QtWidgets as qw

import sys
import maya.mel as mm
import maya.cmds as cmds
import maya.OpenMayaUI as apiUI
import shiboken2

dialog = None

class RenameToolsUI(qw.QWidget):
    def __init__(self):
        super(RenameToolsUI, self).__init__()
        self.setWindowFlags(qc.Qt.Window)
        self.setLayout(qw.QVBoxLayout())
        self.layout().setContentsMargins(5, 5, 5, 5)
        self.layout().setSpacing(5)
        #self.layout().setAlignment(qc.Qt.AlignTop)
        #self.setFixedSize(500, 600)


        characterName_label = qw.QLabel("CharacterName:")
        self.name_line = qw.QLineEdit()
        self.name_bttn = qw.QPushButton("Create")
        self.type_comb = qw.QComboBox()
        self.customType_line = qw.QLineEdit()
        self.suffix_comb = qw.QComboBox()

        self.name_line.setEnabled(True)
        self.name_bttn.setFixedWidth(40)
        self.customType_line.setVisible(False)

        type_list = ["LongHair", "Ponytail", "HeadTop", "Bangs", "Temples", "Earlock", "Lanugo", "Beard", "Eyebrow", "Eyelash", "--- Custom ---"]
        suffix_list = ["---", "01", "02", "03"]
        typeName_label = qw.QLabel("Type:")
        self.type_comb.addItems(type_list)
        suffix_label = qw.QLabel("Suffix:")
        self.suffix_comb.addItems(suffix_list)

        percent_label = qw.QLabel("Percent:")
        self.percent_line = qw.QLineEdit()
        self.percent_bttn = qw.QPushButton("Percent")

        width_label = qw.QLabel("Width:")
        self.width_line = qw.QLineEdit()
        self.width_bttn = qw.QPushButton("Width")

        self.layout().addWidget(characterName_label)
        self.layout().addWidget(self.name_line)
        self.layout().addWidget(typeName_label)
        self.layout().addWidget(self.type_comb)
        self.layout().addWidget(self.customType_line)
        self.layout().addWidget(suffix_label)
        self.layout().addWidget(self.suffix_comb)
        self.layout().addWidget(self.name_bttn)

        self.layout().addWidget(percent_label)
        self.layout().addWidget(self.percent_line)
        self.layout().addWidget(self.percent_bttn)
        self.layout().addWidget(width_label)
        self.layout().addWidget(self.width_line)
        self.layout().addWidget(self.width_bttn)


        self.name_bttn.clicked.connect(self.hairSystemRename)
        self.type_comb.currentTextChanged.connect(self.typeComboChange)
        self.percent_bttn.clicked.connect(self.percentChange)
        self.width_bttn.clicked.connect(self.widthChange)


    def typeComboChange(self):
        if self.type_comb.currentText() == "--- Custom ---":
            self.customType_line.setVisible(True)
        else:
            self.customType_line.setVisible(False)

    def hairSystemRename(self):
        characterName = self.name_line.text()
        typeName = self.type_comb.currentText()
        customType = self.customType_line.text()
        suffix = self.suffix_comb.currentText()

        currentSelection = cmds.ls(selection=True)

        if characterName != "" and typeName != "--- Custom ---" and suffix != "---":
            newName = "%s_%s%s" % (characterName, typeName, suffix)
        elif characterName != "" and typeName != "--- Custom ---" and suffix == "---":
            newName = "%s_%s" % (characterName, typeName)
        elif characterName != "" and customType != "" and suffix != "---":
            newName = "%s_%s%s" % (characterName, customType, suffix)
        elif characterName != "" and customType != "" and suffix == "---":
            newName = "%s_%s" % (characterName, customType)
        else:
            cmds.warning("Please check your name!!!")
            return

        if cmds.objExists("%s_HairSim_GRP" % characterName) is False:
            cmds.group(empty=True, name="%s_HairSim_GRP" % characterName)
            cmds.group(empty=True, name="%s_Hair_FL" % characterName, parent="%s_HairSim_GRP" % characterName)
            cmds.group(empty=True, name="%s_Hair_CV" % characterName, parent="%s_HairSim_GRP" % characterName)
            cmds.group(empty=True, name="%s_Hair_HairSys" % characterName, parent="%s_HairSim_GRP" % characterName)


        cmds.select(currentSelection)
        mm.eval('''convertHairSelection "follicles";''')
        follicle_grp = cmds.pickWalk(direction="up")
        if len(follicle_grp) != 1:
            cmds.warning("There are two Follicles Group, please check!!!")
        else:
            cmds.rename(follicle_grp[0], "%s_FL" % newName)
            cmds.parent("%s_FL" % newName, "%s_Hair_FL" % characterName)

        mm.eval('''convertHairSelection "current";''')
        cv_grp = cmds.pickWalk(direction="up")
        if len(cv_grp) != 1:
            cmds.warning("There are two CV Group, please check!!!")
        else:
            cmds.rename(cv_grp[0], "%s_CV" % newName)
            cmds.parent("%s_CV" % newName, "%s_Hair_CV" % characterName)

        mm.eval('''convertHairSelection "hairSystems";''')
        hairSys_grp = cmds.pickWalk(direction="up")
        if len(hairSys_grp) != 1:
            cmds.warning("There are two HairSys, please check!!!")
        else:
            cmds.rename(hairSys_grp[0], "%s_HairSys" % newName)
            cmds.parent("%s_HairSys" % newName, "%s_Hair_HairSys" % characterName)

        # mm.eval('''displayHairCurves "all" 1;''')

    def percentChange(self):
        import xgenm as xg
        import xgenm.xgGlobal as xgg

        colls = xg.palettes()

        percent_val = str(self.percent_line.text())


        for coll in colls:
            descs = xg.descriptions(coll)
            for desc in descs:
                xg.setAttr("percent", "%s" % percent_val, coll, desc, "GLRenderer")

        de = xgg.DescriptionEditor
        de.refresh("Full")

    def widthChange(self):
        import xgenm as xg
        import xgenm.xgGlobal as xgg

        colls = xg.palettes()

        width_val = str(self.width_line.text())

        for coll in colls:
            descs = xg.descriptions(coll)
            for desc in descs:
                xg.setAttr("width", "%s" % width_val, coll, desc, "SplinePrimitive")

        de = xgg.DescriptionEditor
        de.refresh("Full")


