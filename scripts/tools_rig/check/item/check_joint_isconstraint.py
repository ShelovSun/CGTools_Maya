#coding: utf-8

import maya.cmds as cmds
#from util import skin
import pymel.core as pm

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查是否有未被约束的蒙皮骨骼"
        self.iscolor=True
        self.results=[]

    def get_unconstraint_joints(self):
        root=cmds.ls("DeformationSystem")
        if len(root) == 1:
            root = pm.PyNode("DeformationSystem")
            ch=root.getChildren(ad=1, type="joint")
            ch.reverse()
            influences = ch[0:2]
            un_skin_joints=[]
            for i in influences:
                is_skin = i.inputs(type="parentConstraint") or i.inputs(type="pointConstraint")
                if not is_skin:
                    un_skin_joints.append(i)
            return un_skin_joints
        else:
            pm.displayWarning(u"No DeformationSystem or more than one DeformationSystem")
            return root

    def check(self):
        res=self.get_unconstraint_joints()
        if res:
            self.results.extend(res)
            self.iscolor=False
            pm.select(res)
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            pm.select(self.results)