#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Snow Factory 1.0

#Copyright (c) 2013 Ruchit Bhatt
#All Rights Reserved.
#Email:-ruchitinnewfushion@yahoo.com
    
#Description:
#        To Generate Snow Over Polygon Objects.

#Usage:
#	
#Feel free to email me with any bugs, comments, or requests!


#Steps
#Camera based marquee Selection
#Duplicate Face
#Surface Emission (Nparticle)
#Set Emitter Rate=5000,Speed=0
#Set NparticleShape Ignore Solver Gravity=True, Dynamics Weight & Conserve = 0
#	particle Size radius = 0.1, radius scale randomize=0.5
#play FWD to 25 frames
#Convert Nparticles to polygons
#Set Good settings for good output mesh and then delete history of output mesh.

import maya.cmds as mc
import maya.mel as mm

def snowFactoryWindow():
	#windowsName = "snowFactoryUI"	
	if mc.window('snowFactoryUI', exists=True):
		mc.deleteUI('snowFactoryUI')
	window = mc.window('snowFactoryUI', title=u'Snow Factory 汉化 by ZR v1.01', widthHeight=(400, 600), sizeable=1, minimizeButton=1, maximizeButton=1)
	form = mc.formLayout()
	imagePath = (mc.internalVar(upd=True) + "icons/SnowFactoryLogo.jpg")
	
	mc.text('particleSetupText', label=u'选择需要生成雪的面，然后按执行', font='boldLabelFont')
	mc.button('particlesSetupButton', label=u'执行', width=80, height=30, command=snowFactory)
	mc.text('meshSettingsText', label=u'属性设置:', font='boldLabelFont')
	
	mc.floatSliderGrp('blobbyRadiusScaleSlider', label=u'覆盖大小（可手动输入）', field=True, columnWidth3=(120,40,150), minValue=1, maxValue=100, fieldMinValue=0, fieldMaxValue=10000, value=5, dragCommand=blobbyRadiusScale, changeCommand=blobbyRadiusScale)
	
	mc.floatSliderGrp('MeshTriangleSizeSlider', label=u'贴合度（越小越贴合）', field=True, columnWidth3=(120,40,150), minValue=0, maxValue=10, fieldMinValue=0, fieldMaxValue=10000, value=0.2, dragCommand=MeshTriangleSize, changeCommand=MeshTriangleSize)
	
	
	mc.floatSliderGrp('meshSmoothingItrSlider', label=u'雪模型羽化值', field=True, columnWidth3=(120,40,150), minValue=0, maxValue=10, fieldMinValue=0, fieldMaxValue=10, value=10, dragCommand=MeshSmoothingItr, changeCommand=MeshSmoothingItr)
	mc.text('cleanupText', label=u'清理多余节点:（完成后选雪，然后执行清理，清除多余节点）', font='boldLabelFont')
	mc.button('extractButton', label=u'清理', width=80, height=30, command=snowExtract)
	mc.text('ruchitText', label='By:- Ruchit Bhatt(www.vimeo.com/ruchitbhatt)', font='boldLabelFont')
	mc.formLayout(form, edit=True, attachPosition = [ ('particleSetupText', 'left', 90, 0), ('particlesSetupButton', 'left', 135, 0), ('meshSettingsText', 'left', 10, 0), ('blobbyRadiusScaleSlider', 'left',10, 0), ('MeshTriangleSizeSlider', 'left', 10, 0), ('cleanupText', 'left', 10, 0), ('extractButton', 'left', 160, 0), ('ruchitText', 'left', 10, 0)], attachControl = [ ('particlesSetupButton', 'top', 10, 'particleSetupText'), ('particlesSetupButton', 'top', 10, 'particleSetupText'),('blobbyRadiusScaleSlider', 'top', 30, 'particlesSetupButton'),('MeshTriangleSizeSlider', 'top', 10, 'blobbyRadiusScaleSlider') ,('meshSettingsText', 'top', 15, 'particlesSetupButton'),('meshSmoothingItrSlider', 'top', 15, 'MeshTriangleSizeSlider'),  ('cleanupText', 'top', 15, 'meshSmoothingItrSlider'), ('extractButton', 'top', 10, 'cleanupText'), ('ruchitText', 'top', 25, 'extractButton')])  
	mc.showWindow('snowFactoryUI')

def snowFactory(self):
	#Duplicate Face
	faceSelection = mc.ls(sl=True)
	object = mc.ls(sl=True, o=True)
	mc.polyChipOff(faceSelection, ch=True, kft=True, dup=True, off=0)
	mc.polySeparate(object)
	mc.parent(w=True)
	mc.select(object, deselect=True)
	mm.eval("CenterPivot")
	objA = mc.ls( sl=True, head=1)
	objB = mc.ls( sl=True, tail=1)
	mc.select(objA, deselect=True)
	global objC
	objC = mc.ls( sl=True)
	totalDuplicatedMesh = len(objC)
	#Delete History
	for j in range(0,totalDuplicatedMesh,1):
		TransformNode = mc.ls(objC[j], dependencyNodes=True)
		mc.select(TransformNode[0])
		mm.eval('DeleteHistory')
		mc.delete(TransformNode[0], ch=True)
	orgTrans = mc.ls(objA, dependencyNodes=True)
	mc.select(orgTrans[0])
	mm.eval('DeleteHistory')
	mc.delete(orgTrans[0], ch=True)
	
	#Nparticle Setup
	snowParticle = mc.nParticle()
	for i in range(0,totalDuplicatedMesh,1):
		mc.select(objC[i]) 
		snowEmitter = mc.emitter(n=(objC[i]+'snowEmitter'), type='surface', r=5000, sro=0, nuv=0, cye='none', cyi=1, spd=0, srn=0, nsp=1, tsp=0, mxd=0, mnd=0, dx=1, dy=0, dz=0, sp=0)
		mc.connectDynamic(snowParticle, em=snowEmitter[1])
	mc.setAttr(str(snowParticle[0]) + '.ignoreSolverGravity', 1)
	mc.setAttr(str(snowParticle[0]) + '.dynamicsWeight', 0)
	mc.setAttr(str(snowParticle[0]) + '.conserve', 0)
	mc.setAttr(str(snowParticle[0]) + '.radius', 0.1)
	mc.setAttr(str(snowParticle[0]) + '.radiusScaleRandomize', 0.5)
	mc.setAttr(str(snowParticle[0]) + '.particleRenderType', 3)
	#Play Forward
	
	
	#Generate Nparticle Mesh
	mc.select(snowParticle[0], r=True)
	outMesh = mm.eval('particleToPoly')
	global snowParticleShape
	snowParticleShape = mc.listRelatives(snowParticle[0], s=True)
	mc.setAttr(str(snowParticleShape[0]) + '.blobbyRadiusScale', 1.8)
	mc.setAttr(str(snowParticleShape[0]) + '.meshTriangleSize', 0.2)
	mc.setAttr(str(snowParticleShape[0]) + '.meshMethod', 3)
	mc.setAttr(str(snowParticleShape[0]) + '.meshSmoothingIterations', 10)
	
def threshold(self):
	threshold = mc.floatSliderGrp('thresholdSlider', q=True, value=True)
	mc.setAttr(str(snowParticleShape[0]) + '.threshold', threshold)
	
def blobbyRadiusScale(self):
	blobbyRadius = mc.floatSliderGrp('blobbyRadiusScaleSlider', q=True, value=True)
	mc.setAttr(str(snowParticleShape[0]) + '.blobbyRadiusScale', blobbyRadius)
	
def MotionStreak(self):
	motionStreak = mc.floatSliderGrp('MotionStreakSlider', q=True, value=True)
	mc.setAttr(str(snowParticleShape[0]) + '.motionStreak', motionStreak)
	
def MeshTriangleSize(self):
	meshTriangleSize = mc.floatSliderGrp('MeshTriangleSizeSlider', q=True, value=True)
	mc.setAttr(str(snowParticleShape[0]) + '.meshTriangleSize', meshTriangleSize)
	
def MaxTriangleResolution(self):
	maxTriangleResolution = mc.intFieldGrp('maxTriangleResolutionField', q=True, value1=True)
	mc.setAttr(str(snowParticleShape[0]) + '.maxTriangleResolution', maxTriangleResolution)
	
def MeshMethod(self):
	meshMethod = mc.optionMenuGrp('meshMethodMenu',q=True, select=True)
	mc.setAttr(str(snowParticleShape[0]) + '.meshMethod', meshMethod)
	
def MeshSmoothingItr(self):
	meshSmoothingItr = mc.floatSliderGrp('meshSmoothingItrSlider', q=True, value=True)
	mc.setAttr(str(snowParticleShape[0]) + '.meshSmoothingIterations', meshSmoothingItr)
	
def snowExtract(self):
	mc.delete(objC)
	junkNucleus = mc.listConnections(snowParticleShape, t='nucleus')
	snowParticle = mc.listRelatives('nParticleShape1',parent=True)
	mc.delete(snowParticle)
	mc.delete(junkNucleus)

