#!/usr/bin/env python
# -*- coding: utf-8 -*-
# modTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写


import os, random, maya.OpenMayaUI as omui, maya.cmds as cmds, xgenm as xg
from utils import jsonHelper, publish
from PySide2 import QtUiTools, QtWidgets, QtCore, QtGui
from shiboken2 import wrapInstance

class XGenToolsUI(QtWidgets.QMainWindow):

    def __init__(self):
        super(XGenToolsUI, self).__init__()
        self.init_ui()

    def init_ui(self):
        scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        scriptsPath = scriptsPath.replace('\\', '/')
        scriptsPath = scriptsPath.replace('sources', 'ui')
        f = QtCore.QFile('%s/xgenTools.ui' % scriptsPath)
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader().load(f)
        self.ui = loader
        f.close()
        self.setCentralWidget(self.ui)
        self.ui.density_spBox.valueChanged.connect(lambda : self.spinBoxChange(self.ui.density_slider, self.ui.density_spBox))
        self.ui.percent_spBox.valueChanged.connect(lambda : self.spinBoxChange(self.ui.percent_slider, self.ui.percent_spBox))
        self.ui.density_slider.valueChanged.connect(lambda : self.sliderChange(self.ui.density_slider, self.ui.density_spBox))
        self.ui.percent_slider.valueChanged.connect(lambda : self.sliderChange(self.ui.percent_slider, self.ui.percent_spBox))
        self.ui.density_bttn.clicked.connect(lambda : self.apply(self.ui.density_spBox, 'density', 'RandomGenerator'))
        self.ui.percent_bttn.clicked.connect(lambda : self.apply(self.ui.percent_spBox, 'percent', 'GLRenderer'))
        self.ui.XGen_bttnGrp.buttonToggled.connect(self.getDataList)
        self.ui.XGen_treeWgt.itemSelectionChanged.connect(self.currentSelecetedItems)
        self.ui.abcExport_bttn.clicked.connect(self.exportABC)
        self.ui.abcImport_bttn.clicked.connect(self.importABC)
        self.ui.abcPath_line.installEventFilter(self)

    def projectSetting(self):
        scriptsPath = os.path.split(os.path.realpath(__file__))[0]
        scriptsPath = scriptsPath.replace('\\', '/')
        scriptsPath = scriptsPath.replace('sources', 'config')
        data = jsonHelper.readDictFromFile('%s/projectSetting.json' % scriptsPath)
        return data

    def sliderChange(self, slider, spBox):
        value = slider.value()
        spBox.setValue(float(value / 100.0))

    def spinBoxChange(self, slider, spBox):
        value = spBox.value()
        slider.setValue(value * 100)

    def apply(self, spinBox, type, object):
        value = str(spinBox.value())
        for i in cmds.ls(sl=1):
            coll = xg.palette(str(i))
            xg.setAttr(type, value, coll, str(i), object)

        import xgenm.xgGlobal as xgg
        de = xgg.DescriptionEditor
        de.refresh('Full')

    def getAbcPath(self):
        abcRootPath = cmds.fileDialog2(fileMode=3, dialogStyle=2)[0]
        self.ui.abcPath_line.setText(str(abcRootPath))
        for root, dirs, files in os.walk(abcRootPath):
            for name in files:
                if name.endswith('_CV.abc'):
                    inderim_list = name.split('_', 3)
                    if len(inderim_list) == 4:
                        inderim_name = '%s_%s_%s:%s' % (inderim_list[0], inderim_list[1], inderim_list[2], inderim_list[3])
                        self.ui.abc_listWgt.addItem(inderim_name.split('.')[0])
                    elif len(inderim_list) == 3:
                        self.ui.abc_listWgt.addItem(name.split('.')[0])
                    else:
                        cmds.warning('Please check your alembic name!!!')

    def getDataList(self):
        suffix = self.ui.XGen_bttnGrp.checkedButton().text()
        self.ui.XGen_treeWgt.clear()
        if suffix == 'CV':
            self.ui.abcExport_bttn.setEnabled(True)
            self.ui.abcImport_bttn.setEnabled(False)
            data_list = cmds.ls(['*:*_HairCV_GRP', '*_HairCV_GRP'], type='transform')
        elif suffix == 'Scalp':
            self.ui.abcExport_bttn.setEnabled(True)
            self.ui.abcImport_bttn.setEnabled(False)
            data_list = cmds.ls(['*:*_Scalp_GRP', '*_Scalp_GRP'], type='transform')
        elif suffix == 'XGen':
            self.ui.abcExport_bttn.setEnabled(False)
            self.ui.abcImport_bttn.setEnabled(True)
            data_list = []
            interim_list = cmds.ls(type='xgmPalette')
            for i in interim_list:
                if i.endswith('_Coll'):
                    data_list.append(i)

        if data_list == []:
            cmds.warning('Can not find %s group!!!' % suffix)
            return
        else:
            for i in data_list:
                item = QtWidgets.QTreeWidgetItem()
                item.setText(0, i)
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                self.ui.XGen_treeWgt.addTopLevelItem(item)
                children = cmds.listRelatives(i, children=True)
                if children is not None:
                    for child in children:
                        child_item = QtWidgets.QTreeWidgetItem(item)
                        child_item.setText(0, child)

            return

    def currentSelecetedItems(self):
        currentSelected_items = self.ui.XGen_treeWgt.selectedItems()
        cmds.select(clear=True)
        for i in currentSelected_items:
            cmds.select('%s' % i.text(0), add=True)

    def exportABC(self):
        minTime = cmds.playbackOptions(query=True, minTime=True) - 5
        maxTime = cmds.playbackOptions(query=True, maxTime=True) + 5
        abcRoot_dir = self.ui.abcPath_line.text()
        currentSelected_items = self.ui.XGen_treeWgt.selectedItems()
        if currentSelected_items is None:
            cmds.warning('Please select items!!!')
            return
        else:
            for i in currentSelected_items:
                abcData_name = i.text(0)
                if abcData_name.find(':') != -1:
                    abcData_name = abcData_name.replace(':', '_')
                abcData_path = '%s/%s.abc' % (abcRoot_dir, abcData_name)
                cmds.select(i.text(0))
                longName = cmds.ls(selection=True, long=True)
                jobArg = '-frameRange %s %s -step 0.5 -uvWrite -worldSpace -writeVisibility -dataFormat ogawa -root %s -file %s' % (minTime, maxTime, longName[0], abcData_path)
                cmds.AbcExport(jobArg=jobArg)

            return

    def importABC(self):
        currentSelected_listItems = self.ui.abc_listWgt.selectedItems()
        currentSelected_treeItems = self.ui.XGen_treeWgt.selectedItems()
        abcData_dir = self.ui.abcPath_line.text()
        if currentSelected_listItems is None:
            cmds.warning('Please select alembic!!!')
            return
        else:
            for listItem in currentSelected_listItems:
                interim_desc = str(listItem.text().replace('_CV', '_Desc'))
                if listItem.text().find(':') != -1:
                    abcData_path = str('%s/%s.abc' % (abcData_dir, listItem.text().replace(':', '_')))
                    interim_name = interim_desc.split(':')[(-1)]
                else:
                    abcData_path = str('%s/%s.abc' % (abcData_dir, listItem.text()))
                    interim_name = interim_desc
                if currentSelected_treeItems == []:
                    if cmds.objExists(interim_desc):
                        interim_coll = xg.palette(interim_desc)
                        xg.setAttr('liveMode', '0', interim_coll, interim_desc, 'SplinePrimitive')
                        xg.setAttr('useCache', '1', interim_coll, interim_desc, 'SplinePrimitive')
                        xg.setAttr('cacheFileName', abcData_path, interim_coll, interim_desc, 'SplinePrimitive')
                        print '%s useCache success (^_^)' % interim_desc
                else:
                    for treeItem in currentSelected_treeItems:
                        if treeItem.text(0).find(interim_name) != -1:
                            interim_desc2 = str(treeItem.text(0))
                            interim_coll = xg.palette(interim_desc2)
                            xg.setAttr('liveMode', '0', interim_coll, interim_desc2, 'SplinePrimitive')
                            xg.setAttr('useCache', '1', interim_coll, interim_desc2, 'SplinePrimitive')
                            xg.setAttr('cacheFileName', abcData_path, interim_coll, interim_desc2, 'SplinePrimitive')
                            print '%s useCache success (^_^)' % interim_desc2

            import xgenm.xgGlobal as xgg
            de = xgg.DescriptionEditor
            de.refresh('Full')
            return

    def eventFilter(self, widget, event):
        if widget == self.ui.abcPath_line:
            if event.type() == QtGui.QMouseEvent.MouseButtonDblClick:
                self.getAbcPath()
                return True
            else:
                return False

        else:
            return QtWidgets.QMainWindow.eventFilter(self, widget, event)


def showWindow():
    global win
    try:
        win.close()
    except:
        pass

    win = XGenToolsUI()
    win.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    win.show()