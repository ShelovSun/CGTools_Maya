#coding: utf-8

import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查骨骼是否设置最大最小值"
        self.iscolor=True
        self.results=[]

    def get_Limit_value(self):
        res=[]
        root = cmds.ls("DeformationSystem")
        if len(root) == 1:
            all_joints = cmds.listRelatives(root[0],ad=1,type="joint")
            for jnt in all_joints:
                enable_rx = cmds.transformLimits(jnt, q=1, erx=1)
                enable_ry = cmds.transformLimits(jnt, q=1, ery=1)
                enable_rz = cmds.transformLimits(jnt, q=1, erz=1)
                if (enable_rx[0] or enable_rx[1]):
                    res.append(jnt)
                    continue
                if (enable_ry[0] or enable_ry[1]):
                    res.append(jnt)
                    continue
                if (enable_rz[0] or enable_rz[1]):
                    res.append(jnt)
                    continue
            return res
        else:
            return root

    def check(self):
        res=self.get_Limit_value()
        if res:
            self.results.extend(res)
            cmds.select(res)
            self.iscolor = False
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            for jnt in self.results:
                cmds.transformLimits(jnt, erx=[0,0])
                cmds.transformLimits(jnt, ery=[0,0])
                cmds.transformLimits(jnt, erz=[0,0])