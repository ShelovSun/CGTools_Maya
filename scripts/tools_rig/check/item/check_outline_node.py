#coding: utf-8

import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查大纲中的顶层节点是否正确"
        self.iscolor=True
        self.results=[]
        self.outline_top_nodes=["Group"]

    def get_nodes(self):
        default = [u'persp', u'top', u'front', u'side']
        topNode = []
        for abs in cmds.ls(assemblies=1):
            if not abs in default:
                topNode.append(abs)
        return topNode

    def check(self):
        res = self.get_nodes()
        if len(res) != len(self.outline_top_nodes):
            self.results.extend(res)
            self.iscolor = False
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            cmds.select(self.results)