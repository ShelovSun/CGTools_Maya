#!/usr/bin/env python
"""
BroSimluationCore.py - BroDynamics Simulation Core. This is the core module containing all the simulation functionality.

Includes creation of required objects and connections, running the simulation, tracking and keyframing objects, etc.
"""

import datetime
import math
import json

import maya.cmds as cmds
import maya.mel as mel

import changeLog
import log
import utils

__author__ = "Mikhail Davydov"
__copyright__ = "Copyright 2016"
__version__ = changeLog.currentVersion
__email__ = "nixesvfx@gmail.com"

worldUp = [0,1,0]

def unlockAttributes (objects=None, attrs = ['t','r'], axises = ['x','y','z']):
    if objects == None:
        objects = cmds.ls(sl=1, l=1)

    for obj in objects:
        for attr in attrs:
            for axis in axises:
                cmds.setAttr (obj+'.'+attr+axis, lock=0, keyable=1)


def createAimLocators(axis=[1, 0, 0], up=[0, 1, 0], wuo='none', wu=[0, 1, 0]):
    log.log(">", "AIM:", axis, up, wuo, wu)
    l1 = cmds.spaceLocator()  # cmds.setAttr(l1[0]+'.visibility', 0)
    l2 = cmds.spaceLocator()  # cmds.setAttr(l2[0]+'.visibility', 0)
    aim = cmds.aimConstraint(l2, l1, mo=False, u=up, wut='objectrotation', wuo=wuo, wu=up, aim=axis)
    # aim = cmds.aimConstraint (l2,l1, mo=False, u=up, aim=axis)
    return l1, l2, aim


@utils.try_except
def getDistance(posA, posB):
    dx = posA[0] - posB[0]
    dy = posA[1] - posB[1]
    dz = posA[2] - posB[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def getOffset(obj):
    attr='broDynamicsOffset'
    off = [[0,0,0],[0,0,0]]
    if cmds.objExists(obj+'.'+attr):
        off = json.loads(cmds.getAttr(obj+'.'+attr))
    return off

#@utils.try_except
def getWSPosition(object, rp=False):
    if rp:
        return cmds.xform(object, q=1, ws=1, rp=1)
    else:
        return cmds.xform(object, q=1, ws=1, t=1)


#@utils.try_except
def setWSPosition(object, pos, rp=False):
    if rp:
        return cmds.xform(object, ws=1, rp=pos)
    else:
        return cmds.xform(object, ws=1, t=pos)


#@utils.try_except
def getWSRotation(object, rp=False):
    if rp:
        rotation = cmds.xform(object, q=1, ws=1, rp=1)
    else:
        rotation = cmds.xform(object, q=1, ws=1, ro=1)

    return rotation

#@utils.try_except
def aimToPosition(object, targetPos, l1, l2, axis=[1, 0, 0], up=[0, 1, 0], wuo='none', wu=[0, 1, 0], key=True):
    setWSPosition(l1, getWSPosition(object))
    setWSPosition(l2, targetPos)

    setWSRotation(object, getWSRotation(l1))

    if cmds.objExists(object+'.broDynamicsOffset'):
        offset = getOffset(object)
        cmds.xform(object, r=1, ro=offset[1], t=offset[0])

    cmds.select(cl=True)
    if key:
        cmds.setKeyframe(object)

@utils.try_except
def setWSRotation(object, rot):
    return cmds.xform(object, ws=1, ro=rot)


@utils.try_except
def createCurveByObjects(objects=[], reversed=False, ax = [1,0,0], useRotatePivot=False):
    """
    Create curve by given objects.

    Args:
        objects([str]): An array of objects to work with.

    Returns:
        object: Returns generated Curve object.
    """

    if len(objects) < 3:
        cmds.error(
            "Not enough objects were given for createCurveByObjects command. It requires at least 3 objects selected. If you need to simulate just 1 object's dynamics - there is a workaround for that, refer to the documentation.")

    if useRotatePivot:
        at_t = False
        at_rp = True
    else:
        at_t = True
        at_rp = False

    pps = []
    for obj in objects:
        pps.append(cmds.xform(obj, q=True, ws=True, t=at_t, rp=at_rp))


    lastControl = objects[len(objects) - 1]
    secondToLastControl = objects[len(objects) - 2]

    # create additional end point

    #create locator and place it at the last control
    l1 = cmds.spaceLocator()
    cmds.xform(l1, ws=True, t=cmds.xform(lastControl, q=1, ws=1, t=at_t, rp=at_rp))

    #cerate another locator and place it at the last - 1 control
    l2 = cmds.spaceLocator()
    cmds.xform(l2, ws=True, t=cmds.xform(secondToLastControl, q=1, ws=1, t=at_t, rp=at_rp))

    #Aim one locator at another
    cmds.delete(cmds.aimConstraint(l1, l2, mo=False))

    #get distance between two last controls
    dist = getDistance(cmds.xform(lastControl, q=1, ws=1, t=at_t, rp=at_rp),
                       cmds.xform(secondToLastControl, q=1, ws=1, t=at_t, rp=at_rp))

    #place locator at the position of the last control, full match
    #cmds.xform(l2, ws=True, t=getWSPosition(l1))
    utils.matchTransform (l2, lastControl, t=True, r=True, forcexform=True, useRotatePivot=useRotatePivot)

    #move it at relative distance
    cmds.xform(l2, os=True, r=True, t=(dist*ax[0], dist*ax[1], dist*ax[2]))

    pps.append(cmds.xform(l2, q=True, ws=True, t=True))

    for i in [l1, l2]:
        cmds.delete(i)
    return cmds.curve(p=pps)


@utils.try_except
def generateDynamicHair(myCurve, attract, attractionDamp, bendResistance, stretchResistance, compressionResistance,
                        drag, damp, motionDrag, mass, collideWidthOffset, colliders, forces, collisionMode, useRotatePivot=False):
    dynamicGrp = cmds.group(em=True, n='Spring_Dynamics_temp_' + utils.randomHash())
    dynamicStuff = []

    dynamicHair = cmds.createNode('hairSystem', n='hairSystem_' + utils.randomHash())

    # Simulation properties
    cmds.setAttr(dynamicHair + '.startCurveAttract', attract)  # 0.1
    cmds.setAttr(dynamicHair + '.attractionDamp', attractionDamp)  # 0
    cmds.setAttr(dynamicHair + '.bendResistance', bendResistance)  # 1
    cmds.setAttr(dynamicHair + '.stretchResistance', stretchResistance)  # 10
    cmds.setAttr(dynamicHair + '.compressionResistance', compressionResistance)  # 10
    cmds.setAttr(dynamicHair + '.drag', drag)  # 0.05
    cmds.setAttr(dynamicHair + '.damp', damp)  # 0
    cmds.setAttr(dynamicHair + '.motionDrag', motionDrag)  # 0
    cmds.setAttr(dynamicHair + '.collideWidthOffset', collideWidthOffset)
    cmds.setAttr(dynamicHair + '.mass', mass)
    if collideWidthOffset != 0:
        cmds.setAttr(dynamicHair + '.solverDisplay', 1)

    if cmds.objExists('nucleus_BroDynamics') != True:
        nucleus = cmds.createNode('nucleus', n='nucleus_BroDynamics')
        deleteNucleus = True

        cmds.connectAttr('time1.outTime', nucleus + '.currentTime')
    else:
        nucleus = 'nucleus_BroDynamics'
        deleteNucleus = False


    # connect time node to hair and nucleus node
    cmds.connectAttr('time1.outTime', dynamicHair + '.currentTime')

    # connect nucleus node to hair node
    cmds.connectAttr(nucleus + '.startFrame', dynamicHair + '.startFrame')
    cmds.connectAttr(nucleus + '.outputObjects[0]', dynamicHair + '.nextState')
    cmds.connectAttr(dynamicHair + '.currentState', nucleus + '.inputActive[0]')
    cmds.connectAttr(dynamicHair + '.startState', nucleus + '.inputActiveStart[0]')

    # cmds.rebuildCurve (myCurve, rt=0, ch=0, replaceOriginal=1)

    _follicle = cmds.createNode('follicle', n='follicle_' + utils.randomHash())

    cmds.setAttr(_follicle + '.restPose', 1)

    _nurbsCurve = cmds.createNode('nurbsCurve', n='nurbsCurve' + utils.randomHash())  # output curve
    # connect nodes
    cmds.connectAttr(dynamicHair + '.outputHair[%s]' % (0), _follicle + '.currentPosition')
    cmds.connectAttr(_follicle + '.outHair', dynamicHair + '.inputHair[%s]' % (0))
    # connect follicle node to input curve
    cmds.connectAttr(myCurve + '.local', _follicle + '.startPosition')
    cmds.connectAttr(myCurve + '.worldMatrix[0]', _follicle + '.startPositionMatrix')
    # connect follicle node to output curve
    cmds.connectAttr(_follicle + '.outCurve', _nurbsCurve + '.create')

    if collisionMode:
        log.log("", "COLLISION MODE")
        cmds.setAttr(dynamicHair + '.active', 1)
        cmds.setAttr(_follicle + '.startDirection', 1)

    if len(forces) > 0:
        for force in forces:
            log.log(">", "Applying force", force, "to object", dynamicHair)
            cmds.connectDynamic(dynamicHair, f=force)

    dynamicStuff.append(cmds.listRelatives(dynamicHair, p=True)[0])
    dynamicStuff.append(cmds.listRelatives(_follicle, p=True)[0])
    dynamicStuff.append(cmds.listRelatives(_nurbsCurve, p=True)[0])

    for obj in dynamicStuff:
        cmds.parent(obj, dynamicGrp)
    cmds.parent(myCurve, dynamicGrp)

    return _nurbsCurve, dynamicGrp, myCurve, nucleus, deleteNucleus


def addColliders(objects, nucleus):
    selection = cmds.ls(sl=True, long=True)
    nRigids = []
    for object in objects:

        shapes = cmds.listRelatives(object, shapes=True)
        for shape in shapes:
            rb = cmds.createNode('nRigid', n='nRigid_' + utils.randomHash())
            nRigids.append(cmds.listRelatives(rb, p=True)[0])
            cmds.connectAttr(shape + '.worldMesh', rb + '.inputMesh')
            cls = cmds.listConnections(nucleus + '.inputPassive')
            clsN = 0
            if cls != None:
                clsN = len(cls)
            cmds.connectAttr(rb + '.currentState', nucleus + '.inputPassive[{0}]'.format(clsN))
            cmds.connectAttr(rb + '.startState', nucleus + '.inputPassiveStart[{0}]'.format(clsN))
            cmds.connectAttr('time1.outTime', rb + '.currentTime')
            cmds.connectAttr(nucleus + '.startFrame', rb + '.startFrame')

    cmds.select(selection, r=True)
    return nRigids


@utils.try_except
def simulateNHair(objects, axis=[1, 0, 0], up=[0, 1, 0], skipFrames=1, attract=0.1, attractionDamp=0, bendResistance=1,
                  stretchResistance=10, compressionResistance=10, drag=0.05, damp=0, motionDrag=0, mass=1.0,
                  collideWidthOffset=0, skipControls=1, dontRefresh=False, matchPositions=False, aimRotation=True,
                  reversed=False, shiftDistance=5, colliders=[], forces=[], collisionMode = False, debugMode=False, useRotatePivot=False):
    log.log(">", "Simulating: ",
            '\nobjects', objects,
            '\naxis', axis,
            '\nup', up,
            '\nskipFrames', skipFrames,
            '\nattract', attract,
            '\nattractionDamp', attractionDamp,
            '\nbendResistance', bendResistance,
            '\nstretchResistance', stretchResistance,
            '\ncompressionResistance', compressionResistance,
            '\ndrag', drag,
            '\ndamp', damp,
            '\nmotionDrag', motionDrag,
            '\nmass', mass,
            '\ncollideWidthOffset', collideWidthOffset,
            '\nskipControls', skipControls,
            '\ndontRefresh', dontRefresh,
            '\nmatchPositions', matchPositions,
            '\naimRotation', aimRotation,
            '\nreversed', reversed,
            '\nshiftDistance', shiftDistance,
            '\ncolliders', colliders,
            '\nforces', forces,
            '\ncollisionMode ', collisionMode,
            '\ndebugMode ', debugMode,
            '\nuseRotatePivot ', useRotatePivot)

    if len(objects) < 2:
        cmds.error(
            "Select at least 2 objects. If you need to simulate just 1 jiggly object, select it's parent control, then select object to add jiggle to and simulate.")

    additionalLocators = []
    if len(objects) == 2:
        parentCtrl = objects[0]
        object = objects[1]

        objectLocT = []
        for ax in axis:
            objectLocT.append(ax * shiftDistance)

        parentLocT = []
        for ax in axis:
            parentLocT.append(ax * shiftDistance * (-1))

        objectLoc = cmds.spaceLocator()[0]
        cmds.parent(objectLoc, object)
        cmds.xform(objectLoc, ws=0, a=1, ro=(0, 0, 0))
        cmds.xform(objectLoc, ws=0, a=1, t=objectLocT)
        objects.append(objectLoc)
        additionalLocators.append(objectLoc)

        parentLoc = cmds.spaceLocator()[0]
        cmds.parent(parentLoc, object)
        cmds.xform(parentLoc, ws=0, a=1, ro=(0, 0, 0))
        cmds.xform(parentLoc, ws=0, a=1, t=parentLocT)
        cmds.parent(parentLoc, parentCtrl)
        objects[0] = parentLoc
        additionalLocators.append(parentLoc)


    #create curve
    cur = createCurveByObjects(objects, reversed, axis, useRotatePivot)

    #make it dynamic
    dynamicCurve, dynamicGrp, myCurve, nucleus, deleteNucleus = generateDynamicHair(cur, attract, attractionDamp, bendResistance,
                                                                     stretchResistance, compressionResistance, drag,
                                                                     damp, motionDrag, mass, collideWidthOffset, colliders, forces, collisionMode)
    nRigids = addColliders(colliders, nucleus)
    dynamicCurve = cmds.listRelatives(dynamicCurve, parent=True)[0]
    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)
    frameCount = endFrame - startFrame

    nucleusStartFramePre = cmds.getAttr(nucleus+'.startFrame')
    cmds.setAttr (nucleus+'.startFrame', startFrame)

    #cmds.error("")

    # delete old keys
    for i, obj in enumerate(objects):
        if i >= skipControls:
            for a in ['t', 'r']:
                for t in ['x', 'y', 'z']:
                    cmds.cutKey(obj, time=(startFrame + skipFrames, endFrame), attribute=a + t, option='keys')

    messageColor = '#00FF00'
    message = 'Simulation completed in:'

    cmds.parent(cur, objects[0])
    l1, l2, aim = createAimLocators(axis, up, wuo=objects[0], wu=worldUp)

    # oldBlendAims = getExistingBlendAims()

    if not debugMode:

        # Progressbar
        gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

        cmds.progressBar(gMainProgressBar,
                         edit=True,
                         beginProgress=True,
                         isInterruptable=True,
                         status='...',
                         maxValue=5000)

        cmds.progressBar(gMainProgressBar, e=True, maxValue=int(frameCount) * len(objects), pr=0,
                         status="Simulating...")

        # remember old playback and autoKeyframe settings and change to playeveryframe and turn off autoKeyframing
        old_ps, old_mps = cmds.playbackOptions(q=True, ps=True), cmds.playbackOptions(q=True, mps=True)
        cmds.playbackOptions(ps=0.0), cmds.playbackOptions(mps=0.0)
        oldAutoKeyframe = cmds.autoKeyframe(q=True, st=True)
        cmds.autoKeyframe(st=False)


        #raise

        cmds.currentTime(startFrame+1)
        cmds.refresh()
        cmds.currentTime(startFrame)
        cmds.refresh()

        startTime = datetime.datetime.now()
        averageTime = None
        remainingTime = None

        if dontRefresh:
            cmds.refresh(su=True)
        for frame in range(0, int(frameCount)):

            if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
                message = "Simulation interrupted. Time spent:"
                messageColor = "#FF0000"
                break

            if frame > skipFrames:
                for i, obj in enumerate(objects):
                    if i >= skipControls:
                        #Set rotation order for locators from object
                        for o in [l1, l2]:
                            cmds.setAttr(o[0]+'.rotateOrder',cmds.getAttr (obj+'.rotateOrder'))

                        if aimRotation:
                            aimToPosition(obj, getWSPosition(dynamicCurve + '.cv[' + str(i + 1) + ']'), l1, l2, axis, up,
                                          wuo=objects[0], wu=worldUp)
                        if matchPositions:
                            setWSPosition(obj, getWSPosition(dynamicCurve + '.cv[' + str(i) + ']'))
                            cmds.setKeyframe(obj)

                        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                                         status="Time remaining: " + str(remainingTime))
                    #if i>0:
                        #cmds.error("ops. "+str(obj))
            else:
                for i, obj in enumerate(objects):
                    if i >= skipControls:
                        cmds.setKeyframe(obj)
                        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                                         status="Time remaining: " + str(remainingTime))
            averageTime = (datetime.datetime.now() - startTime) / (int(frame) + 1)
            remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(frame) + 1))

            cmds.currentTime(int(startFrame) + frame)

        if dontRefresh:
            cmds.refresh(su=False)
        cmds.delete(myCurve)
        cmds.delete(dynamicGrp)
        # deleteNewBlendAims(oldBlendAims)
        for o in [aim, l1, l2]:
            cmds.delete(o)

        for locator in additionalLocators:
            cmds.delete(locator)

        cmds.playbackOptions(ps=old_ps), cmds.playbackOptions(mps=old_mps)  # restore playback settings
        cmds.autoKeyframe(st=oldAutoKeyframe)
        #print nRigids
        cmds.setAttr (nucleus+'.startFrame', nucleusStartFramePre)
        if len(nRigids) > 0:
            cmds.delete(nRigids)
        if deleteNucleus:
            cmds.delete(nucleus)


        cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
        completionTime = datetime.datetime.now() - startTime
        log.inViewLog(messageColor, message, completionTime)

    else:
        expCommand = '$cmd = "cmds.undoInfo(swf=False)\\n\\\n'
        for i, obj in enumerate(objects):
            if i >= skipControls:
                if aimRotation:
                    expCommand += 'BroTools.BroDynamics.BroSimulationCore.aimToPosition(\'{obj}\', BroTools.BroDynamics.BroSimulationCore.getWSPosition(\'{dynamicCurve}\' + \'.cv[\' + str({i} + 1) + \']\'), \'{l1}\', \'{l2}\', \'{axis}\', \'{up}\', wuo=\'{objects0}\', wu={worldUp}, key=False)\\n\\\n'.format(obj=obj, dynamicCurve=dynamicCurve, i=i, l1=l1[0],l2=l2[0],axis=axis,up=up,objects0=objects[0], worldUp=worldUp)

                if matchPositions:
                    expCommand += 'BroTools.BroDynamics.BroSimulationCore.setWSPosition(\'{obj}\', BroTools.BroDynamics.BroSimulationCore.getWSPosition(\'{dynamicCurve}\' + \'.cv[\' + str({i}) + \']\'))\\n\\\n'.format(obj=obj, dynamicCurve=dynamicCurve, i=i)
        expCommand += 'cmds.undoInfo(swf=True)";'
        expCommand += "\n\npython($cmd);\n"
        print "Adding expression:\n", expCommand, "\n-\n"


        cmds.expression(s=expCommand, n="BroDynamics_debugOnlyExp_" + utils.randomHash(), ae=True)


        log.inViewLog(messageColor, "Debug mode. You will have to remove all unwanted objects manually, remember the settings and paste them into BroDynamics for final simulation. To change matchPosition\Rotation params, you need to re-run the creation script.")



@utils.try_except
def createNParticle(obj, suffix, goalWeight=0.9, goalSmoothness=3, nucleusName='noNameNucleusNode', startFrame=1,
                    collide=True, selfCollide=False, collideWidthScale=1.0, bounce=0, friction=0.1, stickiness=0,
                    drag=0.010, damp=0):
    """
    Create nParticle following given object.
    Args:
        obj (str): Object to follow.
        suffix (str): naming suffix
        goalWeight (float): Goal Weight. Similar to spring strength.
        goalSmoothness (float) : Goal Smoothness. Similar to spring dampening.

    Returns: object, particle name

    """
    if goalWeight > 1 or goalWeight < 0:
        cmds.error("goalWeight must be in range from 0 to 1. Recieved value: " + str(goalWeight))

    if cmds.objExists(obj) != True:
        cmds.error("Could not find object " + str(obj) + " to add particle to.")

    partName = obj.replace("|", "_") + suffix
    pos = cmds.xform(obj, q=1, ws=1, t=1)

    particle, partShape = cmds.nParticle(n=partName, p=pos)
    cmds.goal(particle, g=obj, utr=True, w=1)

    '''
    if cmds.objExists(nucleusName) != True:
        nucleus = cmds.createNode('nucleus', n=nucleusName)
    else:
        nucleus = nucleusName

    cmds.setAttr (nucleus+'.startFrame', startFrame)

    partShape = cmds.createNode('nParticle', n=partName+'Shape')
    particle = cmds.listRelatives(partShape, p=1)

    #connections from particle
    cmds.connectAttr(partShape+'.currentState',nucleus+'.inputActive')
    cmds.connectAttr(partShape+'.startState',nucleus+'.inputActiveStart')

    #connections to particle
    cmds.connectAttr('time1.outTime',partShape+'.currentTime')
    cmds.connectAttr(nucleus+'.outputObjects',partShape+'.nextState')

    #print obj, goalWeight
    cmds.goal(particle, g=obj, utr=True, w=1)
    '''

    cmds.setAttr(partShape + '.goalWeight[0]', goalWeight)
    cmds.setAttr(partShape + '.goalSmoothness', goalSmoothness)

    settingsDict = {'collide': collide,
                    'selfCollide': selfCollide,
                    'collideWidthScale': collideWidthScale,
                    'bounce': bounce,
                    'friction': friction,
                    'stickiness': stickiness,
                    'drag': drag,
                    'damp': damp,
                    'solverDisplay':1
                    }

    utils.setAttrsFromDict(partShape, settingsDict)
    return obj, partName


@utils.try_except
def simulateNParticles(objects, skipFrames=1, goalWeight=0.9, goalSmoothness=3, dontRefresh=False, collide=True,
                       selfCollide=False, collideWidthScale=1.0, bounce=0, friction=0.1, stickiness=0, drag=0.010,
                       damp=0):
    """
    Apply spring follow behaviour to given objects. Creates nParticles following given objects as springs, runs the simulation and stores positions for each frame, then keyframes objects.
    Args:
        objects:
        skipFrames:
        goalWeight:
        goalSmoothness:
    """
    log.log(">", "Simulating in single object mode. ", goalWeight, goalSmoothness, objects)

    # ERROR CHECK. Initial input values check for errors
    if len(objects) < 1:
        cmds.error("Not enough objects given for simulateNParticles command. Need at least 1.")

    # INITIAL VARIABLES
    particles = []
    positions = [[]]
    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)
    frameCount = endFrame - startFrame

    preExistingNucleusNodes = cmds.ls(type='nucleus')

    # PROGRESSBAR and error messages
    messageColor = '#00FF00'
    message = 'Simulation completed in:'

    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    cmds.progressBar(gMainProgressBar,
                     edit=True,
                     beginProgress=True,
                     isInterruptable=True,
                     status='...',
                     maxValue=5000)

    cmds.progressBar(gMainProgressBar, e=True, maxValue=(int(frameCount) * 2 + len(objects)), pr=0,
                     status="Simulating...")

    # remember old playback and autoKeyframe settings and change to playeveryframe and turn off autoKeyframing
    old_ps, old_mps = cmds.playbackOptions(q=True, ps=True), cmds.playbackOptions(q=True, mps=True)
    cmds.playbackOptions(ps=0.0), cmds.playbackOptions(mps=0.0)
    oldAutoKeyframe = cmds.autoKeyframe(q=True, st=True)
    cmds.autoKeyframe(st=False)

    if dontRefresh:
        cmds.refresh(su=True)

    cmds.currentTime(int(startFrame))

    # Get start time
    startTime = datetime.datetime.now()
    averageTime = None
    remainingTime = None

    # setup nParticles
    for i, obj in enumerate(objects):
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            message = "Simulation interrupted. Time spent:"
            messageColor = "#FF0000"
            break
        obj, partName = createNParticle(obj, '_part_' + str(i), goalWeight, goalSmoothness, collide=collide,
                                        selfCollide=selfCollide, collideWidthScale=collideWidthScale, bounce=bounce,
                                        friction=friction, stickiness=stickiness, drag=drag, damp=damp)
        particles.append(partName)
        averageTime = (datetime.datetime.now() - startTime) / (int(i) + 1)
        remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(i) + 1))
        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                         status="1\\3. Generating particles... Time remaining: " + str(remainingTime))

    # By default cmds.nParticle uses nucleus1 solver. Well, we'll use that as default too, and delete it only if it was not there. This is a place for improvement in the future.
    nucleus = 'nucleus1'

    # START FRAME. set start sim frame and reset it. Remember previous.
    nucleusOldStartFrame = cmds.getAttr(nucleus + '.startFrame')
    cmds.setAttr(nucleus + '.startFrame', int(startFrame))
    cmds.currentTime(int(startFrame) + 1)
    cmds.refresh()
    cmds.currentTime(int(startFrame))
    cmds.refresh()

    # gather positions from nParticle simulation
    for frame in range(0, int(frameCount)):
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            message = "Simulation interrupted. Time spent:"
            messageColor = "#FF0000"
            break
        objPositions = []
        del objPositions[:]
        for i, obj in enumerate(objects):
            targetPos = cmds.getParticleAttr(particles[i] + ".pt[0]", at="worldPosition")
            objPositions.append([targetPos[0], targetPos[1], targetPos[2]])
        positions.append(objPositions)

        cmds.currentTime(int(startFrame) + frame)
        averageTime = (datetime.datetime.now() - startTime) / (int(frame) + 1)
        remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(frame) + 1))
        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                         status="2\\3. Gathering... Time remaining: " + str(remainingTime))

    # Delete particles and nucleus node. No need for particles and nucleus node, only slowing things down.
    cmds.delete(particles)
    nucleusNodes = cmds.ls(type='nucleus')
    cmds.setAttr(nucleus + '.startFrame',
                 nucleusOldStartFrame)  # in case nucleus_BroDynamics existed before simulation, return it's start frame to original.
    for nukeNode in nucleusNodes:
        log.log('', nukeNode, nucleusNodes)
        if nukeNode not in preExistingNucleusNodes:
            cmds.delete(nukeNode)

    cmds.currentTime(int(startFrame))

    # keyframe positions
    # print positions
    for frame in range(0, int(frameCount)):
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            message = "Simulation interrupted. Time spent:"
            messageColor = "#FF0000"
            break
        if frame > skipFrames:
            for i, obj in enumerate(objects):
                targetPos = positions[frame][i]
                setWSPosition(obj, targetPos)
                for a, axis in enumerate(['X', 'Y', 'Z']):
                    # print "Keyframing:", frame, obj, axis, targetPos[a]
                    cmds.setKeyframe(obj, attribute='translate' + axis)
                    # cmds.setKeyframe (obj, attribute='translate'+axis, v=targetPos[a], t=[frame])
        else:
            pass

        cmds.currentTime(int(startFrame) + frame)

        averageTime = (datetime.datetime.now() - startTime) / (int(frame) + 1)
        remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(frame) + 1))

        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                         status="3\\3. Keyframing... Time remaining: " + str(remainingTime))

    if dontRefresh:
        cmds.refresh(su=False)

    cmds.playbackOptions(ps=old_ps), cmds.playbackOptions(mps=old_mps)  # restore playback settings
    cmds.autoKeyframe(st=oldAutoKeyframe)
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    completionTime = datetime.datetime.now() - startTime
    log.inViewLog(messageColor, message, completionTime)


@utils.try_except
def getExistingBlendAims():
    oldSelection = cmds.ls(sl=True, long=True)
    blendAims = []
    try:
        cmds.select('*_blendAim*', r=True)
        blendAims = cmds.ls(sl=True, long=True)
    except:
        pass
    cmds.select(oldSelection, r=True)
    return blendAims


@utils.try_except
def deleteNewBlendAims(oldBlendAims):
    try:
        oldSelection = cmds.ls(sl=True, long=True)
        cmds.select('*_blendAim*', r=True)
        new_blendAims = cmds.ls(sl=True, long=True)
        for ba in new_blendAims:
            if ba not in oldBlendAims:
                cmds.delete(ba)

        cmds.select(oldSelection, r=True)
    except:
        pass

