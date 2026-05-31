#coding: utf-8

import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查文件中是否使用了SHAPES工具的弹窗节点"
        self.iscolor=True
        self.results=[]

    def checkNode(self):
        shapesNodes=[]
        scriptnodes=cmds.ls(type="script")
        for scriptnode in scriptnodes:
            before = cmds.getAttr('%s.before'%(scriptnode))
            if before:
                if "SHAPES Evaluation" in before:
                    cmds.lockNode(scriptnode, lock=False)
                    shapesNodes.append(scriptnode)
        return shapesNodes

    def check(self):
        res = self.checkNode()
        if res:
            self.results.extend(res)
            cmds.select(res)
            self.iscolor = False
        else:
            self.results=[]
            cmds.select(cl=1)
            self.iscolor = True

    def run(self):
        if self.results:
            cmds.delete(self.results)