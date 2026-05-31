 # -*- coding: utf-8 -*
import maya.cmds as mc


def copyAndClear():
    polyNameALL = mc.ls(sl=True)
    #mc.pickWalk(d='down')
    #polySelAll = mc.ls(sl=True)

    for polyName in polyNameALL:
        mc.select(polyName)
        mc.pickWalk(d='down')
        polySel = mc.ls(sl=True)    
    
        skinSel = mc.listConnections(polySel,s=True,d=True,t='skinCluster') #获取蒙皮节点名
        jointSel = mc.listConnections(skinSel,s=True,d=True,t='joint') #获取骨骼节点名
        #print skinSel

        jointSel2 = list(set(jointSel))# 去重
        #print jointSel2

        polySel2 = mc.duplicate((polySel),name=(polyName+'_clear'))
        #mc.select(jointSel2,polySel2)
        #print polySel2

        AttrList =['tx','ty','tz','rx','ry','rz','sx','sy','sz']
        print AttrList
        for i in AttrList:
            mc.setAttr ((polySel2[0]+'.'+i),lock=False,typ="string");#解锁物体

        mc.makeIdentity(polySel2,apply=True,t=1,r=1,s=1,n=0,pn=1)#冻结物体变换


        mc.select(jointSel2,polySel2)
        mc.SmoothBindSkin()#给新物体蒙皮

        mc.select(polySel2)
        polySel2shape = mc.pickWalk(d='down')
        skinSel2 = mc.listConnections(polySel2shape,s=True,d=True,t='skinCluster') #获取蒙皮节点名

        #print skinSel,skinSel2

        mc.copySkinWeights(ss=skinSel[0],ds=skinSel2[0],noMirror=True,surfaceAssociation='closestPoint',influenceAssociation='closestJoint')#复制蒙皮权重

copyAndClear()
