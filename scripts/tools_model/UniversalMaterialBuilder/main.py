# Universal Material Builder
# -*- coding: utf-8 -*-

# import modules
import os
import sys
import json
import webbrowser
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import *

import maya.cmds as cmds

from python.createDefaultTags import resetTags
from python.mayaRedshiftInterpreter import createRsMaterial
from python.mayaArnoldInterpreter import createAiMaterial
from python.mayaVrayInterpreter import createVrMaterial


# set important path variables
script_path = os.path.realpath(__file__)
script_path = os.path.split(script_path)[0]

# Main Window Class
class MainWindow(QMainWindow):

    # Define Window
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setAcceptDrops(True)
        self.main_window_width = 300
        self.main_window_height = 450
        self.main_window_pos_x = 60
        self.main_window_pos_y = 60
        self.mayaWindow = self.getMayaMainWindow()
        self.setParent(self.mayaWindow)
        self.setWindowFlags(Qt.Window)

        self.valid_image_ext = ["jpg", "jpeg", "png", "tif", "tiff", "exr", "hdr", "bmp", "tga"]
        self.initUI()

    #Get Maya Main Window
    def getMayaMainWindow(self):
        import shiboken2
        from maya import OpenMayaUI
        window = OpenMayaUI.MQtUtil.mainWindow()
        window = shiboken2.wrapInstance(int(window), QMainWindow)

        return window

    # Initilize Ui
    def initUI(self):
        # Main Window Style
        self.setWindowTitle("Universal Material Builder")
        self.setWindowIcon(QIcon(script_path + '\\icons\\logo.png'))
        self.setGeometry(self.main_window_pos_x, self.main_window_pos_y, self.main_window_width, self.main_window_height)
        self.setFixedWidth(self.main_window_width)

        self.settings = QSettings('fstrube', 'umb')
        geometry = self.settings.value('geometry')
        self.restoreGeometry(geometry)

        background_image_path = os.path.join(script_path, "icons", "drag_and_drop.png")
        background_image_path = background_image_path.replace("\\","/")
        windowStyle = "MainWindow {background-color: #2b2b2b; background-image: url('%s'); background-repeat: no-repeat;}" % (background_image_path)
        self.setStyleSheet(windowStyle)


        # Menu Bar Style
        self.menuBar().setStyleSheet("""
                QMenuBar {
                    background-color: rgb(49,49,49);
                    color: rgb(255,255,255);
                    border: 1px solid #000;
                }

                QMenuBar::item {
                    background-color: rgb(49,49,49);
                    color: rgb(255,255,255);
                }

                QMenuBar::item::selected {
                    background-color: rgb(30,30,30);
                }

                QMenu {
                    background-color: rgb(49,49,49);
                    color: rgb(255,255,255);
                    border: 1px solid #000;           
                }

                QMenu::item::selected {
                    background-color: rgb(30,30,30);
                }
            """)


        # Define Menu Bar
        self.menubar = self.menuBar()
        self.fileMenu = self.menubar.addMenu('App')
        self.tagsMenu = self.menubar.addMenu('Tags')
        self.aboutMenu = self.menubar.addMenu('About')
        self.empty = self.menubar.addMenu('                                  ')
        self.empty.setEnabled(False)
        #self.moreSettingsMenu = self.menubar.addMenu('More')

        #self.moreSettings = QAction(QIcon(script_path + "/icons/moreOptions.png"),"Options", self)
        #self.moreSettingsMenu.addAction(self.moreSettings)
        #self.moreSettings.triggered.connect(self.extraOptions)

        self.preferencesMenu = QAction('Preferences', self)
        self.resetMenu = QAction('Reset', self)
        self.closeMenu = QAction('Close', self)

        self.fileMenu.addAction(self.preferencesMenu)
        self.fileMenu.addAction(self.resetMenu)
        self.fileMenu.addAction(self.closeMenu)

        self.changeTagsMenu = QAction('Change Tags', self)
        self.resetTagsMenu = QAction('Reset Tags', self)

        self.tagsMenu.addAction(self.changeTagsMenu)
        self.tagsMenu.addAction(self.resetTagsMenu)

        self.updateMenu = QAction('Check for Updates', self)
        self.aboutMeMenu = QAction('About Me', self)

        self.aboutMenu.addAction(self.updateMenu)
        self.aboutMenu.addAction(self.aboutMeMenu)

        #My Tool bar

        self.toolBar = QToolBar("UMB Tools")
        self.toolBar.setIconSize(QSize(16,16))
        self.addToolBar(Qt.BottomToolBarArea, self.toolBar)

        self.combine2DTextures = QAction(QIcon(script_path + "/icons/combine2DTextures.png"),"Combine place2dTextures", self)
        self.toolBar.addAction(self.combine2DTextures)
        self.combine2DTextures.triggered.connect(self.combine2DTex)
        self.combine2DTextures.setStatusTip("Select File Nodes to combine")

        self.fullControlCheckbox = QAction(QIcon(script_path + "/icons/moreOptions.png"),"Remap Textures", self)
        self.toolBar.addAction(self.fullControlCheckbox)
        self.fullControlCheckbox.setCheckable(True)
        self.fullControlCheckbox.setStatusTip("Create remap nodes between your textures")

        self.udimCheckbox = QAction(QIcon(script_path + "/icons/udim.png"),"UDIM", self)
        self.toolBar.addAction(self.udimCheckbox)
        self.udimCheckbox.setCheckable(True)
        self.udimCheckbox.setStatusTip("Turn on for UDIM")

        self.addChannelButton = QAction(QIcon(script_path + "/icons/add.png"),"Add", self)
        self.toolBar.addAction(self.addChannelButton)
        self.addChannelButton.setStatusTip("Add Channel Manually")
        self.addChannelButton.triggered.connect(lambda: self.manualTagsPopUp("add empty channel",""))


        # Assign Methodes to Action Items
        self.resetTagsMenu.triggered.connect(resetTags)
        self.closeMenu.triggered.connect(self.closeApp)
        self.resetMenu.triggered.connect(lambda: self.dismissChannel("reset"))
        self.updateMenu.triggered.connect(self.checkForUpdates)
        self.aboutMeMenu.triggered.connect(self.aboutMePopUp)
        self.changeTagsMenu.triggered.connect(self.changeTags)
        self.preferencesMenu.triggered.connect(self.preferencesWindow)


        # Define Main Area
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        # Set Extra Options
        #self.extraOptionsGroupBox = QGroupBox("")
        #self.extraOptionsGroupBox.setContentsMargins(10, 10, 10, 10)
        #self.extraOptionsGroupBox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(60,60,60); border: 0px; border-radius: 2px;")
        #self.layout.addWidget(self.extraOptionsGroupBox)

        #self.extraOptions_hbox = QHBoxLayout()
        #self.extraOptionsGroupBox.setLayout(self.extraOptions_hbox)
        #self.extraOptionsGroupBox.setFixedHeight(45)
        #self.extraOptions_hbox.setContentsMargins(10,10,10,10)

        #self.fullControlCheckbox = QCheckBox("Remap Textures")
        #self.fullControlCheckbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(60,60,60);")
        #self.extraOptions_hbox.addWidget(self.fullControlCheckbox)

        #self.udimCheckbox = QCheckBox("Udim")
        #self.udimCheckbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(60,60,60);")
        #self.extraOptions_hbox.addWidget(self.udimCheckbox)

        #self.extraOptionsGroupBox.hide()

        # Set Material Name
        self.materialNameLineEdit = QLineEdit()
        self.materialNameLineEdit.setTextMargins(5, 0, 5, 0)
        self.materialNameLineEdit.setPlaceholderText(" My Default Material Name")
        self.materialNameLineEdit.setStyleSheet("color: rgb(255, 255, 255);")
        self.layout.addWidget(self.materialNameLineEdit)

        # Diffuse
        self.diffuse_groupbox = QGroupBox("Diffuse")
        self.diffuse_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.diffuse_groupbox)
        self.diffuse_groupbox.setAlignment(Qt.AlignTop)

        self.diffuse_hbox = QHBoxLayout()
        self.diffuse_hbox.addStretch()
        self.diffuse_groupbox.setLayout(self.diffuse_hbox)
        self.diffuse_groupbox.setFixedHeight(50)

        self.diffuseChangeImage = QPushButton('', self)
        self.diffuseChangeImage.clicked.connect(lambda: self.openFileNameDialog("diffuse"))
        self.diffuseChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.diffuseChangeImage.setIconSize(QSize(12, 12))
        self.diffuse_hbox.addWidget(self.diffuseChangeImage, 0)

        self.diffusePathLineEdit = QLineEdit("empty")
        self.diffusePathLineEdit.setTextMargins(5, 0, 5, 0)
        self.diffusePathLineEdit.setReadOnly(True)
        self.diffusePathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.diffuse_hbox.addWidget(self.diffusePathLineEdit, 8)

        self.dismissDiffuseChannel = QPushButton('', self)
        self.dismissDiffuseChannel.clicked.connect(lambda: self.dismissChannel("diffuse"))
        self.dismissDiffuseChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissDiffuseChannel.setIconSize(QSize(14, 14))
        self.diffuse_hbox.addWidget(self.dismissDiffuseChannel, 0)

        self.diffuse_groupbox.hide()

        # ao
        self.ao_groupbox = QGroupBox("ao")
        self.ao_groupbox.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.ao_groupbox)
        self.ao_groupbox.setAlignment(Qt.AlignTop)

        self.ao_hbox = QHBoxLayout()
        self.ao_hbox.addStretch()
        self.ao_groupbox.setLayout(self.ao_hbox)
        self.ao_groupbox.setFixedHeight(50)

        self.aoChangeImage = QPushButton('', self)
        self.aoChangeImage.clicked.connect(lambda: self.openFileNameDialog("ao"))
        self.aoChangeImage.setIcon(QIcon(script_path + '\\icons\\folder.png'))
        self.aoChangeImage.setIconSize(QSize(12, 12))
        self.ao_hbox.addWidget(self.aoChangeImage, 0)

        self.aoPathLineEdit = QLineEdit("empty")
        self.aoPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.aoPathLineEdit.setReadOnly(True)
        self.aoPathLineEdit.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.ao_hbox.addWidget(self.aoPathLineEdit, 8)

        self.dismissaoChannel = QPushButton('', self)
        self.dismissaoChannel.clicked.connect(lambda: self.dismissChannel("ao"))
        self.dismissaoChannel.setIcon(QIcon(script_path + '\\icons\\dismiss.png'))
        self.dismissaoChannel.setIconSize(QSize(14, 14))
        self.ao_hbox.addWidget(self.dismissaoChannel, 0)

        self.ao_groupbox.hide()


        # Reflection
        self.reflection_groupbox = QGroupBox("Reflection")
        self.reflection_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.reflection_groupbox)
        self.reflection_groupbox.setAlignment(Qt.AlignTop)

        self.reflection_hbox = QHBoxLayout()
        self.reflection_hbox.addStretch()
        self.reflection_groupbox.setLayout(self.reflection_hbox)
        self.reflection_groupbox.setFixedHeight(50)

        self.reflectionChangeImage = QPushButton('', self)
        self.reflectionChangeImage.clicked.connect(lambda: self.openFileNameDialog("reflection"))
        self.reflectionChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.reflectionChangeImage.setIconSize(QSize(12, 12))
        self.reflection_hbox.addWidget(self.reflectionChangeImage, 0)

        self.reflectionPathLineEdit = QLineEdit("empty")
        self.reflectionPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.reflectionPathLineEdit.setReadOnly(True)
        self.reflectionPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.reflection_hbox.addWidget(self.reflectionPathLineEdit, 8)

        self.dismissReflectionChannel = QPushButton('', self)
        self.dismissReflectionChannel.clicked.connect(lambda: self.dismissChannel("reflection"))
        self.dismissReflectionChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissReflectionChannel.setIconSize(QSize(14, 14))
        self.reflection_hbox.addWidget(self.dismissReflectionChannel, 0)

        self.reflection_groupbox.hide()

        # Roughness
        self.roughness_groupbox = QGroupBox("Roughness")
        self.roughness_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.roughness_groupbox)
        self.roughness_groupbox.setAlignment(Qt.AlignTop)

        self.roughness_hbox = QHBoxLayout()
        self.roughness_hbox.addStretch()
        self.roughness_groupbox.setLayout(self.roughness_hbox)
        self.roughness_groupbox.setFixedHeight(50)

        self.roughnessChangeImage = QPushButton('', self)
        self.roughnessChangeImage.clicked.connect(lambda: self.openFileNameDialog("roughness"))
        self.roughnessChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.roughnessChangeImage.setIconSize(QSize(12, 12))
        self.roughness_hbox.addWidget(self.roughnessChangeImage, 0)

        self.roughnessPathLineEdit = QLineEdit("empty")
        self.roughnessPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.roughnessPathLineEdit.setReadOnly(True)
        self.roughnessPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.roughness_hbox.addWidget(self.roughnessPathLineEdit, 8)

        self.dismissroughnessChannel = QPushButton('', self)
        self.dismissroughnessChannel.clicked.connect(lambda: self.dismissChannel("roughness"))
        self.dismissroughnessChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissroughnessChannel.setIconSize(QSize(14, 14))
        self.roughness_hbox.addWidget(self.dismissroughnessChannel, 0)

        self.roughness_groupbox.hide()

        # metalness
        self.metalness_groupbox = QGroupBox("metalness")
        self.metalness_groupbox.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.metalness_groupbox)
        self.metalness_groupbox.setAlignment(Qt.AlignTop)

        self.metalness_hbox = QHBoxLayout()
        self.metalness_hbox.addStretch()
        self.metalness_groupbox.setLayout(self.metalness_hbox)
        self.metalness_groupbox.setFixedHeight(50)

        self.metalnessChangeImage = QPushButton('', self)
        self.metalnessChangeImage.clicked.connect(lambda: self.openFileNameDialog("metalness"))
        self.metalnessChangeImage.setIcon(QIcon(script_path + '\\icons\\folder.png'))
        self.metalnessChangeImage.setIconSize(QSize(12, 12))
        self.metalness_hbox.addWidget(self.metalnessChangeImage, 0)

        self.metalnessPathLineEdit = QLineEdit("empty")
        self.metalnessPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.metalnessPathLineEdit.setReadOnly(True)
        self.metalnessPathLineEdit.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.metalness_hbox.addWidget(self.metalnessPathLineEdit, 8)

        self.dismissmetalnessChannel = QPushButton('', self)
        self.dismissmetalnessChannel.clicked.connect(lambda: self.dismissChannel("metalness"))
        self.dismissmetalnessChannel.setIcon(QIcon(script_path + '\\icons\\dismiss.png'))
        self.dismissmetalnessChannel.setIconSize(QSize(14, 14))
        self.metalness_hbox.addWidget(self.dismissmetalnessChannel, 0)

        self.metalness_groupbox.hide()

        # Refraction
        self.refraction_groupbox = QGroupBox("Refraction")
        self.refraction_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.refraction_groupbox)
        self.refraction_groupbox.setAlignment(Qt.AlignTop)

        self.refraction_hbox = QHBoxLayout()
        self.refraction_hbox.addStretch()
        self.refraction_groupbox.setLayout(self.refraction_hbox)
        self.refraction_groupbox.setFixedHeight(50)

        self.refractionChangeImage = QPushButton('', self)
        self.refractionChangeImage.clicked.connect(lambda: self.openFileNameDialog("refraction"))
        self.refractionChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.refractionChangeImage.setIconSize(QSize(12, 12))
        self.refraction_hbox.addWidget(self.refractionChangeImage, 0)

        self.refractionPathLineEdit = QLineEdit("empty")
        self.refractionPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.refractionPathLineEdit.setReadOnly(True)
        self.refractionPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.refraction_hbox.addWidget(self.refractionPathLineEdit, 8)

        self.dismissrefractionChannel = QPushButton('', self)
        self.dismissrefractionChannel.clicked.connect(lambda: self.dismissChannel("refraction"))
        self.dismissrefractionChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissrefractionChannel.setIconSize(QSize(14, 14))
        self.refraction_hbox.addWidget(self.dismissrefractionChannel, 0)

        self.refraction_groupbox.hide()

        # subsurface
        self.subsurface_groupbox = QGroupBox("Subsurface")
        self.subsurface_groupbox.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.subsurface_groupbox)
        self.subsurface_groupbox.setAlignment(Qt.AlignTop)

        self.subsurface_hbox = QHBoxLayout()
        self.subsurface_hbox.addStretch()
        self.subsurface_groupbox.setLayout(self.subsurface_hbox)
        self.subsurface_groupbox.setFixedHeight(50)

        self.subsurfaceChangeImage = QPushButton('', self)
        self.subsurfaceChangeImage.clicked.connect(lambda: self.openFileNameDialog("subsurface"))
        self.subsurfaceChangeImage.setIcon(QIcon(script_path + '\\icons\\folder.png'))
        self.subsurfaceChangeImage.setIconSize(QSize(12, 12))
        self.subsurface_hbox.addWidget(self.subsurfaceChangeImage, 0)

        self.subsurfacePathLineEdit = QLineEdit("empty")
        self.subsurfacePathLineEdit.setTextMargins(5, 0, 5, 0)
        self.subsurfacePathLineEdit.setReadOnly(True)
        self.subsurfacePathLineEdit.setStyleSheet(
            "color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.subsurface_hbox.addWidget(self.subsurfacePathLineEdit, 8)

        self.dismisssubsurfaceChannel = QPushButton('', self)
        self.dismisssubsurfaceChannel.clicked.connect(lambda: self.dismissChannel("subsurface"))
        self.dismisssubsurfaceChannel.setIcon(QIcon(script_path + '\\icons\\dismiss.png'))
        self.dismisssubsurfaceChannel.setIconSize(QSize(14, 14))
        self.subsurface_hbox.addWidget(self.dismisssubsurfaceChannel, 0)

        self.subsurface_groupbox.hide()

        # Bump
        self.bump_groupbox = QGroupBox("Bump")
        self.bump_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.bump_groupbox)
        self.bump_groupbox.setAlignment(Qt.AlignTop)

        self.bump_hbox = QHBoxLayout()
        self.bump_hbox.addStretch()
        self.bump_groupbox.setLayout(self.bump_hbox)
        self.bump_groupbox.setFixedHeight(50)

        self.bumpChangeImage = QPushButton('', self)
        self.bumpChangeImage.clicked.connect(lambda: self.openFileNameDialog("bump"))
        self.bumpChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.bumpChangeImage.setIconSize(QSize(12, 12))
        self.bump_hbox.addWidget(self.bumpChangeImage, 0)

        self.bumpPathLineEdit = QLineEdit("empty")
        self.bumpPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.bumpPathLineEdit.setReadOnly(True)
        self.bumpPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.bump_hbox.addWidget(self.bumpPathLineEdit, 8)

        self.dismissbumpChannel = QPushButton('', self)
        self.dismissbumpChannel.clicked.connect(lambda: self.dismissChannel("bump"))
        self.dismissbumpChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissbumpChannel.setIconSize(QSize(14, 14))
        self.bump_hbox.addWidget(self.dismissbumpChannel, 0)

        self.bump_groupbox.hide()

        # Normal
        self.normal_groupbox = QGroupBox("Normal")
        self.normal_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.normal_groupbox)
        self.normal_groupbox.setAlignment(Qt.AlignTop)

        self.normal_hbox = QHBoxLayout()
        self.normal_hbox.addStretch()
        self.normal_groupbox.setLayout(self.normal_hbox)
        self.normal_groupbox.setFixedHeight(50)

        self.normalChangeImage = QPushButton('', self)
        self.normalChangeImage.clicked.connect(lambda: self.openFileNameDialog("normal"))
        self.normalChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.normalChangeImage.setIconSize(QSize(12, 12))
        self.normal_hbox.addWidget(self.normalChangeImage, 0)

        self.normalPathLineEdit = QLineEdit("empty")
        self.normalPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.normalPathLineEdit.setReadOnly(True)
        self.normalPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.normal_hbox.addWidget(self.normalPathLineEdit, 8)

        self.dismissnormalChannel = QPushButton('', self)
        self.dismissnormalChannel.clicked.connect(lambda: self.dismissChannel("normal"))
        self.dismissnormalChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissnormalChannel.setIconSize(QSize(14, 14))
        self.normal_hbox.addWidget(self.dismissnormalChannel, 0)

        self.normal_groupbox.hide()

        # Displacement
        self.displacement_groupbox = QGroupBox("Displacement")
        self.displacement_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.displacement_groupbox)
        self.displacement_groupbox.setAlignment(Qt.AlignTop)

        self.displacement_hbox = QHBoxLayout()
        self.displacement_hbox.addStretch()
        self.displacement_groupbox.setLayout(self.displacement_hbox)
        self.displacement_groupbox.setFixedHeight(50)

        self.displacementChangeImage = QPushButton('', self)
        self.displacementChangeImage.clicked.connect(lambda: self.openFileNameDialog("displacement"))
        self.displacementChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.displacementChangeImage.setIconSize(QSize(12, 12))
        self.displacement_hbox.addWidget(self.displacementChangeImage, 0)

        self.displacementPathLineEdit = QLineEdit("empty")
        self.displacementPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.displacementPathLineEdit.setReadOnly(True)
        self.displacementPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.displacement_hbox.addWidget(self.displacementPathLineEdit, 8)

        self.dismissdisplacementChannel = QPushButton('', self)
        self.dismissdisplacementChannel.clicked.connect(lambda: self.dismissChannel("displacement"))
        self.dismissdisplacementChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissdisplacementChannel.setIconSize(QSize(14, 14))
        self.displacement_hbox.addWidget(self.dismissdisplacementChannel, 0)

        self.displacement_groupbox.hide()

        # Emission
        self.emission_groupbox = QGroupBox("Emission")
        self.emission_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.emission_groupbox)
        self.emission_groupbox.setAlignment(Qt.AlignTop)

        self.emission_hbox = QHBoxLayout()
        self.emission_hbox.addStretch()
        self.emission_groupbox.setLayout(self.emission_hbox)
        self.emission_groupbox.setFixedHeight(50)

        self.emissionChangeImage = QPushButton('', self)
        self.emissionChangeImage.clicked.connect(lambda: self.openFileNameDialog("emission"))
        self.emissionChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.emissionChangeImage.setIconSize(QSize(12, 12))
        self.emission_hbox.addWidget(self.emissionChangeImage, 0)

        self.emissionPathLineEdit = QLineEdit("empty")
        self.emissionPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.emissionPathLineEdit.setReadOnly(True)
        self.emissionPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.emission_hbox.addWidget(self.emissionPathLineEdit, 8)

        self.dismissemissionChannel = QPushButton('', self)
        self.dismissemissionChannel.clicked.connect(lambda: self.dismissChannel("emission"))
        self.dismissemissionChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissemissionChannel.setIconSize(QSize(14, 14))
        self.emission_hbox.addWidget(self.dismissemissionChannel, 0)

        self.emission_groupbox.hide()

        # Opacity
        self.opacity_groupbox = QGroupBox("Opacity")
        self.opacity_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80); border: 0px; border-radius: 2px;")
        self.layout.addWidget(self.opacity_groupbox)
        self.opacity_groupbox.setAlignment(Qt.AlignTop)

        self.opacity_hbox = QHBoxLayout()
        self.opacity_hbox.addStretch()
        self.opacity_groupbox.setLayout(self.opacity_hbox)
        self.opacity_groupbox.setFixedHeight(50)

        self.opacityChangeImage = QPushButton('', self)
        self.opacityChangeImage.clicked.connect(lambda: self.openFileNameDialog("opacity"))
        self.opacityChangeImage.setIcon(QIcon(script_path +'\\icons\\folder.png'))
        self.opacityChangeImage.setIconSize(QSize(12, 12))
        self.opacity_hbox.addWidget(self.opacityChangeImage, 0)

        self.opacityPathLineEdit = QLineEdit("empty")
        self.opacityPathLineEdit.setTextMargins(5, 0, 5, 0)
        self.opacityPathLineEdit.setReadOnly(True)
        self.opacityPathLineEdit.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(10,15,25); border: 0px; border-radius: 5px;")
        self.opacity_hbox.addWidget(self.opacityPathLineEdit, 8)

        self.dismissopacityChannel = QPushButton('', self)
        self.dismissopacityChannel.clicked.connect(lambda: self.dismissChannel("opacity"))
        self.dismissopacityChannel.setIcon(QIcon(script_path +'\\icons\\dismiss.png'))
        self.dismissopacityChannel.setIconSize(QSize(14, 14))
        self.opacity_hbox.addWidget(self.dismissopacityChannel, 0)

        self.opacity_groupbox.hide()

        # Create and Dismiss Button
        self.createReset_groupBox = QGroupBox()
        self.createReset_groupBox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(60,60,60); border: 0px; border-radius: 2px;")
        self.createReset_groupBox.setFixedHeight(25)
        self.layout.addWidget(self.createReset_groupBox)
        self.createReset_groupBox.setAlignment(Qt.AlignBottom)

        self.createReset_hbox = QHBoxLayout()
        self.createReset_hbox.setContentsMargins(0,0,0,0)
        self.createReset_groupBox.setLayout(self.createReset_hbox)
        self.createReset_groupBox.setFixedHeight(35)

        self.createButton = QPushButton("Create")
        self.createReset_hbox.addWidget(self.createButton)
        self.createButton.clicked.connect(self.createMaterial)
        self.createButton.setFixedHeight(35)
        self.createButton.setStyleSheet("QPushButton::hover"
                             "{"
                             "background-color : rgb(100,100,200);"
                             "}")
        self.resetButton = QPushButton("Reset")
        self.createReset_hbox.addWidget(self.resetButton)
        self.resetButton.setFixedHeight(35)
        self.resetButton.clicked.connect(lambda: self.dismissChannel("reset"))
        self.resetButton.setStyleSheet("QPushButton::hover"
                             "{"
                             "background-color : rgb(200,100,100);"
                             "}")

        self.createReset_groupBox.hide()

        # Widget Management
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        # Define Status Bar
        self.statusBar().showMessage("Universal Material Builder")
        self.statusBar().setStyleSheet("background-color : white")

    # Show Ui for Input Files
    def createInputUi(self, name, path):
        # Styles
        usedWindowStyle = ("background-color: #2b2b2b;")

        # Find Channel and Make its UI Groupbox visible
        tags = self.readTags()
        diffuseTags = tags.get('diffuse')
        aoTags = tags.get('ao')
        reflectionTags = tags.get("reflection")
        roughnessTags = tags.get("roughness")
        metalnessTags = tags.get("metalness")
        refractionTags = tags.get("refraction")
        subsurfaceTags = tags.get("subsurface")
        bumpTags = tags.get("bump")
        normalTags = tags.get("normal")
        displacementTags = tags.get("displacement")
        emissionTags = tags.get("emission")
        opacityTags = tags.get("opacity")
        found = 0
        for tag in diffuseTags:
            if tag in name.lower():
                self.diffuseName = name
                self.diffusePath = path
                self.createReset_groupBox.show()
                self.diffuse_groupbox.show()
                self.diffusePathLineEdit.setText(self.diffusePath)
                self.setStyleSheet(usedWindowStyle)
                found = 1
                
        if found == 0:
            for tag in aoTags:
                if tag in name.lower():
                    self.aoName = name
                    self.aoPath = path
                    self.ao_groupbox.show()
                    self.createReset_groupBox.show()
                    self.aoPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in reflectionTags:
                if tag in name.lower():
                    self.reflectionName = name
                    self.reflectionPath = path
                    self.reflection_groupbox.show()
                    self.createReset_groupBox.show()
                    self.reflectionPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in roughnessTags:
                if tag in name.lower():
                    self.roughnessName = name
                    self.roughnessPath = path
                    self.roughness_groupbox.show()
                    self.createReset_groupBox.show()
                    self.roughnessPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1
                    
        if found == 0:
            for tag in metalnessTags:
                if tag in name.lower():
                    self.metalnessName = name
                    self.metalnessPath = path
                    self.metalness_groupbox.show()
                    self.createReset_groupBox.show()
                    self.metalnessPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in refractionTags:
                if tag in name.lower():
                    self.refractionName = name
                    self.refractionPath = path
                    self.refraction_groupbox.show()
                    self.createReset_groupBox.show()
                    self.refractionPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1
                    
        if found == 0:
            for tag in subsurfaceTags:
                if tag in name.lower():
                    self.subsurfaceName = name
                    self.subsurfacePath = path
                    self.subsurface_groupbox.show()
                    self.createReset_groupBox.show()
                    self.subsurfacePathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in bumpTags:
                if tag in name.lower():
                    self.bumpName = name
                    self.bumpPath = path
                    self.bump_groupbox.show()
                    self.createReset_groupBox.show()
                    self.bumpPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in normalTags:
                if tag in name.lower():
                    self.normalName = name
                    self.normalPath = path
                    self.normal_groupbox.show()
                    self.createReset_groupBox.show()
                    self.normalPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in displacementTags:
                if tag in name.lower():
                    self.displacementName = name
                    self.displacementPath = path
                    self.displacement_groupbox.show()
                    self.createReset_groupBox.show()
                    self.displacementPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in emissionTags:
                if tag in name.lower():
                    self.emissionName = name
                    self.emissionPath = path
                    self.emission_groupbox.show()
                    self.createReset_groupBox.show()
                    self.emissionPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            for tag in opacityTags:
                if tag in name.lower():
                    self.opacityName = name
                    self.opacityPath = path
                    self.opacity_groupbox.show()
                    self.createReset_groupBox.show()
                    self.opacityPathLineEdit.setText(path)
                    self.setStyleSheet(usedWindowStyle)
                    found = 1

        if found == 0:
            self.manualTagsPopUp(name, path)

    # Read Tags from json
    def readTags(self):
        tagsFilePath = script_path + "\\util\\tags.json"
        with open(tagsFilePath) as tagsFile:
            self.tags = json.load(tagsFile)

        return self.tags

    # Dismiss Channels
    def dismissChannel(self, channel):
        if channel == "diffuse":
            self.diffuse_groupbox.hide()
            self.statusBar().showMessage("Diffuse Input Deleted!")
            
        if channel == "ao":
            self.ao_groupbox.hide()
            self.statusBar().showMessage("Ao Input Deleted!")

        if channel == "reflection":
            self.reflection_groupbox.hide()
            self.statusBar().showMessage("Reflection Input Deleted!")

        if channel == "roughness":
            self.roughness_groupbox.hide()
            self.statusBar().showMessage("Roughness Input Deleted!")
            
        if channel == "metalness":
            self.metalness_groupbox.hide()
            self.statusBar().showMessage("Metalness Input Deleted!")

        if channel == "refraction":
            self.refraction_groupbox.hide()
            self.statusBar().showMessage("Refraction Input Deleted!")
            
        if channel == "subsurface":
            self.subsurface_groupbox.hide()
            self.statusBar().showMessage("Subsurface Input Deleted!")

        if channel == "bump":
            self.bump_groupbox.hide()
            self.statusBar().showMessage("Bump Input Deleted!")

        if channel == "normal":
            self.normal_groupbox.hide()
            self.statusBar().showMessage("Normal Input Deleted!")

        if channel == "displacement":
            self.displacement_groupbox.hide()
            self.statusBar().showMessage("Displacement Input Deleted!")

        if channel == "emission":
            self.emission_groupbox.hide()
            self.statusBar().showMessage("Emission Input Deleted!")

        if channel == "opacity":
            self.opacity_groupbox.hide()
            self.statusBar().showMessage("Opacity Input Deleted!")

        if channel == "reset":
            self.diffuse_groupbox.hide()
            self.ao_groupbox.hide()
            self.reflection_groupbox.hide()
            self.roughness_groupbox.hide()
            self.metalness_groupbox.hide()
            self.refraction_groupbox.hide()
            self.subsurface_groupbox.hide()
            self.bump_groupbox.hide()
            self.normal_groupbox.hide()
            self.displacement_groupbox.hide()
            self.emission_groupbox.hide()
            self.opacity_groupbox.hide()
            self.statusBar().showMessage("Reset UI")


        #Check if any Channel is set to show
        if self.diffuse_groupbox.isVisible() == False and self.reflection_groupbox.isVisible() == False and self.refraction_groupbox.isVisible() == False and self.bump_groupbox.isVisible() == False and self.normal_groupbox.isVisible() == False and self.displacement_groupbox.isVisible() == False and self.emission_groupbox.isVisible() == False and self.opacity_groupbox.isVisible() == False and self.ao_groupbox.isVisible() == False and self.metalness_groupbox.isVisible() == False and self.subsurface_groupbox.isVisible() == False:
            self.createReset_groupBox.hide()
            background_image_path = os.path.join(script_path, "icons", "drag_and_drop.png")
            background_image_path = background_image_path.replace("\\","/")
            windowStyle = "MainWindow {background-color: #2b2b2b; background-image: url('%s'); background-repeat: no-repeat;}" % (background_image_path)
            self.setStyleSheet(windowStyle)

    # Change File Input Directory
    def openFileNameDialog(self, channel):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Choose an image file", "","All Files (*);;Python Files (*.py)", options=options)
        name = fileName.rsplit("/", 1)[1]
        ext = os.path.splitext(name)[1][1:]
        if ext.lower() in self.valid_image_ext:
            if channel == "diffuse":
                self.diffusePath = fileName
                self.diffuseName = fileName.rsplit("/", 1)[1]
                self.diffusePathLineEdit.setText(self.diffusePath)
                
            if channel == "ao":
                self.aoPath = fileName
                self.aoName = fileName.rsplit("/", 1)[1]
                self.aoPathLineEdit.setText(self.aoPath)

            if channel == "reflection":
                self.reflectionPath = fileName
                self.reflectionName = fileName.rsplit("/", 1)[1]
                self.reflectionPathLineEdit.setText(self.reflectionPath)

            if channel == "roughness":
                self.roughnessPath = fileName
                self.roughnessName = fileName.rsplit("/", 1)[1]
                self.roughnessPathLineEdit.setText(self.roughnessPath)
                
            if channel == "metalness":
                self.metalnessPath = fileName
                self.metalnessName = fileName.rsplit("/", 1)[1]
                self.metalnessPathLineEdit.setText(self.metalnessPath)

            if channel == "refraction":
                self.refractionPath = fileName
                self.refractionName = fileName.rsplit("/", 1)[1]
                self.refractionPathLineEdit.setText(self.refractionPath)
                
            if channel == "subsurface":
                self.subsurfacePath = fileName
                self.subsurfaceName = fileName.rsplit("/", 1)[1]
                self.subsurfacePathLineEdit.setText(self.subsurfacePath)

            if channel == "bump":
                self.bumpPath = fileName
                self.bumpName = fileName.rsplit("/", 1)[1]
                self.bumpPathLineEdit.setText(self.bumpPath)

            if channel == "normal":
                self.normalPath = fileName
                self.normalName = fileName.rsplit("/", 1)[1]
                self.normalPathLineEdit.setText(self.normalPath)

            if channel == "displacement":
                self.displacementPath = fileName
                self.displacementName = fileName.rsplit("/", 1)[1]
                self.displacementPathLineEdit.setText(self.displacementPath)

            if channel == "emission":
                self.emissionPath = fileName
                self.emissionName = fileName.rsplit("/", 1)[1]
                self.emissionPathLineEdit.setText(self.emissionPath)

            if channel == "opacity":
                self.opacityPath = fileName
                self.opacityName = fileName.rsplit("/", 1)[1]
                self.opacityPathLineEdit.setText(self.opacityPath)

            self.statusBar().showMessage("Changed Texture Path!")

        else:
            pass

    # Handling Drag Event
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    # Handling Drop Event
    def dropEvent(self, event):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        count = 0
        for f in files:
            path = f
            name = path.rsplit("/", 1)[1]
            ext = os.path.splitext(name)[1][1:]
            if ext.lower() in self.valid_image_ext:
                self.createInputUi(name, path)
                count += 1

            else:
                self.statusBar().showMessage("Please drop image files only!")

        self.statusBar().showMessage("Successfully added " + str(count) + " textures!")

    # Can not find Tag PopUp
    def manualTagsPopUp(self, name, path):
        name = name
        path = path

        self.manualTagsQDialog = QDialog()
        self.manualTagsQDialog.setWindowTitle("Set Channel")
        self.manualTagsQDialog.setWindowIcon(QIcon(script_path + '\\icons\\logo.png'))
        self.manualTagsQDialog.setGeometry(self.main_window_pos_x, 220, 300, 100)
        self.manualTagsQDialog.setFixedSize(300, 100)

        self.qDialogLayout = QVBoxLayout(self.manualTagsQDialog)
        self.qDialogLayout.setAlignment(Qt.AlignTop)

        self.channelInfoLabel = QLabel()
        channelInfoLabelMessage = name + " :"
        self.channelInfoLabel.setText(channelInfoLabelMessage)
        self.qDialogLayout.addWidget(self.channelInfoLabel)


        self.channelDropDown = QComboBox()
        self.channelDropDown.addItem("choose")
        self.channelDropDown.addItem("diffuse")
        self.channelDropDown.addItem("ao")
        self.channelDropDown.addItem("reflection")
        self.channelDropDown.addItem("roughness")
        self.channelDropDown.addItem("metalness")
        self.channelDropDown.addItem("refraction")
        self.channelDropDown.addItem("subsurface")
        self.channelDropDown.addItem("bump")
        self.channelDropDown.addItem("normal")
        self.channelDropDown.addItem("displacement")
        self.channelDropDown.addItem("emission")
        self.channelDropDown.addItem("opacity")
        self.qDialogLayout.addWidget(self.channelDropDown)

        self.qDialogGroupbox = QGroupBox()
        self.qDialogGroupbox.setAlignment(Qt.AlignTop)
        self.qDialogLayout.addWidget(self.qDialogGroupbox)
        self.qDialogGroupbox.setContentsMargins(0, 0, 0, 0)


        self.qDialogButtonLayout = QHBoxLayout()
        self.qDialogButtonLayout.setAlignment(Qt.AlignTop)
        self.qDialogGroupbox.setLayout(self.qDialogButtonLayout)
        self.qDialogButtonLayout.setContentsMargins(0, 0, 0, 0)

        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(lambda: self.popUpAdd(name, path))

        self.skipButton = QPushButton("Skip")
        self.skipButton.clicked.connect(self.popUpSkip)

        self.qDialogButtonLayout.addWidget(self.addButton)
        self.qDialogButtonLayout.addWidget(self.skipButton)

        popUp = self.manualTagsQDialog.exec_()

    # Pop Up Add
    def popUpAdd(self, name, path):
        # Styles
        usedWindowStyle = ("background-color: #2b2b2b;")

        channel = self.channelDropDown.currentText()


        if channel == "diffuse":
            self.diffuseName = name
            self.diffusePath = path
            self.diffuse_groupbox.show()
            self.createReset_groupBox.show()
            self.diffusePathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)
            
        if channel == "ao":
            self.aoName = name
            self.aoPath = path
            self.ao_groupbox.show()
            self.createReset_groupBox.show()
            self.aoPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "reflection":
            self.reflectionName = name
            self.reflectionPath = path
            self.reflection_groupbox.show()
            self.createReset_groupBox.show()
            self.reflectionPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "roughness":
            self.roughnessName = name
            self.roughnessPath = path
            self.roughness_groupbox.show()
            self.createReset_groupBox.show()
            self.roughnessPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)
            
        if channel == "metalness":
            self.metalnessName = name
            self.metalnessPath = path
            self.metalness_groupbox.show()
            self.createReset_groupBox.show()
            self.metalnessPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "refraction":
            self.refractionName = name
            self.refractionPath = path
            self.refraction_groupbox.show()
            self.createReset_groupBox.show()
            self.refractionPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)
            
        if channel == "subsurface":
            self.subsurfaceName = name
            self.subsurfacePath = path
            self.subsurface_groupbox.show()
            self.createReset_groupBox.show()
            self.subsurfacePathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "bump":
            self.bumpName = name
            self.bumpPath = path
            self.bump_groupbox.show()
            self.createReset_groupBox.show()
            self.bumpPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "normal":
            self.normalName = name
            self.normalPath = path
            self.normal_groupbox.show()
            self.createReset_groupBox.show()
            self.normalPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "displacement":
            self.displacementName = name
            self.displacementPath = path
            self.displacement_groupbox.show()
            self.createReset_groupBox.show()
            self.displacementPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "emission":
            self.emissionName = name
            self.emissionPath = path
            self.emission_groupbox.show()
            self.createReset_groupBox.show()
            self.emissionPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)

        if channel == "opacity":
            self.opacityName = name
            self.opacityPath = path
            self.opacity_groupbox.show()
            self.createReset_groupBox.show()
            self.opacityPathLineEdit.setText(path)
            self.setStyleSheet(usedWindowStyle)


        self.manualTagsQDialog.close()

    # Pop Up Skip
    def popUpSkip(self):
        self.manualTagsQDialog.close()

    # Check for Updates
    def checkForUpdates(self):
        url = "https://gumroad.com/fabianstrube"
        webbrowser.open_new(url)

    # About Me Pop Up
    def aboutMePopUp(self):
        self.aboutMeMsgBox = QMessageBox()
        self.aboutMeMsgBox.setWindowIcon(QIcon(script_path + '\\icons\\logo.png'))
        self.aboutMeMsgBox.setWindowTitle("About")
        information = "Universal Material Builder ©2022\n\nAuthor: Fabian Strube\nEmail: strubefabian4@gmail.com\nWebsite: strube-digital.com\n\nCredits:\nTester: Dominic Werner, Gahui Han\nVray Support: Guy Micciche"
        self.aboutMeMsgBox.setText(information)
        self.aboutMeMsgBox.setInformativeText("Bug reports and feature requests via email to: strubefabian4@gmail.com")
        self.aboutMeMsgBox.exec_()

    # Change Tags Window
    def changeTags(self):
        self.changeTagsQDialog = QDialog()
        self.changeTagsQDialog.setWindowTitle("Tags Manager")
        self.changeTagsQDialog.setWindowIcon(QIcon(script_path + '\\icons\\logo.png'))
        self.changeTagsQDialog.setGeometry(self.main_window_pos_x, 220, 300, 100)
        self.changeTagsQDialog.setFixedSize(300, 120)

        self.changeTags_layout = QVBoxLayout()
        self.changeTagsQDialog.setLayout(self.changeTags_layout)

        tags = self.readTags()
        diffuseTags = tags.get('diffuse')
        diffuseTags = ','.join(diffuseTags)
        aoTags = tags.get('ao')
        aoTags = ','.join(aoTags)
        reflectionTags = tags.get("reflection")
        reflectionTags = ','.join(reflectionTags)
        roughnessTags = tags.get("roughness")
        roughnessTags = ','.join(roughnessTags)
        metalnessTags = tags.get('metalness')
        metalnessTags = ','.join(metalnessTags)
        refractionTags = tags.get("refraction")
        refractionTags = ','.join(refractionTags)
        subsurfaceTags = tags.get('subsurface')
        subsurfaceTags = ','.join(subsurfaceTags)
        bumpTags = tags.get("bump")
        bumpTags = ','.join(bumpTags)
        normalTags = tags.get("normal")
        normalTags = ','.join(normalTags)
        displacementTags = tags.get("displacement")
        displacementTags = ','.join(displacementTags)
        emissionTags = tags.get("emission")
        emissionTags = ','.join(emissionTags)
        opacityTags = tags.get("opacity")
        opacityTags = ','.join(opacityTags)

        self.diffuseTags_textEdit = QTextEdit()
        self.diffuseTags_textEdit.setPlainText(diffuseTags)
        self.aoTags_textEdit = QTextEdit()
        self.aoTags_textEdit.setPlainText(aoTags)
        self.reflectionTags_textEdit = QTextEdit()
        self.reflectionTags_textEdit.setPlainText(reflectionTags)
        self.roughnessTags_textEdit = QTextEdit()
        self.roughnessTags_textEdit.setPlainText(roughnessTags)
        self.metalnessTags_textEdit = QTextEdit()
        self.metalnessTags_textEdit.setPlainText(metalnessTags)
        self.refractionTags_textEdit = QTextEdit()
        self.refractionTags_textEdit.setPlainText(refractionTags)
        self.subsurfaceTags_textEdit = QTextEdit()
        self.subsurfaceTags_textEdit.setPlainText(subsurfaceTags)
        self.bumpTags_textEdit = QTextEdit()
        self.bumpTags_textEdit.setPlainText(bumpTags)
        self.normalTags_textEdit = QTextEdit()
        self.normalTags_textEdit.setPlainText(normalTags)
        self.displacementTags_textEdit = QTextEdit()
        self.displacementTags_textEdit.setPlainText(displacementTags)
        self.emissionTags_textEdit = QTextEdit()
        self.emissionTags_textEdit.setPlainText(emissionTags)
        self.opacityTags_textEdit = QTextEdit()
        self.opacityTags_textEdit.setPlainText(opacityTags)


        self.saveTags_btn = QPushButton("Save")
        self.saveTags_btn.clicked.connect(self.saveCustomTags)

        self.channel_tabs = QTabWidget()
        self.channel_tabs.setStyleSheet('font-size: 8pt; margin-left:0px; margin-right:0px;')
        self.channel_tabs.addTab(self.diffuseTags_textEdit, "Diffuse")
        self.channel_tabs.addTab(self.aoTags_textEdit, "Ao")
        self.channel_tabs.addTab(self.reflectionTags_textEdit, "Reflection")
        self.channel_tabs.addTab(self.roughnessTags_textEdit, "Roughness")
        self.channel_tabs.addTab(self.metalnessTags_textEdit, "Metalness")
        self.channel_tabs.addTab(self.refractionTags_textEdit, "Refraction")
        self.channel_tabs.addTab(self.subsurfaceTags_textEdit, "Subsurface")
        self.channel_tabs.addTab(self.bumpTags_textEdit, "Bump")
        self.channel_tabs.addTab(self.normalTags_textEdit, "Normal")
        self.channel_tabs.addTab(self.displacementTags_textEdit, "Displacement")
        self.channel_tabs.addTab(self.emissionTags_textEdit, "Emission")
        self.channel_tabs.addTab(self.opacityTags_textEdit, "Opacity")

        self.changeTags_layout.addWidget(self.channel_tabs)
        self.changeTags_layout.addWidget(self.saveTags_btn)


        changeTagsManager = self.changeTagsQDialog.exec_()

    # Save changed Tags
    def saveCustomTags(self):
        diffuseTags = self.diffuseTags_textEdit.toPlainText()
        diffuseTags = diffuseTags.split(",")
        aoTags = self.aoTags_textEdit.toPlainText()
        aoTags = aoTags.split(",")
        reflectionTags = self.reflectionTags_textEdit.toPlainText()
        reflectionTags = reflectionTags.split(",")
        roughnessTags = self.roughnessTags_textEdit.toPlainText()
        roughnessTags = roughnessTags.split(",")
        metalnessTags = self.metalnessTags_textEdit.toPlainText()
        metalnessTags = metalnessTags.split(",")
        refractionTags = self.refractionTags_textEdit.toPlainText()
        refractionTags = refractionTags.split(",")
        subsurfaceTags = self.subsurfaceTags_textEdit.toPlainText()
        subsurfaceTags = subsurfaceTags.split(",")
        bumpTags = self.bumpTags_textEdit.toPlainText()
        bumpTags = bumpTags.split(",")
        normalTags = self.normalTags_textEdit.toPlainText()
        normalTags = normalTags.split(",")
        displacementTags = self.displacementTags_textEdit.toPlainText()
        displacementTags = displacementTags.split(",")
        emissionTags = self.emissionTags_textEdit.toPlainText()
        emissionTags = emissionTags.split(",")
        opacityTags = self.opacityTags_textEdit.toPlainText()
        opacityTags = opacityTags.split(",")

        tags_path = script_path + "\\util\\tags.json"
        tags = {}

        tags["diffuse"] = diffuseTags
        tags["ao"] = aoTags
        tags["reflection"] = reflectionTags
        tags["roughness"] = roughnessTags
        tags["metalness"] = metalnessTags
        tags["refraction"] = refractionTags
        tags["subsurface"] = subsurfaceTags
        tags["bump"] = bumpTags
        tags["normal"] = normalTags
        tags["displacement"] = displacementTags
        tags["emission"] = emissionTags
        tags["opacity"] = opacityTags

        with open(tags_path, 'w') as tagsFile:
            json.dump(tags, tagsFile, indent=4)

        self.changeTagsQDialog.close()
        self.statusBar().showMessage("Saved custom Tags")

    # Combine 2D Texture Nodes
    def combine2DTex(self):
        sel = cmds.ls(selection=True)
        fileNodes = [f for f in sel if cmds.objectType(f) == "file"]
        if not fileNodes:
            cmds.warning("No file nodes selected!")

        p2dts = []
        for fileNode in fileNodes:
            in_p2dts = cmds.listConnections(fileNode, type="place2dTexture", destination=False)
            if in_p2dts:
                p2dts += [in_p2dts[0]]
                continue
            if not p2dts:
                p2dts += [cmds.shadingNode("place2dTexture", asUtility=True)]

        if len(p2dts) >= 1:
            p2dt = p2dts[0]
            p2dt_ports = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree', 'vertexCameraOne', 'outUV', 'outUvFilterSize']
            f_ports = ['coverage', 'translateFrame', 'rotateFrame', 'mirrorU', 'mirrorV', 'stagger', 'wrapU', 'wrapV', 'repeatUV', 'offset', 'rotateUV', 'noiseUV', 'vertexUvOne', 'vertexUvTwo', 'vertexUvThree', 'vertexCameraOne', 'uvCoord', 'uvFilterSize']
            for fileNode in fileNodes:
                for i in range(len(f_ports)):
                    f_port = f_ports[i]
                    p2dt_port = p2dt_ports[i]
                    if not cmds.isConnected(p2dt + "." + p2dt_port, fileNode + "." + f_port):
                        cmds.connectAttr(p2dt + "." + p2dt_port, fileNode + "." + f_port, f=True)
                    
            for p2dt in p2dts:
                if not cmds.ls(p2dt):
                    continue
                conns = cmds.listConnections(p2dt, type="file")
                if not conns:
                    cmds.delete(p2dt)

    # Change Tags Window
    def preferencesWindow(self):
        self.config = self.readPrefernces()
        self.preferencesQDialog = QDialog()
        self.preferencesQDialog.setWindowTitle("Preferences")
        self.preferencesQDialog.setWindowIcon(QIcon(script_path + '\\icons\\logo.png'))
        self.preferencesQDialog.setGeometry(self.main_window_pos_x, 220, 300, 100)
        self.preferencesQDialog.setFixedSize(250, 350)

        self.preferences_layout = QVBoxLayout()
        self.preferencesQDialog.setLayout(self.preferences_layout)

        # OptionBox
        self.optionBox_groupbox = QGroupBox("Option Box")
        self.optionBox_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80)")
        self.preferences_layout.addWidget(self.optionBox_groupbox)
        self.optionBox_groupbox.setAlignment(Qt.AlignTop)

        self.optionBox_hbox = QVBoxLayout()
        self.optionBox_groupbox.setLayout(self.optionBox_hbox)
        self.optionBox_groupbox.setFixedHeight(50)

        self.assignToSelectionCheckBox = QCheckBox("Assign Material to selected Objects")
        if self.config["assignMaterial"] == 1:
            self.assignToSelectionCheckBox.setChecked(True)
        else:
            self.assignToSelectionCheckBox.setChecked(False)

        self.optionBox_hbox.addWidget(self.assignToSelectionCheckBox)
        self.optionBox_hbox.setContentsMargins(5, 5, 5, 5)
        self.assignToSelectionCheckBox.setStyleSheet("background-color: rgb(50,50,50);")

        # Render Engine
        self.renderEngine_groupbox = QGroupBox("Render Engine")
        self.renderEngine_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80)")
        self.preferences_layout.addWidget(self.renderEngine_groupbox)
        self.renderEngine_groupbox.setAlignment(Qt.AlignTop)

        self.renderEngine_hbox = QVBoxLayout()
        self.renderEngine_groupbox.setLayout(self.renderEngine_hbox)
        self.renderEngine_groupbox.setFixedHeight(50)

        self.renderEngineDropDown = QComboBox()
        self.renderEngineDropDown.addItem("Arnold")
        self.renderEngineDropDown.addItem("Redshift")
        self.renderEngineDropDown.addItem("V-Ray")

        index = self.renderEngineDropDown.findText(self.config["renderEngine"], Qt.MatchFixedString)
        if index >= 0:
            self.renderEngineDropDown.setCurrentIndex(index)

        self.renderEngine_hbox.addWidget(self.renderEngineDropDown)
        self.renderEngine_hbox.setContentsMargins(5, 5, 5, 5)
        self.renderEngineDropDown.setStyleSheet("background-color: rgb(50,50,50);")

        # Color Space
        self.colorSpace_groupbox = QGroupBox("")
        self.colorSpace_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80);")
        self.preferences_layout.addWidget(self.colorSpace_groupbox)
        self.colorSpace_groupbox.setAlignment(Qt.AlignTop)

        self.colorSpace_hbox = QVBoxLayout()
        self.colorSpace_hbox.setContentsMargins(5, 5, 5, 5)
        self.colorSpace_groupbox.setLayout(self.colorSpace_hbox)
        self.colorSpace_groupbox.setFixedHeight(100)

        # Label Color Information
        self.colorInformationLabel = QLabel()
        self.colorInformationLabel.setText("Color space for color conversion")
        self.colorSpace_hbox.addWidget(self.colorInformationLabel)

        # Dropdown Color Information
        self.sRGBcolorSpaceDropDown = QComboBox()
        self.sRGBcolorSpaceDropDown.addItem("sRGB")
        self.sRGBcolorSpaceDropDown.addItem("Utility - Linear - Rec.709")
        self.sRGBcolorSpaceDropDown.addItem("Utility - Linear - sRGB")
        self.sRGBcolorSpaceDropDown.addItem("Utility - sRGB - Texture")
        self.sRGBcolorSpaceDropDown.addItem("ACES - ACEScg")

        index = self.sRGBcolorSpaceDropDown.findText(self.config["rgbColorSpace"], Qt.MatchFixedString)
        if index >= 0:
            self.sRGBcolorSpaceDropDown.setCurrentIndex(index)

        self.colorSpace_hbox.addWidget(self.sRGBcolorSpaceDropDown)
        self.sRGBcolorSpaceDropDown.setStyleSheet("background-color: rgb(50,50,50);")
        #Label Raw Information
        self.rawInformationLabel = QLabel()
        self.rawInformationLabel.setText("Color space for greyscale conversion")
        self.colorSpace_hbox.addWidget(self.rawInformationLabel)
        #Dropdown Raw Information
        self.RAWcolorSpaceDropDown = QComboBox()
        self.RAWcolorSpaceDropDown.addItem("Raw")
        self.RAWcolorSpaceDropDown.addItem("Utility - Raw")

        index = self.RAWcolorSpaceDropDown.findText(self.config["rawColorSpace"], Qt.MatchFixedString)
        if index >= 0:
            self.RAWcolorSpaceDropDown.setCurrentIndex(index)

        self.colorSpace_hbox.addWidget(self.RAWcolorSpaceDropDown)
        self.RAWcolorSpaceDropDown.setStyleSheet("background-color: rgb(50,50,50);")

        #Udim Methode
        # Render Engine
        self.udim_groupbox = QGroupBox("UDIM")
        self.udim_groupbox.setStyleSheet("color: rgb(255, 255, 255); background-color: rgb(80,80,80);")
        self.preferences_layout.addWidget(self.udim_groupbox)
        self.udim_groupbox.setAlignment(Qt.AlignTop)

        self.udim_hbox = QVBoxLayout()
        self.udim_groupbox.setLayout(self.udim_hbox)
        self.udim_groupbox.setFixedHeight(50)

        self.udimDropDown = QComboBox()
        self.udimDropDown.addItem("0-Based (zBrush)")
        self.udimDropDown.addItem("1-Based (Mudbox)")
        self.udimDropDown.addItem("UDIM (Mari)")
        self.udimDropDown.addItem("Explicit Tiles")

        index = self.config["udimMethode"]
        if index >= 0:
            self.udimDropDown.setCurrentIndex(index)

        self.udim_hbox.addWidget(self.udimDropDown)
        self.udim_hbox.setContentsMargins(5, 5, 5, 5)
        self.udimDropDown.setStyleSheet("background-color: rgb(50,50,50);")



        # Save Button
        self.savePreferences_btn = QPushButton("Save")
        self.savePreferences_btn.clicked.connect(self.savePreferences)
        self.preferences_layout.addWidget(self.savePreferences_btn)


        preferencesWindow = self.preferencesQDialog.exec_()

    # Read Config from json
    def readPrefernces(self):
        config_path = script_path + "\\util\\config.json"
        with open(config_path) as configFile:
            self.config = json.load(configFile)

        return self.config

    # Save Preferences
    def savePreferences(self):
        self.assignMaterial = 0
        if self.assignToSelectionCheckBox.isChecked() == True:
            self.assignMaterial = 1
        self.renderEngine = self.renderEngineDropDown.currentText()
        self.rgbColorSpace = self.sRGBcolorSpaceDropDown.currentText()
        self.rawColorSpace = self.RAWcolorSpaceDropDown.currentText()
        self.udimMethode = self.udimDropDown.currentIndex()


        config_path = script_path + "\\util\\config.json"
        config = {}

        config["assignMaterial"] = self.assignMaterial
        config["renderEngine"] = self.renderEngine
        config["rgbColorSpace"] = self.rgbColorSpace
        config["rawColorSpace"] = self.rawColorSpace
        config["udimMethode"] = self.udimMethode


        with open(config_path, 'w') as configFile:
            json.dump(config, configFile, indent=4)

        self.preferencesQDialog.close()
        self.statusBar().showMessage("Saved Preferences!")

    # Extra Options
    def extraOptions(self):
        if self.extraOptionsGroupBox.isVisible():
            self.extraOptionsGroupBox.hide()
        else:
            self.extraOptionsGroupBox.show()

    # Create Material
    def createMaterial(self):
        materialInformationPath = script_path + "\\util\\material_information_tmp.json"
        information_dict = {}
        information_dict['material_dict'] = {}

        self.config = self.readPrefernces()
        materialName = self.materialNameLineEdit.text()
        udim = self.udimCheckbox.isChecked()
        fullControl = self.fullControlCheckbox.isChecked()

        if len(materialName) == 0:
            materialName = "defaultMaterial"

        information_dict['material_dict']['name'] = materialName
        information_dict['material_dict']['renderEngine'] = self.config["renderEngine"]
        information_dict['material_dict']['rgbColorSpace'] = self.config["rgbColorSpace"]
        information_dict['material_dict']['rawColorSpace'] = self.config["rawColorSpace"]
        information_dict['material_dict']['udimMethode'] = self.config["udimMethode"]
        information_dict['material_dict']['udim'] = udim
        information_dict['material_dict']['assignMaterial'] = self.config["assignMaterial"]
        information_dict['material_dict']['fullControl'] = fullControl

        if self.diffuse_groupbox.isVisible():
            information_dict['diffuse_dict'] = {}
            information_dict['diffuse_dict']['name'] = self.diffuseName
            information_dict['diffuse_dict']['path'] = self.diffusePath
            
        if self.ao_groupbox.isVisible():
            information_dict['ao_dict'] = {}
            information_dict['ao_dict']['name'] = self.aoName
            information_dict['ao_dict']['path'] = self.aoPath

        if self.reflection_groupbox.isVisible():
            information_dict['reflection_dict'] = {}
            information_dict['reflection_dict']['name'] = self.reflectionName
            information_dict['reflection_dict']['path'] = self.reflectionPath
            
        if self.roughness_groupbox.isVisible():
            information_dict['roughness_dict'] = {}
            information_dict['roughness_dict']['name'] = self.roughnessName
            information_dict['roughness_dict']['path'] = self.roughnessPath
            
        if self.metalness_groupbox.isVisible():
            information_dict['metalness_dict'] = {}
            information_dict['metalness_dict']['name'] = self.metalnessName
            information_dict['metalness_dict']['path'] = self.metalnessPath
            
        if self.refraction_groupbox.isVisible():
            information_dict['refraction_dict'] = {}
            information_dict['refraction_dict']['name'] = self.refractionName
            information_dict['refraction_dict']['path'] = self.refractionPath
            
        if self.subsurface_groupbox.isVisible():
            information_dict['subsurface_dict'] = {}
            information_dict['subsurface_dict']['name'] = self.subsurfaceName
            information_dict['subsurface_dict']['path'] = self.subsurfacePath
            
        if self.bump_groupbox.isVisible():
            information_dict['bump_dict'] = {}
            information_dict['bump_dict']['name'] = self.bumpName
            information_dict['bump_dict']['path'] = self.bumpPath
            
        if self.normal_groupbox.isVisible():
            information_dict['normal_dict'] = {}
            information_dict['normal_dict']['name'] = self.normalName
            information_dict['normal_dict']['path'] = self.normalPath
            
        if self.displacement_groupbox.isVisible():
            information_dict['displacement_dict'] = {}
            information_dict['displacement_dict']['name'] = self.displacementName
            information_dict['displacement_dict']['path'] = self.displacementPath
            
        if self.emission_groupbox.isVisible():
            information_dict['emission_dict'] = {}
            information_dict['emission_dict']['name'] = self.emissionName
            information_dict['emission_dict']['path'] = self.emissionPath
            
        if self.opacity_groupbox.isVisible():
            information_dict['opacity_dict'] = {}
            information_dict['opacity_dict']['name'] = self.opacityName
            information_dict['opacity_dict']['path'] = self.opacityPath


        with open(materialInformationPath, 'w') as informationFile:
            json.dump(information_dict, informationFile, indent=4)

        if information_dict['material_dict']['renderEngine'] == "Redshift":
            if cmds.pluginInfo('redshift4maya.mll', query=True, loaded=True) == True:
                createRsMaterial()
                self.dismissChannel("reset")
                self.materialNameLineEdit.setText("")
                self.statusBar().showMessage("Material was created!")
            else:
                self.statusBar().showMessage("Please load Redshift first!")

        if information_dict['material_dict']['renderEngine'] == "Arnold":
            if cmds.pluginInfo('mtoa.mll', query=True, loaded=True) == True:
                createAiMaterial()
                self.dismissChannel("reset")
                self.materialNameLineEdit.setText("")
                self.statusBar().showMessage("Material was created!")
            else:
                self.statusBar().showMessage("Please load to Arnold first!")

        if information_dict['material_dict']['renderEngine'] == "V-Ray":
            if cmds.pluginInfo('vrayformaya.mll', query=True, loaded=True) == True:
                createVrMaterial()
                self.dismissChannel("reset")
                self.materialNameLineEdit.setText("")
                self.statusBar().showMessage("Material was created!")
            else:
                self.statusBar().showMessage("Please load to V-Ray first!")


    # Close App
    def closeApp(self):
        self.close()

    def closeEvent(self, event):
        geometry = self.saveGeometry()
        self.settings.setValue('geometry', geometry)


 # Get Maya Window
def getMayaMainWindow():
    import shiboken2
    from maya import OpenMayaUI
    window = OpenMayaUI.MQtUtil.mainWindow()
    window = shiboken2.wrapInstance(int(window), QMainWindow)

    return window

# Open Window
def openUI():
    umb_window = MainWindow()
    umb_window.show()







