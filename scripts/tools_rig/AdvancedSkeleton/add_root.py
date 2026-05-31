# -*- coding: utf-8 -*-

import maya.cmds as cmds
import pymel.core as pm
import math

def add_adv_root():
    if cmds.objExists("Group|Main|FitSkeleton|Root"):
        cmds.rename("Group|Main|FitSkeleton|Root","FitSkeleton_Root")
    if not cmds.objExists("Root"):
        Root = cmds.createNode("joint",name="Root")
    else:
        Root = "|Root"
    if cmds.objExists("Group|Main|DeformationSystem"):
        Root_M = cmds.listRelatives("Group|Main|DeformationSystem",c=1)
        cmds.parent(Root_M,Root)
    if cmds.objExists("Group|Main"):
        scale=cmds.arclen("Group|Main")/math.pi
        Main01=cmds.circle(ch=0,nr=[0, 1, 0],r=scale/2*.85,name="Main01")[0]
        move = cmds.circle(ch=0,nr=[0, 1, 0],r=scale/2*1.0,name="Move")[0]
        if cmds.objExists("RootSystem|RootCenterBtwLegsBlended_M|RootOffsetX_M|RootExtraX_M|RootX_M"):
            m=cmds.xform("RootSystem|RootCenterBtwLegsBlended_M|RootOffsetX_M|RootExtraX_M|RootX_M",q=1,ws=1,m=1)
            cmds.xform(move,m=m)
            cmds.makeIdentity(move,apply=True,t=1,r=1,s=1,n=0,pn=1)
            FitSkeleton="Group|Main|FitSkeleton"
            MotionSystem="Group|Main|MotionSystem"
            DeformationSystem="Group|Main|DeformationSystem"
            if cmds.objExists(FitSkeleton) and cmds.objExists(MotionSystem) and cmds.objExists(DeformationSystem):
                cmds.parent(Main01,"Group|Main")
                cmds.parent(move,Main01)
                cmds.parent(FitSkeleton,move)
                cmds.parent(MotionSystem,move)
                cmds.parent(DeformationSystem,move)
                cmds.parentConstraint(Main01,Root)
                cmds.scaleConstraint(Main01, Root)

def adv_add_global(FKShoulder, FKExtraShoulder, FKOffsetShoulder, side=""):
    cmds.addAttr(FKShoulder, ln="global", at="double", min=0, max=10, dv=0)
    cmds.setAttr(FKShoulder + ".global", keyable=1)
    FKShoulder_L = pm.PyNode(FKShoulder)
    FKExtraShoulder_L = pm.PyNode(FKExtraShoulder)
    FKOffsetShoulder_L = pm.PyNode(FKOffsetShoulder)
    FKGlobalStaticShoulder_L = pm.createNode("transform", name="FKGlobalStaticShoulder_%s" % (side))
    FKGlobalShoulder_L = pm.createNode("transform", name="FKGlobalShoulder_%s" % (side), p=FKGlobalStaticShoulder_L)
    GlobalOffsetShoulder_L = pm.createNode("transform", name="GlobalOffsetShoulder_%s" % (side))
    GlobalShoulder_L = pm.createNode("transform", name="GlobalShoulder_%s" % (side), p=GlobalOffsetShoulder_L)
    pm.delete(pm.parentConstraint(FKShoulder_L, FKGlobalStaticShoulder_L))
    pm.delete(pm.parentConstraint(FKShoulder_L, GlobalOffsetShoulder_L))
    pm.parent(GlobalOffsetShoulder_L, "GlobalSystem")
    pm.parent(FKGlobalStaticShoulder_L, FKOffsetShoulder_L)
    pm.parent(FKExtraShoulder_L, FKGlobalShoulder_L)

    con = pm.orientConstraint(FKGlobalStaticShoulder_L, GlobalShoulder_L, FKGlobalShoulder_L)
    user_attr = pm.listAttr(con, userDefined=1)
    unitConversion = pm.createNode('unitConversion')
    unitConversion.conversionFactor.set(.1)
    reverse = pm.createNode('reverse')
    pm.connectAttr(FKShoulder_L + ".global", unitConversion + ".input")
    pm.connectAttr(unitConversion + ".output", reverse + ".inputX")
    pm.connectAttr(unitConversion + ".output", con + "." + user_attr[1])
    pm.connectAttr(reverse + ".outputX", con + "." + user_attr[0])

def adv_add_global_cmd():
    adv_add_global("FKShoulder_L", "FKExtraShoulder_L", "FKOffsetShoulder_L", "L")
    adv_add_global("FKShoulder_R", "FKExtraShoulder_R", "FKOffsetShoulder_R", "R")