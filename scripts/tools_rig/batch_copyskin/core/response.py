#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob

import pymel.core as pm
import maya.cmds as cmds
from qtundo import undo
from rig.batch_copyskin.ui.head import *
from rig.batch_copyskin.ui.ui_main_window import ui_main_window

class Response(QMainWindow):

    def __init__(self,parent=None):
        super(Response,self).__init__(parent)
        self.maya_win = parent
        self.setWindowTitle("batch_copyskin")
        self.setupUI()
        self.getElems()
        self.setDefault()
        self.connection()

    def setupUI(self):
        self.ui_main_window = ui_main_window()
        self.setCentralWidget(self.ui_main_window)

    def getElems(self):
        self.left_reload_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.left_reload_pushButton
        self.right_reload_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.right_reload_pushButton

        self.left_listWidget = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.left_listWidget
        self.right_listWidget = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.right_listWidget

        self.left_add_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.left_add_pushButton
        self.left_remove_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.left_remove_pushButton
        self.left_clear_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.left_clear_pushButton
        self.right_add_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.right_add_pushButton
        self.right_remove_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.right_remove_pushButton
        self.right_clear_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.right_clear_pushButton

        self.clearall_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.clearall_pushButton
        self.apply_pushButton = self.ui_main_window.ui_batch_copyskin_widget.main_Widget.apply_pushButton

    def connection(self):
        self.left_reload_pushButton.clicked.connect(lambda: self.add_to_list(way="reload",base=True,target=False))
        self.left_add_pushButton.clicked.connect(lambda: self.add_to_list(way="add",base=True,target=False))
        self.right_reload_pushButton.clicked.connect(lambda: self.add_to_list(way="reload",base=False,target=True))
        self.right_add_pushButton.clicked.connect(lambda: self.add_to_list(way="add",base=False,target=True))
        self.left_remove_pushButton.clicked.connect(lambda: self.remove_currentselect_item(base=True,target=False))
        self.right_remove_pushButton.clicked.connect(lambda: self.remove_currentselect_item(base=False,target=True))
        self.left_clear_pushButton.clicked.connect(lambda: self.clear_items(base=True,target=False))
        self.right_clear_pushButton.clicked.connect(lambda: self.clear_items(base=False,target=True))
        self.clearall_pushButton.clicked.connect(lambda: self.clear_items(base=True,target=True))
        self.apply_pushButton.clicked.connect(self.copySkin)

        self.left_listWidget.itemSelectionChanged.connect(lambda: self.select_itemTo_object(base=True,target=False))
        self.right_listWidget.itemSelectionChanged.connect(lambda: self.select_itemTo_object(base=False, target=True))

    def setDefault(self):
        self.left_listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.left_listWidget.setMovement(QListView.Free)
        self.right_listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        #self.right_listWidget.setMovement(QListView.Free)
        #self.Hierarchy_radioButton.setChecked(True)
        #self.selected_radioButton.setChecked(False)
        #self.all_radioButton.setChecked(False)

    def is_inlist(self,obj,item_list):
        for item in item_list:
            if obj == item:
                return True
        return False

    def select_itemTo_object(self,**kwargs):
        listwidget = self.get_listwidget(**kwargs)
        items = [i.text() for i in listwidget.selectedItems()]
        cmds.select(items)

    def get_listwidget(self,base=True,target=False):
        if not target and base:
            listwidget=self.left_listWidget
            return listwidget
        if not base and target:
            listwidget = self.right_listWidget
            return listwidget
        if base and target:
            listwidget = [self.left_listWidget,self.right_listWidget]
            return listwidget

    def add_to_list(self,way="reload",**kwargs):
        listwidget=self.get_listwidget(**kwargs)
        items = [str(i) for i in pm.selected()]
        #items.reverse()
        if way=="reload":
            listwidget.clear()
            listwidget.addItems(items)
        elif way=="add":
            listwidget.addItems(items)
            #item_list =[listwidget.item(i).text() for i in range(listwidget.count())]
            #if not item_list:
            #    listwidget.addItems(items)
            #else:
            #    for current_item in items:
            #        isin=self.is_inlist(current_item,item_list)
            #        if not isin:
            #            listwidget.addItem(current_item)
            #        else:
            #            pass

    def remove_currentselect_item(self,*args,**kwargs):
        listwidget = self.get_listwidget(**kwargs)
        items = listwidget.selectedItems()
        for item in items:
            row=listwidget.row(item)
            listwidget.takeItem(row)
        listwidget.update()

    def clear_items(self,*args,**kwargs):
        listwidget = self.get_listwidget(**kwargs)
        if isinstance(listwidget,QListWidget):
            listwidget.clear()
            listwidget.update()
        elif isinstance(listwidget,list):
            for lw in listwidget:
                lw.clear()
                lw.update()

    def copySkin(self,*args):

        sourceMesh = [self.left_listWidget.item(i).text() for i in range(self.left_listWidget.count())]
        targetMesh = [self.right_listWidget.item(i).text() for i in range(self.right_listWidget.count())]

        '''if not pm.objExists(sourceMesh):
            raise RuntimeError('Input a source mesh into the UI to copy skin from.')

        sel = pm.ls(sl=True, fl=True)

        if not sel:
            raise RuntimeError('Select a mesh or vertices to copy the skin to.')

        meshSel = []
        vtxSel = []
        for each in sel:
            if '.vtx[' in each:
                vtxSel.append(each)
            else:
                meshSel.append(each)

        if vtxSel:
            self.copySkinComponents(sourceMesh, vtxSel)

        if meshSel:
            for each in meshSel:
                self.copySkinCluster(sourceMesh, each)'''
        for base,target in zip(sourceMesh,targetMesh):
            print base, target
            self.copySkinCluster(base, target)

    def getSkinCluster(self,mesh):
        '''
        Return the first skinCluster affecting this mesh.
        '''

        if cmds.nodeType(mesh) in ('mesh','nurbsSurface','nurbsCurve'):
            shapes = [mesh]
        else:
            shapes = cmds.listRelatives(mesh, shapes=True, path=True)

        for shape in shapes:
            history = cmds.listHistory(shape, groupLevels=True, pruneDagObjects=True)
            if not history:
                continue
            skins = cmds.ls(history, type='skinCluster')
            if skins:
                return skins[0]
        return None

    def copySkinInfluences(self,source, dest):

        sourceSkin = self.getSkinCluster(source)
        if not sourceSkin:
            return False

        joints = cmds.skinCluster(sourceSkin, query=True, influence=True)

        destSkin = self.getSkinCluster(dest)

        if not destSkin:
            destSkin = cmds.skinCluster(joints, dest, toSelectedBones=True)[0]
        else:
            destJoints = cmds.skinCluster(destSkin, query=True, influence=True)
            for joint in [x for x in joints if x not in destJoints]:
                cmds.skinCluster(destSkin, edit=True, addInfluence=joint, lockWeights=False, weight=0)

        return destSkin

    def copySkinComponents(self,source, destinationVerts):

        if not cmds.listRelatives(source, shapes=True):
            raise RuntimeError('Source object must be geometry.')

        sourceSkin = self.getSkinCluster(source)

        if not sourceSkin:
            raise RuntimeError("Source mesh doesn't have a skinCluster to copy from.")

        destMesh = cmds.ls(destinationVerts[0], o=True)[0]
        destMesh = cmds.listRelatives(destMesh, parent=True)[0]
        destSkin = self.copySkinInfluences(source, destMesh)

        tempSet = cmds.sets(destinationVerts)

        cmds.select(source, tempSet)

        cmds.copySkinWeights(noMirror=True,
                           surfaceAssociation='closestPoint',
                           influenceAssociation='closestJoint',
                           normalize=True)

        cmds.delete(tempSet)
        cmds.select(destinationVerts)


    def copySkinCluster(self,source, destination):

        sourceSkin = self.getSkinCluster(source)
        if not sourceSkin:
            raise RuntimeError("Source mesh doesn't have a skinCluster to copy from.")

        destSkin = self.copySkinInfluences(source, destination)

        cmds.copySkinWeights(sourceSkin=sourceSkin, destinationSkin=destSkin, noMirror=True,
                           surfaceAssociation='closestPoint',
                           influenceAssociation='closestJoint', normalize=True)

        return destSkin

if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    ui = Response()
    ui.show()
    sys.exit(app.exec_())