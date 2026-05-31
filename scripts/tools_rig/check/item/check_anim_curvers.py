#coding: utf-8

import maya.cmds as cmds

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查文件中是否有动画曲线节点存在"
        self.iscolor=True
        self.results=[]

    def get_anim_nodes(self, *args):
        keyed_objs = []
        TA_keys = cmds.ls(type='animCurveTA')
        if TA_keys:
            print TA_keys
            for i in range(len(TA_keys)):  #差关键帧节点什么也没有连接、就一个空余节点的情况 #if cmds.listConnections( TA_key+'.output' )
                objs = cmds.listConnections( TA_keys[i]+'.output' , type='transform', d=1, plugs=0)
                if objs:
                    keyed_objs.append(objs[0])
        TL_keys = cmds.ls(type='animCurveTL')
        if TL_keys:
            for TL_key in TL_keys:
                objs = cmds.listConnections( TL_key+'.output' , type='transform', d=1, plugs=0)
                if objs:
                    keyed_objs.append(objs[0])
        TT_keys = cmds.ls(type='animCurveTT')
        if TT_keys:
            for TT_key in TT_keys:
                objs = cmds.listConnections( TT_key+'.output' , type='transform', d=1, plugs=0)
                if objs:
                    keyed_objs.append(objs[0])
        TU_keys = cmds.ls(type='animCurveTU')
        if TU_keys:
            for TU_key in TU_keys:
                objs = cmds.listConnections( TU_key+'.output' , type='transform', d=1, plugs=0)
                if objs:
                    keyed_objs.append(objs[0])
        return keyed_objs

    def deleteAnimNodes(self, *args):
        selObjs = cmds.ls(sl=1)
        if len(selObjs) == 0:
            #raise Exception('Please select objects')
            raise Exception(u'请选中物体，然后删除动画帧.')
        keyTypes = [ 'animCurveTA','animCurveTL','animCurveTT','animCurveTU' ]
        allKeyNodes = []
        for sel in selObjs:
            for keyType in keyTypes:
                animKeyNodes = cmds.listConnections(sel, type=keyType, source=1)
                if animKeyNodes:
                    allKeyNodes.append(animKeyNodes)
                    cmds.delete(animKeyNodes)

    def check(self):
        res = self.get_anim_nodes()
        if res:
            self.results.extend(res)
            self.iscolor = False
            cmds.select(res)
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            self.deleteAnimNodes()