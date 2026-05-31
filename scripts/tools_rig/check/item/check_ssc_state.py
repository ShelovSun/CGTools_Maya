#coding: utf-8

import maya.cmds as cmds
import pymel.core as pm
import time

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查Root骨骼下的ssc属性是否勾选"
        self.iscolor=True
        self.results=[]

    def get_rootchild_status(self, *args):
        root = pm.ls("DeformationSystem")
        res=[]
        if len(root)==1:
            root=root[0].getChildren()[0]
            jnts=root.getChildren(type="joint")
            for jnt in jnts:
                ssc=jnt.segmentScaleCompensate.get()
                if ssc:
                    res.append(jnt)
                    #jnt.segmentScaleCompensate.set(False)
        return res

    def check(self):
        res=self.get_rootchild_status()
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
                jnt.segmentScaleCompensate.set(False)
        self.results=[]