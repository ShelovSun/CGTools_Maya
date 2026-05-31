#!/usr/bin/env python
"""
BroDynamicsUI.py - BroDynamics User Interface. This module contains code required to create and display PySide UI of BroDynamics in Maya.
"""

import json
import os

import traceback
import urllib2
import threading
import webbrowser
import datetime

realPath = os.path.dirname(os.path.realpath(__file__))
iconPath = os.path.join(realPath, 'images')

import maya.OpenMayaUI as mui
import maya.OpenMayaUI as omui
import maya.cmds as cmds
try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
    print "Using PySide2"

except:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
    print "Using PySide"

try:
    from maya.app.general.mayaMixin import *
except:
    from mayaMixin import *

import platform

import changeLog
import dataio
import log
import utils

import BroSimulationCore



def getOS():
    try:
        osString = "{} {} ({})".format(platform.system(), platform.release(), platform.version())
    except:
        osString = ''
    return osString

def getMayaVersion():
    try:
        version = cmds.about(iv=True)
    except:
        version = "Error."
    return version


#region Importing optional libs

if os.path.isfile(os.path.join(realPath, 'BroRBDSimulationCore.py')):
    log.log (":) ", "RBD Simulation Core module exists. Plugging it in.")
    try:
        import BroRBDSimulationCore
        log.log (">", "BroRBDSimulationCore imported succesfully.")
        BroRBDCoreExists = True
    except Exception as e:
        log.log ("X", "Error importing BroRBDSimulationCore.", e)
        BroRBDCoreExists = False
else:
    BroRBDCoreExists = False


if os.path.isfile(os.path.join(realPath, 'BroLiveDynamics.py')):
    log.log (":) ", "BroLiveDynamics exists. Plugging in.")
    try:
        import BroLiveDynamics
        log.log (">", "BroLiveDynamics imported succesfully.")
        BroLiveDynamicsExists = True
    except Exception as e:
        log.log ("X", "Error importing BroLiveDynamics.", e)
        BroLiveDynamicsExists = False
else:
    BroLiveDynamicsExists = False

#endregion



def icon(name, type='i16', ext='png'):
    iconFilePath = os.path.join(iconPath, type+'_'+name+'.'+ext)
    if os.path.isfile(iconFilePath) == False:
        log.log('', "Could not find icon:", iconFilePath)
    return QPixmap(iconFilePath)



__author__ = "Mikhail Davydov"
__copyright__ = "Copyright 2016"
__version__ = changeLog.currentVersion
__email__ = "nixesvfx@gmail.com"

BroDynamicsWindow = None
BroAboutWindow = None
BroNucleusWindow = None
BroBatchWindow = None
broDynamicsCss = os.path.join(realPath, 'BroDynamics.css')
broDynamicsDefaultsIni = os.path.join(realPath, 'defaults.ini')
broDynamicsSettingsIni = os.path.join(realPath, 'settings.ini')

settingsConfig = dataio.readConfig(broDynamicsSettingsIni)
makeJokes = settingsConfig.getboolean("Settings", "makeJokes")

if makeJokes:
    jokeRate = settingsConfig.getint("Settings", "jokeRate")
    hmm = 0



#read default settings
firstLaunch = False

#region Global functions
def getTabType(index):
    if index == 0:
        type = 'Point'
    elif index == 1:
        type = 'Chain'
    elif index == 2:
        type = 'RBD'
    else:
        type = 'undefined'
    return type

def broDataGrpCheck():
    bdg = 'broDynamics_Data'
    if cmds.objExists(bdg) == False:
        bdg = cmds.group(em=True, n=bdg)
        oldSelection = cmds.ls(sl=1, long=1)
        cmds.select(bdg, r=1)
        cmds.addAttr(ln='createdWithVersion', nn='Created with Version', dt='string')
        cmds.addAttr(ln='createTime', nn='Creation time', dt='string')
        cmds.addAttr(ln='notes', dt='string')
        description = '''BroDynamics Data node.
This node stores all BroDynamics data, like the list and settings for Batch window.

You can copy this node to other scenes to move simulation settings between scenes, or you can use Presets.

BroDynamics is a script for Autodesk Maya, that can help you easily create secondary motion dynamics simulation without breaking rigs, and bake it to controls, so you can fine-tune it by hand, if needed. It is designed for animators.

Script developed and maintained by Michael Davydov:
http://www.nixes.ru

Get it on gumroad:
https://gum.co/BroDynamics

Documentation:
http://www.nixes.ru/BroTools/Documentation/BroDynamics/
        '''
        cmds.setAttr (bdg +'.createdWithVersion', changeLog.currentVersion, type='string')
        cmds.setAttr(bdg+'.createTime', datetime.datetime.now(), type='string')
        cmds.setAttr(bdg+'.notes', description, type='string')
    return bdg

def convertToQt(mayaName, objectType):
    """
    Given the name of a Maya UI element of any type, return the corresponding QT Type object.
    """
    ptr = mui.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = mui.MQtUtil.findLayout(mayaName)
        if ptr is None:
            ptr = mui.MQtUtil.findMenuItem(mayaName)
    if ptr is not None:
        return wrapInstance(long(ptr), objectType)
#endregion

# region Custom Widgets
class broDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        QDoubleSpinBox.__init__(self, parent=parent)

        self.setFixedWidth(200)


class mySpinBox(QSpinBox):
    def __init__(self, parent=None):
        QSpinBox.__init__(self, parent=parent)

        self.setFixedWidth(200)


class myObjectList(QWidget):
    def __init__(self, parent=None, title='none', acceptedTypes=['']):
        QWidget.__init__(self, parent=parent)
        wrongColor = QColor()
        wrongColor.setRgb(100, 0, 0, 100)

        def getAllItems():
            contentNames = []
            for i in range(self.list.count()):
                contentNames.append(self.list.item(i).text())

            return contentNames

        def addObjects():
            selection = cmds.ls(sl=True, long=True)

            for objName in selection:
                contentNames = getAllItems()
                if objName not in contentNames:
                    listItem = QListWidgetItem(objName)
                    objType = cmds.objectType(objName)
                    shapes = cmds.listRelatives(s=True)
                    shapeApproved = True
                    if shapes != None:
                        if len(shapes) > 0:
                            for shape in shapes:
                                if cmds.objectType(shape) not in acceptedTypes and shapeApproved:
                                    shapeApproved = False
                    #print objType
                    if objType not in acceptedTypes:
                        listItem.setBackground(wrongColor)
                    self.list.addItem(listItem)

        def removeObjects():
            for item in self.list.selectedItems():
                self.list.takeItem(self.list.row(item))

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.label = QLabel(title)
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.addBtn = QPushButton("Add")
        self.addBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_add.png')))
        self.addBtn.setWhatsThis("Add selected objects to the list.")
        self.removeBtn = QPushButton("Remove")
        self.removeBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_remove.png')))
        self.removeBtn.setWhatsThis("Remove selected objects from the list.")

        self.addBtn.clicked.connect(addObjects)
        self.removeBtn.clicked.connect(removeObjects)

        for widget in [self.label, self.list, self.addBtn, self.removeBtn]:
            self.mainLayout.addWidget(widget)

        self.list.setObjectName('myObjectList_list')

        self.loadCss()

    def loadCss(self):
        try:
            with open(broDynamicsCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())

            #print broDynamicsCss
        except:
            log.inViewLog('#FF0000', 'Unable to load CSS style for UI!')

    def getAllItems(self):
        contentNames = []
        for i in range(self.list.count()):
            contentNames.append(self.list.item(i).text())

        return contentNames


class broCollapseTab(QWidget):
    def __init__(self, parent=None, title='', doResize=True, rootWidget=None, *args, **kwargs):
        QWidget.__init__(self, parent=parent)
        self.colorVis = QColor()
        self.colorVis.setRgb(60, 60, 60, 100)
        self.title = title
        self.doResize = doResize
        self.parent = parent
        self.rootWidget = rootWidget

        self.init()

    def init(self):
        self.colorHid = QColor()
        self.colorHid.setRgb(40, 40, 40, 100)

        self.downArrow = QPixmap(os.path.join(realPath, 'downArrow.png'))
        self.rightArrow = QPixmap(os.path.join(realPath, 'rightArrow.png'))

        self.container = QWidget()
        self.titleButton = QPushButton(self.title)
        self.titleButton.setIcon(self.downArrow)
        self.titleButton.setIconSize(QSize(14, 14))
        self.titleButton.setObjectName("TabTitle")

        self.containerLayout = self.initContainerLayout()
        self.container.setLayout(self.containerLayout)

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.titleButton)
        self.mainLayout.addWidget(self.container)

        self.titleButton.clicked.connect(self.switchState)


    def initContainerLayout(self):
        return QVBoxLayout()

    def addWidget(self, item):
        self.containerLayout.addWidget(item)

    def addLayout(self, item):
        self.containerLayout.addLayout(item)

    def switchState(self):
        if self.container.isHidden():
            self.container.show()
            self.titleButton.setIcon(self.downArrow)
        else:
            self.container.hide()
            self.titleButton.setIcon(self.rightArrow)
        self.resizeParent()

    def unlockHeight(self):
        self.parent.setMaximumSize(10000, 10000)

    def lockHeight(self):
        self.parent.initHeight = self.parent.sizeHint().height()
        # self.parent.initWidth = self.parent.sizeHint().width()
        self.parent.setMaximumHeight(self.parent.initHeight)
        # self.parent.setMaximumWidth(self.parent.initWidth)

    def resizeParent(self):
        if self.doResize:
            self.unlockHeight()
            self.parent.resize(0, 0)
            self.lockHeight()

class broCollapseGridTab(broCollapseTab):
    def __init__(self, parent=None, title='', doResize=True, rootWidget=None, *args, **kwargs):
        QWidget.__init__(self, parent=parent)
        self.colorVis = QColor()
        self.colorVis.setRgb(60, 60, 60, 100)
        self.title = title
        self.doResize = doResize
        self.parent = parent
        self.rootWidget = rootWidget
        self.init()

    def initContainerLayout(self):
        return QGridLayout()

    def addWidget(self, item, column, row):
        self.containerLayout.addWidget(item, column, row)

    def addLayout(self, item, column, row):
        self.containerLayout.addLayout(item, column, row)



class broWidgetVLayout(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent=parent)

        self.mainLayout = QVBoxLayout()

        self.setLayout(self.mainLayout)
        self.setAutoFillBackground(True)


    def addWidget(self, widget):
        self.mainLayout.addWidget(widget)

    def setBackgroundColor(self, r,g,b,a):
        self.color = QColor()
        self.color.setRgb(r,g,b,a)

        self.p = self.palette()
        self.p.setColor(self.backgroundRole(), self.color)
        self.setPalette(self.p)

class broGridWidgetLayout(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        QWidget.__init__(self, parent=parent)

        self.mainLayout = QGridLayout()

        self.setLayout(self.mainLayout)

    def addWidget(self, widget, column, row):
        self.mainLayout.addWidget(widget, column, row)


class broImageButton(QPushButton):
    def __init__(self, pixmap, parent=None):
        super(broImageButton, self).__init__(parent)
        self.pixmap = pixmap

    def paintEvent(self, event):
        self.selRect = QRect(0,0,10,21)
        painter = QPainter(self)
        painter.drawRect(self.selRect)
        painter.drawPixmap(event.rect(), self.pixmap)

    def focusInEvent(self, *args, **kwargs): # real signature unknown
        pass

    def sizeHint(self):
        return self.pixmap.size()
# endregion

#region Child Windows

class WelcomeWindow(MayaQWidgetBaseMixin, QWidget):
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(WelcomeWindow, self).__init__(*args, **kwargs)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QWidget)

        try:
            with open(broDynamicsCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())
        except Exception as e:
            log.inViewLog('#FF0000', 'Unable to load CSS style for UI! ' + str(e))

        self.rootWidget = rootWidget

        self.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)
        self.setWindowModality(Qt.ApplicationModal)

        #Accept Decline buttons and layout
        self.buttonLayout = QHBoxLayout()

        self.acceptBtn = QPushButton("Accept")
        self.declineBtn = QPushButton("Decline")

        self.buttonLayout.addWidget(self.acceptBtn)
        self.buttonLayout.addWidget(self.declineBtn)

        self.acceptBtn.clicked.connect(self.accept)
        self.declineBtn.clicked.connect(self.decline)


        #rest of the stuff
        self.setWindowIcon(QIcon(os.path.join(realPath, 'images', 'i32_logo.png')))

        self.setWindowTitle("Thanks for buying BroDynamics!")

        self.mainLayout = QVBoxLayout()

        self.textField = QTextBrowser()
        self.textField.setOpenExternalLinks(True)
        self.textField.setHtml(changeLog.welcome.replace('\n', '<br>'))
        self.textFieldLabel = QLabel("Intro notice")
        self.textFieldLabel.setObjectName("IntroNoticeLabel")

        self.licenseField = QTextBrowser()
        self.licenseField.setOpenExternalLinks(True)
        self.licenseField.setHtml(changeLog.lic.replace('\n', '<br>'))
        self.licenseFieldLabel = QLabel("License agreement")
        self.licenseFieldLabel.setObjectName("IntroLicenseLabel")

        directory = os.path.dirname(os.path.abspath(__file__))
        imagePath = os.path.join(directory, 'BroDynamics.png')
        imageLabel = QLabel(self)
        imageMap = QPixmap(imagePath)
        imageLabel.setPixmap(imageMap)

        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(imageLabel)
        self.mainLayout.addWidget(self.textFieldLabel)
        self.mainLayout.addWidget(self.textField)
        self.mainLayout.addWidget(self.licenseFieldLabel)
        self.mainLayout.addWidget(self.licenseField)
        self.mainLayout.addLayout(self.buttonLayout)



        mayaMainWindowPtr = omui.MQtUtil.mainWindow()
        mayaMainWindow = wrapInstance(long(mayaMainWindowPtr), QWidget)


        self.resize(640, 640)

    def showEvent(self, *args, **kwargs):
        self.updateInfoThread()


    def updateInfoThread(self):
        try:
            connected = cmds.about(cnt=True)
        except:
            connected = True

        if connected:
            self.updateInfo()
        else:
            log.inViewLog("#FF0000", "BroDynamics: No connection to the internet. License and Changelog and Welcome text may be outdated.")

    def updateInfo(self):
        changeLog.updateInfo()
        self.textField.setHtml(changeLog.welcome.replace('\n', '<br>'))
        self.licenseField.setHtml(changeLog.lic.replace('\n', '<br>'))

    def decline(self):
        self.rootWidget.close()


    def accept(self):
        settingsConfig = dataio.readConfig(broDynamicsSettingsIni)
        settingsConfig.set('Settings', 'firstLaunch', False)
        settingsFile = open(broDynamicsSettingsIni,'w')
        settingsConfig.write(settingsFile)
        settingsFile.close()
        self.close()


class AboutWindow(MayaQWidgetBaseMixin, QWidget):
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(AboutWindow, self).__init__(*args, **kwargs)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QWidget)

        self.setWindowIcon(QIcon(os.path.join(realPath, 'images', 'i32_logo.png')))

        self.setWindowFlags(Qt.Dialog)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)

        self.setWindowTitle("About BroDynamics")

        mainLayout = QVBoxLayout()

        self.textField = QTextBrowser()

        try:
            with open(broDynamicsCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())
        except Exception as e:
            log.inViewLog('#FF0000', 'Unable to load CSS style for UI! ' + str(e))

        #Update info button
        self.updateBtn = QPushButton("Update")
        self.updateBtn.setStatusTip("Download actual info.txt file and update text in About window.")
        self.updateBtn.clicked.connect(self.updateInfoThread)

        directory = os.path.dirname(os.path.abspath(__file__))
        imagePath = os.path.join(directory, 'BroDynamics.png')
        imageLabel = QLabel(self)
        imageMap = QPixmap(imagePath)
        imageLabel.setPixmap(imageMap)

        self.textField.setHtml(changeLog.about.replace('\n', '<br>'))

        self.latestVersion = QLabel("Trying to get latest version...")

        self.setLayout(mainLayout)
        mainLayout.addWidget(imageLabel)
        mainLayout.addWidget(self.textField)
        mainLayout.addWidget(self.latestVersion)
        mainLayout.addWidget(self.updateBtn)

        self.resize(640, 480)
        #print "SIZEHINT:", self.sizeHint()
        # download_thread = threading.Thread(target=self.getVersion)
        # download_thread.start()

    def showEvent(self, *args, **kwargs):
        data = changeLog.getInfoFromFile()
        self.textField.setHtml(changeLog.about.replace('\n', '<br>'))

    def updateInfoThread(self):
        try:
            connected = cmds.about(cnt=True)
        except:
            connected = True

        if connected:
            download_thread = threading.Thread(target=self.updateInfo())
            download_thread.start()
        else:
            log.inViewLog("#FF0000", "BroDynamics: No connection to the internet. License and Changelog and Welcome text may be outdated.")

    def updateInfo(self):
        changeLog.updateInfo()
        text = "Your version: {0}; Latest version: {1};".format(changeLog.currentVersion, changeLog.latestVersion)
        self.latestVersion.setText(text)
        self.textField.setHtml(changeLog.about.replace('\n', '<br>'))


class NucleusWindow(MayaQWidgetBaseMixin, QWidget):
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(NucleusWindow, self).__init__(*args, **kwargs)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QWidget)

        self.setWindowIcon(QIcon(os.path.join(realPath, 'images', 'i16_nucleus.png')))

        self.setWindowFlags(Qt.Dialog)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)

        self.setWindowTitle("Nucleus settings")

        self.mainLayout = QHBoxLayout()

        self.collidersList = myObjectList(self, 'Colliders', ['transform', 'mesh', 'nurbsSurface'])
        self.collidersList.setWhatsThis("You can add any geometry objects to this list, and they will be turned into nCloth Passive colliders during Point or Chain simulations. Alternatively, you can create your own nuceleus node and call it 'nucleus1', then it will be used by simulation with settings you give it and objects you set.")
        self.forcesList = myObjectList(self, 'Forces', ['vortexField','uniformField','turbulenceField','radialField','newtonField','dragField','airField','gravityField'])
        self.forcesList.setWhatsThis("A list of force objects. These will be added to Chain nHair simulation.")

        for widget in [self.collidersList, self.forcesList]:
            self.mainLayout.addWidget(widget)

        self.setLayout(self.mainLayout)

        try:
            with open(broDynamicsCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())

            #print broDynamicsCss
        except:
            log.inViewLog('#FF0000', 'Unable to load CSS style for UI!')

        self.resize(450, 435)

class BatchWindow(MayaQWidgetBaseMixin, QDialog):
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(BatchWindow, self).__init__(*args, **kwargs)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QWidget)

        self.setWindowIcon(QIcon(os.path.join(realPath, 'images', 'i16_simulate_all.png')))

        parent = self.rootWidget

        self.loadCss()

        self.setWindowFlags(Qt.Dialog)
        self.setAttribute(Qt.WA_AlwaysShowToolTips)



        self.parent = parent

        self.setWindowTitle("Batch simulation")

        self.mainLayout = QVBoxLayout()

        self.setLayout(self.mainLayout)

        self.addBtn = QPushButton("Add")
        self.addBtn.clicked.connect(self.add)
        self.addBtn.setObjectName("AddBtn")
        self.addBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_add.png')))
        descr = "Selected objects will be added to the list with settings from UI as a single Item."
        self.addBtn.setStatusTip(descr)
        self.addBtn.setWhatsThis(descr)

        self.removeBtn = QPushButton("Remove")
        self.removeBtn.clicked.connect(self.remove)
        self.removeBtn.setObjectName("RemoveBtn")
        self.removeBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_remove.png')))
        descr = "Selected element(s) will be removed from the list."
        self.removeBtn.setStatusTip(descr)
        self.removeBtn.setWhatsThis(descr)

        self.replaceBtn = QPushButton("Replace")
        self.replaceBtn.clicked.connect(self.replace)
        self.replaceBtn.setObjectName("ReplaceBtn")
        self.replaceBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_replace.png')))
        descr = "Selected element will be replaced. Objects will be replaced with selected, and settings will be replaced with current UI settings."
        self.replaceBtn.setStatusTip(descr)
        self.replaceBtn.setWhatsThis(descr)

        self.renameBtn = QPushButton("Rename")
        self.renameBtn.clicked.connect(self.rename)
        self.renameBtn.setObjectName("RenameBtn")
        self.renameBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_rename.png')))
        descr = "Rename selected item(s). Numbers will be added automatically. Note that renaming window may appear behind this window, so you might want to move it to the side. Sorry for this."
        self.renameBtn.setStatusTip(descr)
        self.renameBtn.setWhatsThis(descr)

        self.getSettingsBtn = QPushButton("Get")
        self.getSettingsBtn.clicked.connect(self.getSettingsFromSelected)
        self.getSettingsBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_get.png')))
        descr = "Settings from current first selected Item will be applied to the UI."
        self.getSettingsBtn.setStatusTip(descr)
        self.getSettingsBtn.setWhatsThis(descr)

        self.setSettingsBtn = QPushButton("Set")
        self.setSettingsBtn.clicked.connect(self.replaceSettings)
        self.setSettingsBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_set.png')))
        descr = "Settings in the Item(s) will be replaced with current UI settings."
        self.setSettingsBtn.setStatusTip(descr)
        self.setSettingsBtn.setWhatsThis(descr)

        self.selectBtn = QPushButton("Select")
        self.selectBtn.clicked.connect(self.selectObjectsFromSelected_replace)
        self.selectBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_aselect.png')))
        descr = "Select objects in the viewport from selected Items."
        self.selectBtn.setStatusTip(descr)
        self.selectBtn.setWhatsThis(descr)

        self.selectAddBtn = QPushButton("Select Add")
        self.selectAddBtn.clicked.connect(self.selectObjectsFromSelected_add)
        self.selectAddBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_aselect_add.png')))
        descr = "Append objects to viewport selection from selected Items."
        self.selectAddBtn.setStatusTip(descr)
        self.selectAddBtn.setWhatsThis(descr)

        self.startBtn = QPushButton("Start")
        self.startBtn.clicked.connect(self.startBatchSimulation)
        self.startBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_simulate_all.png')))
        descr = "Start simulation. If something is selected in the list - only selected Items will be simulated. If nothing is selected - everything will be simulated."
        self.startBtn.setStatusTip(descr)
        self.startBtn.setWhatsThis(descr)

        self.buttonLayout = QGridLayout()

        self.buttonLayout.addWidget(self.addBtn, 0, 0)
        self.buttonLayout.addWidget(self.removeBtn, 0, 1)
        self.buttonLayout.addWidget(self.replaceBtn, 0, 2)
        self.buttonLayout.addWidget(self.renameBtn, 0, 3)
        self.buttonLayout.addWidget(self.getSettingsBtn, 1, 0)
        self.buttonLayout.addWidget(self.setSettingsBtn, 1, 1)
        self.buttonLayout.addWidget(self.selectBtn, 1, 2)
        self.buttonLayout.addWidget(self.selectAddBtn, 1, 3)

        # Treeview
        defaultConfig = dataio.readConfig(broDynamicsDefaultsIni)
        defItems = defaultConfig.items('AllSettings')

        self.treeView = QTreeWidget()
        self.treeView.setSelectionMode(QAbstractItemView.MultiSelection)
        self.treeView.setColumnCount(3)
        self.treeView.setHeaderLabels(['Name', 'Type', 'Data'])
        self.treeView.setObjectName("objectSelectView")
        descr = "A list of Items. Each item has a name, which you can replace, and which is just used for display purposes. And a JSON data, containing settings and objects for simulation. Each item will be simulated one by one, one after another. Mind, that actual data for simulation will be taken from the NODE (group node in the scene, called broDynamics_Data) not the UI. Node data is updated each time you use Add, Remove, Replace or Set, and each time you open the Batch window, or load a new Maya Scene."
        self.treeView.setStatusTip(descr)
        self.treeView.setWhatsThis(descr)

        self.mainLayout.addWidget(self.treeView)
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addWidget(self.startBtn)

        self.treeView.itemSelectionChanged.connect(self.simulateButtonTest)
        self.simulateButtonTest()

        # self.restoreFromNode()

        self.resize(450, 435)

    @utils.try_except
    def add(self, replace=False, it=''):
        name = cmds.ls(sl=True)[0]
        selection = cmds.ls(sl=True, l=True)
        settings = {}


        defaultConfig = dataio.readConfig(broDynamicsDefaultsIni, silent=True)
        config = dataio.newConfig()

        sections = [name]
        for section in sections:
            config.add_section(section)
            for item in defaultConfig.items('AllSettings'):
                #print "Looking for:", item[0]
                element = self.parent.findChild(QCheckBox, item[0])
                if element != None:
                    config.set(section, item[0], element.isChecked())
                    settings[item[0]] = element.isChecked()

                element = self.parent.findChild(QDoubleSpinBox, item[0])
                if element != None:
                    config.set(section, item[0], element.value())
                    settings[item[0]] = element.value()

                element = self.parent.findChild(QSpinBox, item[0])
                if element != None:
                    config.set(section, item[0], element.value())
                    settings[item[0]] = element.value()

                element = self.parent.findChild(QRadioButton, item[0])
                if element != None:
                    config.set(section, item[0], element.isChecked())
                    settings[item[0]] = element.isChecked()

        # cfgfilePath = os.path.dirname(os.path.realpath(__file__))+"\temp.ini"
        element = [name, selection, settings]
        elementJSON = json.dumps(element)
        if replace:
            self.treeItem = it
        else:
            self.treeItem = QTreeWidgetItem(self.treeView, [name])
        itemType = getTabType(self.parent.tabWidget.currentIndex())
        self.treeItem.setData(1, Qt.EditRole, itemType)
        self.treeItem.setData(2, Qt.EditRole, elementJSON)
        self.treeItem.setIcon(1, QIcon(os.path.join(realPath, 'images', 'i16_{0}.png'.format(itemType))))
        self.storeToNode()

        '''
        cfgfile = open(cfgfilePath,'w')
        config.write(cfgfile)
        cfgfile.close()
        log.inViewLog("Config saved: "+str(cfgfilePath))
        '''
        # Store array: name:value,name:value. Then parse it to and from string?
        cmds.select(selection, r=True)

    @utils.try_except
    def remove(self):
        root = self.treeView.invisibleRootItem()
        for item in self.treeView.selectedItems():
            (item.parent() or root).removeChild(item)
        self.storeToNode()

    @utils.try_except
    def replaceSettings(self):
        oldSel = cmds.ls(sl=1, l=1)
        root = self.treeView.invisibleRootItem()
        for item in self.treeView.selectedItems():
            dataJSON = item.text(2)
            data = json.loads(dataJSON)
            objects = data[1]

            cmds.select(objects, r=1)
            self.add(True, item)
            log.log("/", "Updated item's settings for: " + str(data[0]))

        cmds.select(oldSel, r=1)
        self.storeToNode()
        log.inViewLog("#00FF00", "Settings updated.")

    @utils.try_except
    def replace(self):
        root = self.treeView.invisibleRootItem()
        for item in self.treeView.selectedItems():
            dataJSON = item.text(2)
            data = json.loads(dataJSON)
            self.add(True, item)
            log.log("/", "Replaced: " + str(data[0]))

        self.storeToNode()
        log.inViewLog("#00FF00", "Settings updated.")

    @utils.try_except
    def rename(self):
        result = cmds.promptDialog(
            title='Rename Object',
            message='Enter Name:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')

        if result == 'OK':
            items = self.treeView.selectedItems()
            newName = cmds.promptDialog(query=True, text=True)
            for i, item in enumerate(items):
                item.setText(0, newName + '_' + str(i))
            self.storeToNode()

    def storeToNode(self):
        node = broDataGrpCheck()
        attr = 'broDynamics_BatchData'
        if cmds.objExists(node + '.' + attr) == False:
            s = cmds.ls(sl=True, l=True)
            cmds.select(node, r=1)
            cmds.addAttr(ln=attr, dt='string')
            if not cmds.objExists(node+'.updatedWithVersion'):
                cmds.addAttr(ln='updatedWithVersion', nn='Updated with Version', dt='string')
            if not cmds.objExists(node+'.lastUpdateTime'):
                cmds.addAttr(ln='lastUpdateTime', nn='Last update', dt='string')
            cmds.select(s, r=1)
        data = []
        root = self.treeView.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            data.append([item.text(0), item.text(1), item.text(2)])

        jsonData = json.dumps(data)
        cmds.setAttr(node + '.' + attr, jsonData, type='string')
        cmds.setAttr(node + '.lastUpdateTime', datetime.datetime.now(), type='string')
        cmds.setAttr(node + '.updatedWithVersion', changeLog.currentVersion, type='string')

    def simulateItem(self,item):
        cmds.refresh()
        itemName = item.text(0)
        itemType = item.text(1)
        dataJSON = item.text(2)
        data = json.loads(dataJSON)
        name = data[0]
        objects = data[1]
        settings = data[2]
        log.log ('<>', 'simulateItem START', itemName, '\n')

        '''
        print '\n'
        print 'itemName', itemName
        print 'itemType', itemType
        print 'dataJSON', dataJSON
        print 'name', name
        print 'data', data
        print 'objects', objects
        print 'settings', settings
        print "skipCONTROLS", settings['skipControls']
        print "\n\n"
        '''

        fx = 0
        fy = 0
        fz = 0
        ux = 0
        uy = 0
        uz = 0

        if settings['frontX']:
            fx = 1
        if settings['frontY']:
            fy = 1
        if settings['frontZ']:
            fz = 1
        if settings['upX']:
            ux = 1
        if settings['upY']:
            uy = 1
        if settings['upZ']:
            uz = 1

        if settings['frontR']:
            fx *= -1
            fy *= -1
            fz *= -1

        if settings['upR']:
            ux *= -1
            uy *= -1
            uz *= -1

        try:
            cmds.undoInfo(ock=True)
            log.log('>', 'SIMULATION START')
            if itemType == 'Chain':
                log.log('>', 'Item type,', itemType)
                BroSimulationCore.simulateNHair(objects, axis=[fx, fy, fz], up=[ux, uy, uz],
                                                matchPositions=settings['matchPositions'],
                                                aimRotation=settings['aimRotation'], skipFrames=settings['skipFrames'],
                                                skipControls=settings['skipControls'], attract=settings['attract'],
                                                attractionDamp=settings['attractionDamp'],
                                                bendResistance=settings['bendResistance'],
                                                stretchResistance=settings['stretchResistance'],
                                                compressionResistance=settings['compressionResistance'],
                                                drag=settings['drag'], damp=settings['damp'],
                                                motionDrag=settings['motionDrag'],
                                                mass=settings['nHairMass'],
                                                collideWidthOffset=settings['collideWidthOffset'],
                                                dontRefresh=BroDynamicsWindow.dontRefresh.isChecked(),
                                                reversed=settings['frontR'],
                                                colliders=BroDynamicsWindow.BroNucleusWindow.collidersList.getAllItems(),
                                                forces=BroDynamicsWindow.BroNucleusWindow.forcesList.getAllItems(),
                                                collisionMode=settings['collisionMode'])
            elif itemType == 'Point':
                log.log('>', 'Item type,', itemType)
                BroSimulationCore.simulateNParticles(objects, 1, settings["singleObjWeight"],
                                                     settings["singleObjSmoothness"], BroDynamicsWindow.dontRefresh.isChecked(),
                                                     collide = settings["collide"],
                                                     selfCollide =settings["selfCollide"],
                                                     collideWidthScale=settings["collideWidthScale"],
                                                     bounce=settings["bounce"],
                                                     friction=settings["friction"],
                                                     stickiness=settings["stickiness"],
                                                     drag=settings["drag"],
                                                     damp=settings["damp"])
            elif itemType == 'RBD':
                log.log('>', 'Item type,', itemType)
                if BroRBDCoreExists:
                    BroRBDSimulationCore.simulateRBDControls(objects, dontRefresh=BroDynamicsWindow.dontRefresh.isChecked())
                else:
                    log.inViewLog("#FF0000", "RBD Module is missing. Item", itemName, "won't be simulated. Get BroDynamics RBD Module for it to work, or chech if it is installed correctly.")
            cmds.undoInfo(cck=True)
        except Exception as e:
            cmds.undoInfo(cck=True)
            log.log('>', 'SIMULATION FAILED', e)
        log.log ('<>', 'simulateItem END', itemName, '\n')
        cmds.refresh()

    @utils.try_except
    def startBatchSimulation(self):
        selection = cmds.ls(sl=True)  # store selection
        self.oldMessage = self.parent.statusBar.currentMessage()

        selectedItems = self.treeView.selectedItems()
        print "SELECTED:", str(selectedItems)
        if len(selectedItems) > 0:
            for idx, item in enumerate(selectedItems):
                self.parent.statusBar.showMessage("Batch simulation. " + str(idx) + '\\' + str(len(selectedItems)), 0)
                self.simulateItem(item)

        else:
            root = self.treeView.invisibleRootItem()
            child_count = root.childCount()
            for i in range(child_count):
                self.parent.statusBar.showMessage("Batch simulation. " + str(i) + '\\' + str(child_count), 0)
                item = root.child(i)
                self.simulateItem(item)

        self.parent.statusBar.showMessage(self.oldMessage, 0)

        if selection != None:
            if len(selection) > 0:
                cmds.select(selection, r=True)

    def loadCss(self):
        try:
            with open(broDynamicsCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())

            #print broDynamicsCss
        except:
            log.inViewLog('#FF0000', 'Unable to load CSS style for UI!')

    def simulateButtonTest(self):
        selectedItems = self.treeView.selectedItems()
        if len(selectedItems) > 0:
            self.startBtn.setText("Simulate selected")
            self.startBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_simulate_selected.png')))
        else:
            self.startBtn.setText("Simulate all")
            self.startBtn.setIcon(QPixmap(os.path.join(realPath, 'images', 'i16_simulate_all.png')))

    def selectObjectsFromSelected(self, replace=True):
        selectedItems = self.treeView.selectedItems()

        notFound = []
        del notFound[:]
        if replace:
            cmds.select(cl=True)

        for item in selectedItems:
            dataJSON = item.text(2)
            data = json.loads(dataJSON)
            objects = data[1]
            for obj in objects:
                if cmds.objExists(obj):
                    cmds.select(obj, add=True)
                else:
                    objName = obj.split('|')
                    objName = objName[len(objName) - 1]
                    notFound.append(objName)
        if len(notFound) > 0:
            log.inViewLog("#FF2020", "Missing Objects:", str(notFound))
        else:
            log.inViewLog("#20FF20", "Successfully selected objects")

    def selectObjectsFromSelected_replace(self):
        self.selectObjectsFromSelected(replace=True)

    def selectObjectsFromSelected_add(self):
        self.selectObjectsFromSelected(replace=False)

    def getSettingsFromSelected(self):
        selectedItems = self.treeView.selectedItems()
        item = selectedItems[0]
        itemName = item.text(0)
        itemType = item.text(1)
        dataJSON = item.text(2)
        data = json.loads(dataJSON)
        name = data[0]
        objects = data[1]
        settings = data[2]

        try:
            defaultConfig = dataio.readConfig(broDynamicsDefaultsIni)
            sections = ['AllSettings']
            for section in sections:
                for item in defaultConfig.items(section):
                    #print "Looking for:", item[0], 'in', section
                    #print "Item:" ,item
                    try:
                        element = self.rootWidget.findChild(QCheckBox, item[0])

                        if element != None:
                            element.setChecked(settings[item[0]])

                        element = self.rootWidget.findChild(QDoubleSpinBox, item[0])
                        if element != None:
                            element.setValue(settings[item[0]])

                        element = self.rootWidget.findChild(QSpinBox, item[0])
                        if element != None:
                            element.setValue(settings[item[0]])

                        element = self.rootWidget.findChild(QRadioButton, item[0])
                        if element != None:
                            element.setChecked(settings[item[0]])
                    except:
                        print "Could not set parameter:", str(item[0]), "skipping."

            log.inViewLog("#20FF20", "Config loaded")
        except Exception as e:
            log.inViewLog("#FF2020", "Error:", e)
            print traceback.print_exc()

    def restoreFromNode(self, silent=False):
        attr = 'broDynamics_Data.broDynamics_BatchData'
        if cmds.objExists(attr):
            jsonData = cmds.getAttr(attr)
            data = json.loads(jsonData)
            self.treeView.clear()
            for item in data:
                try:
                    self.treeItem = QTreeWidgetItem(self.treeView, [item[0]])
                    self.treeItem.setData(1, Qt.EditRole, item[1])
                    self.treeItem.setData(2, Qt.EditRole, item[2])
                    self.treeItem.setIcon(1, QIcon(os.path.join(realPath, 'images', 'i16_{0}.png'.format(item[1]))))
                except Exception as e:
                    try:
                        log.log ('warning', 'Could not load data from node. Item:', item[0], '. Error: ', e)
                    except:
                        log.log ('warning', 'Cloud not load data from node. Unknown error.')
            if not silent:
                log.log('<', "Data loaded from node.")
        else:
            log.log("/", "Found no data stored in the scene.")
#endregion


# region Main Window
class DockableWindow(MayaQWidgetDockableMixin, QMainWindow):
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(DockableWindow, self).__init__(rootWidget)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QWidget)

        self.setWindowIcon(QIcon(os.path.join(realPath, 'images', 'i32_logo.png')))

        # Destroy this widget when closed.  Otherwise it will stay around
        self.setAttribute(Qt.WA_DeleteOnClose, True)

        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        self.loadCss()

        self.createScriptJobs()

        self.initChildWindows()

        self.textField = QTextBrowser()
        self.textField.setFixedHeight(0)
        self.textField.hide()

        # region image
        directory = os.path.dirname(os.path.abspath(__file__))
        imagePath = os.path.join(directory, 'BroDynamics.png')
        imageLabel = QLabel(self)
        imageMap = QPixmap(imagePath)
        imageLabel.setPixmap(imageMap)
        imageLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        # endregion

        # region create fonts
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)

        fontHeading = QFont()
        fontHeading.setPointSize(12)
        # endregion

        # region create a widget
        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.setWindowTitle("BroDynamics")
        # endregion

        # region Init Layouts
        self.mainLayout = QVBoxLayout(widget)
        self.buttonLayout = QVBoxLayout()


        self.pointTabLayout = broWidgetVLayout()
        self.pointTabLayout.setBackgroundColor(250,163,0, 4)
        
        self.ChainTabLayout = broWidgetVLayout()
        self.ChainTabLayout.setBackgroundColor(0,149,182, 4)
        
        self.RBDTabLayout = broWidgetVLayout()
        self.RBDTabLayout.setBackgroundColor(220,220,220, 4)
        
        # endregion

        # region CollapseTabs and FormLayout init

        # region simulateCTab
        self.simulationCTab = broCollapseTab(self.ChainTabLayout, "Simulation properties", rootWidget=self)
        self.simulationFormLayout = QFormLayout()
        self.simulationFormLayout.setLabelAlignment(Qt.AlignRight)
        self.simulationFormLayout.setAlignment(Qt.AlignRight)
        self.simulationFormLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.simulationCTab.addLayout(self.simulationFormLayout)
        # endregion

        # region aligmentCTab
        self.aligmentCTab = broCollapseTab(self.ChainTabLayout, "Aligment settings", rootWidget=self)
        self.aligmentFormLayout = QFormLayout()
        self.aligmentFormLayout.setLabelAlignment(Qt.AlignRight)
        self.aligmentFormLayout.setAlignment(Qt.AlignRight)
        self.aligmentFormLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.aligmentCTab.addLayout(self.aligmentFormLayout)
        # endregion

        # region otherCTab
        self.otherCTab = broCollapseTab(self.ChainTabLayout, "General settings", rootWidget=self)
        self.otherFormLayout = QFormLayout()
        self.otherFormLayout.setLabelAlignment(Qt.AlignRight)
        self.otherFormLayout.setAlignment(Qt.AlignRight)
        self.otherFormLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.otherCTab.addLayout(self.otherFormLayout)
        # endregion

        # region singleObjSettingsCTab
        self.singleObjSettingsCTab = broCollapseTab(self.pointTabLayout, "Simulation properties", rootWidget=self)
        self.singleObjSettingsFormLayout = QFormLayout()
        self.singleObjSettingsFormLayout.setLabelAlignment(Qt.AlignRight)
        self.singleObjSettingsFormLayout.setAlignment(Qt.AlignRight)
        self.singleObjSettingsFormLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.singleObjSettingsCTab.addLayout(self.singleObjSettingsFormLayout)

        self.pointSettingsFormLayout = QFormLayout()
        self.pointSettingsFormLayout.setLabelAlignment(Qt.AlignRight)
        self.pointSettingsFormLayout.setAlignment(Qt.AlignRight)
        self.pointSettingsFormLayout.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        # endregion

        # region RBDSCTabs
        self.rbdSetupCTab = broCollapseGridTab(self.RBDTabLayout, title="Setup", rootWidget=self)

        self.rbdCTab = broCollapseGridTab(self.RBDTabLayout, title="Workbench", rootWidget=self)

        # endregion

        # endregion

        # region Tab Layouts Populate
        self.ChainTabLayout.addWidget(self.otherCTab)
        self.ChainTabLayout.addWidget(self.aligmentCTab)
        self.ChainTabLayout.addWidget(self.simulationCTab)

        self.pointTabLayout.addWidget(self.singleObjSettingsCTab)

        self.RBDTabLayout.addWidget(self.rbdSetupCTab)
        self.RBDTabLayout.addWidget(self.rbdCTab)
        # endregion

        # region TABS
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.pointTabLayout,
                              QIcon(os.path.join(realPath, 'images', 'i16_Point.png')), 'Points')
        self.tabWidget.addTab(self.ChainTabLayout,
                              QIcon(os.path.join(realPath, 'images', 'i16_Chain.png')), 'Chains')
        self.tabWidget.addTab(self.RBDTabLayout,
                              QIcon(os.path.join(realPath, 'images', 'i16_RBD.png')), 'RBD')

        self.tabWidget.currentChanged.connect(self.switchTabReaction)

        if BroRBDCoreExists != True:
            self.tabWidget.setTabEnabled(2, False)
        # endregion

        # region  populate main layout
        self.mainLayout.addLayout(self.buttonLayout)
        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addStretch()
        self.mainLayout.setSpacing(0)
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        # endregion

        #region Header elements, Start button
        self.simulateIcon = os.path.join(realPath, 'images', 'i16_simulate.png')
        self.simulateChainIcon = os.path.join(realPath, 'images', 'i16_simulate_chain.png')
        self.simulateRBDIcon = os.path.join(realPath, 'images', 'i16_simulate_RBD.png')
        self.simButton = QPushButton("")#broImageButton(QPixmap(self.simulateIcon))

        if os.path.isfile(self.simulateIcon):
            self.simButton.setIcon(QPixmap(self.simulateIcon))
        else:
            self.simButton = QPushButton("Simulate")

        self.simButton.setFixedHeight(40)
        self.simButton.setStatusTip('Simulate and bake keys on controls for the active timeslider range.')
        self.simButton.installEventFilter(self)
        self.simButton.setObjectName("SimulateButton")
        self.simButton.clicked.connect(self.startSimulation)

        #endregion

        # region ========== CHAIN TAB CONTENTS ==========
        dummy = QLabel('')

        axisFrontLayout = QHBoxLayout()
        axisUpLayout = QHBoxLayout()

        self.frontX = QRadioButton("X")
        self.frontX.setObjectName('frontX')
        self.frontY = QRadioButton("Y")
        self.frontY.setObjectName('frontY')
        self.frontZ = QRadioButton("Z")
        self.frontZ.setObjectName('frontZ')
        self.frontR = QCheckBox("Reverse")
        self.frontR.setObjectName('frontR')

        self.frontX.setChecked(True)

        axisFrontLayout.addWidget(self.frontX)
        axisFrontLayout.addWidget(self.frontY)
        axisFrontLayout.addWidget(self.frontZ)
        axisFrontLayout.addWidget(self.frontR)

        self.frontGrp = QGroupBox()
        self.frontGrp.setStatusTip("Control objects' forward axis.")
        self.frontGrp.installEventFilter(self)
        self.frontGrp.setLayout(axisFrontLayout)

        self.upX = QRadioButton("X")
        self.upX.setObjectName('upX')
        self.upY = QRadioButton("Y")
        self.upY.setObjectName('upY')
        self.upZ = QRadioButton("Z")
        self.upZ.setObjectName('upZ')
        self.upR = QCheckBox("Reverse")
        self.upR.setObjectName('upR')
        self.upY.setChecked(True)

        axisUpLayout.addWidget(self.upX)
        axisUpLayout.addWidget(self.upY)
        axisUpLayout.addWidget(self.upZ)
        axisUpLayout.addWidget(self.upR)

        self.upGrp = QGroupBox()
        self.upGrp.setStatusTip("Control objects' up axis. Will be aligned to the rotation of the first ctrl.")
        self.upGrp.installEventFilter(self)
        self.upGrp.setLayout(axisUpLayout)

        self.attract = broDoubleSpinBox()
        self.attract.setStatusTip('Stiffness. How much controls try to match the initial pose.')
        self.attract.installEventFilter(self)
        self.attract.setObjectName('attract')
        self.attractionDamp = broDoubleSpinBox()
        self.attractionDamp.setStatusTip('Dampening. Air density\\viscocity.')
        self.attractionDamp.installEventFilter(self)
        self.attractionDamp.setObjectName('attractionDamp')
        self.bendResistance = broDoubleSpinBox()
        self.bendResistance.setStatusTip('Controls how stiff the chain is.')
        self.bendResistance.installEventFilter(self)
        self.bendResistance.setObjectName('bendResistance')
        self.stretchResistance = broDoubleSpinBox()
        self.stretchResistance.setStatusTip('Works only with position turned on.')
        self.stretchResistance.installEventFilter(self)
        self.stretchResistance.setObjectName('stretchResistance')

        self.compressionResistance = broDoubleSpinBox()
        self.compressionResistance.setStatusTip('Works only with position turned on.')
        self.compressionResistance.installEventFilter(self)
        self.compressionResistance.setObjectName('compressionResistance')

        self.drag = broDoubleSpinBox()
        self.drag.setStatusTip('Another way to controls air density\\drag. Follow delay.')
        self.drag.installEventFilter(self)
        self.drag.setObjectName('drag')
        self.damp = broDoubleSpinBox()
        self.damp.setStatusTip('Another way to control dampening.')
        self.damp.installEventFilter(self)
        self.damp.setObjectName('damp')
        self.motionDrag = broDoubleSpinBox()
        self.motionDrag.setStatusTip('Yet another drag! :) Check nHair documentation for more info.')
        self.motionDrag.installEventFilter(self)
        self.motionDrag.setObjectName('motionDrag')

        self.nHairMass = broDoubleSpinBox()
        self.nHairMass.setStatusTip('Mass of nHair.')
        self.nHairMass.installEventFilter(self)
        self.nHairMass.setObjectName('nHairMass')
        self.nHairMass.setValue(1.0)
        self.nHairMass.setSingleStep(0.1)

        self.collideWidthOffset = broDoubleSpinBox()
        self.collideWidthOffset.setStatusTip(
            "Works with colliders only. How thick the hair is. 0 is default. 1 equals to the radius of maya's default circle object.")
        self.collideWidthOffset.installEventFilter(self)
        self.collideWidthOffset.setObjectName('collideWidthOffset')

        self.attract.setValue(0.1)
        self.attractionDamp.setValue(0.15)
        self.bendResistance.setValue(1)
        self.stretchResistance.setValue(10)
        self.compressionResistance.setValue(10)
        self.drag.setValue(0.05)
        self.damp.setValue(0)
        self.motionDrag.setValue(0)
        self.collideWidthOffset.setValue(0)

        self.attract.setSingleStep(0.1)
        self.attractionDamp.setSingleStep(0.1)
        self.drag.setSingleStep(0.1)
        self.damp.setSingleStep(0.1)
        self.motionDrag.setSingleStep(0.1)
        self.collideWidthOffset.setSingleStep(0.1)

        self.skipControls = mySpinBox()
        self.skipControls.setObjectName('skipControls')
        self.skipControls.setValue(1)
        self.skipControls.setRange(0, 99999999)
        self.skipControls.setStatusTip('First N controls will not be affected by the script.')
        self.skipControls.installEventFilter(self)

        self.skipFrames = mySpinBox()
        self.skipFrames.setObjectName('skipFrames')
        self.skipFrames.setValue(1)
        self.skipFrames.setRange(0, 99999999)
        self.skipFrames.setStatusTip('First N frames will not be keyed. Recommended to skip at least 1 frame. Simulation will still run on these frames. You can use this value for pre-roll.')
        self.skipFrames.installEventFilter(self)

        self.dontRefresh = QCheckBox("Do Not Refresh Viewport")
        self.dontRefresh.setObjectName('dontRefresh')
        self.dontRefresh.setChecked(False)
        self.dontRefresh.setStatusTip('Do not refresh Maya window during simulation.')
        self.dontRefresh.installEventFilter(self)

        self.aimRotation = QCheckBox()
        self.aimRotation.setObjectName('aimRotation')
        self.aimRotation.setChecked(True)
        self.aimRotation.setStatusTip('Match rotation by aiming. Common FK behaviour.')
        self.aimRotation.installEventFilter(self)
        self.aimRotation.setToolTip("Each object will look at it's child.")

        self.matchPositions = QCheckBox()
        self.matchPositions.setObjectName('matchPositions')
        self.matchPositions.setChecked(False)
        self.matchPositions.setStatusTip('Also match positions. Turn on for non-FK hierarchies.')
        self.matchPositions.installEventFilter(self)
        self.matchPositions.setToolTip(
            "By default the simulation only matches objects by rotation, aiming them at the simulated hair's vertices. This will enable position matching, allowing you to use this tool even with free-floating objects.")

        self.shiftDistance = broDoubleSpinBox()
        self.shiftDistance.setStatusTip(
            'Used when simulating 2 objects. How far to shift start\\end locators away from CTRL along the forward axis')
        self.shiftDistance.installEventFilter(self)
        self.shiftDistance.setObjectName('shiftDistance')
        self.shiftDistance.setValue(5)

        self.collisionMode = QCheckBox()
        self.collisionMode.setObjectName('collisionMode')
        self.collisionMode.setChecked(False)
        self.collisionMode.setStatusTip("Gives a bit different behavior for nHair. Better turn this off if you don't need collisions or forces.")
        self.collisionMode.installEventFilter(self)

        self.debugMode = QCheckBox()
        self.debugMode.setObjectName('debugMode')
        self.debugMode.setChecked(False)
        self.debugMode.setStatusTip("It will leave simulation objects in the scene, so you can debug what's going on, and test different Simulation Properties by editing them inside the Follicle and Hair objects. Please mind, that it is only recommended to be used in Debuging and Testing purposes, please make sure to save a copy of your scene, you may not be able to Undo some of it.")
        self.debugMode.setWhatsThis("It will leave simulation objects in the scene, so you can debug what's going on, and test different Simulation Properties by editing them inside the Follicle and Hair objects. Please mind, that it is only recommended to be used in Debuging and Testing purposes, please make sure to save a copy of your scene, you may not be able to Undo some of it.")
        self.debugMode.installEventFilter(self)

        self.useRotatePivot = QCheckBox()
        self.useRotatePivot.setObjectName('useRotatePivot')
        self.useRotatePivot.setChecked(False)
        self.useRotatePivot.setStatusTip("Use rotate pivot world position for matching instead of object's world translation.")
        self.useRotatePivot.setWhatsThis("Use rotate pivot world position for matching instead of object's world translation.")
        self.useRotatePivot.installEventFilter(self)

        # endregion

        # region =========== POINT TAB CONTENTS ============

        self.singleObjWeight = broDoubleSpinBox()
        self.singleObjWeight.setObjectName('singleObjWeight')
        self.singleObjWeight.setValue(0.8)
        self.singleObjWeight.setSingleStep(0.1)
        self.singleObjWeight.setStatusTip('Similar to spring stiffness.')
        self.singleObjWeight.installEventFilter(self)

        self.singleObjSmoothness = broDoubleSpinBox()
        self.singleObjSmoothness.setObjectName('singleObjSmoothness')
        self.singleObjSmoothness.setValue(3)
        self.singleObjSmoothness.setSingleStep(0.1)
        self.singleObjSmoothness.setStatusTip('Similar to spring dampening.')
        self.singleObjSmoothness.installEventFilter(self)

        #GET OVER HERE
        self.pointDrag = broDoubleSpinBox()
        self.pointDrag.setStatusTip('Particle overall drag.')
        self.pointDrag.installEventFilter(self)
        self.pointDrag.setObjectName('pointDrag')
        self.pointDrag.setValue(0.010)

        self.pointDamp = broDoubleSpinBox()
        self.pointDamp.setStatusTip('Particle overall dampening.')
        self.pointDamp.installEventFilter(self)
        self.pointDamp.setObjectName('pointDamp')
        self.pointDamp.setValue(0)

        self.pointCollide = QCheckBox()
        self.pointCollide.setStatusTip('If on, particles will collide with nCloth Passive Collider objects setup through nucleus settings of BroDynamics or connected to nucleus1 node.')
        self.pointCollide.installEventFilter(self)
        self.pointCollide.setObjectName('collide')
        self.pointCollide.setChecked(True)

        self.pointSelfCollide = QCheckBox()
        self.pointSelfCollide.setStatusTip('If on, particles will collide with each other.')
        self.pointSelfCollide.installEventFilter(self)
        self.pointSelfCollide.setObjectName('selfCollide')
        self.pointSelfCollide.setChecked(False)

        self.pointCollisionRadius = broDoubleSpinBox()
        self.pointCollisionRadius.setStatusTip('Radius of particle collision shapes.')
        self.pointCollisionRadius.installEventFilter(self)
        self.pointCollisionRadius.setObjectName('collideWidthScale')
        self.pointCollisionRadius.setValue(1.0)
        self.pointCollisionRadius.setRange(0,99999999)

        self.pointBounce = broDoubleSpinBox()
        self.pointBounce.setStatusTip('Bounciness of the particles with collision objects.')
        self.pointBounce.installEventFilter(self)
        self.pointBounce.setObjectName('bounce')
        self.pointBounce.setValue(0)

        self.pointFriction = broDoubleSpinBox()
        self.pointFriction.setStatusTip('Particle friction with collision objects')
        self.pointFriction.installEventFilter(self)
        self.pointFriction.setObjectName('friction')
        self.pointFriction.setValue(0.1)

        self.pointStickiness = broDoubleSpinBox()
        self.pointStickiness.setStatusTip('Stickiness of the particle to collision objects.')
        self.pointStickiness.installEventFilter(self)
        self.pointStickiness.setObjectName('stickiness')
        self.pointStickiness.setValue(0)

        # endregion

        # region =========== RBD TAB CONTENTS AND CTAB FILL ============

        self.rbdAddBtn = QPushButton("Add RBD")
        self.rbdAddBtn.setIcon(icon('rigidActive', type='bullet'))
        self.rbdAddBtn.setStatusTip("Add rigid body mesh to selected control object.")

        self.rbdRemoveBtn = QPushButton("Remove RBD")
        self.rbdRemoveBtn.setIcon(icon('rigidActive_remove', type='bullet'))
        self.rbdRemoveBtn.setStatusTip("Remove rigid body mesh and connection attribute from selected control objects.")

        self.rbdConnectBtn = QPushButton("Connect")
        self.rbdConnectBtn.setIcon(icon('connect', type='i16'))
        self.rbdConnectBtn.setStatusTip("Connect two objects together with broMatchTo connection. They will be matched together during snap, track and simulate procedures. Selection order does not matter.")

        self.rbdRemoveConnectionBtn = QPushButton("Remove connection")
        self.rbdRemoveConnectionBtn.setIcon(icon('disconnect', type='i16'))
        self.rbdRemoveConnectionBtn.setStatusTip("Remove broMatchTo connection from selected objects. This only deletes it from selected object.")

        self.rbdSetupConstraintBtn = QPushButton("Constraint")
        self.rbdSetupConstraintBtn.setIcon(icon('rigidConstraint', type='bullet'))
        self.rbdSetupConstraintBtn.setStatusTip("Select children and then parent object to constraint them to with RBD constraint. You should select RBD mesh objects.")

        self.rbdMatchSelectedToBtn = QPushButton("Snap selected")
        self.rbdMatchSelectedToBtn.setStatusTip("Select CTRL you want to match to RBD. Script will find connected RBD object and match control to it.")
        self.rbdMatchSelectedToBtn.setIcon(icon('simpleSnap', type='i16'))

        self.rbdMatchToSelectedBtn = QPushButton("Snap to selected")
        self.rbdMatchToSelectedBtn.setStatusTip("Select CTRL you want to match RBD to. Script will find connected RBD object and match it to control.")
        self.rbdMatchToSelectedBtn.setIcon(icon('simpleSnap', type='i16'))

        self.rbdTrackSelectedToBtn = QPushButton("Track selected to")
        self.rbdTrackSelectedToBtn.setStatusTip("It's like Snap, but automatically for current time-range.")
        self.rbdTrackSelectedToBtn.setIcon(icon('track', type='i16'))

        self.rbdTrackToSelectedBtn = QPushButton("Track to selected")
        self.rbdTrackToSelectedBtn.setStatusTip("It's like Snap, but automatically for current time-range.")
        self.rbdTrackToSelectedBtn.setIcon(icon('track', type='i16'))

        self.rbdSetKinematicBtn = QPushButton("Set RBD Kinematic")
        self.rbdSetKinematicBtn.setStatusTip("Set selected RBD Kinematic. It does not matter if you select RBD Mesh or Shape.")
        self.rbdSetKinematicBtn.setIcon(icon('rigidPassive', type='bullet'))

        self.rbdSetDynamicBtn = QPushButton("Set RBD Dynamic")
        self.rbdSetDynamicBtn.setStatusTip("Set selected RBD Kinematic. It does not matter if you select RBD Mesh or Shape.")
        self.rbdSetDynamicBtn.setIcon(icon('rigidActive', type='bullet'))

        self.rbdMatchKeyframeCB = QCheckBox("Set Keyframe on Match")

        self.rbdSelectRBDMeshBtn = QPushButton("Select RBD\\CTRL")
        self.rbdSelectRBDMeshBtn.setStatusTip("This cycles selection between CTRL and RBD. If CTRL is selected, it will select RBD. It RBD is selected, it will select CTRL.")

        self.rbdSelectRBDShapeBtn = QPushButton("Select RBD Shape")
        self.rbdSelectRBDShapeBtn.setStatusTip("This will select all RBD Shapes connected to selected controls.")

        self.rbdResetCompoundBtn = QPushButton("Reset compound shape")
        self.rbdResetCompoundBtn.setStatusTip("This will reset compound shapes on all selected RBD Meshes.")

        #region Connections

        if BroRBDCoreExists:
            self.rbdAddBtn.clicked.connect (BroRBDSimulationCore.rbdAdd)

            self.rbdRemoveBtn.clicked.connect (BroRBDSimulationCore.rbdRemove)

            self.rbdConnectBtn.clicked.connect(BroRBDSimulationCore.rbdConnect)

            self.rbdRemoveConnectionBtn.clicked.connect(BroRBDSimulationCore.rbdRemoveConnection)

            self.rbdMatchSelectedToBtn.clicked.connect(BroRBDSimulationCore.rbdMatchSelectedTo)

            self.rbdMatchToSelectedBtn.clicked.connect((BroRBDSimulationCore.rbdMatchToSelected))

            self.rbdTrackSelectedToBtn.clicked.connect(lambda: BroRBDSimulationCore.trackObjectsToConnection(cmds.ls(sl=1, l=1), reverse=False, dontRefresh=self.dontRefresh.isChecked()))

            self.rbdTrackToSelectedBtn.clicked.connect(lambda: BroRBDSimulationCore.trackObjectsToConnection(cmds.ls(sl=1, l=1), reverse=True, dontRefresh=self.dontRefresh.isChecked()))

            self.rbdSetKinematicBtn.clicked.connect(BroRBDSimulationCore.rbdSetKinematic)

            self.rbdSetDynamicBtn.clicked.connect(BroRBDSimulationCore.rbdSetDynamic)

            self.rbdSetupConstraintBtn.clicked.connect(BroRBDSimulationCore.rbdSetupConstraint)

            self.rbdSelectRBDMeshBtn.clicked.connect(BroRBDSimulationCore.rbdSelectRBDMesh)

            self.rbdSelectRBDShapeBtn.clicked.connect(BroRBDSimulationCore.rbdSelectRBDShape)

            self.rbdResetCompoundBtn.clicked.connect(BroRBDSimulationCore.rbdResetCompound)

        #endregion

        row = 0
        column = 0
        for btn in [self.rbdAddBtn, self.rbdRemoveBtn, self.rbdConnectBtn, self.rbdRemoveConnectionBtn, self.rbdSetupConstraintBtn, self.rbdResetCompoundBtn]:
            btn.installEventFilter(self)
            self.rbdSetupCTab.addWidget(btn, column, row)
            row += 1
            if row == 2:
                row = 0
                column += 1

        row = 0
        column = 0
        for btn in [self.rbdMatchSelectedToBtn, self.rbdMatchToSelectedBtn, self.rbdTrackSelectedToBtn, self.rbdTrackToSelectedBtn,
                    self.rbdSetKinematicBtn, self.rbdSetDynamicBtn, self.rbdSelectRBDMeshBtn, self.rbdSelectRBDShapeBtn]:
            btn.installEventFilter(self)
            self.rbdCTab.addWidget(btn, column, row)
            row += 1
            if row == 2:
                row = 0
                column += 1

        # endregion

        # region ========== Collapse tabs fill ==========
        self.otherFormLayout.addRow(("Skip First N Controls"), self.skipControls)
        self.otherFormLayout.addRow(("Skip First N Frames"), self.skipFrames)

        self.aligmentFormLayout.addRow(("Front Axis"), self.frontGrp)
        self.aligmentFormLayout.addRow(("Up Axis"), self.upGrp)
        self.aligmentFormLayout.addRow(("&Aim Rotation"), self.aimRotation)
        self.aligmentFormLayout.addRow(("&Match Positions"), self.matchPositions)
        self.aligmentFormLayout.addRow(("&Shift Distance"), self.shiftDistance)

        self.simulationFormLayout.addRow(("&Attract"), self.attract)
        self.simulationFormLayout.addRow(("&Attraction damp"), self.attractionDamp)
        self.simulationFormLayout.addRow(("&Bend Resistance"), self.bendResistance)
        self.simulationFormLayout.addRow(("&Stretch Resistance"), self.stretchResistance)
        self.simulationFormLayout.addRow(("&Compression Resistance"), self.compressionResistance)
        self.simulationFormLayout.addRow(("&Drag"), self.drag)
        self.simulationFormLayout.addRow(("&Damp"), self.damp)
        self.simulationFormLayout.addRow(("&Motion Drag"), self.motionDrag)
        self.simulationFormLayout.addRow(("&Mass"), self.nHairMass)

        self.simulationFormLayout.addRow(("&Collide Width Offset"), self.collideWidthOffset)
        self.simulationFormLayout.addRow(("&Use nucleus (Collision mode)"), self.collisionMode)
        self.simulationFormLayout.addRow(("&Use Rotate Pivot"), self.useRotatePivot)
        self.simulationFormLayout.addRow(("&Debug Mode"), self.debugMode)

        self.singleObjSettingsFormLayout.addRow(("&Goal Weight"), self.singleObjWeight)
        self.singleObjSettingsFormLayout.addRow(("&Goal Smoothness"), self.singleObjSmoothness)
        self.singleObjSettingsFormLayout.addRow(("&Drag"), self.pointDrag)
        self.singleObjSettingsFormLayout.addRow(("&Damp"), self.pointDamp)
        self.singleObjSettingsFormLayout.addRow(("&Collide"), self.pointCollide)
        self.singleObjSettingsFormLayout.addRow(("&Self Collide"), self.pointSelfCollide)
        self.singleObjSettingsFormLayout.addRow(("&Collision radius"), self.pointCollisionRadius)
        self.singleObjSettingsFormLayout.addRow(("&Bounce"), self.pointBounce)
        self.singleObjSettingsFormLayout.addRow(("&Friction"), self.pointFriction)
        self.singleObjSettingsFormLayout.addRow(("&Stickiness"), self.pointStickiness)
        # endregion

        # region Button Layout

        self.buttonLayout.addWidget(imageLabel)
        self.buttonLayout.addWidget(self.simButton)
        self.buttonLayout.addWidget(self.dontRefresh)
        self.buttonLayout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.dummyLabel = QLabel(" ")
        self.buttonLayout.addWidget(self.dummyLabel)
        self.buttonLayout.setSpacing(10)

        # endregion

        # region MenuBar
        menuBar = QMenuBar()
        presetsMenu = menuBar.addMenu(("&Presets"))
        saveConfigAction = QAction(("&Save Settings"), self)
        saveConfigAction.triggered.connect(self.saveConfig)
        saveConfigAction.setIcon(icon('save'))
        presetsMenu.addAction(saveConfigAction)

        loadConfigAction = QAction(("&Load Settings"), self)
        loadConfigAction.triggered.connect(self.readConfig)
        loadConfigAction.setIcon(icon('open'))
        presetsMenu.addAction(loadConfigAction)

        presetsMenu.addSeparator()

        loadDefaultsAction = QAction(("&Load Defaults"), self)
        loadDefaultsAction.triggered.connect(self.loadDefaults)
        presetsMenu.addAction(loadDefaultsAction)

        toolsMenu = menuBar.addMenu(("&Tools"))
        nucleusAction = QAction(("Colliders and Forces"), self)
        nucleusAction.triggered.connect(self.showNucleus)
        nucleusAction.setIcon(icon('nucleus'))
        toolsMenu.addAction(nucleusAction)

        batchAction = QAction(("&Batch Simulation"), self)
        batchAction.triggered.connect(self.showBatch)
        batchAction.setIcon(icon('simulate_all'))
        toolsMenu.addAction(batchAction)

        unlockAttrsAction = QAction(("&Unlock T&R Attributes"), self)
        unlockAttrsAction.triggered.connect(BroSimulationCore.unlockAttributes)
        unlockAttrsAction.setIcon(icon('script'))
        unlockAttrsAction.setStatusTip("This script will unlock translation and rotaion attributes on selected objects.")
        toolsMenu.addAction(unlockAttrsAction)

        helpMenu = menuBar.addMenu(("&Help"))

        DocumentationAction = QAction(("&Documentation"), self)
        DocumentationAction.triggered.connect(lambda: self.openWebUrl('http://www.nixes.ru/BroTools/Documentation/BroDynamics/'))
        DocumentationAction.setIcon(icon('url'))
        helpMenu.addAction(DocumentationAction)

        FacebookAction = QAction(("&Facebook page"), self)
        FacebookAction.triggered.connect(lambda: self.openWebUrl('https://www.facebook.com/BroDynamics'))
        FacebookAction.setIcon(icon('url'))
        helpMenu.addAction(FacebookAction)

        BugReportAction = QAction(("&Bug report"), self)
        BugReportAction.triggered.connect(lambda: self.openWebUrl('https://docs.google.com/forms/d/e/1FAIpQLSeEM2FuToBPuPmv7gtY4pi4cuuXmM3nHM9BrIeLeP9eIZ5oTA/viewform?entry.1787609625&entry.2076223753={0}&entry.1611584781={1}&entry.1718381786&entry.791898987&entry.1538779163'.format(getOS(), getMayaVersion())))
        BugReportAction.setIcon(icon('url'))
        helpMenu.addAction(BugReportAction)

        UsageSurveyAction = QAction(("&Usage survey"), self)
        UsageSurveyAction.triggered.connect(lambda: self.openWebUrl('https://docs.google.com/forms/d/e/1FAIpQLSfC4HYgmJ7x-9A1vH1ShYGEpOv0c-MhQFMDU6N49Ktgzy2q3Q/viewform?entry.1440558169&entry.1317559609&entry.1131457850&entry.952373254&entry.2140665439&entry.891808480={0}&entry.1835236540={1}&entry.1660953863&entry.1285615578'.format(getMayaVersion(), getOS())))
        UsageSurveyAction.setIcon(icon('url'))
        helpMenu.addAction(UsageSurveyAction)

        aboutAction = QAction(("&About"), self)
        aboutAction.triggered.connect(self.showAbout)
        aboutAction.setIcon(icon('question'))
        helpMenu.addAction(aboutAction)

        self.setMenuBar(menuBar)
        # endregion

        # region statusBar

        self.statusBar = QStatusBar()

        self.setStatusBar(self.statusBar)

        # endregion

        self.mainLayout.addWidget(self.textField)
        self.resize(100, 100)
        self.lockSize()


        if firstLaunch:
            self.showWelcome()

        self.simulationCTab.switchState()

    def openWebUrl(self, url=None):
        if url != None:
            try:
                webbrowser.open(url)
            except Exception as e:
                log.log('warning', 'Tried to open web-link, but experienced an error:', e)
        else:
            log.log("Tried to open web-link, but no link provided.")

    def createScriptJobs(self):
        cmds.scriptJob(event=['NewSceneOpened',
                              'BroTools.BroDynamics.BroDynamicsUI.BroDynamicsWindow.BroBatchWindow.restoreFromNode()'],
                       parent=self.objectName())
        cmds.scriptJob(event=['PostSceneRead',
                              'BroTools.BroDynamics.BroDynamicsUI.BroDynamicsWindow.BroBatchWindow.restoreFromNode()'],
                       parent=self.objectName())

        cmds.scriptJob(event=['Undo',
                              'BroTools.BroDynamics.BroDynamicsUI.BroDynamicsWindow.BroBatchWindow.restoreFromNode(silent=True)'],
                       parent=self.objectName())

    def unlockSize(self):
        self.setMaximumSize(10000, 10000)

    def lockSize(self):
        self.initHeight = self.sizeHint().height()
        self.initWidth = self.sizeHint().width()
        self.setMaximumHeight(self.initHeight)
        self.setMaximumWidth(self.initWidth)

    def hideSettings(self):
        log.log(">", "Hiding Form Layout")
        lostHeight = self.formWrapperWidget.sizeHint().height()
        previousWidth = self.sizeHint().width()
        previousHeight = self.sizeHint().height()
        newHeight = previousHeight - lostHeight
        #print lostHeight, previousHeight, previousWidth, newHeight
        self.formWrapperWidget.hide()
        self.setMaximumHeight(newHeight)

    def loadCss(self):
        try:
            with open(broDynamicsCss) as styleSheetFile:
                self.setStyleSheet(styleSheetFile.read())

            log.log('', broDynamicsCss)
        except:
            log.inViewLog('#FF0000', 'Unable to load CSS style for UI!')

    def switchTabReaction(self):
        itemType = getTabType(self.tabWidget.currentIndex())
        if itemType == 'Point':
            self.simButton.setIcon(QPixmap(self.simulateIcon))

        elif itemType == 'Chain':
            self.simButton.setIcon(QPixmap(self.simulateChainIcon))

        else:
            self.simButton.setIcon(QPixmap(self.simulateRBDIcon))


        if makeJokes:
            global hmm
            global jokeRate
            hmm += 1
            if hmm >= jokeRate:
                makeJoke()
                hmm = 0

    def startSimulation(self):
            selection = cmds.ls(sl=True)  # store selection
            self.oldMessage1 = self.statusBar.currentMessage()
            self.statusBar.showMessage("Simulation in progress", 240000)
            itemType = getTabType(self.tabWidget.currentIndex())
            if itemType == 'Chain':
                fx = 0
                fy = 0
                fz = 0
                ux = 0
                uy = 0
                uz = 0

                if self.frontX.isChecked():
                    fx = 1
                if self.frontY.isChecked():
                    fy = 1
                if self.frontZ.isChecked():
                    fz = 1
                if self.upX.isChecked():
                    ux = 1
                if self.upY.isChecked():
                    uy = 1
                if self.upZ.isChecked():
                    uz = 1

                if self.frontR.isChecked():
                    fx *= -1
                    fy *= -1
                    fz *= -1

                if self.upR.isChecked():
                    ux *= -1
                    uy *= -1
                    uz *= -1

                    #print "VAL", self.attractionDamp.value(), self.bendResistance.value(), self.stretchResistance.value(), self.compressionResistance, self.drag.value(), self.damp.value(), self.motionDrag.value()

                    # objects, axis = [1,0,0], up = [0,1,0], skipFrames = 1, attract = 0.1, attractionDamp = 0, bendResistance = 1, stretchResistance = 10, compressionResistance = 10, drag = 0.05, damp = 0, motionDrag = 0

                try:
                    cmds.undoInfo(ock=True)
                    BroSimulationCore.simulateNHair(cmds.ls(sl=True), axis=[fx, fy, fz], up=[ux, uy, uz],
                                                    matchPositions=self.matchPositions.isChecked(),
                                                    aimRotation=self.aimRotation.isChecked(),
                                                    skipFrames=self.skipFrames.value(),
                                                    skipControls=self.skipControls.value(),
                                                    attract=self.attract.value(),
                                                    attractionDamp=self.attractionDamp.value(),
                                                    bendResistance=self.bendResistance.value(),
                                                    stretchResistance=self.stretchResistance.value(),
                                                    compressionResistance=self.compressionResistance.value(),
                                                    drag=self.drag.value(), damp=self.damp.value(),
                                                    motionDrag=self.motionDrag.value(),
                                                    mass=self.nHairMass.value(),
                                                    collideWidthOffset=self.collideWidthOffset.value(),
                                                    dontRefresh=self.dontRefresh.isChecked(),
                                                    reversed=self.frontR.isChecked(),
                                                    shiftDistance=self.shiftDistance.value(),
                                                    colliders=self.BroNucleusWindow.collidersList.getAllItems(),
                                                    forces=BroDynamicsWindow.BroNucleusWindow.forcesList.getAllItems(),
                                                    collisionMode=self.collisionMode.isChecked(),
                                                    debugMode=self.debugMode.isChecked(),
                                                    useRotatePivot=self.useRotatePivot.isChecked())
                    cmds.undoInfo(cck=True)
                    self.statusBar.showMessage(self.oldMessage, 0)
                except Exception as e:
                    cmds.undoInfo(cck=True)
                    self.statusBar.showMessage(self.oldMessage, 0)
                    log.log('warning', 'Tried to run startSimulation, Chain mode, experienced an error:', e)

            elif itemType == 'Point':
                try:
                    cmds.undoInfo(ock=True)
                    BroSimulationCore.simulateNParticles(selection, 1, self.singleObjWeight.value(),
                                                         self.singleObjSmoothness.value(), self.dontRefresh.isChecked(),
                                                         collide = self.pointCollide.isChecked(), selfCollide = self.pointSelfCollide.isChecked(), collideWidthScale=self.pointCollisionRadius.value(),
                                                         bounce=self.pointBounce.value(), friction=self.pointFriction.value(), stickiness=self.pointStickiness.value(),
                                                         drag=self.pointDrag.value(), damp=self.pointDamp.value())
                    cmds.undoInfo(cck=True)
                    self.statusBar.showMessage(self.oldMessage, 0)
                except Exception as e:
                    cmds.undoInfo(cck=True)
                    self.statusBar.showMessage(self.oldMessage, 0)
                    log.log('warning', 'Tried to run startSimulation, Point mode, experienced an error:', e)

            elif itemType == 'RBD':
                log.log('>', 'Item type,', itemType)
                if BroRBDCoreExists:
                    BroRBDSimulationCore.simulateRBDControls(cmds.ls(sl=1, l=1), dontRefresh=self.dontRefresh.isChecked())
                else:
                    log.inViewLog("#FF0000", "RBD Module is missing. Objects", cmds.ls(sl=1, l=1), "won't be simulated. Get BroDynamics RBD Module for it to work, or chech if it is installed correctly.")

            self.statusBar.showMessage(self.oldMessage, 0)
            cmds.select(selection, r=True)

    def showAbout(self):
        log.log('^', 'Show About window')
        self.BroAboutWindow.show()

    def showNucleus(self):
        log.log('^', 'Show Nucleus window')
        self.BroNucleusWindow.show()

    def showBatch(self):
        log.log('^', 'Show Batch window')

        self.BroBatchWindow.restoreFromNode()
        self.BroBatchWindow.show()

    def showWelcome(self):
        self.broWelcomeWindowName = 'broDynamics_Welcome'
        if cmds.window(self.broWelcomeWindowName, ex=True):
            cmds.deleteUI(self.broWelcomeWindowName, wnd=True)
        self.BroWelcomeWindow = WelcomeWindow(rootWidget=self)
        self.BroWelcomeWindow.setObjectName(self.broWelcomeWindowName)

        self.BroWelcomeWindow.show()

    @utils.try_except
    def readConfig(self):
        cfgfilePath = cmds.fileDialog2(fileMode=1, cap="Save config", ff='*.ini')[0]
        config = dataio.readConfig(cfgfilePath)
        try:
            sections = ['AllSettings']
            for section in sections:
                for item in config.items(section):
                    #print "Looking for:", item[0]
                    element = self.findChild(QCheckBox, item[0])
                    if element != None:
                        element.setChecked(config.getboolean(section, item[0]))

                    element = self.findChild(QDoubleSpinBox, item[0])
                    if element != None:
                        element.setValue(config.getfloat(section, item[0]))

                    element = self.findChild(QSpinBox, item[0])
                    if element != None:
                        element.setValue(config.getint(section, item[0]))

                    element = self.findChild(QRadioButton, item[0])
                    if element != None:
                        element.setChecked(config.getboolean(section, item[0]))
            log.inViewLog("#20FF20", "Config loaded")
        except Exception as e:
            log.inViewLog("#FF2020", "Error:", e)

    @utils.try_except
    def saveConfig(self):
        log.log("///", "Saving config")
        defaultConfig = dataio.readConfig(broDynamicsDefaultsIni)
        config = dataio.newConfig()
        try:
            sections = ['AllSettings']
            for section in sections:
                log.log("//", "Section: ", section)
                config.add_section(section)
                for item in defaultConfig.items(section):

                    #print "Looking for:", item[0]
                    element = self.findChild(QCheckBox, item[0])
                    if element != None:
                        config.set(section, item[0], element.isChecked())
                        log.log("//", "Saving item: ", item[0], element.isChecked())

                    element = self.findChild(QDoubleSpinBox, item[0])
                    if element != None:
                        config.set(section, item[0], element.value())
                        log.log("//", "Saving item: ", item[0], element.value())

                    element = self.findChild(QSpinBox, item[0])
                    if element != None:
                        config.set(section, item[0], element.value())
                        log.log("//", "Saving item: ", item[0], element.value())

                    element = self.findChild(QRadioButton, item[0])
                    if element != None:
                        config.set(section, item[0], element.isChecked())
                        log.log("//", "Saving item: ", item[0], element.isChecked())

            cfgfilePath = cmds.fileDialog2(fileMode=0, cap="Save config", ff='*.ini')[0]
            cfgfile = open(cfgfilePath, 'w')
            config.write(cfgfile)
            cfgfile.close()

            log.inViewLog("#20FF20", "Config saved: " + str(cfgfilePath))
        except Exception as e:
            log.inViewLog("#FF2020", "Error:", e)

    @utils.try_except
    def loadDefaults(self):
        config = dataio.readConfig(broDynamicsDefaultsIni)

        sections = ['AllSettings']
        for section in sections:
            for item in config.items(section):
                #print "Looking for:", item[0]
                element = self.findChild(QCheckBox, item[0])
                if element != None:
                    element.setChecked(config.getboolean(section, item[0]))

                element = self.findChild(QDoubleSpinBox, item[0])
                if element != None:
                    element.setValue(config.getfloat(section, item[0]))

                element = self.findChild(QSpinBox, item[0])
                if element != None:
                    element.setValue(config.getint(section, item[0]))

                element = self.findChild(QRadioButton, item[0])
                if element != None:
                    element.setChecked(config.getboolean(section, item[0]))

    def initChildWindows(self):
        self.batchWindowName = 'broDynamics_Batch'
        if cmds.window(self.batchWindowName, ex=True):
            cmds.deleteUI(self.batchWindowName, wnd=True)
        self.BroBatchWindow = BatchWindow(rootWidget=self)

        self.aboutWindowName = 'broDynamics_About'
        if cmds.window(self.aboutWindowName, ex=True):
            cmds.deleteUI(self.aboutWindowName, wnd=True)
        self.BroAboutWindow = AboutWindow(rootWidget=self)
        self.BroAboutWindow.setObjectName(self.aboutWindowName)

        self.nucleusWindowName = 'broDynamics_Nucleus'
        if cmds.window(self.nucleusWindowName, ex=True):
            cmds.deleteUI(self.nucleusWindowName, wnd=True)
        self.BroNucleusWindow = NucleusWindow(rootWidget=self)
        self.BroNucleusWindow.setObjectName(self.nucleusWindowName)

    def setDockableParameters(self, dockable=None, floating=None, area=None, allowedArea=None, width=None, height=None, x=None, y=None, *args, **kwargs):
        '''
        Set the dockable parameters.

        :Parameters:
            dockable (bool)
                Specify if the window is dockable (default=False)
            floating (bool)
                Should the window be floating or docked (default=True)
            area (string)
                Default area to dock into (default='left')
                Options: 'top', 'left', 'right', 'bottom'
            allowedArea (string)
                Allowed dock areas (default='all')
                Options: 'top', 'left', 'right', 'bottom', 'all'
            width (int)
                Width of the window
            height (int)
                Height of the window
            x (int)
                left edge of the window
            y (int)
                top edge of the window

        :See: show(), hide(), and setVisible()
        '''
        if (dockable == True) or (dockable == None and self.isDockable()): # == Handle docked window ==
            # Conversion parameters (used below)
            dockAreaStrMap = {
                'left'   : Qt.LeftDockWidgetArea,
                'right'  : Qt.RightDockWidgetArea,
                'top'    : Qt.TopDockWidgetArea,
                'bottom' : Qt.BottomDockWidgetArea,
                'all'    : Qt.AllDockWidgetAreas,
                'none'   : Qt.NoDockWidgetArea,   # Note: Not currently supported in maya dockControl command
            }

            # Create dockControl (QDockWidget) if needed
            if dockable == True and not self.isDockable():
                # Retrieve original position and size
                # Position
                if x == None:
                    x = self.x()
                if y == None:
                    y = self.y()
                # Size
                unininitializedSize = QSize(640,480)  # Hardcode: (640,480) is the default size for a QWidget
                if self.size() == unininitializedSize:
                    # Get size from widget sizeHint if size not yet initialized (before the first show())
                    widgetSizeHint = self.sizeHint()
                else:
                    widgetSizeHint = self.size() # use the current size of the widget
                if width == None:
                    width = widgetSizeHint.width()
                if height == None:
                    height = widgetSizeHint.height()

                # Create the QDockWidget
                dockWidget = MayaQDockWidget()
                dockWidget.setWindowTitle(self.windowTitle())
                dockWidget.setWidget(self)

                # By default, when making dockable, make it floating
                #   This addresses an issue on Windows with the window decorators
                #   not showing up.  Setting this here will cause setFloating() to be called below.
                if floating == None:
                    floating = True

                # Hook up signals
                dockWidget.topLevelChanged.connect(self.floatingChanged)
                dockWidget.closeEventTriggered.connect(self.dockCloseEventTriggered)
            else:
                if floating == True:
                    # Retrieve original position (if floating)
                    pos = self.parent().mapToGlobal( QPoint(0,0) )
                    if x == None:
                        x = pos.x()
                    if y == None:
                        y = pos.y()

                # Retrieve original size
                if width == None:
                    width = self.width()
                if height == None:
                    height = self.height()

            # Get dock widget identifier
            dockWidget = self.parent()

            # Update dock values
            if area        != None:
                areaValue = dockAreaStrMap.get(area, Qt.LeftDockWidgetArea)
                dockWidget.setArea(areaValue)
            if allowedArea != None:
                areaValue = dockAreaStrMap.get(allowedArea, Qt.AllDockWidgetAreas)
                dockWidget.setAllowedAreas(areaValue)
            if floating    != None:
                dockWidget.setFloating(floating)

            # Position window
            if dockWidget.isFloating() and ((x != None) or (y != None)):
                dockPos = dockWidget.mapToGlobal( QPoint(0,0) )
                if x == None:
                    x = dockPos.x()
                if y == None:
                    y = dockPos.y()
                dockWidget.move(x,y)
            if (width != None) or (height != None):
                if width == None:
                    width = self.width()
                if height == None:
                    height = self.height()
                # Perform first resize on dock, determine delta with widget, and resize with that adjustment
                # Result: Keeps the content widget at the same size whether under the QDockWidget or a standalone window
                dockWidget.resize(width, height) # Size once to know the difference in the dockWidget to the targetSize
                dockWidgetSize = dockWidget.size() + QSize(width,height)-self.size() # find the delta and add it to the current dock size
                # Perform the final resize (call MayaQDockWidget.resize() which also sets the 'savedSize' property used for sizing when docking to the Maya MainWindow)
                dockWidget.resize(dockWidgetSize)

        else:  # == Handle Standalone Window ==
            # Make standalone as needed
            if dockable == False and self.isDockable():
                # Retrieve original position and size
                dockPos = self.parent().mapToGlobal( QPoint(0,0) )
                if x == None:
                    x = dockPos.x()
                if y == None:
                    y = dockPos.y()
                if width == None:
                    width = self.width()
                if height == None:
                    height = self.height()
                # Turn into a standalone window and reposition
                currentVisibility = self.isVisible()
                self._makeMayaStandaloneWindow() # Set the parent back to Maya and remove the parent dock widget
                self.setVisible(currentVisibility)

            # Handle position and sizing
            if (width != None) or (height != None):
                if width == None:
                    width = self.width()
                if height == None:
                    height = self.height()
                self.resize(width, height)
            if (x != None) or (y != None):
                if x == None:
                    x = self.x()
                if y == None:
                    y = self.y()
                self.move(x,y)

    def eventFilter(self, obj, event):
        '''Connect signals on mouse over'''

        if event.type() == QEvent.Enter:
            self.oldMessage = self.statusBar.currentMessage()
            self.statusBar.showMessage(obj.statusTip(), 0)
        elif event.type() == QEvent.Leave:
            self.statusBar.showMessage(self.oldMessage, 0)
            pass
        if event != None:
            event.accept()
        return False

    def dockCloseEventTriggered(self):
        log.log("/", "BroDynamics window close button pressed. Closing window and deleting window and child windows from memory.")
        self.close()

    def closeEvent(self, evt):
        '''Hide the QDockWidget and trigger the closeEventTriggered signal
        '''
        # Handle the standard closeEvent()
        #super(MayaQDockWidget, self).closeEvent(evt)

        if evt.isAccepted():
            # Force visibility to False
            self.BroBatchWindow.deleteLater()
            self.BroNucleusWindow.deleteLater()
            self.BroAboutWindow.deleteLater()
            if firstLaunch:
                self.BroWelcomeWindow.deleteLater()
            self.deleteLater()
            self.parentWidget().deleteLater()




# endregion

def joke():
    '''
    Careful now...
    '''
    try:
        jsonData = urllib2.urlopen('http://api.icndb.com/jokes/random?escape=javascript').read()
        data = json.loads(jsonData)

        print "\n", data['value']['joke']


    except Exception as e:
        pass

def makeJoke():
    #jokeThread = threading.Thread(target=joke)
    #jokeThread.start()
    joke()


def getMayaWindow():
    pointer = omui.MQtUtil.mainWindow()
    return shiboken.wrapInstance(long(pointer), QWidget)
@utils.try_except
def initUI():
    log.log('^', 'Initializing BroDynamics UI')
    try:
        global firstLaunch
        try:
            settingsConfig = dataio.readConfig(broDynamicsSettingsIni)
            firstLaunch = settingsConfig.getboolean('Settings', 'firstLaunch')
            settingsConfig.set('Settings', 'firstLaunch', False)
        except Exception as e:
            log.log('', "\nERROR OH MY GOD, I CANT READ settings.ini FILE!", e, '\n')
        #print firstLaunch

        windowName = "broDynamics_Window"

        global BroDynamicsWindow

        if cmds.window(windowName, ex=True):
            cmds.deleteUI(windowName, wnd=True)

        BroDynamicsWindow = DockableWindow()
        BroDynamicsWindow.setObjectName(windowName)
        BroDynamicsWindow.statusBar.showMessage("Current version: " + changeLog.currentVersion, 0)

        BroDynamicsWindow.show(dockable=True, area='left', floating=True, allowedArea='left, right')

        def getVersion():
            try:
                connected = cmds.about(cnt=True)
            except:
                connected = True

            if connected:
                try:
                    text = ''
                    data = changeLog.getVersion()
                    stat = ""
                    if data != changeLog.currentVersion and data != 'Could not check latest version':
                        stat = "New version available: " + str(data)
                    text = "Your version: {0}; Latest version: {1};".format(changeLog.currentVersion, str(data))
                    BroDynamicsWindow.BroAboutWindow.latestVersion.setText(text)
                    BroDynamicsWindow.statusBar.showMessage("Current version: {0}. {1}".format(changeLog.currentVersion, stat), 0)
                except Exception as e:
                    log.log("X", "Unable to connect to get latest version.\n", e, '\n')


        settingsConfig = dataio.readConfig(broDynamicsSettingsIni)
        checkForNewVersions = settingsConfig.getboolean('Settings', 'checkForNewVersions')
        if checkForNewVersions:
            download_thread = threading.Thread(target=getVersion)
            download_thread.start()

        else:
            BroDynamicsWindow.statusBar.showMessage("Current version: {0}. Version check disabled.".format(
                changeLog.currentVersion), 0)

        log.log (":) ", "BroDynamics UI Loaded!")
    except Exception as e:
        print "Traceback:", str(traceback.print_exc())
        log.log ("!!!", "BroDynamics UI was not Loaded! :(", e)

