#coding: utf-8

import maya.cmds as cmds
import pymel.core as pm
import time

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查模型的绑定状态是否为初始状态"
        self.iscolor=True
        self.results=[]

    def set_skinCluster_status(self, *args):
        skClrs = pm.ls(type='skinCluster')
        for skClr in skClrs:
            skClr.envelope.set(0)
        cmds.refresh()
        time.sleep(1)
        for skClr in skClrs:
            skClr.envelope.set(1)

    def check(self):
        self.set_skinCluster_status()

    def run(self):
        print u"处理错误"