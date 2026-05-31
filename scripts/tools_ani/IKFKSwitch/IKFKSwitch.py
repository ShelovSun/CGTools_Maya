#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AssetsManager_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import maya.cmds as mc
from functools import partial

objDict = {
    0: ["FKShoulder_L", "FKElbow_L", "FKWrist_L", "IKArm_L", "PoleArm_L", "FKIKArm_L", "IKXShoulder_L", "IKXElbow_L",
        "IKXWrist_L", "IKWrist_L_loc"],
    1: ["FKShoulder_R", "FKElbow_R", "FKWrist_R", "IKArm_R", "PoleArm_R", "FKIKArm_R", "IKXShoulder_R", "IKXElbow_R",
        "IKXWrist_R", "IKWrist_R_loc"],
    2: ["FKHip_L", "FKKnee_L", "FKAnkle_L", "IKLeg_L", "PoleLeg_L", "FKIKLeg_L", "IKXHip_L", "IKXKnee_L", "IKXAnkle_L",
        "IKLeg_L_loc"],
    3: ["FKHip_R", "FKKnee_R", "FKAnkle_R", "IKLeg_R", "PoleLeg_R", "FKIKLeg_R", "IKXHip_R", "IKXKnee_R", "IKXAnkle_R",
        "IKLeg_R_loc"], }


class ikFkSwitch(object):
    def __init__(self):
        self.window = 'window'

    def createUi(self):
        if mc.window(self.window, exists=True):
            mc.deleteUI(self.window, window=True)
        self.window = mc.window(self.window, title="IK/FK Switcher v 1.0", widthHeight=[300, 100])
        self.mainForm()
        mc.windowPref(self.window, remove=True)
        mc.showWindow()

    def mainForm(self):
        layout = mc.formLayout()
        self.lArm = mc.button(label=u"左手", w=100, bgc=[0, 0.9, 0.9], c=partial(self.switch, objDict[0]))
        self.rArm = mc.button(label=u"右手", w=100, bgc=[0, 0.9, 0.9], c=partial(self.switch, objDict[1]))
        self.lLeg = mc.button(label=u"左脚", w=100, bgc=[0, 0.9, 0.9], c=partial(self.switch, objDict[2]))
        self.rLeg = mc.button(label=u"右脚", w=100, bgc=[0, 0.9, 0.9], c=partial(self.switch, objDict[3]))
        mc.formLayout(layout, e=True, attachForm=[(self.lArm, "top", 15), (self.lArm, "left", 170),
                                                  (self.rArm, "top", 15), (self.rArm, "left", 30),
                                                  (self.lLeg, "top", 55), (self.lLeg, "left", 170),
                                                  (self.rLeg, "top", 55), (self.rLeg, "left", 30), ])

    def get_xformT(self, *arg):
        sel = arg
        tempValueT = []
        for eachCrv in sel:
            buffer = mc.xform(eachCrv, q=1, ws=1, t=1)
            tempValueT.append(buffer)
        return tempValueT

    def get_xformR(self, *arg):
        sel = arg
        tempValueR = []
        for eachCrv in sel:
            buffer = mc.xform(eachCrv, q=1, ws=1, ro=1)
            tempValueR.append(buffer)
        return tempValueR

    def set_xformT(self, sellist=[], pos_info=[]):
        i = 0
        for eachValue in pos_info:
            mc.xform(sellist[i], ws=1, t=eachValue)
            i = i + 1

    def set_xformR(self, sellist=[], pos_info=[]):
        i = 0
        for eachValue in pos_info:
            mc.xform(sellist[i], ws=1, ro=eachValue)
            i = i + 1

    def switch(self, *args):
        stls = []
        if mc.ls(sl=True):
            self.namespace = mc.ls(sl=True)[0].split(':')[0]
        else:
            mc.error(u"请至少选择一个控制器！")
        for i in args[0]:
            stls.append(self.namespace + ':' + i)
        FKIKBlend = mc.getAttr(stls[5] + '.FKIKBlend')
        if FKIKBlend == 10:  # IK转FK
            xformR = self.get_xformR(stls[6], stls[7], stls[8])
            self.set_xformR([stls[0], stls[1], stls[2]], xformR)
            mc.setAttr(stls[5] + '.FKIKBlend', 0)
        elif FKIKBlend == 0:  # FK转IK
            if mc.ls(stls[9]):
                print(u"存在%s" % stls[9])
            else:
                self.saveTime()
                self.setTPose()
                self.creatLoc()
                self.setANIBack()
            xformT = self.get_xformT(stls[9])
            xformR = self.get_xformR(stls[9])
            arm01 = [self.get_xformT(stls[1])[0][i] - self.get_xformT(stls[0])[0][i] for i in range(3)]
            arm02 = [self.get_xformT(stls[1])[0][i] - self.get_xformT(stls[2])[0][i] for i in range(3)]
            polv = [mc.xform(stls[1], t=1, q=1, ws=1)[i] + arm01[i] + arm02[i] for i in range(3)]
            self.set_xformT([stls[3]], xformT)
            self.set_xformR([stls[3]], xformR)
            self.set_xformT([stls[4]], [polv])
            mc.setAttr(stls[5] + '.FKIKBlend', 10)
        else:
            mc.error(u"请在IK/FK之间确定一种状态")

    def creatLoc(self):  # 添加loc
        namespace = self.namespace
        locName = ['IKWrist_L_loc', 'IKWrist_R_loc', 'IKLeg_L_loc', 'IKLeg_R_loc']
        jiontName = ('Wrist_L', 'Wrist_R', 'Ankle_L', 'Ankle_R')
        for num in range(0, 4):
            LN = (namespace + ':' + locName[num])  # locName
            JN = (namespace + ':' + jiontName[num])  # jiontName
            locator = mc.spaceLocator(n=LN)
            aa = mc.pointConstraint(JN, LN, mo=0)
            mc.delete(aa)
            mc.parentConstraint(JN, LN, mo=1)

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
