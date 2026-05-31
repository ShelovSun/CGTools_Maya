#coding: utf-8

import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查文件中是否有重名的物体"
        self.iscolor=True
        self.results=[]

    def checkDuplicateName(self, *args):
        ''' Check if have name that are repeate.
        '''
        self.results=[]
        duplicateNames = []
        nodeNames = cmds.ls(dag=1)
        for nodeName in nodeNames:
            if "|" in nodeName:
                duplicateNames.append(nodeName)
        return duplicateNames
        #if duplicateNames:
        #    cmds.select(duplicateNames, r=1)
        #    num = len(duplicateNames)

    def check(self):
        res = self.checkDuplicateName()
        if res:
            self.results.extend(res)
            self.iscolor = False
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            cmds.select(self.results)