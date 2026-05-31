#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置选择右键菜单

import os, re, maya.cmds as cmds
from PySide2 import QtWidgets, QtGui

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('/tools_select', '')


def showMenu():
    menu = QtWidgets.QMenu()
    action_a = QtWidgets.QAction(u"选择最上层", menu)
    action_a.setIcon(QtGui.QIcon("{}/icons/cursor_64.png".format(scriptsPath)))
    action_a.triggered.connect(GetObjectTop)

    action_b = QtWidgets.QAction(u"选择每物体", menu)
    action_b.setIcon(QtGui.QIcon("{}/icons/cursor_64.png".format(scriptsPath)))
    action_b.triggered.connect(GetEachObjectQuite)

    menu.addAction(action_a)
    menu.addAction(action_b)

    menu.exec_(QtGui.QCursor.pos())


def GetObjectTop():
    """
    选择最上层
    :return:
    """
    selectObj = cmds.ls(sl=True)
    returnList = []
    if selectObj:
        for eachObj in selectObj:
            longName = cmds.ls(eachObj, long=True)
            if len(longName):
                cutName = re.split("\|", longName[0])
                if len(cutName) > 1:
                    if "|" + cutName[1] not in returnList:
                        returnList.append("|" + cutName[1])
        cmds.select(returnList)
    return returnList


def GetEachObjectQuite():
    """
    选择每个物体
    :return:
    """
    GetObjectTop()
    returnList = []
    meshAll = cmds.ls(dag=True, sl=True, type="mesh")
    nurbsSurfaceAll = cmds.ls(dag=True, sl=True, type="nurbsSurface")
    subdivAll = cmds.ls(dag=True, sl=True, type="subdiv")
    allObject = meshAll + nurbsSurfaceAll + subdivAll
    transformList = GetTransform(allObject, True)
    parents = GetParents(allObject, True)
    allObject = transformList + parents
    for eachObject in allObject:
        if cmds.objExists(eachObject) and eachObject not in returnList:
            returnList.append(eachObject)
    cmds.select(returnList)
    return returnList


def GetTransform(shapeList, full=True):
    transformList = []
    for eachShape in shapeList:
        if cmds.nodeType(eachShape) != "transform":
            transforms = cmds.listRelatives(eachShape, fullPath=full, parent=True)
            if transforms is not None:
                if len(transforms):
                    transformList.append(transforms[0])
    return transformList


def GetParents(objectList, full=True):
    parentList = []
    for eachObjext in objectList:
        if cmds.nodeType(eachObjext) == "transform":
            shapesObj = cmds.listRelatives(eachObjext, fullPath=full, shapes=True)
        else:
            shapesObj = eachObjext
        parents = cmds.listRelatives(shapesObj, fullPath=full, allParents=True)
        if parents is not None:
            if len(parents) >= 2:
                for eachParent in parents:
                    if eachParent in parentList:
                        pass
                    else:
                        parentList.append(eachParent)
    return parentList
