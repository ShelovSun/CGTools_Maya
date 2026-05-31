#coding: utf-8

import maya.cmds as cmds
import pymel.core as pm

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查骨骼的FBX ID"
        self.iscolor=True
        self.results=[]

    def getFBXID(self):
        root=cmds.ls("DeformationSystem")
        if len(root) == 1:
            root = pm.PyNode("DeformationSystem")
            ch=root.getChildren(ad=1, type="joint")
            ch.reverse()
            influences = [root] + ch
            three_id_joints=[]
            for i in influences:
                if i.hasAttr("fbxID"):
                    fbxid = i.getAttr("fbxID")
                    if fbxid == 3:
                        three_id_joints.append(i)
            return three_id_joints
        else:
            pm.displayWarning(u"No DeformationSystem Joint or more than one DeformationSystem Joint")
            return root

    def check(self):
        res=self.getFBXID()
        if res:
            self.results.extend(res)
            self.iscolor=False
            pm.select(res)
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            for i in self.results:
                i.setAttr('fbxID',5)