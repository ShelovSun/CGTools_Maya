#coding: utf-8

import maya.cmds as cmds
import pymel.core as pm
class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查绑定文件中是否具有带有命名空间的物体"
        self.iscolor=True
        self.results=[]

    def checkNamespace(self, *args):
        ''' Check if have name that are repeate.
        '''
        self.results=[]
        namespaceNames = []
        nodeNames = cmds.ls(dag=1)
        for nodeName in nodeNames:
            if ":" in nodeName:
                namespaceNames.append(nodeName)
        return namespaceNames

    def check(self):
        res = self.checkNamespace()
        if res:
            self.results.extend(res)
            self.iscolor = False
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            cmds.select(self.results)
            pm.mel.eval("NamespaceEditor;")