#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import os
import sys
import maya.cmds as mc
import maya.mel as mel
from functools import partial
scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')

objDict = {
    0: ["FKShoulder_L", "FKElbow_L", "FKWrist_L", "IKArm_L", "PoleArm_L", "FKIKArm_L", "IKXShoulder_L", "IKXElbow_L",
        "IKXWrist_L", "IKWrist_L_loc"],
    1: ["FKShoulder_R", "FKElbow_R", "FKWrist_R", "IKArm_R", "PoleArm_R", "FKIKArm_R", "IKXShoulder_R", "IKXElbow_R",
        "IKXWrist_R", "IKWrist_R_loc"],
    2: ["FKHip_L", "FKKnee_L", "FKAnkle_L", "IKLeg_L", "PoleLeg_L", "FKIKLeg_L", "IKXHip_L", "IKXKnee_L", "IKXAnkle_L",
        "IKLeg_L_loc"],
    3: ["FKHip_R", "FKKnee_R", "FKAnkle_R", "IKLeg_R", "PoleLeg_R", "FKIKLeg_R", "IKXHip_R", "IKXKnee_R", "IKXAnkle_R",
        "IKLeg_R_loc"], }


class ShowUI(object):
    def __init__(self):
        self.window = 'window'

    def createUi(self):
        if mc.window(self.window, exists=True):
            mc.deleteUI(self.window, window=True)
        self.window = mc.window(self.window, title="动作小工具", widthHeight=[300, 100])
        self.mainForm()
        mc.windowPref(self.window, remove=True)
        mc.showWindow()

    def mainForm(self):
        layout = mc.formLayout()
        ik_fk = mc.button(label=u"IK/FK切换(New)", w=100, bgc=[0, 0.9, 0.9], c=partial(self.switch))
        tra_zero = mc.button(label=u"控制器位移归零", w=100, bgc=[0.9, 0.2, 0.5], c=partial(self.zero_Trans))
        rot_zero = mc.button(label=u"控制器旋转归零", w=100, bgc=[0.9, 0.2, 0.5], c=partial(self.zero_Rot))
        # self.rLeg = mc.button(label=u"右脚", w=100, bgc=[0, 0.9, 0.9], c=partial(self.switch, objDict[3]))
        mc.formLayout(layout, e=True, attachForm=[(tra_zero, "top", 15), (tra_zero, "left", 15),
                                                  (rot_zero, "top", 15), (rot_zero, "left", 130),
                                                  (ik_fk, "top", 50), (ik_fk, "left", 15)])

    @staticmethod
    def switch(*arg):
        """ """
        mel.eval('source "%s/ikFk.mel";asAutoSwitchFKIK;' % scriptsPath)

    @staticmethod
    def zero_Trans(*arg):
        ctrName = mc.ls(sl=True)
        for ctrl in ctrName:
            shapes = mc.listRelatives(ctrl, shapes=True, fullPath=True)
            for shape in shapes:
                if mc.nodeType(shape) == 'nurbsCurve':
                    try:
                        mc.setAttr((ctrl + ".translateX"), 0)
                        mc.setAttr((ctrl + ".translateY"), 0)
                        mc.setAttr((ctrl + ".translateZ"), 0)
                    except:
                        # print (namespace+":"+a+" can't rotate!")
                        pass

    @staticmethod
    def zero_Rot(*arg):
        ctrName = mc.ls(sl=True)
        for ctrl in ctrName:
            shapes = mc.listRelatives(ctrl, shapes=True, fullPath=True)
            for shape in shapes:
                if mc.nodeType(shape) == 'nurbsCurve':
                    try:
                        mc.setAttr((ctrl + ".rotateZ"), 0)
                        mc.setAttr((ctrl + ".rotateX"), 0)
                        mc.setAttr((ctrl + ".rotateY"), 0)
                    except:
                        # print (namespace+":"+a+" can't rotate!")
                        pass

    def setTPose(self):  # 归零tpose
        namespace = self.namespace
        CtrNameALL = [
            'RootX_M', 'FKXiong_R', 'FKXiong_L', 'AimXiong_L', 'AimXiong_R', 'AimXiong_M', 'HipSwinger_M', 'FKChest_M',
            'FKSpine1_M', 'FKRoot_M', 'FKWrist_R', 'FKElbow_R', 'FKShoulder_R', 'FKScapula_L', 'FKScapula_R',
            'FKAnkle_L',
            'FKKnee_L', 'FKHip_L', 'FKHead_M', 'FKNeck_M', 'FKToes_L', 'FKToes_R', 'FKAnkle_R', 'FKKnee_R', 'FKHip_R',
            'Main',
            'All_Ctr', 'FKWrist_L', 'FKElbow_L', 'FKShoulder_L', 'IKArm_L', 'PoleLeg_L', 'IKToes_L', 'RollToes_L',
            'PoleArm_L',
            'IKSpine3_M', 'IKhybridSpine3_M', 'IKhybridSpine2_M', 'IKhybridSpine1_M', 'RollToesEnd_L', 'RollHeel_L',
            'IKLeg_L',
            'PoleArm_R', 'IKSpine1_M', 'IKSpine2_M', 'RollToesEnd_R', 'RollHeel_R', 'IKLeg_R', 'IKArm_R', 'PoleLeg_R',
            'IKToes_R', 'RollToes_R']
        for a in CtrNameALL:
            try:
                mc.setAttr((namespace + ":" + a + ".rotateZ"), 0)
                mc.setAttr((namespace + ":" + a + ".rotateX"), 0)
                mc.setAttr((namespace + ":" + a + ".rotateY"), 0)
            except:
                # print (namespace+":"+a+" can't rotate!")
                pass
            try:
                mc.setAttr((namespace + ":" + a + ".translateX"), 0)
                mc.setAttr((namespace + ":" + a + ".translateY"), 0)
                mc.setAttr((namespace + ":" + a + ".translateZ"), 0)
            except:
                # print (namespace+":"+a+" can't translate!")
                pass

    def saveTime(self):  # 记录当前帧并移动到-100帧位置
        self.timeNow = mc.currentTime(query=True)
        mc.currentTime(-100)

    def setANIBack(self):  # 恢复记录的帧
        mc.currentTime(self.timeNow)
