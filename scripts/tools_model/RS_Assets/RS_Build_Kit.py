# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.6 (tags/v3.8.6:db45529, Sep 23 2020, 15:37:30) [MSC v.1927 32 bit (Intel)]
# Embedded file name: C:/Users/Erik Lehmann/Documents/maya/2020/for_Maya\RS_Build_Kit.py
# Compiled at: 2020-12-20 17:28:35
"""
Build Kit 1.0.5
Author: Erik Lehmann
Copyright (c) 2020 Erik Lehmann
Email: hello(at)rocket-square.com
"""
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui, maya.OpenMaya as om, maya.cmds as mc, maya.mel as mm, math, sys, os, re, random, time
from array import array

def buKi_maya_main_window():
    buKi_main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(buKi_main_window_ptr), QtWidgets.QWidget)


class QListWidget_Custom(QtWidgets.QListWidget):

    def __init__(self, name, parent=None):
        super(QListWidget_Custom, self).__init__(parent)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Delete:
            self._del_item()

    def _del_item(self):
        for item in self.selectedItems():
            self.takeItem(self.row(item))


class QPushButton_Custom(QtWidgets.QPushButton):
    rmb_clicked = QtCore.Signal()

    def __init__(self, name, parent=None):
        super(QPushButton_Custom, self).__init__(name, parent)

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:
            self.setDown(True)
            return
        super(QPushButton_Custom, self).mousePressEvent(mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:
            self.setDown(False)
            self.rmb_clicked.emit()
            return
        super(QPushButton_Custom, self).mouseReleaseEvent(mouse_event)


class QDialog_Custom_Warning(QtWidgets.QDialog):

    def __init__(self, parent=buKi_maya_main_window()):
        super(QDialog_Custom_Warning, self).__init__(parent)
        self.setWindowTitle('  Save as')
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        os_check = sys.platform
        if os_check == 'darwin':
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.buKi_warning_message_label = QtWidgets.QLabel()
        self.buKi_warning_message_label.setText('')
        self.ok_btn = QtWidgets.QPushButton('Ok')
        self.cancel_btn = QtWidgets.QPushButton('Cancel')

    def create_layout(self):
        message_layout = QtWidgets.QHBoxLayout()
        message_layout.addWidget(self.buKi_warning_message_label)
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(message_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.close)


class MainClass_BuildKit(QtWidgets.QDialog):
    buKi_instance = None

    @classmethod
    def show_buKi_dialog(cls):
        if not cls.buKi_instance:
            cls.buKi_instance = MainClass_BuildKit()
        if cls.buKi_instance.isHidden():
            cls.buKi_instance.show()
        else:
            cls.buKi_instance.raise_()
            cls.buKi_instance

    def __init__(self, parent=buKi_maya_main_window()):
        super(MainClass_BuildKit, self).__init__(parent)
        self.buKi_user_path = self.get_user_path()
        self.build_kit_window = self
        self.build_kit_window.setMinimumWidth(200)
        self.build_kit_window.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        os_check = sys.platform
        if os_check == 'darwin':
            self.build_kit_window.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowStaysOnTopHint)
        self.buKi_create_styleSheet()
        self.buKi_load_images()
        self.buKi_create_pageSizes()
        self.buKi_create_widgets()
        self.buKi_create_layouts()
        self.buKi_create_connections()
        self.buKi_create_libraries()
        self.buKi_change_active_page('  Build Kit', 30, False)
        self.build_kit_window.setWindowIcon(QtGui.QIcon(self.icon_RS_logo))

    def get_user_path(self):
        user_path = os.getenv('RS_TOOLS_PATH')
        if not user_path:
            user_path = mc.internalVar(usd=True)
            if os.path.isfile('%sRS_Build_Kit.pyc' % user_path) == True or os.path.isfile('%sRS_Build_Kit.py' % user_path) == True:
                user_path = user_path + 'RS_Assets/RS_Build_Kit/'
            else:
                user_path = mc.internalVar(upd=True)
                user_path = user_path + 'for_Maya/RS_Assets/RS_Build_Kit/'
        else:
            user_path = user_path + '/RS_Assets/RS_Build_Kit/'
        return user_path

    def buKi_create_libraries(self):
        self.buKi_windowTitles = [
         '  Mesh Tools', '  Import \\ Export', '  About', '  Build Kit']
        self.buKi_lib_menuPage = [self.buKi_mesh_page, self.buKi_importExport_page, self.buKi_about_page]
        self.buKi_lib_meshSettings = [
         self.buKi_mesh_settings_combine,
         self.buKi_select_settings_topology, self.buKi_select_settings_angle, self.buKi_select_settings_nthEdge, self.buKi_select_settings_percentage, self.buKi_select_settings_cmptCount, self.buKi_select_settings_name, self.buKi_select_settings_type,
         self.buKi_mesh_settings_place, self.buKi_mesh_settings_paint, self.buKi_mesh_settings_distribute, self.buKi_mesh_settings_duplicator]
        self.buKi_lib_meshSettingsBtn = [
         self.buKi_mesh_toolbox_combine_btn,
         self.buKi_mesh_select_topology_btn, self.buKi_mesh_select_angle_btn, self.buKi_mesh_select_nthEdge_btn, self.buKi_mesh_select_percentage_btn, self.buKi_mesh_select_cmptCount_btn, self.buKi_mesh_select_name_btn, self.buKi_mesh_select_type_btn,
         self.buKi_mesh_layout_place_btn, self.buKi_mesh_layout_paint_btn, self.buKi_mesh_layout_distribute_btn, self.buKi_mesh_layout_duplicator_btn]
        self.buKi_lib_importExport_settings = [
         self.buKi_import_settings_obj,
         self.buKi_export_settings_obj, self.buKi_export_settings_fbx, self.buKi_export_settings_abc]
        self.buKi_lib_importExport_settingsBtn = [
         self.buKi_obj_import_btn,
         self.buKi_obj_export_btn, self.buKi_fbx_export_btn, self.buKi_abc_export_btn]
        self.buKi_lib_settingsBtn = [
         self.buKi_lib_meshSettingsBtn, self.buKi_lib_importExport_settingsBtn, '']
        self.hotkey_library_mesh = [{'name': 'AdvancedCombine', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_combine()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_combine()'}, {'name': 'AdvancedSeparate', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_separate()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_separate()'}, {'name': 'AdvancedExtract', 'command': "try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_extract_duplicate_check('_Ext')\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_extract_duplicate_check('_Ext')"}, {'name': 'AdvancedDuplicateFace', 'command': "try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_extract_duplicate_check('_Dup')\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_extract_duplicate_check('_Dup')"}, {'name': 'AppendPlus', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_append_plus()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_append_plus()'}, {'name': 'AppendRingLoop', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buki_append_ring_loop()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buki_append_ring_loop()'}, {'name': 'QuadFill', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_quad_fill()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_quad_fill()'}, {'name': 'PivotBottom', 'command': "try:\n\tRS_Build_Kit.MainClass_BuildKit().pivot_position('bottom')\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().pivot_position('bottom')"}, {'name': 'PivotTop', 'command': "try:\n\tRS_Build_Kit.MainClass_BuildKit().pivot_position('top')\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().pivot_position('top')"}, {'name': 'ConnectDiamond', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_diamond()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_diamond()'}, {'name': 'ConnectCorner', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_corner()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_corner()'}, {'name': 'ConnectEnd', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_end()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_end()'}, {'name': 'ConnectLine', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_line()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_connect_line()'}, {'name': 'FortyFiveMeshAngle', 'command': "try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_forty_five_mesh_angle('positive', False)\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_forty_five_mesh_angle('positive', False)"}]
        self.hotkey_library_select = [{'name': 'SelectByAngle', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_select_by_angle()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_select_by_angle()'}, {'name': 'FillShell', 'command': 'try:\n\tRS_Build_Kit.MainClass_BuildKit().buKi_fill_prepare_shell()\nexcept:\n\timport RS_Build_Kit\n\tRS_Build_Kit.MainClass_BuildKit().buKi_fill_prepare_shell()'}]
        self.hotkey_library_launch = [{'name': 'BuildKit', 'command': 'import RS_Build_Kit\nreload(RS_Build_Kit)\nRS_Build_Kit.MainClass_BuildKit.show_buKi_dialog()'}]

    def buKi_load_images(self):
        self.icon_RS_logo = QtGui.QPixmap('%sicon_RS_logo.png' % self.buKi_user_path)
        self.buKi_icon_mesh_active = QtGui.QPixmap('%smesh_active.png' % self.buKi_user_path)
        self.buKi_icon_mesh_inactive = QtGui.QPixmap('%smesh_inactive.png' % self.buKi_user_path)
        self.buKi_icon_importExport_active = QtGui.QPixmap('%simportExport_active.png' % self.buKi_user_path)
        self.buKi_icon_importExport_inactive = QtGui.QPixmap('%simportExport_inactive.png' % self.buKi_user_path)
        self.buKi_icon_about_active = QtGui.QPixmap('%sstack_active.png' % self.buKi_user_path)
        self.buKi_icon_about_inactive = QtGui.QPixmap('%sstack_inactive.png' % self.buKi_user_path)
        self.buKi_icon_expand = QtGui.QPixmap('%sicon_expand.png' % self.buKi_user_path)
        self.buKi_icon_collapse = QtGui.QPixmap('%sicon_collapse.png' % self.buKi_user_path)
        self.buKi_icon_extract_btn = QtGui.QPixmap('%sicon_mesh_extract.png' % self.buKi_user_path)
        self.buKi_icon_duplicateFace_btn = QtGui.QPixmap('%sicon_mesh_duplicateFace.png' % self.buKi_user_path)
        self.buKi_icon_connect_btn = QtGui.QPixmap('%sicon_mesh_connect.png' % self.buKi_user_path)
        self.buKi_icon_append_btn = QtGui.QPixmap('%sicon_mesh_append.png' % self.buKi_user_path)
        self.buKi_icon_combine_btn = QtGui.QPixmap('%sicon_mesh_combine.png' % self.buKi_user_path)
        self.buKi_icon_separate_btn = QtGui.QPixmap('%sicon_mesh_separate.png' % self.buKi_user_path)
        self.buKi_icon_mirror_btn = QtGui.QPixmap('%sicon_mesh_mirror.png' % self.buKi_user_path)
        self.buKi_icon_pivot_btn = QtGui.QPixmap('%sicon_mesh_pivot.png' % self.buKi_user_path)
        self.buKi_icon_group_btn = QtGui.QPixmap('%sicon_mesh_group.png' % self.buKi_user_path)
        self.buKi_icon_corner_btn = QtGui.QPixmap('%sicon_mesh_angle.png' % self.buKi_user_path)
        self.buKi_icon_quadFill_btn = QtGui.QPixmap('%sicon_mesh_quadFill.png' % self.buKi_user_path)
        self.buKi_icon_topology_btn = QtGui.QPixmap('%sicon_select_topology.png' % self.buKi_user_path)
        self.buKi_icon_angle_btn = QtGui.QPixmap('%sicon_select_angle.png' % self.buKi_user_path)
        self.buKi_icon_nthEdge_btn = QtGui.QPixmap('%sicon_select_nthEdge.png' % self.buKi_user_path)
        self.buKi_icon_fillShell_btn = QtGui.QPixmap('%sicon_select_fillShell.png' % self.buKi_user_path)
        self.buKi_icon_percentage_btn = QtGui.QPixmap('%sicon_select_percentage.png' % self.buKi_user_path)
        self.buKi_icon_cmptCount_btn = QtGui.QPixmap('%sicon_select_cmptCount.png' % self.buKi_user_path)
        self.buKi_icon_name_btn = QtGui.QPixmap('%sicon_select_name.png' % self.buKi_user_path)
        self.buKi_icon_type_btn = QtGui.QPixmap('%sicon_select_type.png' % self.buKi_user_path)
        self.buKi_icon_layout_place_btn = QtGui.QPixmap('%sicon_layout_place.png' % self.buKi_user_path)
        self.buKi_icon_layout_paint_btn = QtGui.QPixmap('%sicon_layout_paint.png' % self.buKi_user_path)
        self.buKi_icon_layout_distribute_btn = QtGui.QPixmap('%sicon_layout_distribute.png' % self.buKi_user_path)
        self.buKi_icon_layout_duplicator_btn = QtGui.QPixmap('%sicon_layout_duplicator.png' % self.buKi_user_path)
        self.buKi_icon_import_obj_btn = QtGui.QPixmap('%sicon_import_obj.png' % self.buKi_user_path)
        self.buKi_icon_import_fbx_btn = QtGui.QPixmap('%sicon_import_fbx.png' % self.buKi_user_path)
        self.buKi_icon_import_abc_btn = QtGui.QPixmap('%sicon_import_abc.png' % self.buKi_user_path)
        self.buKi_icon_export_obj_btn = QtGui.QPixmap('%sicon_export_obj.png' % self.buKi_user_path)
        self.buKi_icon_export_fbx_btn = QtGui.QPixmap('%sicon_export_fbx.png' % self.buKi_user_path)
        self.buKi_icon_export_abc_btn = QtGui.QPixmap('%sicon_export_abc.png' % self.buKi_user_path)
        self.buKi_img_about_header = QtGui.QPixmap('%sRS_Build_Kit_about.png' % self.buKi_user_path)

    def setup_button(self, button, style=None, tip=None, icon=None, obj_name=None, iSize=None, h=None, w=None):
        if tip:
            button.setToolTip('%s' % tip)
        if style:
            button.setStyleSheet(style)
        if obj_name:
            button.setObjectName('%s' % obj_name)
        if icon:
            button.setIcon(QtGui.QPixmap(icon))
        if iSize:
            button.setIconSize(QtCore.QSize(iSize, iSize))
        if h:
            button.setFixedHeight(h)
        if w:
            button.setFixedWidth(w)

    def setup_line_edit(self, line_edit, style=None, fPolicy=None, height=None, margin=None, placeholder=None):
        if fPolicy:
            line_edit.setFocusPolicy(QtCore.Qt.FocusPolicy(fPolicy))
        if height:
            line_edit.setFixedHeight(height)
        if style:
            line_edit.setStyleSheet(style)
        if margin:
            line_edit.setTextMargins(QtCore.QMargins(margin[0], margin[1], margin[2], margin[3]))
        if placeholder:
            line_edit.setPlaceholderText('%s' % placeholder)

    def setup_spin_box(self, spin_box, style=None, sPolicy=None, setMin=None, setMax=None, setStep=None, val=None, obj_name=None, align=None):
        if style:
            spin_box.setStyleSheet(style)
        if sPolicy:
            spin_box.setSizePolicy(sPolicy[0], sPolicy[1])
        if setMin:
            spin_box.setMinimum(setMin)
        if setMax:
            spin_box.setMaximum(setMax)
        if setStep:
            spin_box.setSingleStep(setStep)
        if val:
            spin_box.setValue(val)
        if align:
            spin_box.setAlignment(align)

    def setup_spin_box_double(self, d_spin_box, style=None, sPolicy=None, setMin=None, setMax=None, setStep=None, val=None, obj_name=None, align=None, w=None, deci=None):
        if style:
            d_spin_box.setStyleSheet(style)
        if sPolicy:
            d_spin_box.setSizePolicy(sPolicy[0], sPolicy[1])
        if setMin:
            d_spin_box.setMinimum(setMin)
        if setMax:
            d_spin_box.setMaximum(setMax)
        if setStep:
            d_spin_box.setSingleStep(setStep)
        if val:
            d_spin_box.setValue(val)
        if align:
            d_spin_box.setAlignment(align)
        if w:
            d_spin_box.setFixedWidth(w)
        if deci:
            d_spin_box.setDecimals(deci)

    def buKi_create_widgets(self):
        self.buKi_menuWidget = QtWidgets.QWidget()
        self.buKi_menuWidget.setFixedHeight(30)
        self.buKi_mesh_btnIcon = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_btnIcon, tip='Mesh, layout and selection tools', style=self.buKi_styleSheet, obj_name='menuIcon', iSize=30, icon=self.buKi_icon_mesh_inactive)
        self.buKi_importExport_btnIcon = QtWidgets.QPushButton()
        self.setup_button(self.buKi_importExport_btnIcon, tip='Import / Export Obj, Fbx and Abc', style=self.buKi_styleSheet, obj_name='menuIcon', iSize=30, icon=self.buKi_icon_importExport_inactive)
        self.buKi_about_btnIcon = QtWidgets.QPushButton()
        self.setup_button(self.buKi_about_btnIcon, tip='Information / Weblinks / Create Shortcuts', style=self.buKi_styleSheet, obj_name='menuIcon', iSize=30, icon=self.buKi_icon_about_inactive)
        self.buKi_stack = QtWidgets.QStackedWidget()
        self.buKi_stack.setStyleSheet('* { background-color: rgb(70,70,70);}')
        self.buKi_mesh_toolbox_header = QtWidgets.QWidget()
        self.buKi_mesh_toolbox_header.setFixedHeight(25)
        self.buKi_mesh_ui_toolboxLabel = QtWidgets.QPushButton('  Edit Mesh')
        self.setup_button(self.buKi_mesh_ui_toolboxLabel, style=self.buKi_styleSheet, obj_name='label', h=25)
        self.buKi_mesh_ui_toolboxToggle = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_ui_toolboxToggle, style=self.buKi_styleSheet, obj_name='toggle', h=25, w=25, icon=self.buKi_icon_expand)
        self.buKi_mesh_ui_toolbox_widget = QtWidgets.QWidget()
        self.buKi_mesh_ui_toolbox_widget.setVisible(False)
        self.buKi_mesh_toolbox_combine_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_toolbox_combine_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_combine_btn, tip='Advanced Combine\n\nRMB: Settings')
        self.buKi_mesh_toolbox_separate_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_separate_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_separate_btn, tip='Advanced Separate')
        self.buKi_mesh_toolbox_extract_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_extract_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_extract_btn, tip='Advanced Extract')
        self.buKi_mesh_toolbox_duplicateFace_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_duplicateFace_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_duplicateFace_btn, tip='Advanced Duplicate Face')
        self.buKi_mesh_toolbox_mirror_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_toolbox_mirror_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_mirror_btn, tip='Mirror\n\nLMB: X\n\nALT: Y\n\nCTRL: Z\n\nAdd SHIFT to Mirror from Pivot Position')
        self.buKi_mesh_toolbox_connect_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_connect_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_connect_btn, tip='Connect\n\nLMB: Connect Line\n\nALT: Connect Diamond\n\nCTRL: Connect Corner\n\nSHIFT: Connect End')
        self.buKi_mesh_toolbox_group_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_group_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_group_btn, tip='Group\n\nLMB: Add all objects to one group\n\nALT: Add each object to an individual group')
        self.buKi_mesh_toolbox_pivot_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_pivot_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_pivot_btn, tip='Modify Pivot Position\n\nLMB: Bottom\n\nALT: Front\n\nCTRL: Right\n\nAdd SHIFT for opposite position\n\nSHIFT+ALT+CTRL: Center Pivot')
        self.buKi_mesh_toolbox_append_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_append_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_append_btn, tip='Append Plus\n\nLMB: Append Poly (Vertex input)\n\nLMB: Append Bridge (Edge input)\n\nALT: Append Ring Loop (Edge input)')
        self.buKi_mesh_toolbox_quadFill_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_quadFill_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_quadFill_btn, tip='Quad Fill')
        self.buKi_mesh_toolbox_corner_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_toolbox_corner_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_corner_btn, tip='45 Mesh Angle')
        self.buKi_mesh_select_header = QtWidgets.QWidget()
        self.buKi_mesh_select_header.setFixedHeight(25)
        self.buKi_mesh_ui_selectLabel = QtWidgets.QPushButton('  Select')
        self.setup_button(self.buKi_mesh_ui_selectLabel, style=self.buKi_styleSheet, obj_name='label', h=25)
        self.buKi_mesh_ui_selectToggle = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_ui_selectToggle, style=self.buKi_styleSheet, obj_name='toggle', h=25, w=25, icon=self.buKi_icon_expand)
        self.buKi_mesh_ui_select_widget = QtWidgets.QWidget()
        self.buKi_mesh_ui_select_widget.setVisible(False)
        self.buKi_mesh_select_topology_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_topology_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_topology_btn, tip='Topology / Select by Topology\n\nALT: Toggle Poly Count Display\n\nRMB: Settings')
        self.buKi_mesh_select_angle_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_angle_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_angle_btn, tip='Angle / Grow a polygon face selection based on their edge normal angle\n\nRMB: Settings')
        self.buKi_mesh_select_nthEdge_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_nthEdge_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_nthEdge_btn, tip='Nth Edge / Select every nth edge within a Loop, Ring or Border edge.\n\nLMB: Loop\n\nALT: Ring\n\nCTRL: Border\n\nRMB: Settings')
        self.buKi_mesh_select_fillShell_btn = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_select_fillShell_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_fillShell_btn, tip='Fill Shell / Temporarily cut a mesh into selectable shells with an edge selection')
        self.buKi_mesh_select_percentage_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_percentage_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_percentage_btn, tip='Percentage / Randomly selects a specified percentage from the current object selection.\n\nRMB: Settings')
        self.buKi_mesh_select_cmptCount_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_cmptCount_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_cmptCount_btn, tip='Select by Component Count\n\nLMB: Face\n\nALT: Vertices\n\nCTRL: Edges\n\nSHIFT: UVs\n\nRMB: Settings')
        self.buKi_mesh_select_name_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_name_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_name_btn, tip='Select by Name\n\nRMB: Settings')
        self.buKi_mesh_select_type_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_select_type_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_type_btn, tip='Select by Type\n\nRMB: Settings')
        self.buKi_mesh_layout_header = QtWidgets.QWidget()
        self.buKi_mesh_layout_header.setFixedHeight(25)
        self.buKi_mesh_ui_layoutLabel = QtWidgets.QPushButton('  Layout')
        self.setup_button(self.buKi_mesh_ui_layoutLabel, style=self.buKi_styleSheet, obj_name='label', h=25)
        self.buKi_mesh_ui_layoutToggle = QtWidgets.QPushButton()
        self.setup_button(self.buKi_mesh_ui_layoutToggle, style=self.buKi_styleSheet, obj_name='toggle', h=25, w=25, icon=self.buKi_icon_expand)
        self.buKi_mesh_ui_layout_widget = QtWidgets.QWidget()
        self.buKi_mesh_ui_layout_widget.setVisible(False)
        self.buKi_mesh_layout_place_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_layout_place_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_layout_place_btn, tip='Place source objects on a target\n\nRMB: Settings')
        self.buKi_mesh_layout_paint_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_layout_paint_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_layout_paint_btn, tip='Paint source objects on a target\n\nRMB: Settings')
        self.buKi_mesh_layout_distribute_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_layout_distribute_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_layout_distribute_btn, tip='Distribute objects\n\nLMB: X\n\nALT: Y\n\nCTRL: Z\n\nAdd SHIFT for negative direction\n\nRMB: Settings')
        self.buKi_mesh_layout_duplicator_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_mesh_layout_duplicator_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_layout_duplicator_btn, tip='Duplicate objects\n\nLMB: X\n\nALT: Y\n\nCTRL: Z\n\nAdd SHIFT for negative direction\n\nRMB: Settings')
        self.buKi_mesh_combine_orientation_cb = QtWidgets.QCheckBox('Keep orientation')
        self.buKi_mesh_combine_orientation_cb.setFocusPolicy(QtCore.Qt.FocusPolicy(QtCore.Qt.ClickFocus))
        self.buKi_select_topology_triangles_rb = QtWidgets.QRadioButton('Triangles')
        self.buKi_select_topology_quads_rb = QtWidgets.QRadioButton('Quads')
        self.buKi_select_topology_ngons_rb = QtWidgets.QRadioButton('N-Gons')
        self.buKi_select_topology_ngons_rb.setChecked(True)
        self.buKi_select_topology_concave_rb = QtWidgets.QRadioButton('Concave')
        self.buKi_select_topology_lamina_rb = QtWidgets.QRadioButton('Lamina')
        self.buKi_select_topology_holes_rb = QtWidgets.QRadioButton('Holes')
        self.buKi_select_topology_manifold_rb = QtWidgets.QRadioButton('Non-Manifold')
        self.buKi_select_topology_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_triangles_rb)
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_quads_rb)
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_ngons_rb)
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_concave_rb)
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_lamina_rb)
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_holes_rb)
        self.buKi_select_topology_btnGrp.addButton(self.buKi_select_topology_manifold_rb)
        self.buKi_select_angle_dSpinBox = QtWidgets.QSpinBox()
        self.setup_spin_box(self.buKi_select_angle_dSpinBox, style=self.buKi_styleSheet, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0, setMax=180, val=15, setStep=1)
        self.buKi_select_angle_slider = QtWidgets.QSlider()
        self.buKi_select_angle_slider.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_angle_slider.setOrientation(QtCore.Qt.Horizontal)
        self.buKi_select_angle_slider.setFixedWidth(130)
        self.buKi_select_angle_slider.setMinimum(0)
        self.buKi_select_angle_slider.setMaximum(180)
        self.buKi_select_angle_slider.setValue(15)
        self.buKi_select_nthEdge_label = QtWidgets.QLabel('Select every   ')
        self.buKi_select_nthEdge_label.setFixedWidth(70)
        self.buKi_select_nthEdge_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_nthEdge_spinBox = QtWidgets.QSpinBox()
        self.setup_spin_box(self.buKi_select_nthEdge_spinBox, style=self.buKi_styleSheet, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=2, setMax=100, val=2)
        self.buKi_select_percentage_label = QtWidgets.QLabel('Percentage   ')
        self.buKi_select_percentage_label.setFixedWidth(70)
        self.buKi_select_percentage_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_percentage_spinBox = QtWidgets.QSpinBox()
        self.setup_spin_box(self.buKi_select_percentage_spinBox, style=self.buKi_styleSheet, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=1, setMax=100, val=25)
        self.buKi_select_cmptCountValues_label = QtWidgets.QLabel('Value Mode')
        self.buKi_select_cmptCountValues_label.setFixedWidth(70)
        self.buKi_select_cmptCountValues_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_cmptCountValues_qFrame = QtWidgets.QFrame()
        self.buKi_select_cmptCountValues_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_select_cmptCountValues_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_cmptCountValues_qFrame.setFixedHeight(1)
        self.buKi_select_cmptCountValues_switch_label = QtWidgets.QLabel('Switch   ')
        self.buKi_select_cmptCountValues_switch_label.setFixedWidth(70)
        self.buKi_select_cmptCountValues_switch_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_cmptCountValues_on_rb = QtWidgets.QRadioButton('On')
        self.buKi_select_cmptCountValues_off_rb = QtWidgets.QRadioButton('Off')
        self.buKi_select_cmptCountValues_off_rb.setChecked(True)
        self.buKi_select_cmptCountValues_activate_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_select_cmptCountValues_activate_btnGrp.addButton(self.buKi_select_cmptCountValues_on_rb)
        self.buKi_select_cmptCountValues_activate_btnGrp.addButton(self.buKi_select_cmptCountValues_off_rb)
        self.buKi_select_cmptCountMinMax_label = QtWidgets.QLabel('Min / Max   ')
        self.buKi_select_cmptCountMinMax_label.setFixedWidth(70)
        self.buKi_select_cmptCountMinMax_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_cmptCountMin_spinBox = QtWidgets.QSpinBox()
        self.setup_spin_box(self.buKi_select_cmptCountMin_spinBox, style=self.buKi_styleSheet, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0, setMax=99998, val=1)
        self.buKi_select_cmptCountMax_spinBox = QtWidgets.QSpinBox()
        self.setup_spin_box(self.buKi_select_cmptCountMax_spinBox, style=self.buKi_styleSheet, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=1, setMax=99999, val=1000)
        self.buKi_select_cmptCountScope_label = QtWidgets.QLabel('Value Mode Scope')
        self.buKi_select_cmptCountScope_label.setFixedWidth(105)
        self.buKi_select_cmptCountScope_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_cmptCountScope_qFrame = QtWidgets.QFrame()
        self.buKi_select_cmptCountScope_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_select_cmptCountScope_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_cmptCountScope_qFrame.setFixedHeight(1)
        self.buKi_select_cmptCountScope_scene_rb = QtWidgets.QRadioButton('Scene')
        self.buKi_select_cmptCountScope_scene_rb.setChecked(True)
        self.buKi_select_cmptCountScope_selection_rb = QtWidgets.QRadioButton('Selection')
        self.buKi_select_cmptCountScope_scene_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_select_cmptCountScope_scene_btnGrp.addButton(self.buKi_select_cmptCountScope_scene_rb)
        self.buKi_select_cmptCountScope_scene_btnGrp.addButton(self.buKi_select_cmptCountScope_selection_rb)
        self.buKi_select_nameScope_label = QtWidgets.QLabel('Scope')
        self.buKi_select_nameScope_label.setFixedWidth(55)
        self.buKi_select_nameScope_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_nameScope_qFrame = QtWidgets.QFrame()
        self.buKi_select_nameScope_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_select_nameScope_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_nameScope_qFrame.setFixedHeight(1)
        self.buKi_select_nameScope_scene_rb = QtWidgets.QRadioButton('Scene')
        self.buKi_select_nameScope_scene_rb.setChecked(True)
        self.buKi_select_nameScope_hierarchy_rb = QtWidgets.QRadioButton('Hierarchy')
        self.buKi_select_nameScope_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_select_nameScope_btnGrp.addButton(self.buKi_select_nameScope_scene_rb)
        self.buKi_select_nameScope_btnGrp.addButton(self.buKi_select_nameScope_hierarchy_rb)
        self.buKi_select_name_label = QtWidgets.QLabel('Name')
        self.buKi_select_name_label.setFixedWidth(55)
        self.buKi_select_name_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_name_qFrame = QtWidgets.QFrame()
        self.buKi_select_name_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_select_name_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_name_qFrame.setFixedHeight(1)
        self.buKi_select_name_lineEdit = QtWidgets.QLineEdit()
        self.buKi_select_name_lineEdit.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_typeScope_label = QtWidgets.QLabel('Scope')
        self.buKi_select_typeScope_label.setFixedWidth(55)
        self.buKi_select_typeScope_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_typeScope_qFrame = QtWidgets.QFrame()
        self.buKi_select_typeScope_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_select_typeScope_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_typeScope_qFrame.setFixedHeight(1)
        self.buKi_select_typeScope_scene_rb = QtWidgets.QRadioButton('Scene')
        self.buKi_select_typeScope_scene_rb.setChecked(True)
        self.buKi_select_typeScope_hierarchy_rb = QtWidgets.QRadioButton('Hierarchy')
        self.buKi_select_typeScope_scene_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_select_typeScope_scene_btnGrp.addButton(self.buKi_select_typeScope_scene_rb)
        self.buKi_select_typeScope_scene_btnGrp.addButton(self.buKi_select_typeScope_hierarchy_rb)
        self.buKi_select_type_label = QtWidgets.QLabel('Type')
        self.buKi_select_type_label.setFixedWidth(55)
        self.buKi_select_type_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_select_type_qFrame = QtWidgets.QFrame()
        self.buKi_select_type_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_select_type_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_select_type_qFrame.setFixedHeight(1)
        self.buKi_select_type_group_rb = QtWidgets.QRadioButton('Group')
        self.buKi_select_type_group_rb.setChecked(True)
        self.buKi_select_type_geometry_rb = QtWidgets.QRadioButton('Geometry')
        self.buKi_select_type_curve_rb = QtWidgets.QRadioButton('Curve')
        self.buKi_select_type_light_rb = QtWidgets.QRadioButton('Light')
        self.buKi_select_type_locator_rb = QtWidgets.QRadioButton('Locator')
        self.buKi_select_type_camera_rb = QtWidgets.QRadioButton('Camera')
        self.buKi_select_type_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_select_type_btnGrp.addButton(self.buKi_select_type_group_rb)
        self.buKi_select_type_btnGrp.addButton(self.buKi_select_type_geometry_rb)
        self.buKi_select_type_btnGrp.addButton(self.buKi_select_type_curve_rb)
        self.buKi_select_type_btnGrp.addButton(self.buKi_select_type_light_rb)
        self.buKi_select_type_btnGrp.addButton(self.buKi_select_type_locator_rb)
        self.buKi_select_type_btnGrp.addButton(self.buKi_select_type_camera_rb)
        self.buKi_mesh_place_add_source_btn = QtWidgets.QPushButton('Add')
        self.setup_button(self.buKi_mesh_place_add_source_btn, style=self.buKi_styleSheet, tip='Add source object(s)')
        self.buKi_mesh_place_clear_source_btn = QtWidgets.QPushButton('Clear')
        self.setup_button(self.buKi_mesh_place_clear_source_btn, style=self.buKi_styleSheet, tip='Clear list')
        self.buKi_mesh_place_source_list = QListWidget_Custom('')
        self.buKi_mesh_place_source_list.setStyleSheet(self.buKi_styleSheet)
        self.buKi_mesh_place_source_list.setFixedHeight(100)
        self.buKi_mesh_place_source_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.buKi_mesh_place_random_cb = QtWidgets.QCheckBox('Random')
        self.buKi_mesh_paint_add_source_btn = QtWidgets.QPushButton('Add')
        self.setup_button(self.buKi_mesh_paint_add_source_btn, style=self.buKi_styleSheet, tip='Add source object(s)')
        self.buKi_mesh_paint_clear_source_btn = QtWidgets.QPushButton('Clear')
        self.setup_button(self.buKi_mesh_paint_clear_source_btn, style=self.buKi_styleSheet, tip='Clear list')
        self.buKi_mesh_paint_source_list = QListWidget_Custom('')
        self.buKi_mesh_paint_source_list.setStyleSheet(self.buKi_styleSheet)
        self.buKi_mesh_paint_source_list.setFixedHeight(100)
        self.buKi_mesh_paint_source_list.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.buKi_mesh_paint_time_label = QtWidgets.QLabel('Time  ')
        self.buKi_mesh_paint_time_label.setFixedWidth(30)
        self.buKi_mesh_paint_time_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_paint_time_dSpinBox = QtWidgets.QDoubleSpinBox()
        self.setup_spin_box_double(self.buKi_mesh_paint_time_dSpinBox, style=self.buKi_styleSheet, deci=2, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0.01, setMax=0.2, val=0.1, setStep=0.01, w=60)
        self.buKi_mesh_paint_random_cb = QtWidgets.QCheckBox('Random')
        self.buKi_mesh_distribute_moveBy_label = QtWidgets.QLabel('Move by   ')
        self.buKi_mesh_distribute_moveBy_label.setFixedWidth(55)
        self.buKi_mesh_distribute_moveBy_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_distribute_bb_rb = QtWidgets.QRadioButton('BBox')
        self.buKi_mesh_distribute_bb_rb.setChecked(True)
        self.buKi_mesh_distribute_value_rb = QtWidgets.QRadioButton('Value')
        self.buKi_mesh_distribute_spacing_label = QtWidgets.QLabel('Spacing  ')
        self.buKi_mesh_distribute_spacing_label.setFixedWidth(70)
        self.buKi_mesh_distribute_spacing_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_distribute_spacing_dSpinBox = QtWidgets.QDoubleSpinBox()
        self.setup_spin_box_double(self.buKi_mesh_distribute_spacing_dSpinBox, style=self.buKi_styleSheet, deci=3, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0.0, setMax=9999.999, val=0.0, setStep=0.1)
        self.buKi_mesh_distribute_moveValue_label = QtWidgets.QLabel('Move value  ')
        self.buKi_mesh_distribute_moveValue_label.setFixedWidth(70)
        self.buKi_mesh_distribute_moveValue_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_distribute_moveValue_dSpinBox = QtWidgets.QDoubleSpinBox()
        self.setup_spin_box_double(self.buKi_mesh_distribute_moveValue_dSpinBox, style=self.buKi_styleSheet, deci=3, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0.0, setMax=9999.999, val=1.0, setStep=0.1)
        self.buKi_mesh_duplicator_direction_label = QtWidgets.QLabel('Direction')
        self.buKi_mesh_duplicator_direction_label.setFixedWidth(55)
        self.buKi_mesh_duplicator_direction_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_duplicator_direction_qFrame = QtWidgets.QFrame()
        self.buKi_mesh_duplicator_direction_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_mesh_duplicator_direction_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_mesh_duplicator_direction_qFrame.setFixedHeight(1)
        self.buKi_mesh_duplicator_direction_cb = QtWidgets.QCheckBox('Manipulator (Objects only)')
        self.buKi_mesh_duplicator_moveBy_label = QtWidgets.QLabel('Move by')
        self.buKi_mesh_duplicator_moveBy_label.setFixedWidth(55)
        self.buKi_mesh_duplicator_moveBy_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_duplicator_moveBy_qFrame = QtWidgets.QFrame()
        self.buKi_mesh_duplicator_moveBy_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_mesh_duplicator_moveBy_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_mesh_duplicator_moveBy_qFrame.setFixedHeight(1)
        self.buKi_mesh_duplicator_bb_rb = QtWidgets.QRadioButton('Bounding Box')
        self.buKi_mesh_duplicator_bb_rb.setFixedWidth(110)
        self.buKi_mesh_duplicator_bb_rb.setChecked(True)
        self.buKi_mesh_duplicator_value_rb = QtWidgets.QRadioButton('Value')
        self.buKi_mesh_duplicator_copies_label = QtWidgets.QLabel('Copies  ')
        self.buKi_mesh_duplicator_copies_label.setFixedWidth(70)
        self.buKi_mesh_duplicator_copies_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_duplicator_copies_spinBox = QtWidgets.QSpinBox()
        self.setup_spin_box(self.buKi_mesh_duplicator_copies_spinBox, style=self.buKi_styleSheet, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=1, setMax=1000, val=1)
        self.buKi_mesh_duplicator_spacing_label = QtWidgets.QLabel('Spacing  ')
        self.buKi_mesh_duplicator_spacing_label.setFixedWidth(70)
        self.buKi_mesh_duplicator_spacing_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_duplicator_spacing_dSpinBox = QtWidgets.QDoubleSpinBox()
        self.setup_spin_box_double(self.buKi_mesh_duplicator_spacing_dSpinBox, style=self.buKi_styleSheet, deci=3, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0.0, setMax=9999.999, val=1.0, setStep=0.1)
        self.buKi_mesh_duplicator_moveValue_label = QtWidgets.QLabel('Move value  ')
        self.buKi_mesh_duplicator_moveValue_label.setFixedWidth(70)
        self.buKi_mesh_duplicator_moveValue_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_mesh_duplicator_moveValue_dSpinBox = QtWidgets.QDoubleSpinBox()
        self.setup_spin_box_double(self.buKi_mesh_duplicator_moveValue_dSpinBox, style=self.buKi_styleSheet, deci=3, sPolicy=[QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed], setMin=0.0, setMax=9999.999, val=1.0, setStep=0.1)
        self.buKi_mesh_settings_combine = QtWidgets.QWidget()
        self.buKi_mesh_settings_mirror = QtWidgets.QWidget()
        self.buKi_select_settings_topology = QtWidgets.QWidget()
        self.buKi_select_settings_angle = QtWidgets.QWidget()
        self.buKi_select_settings_nthEdge = QtWidgets.QWidget()
        self.buKi_select_settings_percentage = QtWidgets.QWidget()
        self.buKi_select_settings_cmptCount = QtWidgets.QWidget()
        self.buKi_select_settings_name = QtWidgets.QWidget()
        self.buKi_select_settings_type = QtWidgets.QWidget()
        self.buKi_mesh_settings_place = QtWidgets.QWidget()
        self.buKi_mesh_settings_paint = QtWidgets.QWidget()
        self.buKi_mesh_settings_distribute = QtWidgets.QWidget()
        self.buKi_mesh_settings_duplicator = QtWidgets.QWidget()
        self.buKi_mesh_settings_stack = QtWidgets.QStackedWidget()
        self.buKi_mesh_settings_stack.setStyleSheet('* { background-color: rgb(55,55,55); border: none;}')
        self.buKi_mesh_settings_stack.setMinimumHeight(30)
        self.buKi_mesh_settings_stack.setContentsMargins(0, 5, 0, 0)
        self.buKi_mesh_settings_stack.setVisible(False)
        self.buKi_mesh_widget_lib = [
         self.buKi_mesh_ui_toolbox_widget, self.buKi_mesh_ui_layout_widget, self.buKi_mesh_ui_select_widget]
        self.buKi_mesh_toggle_lib = [self.buKi_mesh_ui_toolboxToggle, self.buKi_mesh_ui_layoutToggle, self.buKi_mesh_ui_selectToggle]
        self.buKi_import_header = QtWidgets.QWidget()
        self.buKi_import_header.setFixedHeight(25)
        self.buKi_import_label = QtWidgets.QPushButton('  Import')
        self.setup_button(self.buKi_import_label, style=self.buKi_styleSheet, obj_name='label', h=25)
        self.buKi_import_toggle = QtWidgets.QPushButton()
        self.setup_button(self.buKi_import_toggle, style=self.buKi_styleSheet, obj_name='toggle', icon=self.buKi_icon_expand, h=25, w=25)
        self.buKi_importExport_import_widget = QtWidgets.QWidget()
        self.buKi_importExport_import_widget.setVisible(False)
        self.buKi_obj_import_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_obj_import_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_import_obj_btn, tip='Import .obj files\n\nRMB: Settings')
        self.buKi_fbx_import_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_fbx_import_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_import_fbx_btn, tip='Import .fbx files')
        self.buKi_abc_import_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_abc_import_btn, style=self.buKi_styleSheet, obj_name='icon', iSize=40, icon=self.buKi_icon_import_abc_btn, tip='Import .abc files')
        self.buKi_placeholder_import_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_placeholder_import_btn, style=self.buKi_styleSheet, obj_name='placeholder', iSize=40, tip='')
        self.buKi_export_header = QtWidgets.QWidget()
        self.buKi_export_header.setFixedHeight(25)
        self.buKi_export_label = QtWidgets.QPushButton('  Export')
        self.setup_button(self.buKi_export_label, style=self.buKi_styleSheet, obj_name='label', h=25)
        self.buKi_export_toggle = QtWidgets.QPushButton()
        self.setup_button(self.buKi_export_toggle, style=self.buKi_styleSheet, obj_name='toggle', icon=self.buKi_icon_expand, h=25, w=25)
        self.buKi_importExport_export_widget = QtWidgets.QWidget()
        self.buKi_importExport_export_widget.setVisible(False)
        self.buKi_obj_export_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_obj_export_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_export_obj_btn, tip='Export .obj files\n\nRMB: Settings')
        self.buKi_fbx_export_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_fbx_export_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_export_fbx_btn, tip='Export .fbx files\n\nRMB: Settings')
        self.buKi_abc_export_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_abc_export_btn, style=self.buKi_styleSheet, obj_name='iconSettings', iSize=40, icon=self.buKi_icon_export_abc_btn, tip='Export .abc files\n\nRMB: Settings')
        self.buKi_placeholder_export_btn = QPushButton_Custom('')
        self.setup_button(self.buKi_placeholder_export_btn, style=self.buKi_styleSheet, obj_name='placeholder', iSize=40, tip='')
        self.buKi_import_obj_combined_rb = QtWidgets.QRadioButton('Combined')
        self.buKi_import_obj_separate_rb = QtWidgets.QRadioButton('Separate files')
        self.buKi_import_obj_separate_rb.setChecked(True)
        self.buKi_import_obj_blendshapes_rb = QtWidgets.QRadioButton('As blendshapes')
        self.buKi_export_obj_combined_rb = QtWidgets.QRadioButton('Combined')
        self.buKi_export_obj_separate_rb = QtWidgets.QRadioButton('Separate files')
        self.buKi_export_obj_separate_rb.setChecked(True)
        self.buKi_export_obj_blendshapes_rb = QtWidgets.QRadioButton('Blendshapes')
        self.buKi_export_options_label = QtWidgets.QLabel('Options')
        self.buKi_export_options_label.setFixedWidth(60)
        self.buKi_export_options_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_export_options_qFrame = QtWidgets.QFrame()
        self.buKi_export_options_qFrame.setFrameShape(QtWidgets.QFrame.HLine)
        self.buKi_export_options_qFrame.setStyleSheet(self.buKi_styleSheet)
        self.buKi_export_options_qFrame.setFixedHeight(1)
        self.buKi_export_options_groups_label = QtWidgets.QLabel('Groups   ')
        self.buKi_export_options_groups_label.setFixedWidth(90)
        self.buKi_export_options_groups_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_export_options_groups_on_rb = QtWidgets.QRadioButton('On')
        self.buKi_export_options_groups_on_rb.setFixedWidth(50)
        self.buKi_export_options_groups_off_rb = QtWidgets.QRadioButton('Off')
        self.buKi_export_options_groups_off_rb.setChecked(True)
        self.buKi_export_options_groups_activate_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_export_options_groups_activate_btnGrp.addButton(self.buKi_export_options_groups_on_rb)
        self.buKi_export_options_groups_activate_btnGrp.addButton(self.buKi_export_options_groups_off_rb)
        self.buKi_export_options_pointGroups_label = QtWidgets.QLabel('Point Groups   ')
        self.buKi_export_options_pointGroups_label.setFixedWidth(90)
        self.buKi_export_options_pointGroups_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_export_options_pointGroups_on_rb = QtWidgets.QRadioButton('On')
        self.buKi_export_options_pointGroups_on_rb.setFixedWidth(50)
        self.buKi_export_options_pointGroups_off_rb = QtWidgets.QRadioButton('Off')
        self.buKi_export_options_pointGroups_off_rb.setChecked(True)
        self.buKi_export_options_pointGroups_activate_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_export_options_pointGroups_activate_btnGrp.addButton(self.buKi_export_options_pointGroups_on_rb)
        self.buKi_export_options_pointGroups_activate_btnGrp.addButton(self.buKi_export_options_pointGroups_off_rb)
        self.buKi_export_options_materials_label = QtWidgets.QLabel('Materials   ')
        self.buKi_export_options_materials_label.setFixedWidth(90)
        self.buKi_export_options_materials_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_export_options_materials_on_rb = QtWidgets.QRadioButton('On')
        self.buKi_export_options_materials_on_rb.setFixedWidth(50)
        self.buKi_export_options_materials_off_rb = QtWidgets.QRadioButton('Off')
        self.buKi_export_options_materials_off_rb.setChecked(True)
        self.buKi_export_options_materials_activate_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_export_options_materials_activate_btnGrp.addButton(self.buKi_export_options_materials_on_rb)
        self.buKi_export_options_materials_activate_btnGrp.addButton(self.buKi_export_options_materials_off_rb)
        self.buKi_export_options_smoothing_label = QtWidgets.QLabel('Smoothing   ')
        self.buKi_export_options_smoothing_label.setFixedWidth(90)
        self.buKi_export_options_smoothing_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_export_options_smoothing_on_rb = QtWidgets.QRadioButton('On')
        self.buKi_export_options_smoothing_on_rb.setFixedWidth(50)
        self.buKi_export_options_smoothing_off_rb = QtWidgets.QRadioButton('Off')
        self.buKi_export_options_smoothing_off_rb.setChecked(True)
        self.buKi_export_options_smoothing_activate_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_export_options_smoothing_activate_btnGrp.addButton(self.buKi_export_options_smoothing_on_rb)
        self.buKi_export_options_smoothing_activate_btnGrp.addButton(self.buKi_export_options_smoothing_off_rb)
        self.buKi_export_options_normals_label = QtWidgets.QLabel('Normals   ')
        self.buKi_export_options_normals_label.setFixedWidth(90)
        self.buKi_export_options_normals_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.buKi_export_options_normals_on_rb = QtWidgets.QRadioButton('On')
        self.buKi_export_options_normals_on_rb.setFixedWidth(50)
        self.buKi_export_options_normals_off_rb = QtWidgets.QRadioButton('Off')
        self.buKi_export_options_normals_off_rb.setChecked(True)
        self.buKi_export_options_normals_activate_btnGrp = QtWidgets.QButtonGroup()
        self.buKi_export_options_normals_activate_btnGrp.addButton(self.buKi_export_options_normals_on_rb)
        self.buKi_export_options_normals_activate_btnGrp.addButton(self.buKi_export_options_normals_off_rb)
        self.buKi_export_fbx_single_rb = QtWidgets.QRadioButton('Single file')
        self.buKi_export_fbx_separate_rb = QtWidgets.QRadioButton('Separate files')
        self.buKi_export_fbx_separate_rb.setChecked(True)
        self.buKi_export_abc_single_rb = QtWidgets.QRadioButton('Single file')
        self.buKi_export_abc_separate_rb = QtWidgets.QRadioButton('Separate files')
        self.buKi_export_abc_separate_rb.setChecked(True)
        self.buKi_export_abc_startFrame_label = QtWidgets.QLabel('Start')
        self.buKi_export_abc_startFrame_label.setFixedWidth(24)
        self.buKi_export_abc_startFrame_spinBox = QtWidgets.QSpinBox()
        self.buKi_export_abc_startFrame_spinBox.setFixedWidth(55)
        self.buKi_export_abc_startFrame_spinBox.setStyleSheet(self.buKi_styleSheet)
        self.buKi_export_abc_startFrame_spinBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.buKi_export_abc_startFrame_spinBox.setMinimum(0)
        self.buKi_export_abc_startFrame_spinBox.setMaximum(9999)
        self.buKi_export_abc_startFrame_spinBox.setValue(1001)
        self.buKi_export_abc_endFrame_label = QtWidgets.QLabel('End')
        self.buKi_export_abc_endFrame_label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.buKi_export_abc_endFrame_label.setFixedWidth(27)
        self.buKi_export_abc_endFrame_spinBox = QtWidgets.QSpinBox()
        self.buKi_export_abc_endFrame_spinBox.setFixedWidth(55)
        self.buKi_export_abc_endFrame_spinBox.setStyleSheet(self.buKi_styleSheet)
        self.buKi_export_abc_endFrame_spinBox.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.buKi_export_abc_endFrame_spinBox.setMinimum(0)
        self.buKi_export_abc_endFrame_spinBox.setMaximum(9999)
        self.buKi_export_abc_endFrame_spinBox.setValue(1001)
        self.buKi_import_settings_obj = QtWidgets.QWidget()
        self.buKi_import_settings_fbx = QtWidgets.QWidget()
        self.buKi_import_settings_abc = QtWidgets.QWidget()
        self.buKi_export_settings_obj = QtWidgets.QWidget()
        self.buKi_export_settings_fbx = QtWidgets.QWidget()
        self.buKi_export_settings_abc = QtWidgets.QWidget()
        self.buKi_importExport_settings_stack = QtWidgets.QStackedWidget()
        self.buKi_importExport_settings_stack.setStyleSheet('* { background-color: rgb(55,55,55); border: none;}')
        self.buKi_importExport_settings_stack.setMinimumHeight(30)
        self.buKi_importExport_settings_stack.setContentsMargins(0, 5, 0, 0)
        self.buKi_importExport_settings_stack.setVisible(False)
        self.buKi_importExport_widget_lib = [
         self.buKi_importExport_import_widget, self.buKi_importExport_export_widget]
        self.buKi_importExport_toggle_lib = [self.buKi_import_toggle, self.buKi_export_toggle]
        self.buKi_about_toolTitle = QtWidgets.QLabel()
        self.buKi_about_toolTitle.setPixmap(self.buKi_img_about_header)
        self.buKi_about_toolTitle.setFixedSize(196, 90)
        self.buKi_about_version = QtWidgets.QLabel(self)
        self.buKi_about_version.setText('Version 1.0.5')
        self.buKi_about_version.setStyleSheet('* { color: rgb(255,255,255); border: none;}')
        self.buKi_about_author = QtWidgets.QLabel(self)
        self.buKi_about_author.setText('Author: Erik Lehmann')
        self.buKi_about_author.setStyleSheet('* { color: rgb(255,255,255); border: none;}')
        self.buKi_about_email = QtWidgets.QLabel(self)
        self.buKi_about_email.setText('Email: hello@rocket-square.com')
        self.buKi_about_email.setStyleSheet('* { color: rgb(255,255,255); border: none;}')
        self.buKi_about_copyright = QtWidgets.QLabel(self)
        self.buKi_about_copyright.setText('Copyright (C) 2020 Rocket Square.\nAll Rights Reserved.')
        self.buKi_about_copyright.setStyleSheet('* { color: rgb(255,255,255); border: none;}')
        self.buKi_about_documentation_btn = QtWidgets.QPushButton('Online Documentation')
        self.buKi_about_documentation_btn.setStyleSheet(self.buKi_styleSheet)
        self.buKi_about_documentation_btn.setFixedHeight(30)
        self.buKi_about_website_btn = QtWidgets.QPushButton('Website')
        self.buKi_about_website_btn.setStyleSheet(self.buKi_styleSheet)
        self.buKi_about_website_btn.setFixedHeight(30)
        self.buKi_about_gumroad_btn = QtWidgets.QPushButton('Gumroad')
        self.buKi_about_gumroad_btn.setStyleSheet(self.buKi_styleSheet)
        self.buKi_about_gumroad_btn.setFixedHeight(30)
        self.buKi_about_shortcuts_btn = QtWidgets.QPushButton('Create Hotkey Shortcuts')
        self.buKi_about_shortcuts_btn.setStyleSheet(self.buKi_styleSheet)
        self.buKi_about_shortcuts_btn.setFixedHeight(30)

    def buKi_create_layouts(self):
        buKi_menu_layout = QtWidgets.QHBoxLayout()
        buKi_menu_layout.setContentsMargins(0, 0, 0, 0)
        buKi_menu_layout.addWidget(self.buKi_mesh_btnIcon)
        buKi_menu_layout.addWidget(self.buKi_importExport_btnIcon)
        buKi_menu_layout.addStretch()
        buKi_menu_layout.addWidget(self.buKi_about_btnIcon)
        buKi_menu_layout.setSpacing(0)
        self.buKi_menuWidget.setLayout(buKi_menu_layout)
        mesh_toolbox_header_layout = QtWidgets.QHBoxLayout()
        mesh_toolbox_header_layout.setContentsMargins(0, 0, 0, 0)
        mesh_toolbox_header_layout.setSpacing(0)
        mesh_toolbox_header_layout.addWidget(self.buKi_mesh_ui_toolboxLabel)
        mesh_toolbox_header_layout.addWidget(self.buKi_mesh_ui_toolboxToggle)
        self.buKi_mesh_toolbox_header.setLayout(mesh_toolbox_header_layout)
        mesh_toolbox_layout = QtWidgets.QGridLayout()
        mesh_toolbox_layout.setContentsMargins(0, 0, 0, 0)
        mesh_toolbox_layout.setSpacing(2)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_extract_btn, 0, 0)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_duplicateFace_btn, 0, 1)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_connect_btn, 0, 2)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_append_btn, 0, 3)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_combine_btn, 1, 0)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_separate_btn, 1, 1)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_mirror_btn, 1, 2)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_pivot_btn, 1, 3)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_group_btn, 2, 0)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_quadFill_btn, 2, 1)
        mesh_toolbox_layout.addWidget(self.buKi_mesh_toolbox_corner_btn, 2, 2)
        self.buKi_mesh_ui_toolbox_widget.setLayout(mesh_toolbox_layout)
        mesh_layout_header_layout = QtWidgets.QHBoxLayout()
        mesh_layout_header_layout.setContentsMargins(0, 0, 0, 0)
        mesh_layout_header_layout.setSpacing(0)
        mesh_layout_header_layout.addWidget(self.buKi_mesh_ui_layoutLabel)
        mesh_layout_header_layout.addWidget(self.buKi_mesh_ui_layoutToggle)
        self.buKi_mesh_layout_header.setLayout(mesh_layout_header_layout)
        mesh_layout_layout = QtWidgets.QGridLayout()
        mesh_layout_layout.setContentsMargins(2, 0, 2, 0)
        mesh_layout_layout.setSpacing(2)
        mesh_layout_layout.addWidget(self.buKi_mesh_layout_place_btn, 0, 0)
        mesh_layout_layout.addWidget(self.buKi_mesh_layout_paint_btn, 0, 1)
        mesh_layout_layout.addWidget(self.buKi_mesh_layout_distribute_btn, 0, 2)
        mesh_layout_layout.addWidget(self.buKi_mesh_layout_duplicator_btn, 0, 3)
        self.buKi_mesh_ui_layout_widget.setLayout(mesh_layout_layout)
        mesh_select_header_layout = QtWidgets.QHBoxLayout()
        mesh_select_header_layout.setContentsMargins(0, 0, 0, 0)
        mesh_select_header_layout.setSpacing(0)
        mesh_select_header_layout.addWidget(self.buKi_mesh_ui_selectLabel)
        mesh_select_header_layout.addWidget(self.buKi_mesh_ui_selectToggle)
        self.buKi_mesh_select_header.setLayout(mesh_select_header_layout)
        mesh_select_layout = QtWidgets.QGridLayout()
        mesh_select_layout.setContentsMargins(2, 0, 2, 0)
        mesh_select_layout.setSpacing(2)
        mesh_select_layout.addWidget(self.buKi_mesh_select_topology_btn, 0, 0)
        mesh_select_layout.addWidget(self.buKi_mesh_select_angle_btn, 0, 1)
        mesh_select_layout.addWidget(self.buKi_mesh_select_nthEdge_btn, 0, 2)
        mesh_select_layout.addWidget(self.buKi_mesh_select_fillShell_btn, 0, 3)
        mesh_select_layout.addWidget(self.buKi_mesh_select_percentage_btn, 1, 0)
        mesh_select_layout.addWidget(self.buKi_mesh_select_cmptCount_btn, 1, 1)
        mesh_select_layout.addWidget(self.buKi_mesh_select_name_btn, 1, 2)
        mesh_select_layout.addWidget(self.buKi_mesh_select_type_btn, 1, 3)
        self.buKi_mesh_ui_select_widget.setLayout(mesh_select_layout)
        mesh_combine_layout = QtWidgets.QVBoxLayout()
        mesh_combine_layout.setContentsMargins(10, 0, 2, 0)
        mesh_combine_layout.setSpacing(2)
        mesh_combine_layout.addWidget(self.buKi_mesh_combine_orientation_cb)
        mesh_select_topology = QtWidgets.QGridLayout()
        mesh_select_topology.setContentsMargins(10, 0, 2, 2)
        mesh_select_topology.setSpacing(4)
        mesh_select_topology.addWidget(self.buKi_select_topology_triangles_rb, 0, 0)
        mesh_select_topology.addWidget(self.buKi_select_topology_quads_rb, 0, 1)
        mesh_select_topology.addWidget(self.buKi_select_topology_ngons_rb, 1, 0)
        mesh_select_topology.addWidget(self.buKi_select_topology_concave_rb, 1, 1)
        mesh_select_topology.addWidget(self.buKi_select_topology_lamina_rb, 2, 0)
        mesh_select_topology.addWidget(self.buKi_select_topology_holes_rb, 2, 1)
        mesh_select_topology.addWidget(self.buKi_select_topology_manifold_rb, 3, 0)
        mesh_select_angle = QtWidgets.QHBoxLayout()
        mesh_select_angle.setContentsMargins(8, 0, 8, 4)
        mesh_select_angle.setSpacing(2)
        mesh_select_angle.addWidget(self.buKi_select_angle_dSpinBox)
        mesh_select_angle.addWidget(self.buKi_select_angle_slider)
        mesh_select_nthEdge = QtWidgets.QHBoxLayout()
        mesh_select_nthEdge.setContentsMargins(8, 0, 8, 4)
        mesh_select_nthEdge.setSpacing(2)
        mesh_select_nthEdge.addWidget(self.buKi_select_nthEdge_label)
        mesh_select_nthEdge.addWidget(self.buKi_select_nthEdge_spinBox)
        mesh_select_percentage = QtWidgets.QHBoxLayout()
        mesh_select_percentage.setContentsMargins(8, 0, 8, 4)
        mesh_select_percentage.setSpacing(2)
        mesh_select_percentage.addWidget(self.buKi_select_percentage_label)
        mesh_select_percentage.addWidget(self.buKi_select_percentage_spinBox)
        mesh_select_cmptCount_mode_separator = QtWidgets.QHBoxLayout()
        mesh_select_cmptCount_mode_separator.setContentsMargins(2, 0, 2, 0)
        mesh_select_cmptCount_mode_separator.setSpacing(2)
        mesh_select_cmptCount_mode_separator.addWidget(self.buKi_select_cmptCountValues_label)
        mesh_select_cmptCount_mode_separator.addWidget(self.buKi_select_cmptCountValues_qFrame)
        mesh_select_cmptCount_switch = QtWidgets.QHBoxLayout()
        mesh_select_cmptCount_switch.setContentsMargins(8, 0, 8, 4)
        mesh_select_cmptCount_switch.setSpacing(2)
        mesh_select_cmptCount_switch.addWidget(self.buKi_select_cmptCountValues_switch_label)
        mesh_select_cmptCount_switch.addWidget(self.buKi_select_cmptCountValues_on_rb)
        mesh_select_cmptCount_switch.addWidget(self.buKi_select_cmptCountValues_off_rb)
        mesh_select_cmptCount_MinMax = QtWidgets.QHBoxLayout()
        mesh_select_cmptCount_MinMax.setContentsMargins(8, 0, 8, 4)
        mesh_select_cmptCount_MinMax.setSpacing(2)
        mesh_select_cmptCount_MinMax.addWidget(self.buKi_select_cmptCountMinMax_label)
        mesh_select_cmptCount_MinMax.addWidget(self.buKi_select_cmptCountMin_spinBox)
        mesh_select_cmptCount_MinMax.addWidget(self.buKi_select_cmptCountMax_spinBox)
        mesh_select_cmptCount_scope_separator = QtWidgets.QHBoxLayout()
        mesh_select_cmptCount_scope_separator.setContentsMargins(2, 0, 2, 0)
        mesh_select_cmptCount_scope_separator.setSpacing(2)
        mesh_select_cmptCount_scope_separator.addWidget(self.buKi_select_cmptCountScope_label)
        mesh_select_cmptCount_scope_separator.addWidget(self.buKi_select_cmptCountScope_qFrame)
        mesh_select_cmptCount_scope_options = QtWidgets.QHBoxLayout()
        mesh_select_cmptCount_scope_options.setContentsMargins(10, 0, 2, 0)
        mesh_select_cmptCount_scope_options.setSpacing(2)
        mesh_select_cmptCount_scope_options.addWidget(self.buKi_select_cmptCountScope_scene_rb)
        mesh_select_cmptCount_scope_options.addWidget(self.buKi_select_cmptCountScope_selection_rb)
        mesh_select_cmptCount = QtWidgets.QVBoxLayout()
        mesh_select_cmptCount.setContentsMargins(8, 2, 8, 0)
        mesh_select_cmptCount.setSpacing(8)
        mesh_select_cmptCount.addLayout(mesh_select_cmptCount_mode_separator)
        mesh_select_cmptCount.addLayout(mesh_select_cmptCount_switch)
        mesh_select_cmptCount.addLayout(mesh_select_cmptCount_MinMax)
        mesh_select_cmptCount.addLayout(mesh_select_cmptCount_scope_separator)
        mesh_select_cmptCount.addLayout(mesh_select_cmptCount_scope_options)
        mesh_select_cmptCount.addStretch()
        mesh_select_name_scope_separator = QtWidgets.QHBoxLayout()
        mesh_select_name_scope_separator.setContentsMargins(2, 0, 2, 0)
        mesh_select_name_scope_separator.setSpacing(2)
        mesh_select_name_scope_separator.addWidget(self.buKi_select_nameScope_label)
        mesh_select_name_scope_separator.addWidget(self.buKi_select_nameScope_qFrame)
        mesh_select_name_scope_options = QtWidgets.QHBoxLayout()
        mesh_select_name_scope_options.setContentsMargins(10, 0, 2, 0)
        mesh_select_name_scope_options.setSpacing(2)
        mesh_select_name_scope_options.addWidget(self.buKi_select_nameScope_scene_rb)
        mesh_select_name_scope_options.addWidget(self.buKi_select_nameScope_hierarchy_rb)
        mesh_select_name_search_separator = QtWidgets.QHBoxLayout()
        mesh_select_name_search_separator.setContentsMargins(2, 0, 2, 0)
        mesh_select_name_search_separator.setSpacing(2)
        mesh_select_name_search_separator.addWidget(self.buKi_select_name_label)
        mesh_select_name_search_separator.addWidget(self.buKi_select_name_qFrame)
        mesh_select_name_search_options = QtWidgets.QHBoxLayout()
        mesh_select_name_search_options.setContentsMargins(10, 0, 2, 0)
        mesh_select_name_search_options.setSpacing(2)
        mesh_select_name_search_options.addWidget(self.buKi_select_name_lineEdit)
        mesh_select_name = QtWidgets.QVBoxLayout()
        mesh_select_name.setContentsMargins(8, 2, 8, 0)
        mesh_select_name.setSpacing(8)
        mesh_select_name.addLayout(mesh_select_name_scope_separator)
        mesh_select_name.addLayout(mesh_select_name_scope_options)
        mesh_select_name.addLayout(mesh_select_name_search_separator)
        mesh_select_name.addLayout(mesh_select_name_search_options)
        mesh_select_name.addStretch()
        mesh_select_type_scope_separator = QtWidgets.QHBoxLayout()
        mesh_select_type_scope_separator.setContentsMargins(2, 0, 2, 0)
        mesh_select_type_scope_separator.setSpacing(2)
        mesh_select_type_scope_separator.addWidget(self.buKi_select_typeScope_label)
        mesh_select_type_scope_separator.addWidget(self.buKi_select_typeScope_qFrame)
        mesh_select_type_scope_options = QtWidgets.QHBoxLayout()
        mesh_select_type_scope_options.setContentsMargins(10, 0, 2, 0)
        mesh_select_type_scope_options.setSpacing(2)
        mesh_select_type_scope_options.addWidget(self.buKi_select_typeScope_scene_rb)
        mesh_select_type_scope_options.addWidget(self.buKi_select_typeScope_hierarchy_rb)
        mesh_select_type_separator = QtWidgets.QHBoxLayout()
        mesh_select_type_separator.setContentsMargins(2, 0, 2, 0)
        mesh_select_type_separator.setSpacing(2)
        mesh_select_type_separator.addWidget(self.buKi_select_type_label)
        mesh_select_type_separator.addWidget(self.buKi_select_type_qFrame)
        mesh_select_type_options = QtWidgets.QGridLayout()
        mesh_select_type_options.setContentsMargins(10, 0, 2, 0)
        mesh_select_type_options.setSpacing(8)
        mesh_select_type_options.addWidget(self.buKi_select_type_group_rb, 0, 0)
        mesh_select_type_options.addWidget(self.buKi_select_type_geometry_rb, 0, 1)
        mesh_select_type_options.addWidget(self.buKi_select_type_curve_rb, 1, 0)
        mesh_select_type_options.addWidget(self.buKi_select_type_light_rb, 1, 1)
        mesh_select_type_options.addWidget(self.buKi_select_type_locator_rb, 2, 0)
        mesh_select_type_options.addWidget(self.buKi_select_type_camera_rb, 2, 1)
        mesh_select_type = QtWidgets.QVBoxLayout()
        mesh_select_type.setContentsMargins(8, 2, 8, 0)
        mesh_select_type.setSpacing(8)
        mesh_select_type.addLayout(mesh_select_type_scope_separator)
        mesh_select_type.addLayout(mesh_select_type_scope_options)
        mesh_select_type.addLayout(mesh_select_type_separator)
        mesh_select_type.addLayout(mesh_select_type_options)
        mesh_select_type.addStretch()
        mesh_place_buttons = QtWidgets.QHBoxLayout()
        mesh_place_buttons.setContentsMargins(2, 0, 2, 0)
        mesh_place_buttons.setSpacing(2)
        mesh_place_buttons.addWidget(self.buKi_mesh_place_add_source_btn)
        mesh_place_buttons.addWidget(self.buKi_mesh_place_clear_source_btn)
        mesh_place_list = QtWidgets.QVBoxLayout()
        mesh_place_list.setContentsMargins(2, 2, 2, 0)
        mesh_place_list.setSpacing(2)
        mesh_place_list.addWidget(self.buKi_mesh_place_source_list)
        mesh_place_random = QtWidgets.QVBoxLayout()
        mesh_place_random.setContentsMargins(2, 4, 2, 0)
        mesh_place_random.setSpacing(2)
        mesh_place_random.addWidget(self.buKi_mesh_place_random_cb)
        mesh_place_layout = QtWidgets.QVBoxLayout()
        mesh_place_layout.setContentsMargins(8, 3, 8, 0)
        mesh_place_layout.setSpacing(4)
        mesh_place_layout.addLayout(mesh_place_list)
        mesh_place_layout.addLayout(mesh_place_buttons)
        mesh_place_layout.addLayout(mesh_place_random)
        mesh_place_layout.addStretch()
        mesh_paint_buttons = QtWidgets.QHBoxLayout()
        mesh_paint_buttons.setContentsMargins(2, 0, 2, 0)
        mesh_paint_buttons.setSpacing(2)
        mesh_paint_buttons.addWidget(self.buKi_mesh_paint_add_source_btn)
        mesh_paint_buttons.addWidget(self.buKi_mesh_paint_clear_source_btn)
        mesh_paint_list = QtWidgets.QVBoxLayout()
        mesh_paint_list.setContentsMargins(2, 2, 2, 0)
        mesh_paint_list.setSpacing(2)
        mesh_paint_list.addWidget(self.buKi_mesh_paint_source_list)
        mesh_paint_time_layout = QtWidgets.QHBoxLayout()
        mesh_paint_time_layout.setContentsMargins(2, 5, 2, 0)
        mesh_paint_time_layout.setSpacing(8)
        mesh_paint_time_layout.addWidget(self.buKi_mesh_paint_time_label)
        mesh_paint_time_layout.addWidget(self.buKi_mesh_paint_time_dSpinBox)
        mesh_paint_time_layout.addWidget(self.buKi_mesh_paint_random_cb)
        mesh_paint_layout = QtWidgets.QVBoxLayout()
        mesh_paint_layout.setContentsMargins(8, 3, 8, 0)
        mesh_paint_layout.setSpacing(4)
        mesh_paint_layout.addLayout(mesh_paint_list)
        mesh_paint_layout.addLayout(mesh_paint_buttons)
        mesh_paint_layout.addLayout(mesh_paint_time_layout)
        mesh_paint_layout.addStretch()
        mesh_distribute_moveBy_options = QtWidgets.QHBoxLayout()
        mesh_distribute_moveBy_options.setContentsMargins(8, 0, 8, 0)
        mesh_distribute_moveBy_options.setSpacing(2)
        mesh_distribute_moveBy_options.addWidget(self.buKi_mesh_distribute_moveBy_label)
        mesh_distribute_moveBy_options.addWidget(self.buKi_mesh_distribute_bb_rb)
        mesh_distribute_moveBy_options.addWidget(self.buKi_mesh_distribute_value_rb)
        mesh_distribute_properties_form = QtWidgets.QFormLayout()
        mesh_distribute_properties_form.setContentsMargins(2, 0, 2, 0)
        mesh_distribute_properties_form.setSpacing(2)
        mesh_distribute_properties_form.addRow(self.buKi_mesh_distribute_spacing_label, self.buKi_mesh_distribute_spacing_dSpinBox)
        mesh_distribute_properties_form.addRow(self.buKi_mesh_distribute_moveValue_label, self.buKi_mesh_distribute_moveValue_dSpinBox)
        mesh_distribute_layout = QtWidgets.QVBoxLayout()
        mesh_distribute_layout.setContentsMargins(8, 4, 8, 0)
        mesh_distribute_layout.setSpacing(12)
        mesh_distribute_layout.addLayout(mesh_distribute_moveBy_options)
        mesh_distribute_layout.addLayout(mesh_distribute_properties_form)
        mesh_duplicator_direction_separator = QtWidgets.QHBoxLayout()
        mesh_duplicator_direction_separator.setContentsMargins(2, 0, 2, 0)
        mesh_duplicator_direction_separator.setSpacing(2)
        mesh_duplicator_direction_separator.addWidget(self.buKi_mesh_duplicator_direction_label)
        mesh_duplicator_direction_separator.addWidget(self.buKi_mesh_duplicator_direction_qFrame)
        mesh_duplicator_direction_options = QtWidgets.QHBoxLayout()
        mesh_duplicator_direction_options.setContentsMargins(10, 0, 2, 0)
        mesh_duplicator_direction_options.setSpacing(2)
        mesh_duplicator_direction_options.addWidget(self.buKi_mesh_duplicator_direction_cb)
        mesh_duplicator_moveBy_separator = QtWidgets.QHBoxLayout()
        mesh_duplicator_moveBy_separator.setContentsMargins(2, 0, 2, 0)
        mesh_duplicator_moveBy_separator.setSpacing(2)
        mesh_duplicator_moveBy_separator.addWidget(self.buKi_mesh_duplicator_moveBy_label)
        mesh_duplicator_moveBy_separator.addWidget(self.buKi_mesh_duplicator_moveBy_qFrame)
        mesh_duplicator_moveBy_options = QtWidgets.QHBoxLayout()
        mesh_duplicator_moveBy_options.setContentsMargins(10, 0, 2, 0)
        mesh_duplicator_moveBy_options.setSpacing(2)
        mesh_duplicator_moveBy_options.addWidget(self.buKi_mesh_duplicator_bb_rb)
        mesh_duplicator_moveBy_options.addWidget(self.buKi_mesh_duplicator_value_rb)
        mesh_duplicator_properties_form = QtWidgets.QFormLayout()
        mesh_duplicator_properties_form.setContentsMargins(2, 0, 2, 0)
        mesh_duplicator_properties_form.setSpacing(2)
        mesh_duplicator_properties_form.addRow(self.buKi_mesh_duplicator_copies_label, self.buKi_mesh_duplicator_copies_spinBox)
        mesh_duplicator_properties_form.addRow(self.buKi_mesh_duplicator_spacing_label, self.buKi_mesh_duplicator_spacing_dSpinBox)
        mesh_duplicator_properties_form.addRow(self.buKi_mesh_duplicator_moveValue_label, self.buKi_mesh_duplicator_moveValue_dSpinBox)
        mesh_duplicator_layout = QtWidgets.QVBoxLayout()
        mesh_duplicator_layout.setContentsMargins(8, 4, 8, 0)
        mesh_duplicator_layout.setSpacing(12)
        mesh_duplicator_layout.addLayout(mesh_duplicator_direction_separator)
        mesh_duplicator_layout.addLayout(mesh_duplicator_direction_options)
        mesh_duplicator_layout.addLayout(mesh_duplicator_moveBy_separator)
        mesh_duplicator_layout.addLayout(mesh_duplicator_moveBy_options)
        mesh_duplicator_layout.addLayout(mesh_duplicator_properties_form)
        self.buKi_mesh_settings_combine.setLayout(mesh_combine_layout)
        self.buKi_mesh_settings_place.setLayout(mesh_place_layout)
        self.buKi_select_settings_topology.setLayout(mesh_select_topology)
        self.buKi_select_settings_angle.setLayout(mesh_select_angle)
        self.buKi_select_settings_nthEdge.setLayout(mesh_select_nthEdge)
        self.buKi_select_settings_percentage.setLayout(mesh_select_percentage)
        self.buKi_select_settings_cmptCount.setLayout(mesh_select_cmptCount)
        self.buKi_select_settings_name.setLayout(mesh_select_name)
        self.buKi_select_settings_type.setLayout(mesh_select_type)
        self.buKi_mesh_settings_paint.setLayout(mesh_paint_layout)
        self.buKi_mesh_settings_distribute.setLayout(mesh_distribute_layout)
        self.buKi_mesh_settings_duplicator.setLayout(mesh_duplicator_layout)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_mesh_settings_combine)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_topology)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_angle)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_nthEdge)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_percentage)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_cmptCount)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_name)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_select_settings_type)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_mesh_settings_place)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_mesh_settings_paint)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_mesh_settings_distribute)
        self.buKi_mesh_settings_stack.addWidget(self.buKi_mesh_settings_duplicator)
        mesh_page_layout = QtWidgets.QVBoxLayout()
        mesh_page_layout.setAlignment(QtCore.Qt.AlignTop)
        mesh_page_layout.setContentsMargins(0, 2, 0, 0)
        mesh_page_layout.setSpacing(2)
        mesh_page_layout.addWidget(self.buKi_mesh_toolbox_header)
        mesh_page_layout.addWidget(self.buKi_mesh_ui_toolbox_widget)
        mesh_page_layout.addWidget(self.buKi_mesh_select_header)
        mesh_page_layout.addWidget(self.buKi_mesh_ui_select_widget)
        mesh_page_layout.addWidget(self.buKi_mesh_layout_header)
        mesh_page_layout.addWidget(self.buKi_mesh_ui_layout_widget)
        mesh_page_layout.addWidget(self.buKi_mesh_settings_stack)
        importExport_import_header_layout = QtWidgets.QHBoxLayout()
        importExport_import_header_layout.setContentsMargins(0, 0, 0, 0)
        importExport_import_header_layout.setSpacing(0)
        importExport_import_header_layout.addWidget(self.buKi_import_label)
        importExport_import_header_layout.addWidget(self.buKi_import_toggle)
        self.buKi_import_header.setLayout(importExport_import_header_layout)
        importExport_import_layout = QtWidgets.QGridLayout()
        importExport_import_layout.setContentsMargins(0, 0, 0, 0)
        importExport_import_layout.setSpacing(2)
        importExport_import_layout.addWidget(self.buKi_obj_import_btn, 0, 0)
        importExport_import_layout.addWidget(self.buKi_fbx_import_btn, 0, 1)
        importExport_import_layout.addWidget(self.buKi_abc_import_btn, 0, 2)
        importExport_import_layout.addWidget(self.buKi_placeholder_import_btn, 0, 3)
        self.buKi_importExport_import_widget.setLayout(importExport_import_layout)
        importExport_export_header_layout = QtWidgets.QHBoxLayout()
        importExport_export_header_layout.setContentsMargins(0, 0, 0, 0)
        importExport_export_header_layout.setSpacing(0)
        importExport_export_header_layout.addWidget(self.buKi_export_label)
        importExport_export_header_layout.addWidget(self.buKi_export_toggle)
        self.buKi_export_header.setLayout(importExport_export_header_layout)
        importExport_export_layout = QtWidgets.QGridLayout()
        importExport_export_layout.setContentsMargins(0, 0, 0, 0)
        importExport_export_layout.setSpacing(2)
        importExport_export_layout.addWidget(self.buKi_obj_export_btn, 0, 0)
        importExport_export_layout.addWidget(self.buKi_fbx_export_btn, 0, 1)
        importExport_export_layout.addWidget(self.buKi_abc_export_btn, 0, 2)
        importExport_export_layout.addWidget(self.buKi_placeholder_export_btn, 0, 3)
        self.buKi_importExport_export_widget.setLayout(importExport_export_layout)
        settings_import_obj_layout = QtWidgets.QVBoxLayout()
        settings_import_obj_layout.setAlignment(QtCore.Qt.AlignTop)
        settings_import_obj_layout.setContentsMargins(10, 4, 2, 2)
        settings_import_obj_layout.setSpacing(6)
        settings_import_obj_layout.addWidget(self.buKi_import_obj_combined_rb)
        settings_import_obj_layout.addWidget(self.buKi_import_obj_separate_rb)
        settings_import_obj_layout.addWidget(self.buKi_import_obj_blendshapes_rb)
        settings_import_obj_layout.addStretch()
        settings_export_obj_operation = QtWidgets.QVBoxLayout()
        settings_export_obj_operation.setContentsMargins(10, 4, 2, 2)
        settings_export_obj_operation.setSpacing(6)
        settings_export_obj_operation.addWidget(self.buKi_export_obj_combined_rb)
        settings_export_obj_operation.addWidget(self.buKi_export_obj_separate_rb)
        settings_export_obj_operation.addWidget(self.buKi_export_obj_blendshapes_rb)
        settings_export_obj_options_separator = QtWidgets.QHBoxLayout()
        settings_export_obj_options_separator.setContentsMargins(6, 8, 2, 5)
        settings_export_obj_options_separator.setSpacing(2)
        settings_export_obj_options_separator.addWidget(self.buKi_export_options_label)
        settings_export_obj_options_separator.addWidget(self.buKi_export_options_qFrame)
        settings_export_obj_options_groups_switch = QtWidgets.QHBoxLayout()
        settings_export_obj_options_groups_switch.setContentsMargins(10, 0, 8, 4)
        settings_export_obj_options_groups_switch.setSpacing(2)
        settings_export_obj_options_groups_switch.addWidget(self.buKi_export_options_groups_label)
        settings_export_obj_options_groups_switch.addWidget(self.buKi_export_options_groups_on_rb)
        settings_export_obj_options_groups_switch.addWidget(self.buKi_export_options_groups_off_rb)
        settings_export_obj_options_groups_switch.addStretch()
        settings_export_obj_options_pointGroups_switch = QtWidgets.QHBoxLayout()
        settings_export_obj_options_pointGroups_switch.setContentsMargins(10, 0, 8, 4)
        settings_export_obj_options_pointGroups_switch.setSpacing(2)
        settings_export_obj_options_pointGroups_switch.addWidget(self.buKi_export_options_pointGroups_label)
        settings_export_obj_options_pointGroups_switch.addWidget(self.buKi_export_options_pointGroups_on_rb)
        settings_export_obj_options_pointGroups_switch.addWidget(self.buKi_export_options_pointGroups_off_rb)
        settings_export_obj_options_pointGroups_switch.addStretch()
        settings_export_obj_options_materials_switch = QtWidgets.QHBoxLayout()
        settings_export_obj_options_materials_switch.setContentsMargins(10, 0, 8, 4)
        settings_export_obj_options_materials_switch.setSpacing(2)
        settings_export_obj_options_materials_switch.addWidget(self.buKi_export_options_materials_label)
        settings_export_obj_options_materials_switch.addWidget(self.buKi_export_options_materials_on_rb)
        settings_export_obj_options_materials_switch.addWidget(self.buKi_export_options_materials_off_rb)
        settings_export_obj_options_materials_switch.addStretch()
        settings_export_obj_options_smoothing_switch = QtWidgets.QHBoxLayout()
        settings_export_obj_options_smoothing_switch.setContentsMargins(10, 0, 8, 4)
        settings_export_obj_options_smoothing_switch.setSpacing(2)
        settings_export_obj_options_smoothing_switch.addWidget(self.buKi_export_options_smoothing_label)
        settings_export_obj_options_smoothing_switch.addWidget(self.buKi_export_options_smoothing_on_rb)
        settings_export_obj_options_smoothing_switch.addWidget(self.buKi_export_options_smoothing_off_rb)
        settings_export_obj_options_smoothing_switch.addStretch()
        settings_export_obj_options_normals_switch = QtWidgets.QHBoxLayout()
        settings_export_obj_options_normals_switch.setContentsMargins(10, 0, 8, 4)
        settings_export_obj_options_normals_switch.setSpacing(2)
        settings_export_obj_options_normals_switch.addWidget(self.buKi_export_options_normals_label)
        settings_export_obj_options_normals_switch.addWidget(self.buKi_export_options_normals_on_rb)
        settings_export_obj_options_normals_switch.addWidget(self.buKi_export_options_normals_off_rb)
        settings_export_obj_options_normals_switch.addStretch()
        settings_export_obj_layout = QtWidgets.QVBoxLayout()
        settings_export_obj_layout.setAlignment(QtCore.Qt.AlignTop)
        settings_export_obj_layout.setContentsMargins(0, 0, 2, 0)
        settings_export_obj_layout.setSpacing(6)
        settings_export_obj_layout.addLayout(settings_export_obj_operation)
        settings_export_obj_layout.addLayout(settings_export_obj_options_separator)
        settings_export_obj_layout.addLayout(settings_export_obj_options_groups_switch)
        settings_export_obj_layout.addLayout(settings_export_obj_options_pointGroups_switch)
        settings_export_obj_layout.addLayout(settings_export_obj_options_materials_switch)
        settings_export_obj_layout.addLayout(settings_export_obj_options_smoothing_switch)
        settings_export_obj_layout.addLayout(settings_export_obj_options_normals_switch)
        settings_export_obj_layout.addStretch()
        settings_export_fbx_layout = QtWidgets.QVBoxLayout()
        settings_export_fbx_layout.setAlignment(QtCore.Qt.AlignTop)
        settings_export_fbx_layout.setContentsMargins(10, 4, 2, 2)
        settings_export_fbx_layout.setSpacing(6)
        settings_export_fbx_layout.addWidget(self.buKi_export_fbx_single_rb)
        settings_export_fbx_layout.addWidget(self.buKi_export_fbx_separate_rb)
        settings_export_fbx_layout.addStretch()
        settings_export_abc_frameRange = QtWidgets.QHBoxLayout()
        settings_export_abc_frameRange.setAlignment(QtCore.Qt.AlignTop)
        settings_export_abc_frameRange.setContentsMargins(0, 10, 0, 0)
        settings_export_abc_frameRange.addWidget(self.buKi_export_abc_startFrame_label)
        settings_export_abc_frameRange.addWidget(self.buKi_export_abc_startFrame_spinBox)
        settings_export_abc_frameRange.addWidget(self.buKi_export_abc_endFrame_label)
        settings_export_abc_frameRange.addWidget(self.buKi_export_abc_endFrame_spinBox)
        settings_export_abc_layout = QtWidgets.QVBoxLayout()
        settings_export_abc_layout.setAlignment(QtCore.Qt.AlignTop)
        settings_export_abc_layout.setContentsMargins(10, 4, 2, 2)
        settings_export_abc_layout.setSpacing(6)
        settings_export_abc_layout.addWidget(self.buKi_export_abc_single_rb)
        settings_export_abc_layout.addWidget(self.buKi_export_abc_separate_rb)
        settings_export_abc_layout.addLayout(settings_export_abc_frameRange)
        settings_export_abc_layout.addStretch()
        self.buKi_import_settings_obj.setLayout(settings_import_obj_layout)
        self.buKi_export_settings_obj.setLayout(settings_export_obj_layout)
        self.buKi_export_settings_fbx.setLayout(settings_export_fbx_layout)
        self.buKi_export_settings_abc.setLayout(settings_export_abc_layout)
        self.buKi_importExport_settings_stack.addWidget(self.buKi_import_settings_obj)
        self.buKi_importExport_settings_stack.addWidget(self.buKi_export_settings_obj)
        self.buKi_importExport_settings_stack.addWidget(self.buKi_export_settings_fbx)
        self.buKi_importExport_settings_stack.addWidget(self.buKi_export_settings_abc)
        importExport_page_layout = QtWidgets.QVBoxLayout()
        importExport_page_layout.setAlignment(QtCore.Qt.AlignTop)
        importExport_page_layout.setContentsMargins(0, 2, 0, 0)
        importExport_page_layout.setSpacing(2)
        importExport_page_layout.addWidget(self.buKi_import_header)
        importExport_page_layout.addWidget(self.buKi_importExport_import_widget)
        importExport_page_layout.addWidget(self.buKi_export_header)
        importExport_page_layout.addWidget(self.buKi_importExport_export_widget)
        importExport_page_layout.addWidget(self.buKi_importExport_settings_stack)
        about_page_image_layout = QtWidgets.QVBoxLayout()
        about_page_image_layout.setAlignment(QtCore.Qt.AlignTop)
        about_page_image_layout.addWidget(self.buKi_about_toolTitle)
        about_page_information_layout = QtWidgets.QVBoxLayout()
        about_page_information_layout.setAlignment(QtCore.Qt.AlignTop)
        about_page_information_layout.setContentsMargins(8, 6, 0, 6)
        about_page_information_layout.setSpacing(6)
        about_page_information_layout.addWidget(self.buKi_about_version)
        about_page_information_layout.addWidget(self.buKi_about_author)
        about_page_information_layout.addWidget(self.buKi_about_email)
        about_page_information_layout.addWidget(self.buKi_about_copyright)
        about_page_information_layout.addStretch()
        about_page_links_layout = QtWidgets.QGridLayout()
        about_page_links_layout.setSpacing(2)
        about_page_links_layout.addWidget(self.buKi_about_documentation_btn, 0, 0, 1, 2, QtCore.Qt.AlignTop)
        about_page_links_layout.addWidget(self.buKi_about_website_btn, 1, 0, 1, 1, QtCore.Qt.AlignTop)
        about_page_links_layout.addWidget(self.buKi_about_gumroad_btn, 1, 1, 1, 1, QtCore.Qt.AlignTop)
        about_page_links_layout.addWidget(self.buKi_about_shortcuts_btn, 2, 0, 1, 2, QtCore.Qt.AlignTop)
        about_page_layout = QtWidgets.QVBoxLayout()
        about_page_layout.setAlignment(QtCore.Qt.AlignTop)
        about_page_layout.setContentsMargins(2, 2, 2, 2)
        about_page_layout.addLayout(about_page_image_layout)
        about_page_layout.addLayout(about_page_information_layout)
        about_page_layout.addLayout(about_page_links_layout)
        self.buKi_mesh_page = QtWidgets.QWidget()
        self.buKi_mesh_page.setLayout(mesh_page_layout)
        self.buKi_importExport_page = QtWidgets.QWidget()
        self.buKi_importExport_page.setLayout(importExport_page_layout)
        self.buKi_about_page = QtWidgets.QWidget()
        self.buKi_about_page.setLayout(about_page_layout)
        self.buKi_stack.addWidget(self.buKi_mesh_page)
        self.buKi_stack.addWidget(self.buKi_importExport_page)
        self.buKi_stack.addWidget(self.buKi_about_page)
        buKi_stack_layout = QtWidgets.QVBoxLayout()
        buKi_stack_layout.addWidget(self.buKi_stack)
        buKi_main_layout = QtWidgets.QVBoxLayout(self)
        buKi_main_layout.setMargin(0)
        buKi_main_layout.setSpacing(0)
        buKi_main_layout.addWidget(self.buKi_menuWidget)
        buKi_main_layout.addLayout(buKi_stack_layout)

    def buKi_create_connections(self):
        self.buKi_mesh_btnIcon.clicked.connect(lambda : self.buKi_goToPage(widget_lib=self.buKi_mesh_widget_lib, toggle_lib=self.buKi_mesh_toggle_lib, pageSize=self.buKi_pageSize_mesh, index=0))
        self.buKi_mesh_ui_toolboxLabel.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_mesh_ui_toolbox_widget, icon=self.buKi_mesh_ui_toolboxToggle, winSizeValue=126))
        self.buKi_mesh_ui_toolboxToggle.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_mesh_ui_toolbox_widget, icon=self.buKi_mesh_ui_toolboxToggle, winSizeValue=126))
        self.buKi_mesh_ui_selectLabel.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_mesh_ui_select_widget, icon=self.buKi_mesh_ui_selectToggle, winSizeValue=84))
        self.buKi_mesh_ui_selectToggle.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_mesh_ui_select_widget, icon=self.buKi_mesh_ui_selectToggle, winSizeValue=84))
        self.buKi_mesh_ui_layoutLabel.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_mesh_ui_layout_widget, icon=self.buKi_mesh_ui_layoutToggle, winSizeValue=44))
        self.buKi_mesh_ui_layoutToggle.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_mesh_ui_layout_widget, icon=self.buKi_mesh_ui_layoutToggle, winSizeValue=44))
        self.buKi_mesh_toolbox_extract_btn.clicked.connect(self.buKi_run_mesh_extract_LMB)
        self.buKi_mesh_toolbox_duplicateFace_btn.clicked.connect(self.buKi_run_mesh_duplicateFace_LMB)
        self.buKi_mesh_toolbox_connect_btn.clicked.connect(self.buKi_run_mesh_connect_LMB)
        self.buKi_mesh_toolbox_append_btn.clicked.connect(self.buKi_run_mesh_append_LMB)
        self.buKi_mesh_toolbox_combine_btn.clicked.connect(self.buKi_run_mesh_combine_LMB)
        self.buKi_mesh_toolbox_combine_btn.rmb_clicked.connect(self.buKi_run_mesh_combine_RMB)
        self.buKi_mesh_toolbox_separate_btn.clicked.connect(self.buKi_run_mesh_separate_LMB)
        self.buKi_mesh_toolbox_mirror_btn.clicked.connect(self.buKi_run_mesh_mirror_LMB)
        self.buKi_mesh_toolbox_pivot_btn.clicked.connect(self.buKi_run_mesh_pivot_LMB)
        self.buKi_mesh_toolbox_group_btn.clicked.connect(self.buKi_run_mesh_group_LMB)
        self.buKi_mesh_toolbox_quadFill_btn.clicked.connect(self.buKi_run_mesh_quadFill_LMB)
        self.buKi_mesh_toolbox_corner_btn.clicked.connect(self.buKi_run_mesh_corner_LMB)
        self.buKi_mesh_select_topology_btn.clicked.connect(self.buKi_run_mesh_select_topology_LMB)
        self.buKi_mesh_select_topology_btn.rmb_clicked.connect(self.buKi_run_mesh_select_topology_RMB)
        self.buKi_mesh_select_angle_btn.clicked.connect(self.buKi_run_mesh_select_angle_LMB)
        self.buKi_mesh_select_angle_btn.rmb_clicked.connect(self.buKi_run_mesh_select_angle_RMB)
        self.buKi_select_angle_slider.valueChanged.connect(self.angle_select_valid_geometry)
        self.buKi_select_angle_dSpinBox.valueChanged.connect(self.buKi_select_angle_slider.setValue)
        self.buKi_select_angle_slider.valueChanged.connect(self.buKi_select_angle_dSpinBox.setValue)
        self.buKi_mesh_select_nthEdge_btn.clicked.connect(self.buKi_run_mesh_select_nthEdge_LMB)
        self.buKi_mesh_select_nthEdge_btn.rmb_clicked.connect(self.buKi_run_mesh_select_nthEdge_RMB)
        self.buKi_mesh_select_fillShell_btn.clicked.connect(self.buKi_run_mesh_select_fillShell_LMB)
        self.buKi_mesh_select_percentage_btn.clicked.connect(self.buKi_run_mesh_select_percentage_LMB)
        self.buKi_mesh_select_percentage_btn.rmb_clicked.connect(self.buKi_run_mesh_select_percentage_RMB)
        self.buKi_mesh_select_cmptCount_btn.clicked.connect(self.buKi_run_mesh_select_cmptCount_LMB)
        self.buKi_mesh_select_cmptCount_btn.rmb_clicked.connect(self.buKi_run_mesh_select_cmptCount_RMB)
        self.buKi_mesh_select_name_btn.clicked.connect(self.buKi_run_mesh_select_name_LMB)
        self.buKi_mesh_select_name_btn.rmb_clicked.connect(self.buKi_run_mesh_select_name_RMB)
        self.buKi_mesh_select_type_btn.clicked.connect(self.buKi_run_mesh_select_type_LMB)
        self.buKi_mesh_select_type_btn.rmb_clicked.connect(self.buKi_run_mesh_select_type_RMB)
        self.buKi_mesh_layout_place_btn.clicked.connect(self.buKi_run_mesh_layout_place_LMB)
        self.buKi_mesh_layout_place_btn.rmb_clicked.connect(self.buKi_run_mesh_layout_place_RMB)
        self.buKi_mesh_place_add_source_btn.clicked.connect(lambda : self.list_add_items(self.buKi_mesh_place_source_list))
        self.buKi_mesh_place_clear_source_btn.clicked.connect(lambda : self.list_clear(self.buKi_mesh_place_source_list))
        self.buKi_mesh_layout_paint_btn.clicked.connect(self.buKi_run_mesh_layout_paint_LMB)
        self.buKi_mesh_layout_paint_btn.rmb_clicked.connect(self.buKi_run_mesh_layout_paint_RMB)
        self.buKi_mesh_paint_add_source_btn.clicked.connect(lambda : self.list_add_items(self.buKi_mesh_paint_source_list))
        self.buKi_mesh_paint_clear_source_btn.clicked.connect(lambda : self.list_clear(self.buKi_mesh_paint_source_list))
        self.buKi_mesh_layout_distribute_btn.clicked.connect(self.buKi_run_mesh_layout_distribute_LMB)
        self.buKi_mesh_layout_distribute_btn.rmb_clicked.connect(self.buKi_run_mesh_layout_distribute_RMB)
        self.buKi_mesh_layout_duplicator_btn.clicked.connect(self.buKi_run_mesh_layout_duplicator_LMB)
        self.buKi_mesh_layout_duplicator_btn.rmb_clicked.connect(self.buKi_run_mesh_layout_duplicator_RMB)
        self.buKi_importExport_btnIcon.clicked.connect(lambda : self.buKi_goToPage(widget_lib=self.buKi_importExport_widget_lib, toggle_lib=self.buKi_importExport_toggle_lib, pageSize=self.buKi_pageSize_importExport, index=1))
        self.buKi_import_label.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_importExport_import_widget, icon=self.buKi_import_toggle, winSizeValue=42))
        self.buKi_import_toggle.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_importExport_import_widget, icon=self.buKi_import_toggle, winSizeValue=42))
        self.buKi_export_label.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_importExport_export_widget, icon=self.buKi_export_toggle, winSizeValue=42))
        self.buKi_export_toggle.clicked.connect(lambda : self.buKi_toggle_header(widgetName=self.buKi_importExport_export_widget, icon=self.buKi_export_toggle, winSizeValue=42))
        self.buKi_obj_import_btn.clicked.connect(self.buKi_run_import_obj_LMB)
        self.buKi_obj_import_btn.rmb_clicked.connect(self.buKi_run_import_obj_RMB)
        self.buKi_fbx_import_btn.clicked.connect(self.buKi_run_import_fbx_LMB)
        self.buKi_abc_import_btn.clicked.connect(self.buKi_run_import_abc_LMB)
        self.buKi_obj_export_btn.clicked.connect(self.buKi_run_export_obj_LMB)
        self.buKi_obj_export_btn.rmb_clicked.connect(self.buKi_run_export_obj_RMB)
        self.buKi_fbx_export_btn.clicked.connect(self.buKi_run_export_fbx_LMB)
        self.buKi_fbx_export_btn.rmb_clicked.connect(self.buKi_run_export_fbx_RMB)
        self.buKi_abc_export_btn.clicked.connect(self.buKi_run_export_abc_LMB)
        self.buKi_abc_export_btn.rmb_clicked.connect(self.buKi_run_export_abc_RMB)
        self.buKi_about_btnIcon.clicked.connect(lambda : self.buKi_goToPage(widget_lib='', toggle_lib='', pageSize=self.buKi_pageSize_about, index=2))
        self.buKi_about_documentation_btn.clicked.connect(lambda : self.buKi_open_browser('Documentation'))
        self.buKi_about_website_btn.clicked.connect(lambda : self.buKi_open_browser('Website'))
        self.buKi_about_gumroad_btn.clicked.connect(lambda : self.buKi_open_browser('Gumroad'))
        self.buKi_about_shortcuts_btn.clicked.connect(self.run_hotkeys)

    def buKi_create_styleSheet(self):
        self.buKi_styleSheet = '\n            QDialog {\n                background-color: rgb(43,43,43);\n                }\n\n            QFrame {\n                background-color: grey;\n                }\n\n            QPushButton {\n                background-color: rgb(105,105,105);\n                border: none;\n                height: 30px;\n                }\n\n            QPushButton:hover {\n                background-color: rgb(70,130,180)\n                }\n\n            QPushButton#default {\n                background-color: rgb(105,105,105);\n                border: none;\n                height: 30px;\n                }\n\n            QPushButton#label {\n                font: bold; \n                text-align: left; \n                color: rgb(187,187,187); \n                background-color: rgb(43,43,43);\n                border: none;\n                }\n\n            QPushButton#toggle {\n                background-color: rgb(43,43,43);\n                border: none\n                }\n\n            QPushButton#menuIcon {\n                background-color: transparent;\n                border: none;\n                height: 40px;\n                }\n\n            QPushButton#icon {\n                background-color: rgb(63,63,63);\n                border: none;\n                height: 40px;\n                }\n            QPushButton#icon:hover {\n                background-color: rgb(90,90,90)\n                }\n\n            QPushButton#placeholder {\n                background-color: rgb(70,70,70);\n                border: none;\n                height: 40px;\n                }\n\n            QPushButton#iconSettings {\n                background-color: rgb(63,63,63);\n                border: none;\n                height: 40px;\n                }\n            QPushButton#iconSettings:hover {\n                background: qlineargradient(x1: 1, y1: 1, x2: 1, y2: 0,\n                                      stop: 0.06 rgb(0, 168, 255), stop: 0.07 rgb(90,90,90) );\n                }\n\n            QLineEdit {\n                background-color: rgb(35,35,35);\n                border: none;\n                height: 25px;\n                }\n\n            QLineEdit#renamer {\n                background-color: rgb(55,55,55);\n                }\n              \n            QSpinBox {\n                background-color: rgb(35,35,35);\n                border: none;\n                height: 25px;\n                }\n\n            QDoubleSpinBox {\n                background-color: rgb(35,35,35);\n                border: none;\n                height: 25px;\n                }\n\n            QToolTip { \n                background-color: rgb(238,232,170);\n                color: black;\n                border: black solid 1px;\n                padding: 3px;\n                }\n            \n            QSlider{\n                height: 40px;\n                }\n\n            QSlider:groove:horizontal {\n                background-color: rgb(35,35,35);\n                border-radius: 2px;\n                height: 4px;\n                }\n\n            QSlider:handle:horizontal {\n                background-color: rgb(150,150,150);\n                border-radius: 2px;\n                margin: 10px 0px;\n                width: 10px;\n                }\n\n            QListWidget {\n                background-color: rgb(35,35,35);\n                border: none;\n                }\n            '
        self.build_kit_window.setStyleSheet(self.buKi_styleSheet)

    def buKi_create_pageSizes(self):
        self.buKi_pageSize_about = 300
        self.buKi_minSize_mesh = 81
        self.buKi_minSize_importExport = 54
        self.buKi_maxSize_mesh = 335
        self.buKi_maxSize_importExport = 140
        self.buKi_pageSize_mesh = self.buKi_minSize_mesh
        self.buKi_pageSize_importExport = self.buKi_minSize_importExport

    def buKi_switch_focus_to_main_widget(self):
        self.buKi_menuWidget.setFocus()

    def buKi_goToPage(self, widget_lib, toggle_lib, pageSize, index):
        menuBtnModifiers = QtGui.QGuiApplication.keyboardModifiers()
        currentPageIndex = self.buKi_stack.currentIndex()
        settingsBtn = self.buKi_lib_settingsBtn[currentPageIndex]
        for i in settingsBtn:
            i.setStyleSheet(self.buKi_styleSheet)

        if currentPageIndex == 0 and self.buKi_mesh_settings_stack.isVisible() == True:
            tempSize = self.buKi_pageSize_mesh
            self.buKi_mesh_settings_stack.setVisible(False)
            self.buKi_pageSize_mesh = tempSize
        if currentPageIndex == 1 and self.buKi_importExport_settings_stack.isVisible() == True:
            tempSize = self.buKi_pageSize_importExport
            self.buKi_importExport_settings_stack.setVisible(False)
            self.buKi_pageSize_importExport = tempSize
        title = self.buKi_windowTitles[index]
        page = self.buKi_lib_menuPage[index]
        if self.buKi_menuWidget.isVisible():
            windowHeight = pageSize + 30
        else:
            windowHeight = pageSize
        if menuBtnModifiers == QtCore.Qt.NoModifier:
            self.buKi_stack.setCurrentWidget(page)
            self.buKi_set_menu_icon_status(0)
            self.buKi_change_active_page('%s' % title, windowHeight, True)
        elif index == 2:
            pass
        else:
            self.buKi_collapse_expand_header(widget_lib, toggle_lib, index)

    def buKi_change_active_page(self, title, height, visibility):
        self.build_kit_window.setWindowTitle('%s' % title)
        self.build_kit_window.setFixedHeight(height)
        self.buKi_stack.setVisible(visibility)

    def buKi_set_menu_icon_status(self, index):
        if index != 3:
            index = self.buKi_stack.currentIndex()
        if index == 0:
            self.buKi_mesh_btnIcon.setIcon(QtGui.QPixmap(self.buKi_icon_mesh_active))
        else:
            self.buKi_mesh_btnIcon.setIcon(QtGui.QPixmap(self.buKi_icon_mesh_inactive))
        if index == 1:
            self.buKi_importExport_btnIcon.setIcon(QtGui.QPixmap(self.buKi_icon_importExport_active))
        else:
            self.buKi_importExport_btnIcon.setIcon(QtGui.QPixmap(self.buKi_icon_importExport_inactive))
        if index == 2:
            self.buKi_about_btnIcon.setIcon(QtGui.QPixmap(self.buKi_icon_about_active))
        else:
            self.buKi_about_btnIcon.setIcon(QtGui.QPixmap(self.buKi_icon_about_inactive))

    def buKi_collapse_expand_header(self, widgetLib, toggleLib, index):
        meshMenuBtnModifiers = QtGui.QGuiApplication.keyboardModifiers()
        meshPageIndexCheck = self.buKi_stack.currentIndex()
        if meshPageIndexCheck == index:
            if meshMenuBtnModifiers == QtCore.Qt.AltModifier:
                for i in widgetLib:
                    i.setVisible(False)

                for i in toggleLib:
                    i.setIcon(QtGui.QPixmap(self.buKi_icon_expand))

                tmpWinHeight = self.buKi_update_pageSize('min', index, '')
            elif meshMenuBtnModifiers == QtCore.Qt.ControlModifier:
                for i in widgetLib:
                    i.setVisible(True)

                for i in toggleLib:
                    i.setIcon(QtGui.QPixmap(self.buKi_icon_collapse))

                tmpWinHeight = self.buKi_update_pageSize('max', index, '')
            self.build_kit_window.setFixedHeight(tmpWinHeight)

    def buKi_toggle_header(self, widgetName, icon, winSizeValue):
        winCurrentHeight = self.build_kit_window.height()
        index = self.buKi_stack.currentIndex()
        if widgetName.isVisible() == True:
            widgetName.setVisible(False)
            if icon:
                icon.setIcon(QtGui.QPixmap(self.buKi_icon_expand))
            self.build_kit_window.setFixedHeight(winCurrentHeight - winSizeValue)
        else:
            widgetName.setVisible(True)
            if icon:
                icon.setIcon(QtGui.QPixmap(self.buKi_icon_collapse))
            self.build_kit_window.setFixedHeight(winCurrentHeight + winSizeValue)
        currentStackHeight = self.buKi_stack.frameSize().height()
        self.buKi_update_pageSize('currentStackHeight', index, currentStackHeight)

    def buKi_toggle_settings(self, clickedButton, settingsLib, settingsStack, settingsIndex, winSizeValue):
        winCurrentHeight = self.build_kit_window.height()
        pageIndex = self.buKi_stack.currentIndex()
        currentSettingsIndex = settingsStack.currentIndex()
        currentWidgetHeight = settingsStack.frameSize().height()
        settingsPage = settingsLib[settingsIndex]
        settingsBtn = clickedButton[settingsIndex]
        for i in clickedButton:
            if i == clickedButton[settingsIndex]:
                i.setStyleSheet('* { background-color: rgb(55,55,55);}')
            else:
                i.setStyleSheet(self.buKi_styleSheet)

        if currentSettingsIndex != settingsIndex:
            if settingsStack.isVisible() == True:
                settingsStack.setVisible(False)
                self.build_kit_window.setFixedHeight(winCurrentHeight - currentWidgetHeight)
            settingsStack.setCurrentWidget(settingsPage)
            winCurrentHeight = self.build_kit_window.height()
        if settingsStack.isVisible() == True:
            settingsStack.setVisible(False)
            settingsBtn.setStyleSheet(self.buKi_styleSheet)
            self.build_kit_window.setFixedHeight(winCurrentHeight - winSizeValue)
        else:
            settingsStack.setVisible(True)
            self.build_kit_window.setFixedHeight(winCurrentHeight + winSizeValue)

    def buKi_update_pageSize(self, type, index, height):
        if type == 'menuToggle':
            if self.buKi_menuWidget.isVisible() == True:
                menuHeight = -30
            else:
                menuHeight = 30
            self.buKi_pageSize_mesh -= menuHeight
            self.buKi_pageSize_importExport -= menuHeight
            self.buKi_pageSize_about -= menuHeight
            winCurrentHeight = self.build_kit_window.height()
            self.build_kit_window.setFixedHeight(winCurrentHeight - menuHeight)
        if type == 'min':
            if index == 0:
                self.buKi_mesh_settings_stack.setVisible(False)
                self.buKi_pageSize_mesh = tmpWinHeight = self.buKi_minSize_mesh
            elif index == 1:
                self.buKi_pageSize_importExport = tmpWinHeight = self.buKi_minSize_importExport
            if self.buKi_menuWidget.isVisible() == True:
                tmpWinHeight += 30
            return tmpWinHeight
        if type == 'max':
            if index == 0:
                self.buKi_pageSize_mesh = tmpWinHeight = self.buKi_maxSize_mesh
            elif index == 1:
                self.buKi_pageSize_importExport = tmpWinHeight = self.buKi_maxSize_importExport
            if self.buKi_menuWidget.isVisible() == True:
                tmpWinHeight += 30
            return tmpWinHeight
        if type == 'currentStackHeight':
            if index == 0:
                self.buKi_pageSize_mesh = height
            elif index == 1:
                self.buKi_pageSize_importExport = height

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter:
            self.buKi_switch_focus_to_main_widget()
        if e.key() == QtCore.Qt.Key_Return:
            self.buKi_switch_focus_to_main_widget()
        if e.key() == QtCore.Qt.Key_1:
            self.buKi_goToPage(self.buKi_mesh_widget_lib, self.buKi_mesh_toggle_lib, self.buKi_pageSize_mesh, 0)
        elif e.key() == QtCore.Qt.Key_2:
            self.buKi_goToPage(self.buKi_importExport_widget_lib, self.buKi_importExport_toggle_lib, self.buKi_pageSize_importExport, 1)
        elif e.key() == QtCore.Qt.Key_3:
            self.buKi_goToPage('', '', self.buKi_pageSize_about, 2)
        elif e.key() == QtCore.Qt.Key_4:
            meshMenuBtnModifiers = QtGui.QGuiApplication.keyboardModifiers()
            if meshMenuBtnModifiers == QtCore.Qt.AltModifier:
                currentPageIndex = self.buKi_stack.currentIndex()
                if currentPageIndex == 0:
                    self.buKi_mesh_settings_stack.setVisible(False)
                self.buKi_change_active_page('  Build Kit', 30, False)
                self.buKi_set_menu_icon_status(3)
            else:
                if self.build_kit_window.height() == 30:
                    return
                if self.buKi_menuWidget.isVisible() == False:
                    self.buKi_menuWidget.setVisible(True)
                else:
                    self.buKi_menuWidget.setVisible(False)
                self.buKi_update_pageSize('menuToggle', '', '')
        else:
            super(MainClass_BuildKit, self).keyPressEvent(e)

    def buKi_run_mesh_extract_LMB(self):
        self.buKi_extract_duplicate_check('_Ext')

    def buKi_run_mesh_duplicateFace_LMB(self):
        self.buKi_extract_duplicate_check('_Dup')

    def buKi_run_mesh_connect_LMB(self):
        modifier = mc.getModifiers()
        if modifier == 0:
            self.buKi_connect_line()
        if modifier & 8 > 0:
            self.buKi_connect_diamond()
        if modifier & 4 > 0:
            self.buKi_connect_corner()
        if modifier & 1 > 0:
            self.buKi_connect_end()

    def buKi_run_mesh_append_LMB(self):
        modifier = mc.getModifiers()
        if modifier == 0:
            self.buKi_append_plus()
        if modifier & 8 > 0:
            self.buki_append_ring_loop()

    def buKi_run_mesh_combine_LMB(self):
        self.buKi_combine()

    def buKi_run_mesh_combine_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_toolbox_combine_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=50)

    def buKi_run_mesh_separate_LMB(self):
        self.buKi_separate()

    def buKi_run_mesh_mirror_LMB(self):
        modifier = mc.getModifiers()
        if modifier & 1 > 0:
            mirror_type = 'Pivot'
            axis = 0
            if modifier & 8 > 0:
                axis = 1
            if modifier & 4 > 0:
                axis = 2
        else:
            mirror_type = 'World'
            axis = 0
            if modifier & 8 > 0:
                axis = 1
            if modifier & 4 > 0:
                axis = 2
        self.buKi_mirror(axis, mirror_type)

    def buKi_run_mesh_pivot_LMB(self):
        modifier = mc.getModifiers()
        if modifier & 1 > 0:
            if modifier & 8 > 0:
                if modifier & 4 > 0:
                    mc.CenterPivot()
                else:
                    self.pivot_position('back')
            elif modifier & 4 > 0:
                self.pivot_position('right')
            else:
                self.pivot_position('top')
        else:
            if modifier == 0:
                self.pivot_position('bottom')
            if modifier & 8 > 0:
                self.pivot_position('front')
            if modifier & 4 > 0:
                self.pivot_position('left')

    def buKi_run_mesh_group_LMB(self):
        modifier = mc.getModifiers()
        if modifier == 0:
            self.buKi_group_all()
        if modifier & 8 > 0:
            self.buKi_group_individual()

    def buKi_run_mesh_quadFill_LMB(self):
        self.buKi_quad_fill()

    def buKi_run_mesh_corner_LMB(self):
        self.buKi_forty_five_mesh_angle('positive', False)

    def buKi_run_mesh_select_topology_LMB(self):
        modifier = mc.getModifiers()
        if modifier == 0:
            if self.buKi_select_topology_triangles_rb.isChecked():
                self.buKi_topology_triangles()
            if self.buKi_select_topology_quads_rb.isChecked():
                self.buKi_topology_quads()
            if self.buKi_select_topology_ngons_rb.isChecked():
                self.buKi_topology_ngons()
            if self.buKi_select_topology_concave_rb.isChecked():
                self.buKi_topology_concave()
            if self.buKi_select_topology_lamina_rb.isChecked():
                self.buKi_topology_lamina()
            if self.buKi_select_topology_holes_rb.isChecked():
                self.buKi_topology_holes()
            if self.buKi_select_topology_manifold_rb.isChecked():
                self.buKi_topology_manifold()
        if modifier & 8 > 0:
            mc.TogglePolyCount()

    def buKi_run_mesh_select_topology_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_topology_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=120)

    def buKi_run_mesh_select_angle_LMB(self):
        self.buKi_select_by_angle()

    def buKi_run_mesh_select_angle_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_angle_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=40)

    def buKi_run_mesh_select_nthEdge_LMB(self):
        modifier = mc.getModifiers()
        if modifier == 0:
            nth_type = 'edgeLoop'
        if modifier & 8 > 0:
            nth_type = 'edgeRing'
        if modifier & 4 > 0:
            nth_type = 'edgeBorder'
        self.buKi_select_nth_edge(nth_type)

    def buKi_run_mesh_select_nthEdge_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_nthEdge_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=40)

    def buKi_run_mesh_select_fillShell_LMB(self):
        self.buKi_fill_prepare_shell()

    def buKi_run_mesh_select_percentage_LMB(self):
        self.buKi_select_by_percentage()

    def buKi_run_mesh_select_percentage_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_percentage_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=40)

    def buKi_run_mesh_select_cmptCount_LMB(self):
        modifier = mc.getModifiers()
        if self.buKi_select_cmptCountValues_on_rb.isChecked():
            if modifier & 8 > 0:
                self.buKi_select_by_component_value('v')
            elif modifier & 4 > 0:
                self.buKi_select_by_component_value('e')
            elif modifier & 1 > 0:
                self.buKi_select_by_component_value('uv')
            else:
                self.buKi_select_by_component_value('f')
        elif modifier & 8 > 0:
            component_count = mc.polyEvaluate(v=True)
            self.buKi_select_by_component_count('v', component_count)
        elif modifier & 4 > 0:
            component_count = mc.polyEvaluate(e=True)
            self.buKi_select_by_component_count('e', component_count)
        elif modifier & 1 > 0:
            component_count = mc.polyEvaluate(uv=True)
            self.buKi_select_by_component_count('uv', component_count)
        else:
            component_count = mc.polyEvaluate(f=True)
            self.buKi_select_by_component_count('f', component_count)

    def buKi_run_mesh_select_cmptCount_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_cmptCount_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=140)

    def buKi_run_mesh_select_name_LMB(self):
        self.buKi_select_by_name()

    def buKi_run_mesh_select_name_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_name_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=110)

    def buKi_run_mesh_select_type_LMB(self):
        self.buKi_select_by_type()

    def buKi_run_mesh_select_type_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_select_type_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=140)

    def buKi_run_mesh_layout_place_LMB(self):
        self.buKi_layout_place()

    def buKi_run_mesh_layout_place_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_layout_place_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=174)

    def buKi_run_mesh_layout_paint_LMB(self):
        self.buKi_layout_paint()

    def buKi_run_mesh_layout_paint_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_layout_paint_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=190)

    def buKi_run_mesh_layout_distribute_LMB(self):
        self.buKi_layout_distribute()

    def buKi_run_mesh_layout_distribute_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_layout_distribute_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=97)

    def buKi_run_mesh_layout_duplicator_LMB(self):
        self.buKi_layout_duplicator()

    def buKi_run_mesh_layout_duplicator_RMB(self):
        index = self.buKi_lib_meshSettingsBtn.index(self.buKi_mesh_layout_duplicator_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_meshSettingsBtn, settingsLib=self.buKi_lib_meshSettings, settingsStack=self.buKi_mesh_settings_stack, settingsIndex=index, winSizeValue=200)

    def buKi_run_import_obj_LMB(self):
        self.buKi_import_obj()

    def buKi_run_import_obj_RMB(self):
        index = self.buKi_lib_importExport_settingsBtn.index(self.buKi_obj_import_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_importExport_settingsBtn, settingsLib=self.buKi_lib_importExport_settings, settingsStack=self.buKi_importExport_settings_stack, settingsIndex=index, winSizeValue=70)

    def buKi_run_import_fbx_LMB(self):
        self.buKi_import_fbx()

    def buKi_run_import_abc_LMB(self):
        self.buKi_import_abc()

    def buKi_run_export_obj_LMB(self):
        self.buKi_export_obj()

    def buKi_run_export_obj_RMB(self):
        index = self.buKi_lib_importExport_settingsBtn.index(self.buKi_obj_export_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_importExport_settingsBtn, settingsLib=self.buKi_lib_importExport_settings, settingsStack=self.buKi_importExport_settings_stack, settingsIndex=index, winSizeValue=215)

    def buKi_run_export_fbx_LMB(self):
        self.buKi_export_fbx()

    def buKi_run_export_fbx_RMB(self):
        index = self.buKi_lib_importExport_settingsBtn.index(self.buKi_fbx_export_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_importExport_settingsBtn, settingsLib=self.buKi_lib_importExport_settings, settingsStack=self.buKi_importExport_settings_stack, settingsIndex=index, winSizeValue=50)

    def buKi_run_export_abc_LMB(self):
        self.buKi_export_abc()

    def buKi_run_export_abc_RMB(self):
        index = self.buKi_lib_importExport_settingsBtn.index(self.buKi_abc_export_btn)
        self.buKi_toggle_settings(clickedButton=self.buKi_lib_importExport_settingsBtn, settingsLib=self.buKi_lib_importExport_settings, settingsStack=self.buKi_importExport_settings_stack, settingsIndex=index, winSizeValue=90)

    def calc_length(self, pointA, pointB):
        length = math.sqrt(math.pow(pointB[0] - pointA[0], 2) + math.pow(pointB[1] - pointA[1], 2) + math.pow(pointB[2] - pointA[2], 2))
        return length

    def MAS_list_points(self, A, B, operation):
        listbutton_response = []
        for i in range(3):
            if operation == '*':
                temp = A[i] * B
            elif operation == '+':
                temp = A[i] + B[i]
            elif operation == '-':
                temp = A[i] - B[i]
            listbutton_response.append(temp)

        return listbutton_response

    def calc_hilfsebene(self, V, P3):
        d = V[0] * P3[0] + V[1] * P3[1] + V[2] * P3[2]
        return d

    def calc_gerade_in_H(self, P1, V, hilfsebene):
        hilfsebene = round(hilfsebene, 2)
        s = 0
        while True:
            a = P1[0] + V[0] * s
            b = P1[1] + V[1] * s
            c = P1[2] + V[2] * s
            d = V[0] * a + V[1] * b + V[2] * c
            if round(d, 2) == hilfsebene:
                return round(s, 4)
                break
            s += 0.001

    def calc_lotfusspunkt(self, P1, s, V):
        F = [0, 0, 0]
        F[0] = P1[0] + s * V[0]
        F[1] = P1[1] + s * V[1]
        F[2] = P1[2] + s * V[2]
        return F

    def calc_normal(self, pointA, length):
        grid_origin = [
         0, 0, 0]
        length = self.calc_length(grid_origin, pointA)
        for i in range(3):
            pointA[i] = pointA[i] / length

        return pointA

    def calc_cross_product(self, pointA, pointB):
        cross_product = [
         0, 0, 0]
        cross_product[0] = pointA[1] * pointB[2] - pointA[2] * pointB[1]
        cross_product[1] = pointA[2] * pointB[0] - pointA[0] * pointB[2]
        cross_product[2] = pointA[0] * pointB[1] - pointA[1] * pointB[0]
        return cross_product

    def create_hotkeys(self, hotkey, categoryName):
        name = hotkey['name']
        command = hotkey['command']
        try:
            mc.runTimeCommand(name, c=command, cat='%s' % categoryName, cl='python')
            om.MGlobal.displayInfo('Info: Added %s script to the hotkey editor.' % name)
        except:
            pass

    def run_hotkeys(self):
        for key in self.hotkey_library_mesh:
            self.create_hotkeys(key, 'BuKi_Mesh')

        for key in self.hotkey_library_select:
            self.create_hotkeys(key, 'BuKi_Select')

        for key in self.hotkey_library_launch:
            self.create_hotkeys(key, 'RS Tools')

    def warning_message(self, file_name):
        warning_dialog = QDialog_Custom_Warning()
        warning_dialog.buKi_warning_message_label.setText('%s already exists. \nDo you want to replace it?' % file_name)
        button_response = warning_dialog.exec_()
        if button_response == QtWidgets.QDialog.Accepted:
            return True
        else:
            return False

    def split_name(self, object_input, split_input, split_position):
        if '%s' % split_input in object_input:
            temp_name = object_input.split('%s' % split_input)[split_position]
            return temp_name

    def buKi_get_blendshape_name(self):
        blendshape_name = ''
        history = mc.listHistory()
        for i in history:
            if 'blendShape' in i and 'Group' not in i:
                blendshape_name = i

        return blendshape_name

    def buKi_set_obj_options(self, obj_options):
        if self.buKi_export_options_groups_on_rb.isChecked():
            obj_options[0] = 1
        if self.buKi_export_options_groups_off_rb.isChecked():
            obj_options[0] = 0
        if self.buKi_export_options_pointGroups_on_rb.isChecked():
            obj_options[1] = 1
        if self.buKi_export_options_pointGroups_off_rb.isChecked():
            obj_options[1] = 0
        if self.buKi_export_options_materials_on_rb.isChecked():
            obj_options[2] = 1
        if self.buKi_export_options_materials_off_rb.isChecked():
            obj_options[2] = 0
        if self.buKi_export_options_smoothing_on_rb.isChecked():
            obj_options[3] = 1
        if self.buKi_export_options_smoothing_off_rb.isChecked():
            obj_options[3] = 0
        if self.buKi_export_options_normals_on_rb.isChecked():
            obj_options[4] = 1
        if self.buKi_export_options_normals_off_rb.isChecked():
            obj_options[4] = 0
        return obj_options

    def buKi_write_file(self, file_name, file_type):
        obj_options = [
         0, 0, 0, 0, 0]
        if file_type == 'OBJexport':
            obj_options = self.buKi_set_obj_options(obj_options)
        mc.file(file_name, es=True, f=True, typ='%s' % file_type, op='groups=%s;ptgroups=%s;materials=%s;smoothing=%s;normals=%s' % (obj_options[0], obj_options[1], obj_options[2], obj_options[3], obj_options[4]))

    def buKi_get_file_path(self, file_mode, cap, format_filter):
        get_path = mc.fileDialog2(fm=file_mode, ff='%s' % format_filter, ds=2, cap='%s' % cap)
        return get_path

    def get_object_scale_value(self, scale_input):
        get_scale_x = mc.getAttr('%s.scaleX' % scale_input)
        get_scale_y = mc.getAttr('%s.scaleY' % scale_input)
        get_scale_z = mc.getAttr('%s.scaleZ' % scale_input)
        object_scale_values = [get_scale_x, get_scale_y, get_scale_z]
        return object_scale_values

    def get_bounding_box(self, bb_input):
        get_bb_axis_length = [
         0, 0, 0]
        get_bb_transform_scale = self.get_object_scale_value(bb_input)
        if self.is_group_check(bb_input) == True:
            object_bb = mc.exactWorldBoundingBox(bb_input, ce=True)
            object_bb_min = object_bb[0:3]
            object_bb_max = object_bb[3:6]
            get_bb_axis_length[0] = object_bb_max[0] - object_bb_min[0]
            get_bb_axis_length[1] = object_bb_max[1] - object_bb_min[1]
            get_bb_axis_length[2] = object_bb_max[2] - object_bb_min[2]
        else:
            bb_shape = mc.listRelatives(bb_input, s=True)
            object_bb_min = list(mc.getAttr('%s.boundingBoxMin' % bb_shape[0])[0])
            object_bb_max = list(mc.getAttr('%s.boundingBoxMax' % bb_shape[0])[0])
            get_bb_axis_length[0] = (object_bb_max[0] - object_bb_min[0]) * get_bb_transform_scale[0]
            get_bb_axis_length[1] = (object_bb_max[1] - object_bb_min[1]) * get_bb_transform_scale[1]
            get_bb_axis_length[2] = (object_bb_max[2] - object_bb_min[2]) * get_bb_transform_scale[2]
        return get_bb_axis_length

    def buKi_get_transform_selection(self):
        buKi_return_list = []
        buKi_list = mc.ls(sl=True, fl=True, tr=True, l=True)
        for i in reversed(buKi_list):
            buKi_return_list.append(i)

        return buKi_return_list

    def buKi_search_replace_swap_L_R(self):
        mc.undoInfo(ock=True)
        buKi_search_replace_swap_list = self.buKi_get_transform_selection()
        buKi_search_value = ''
        buKi_replace_value = ''
        for i in buKi_search_replace_swap_list:
            if 'L_' in i:
                buKi_search_value = 'L_'
                buKi_replace_value = 'R_'
            if 'R_' in i:
                buKi_search_value = 'R_'
                buKi_replace_value = 'L_'
            if '%s' % buKi_search_value in i:
                buKi_line = i.split('|')[(-1)]
                buKi_new_text = buKi_line.replace('%s' % buKi_search_value, '%s' % buKi_replace_value)
                mc.rename(i, '%s' % buKi_new_text)

        mc.undoInfo(cck=True)

    def list_add_items(self, widget_list):
        objects = mc.ls(sl=True, fl=True)
        if not objects:
            return
        for i in objects:
            widget_list.addItem(i)

    def list_get_items(self, item_list):
        list_items = [ str(item_list.item(i).text()) for i in range(item_list.count()) ]
        return list_items

    def list_clear(self, widget_list):
        widget_list.clear()

    def list_remove_item(self, widget_list):
        list_item = widget_list.selectedItems()
        if not list_item:
            return
        for item in list_item:
            widget_list.takeItem(widget_list.row(item))

    def buKi_object_under_cursor(self):
        pos = QtGui.QCursor.pos()
        widget = QtWidgets.qApp.widgetAt(pos)
        relpos = widget.mapFromGlobal(pos)
        panel = mc.getPanel(up=True) or ''
        if 'modelPanel' not in panel:
            return
        else:
            return (mc.hitTest(panel, relpos.x(), relpos.y()) or [None])[0]

    def is_group_check(self, is_group_input):
        if not mc.listRelatives(is_group_input, s=True) and mc.nodeType(is_group_input) == 'transform':
            return True
        else:
            return False

    def buKi_select_groups(self):
        group_list = []
        for grp in mc.ls(sl=True, fl=True):
            if not mc.listRelatives(grp, shapes=True) and mc.nodeType(grp) == 'transform':
                group_list.append(grp)

        mc.select(group_list)

    def get_object_parent(self, child):
        parent = mc.listRelatives(child, p=True, f=True)
        return parent

    def pivot_store(self):
        source = mc.ls(sl=True)
        mc.spaceLocator(n='Temp_PivotLocator', p=(0, 0, 0), a=True)
        target = mc.ls(sl=True)
        self.pivot_parent(source[0], target[0])
        mc.select(source)

    def pivot_parent(self, source, target):
        mc.parent(target, source)
        mc.makeIdentity(target, a=True, t=True, r=True, s=True)
        mc.parent(target, w=True)

    def pivot_assign(self):
        target = mc.ls(sl=True)
        target_parent = self.get_object_parent(target)
        source = mc.ls('Temp_PivotLocator')
        self.pivot_parent(source, target)
        mc.delete('Temp_PivotLocator')
        mc.parent(target, target_parent)

    def buKi_extract_duplicate_check(self, extension):
        mc.undoInfo(ock=True)
        selected_faces_list = mc.ls(sl=True, fl=True, l=True)
        parent_shapes = mc.ls(sl=True, o=True, l=True)
        parent_shapes = list(dict.fromkeys(parent_shapes))
        if len(parent_shapes) > 1:
            for i in parent_shapes:
                parent_object = []
                face_selection = []
                split_mesh_name = i.split('|')
                parent_object.append(split_mesh_name[(-2)])
                indices = [ i for i, x in enumerate(selected_faces_list) if '%s' % parent_object[0] in x ]
                for i in indices:
                    face_selection.append(selected_faces_list[i])

                mc.select(face_selection)
                self.buKi_extract_duplicate('%s' % extension)

        else:
            self.buKi_extract_duplicate('%s' % extension)
        mc.undoInfo(cck=True)

    def buKi_extract_duplicate(self, extension):
        mc.undoInfo(ock=True)
        faces_to_extract = mc.ls(sl=True, fl=True, l=True)
        mesh_name = mc.ls(faces_to_extract, o=True, l=True)
        if '.f[' in faces_to_extract[0]:
            mc.InvertSelection()
            faces_to_keep = mc.ls(sl=True, fl=True, l=True)
            if extension == '_Ext' and len(faces_to_keep) == 0:
                om.MGlobal.displayInfo('Info: Nothing to extract from.')
                return
            mc.duplicate(mesh_name, n='RS_TempObject', st=True)
            split_mesh_name = mesh_name[0].split('|')
            faces_to_keep = [ ek.replace('%s' % split_mesh_name[(-2)], 'RS_TempObject') for ek in faces_to_keep ]
            if len(faces_to_keep) > 0:
                mc.delete(faces_to_keep)
            if extension == '_Ext':
                mc.delete(faces_to_extract)
            mc.select('RS_TempObject')
            mc.CenterPivot()
            extCheck = False
            if extension == '_Ext':
                if '_Ext' in '%s' % split_mesh_name[(-2)]:
                    mc.rename('RS_TempObject', '%s' % split_mesh_name[(-2)])
                    extCheck = True
            if extension == '_Dup':
                if '_Dup' in '%s' % split_mesh_name[(-2)]:
                    mc.rename('RS_TempObject', '%s' % split_mesh_name[(-2)])
                    extCheck = True
            if extCheck == False:
                mc.rename('RS_TempObject', '%s%s' % (split_mesh_name[(-2)], extension))
        else:
            om.MGlobal.displayInfo('Info: Please select a face.')
        mc.undoInfo(cck=True)

    def buKi_connect_line(self):
        mc.undoInfo(ock=True)
        mc.SelectEdgeRingSp()
        mc.ConnectComponents()
        mc.undoInfo(cck=True)

    def buKi_connect_diamond(self):
        mc.polySmooth(mth=0, sdt=2, ost=False, dv=1, c=True, suv=False, khe=True, kb=True, kmb=True, kt=True)

    def get_corner_vertex(self, vertice_list, lowerEdgeAVertices, lowerEdgeBVertices):
        for vert in vertice_list:
            if vert in lowerEdgeAVertices and vert in lowerEdgeBVertices:
                corner_vert = vert

        return corner_vert

    def get_edge_vertices(self, edge):
        mc.select(edge)
        mc.ConvertSelectionToVertices()
        edgeVertices = mc.ls(sl=True, fl=True)
        return edgeVertices

    def get_subdivide_edges(self, vertA, vertB):
        mc.select(vertA, vertB)
        mc.ConvertSelectionToContainedEdges()
        mc.polySubdivideEdge(ws=True, s=False, dv=1, ch=True)
        subdiv_edges = mc.ls(sl=True, fl=True)
        return subdiv_edges

    def get_subdivEdges_centroid(self, edges, vertA, vertB):
        mc.select(edges)
        mc.ConvertSelectionToVertices()
        centroid = mc.ls(sl=True, fl=True)
        centroid.remove(vertA)
        centroid.remove(vertB)
        return centroid

    def buKi_connect_corner(self):
        mc.undoInfo(ock=True)
        lower_corner_edges = mc.ls(sl=True, fl=True)
        mc.ConvertSelectionToVertices()
        vertices = mc.ls(sl=True, fl=True)
        lowerEdgeAVertices = self.get_edge_vertices(lower_corner_edges[0])
        lowerEdgeBVertices = self.get_edge_vertices(lower_corner_edges[1])
        lower_corner_vert = self.get_corner_vertex(vertices, lowerEdgeAVertices, lowerEdgeBVertices)
        mc.select(lower_corner_edges)
        mc.ConvertSelectionToFaces()
        faces = mc.ls(sl=True, fl=True)
        for face in faces:
            mc.select(face)
            mc.ConvertSelectionToEdgePerimeter()
            tmpEdges = mc.ls(sl=True, fl=True)
            if lower_corner_edges[0] in tmpEdges and lower_corner_edges[1] in tmpEdges:
                corner_face = face

        mc.select(corner_face)
        mc.ConvertSelectionToEdgePerimeter()
        upper_corner_edges = mc.ls(sl=True, fl=True)
        upper_corner_edges.remove(lower_corner_edges[0])
        upper_corner_edges.remove(lower_corner_edges[1])
        mc.select(upper_corner_edges)
        mc.ConvertSelectionToVertices()
        upper_vertices = mc.ls(sl=True, fl=True)
        upperEdgeAVertices = self.get_edge_vertices(upper_corner_edges[0])
        upperEdgeBVertices = self.get_edge_vertices(upper_corner_edges[1])
        upper_corner_vert = self.get_corner_vertex(upper_vertices, upperEdgeAVertices, upperEdgeBVertices)
        mc.select(upper_corner_vert, lower_corner_vert)
        mc.ConnectComponents()
        diagonal_edges = self.get_subdivide_edges(upper_corner_vert, lower_corner_vert)
        diagonal_centroid = self.get_subdivEdges_centroid(diagonal_edges, upper_corner_vert, lower_corner_vert)
        lowerSubdivEdgesA = self.get_subdivide_edges(lowerEdgeAVertices[0], lowerEdgeAVertices[1])
        lowerSubdivEdgesB = self.get_subdivide_edges(lowerEdgeBVertices[0], lowerEdgeBVertices[1])
        lower_centroid_A = self.get_subdivEdges_centroid(lowerSubdivEdgesA, lowerEdgeAVertices[0], lowerEdgeAVertices[1])
        lower_centroid_B = self.get_subdivEdges_centroid(lowerSubdivEdgesB, lowerEdgeBVertices[0], lowerEdgeBVertices[1])
        mc.select(lower_centroid_A, diagonal_centroid)
        mc.ConnectComponents()
        mc.select(lower_centroid_B, diagonal_centroid)
        mc.ConnectComponents()
        mc.select(diagonal_centroid, lower_corner_vert)
        temp_edge = mc.ConvertSelectionToContainedEdges()
        mc.delete()
        mc.undoInfo(cck=True)

    def get_contained_edge_subdivide_vertices(self, vertices):
        mc.select(vertices)
        mc.ConvertSelectionToContainedEdges()
        mc.polySubdivideEdge(ws=True, dv=2)
        tempVertices = mc.ls(mc.polyListComponentConversion(mc.ls(sl=True), tv=True), fl=True)
        for vert in vertices:
            if vert in tempVertices:
                tempVertices.remove(vert)

        return tempVertices

    def get_point_positions(self, vertices):
        pointGrp = range(0, len(vertices))
        for i in range(len(vertices)):
            pointGrp[i] = mc.pointPosition(vertices[i], w=True)

        return pointGrp

    def buKi_connect_end(self):
        mc.undoInfo(ock=True)
        edges = mc.ls(sl=True, fl=True)
        vertices = mc.ls(mc.polyListComponentConversion(edges, tv=True), fl=True)
        doubleSliceEdge = []
        for edge in edges:
            tmpVertices = mc.ls(mc.polyListComponentConversion(edge, tv=True), fl=True)
            for vert in tmpVertices:
                if vert in doubleSliceEdge:
                    doubleSliceEdge.remove(vert)
                else:
                    doubleSliceEdge.append(vert)

        for i in doubleSliceEdge:
            vertices.remove(i)

        lowerVertices = self.get_contained_edge_subdivide_vertices(doubleSliceEdge)
        upperVertices = self.get_contained_edge_subdivide_vertices(vertices)
        upperPoints = self.get_point_positions(upperVertices)
        lowerPoints = self.get_point_positions(lowerVertices)
        innerEdgesVertices = [
         0, 0]
        for i in range(2):
            length = [
             0, 0]
            for j in range(2):
                length[j] = self.calc_length(lowerPoints[i], upperPoints[j])

            if length[0] < length[1]:
                innerEdgesVertices[i] = [
                 lowerVertices[i], upperVertices[0]]
            else:
                innerEdgesVertices[i] = [
                 lowerVertices[i], upperVertices[1]]

        for i in innerEdgesVertices:
            mc.select(i)
            mc.ConnectComponents()

        innerEdges = [0, 0]
        for i in range(2):
            mc.select(innerEdgesVertices[i])
            mc.ConvertSelectionToContainedEdges()
            innerEdges[i] = mc.ls(sl=True)

        mc.select(innerEdges[0], innerEdges[1])
        mc.ConnectComponents()
        cornerPoints = self.get_point_positions(vertices)
        for j in range(2):
            length[j] = self.calc_length(upperPoints[0], cornerPoints[j])

        if length[0] < length[1]:
            mc.select(upperVertices[0])
            mc.move(cornerPoints[0][0], cornerPoints[0][1], cornerPoints[0][2], ws=True)
            cornerA = []
            (cornerA.append(upperVertices[0]), cornerA.append(vertices[0]))
            mc.select(upperVertices[1])
            mc.move(cornerPoints[1][0], cornerPoints[1][1], cornerPoints[1][2], ws=True)
            cornerB = []
            (cornerB.append(upperVertices[1]), cornerB.append(vertices[1]))
        else:
            mc.select(upperVertices[1])
            mc.move(cornerPoints[0][0], cornerPoints[0][1], cornerPoints[0][2], ws=True)
            cornerA = []
            (cornerA.append(upperVertices[1]), cornerA.append(vertices[0]))
            mc.select(upperVertices[0])
            mc.move(cornerPoints[1][0], cornerPoints[1][1], cornerPoints[1][2], ws=True)
            cornerB = []
            (cornerB.append(upperVertices[0]), cornerB.append(vertices[1]))
        mc.select(cornerA, cornerB)
        mc.polyMergeVertex(d=0.001)
        mc.undoInfo(cck=True)

    def check_component_type(self, selection):
        if '.vtx[' in selection[0]:
            return 'vertice'
        if '.e[' in selection[0]:
            return 'edge'
        if '.f[' in selection[0]:
            return 'face'

    def buKi_append_plus(self):
        mc.undoInfo(ock=True)
        currentSel = mc.ls(sl=True)
        meshName = mc.ls(currentSel, o=True)
        mc.delete(meshName, ch=True)
        if len(currentSel) != 1:
            return
        if self.check_component_type(currentSel) == 'vertice':
            edgeSel = mc.ls(mc.polyListComponentConversion(currentSel, te=True), fl=True)
            borderEdges = []
            for i in edgeSel:
                faceConv = mc.ls(mc.polyListComponentConversion(i, tf=True), fl=True)
                if len(faceConv) == 1:
                    borderEdges.append(i)

            mc.select(borderEdges[0])
            V1 = mc.ls(mc.polyListComponentConversion(mc.ls(sl=True), tv=True), fl=True)
            V1.remove(currentSel[0])
            P1 = mc.pointPosition(V1[0], w=True)
            P2 = mc.pointPosition(currentSel[0], w=True)
            mc.select(borderEdges[1])
            V3 = mc.ls(mc.polyListComponentConversion(mc.ls(sl=True), tv=True), fl=True)
            V3.remove(currentSel[0])
            P3 = mc.pointPosition(V3[0], w=True)
            P4 = self.MAS_list_points(P2, P1, '-')
            P4 = self.MAS_list_points(P4, -1, '*')
            P4 = self.MAS_list_points(P3, P4, '+')
            edgeNum1 = re.split('\\[(.*?)\\]', borderEdges[0])
            edgeNum2 = re.split('\\[(.*?)\\]', borderEdges[1])
            mm.eval('polyAppend -ch 0 -ed %s -ed %s %s;' % (edgeNum2[1], edgeNum1[1], meshName[0]))
            mc.select(V1, V3)
            mm.eval('ConvertSelectionToContainedEdges;')
            containEdge = mc.ls(sl=True)
            mc.polySubdivideEdge(containEdge, ws=False, s=False, dv=1, ch=False)
            V4 = mc.ls(mc.polyListComponentConversion(mc.ls(sl=True), tv=True), fl=True)
            V4.remove(V1[0])
            V4.remove(V3[0])
            mc.move(P4[0], P4[1], P4[2], V4, ws=True, a=True)
            if len(mc.ls(mc.polyListComponentConversion(V1, te=True), fl=True)) == 4 and len(mc.ls(mc.polyListComponentConversion(V3, te=True), fl=True)) == 4:
                mc.select(V3)
            elif len(mc.ls(mc.polyListComponentConversion(V1, te=True), fl=True)) == 4:
                mc.select(V1)
            else:
                mc.select(V3)
        if self.check_component_type(currentSel) == 'edge':
            currentSel = mc.ls(sl=True, fl=True)
            if len(currentSel) != 1:
                return
            mc.GrowPolygonSelectionRegion()
            edgeSel = mc.ls(sl=True, fl=True)
            borderEdges = []
            for i in edgeSel:
                faceConv = mc.ls(mc.polyListComponentConversion(i, tf=True), fl=True)
                if len(faceConv) == 1:
                    borderEdges.append(i)

            borderEdges.remove(currentSel[0])
            mc.select(borderEdges)
            mc.polyBridgeEdge(ch=False, sma=30, dv=0)
            mc.select(borderEdges)
            mc.select(currentSel, add=True)
            tempEdges = mc.ls(sl=True, fl=True)
            tempVertices = mc.ls(mc.polyListComponentConversion(tempEdges, tv=True), fl=True)
            mc.select(tempVertices)
            mc.ConvertSelectionToContainedFaces()
            newEdge = mc.ls(mc.polyListComponentConversion(mc.ls(sl=True), te=True), fl=True)
            newEdge.remove(borderEdges[0])
            newEdge.remove(borderEdges[1])
            newEdge.remove(currentSel[0])
            mc.select(newEdge)
        mc.undoInfo(cck=True)

    def buki_append_ring_loop(self):
        endEdges = mc.ls(sl=True, fl=True)
        meshName = mc.ls(endEdges, o=True)
        mc.delete(meshName, ch=True)
        loop = mc.polySelectSp(endEdges[0], l=True)
        loop = mc.ls(sl=True, fl=True)
        loop.remove(endEdges[0])
        loop.remove(endEdges[1])
        try:
            mc.select(loop)
            mc.polyBridgeEdge(ch=False, sma=30, dv=0)
        except:
            om.MGlobal.displayWarning('Not the same edge count')

    def buKi_combine(self):
        mc.undoInfo(ock=True)
        combine_input = mc.ls(sl=True)
        first_mesh_name = combine_input[0]
        if len(combine_input) == 0:
            mc.warning('Please select 2 polygonal objects')
            return
        if len(combine_input) == 1 and self.is_group_check(combine_input[0]) == False:
            mc.warning('Please select 2 polygonal objects')
            return
        is_duplicate = False
        if '|' in first_mesh_name:
            temp_list = first_mesh_name.split('|')
            first_mesh_name = temp_list[(-1)]
            is_duplicate = True
        if len(combine_input) == 1 and self.is_group_check(combine_input[0]) == True:
            mc.polyUnite(ch=False, cp=True)
            mc.rename('%s' % first_mesh_name)
        else:
            if self.buKi_mesh_combine_orientation_cb.isChecked() == True:
                self.pivot_store()
            combine_parent = self.get_object_parent(combine_input[0])
            mc.polyUnite(n='RS_TmpCombineName', cp=True)
            combined_object = mc.ls(sl=True)
            if combine_parent:
                mc.parent(combined_object, combine_parent[0])
            mc.delete(ch=True)
            if is_duplicate == False:
                mc.rename('%s' % first_mesh_name)
            if is_duplicate == True:
                mc.rename('%s_comb' % first_mesh_name)
            if self.buKi_mesh_combine_orientation_cb.isChecked() == True:
                self.pivot_assign()
        mc.undoInfo(cck=True)

    def buKi_separate(self):
        mc.undoInfo(ock=True)
        object_list = mc.filterExpand(sm=12)
        SeparateStep = 0
        if object_list == None:
            om.MGlobal.displayWarning('Please select a polygon object')
            return
        else:
            for i in object_list:
                if '|' in i:
                    temp_list = i.split('|')
                    mesh_name = temp_list[(-1)]
                else:
                    mesh_name = i
                mc.select(i)
                mc.makeIdentity(i, a=True, t=True, r=True, s=True)
                object_parent = self.get_object_parent(i)
                mc.polySeparate(ch=False, rs=False, n='%s_Sep' % mesh_name)
                separated_objects = mc.ls(sl=True, fl=True)
                separated_parent = self.get_object_parent(separated_objects[0])
                for i in separated_objects:
                    mc.CenterPivot()
                    if object_parent == None:
                        mc.parent(i, w=True)
                    else:
                        try:
                            mc.parent(i, object_parent, relative=True)
                        except:
                            pass

                mc.delete(separated_parent)
                SeparateStep += 1

            mc.undoInfo(cck=True)
            return

    def pivot_position(self, location):
        object_list = mc.ls(sl=True)
        for i in object_list:
            bbox = mc.exactWorldBoundingBox(i)
            if location == 'top':
                pivot = [(bbox[0] + bbox[3]) / 2, bbox[4], (bbox[2] + bbox[5]) / 2]
            elif location == 'bottom':
                pivot = [(bbox[0] + bbox[3]) / 2, bbox[1], (bbox[2] + bbox[5]) / 2]
            elif location == 'front':
                pivot = [(bbox[0] + bbox[3]) / 2, (bbox[1] + bbox[4]) / 2, bbox[5]]
            elif location == 'back':
                pivot = [(bbox[0] + bbox[3]) / 2, (bbox[1] + bbox[4]) / 2, bbox[2]]
            elif location == 'left':
                pivot = [bbox[0], (bbox[1] + bbox[4]) / 2, (bbox[2] + bbox[5]) / 2]
            elif location == 'right':
                pivot = [bbox[3], (bbox[1] + bbox[4]) / 2, (bbox[2] + bbox[5]) / 2]
            mc.xform(i, piv=pivot, ws=True)

    def buKi_group_all(self):
        mc.group()
        group_name = mc.ls(sl=True)
        mc.rename(group_name, '%s_grp' % group_name[0])

    def buKi_group_individual(self):
        mc.undoInfo(ock=True)
        object_list = mc.ls(sl=True, fl=True)
        for i in object_list:
            mc.group(i, n='%s_grp' % i)

        mc.undoInfo(cck=True)

    def buKi_quad_fill(self):
        mc.undoInfo(ock=True)
        edgeSelection = mc.ls(os=True)
        cornerEdges = []
        for edge in edgeSelection:
            test = ('%s' % edge).split('.e')
            number = test[1]
            number = number[1:]
            number = number[:-1]
            cornerEdges.append(int(number))

        mc.polySelect(ebp=(cornerEdges[0], cornerEdges[1]))
        rowA = mc.ls(sl=True, fl=True)
        mc.polySelect(ebp=(cornerEdges[2], cornerEdges[3]))
        rowB = mc.ls(sl=True, fl=True)
        mc.polySelect(ebp=(cornerEdges[0], cornerEdges[2]))
        sideA = mc.ls(sl=True, fl=True)
        mc.polySelect(ebp=(cornerEdges[1], cornerEdges[3]))
        sideB = mc.ls(sl=True, fl=True)
        for i in edgeSelection:
            if i in rowA:
                rowA.remove(i)
            if i in rowB:
                rowB.remove(i)
            if i in sideA:
                sideA.remove(i)
            if i in sideB:
                sideB.remove(i)

        divisionAmount = len(sideA) - 1
        mc.select(rowA, rowB)
        mc.polyBridgeEdge(dv=divisionAmount, ch=1, ctp=0, twt=0, tp=1, sma=30, d=0, sd=0, td=0)
        mc.select(edgeSelection[0], edgeSelection[2])
        self.buki_append_ring_loop()
        mc.select(edgeSelection[1], edgeSelection[3])
        self.buki_append_ring_loop()
        mc.undoInfo(cck=True)

    def buKi_forty_five_mesh_angle_confirm(self, orignal_selection):
        pressed_button = mc.confirmDialog(title='Options', message='How do you want to proceed?', button=[
         'Accept', 'Opposite', 'Undo'], icon='question', defaultButton='Accept', cancelButton='Undo', dismissString='Undo')
        self.buKi_forty_five_mesh_angle_btn_options(pressed_button, orignal_selection)

    def buKi_forty_five_mesh_angle_btn_options(self, pressed_button, original_selection):
        if pressed_button == 'Undo':
            mc.undo()
        if pressed_button == 'Opposite':
            mc.undo()
            mc.select(original_selection)
            self.buKi_forty_five_mesh_angle('negative', True)

    def buKi_forty_five_mesh_angle(self, direction, opposite_check):
        mc.undoInfo(ock=True)
        grid_origin = [
         0, 0, 0]
        edges = []
        faces = []
        original_selection = mc.ls(sl=True, fl=True)
        for i in original_selection:
            if '.e[' in i:
                edges.append(i)
            elif '.f[' in i:
                faces.append(i)

        if len(edges) != 1 or len(faces) < 1 or edges == []:
            om.MGlobal.displayWarning('Please select 1 Edge and at least 1 Face')
        else:
            vertices_pivot = mc.ls(mc.polyListComponentConversion(edges, tv=True), fl=True)
            vertices_all = mc.ls(mc.polyListComponentConversion(faces, tv=True), fl=True)
            pivot_PointA = mc.xform(vertices_pivot[0], q=True, ws=True, t=True)
            pivot_PointB = mc.xform(vertices_pivot[1], q=True, ws=True, t=True)
            points_list = list(set(vertices_all) - set(vertices_pivot))
            if direction == 'negative':
                pivot_vector = self.MAS_list_points(pivot_PointA, pivot_PointB, '-')
            elif direction == 'positive':
                pivot_vector = self.MAS_list_points(pivot_PointB, pivot_PointA, '-')
            for i in points_list:
                currentPoint = mc.xform(i, q=True, ws=True, t=True)
                nc = self.MAS_list_points(currentPoint, pivot_vector, '+')
                fb = self.MAS_list_points(pivot_PointA, currentPoint, '-')
                length_value = self.calc_length(grid_origin, fb)
                normalA = self.calc_normal(fb, length_value)
                normalB = self.calc_normal(pivot_vector, length_value)
                cross_product = self.calc_cross_product(normalA, normalB)
                new_point_location_temp = self.MAS_list_points(cross_product, length_value, '*')
                new_point_location = self.MAS_list_points(currentPoint, new_point_location_temp, '+')
                mc.move(new_point_location[0], new_point_location[1], new_point_location[2], i, ws=True, a=True)

        mc.select(cl=True)
        mc.select(faces)
        mc.undoInfo(cck=True)
        mc.refresh()
        if opposite_check == False:
            self.buKi_forty_five_mesh_angle_confirm(original_selection)

    def buKi_mirror(self, axis, mirror_type):
        x = 1
        y = 1
        z = 1
        if axis == 0:
            x = -1
        if axis == 1:
            y = -1
        if axis == 2:
            z = -1
        mc.duplicate(rr=True)
        if mirror_type == 'World':
            mc.scale(x, y, z, p=(0, 0, 0), r=True)
        else:
            mc.scale(x, y, z, r=True)
        mc.makeIdentity(a=True, t=True, r=True, s=True, n=0, pn=True, jo=True)
        if mirror_type == 'World' and axis == 0:
            mc.SelectHierarchy()
            self.buKi_search_replace_swap_L_R()

    def topology_message(self, number, text, original_selection):
        if number:
            om.MGlobal.displayInfo('Info: %s %s' % (number, text))
        else:
            om.MGlobal.displayInfo('%s info: Nothing found or nothing is selected.' % text)
            mc.select(original_selection)

    def buKi_topology_triangles(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        mc.polySelectConstraint(m=3, t=8, sz=1)
        mc.polySelectConstraint(dis=True)
        selected_polys = mc.polyEvaluate(fc=True)
        self.topology_message(int(selected_polys), 'Triangle(s)', original_selection)

    def buKi_topology_quads(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        mc.polySelectConstraint(m=3, t=8, sz=2)
        mc.polySelectConstraint(dis=True)
        selected_polys = mc.polyEvaluate(fc=True)
        self.topology_message(int(selected_polys), 'Quad(s)', original_selection)

    def buKi_topology_ngons(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        mc.polySelectConstraint(m=3, t=8, sz=3)
        mc.polySelectConstraint(dis=True)
        selected_polys = mc.polyEvaluate(fc=True)
        self.topology_message(int(selected_polys), 'N-Gon(s)', original_selection)

    def buKi_topology_concave(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        mc.polySelectConstraint(m=3, t=8, c=1)
        mc.polySelectConstraint(dis=True)
        selected_polys = mc.polyEvaluate(fc=True)
        self.topology_message(int(selected_polys), 'Concave(s)', original_selection)

    def buKi_topology_lamina(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        p = mc.polyInfo(lf=True)
        if p == None:
            selected_polys = 0
            mc.select(d=True)
        else:
            mc.select(p)
            selected_polys = mc.polyEvaluate(fc=True)
        self.topology_message(int(selected_polys), 'Lamina', original_selection)
        return

    def buKi_topology_holes(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        mc.polySelectConstraint(m=3, t=8, h=1)
        mc.polySelectConstraint(dis=True)
        selected_polys = mc.polyEvaluate(fc=True)
        self.topology_message(int(selected_polys), 'Hole(s)', original_selection)

    def buKi_topology_manifold(self):
        original_selection = mc.ls(sl=True)
        mc.selectMode(q=True, co=True)
        manifold_count = 0
        selected_polys = mm.eval('polyCleanupArgList 4 { "0","2","1","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","1","0","0" };')
        for i in selected_polys:
            manifold_count = manifold_count + 1

        mc.select(selected_polys)
        self.topology_message(manifold_count, 'Non-Manifold(s)', original_selection)

    def buKi_select_by_angle(self):
        self.targetGeom = []
        selList = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selList)
        selListIter = om.MItSelectionList(selList)
        while not selListIter.isDone():
            components = om.MObject()
            dagPath = om.MDagPath()
            selListIter.getDagPath(dagPath, components)
            if components.isNull():
                selListIter.next()
                continue
            compListFn = om.MFnComponent(components)
            compType = compListFn.componentType()
            if compType == om.MFn.kMeshPolygonComponent:
                compListFn = om.MFnSingleIndexedComponent(components)
                ids = om.MIntArray()
                compListFn.getElements(ids)
                selItem = SelectionItem(dagPath, ids)
                self.targetGeom.append(selItem)
            selListIter.next()

        try:
            self.geometryData.generateGeometryInfo(self.targetGeom)
        except AttributeError:
            self.geometryData = GeometryData()
            self.geometryData.generateGeometryInfo(self.targetGeom)

        self.angle_select_valid_geometry()

    def angle_select_valid_geometry(self, *args):
        min = 0
        try:
            max = self.buKi_select_angle_dSpinBox.value()
        except:
            max = 15

        mm.eval('changeSelectMode -component; setComponentPickMask "All" 0; setComponentPickMask "Facet" true;')
        validEdges = self.geometryData.getValidEdges(min, max)
        om.MGlobal.setActiveSelectionList(validEdges)

    def buKi_select_nth_edge(self, nth_type):
        nth_number = self.buKi_select_nthEdge_spinBox.value()
        mm.eval('polySelectEdgesEveryN "%s" %s;' % (nth_type, nth_number))

    def buKi_fill_select_proceed_check(self, _=False):
        if mc.window(self.buKi_fill_proceed_win_ID, exists=True):
            mc.deleteUI(self.buKi_fill_proceed_win_ID, wnd=True)
            mc.windowPref(self.buKi_fill_proceed_win_ID, r=True)
        mc.window(self.buKi_fill_proceed_win_ID, s=False, tlb=True, t='Proceed with selection?')
        mc.columnLayout(adj=True)
        mc.rowLayout(nc=1)
        mc.text(l='', h=10)
        mc.setParent('..')
        mc.rowLayout(nc=3)
        mc.text(l='', w=50)
        mc.button(l='OK', h=30, w=80, c=lambda *_: self.buKi_fill_select_shell())
        mc.text(l='', w=50)
        mc.setParent(top=True)
        mc.showWindow(self.buKi_fill_proceed_win_ID)
        mc.window(self.buKi_fill_proceed_win_ID, e=True, w=190, h=60)

    def buKi_fill_prepare_shell(self):
        self.buKi_fill_proceed_win_ID = 'fill_selection_check_win'
        fill_edges = mc.ls(sl=True)
        fill_object = mc.ls(sl=True, o=True)
        self.fill_object_history = mc.listHistory(fill_object[0], pdo=True)
        selKitUVSetTemp = mc.polyUVSet(fill_object[0], q=True, auv=True)
        if "u'buKi_tmp_fill_shell'" in selKitUVSetTemp:
            mc.polyUVSet(d=True, uvs='buKi_tmp_fill_shell')
        elif "u'buKi_tmp_fill_shell1'" in selKitUVSetTemp:
            mc.polyUVSet(d=True, uvs='buKi_tmp_fill_shell1')
        elif "u'___delete___buKi_tmp_fill_shell___'" in selKitUVSetTemp:
            mc.polyUVSet(d=True, uvs='___delete___buKi_tmp_fill_shell___')
        mc.polyProjection(fill_object[0] + '.f[*]', t='Planar', ibd=True, cm=True, uvs='buKi_tmp_fill_shell', md='x')
        mc.polyUVSet(fill_object[0], cuv=True, uvs='buKi_tmp_fill_shell')
        mc.polyMapCut(fill_edges)
        mc.select(cl=True)
        mm.eval('doMenuComponentSelection("%s", "meshUVShell");' % fill_object[0])
        mc.scriptJob(e=('SelectionChanged', self.buKi_fill_select_proceed_check), ro=True)

    def buKi_fill_select_shell(self):
        mc.deleteUI(self.buKi_fill_proceed_win_ID, wnd=True)
        fill_object = mc.ls(sl=True, o=True)
        fill_object = mc.listRelatives(fill_object[0], p=True)
        fill_selection = mc.ls(sl=True)
        mc.polySelectConstraint(sh=False)
        selKitUVSetTemp = mc.polyUVSet(fill_object[0], q=True, auv=True)
        mc.polyUVSet(fill_object[0], d=True, uvs='buKi_tmp_fill_shell')
        mc.polyUVSet(fill_object[0], cuv=True, uvs='%s' % selKitUVSetTemp[0])
        if self.fill_object_history == None:
            mc.delete(fill_object[0], ch=True)
        else:
            fill_object_history_tmp = mc.listHistory(fill_object[0], pdo=True)
            for i in fill_object_history_tmp:
                if i not in self.fill_object_history:
                    mc.delete(i)

        mm.eval('doMenuComponentSelection("%s", "facet");' % fill_object[0])
        mc.select(fill_selection, r=True)
        return

    def buKi_select_by_percentage(self):
        percentage_value = self.buKi_select_percentage_spinBox.value()
        object_selection = mc.ls(sl=True, o=True)
        if object_selection:
            percentage = int(len(object_selection) * percentage_value / 100)
            temp_list = []
            while len(temp_list) <= percentage:
                temp_value = random.choice(object_selection)
                temp_list.append(temp_value)
                object_selection.remove(temp_value)

            mc.select(temp_list)
        else:
            om.MGlobal.displayWarning('Please select polygon objects.')

    def buKi_select_by_component_count(self, cc_type, component_count):
        if cc_type == 'v':
            om.MGlobal.displayInfo('Number of vertices: %s' % component_count)
        if cc_type == 'e':
            om.MGlobal.displayInfo('Number of edges: %s' % component_count)
        if cc_type == 'f':
            om.MGlobal.displayInfo('Number of faces: %s' % component_count)
        if cc_type == 'uv':
            om.MGlobal.displayInfo('Number of UVs: %s' % component_count)
        progress_control = ''
        progress_control_check = False
        geometry_list = mc.ls(g=True, fl=True)
        component_count_list_max = len(geometry_list)
        geometry_list_temp = []
        component_flag = {cc_type: True}
        if component_count_list_max > 200:
            progress_control = mc.progressWindow(t='In progress...', ii=True, maxValue=component_count_list_max)
            progress_control_check = True
        for i in geometry_list:
            mc.select(i)
            component_check_count = mc.polyEvaluate(**component_flag)
            if component_check_count == component_count:
                geometry_list_temp.append(i)
            if progress_control_check == True and mc.progressWindow(q=True, ic=True):
                break
                mc.progressWindow(progress_control, edit=True, ep=True)
            elif progress_control_check == True:
                mc.progressWindow(progress_control, edit=True, step=1)

        mc.progressWindow(progress_control, edit=True, ep=True)
        mc.select(geometry_list_temp)

    def buKi_select_by_component_value(self, cc_type):
        minValue = self.buKi_select_cmptCountMin_spinBox.value()
        maxValue = self.buKi_select_cmptCountMax_spinBox.value()
        if self.buKi_select_cmptCountScope_selection_rb.isChecked():
            mc.SelectHierarchy()
            nSelection = mc.ls(sl=True, fl=True)
        else:
            nSelection = mc.ls(g=True, fl=True)
        hitList = []
        if cc_type == 'f':
            resultList = self.buKi_select_by_component_face(minValue, maxValue, hitList, nSelection)
        if cc_type == 'v':
            resultList = self.buKi_select_by_component_vertice(minValue, maxValue, hitList, nSelection)
        if cc_type == 'e':
            resultList = self.buKi_select_by_component_edge(minValue, maxValue, hitList, nSelection)
        if cc_type == 'uv':
            resultList = self.buKi_select_by_component_uv(minValue, maxValue, hitList, nSelection)
        mc.select(resultList)

    def buKi_select_by_component_face(self, minValue, maxValue, hitList, nSelection):
        for i in nSelection:
            componentCount = mc.polyEvaluate(i, f=True)
            if componentCount >= minValue and componentCount <= maxValue:
                hitList.append(i)

        return hitList

    def buKi_select_by_component_edge(self, minValue, maxValue, hitList, nSelection):
        for i in nSelection:
            componentCount = mc.polyEvaluate(i, e=True)
            if componentCount >= minValue and componentCount <= maxValue:
                hitList.append(i)

        return hitList

    def buKi_select_by_component_vertice(self, minValue, maxValue, hitList, nSelection):
        for i in nSelection:
            componentCount = mc.polyEvaluate(i, v=True)
            if componentCount >= minValue and componentCount <= maxValue:
                hitList.append(i)

        return hitList

    def buKi_select_by_component_uv(self, minValue, maxValue, hitList, nSelection):
        for i in nSelection:
            componentCount = mc.polyEvaluate(i, uv=True)
            if componentCount >= minValue and componentCount <= maxValue:
                hitList.append(i)

        return hitList

    def buKi_select_by_name(self):
        user_text_input = self.buKi_select_name_lineEdit.text()
        if user_text_input:
            if self.buKi_select_nameScope_scene_rb.isChecked():
                mc.select(all=True)
                mc.select(hi=True)
            if self.buKi_select_nameScope_hierarchy_rb.isChecked():
                mc.select(hi=True)
            list_selection = mc.ls(sl=True)
            temp_list = []
            for i in list_selection:
                if user_text_input in i:
                    temp_list.append(i)

            mc.select(temp_list)

    def buKi_select_by_type(self):
        temp_list = []
        if self.buKi_select_typeScope_hierarchy_rb.isChecked():
            mc.select(hi=True)
        elif self.buKi_select_typeScope_scene_rb.isChecked():
            mc.select(all=True)
            mc.select(hi=True)
        if self.buKi_select_type_group_rb.isChecked():
            self.buKi_select_groups()
        else:
            if self.buKi_select_type_geometry_rb.isChecked():
                checked_type = ('mesh', 'nurbsSurface')
            if self.buKi_select_type_curve_rb.isChecked():
                checked_type = ('nurbsCurve', 'bezierCurve')
            if self.buKi_select_type_light_rb.isChecked():
                checked_type = 'light'
            if self.buKi_select_type_locator_rb.isChecked():
                checked_type = 'locator'
            if self.buKi_select_type_camera_rb.isChecked():
                checked_type = 'camera'
            selection_list = mc.ls(sl=True, type=checked_type)
            mc.select(selection_list)
            temp_list = mc.listRelatives(p=True)
            mc.select(temp_list)

    def buKi_layout_place(self):
        place_ctx = 'buKi_GetWorldPointCtx'
        source_indexes = [ x.row() for x in self.buKi_mesh_place_source_list.selectedIndexes() ]
        if len(source_indexes) < 1:
            om.MGlobal.displayWarning('Please add to and/or select an item from the list.')
            return
        self.place_sources = []
        for i in range(0, len(source_indexes)):
            current_sel = self.buKi_mesh_place_source_list.selectedIndexes()[i]
            self.place_sources.append(current_sel.data())

        self.place_sources_max = len(self.place_sources)
        self.place_counter = 0
        if mc.draggerContext(place_ctx, exists=True):
            mc.deleteUI(place_ctx)
        mc.draggerContext(place_ctx, pc=self.buKi_layout_place_onPress, n=place_ctx, cursor='crossHair')
        mc.setToolTo(place_ctx)

    def buKi_layout_place_onPress(self):
        if self.buKi_mesh_place_random_cb.isChecked():
            self.place_counter = random.randrange(0, self.place_sources_max, 1)
        elif self.place_counter == self.place_sources_max:
            self.place_counter = 0
        target = self.buKi_object_under_cursor()
        mc.select(target)
        mc.makeLive()
        place_world_position = mc.autoPlace(um=True)
        mc.makeLive()
        mc.select(self.place_sources[self.place_counter])
        mc.duplicate()
        temp_move_obj = mc.ls(sl=True)
        mc.move(place_world_position[0], place_world_position[1], place_world_position[2], rpr=True)
        mc.select(target)
        mc.select(temp_move_obj, add=True)
        mc.normalConstraint(w=1, aim=(0, 1, 0), u=(0, 1, 0), wut='vector', wu=(0, 1,
                                                                               0))
        mc.delete('%s_normalConstraint1' % temp_move_obj[0])
        mc.select(target)
        self.place_counter += 1

    def buKi_layout_paint(self):
        mc.undoInfo(ock=True)
        paint_ctx = 'buKi_GetWorldPointCtx'
        source_indexes = [ x.row() for x in self.buKi_mesh_paint_source_list.selectedIndexes() ]
        if len(source_indexes) < 1:
            om.MGlobal.displayWarning('Please add to and/or select an item from the list.')
            return
        self.paint_sources = []
        for i in range(0, len(source_indexes)):
            current_sel = self.buKi_mesh_paint_source_list.selectedIndexes()[i]
            self.paint_sources.append(current_sel.data())

        self.paint_sources_max = len(self.paint_sources)
        self.paint_counter = 0
        if mc.draggerContext(paint_ctx, exists=True):
            mc.deleteUI(paint_ctx)
        mc.draggerContext(paint_ctx, dc=self.buKi_layout_paint_onPress, n=paint_ctx, cursor='crossHair')
        mc.setToolTo(paint_ctx)
        mc.undoInfo(cck=True)

    def buKi_layout_paint_onPress(self):
        if self.buKi_mesh_paint_random_cb.isChecked():
            self.paint_counter = random.randrange(0, self.paint_sources_max, 1)
        elif self.paint_counter == self.paint_sources_max:
            self.paint_counter = 0
        target = self.buKi_object_under_cursor()
        mc.select(target)
        mc.makeLive()
        paint_world_position = mc.autoPlace(um=True)
        mc.makeLive()
        mc.select(self.paint_sources[self.paint_counter])
        mc.duplicate()
        temp_move_obj = mc.ls(sl=True)
        mc.move(paint_world_position[0], paint_world_position[1], paint_world_position[2], rpr=True)
        mc.select(target)
        mc.select(temp_move_obj, add=True)
        mc.normalConstraint(w=1, aim=(0, 1, 0), u=(0, 1, 0), wut='vector', wu=(0, 1,
                                                                               0))
        mc.delete('%s_normalConstraint1' % temp_move_obj[0])
        mc.select(target)
        sleep_value = self.buKi_mesh_paint_time_dSpinBox.value()
        time.sleep(sleep_value)
        self.paint_counter += 1

    def buKi_layout_distribute(self):
        mc.undoInfo(ock=True)
        modifier = mc.getModifiers()
        spacing_value = self.buKi_mesh_distribute_spacing_dSpinBox.value()
        if modifier & 1 > 0:
            direction = -1
        else:
            direction = 1
        if modifier & 8 > 0:
            axis_direction = 1
        else:
            if modifier & 4 > 0:
                axis_direction = 2
            else:
                axis_direction = 0
            current_selection = mc.ls(sl=True, fl=True)
            if len(current_selection) < 2:
                om.MGlobal.displayWarning('Please select 2 or more objects.')
                return
        move_x = 0
        move_y = 0
        move_z = 0
        if self.buKi_mesh_distribute_bb_rb.isChecked():
            move_sum = 0
            check_iteration = 1
            previous_length = 0
            half_difference = 0
            for i in current_selection:
                mc.select(i)
                axis_length = self.get_bounding_box(i)
                if previous_length == 0 or previous_length == axis_length[axis_direction]:
                    move_button_response = axis_length[axis_direction]
                if previous_length > 0 and axis_length[axis_direction] > previous_length:
                    half_difference = (axis_length[axis_direction] - previous_length) / 2
                    move_button_response = axis_length[axis_direction] + half_difference
                if previous_length > 0 and axis_length[axis_direction] < previous_length:
                    half_difference = (previous_length - axis_length[axis_direction]) / -2
                    move_button_response = axis_length[axis_direction] + half_difference
                if modifier & 8 > 0:
                    move_y = (move_sum + half_difference) * direction
                elif modifier & 4 > 0:
                    move_z = (move_sum + half_difference) * direction
                else:
                    move_x = (move_sum + half_difference) * direction
                if check_iteration == 1:
                    pass
                else:
                    mc.move(move_x, move_y, move_z, os=False, r=True)
                move_sum += move_button_response + spacing_value
                check_iteration += 1
                half_difference = 0
                previous_length = axis_length[axis_direction]

        if self.buKi_mesh_distribute_value_rb.isChecked():
            move = 0
            move_value = self.buKi_mesh_distribute_moveValue_dSpinBox.value()
            for i in current_selection:
                mc.select(i)
                if move == 0:
                    move = move + move_value
                else:
                    if modifier & 8 > 0:
                        move_y = move * direction
                    elif modifier & 4 > 0:
                        move_z = move * direction
                    else:
                        move_x = move * direction
                    mc.move(move_x, move_y, move_z, os=False, r=True)
                    move = move + move_value

        mc.select(current_selection)
        mc.undoInfo(cck=True)

    def buKi_layout_duplicator(self):
        mc.undoInfo(ock=True)
        current_selection = mc.ls(sl=True, fl=True)
        move_x = 0
        move_y = 0
        move_z = 0
        copy_value = self.buKi_mesh_duplicator_copies_spinBox.value()
        spacing_value = self.buKi_mesh_duplicator_spacing_dSpinBox.value()
        move_value = self.buKi_mesh_duplicator_moveValue_dSpinBox.value()
        for i in current_selection:
            modifier = mc.getModifiers()
            mc.select(i)
            axis_length = self.get_bounding_box(i)
            if self.buKi_mesh_duplicator_direction_cb.isChecked():
                self.object_orientation = True
            else:
                self.object_orientation = False
            if modifier & 8 > 0:
                duplication_axis = 1
            elif modifier & 4 > 0:
                duplication_axis = 2
            else:
                duplication_axis = 0
            if modifier & 1 > 0:
                duplication_direction = -1
            else:
                duplication_direction = 1
            mc.duplicate(i)
            if self.buKi_mesh_duplicator_bb_rb.isChecked():
                move_button_response = (axis_length[duplication_axis] + spacing_value) * duplication_direction
            if self.buKi_mesh_duplicator_value_rb.isChecked():
                move_button_response = (move_value + spacing_value) * duplication_direction
            if modifier & 8 > 0:
                move_y = move_button_response
            elif modifier & 4 > 0:
                move_z = move_button_response
            else:
                move_x = move_button_response
            mc.move(move_x, move_y, move_z, os=self.object_orientation, r=True)
            if copy_value > 1:
                for j in range(copy_value - 1):
                    mc.duplicate(st=True)

        mc.undoInfo(cck=True)

    def buKi_import_obj(self):
        plugin_check = mc.pluginInfo('objExport', query=True, l=True)
        if plugin_check == True:
            base_selection = mc.ls(sl=True, fl=True)
            file_path = self.buKi_get_file_path(4, 'Import', '*.obj')
            combined_temp = []
            for i in file_path:
                import_name = self.split_name(i, '/', -1)
                import_name = self.split_name(import_name, '.', 0)
                imported_object = mc.file(i, i=True, rnn=True)
                mc.select(imported_object[0])
                mc.rename('%s' % import_name)
                name_catch = mc.ls(sl=True)
                combined_temp.append(name_catch[0])

            if len(combined_temp) > 1:
                if self.buKi_import_obj_combined_rb.isChecked():
                    mc.select(combined_temp)
                    self.buKi_combine()
            if self.buKi_import_obj_blendshapes_rb.isChecked():
                if mc.objExists('blendShapes_grp') == True:
                    for i in combined_temp:
                        mc.parent(i, 'blendShapes_grp')

                else:
                    mc.select(combined_temp)
                    mc.group(n='blendShapes_grp')
                self.buKi_import_obj_as_blendshapes(base_selection[0], combined_temp)
        else:
            mc.warning('The objExport plugin is not loaded.')

    def buKi_import_obj_as_blendshapes(self, current_selection, blendshape_list):
        mc.select(current_selection)
        blendshape_name = self.buKi_get_blendshape_name()
        if blendshape_name == '':
            mc.blendShape(current_selection, at=True)
            blendshape_name = self.buKi_get_blendshape_name()
        for i in blendshape_list:
            blendshape_weights = mc.blendShape('%s' % blendshape_name, q=True, w=True)
            if blendshape_weights == None:
                blendshape_index = 1
            else:
                blendshape_index = len(blendshape_weights) + 1
            mc.blendShape('%s' % blendshape_name, e=True, tc=True, t=(
             '%s' % current_selection, blendshape_index, '%s' % i, 1.0), w=(blendshape_index, 0))

        mc.select('blendShapes_grp')
        mc.HideSelectedObjects()
        return

    def buKi_export_obj(self):
        plugin_check = mc.pluginInfo('objExport', query=True, l=True)
        if plugin_check == True:
            export_list = mc.ls(sl=True, fl=True)
            if self.buKi_export_obj_blendshapes_rb.isChecked():
                mc.select(export_list[0])
                blendshape_name = self.buKi_get_blendshape_name()
                if blendshape_name == '':
                    pass
                else:
                    export_weights = mc.listAttr('%s.w' % blendshape_name, m=True)
                    file_path = self.buKi_get_file_path(2, 'Save to', '*.obj')
                    for i in export_weights:
                        mc.setAttr('%s.%s' % (blendshape_name, i), 0)

                    for i in export_weights:
                        mc.setAttr('%s.%s' % (blendshape_name, i), 1)
                        mc.select(export_list[0])
                        if os.path.isfile('%s/%s.obj' % (file_path[0], i)):
                            check = self.warning_message(i)
                            if check == True:
                                self.buKi_write_file('%s/%s.obj' % (file_path[0], i), 'OBJexport')
                            else:
                                break
                        else:
                            self.buKi_write_file('%s/%s.obj' % (file_path[0], i), 'OBJexport')
                        mc.setAttr('%s.%s' % (blendshape_name, i), 0)

            if self.buKi_export_obj_separate_rb.isChecked():
                file_path = self.buKi_get_file_path(2, 'Save to', '*.obj')
                for i in export_list:
                    mc.select(i)
                    if os.path.isfile('%s/%s.obj' % (file_path[0], i)):
                        check = self.warning_message(i)
                        if check == True:
                            self.buKi_write_file('%s/%s.obj' % (file_path[0], i), 'OBJexport')
                        else:
                            continue
                    else:
                        self.buKi_write_file('%s/%s.obj' % (file_path[0], i), 'OBJexport')

            if self.buKi_export_obj_combined_rb.isChecked():
                file_path = self.buKi_get_file_path(0, 'Save as', '*.obj')
                self.buKi_write_file('%s' % file_path[0], 'OBJexport')
        else:
            mc.warning('The objExport plugin is not loaded.')

    def buKi_import_fbx(self):
        plugin_check = mc.pluginInfo('fbxmaya', query=True, l=True)
        if plugin_check == True:
            base_selection = mc.ls(sl=True, fl=True)
            file_path = self.buKi_get_file_path(4, 'Import', '*.fbx')
            for i in file_path:
                mc.file(i, i=True, rnn=True)

        else:
            mc.warning('The fbxmaya plugin is not loaded.')

    def buKi_export_fbx(self):
        plugin_check = mc.pluginInfo('fbxmaya', query=True, l=True)
        if plugin_check == True:
            export_list = mc.ls(sl=True, fl=True)
            if self.buKi_export_fbx_separate_rb.isChecked():
                file_path = self.buKi_get_file_path(2, 'Save to', '*.fbx')
                for i in export_list:
                    mc.select(i)
                    if os.path.isfile('%s/%s.fbx' % (file_path[0], i)):
                        check = self.warning_message(i)
                        if check == True:
                            self.buKi_write_file('%s/%s.fbx' % (file_path[0], i), 'FBX export')
                        else:
                            continue
                    else:
                        self.buKi_write_file('%s/%s.fbx' % (file_path[0], i), 'FBX export')

            if self.buKi_export_fbx_single_rb.isChecked():
                file_path = self.buKi_get_file_path(0, 'Save as', '*.fbx')
                self.buKi_write_file('%s' % file_path[0], 'FBX export')
        else:
            mc.warning('The fbxmaya plugin is not loaded.')

    def buKi_export_abc(self):
        plugin_check = mc.pluginInfo('AbcImport', query=True, l=True)
        startFrame = self.buKi_export_abc_startFrame_spinBox.value()
        endFrame = self.buKi_export_abc_endFrame_spinBox.value()
        if plugin_check == True:
            export_list = mc.ls(sl=True, fl=True)
            if self.buKi_export_abc_single_rb.isChecked():
                file_path = self.buKi_get_file_path(0, 'Save as', '*.abc')
                file_path = '"%s"' % file_path[0]
                abc_string = '-frameRange %s %s -uvWrite -writeUVSets -dataFormat ogawa -file %s' % (startFrame, endFrame, file_path)
                for i in export_list:
                    abc_string = abc_string[:62] + '-root %s ' % i + abc_string[62:]

                mc.AbcExport(j=abc_string)
            if self.buKi_export_abc_separate_rb.isChecked():
                file_path = self.buKi_get_file_path(2, 'Save to', '*.abc')
                for i in export_list:
                    if os.path.isfile('%s/%s.abc' % (file_path[0], i)):
                        check = self.warning_message(i)
                        if check == True:
                            tmp_path = '"%s/%s.abc"' % (file_path[0], i)
                            abc_string = '-frameRange %s %s -uvWrite -writeUVSets -dataFormat ogawa -root %s -file %s' % (startFrame, endFrame, i, tmp_path)
                            mc.AbcExport(j=abc_string)
                        else:
                            continue
                    else:
                        tmp_path = '"%s/%s.abc"' % (file_path[0], i)
                        abc_string = '-frameRange %s %s -uvWrite -writeUVSets -dataFormat ogawa -root %s -file %s' % (startFrame, endFrame, i, tmp_path)
                        mc.AbcExport(j=abc_string)

        else:
            mc.warning('The AbcImport plugin is not loaded.')

    def buKi_import_abc(self):
        plugin_check = mc.pluginInfo('AbcImport', query=True, l=True)
        if plugin_check == True:
            base_selection = mc.ls(sl=True, fl=True)
            file_path = self.buKi_get_file_path(4, 'Import', '*.abc')
            list_position = 0
            for i in file_path:
                mc.AbcImport('%s' % file_path[list_position], m='import')
                list_position += 1

        else:
            mc.warning('The AbcImport plugin is not loaded.')

    def buKi_open_browser(self, site_code):
        if site_code == 'Documentation':
            mc.launch(web='https://www.rocket-square.com/docs')
        elif site_code == 'Website':
            mc.launch(web='http://www.rocket-square.com/')
        elif site_code == 'Gumroad':
            mc.launch(web='https://gumroad.com/eriklehmann')


class GeometryData():

    def __init__(self):
        self.polyData = []

    def generateGeometryInfo(self, objList):
        pi = math.pi
        normal1 = om.MVector()
        normal2 = om.MVector()
        connectedFaces = om.MIntArray()
        polyEdgesIds = om.MIntArray()
        edgeFaces = om.MIntArray()
        dummy = om.MScriptUtil()
        dummyIntPtr = dummy.asIntPtr()
        self.polyData = []
        for obj in objList:
            edgeIter = om.MItMeshEdge(obj.dagPath)
            faceIter = om.MItMeshPolygon(obj.dagPath)
            _mvector = om.MVector
            normalCache = [ _mvector() for _ in xrange(faceIter.count()) ]
            while not faceIter.isDone():
                faceIter.getNormal(normalCache[faceIter.index()], om.MSpace.kWorld)
                faceIter.next()

            edgeAnglesCache = array('d', [-1000] * edgeIter.count())
            i = 0
            while not edgeIter.isDone():
                cfLength = edgeIter.getConnectedFaces(connectedFaces)
                if cfLength == 2:
                    normal1 = normalCache[connectedFaces[0]]
                    normal2 = normalCache[connectedFaces[1]]
                    edgeAnglesCache[i] = normal1.angle(normal2) * 180 / pi
                i += 1
                edgeIter.next()

            objPolyData = ObjectPolyData()
            self.polyData.append(objPolyData)
            objPolyData.dagPath = obj.dagPath
            objPolyData.polygons = [ PolyData() for _ in xrange(faceIter.count()) ]
            i = 0
            faceIter.reset()
            while not faceIter.isDone():
                polyData = objPolyData.polygons[i]
                faceIter.getEdges(polyEdgesIds)
                for edgeId in polyEdgesIds:
                    edgeIter.setIndex(edgeId, dummyIntPtr)
                    cfLength = edgeIter.getConnectedFaces(edgeFaces)
                    if cfLength == 2:
                        otherFace = edgeFaces[1] if edgeFaces[0] == i else edgeFaces[0]
                        polyData.connectedFaces[otherFace] = edgeAnglesCache[edgeId]

                i += 1
                faceIter.next()

            for p in obj.polyIds:
                objPolyData.polygons[p].selected = True
                objPolyData.polygons[p].initSelection = True

    def growSelection(self, min, max):
        for obj in self.polyData:
            polysToGrow = []
            polysToGrowNextIter = [ i for i, poly in enumerate(obj.polygons) if poly.selected ]
            while True:
                selectionWasGrown = False
                polysToGrow = polysToGrowNextIter
                polysToGrowNextIter = []
                for polyId in polysToGrow:
                    for polyNeighbourId in obj.polygons[polyId].connectedFaces:
                        if min <= obj.polygons[polyId].connectedFaces[polyNeighbourId] <= max and not obj.polygons[polyNeighbourId].selected:
                            polysToGrowNextIter.append(polyNeighbourId)
                            obj.polygons[polyNeighbourId].selected = True
                            selectionWasGrown = True

                if not selectionWasGrown:
                    break

    def resetSelection(self):
        for obj in self.polyData:
            for poly in obj.polygons:
                poly.selected = poly.initSelection

    def getValidEdges(self, min, max):
        self.resetSelection()
        self.growSelection(min, max)
        selList = om.MSelectionList()
        compListFn = om.MFnSingleIndexedComponent()
        indexes = om.MIntArray()
        for obj in self.polyData:
            components = compListFn.create(om.MFn.kMeshPolygonComponent)
            indexes.clear()
            for i, poly in enumerate(obj.polygons):
                if poly.selected:
                    indexes.append(i)

            compListFn.addElements(indexes)
            selList.add(obj.dagPath, components)

        return selList


class PolyData():

    def __init__(self):
        self.selected = False
        self.initSelection = False
        self.connectedFaces = {}

    def __str__(self):
        endStr = '\n'
        outStr = ''
        outStr += 'initSelected = ' + str(self.initSelection) + ', selected = ' + str(self.selected) + endStr
        for key in self.connectedFaces:
            outStr += '[' + str(key) + '] = ' + str(self.connectedFaces[key]) + endStr

        return outStr


class ObjectPolyData():

    def __init__(self):
        self.dagPath = None
        self.polygons = []
        return

    def __str__(self):
        endStr = '\n'
        outStr = ''
        outStr += 'DagPath = ' + self.dagPath.fullPathName() + endStr
        for i, poly in enumerate(self.polygons):
            outStr += 'polyId = ' + str(i) + endStr
            outStr += str(poly) + endStr

        return outStr


class SelectionItem():

    def __init__(self, dagPath, polyIds):
        self.dagPath = dagPath
        self.polyIds = polyIds

    def __str__(self):
        endStr = '\n'
        outStr = ''
        outStr += 'DagPath = ' + self.dagPath.fullPathName() + endStr
        for i, elem in enumerate(self.polyIds):
            outStr += 'polyIds[' + str(i) + '] = ' + str(self.polyIds[i]) + endStr

        return outStr


if __name__ == '__main__':
    try:
        build_Kit.close()
        build_Kit.deleteLater()
    except:
        pass

    build_Kit = MainClass_BuildKit()
    build_Kit.show()