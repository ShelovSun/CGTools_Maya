# -*- coding: utf-8 -*-
"""
Author: onemt
Date: 2020/5/20 14:55
"""

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.mel as mel

from functools import partial

def maya_main_window():
    """
    Return the Maya main window widget as a Python object
    """
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class CustomDialog(QtWidgets.QDialog):
    WINDOW_TITLE = "Shader Helper"
    
    def __init__(self, parent=maya_main_window()):
        super(CustomDialog, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(600, 400)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.lambert_items = []

    def create_widgets(self):
        self.label = QtWidgets.QLabel("Shader Name")
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.name_le = QtWidgets.QLineEdit()
        self.create_bttn = QtWidgets.QPushButton("Create")
        self.refresh_bttn = QtWidgets.QPushButton("Refresh")

    def create_layout(self):
        shader_layout = QtWidgets.QHBoxLayout()
        shader_layout.addWidget(self.name_le)
        shader_layout.addWidget(self.create_bttn)
        shader_layout.addWidget(self.refresh_bttn)

        lambert_list_wdg = QtWidgets.QWidget()
        self.lambert_layout = QtWidgets.QVBoxLayout(lambert_list_wdg)
        self.lambert_layout.setContentsMargins(2, 2, 2, 2)
        self.lambert_layout.setSpacing(3)
        self.lambert_layout.setAlignment(QtCore.Qt.AlignTop)

        lambert_list_scroll_area = QtWidgets.QScrollArea()
        lambert_list_scroll_area.setWidgetResizable(True)
        lambert_list_scroll_area.setWidget(lambert_list_wdg)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.addWidget(self.label)
        main_layout.addLayout(shader_layout)
        main_layout.addWidget(lambert_list_scroll_area)
        main_layout.addStretch()

    def create_connections(self):
        self.create_bttn.clicked.connect(self.create_lambert)
        self.refresh_bttn.clicked.connect(self.refresh_lambert)

    def showEvent(self, event):
        super(CustomDialog, self).showEvent(event)
        self.refresh_lambert()

    def create_lambert(self):
        lambert_name = self.name_le.text()
        if not lambert_name:
            cmds.warning("Please give a name.")
            return

        lambert_name = cmds.shadingNode("lambert", name=lambert_name+"_ID_MTL", asShader=True)

        self.refresh_lambert()

    def refresh_lambert(self):
        self.clear_lambert()

        lambert_list = cmds.ls("*_ID_MTL*", materials=True)
        for lambert in lambert_list:
            lambert_item = ShaderItem(lambert)
            self.lambert_layout.addWidget(lambert_item)
            self.lambert_items.append(lambert_item)

    def clear_lambert(self):
        self.lambert_items = []

        while self.lambert_layout.count() > 0:
            lambert_item = self.lambert_layout.takeAt(0)
            if lambert_item.widget():
                lambert_item.widget().deleteLater()


class ShaderItem(QtWidgets.QWidget):
    def __init__(self, lambert_name, parent=None):
        super(ShaderItem, self).__init__(parent)

        self.name = lambert_name

        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.update_value()

    def create_widgets(self):
        self.lambert_name = QtWidgets.QLabel(self.name)
        self.lambert_color = CustomColorButton()
        self.apply_bttn = QtWidgets.QPushButton("Apply")
        self.select_bttn = QtWidgets.QPushButton("Select")

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.lambert_name)
        main_layout.addWidget(self.lambert_color)
        main_layout.addWidget(self.apply_bttn)
        main_layout.addWidget(self.select_bttn)

    def create_connections(self):
        self.lambert_color.color_changed.connect(self.update_color)
        self.apply_bttn.clicked.connect(self.apply_material)
        self.select_bttn.clicked.connect(self.select_mesh)

    def update_value(self):
        self.lambert_color.color_changed.disconnect(self.update_color)

        current_color = cmds.getAttr("{0}.color".format(self.name))[0]
        col = QtGui.QColor(current_color[0]*255, current_color[1]*255, current_color[2]*255)
        self.lambert_color.set_color(col)

        self.lambert_color.color_changed.connect(self.update_color)

    def update_color(self):
        col = self.lambert_color.get_color()
        cmds.setAttr("{0}.{1}".format(self.name, "color"), col.redF(), col.greenF(), col.blueF())

    def apply_material(self):
        sg_name = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="{0}_SG".format(self.name))
        cmds.connectAttr("{0}.{1}".format(self.name, "outColor"), "{0}.{1}".format(sg_name, "surfaceShader"), force=True)

        selected_list = cmds.ls(selection=True)
        for i in selected_list:
            cmds.select(i)
            cmds.sets(forceElement=sg_name, edit=True)

    def select_mesh(self):
        meshs = cmds.listConnections("{}_SG".format(self.name), type="mesh")
        cmds.select(meshs, replace=True)


class CustomColorButton(QtWidgets.QWidget):
    color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color=QtCore.Qt.white, parent=None):
        super(CustomColorButton, self).__init__(parent)
        self.setObjectName("CustomColorButton")

        self.create_control()
        # self.set_size(50, 14)
        self.set_color(color)

    def create_control(self):
        window = cmds.window()
        color_slider_name = cmds.colorSliderGrp()

        self._color_slider_obj = omui.MQtUtil.findControl(color_slider_name)
        if self._color_slider_obj:
            self._color_slider_widget = wrapInstance(long(self._color_slider_obj), QtWidgets.QWidget)

            main_layout = QtWidgets.QVBoxLayout(self)
            main_layout.setObjectName("main_layout")
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.addWidget(self._color_slider_widget)

            # children = self._color_slider_widget.children()
            self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "slider")
            # if self._slider_widget:
            #     self._slider_widget.hide()

            self._color_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, "port")

            cmds.colorSliderGrp(self.get_full_name(), e=True, changeCommand=partial(self.on_color_changed))

        cmds.deleteUI(window, window=True)

    def get_full_name(self):
        return omui.MQtUtil.fullName(long(self._color_slider_obj))

    def set_size(self, width, height):
        self._color_slider_widget.setFixedWidth(width)
        self._color_widget.setFixedHeight(height)

    def set_color(self, color):
        color = QtGui.QColor(color)
        if color != self.get_color():
            cmds.colorSliderGrp(self.get_full_name(), e=True, rgbValue=(color.redF(), color.greenF(), color.blueF()))
            self.on_color_changed()

    def get_color(self):
        color = cmds.colorSliderGrp(self.get_full_name(), query=True, rgbValue=True)

        color = QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        return color

    def on_color_changed(self, *args):
        self.color_changed.emit(self.get_color())


def showWindow():
    global dialog
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = CustomDialog()
    dialog.show()


if __name__ == "__main__":
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = CustomDialog()
    dialog.show()
