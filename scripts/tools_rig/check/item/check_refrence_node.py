#coding: utf-8

import pymel.core as pm
import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查大纲中的是否具有reference节点"
        self.iscolor=True
        self.results=[]

    def get_ref_nodes(self):
        return cmds.ls(type="reference")

    def check(self):
        res=self.get_ref_nodes()
        if res:
            self.results.extend(res)
            self.iscolor=False
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            pm.select(self.results)