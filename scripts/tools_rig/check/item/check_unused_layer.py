#coding: utf-8

import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查文件中无用的层节点"
        self.iscolor=True
        self.results=[]

    def checkLayers(self):
        displayLayers = cmds.layout('LayerEditorDisplayLayerLayout', q=1, childArray=1)
        renderLayers = cmds.ls(type='renderLayer')
        layers=[]

        if displayLayers==None and len(renderLayers) > 1:
            rendNum = len(renderLayers)-1
            renderLayers.remove('defaultRenderLayer')
            layers = renderLayers
        elif displayLayers!=None and len(renderLayers) == 1:
            disNum = len(displayLayers)
            layers = displayLayers
        elif displayLayers!=None and len(renderLayers) > 1:
            disNum = len(displayLayers)
            rendNum = len(renderLayers)-1
            renderLayers.remove('defaultRenderLayer')
            layers = renderLayers+displayLayers
        else:
            print "no layer"
        return layers

    def check(self):
        res = self.checkLayers()
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