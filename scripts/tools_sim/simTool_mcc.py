#!/usr/bin/env python
# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel


class createMyLayoutCls(object):
    def __init__(self, *args):
        pass

    def show(self):
        self.createMyLayout()

    def createMyLayout(self):
        if cmds.window("SimToolWindow", ex=True):
            cmds.deleteUI("SimToolWindow")

        self.window = cmds.window("SimToolWindow", widthHeight=(100, 100), title="解算助手", resizeToFitChildren=1)
        cmds.rowLayout("button1, button2, button3", numberOfColumns=5)

        cmds.columnLayout(adjustableColumn=True, columnAlign="center", rowSpacing=3)

        cmds.button(label='切换成解算模型', width=300, c='switchSim()')
        cmds.button(label='切换成动画模型', width=300, c='switchRig()')
        cmds.button(label='开始解算', width=300, c='creatCache()')

        cmds.button(label='高低模切换', width=300, c='switchPoly()')
        cmds.button(label='导出ABC', width=300, c='exportABC()')

        cmds.setParent(menu=True)

        cmds.showWindow(self.window)


# switchSim()
# switchRig()

# makeCollide()
# creatCache()

# switchPoly()
# exportABC()

def test(*args):
    print("clike")
    pass


def getFilePath():
    sel = cmds.ls(sl=True)
    referenceFilePath = cmds.referenceQuery(sel, filename=True)
    return referenceFilePath


def referenceNodeName():
    sel = cmds.ls(sl=True)
    referenceNodeName = cmds.referenceQuery(sel, referenceNode=True)
    return referenceNodeName


def turnPathToSim():
    namespace = cmds.ls(sl=True)[0].split(':')[0]
    cmds.setAttr((namespace + ':cloth_grp.visibility'), 0)
    getFilePath()
    text = getFilePath()
    FileName = text.split("_hi_rig", 1)
    simFileName = (FileName[0] + '_all_rig.ma')
    return simFileName


def turnPathToRig():
    namespace = cmds.ls(sl=True)[0].split(':')[0]
    cmds.setAttr((namespace + ':cloth_grp.visibility'), 1)
    getFilePath()
    test = getFilePath()
    FileName = test.split("_all_rig", 1)
    rigFileName = (FileName[0] + '_hi_rig.ma')
    return rigFileName


def switchSim():
    getFilePath()
    SimPath = turnPathToSim()
    reNodeName = referenceNodeName()
    cmds.file(SimPath, loadReference=(reNodeName), type=("mayaAscii"), options=("v=0;"))


def switchRig():
    getFilePath()
    RigPath = turnPathToRig()
    reNodeName = referenceNodeName()
    cmds.file(RigPath, loadReference=(reNodeName), type=("mayaAscii"), options=("v=0;"))


# 创建nCache缓存
def creatCache():
    maya.mel.eval('doCreateNclothCache 5 { "2", "1", "10", "OneFilePerFrame", "1", "","1","","0", "add", "0", "1", "1","0","1","mcx" } ')


# 设置碰撞还有点问题，第一次运行会出错，就先不用了
def makeCollide():
    maya.mel.eval('makeCollideNCloth;')


def exportABC():
    maya.mel.eval('AlembicExportSelection;')


def switchPoly():
    sel = cmds.ls(sl=True)
    if sel[0].find("_Hi") == -1:
        # print "its lowpoly"
        cmds.hide(sel[0])
        hiPolyName = sel[0].replace("_Low", "_Hi")

        cmds.showHidden(hiPolyName)

        list1 = cmds.listConnections(sel[0], d=1, type='wrap')
        wrapNode = list(set(list1))
        cmds.setAttr((wrapNode[0] + '.envelope'), 1)
    else:
        # print "its hipoly"
        cmds.hide(sel[0])
        lowPolyName = sel[0].replace("_Hi", "_Low")
        cmds.showHidden(lowPolyName)

        list1 = cmds.listConnections(lowPolyName, d=1, type='wrap')
        wrapNode = list(set(list1))
        cmds.setAttr((wrapNode[0] + '.envelope'), 0)


b_cls = createMyLayoutCls()
b_cls.show()