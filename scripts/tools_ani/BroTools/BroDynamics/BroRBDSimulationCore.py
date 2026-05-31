#!/usr/bin/env python
"""
BroRBDSimulationCore.py - BroDynamics module. It is a separate module from BroSimulationCore for distribution purposes.
This module contains RBD and Ragdoll simulation functionality, which includes:

- connecting object using connections module to setup
- running simulation

Ctrl+Q to view doc in pycharm
"""

import datetime
import json

import maya.cmds as cmds
import maya.mel as mel

import connections
import log
import utils
from utils import setAttrsFromDict

__author__ = "Mikhail Davydov"
__copyright__ = "Copyright 2016"
__version__ = "BroDynamics 1.0.0"
__email__ = "nixesvfx@gmail.com"


def defaultRBDSettings():
    '''

    Returns: Dict of default settings for bullet RBD Shape

    '''
    settings = {'colliderShapeType':8,
                          'bodyType':2,
                'linearDamping':0.1,
                'angularDamping':0.1,
                'friction':1,
                'restitution':0.15,
                'autoFit':1
                }

    return settings

def defaultConstraintSettings():
    '''

    Returns: Dict of default settings for bullet constraint object

    '''
    settings = {'constraintType':4}

    for axis in ['X', 'Y', 'Z']:
        settings['linearConstraint'+axis] = 1
        settings['angularConstraint'+axis] = 2
        settings['angularConstraintMin'+axis] = -45
        settings['angularConstraintMax'+axis] = 45
        settings['angularSpringStiffness'+axis] = 200
        settings['angularSpringDamping'+axis] = 0.9
        settings['angularSpringEnabled'+axis] = 1

    return settings

def rbdGroup():
    rbdGroupName = 'broRBD_Group'
    if cmds.objExists(rbdGroupName) != True:
        cmds.group(em=1, n=rbdGroupName)

    return rbdGroupName

def snap(nodes=None, snapTranslates=True, snapRotates=True):
    '''
    Implementation of Red9's simple snap.

    This takes 2 given transform nodes and snaps them together. It takes into
    account offsets in the pivots of the objects. Uses the API MFnTransform nodes
    to calculate the data via a command plugin. This is a stripped down version
    of the snapTransforms cmd
    '''

    if not nodes:
        nodes = cmds.ls(sl=True, l=True)
    if nodes:
        if not len(nodes) >= 2:
            raise StandardError('Please select at least 2 base objects for the SnapAlignment')
    else:
        raise StandardError('Please select at least 2 base objects for the SnapAlignment')

    #pass to the plugin SnapCommand
    for node in nodes[1:]:
        cmds.SnapTransforms(source=nodes[0], destination=node, snapTranslates=snapTranslates, snapRotates=snapRotates)

#@utils.try_except
def matchTransform(child, parent, t=True, r=False, offset=[]):
    """
    Match one object's position and\or rotation to another. Requires SnapRuntime plugin to be loaded.
    Thanks to Red9 consultancy for the plugin.
    If the plugin can't be loaded, it will use cmds.xform, but that does not always work correctly.

    Args:
        child:
        parent:
        t: match transform or not
        r: match rotation or not
        offset: [[tx,ty,tz] [rx,ry,rz]] array. Local-space offset will be applied to object after snapping.

    Version:
        1.0
    """
    if cmds.pluginInfo('SnapRuntime.py', query=True, loaded=True):
        try:
            cmds.SnapTransforms(source=parent, destination=child, snapTranslates=t, snapRotates=r)
        except Exception as e:
            log.log("warning", "Failed to match object", child, "to", parent, "using SnapRuntime plugin. Error: ", e)

    else:
        log.log("warning", "SnapRuntime.py plugin is not loaded. Using cmds.xform to match transforms, but this may result in incorrect matching.")

        if t:
            cmds.xform(child, ws=True, t=cmds.xform(parent, q=True, ws=True, t=True))
        if r:
            cmds.xform(child, ws=True, ro=cmds.xform(parent, q=True, ws=True, ro=True))
            cmds.xform(child, ws=True, rp=cmds.xform(parent, q=True, ws=True, rp=True))

    if len(offset)>0:
        cmds.xform(child, r=1, ro=offset[1], t=offset[0])

def getOffset(obj):
    attr='broMatchOffset'
    off = [[0,0,0],[0,0,0]]
    if cmds.objExists(obj+'.'+attr):
        off = json.loads(cmds.getAttr(obj+'.'+attr))
    return off

#region Functions

@utils.try_except
def addRBDToSelection(selection, scale=40):
    oldSelection = cmds.ls(sl=1, l=1)
    rbdShapes = []
    rbdShapesDict = {}
    cubes = []

    for ctrl in selection:
        cube = cmds.polyCube(n=ctrl.replace('|','_')+'_rbdMesh', d=scale, w=scale, h=scale, ch=False)[0]
        cube = cmds.parent(cube, rbdGroup())[0]
        cube = 'broRBD_Group|'+cube
        matchTransform(cube, ctrl, t=1, r=1)
        cubes.append(cube)

    cmds.select(cubes, r=1)
    rbdOutput = mel.eval('python("RigidBody.CreateRigidBody().executeCommandCB()")')

    for obj in rbdOutput[0::2]:
        rbdShapes.append([obj])

    for i, shape in enumerate(rbdOutput[1::2]):
        rbdShapes[i].append(shape)
        rbdShapes[i].append(selection[i])

    for pair in rbdShapes:
        #print pair
        rbdShapesDict[pair[0]] = pair[1]


    #rbdShapes = [obj, shape]
    log.log('', rbdShapes)
    log.log('', rbdShapesDict)

    #connect
    for pair in rbdShapes:
        connectCTRLToRBD(pair[2], pair[0])

    #Attributes
    for shape in rbdShapes:
        setAttrsFromDict(shape[1], defaultRBDSettings())

    cmds.select (oldSelection, r=1)

    return rbdShapes, rbdShapesDict

@utils.try_except
def removeRBDFromControls(controls):
    for ctrl in controls:
        matchToObj = connections.getConnectionByName(ctrl + '.broMatchTo', multi=False)[0]
        cmds.delete(matchToObj)
    removeRBDConnectionFromCTRLs(controls)

@utils.try_except
def connectCTRLToRBD(ctrl, rbd):
    connections.metaConnect(ctrl, rbd, "broMatchTo", multi=False, force=True)
    connections.metaConnect(rbd, ctrl, "broMatchTo", multi=False, force=True)

    selection = cmds.ls(sl=1, l=1)

    for obj in [ctrl, rbd]:
        if cmds.objExists(obj+'.broMatchOffset') != True:
            cmds.select(obj, r=1)
            cmds.addAttr (ln='broMatchOffset', dt='string')
            cmds.setAttr (obj+'.broMatchOffset', '[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]', type='string')

@utils.try_except
def removeRBDConnectionFromCTRLs(controls):
    for ctrl in controls:
        cmds.deleteAttr(ctrl+'.broMatchTo')

def matchObjects(objects, keyframe=False):
    for obj in objects:

        rbdShape = None
        shapes = cmds.listRelatives(obj, s=1)
        for shape in shapes:
            if cmds.objectType(shape) == 'bulletRigidBodyShape':
                rbdShape = shape

        if rbdShape != None:
            oldRbdType = cmds.getAttr(rbdShape+'.bodyType')
            cmds.setAttr (rbdShape+'.bodyType', 1)
            #cmds.setKeyframe(rbdShape, at='bodyType')
        matchToObj = connections.getConnectionByName(obj + '.broMatchTo', multi=False)[0]
        matchTransform(obj, matchToObj, True, True, getOffset(obj))
        if keyframe:
            for a, axis in enumerate(['X', 'Y', 'Z']):
                cmds.setKeyframe (obj, attribute='translate'+axis)
                cmds.setKeyframe (obj, attribute='rotate'+axis)


        #if rbdShape != None:
            #cmds.setAttr (rbdShape+'.bodyType', oldRbdType)

@utils.try_except
def constraintObjects(objA, objB, bulletSolver='bulletSolver1', scale=10):
    constraintShape = cmds.createNode('bulletRigidBodyConstraintShape', n=objB.replace('|','_')+'_to_'+objA.replace('|','_')+'_constraintShape')
    constraintTransform = cmds.listRelatives(constraintShape, p=1)[0]

    try:
        matchTransform(constraintTransform, objB, True, True)
    except:
        log.log("!", "Could not match constraint", constraintTransform, 'to', objA)


    #incoming connections
    cmds.connectAttr (bulletSolver+'.currentTime', constraintShape+'.currentTime')
    cmds.connectAttr (bulletSolver+'.startTime', constraintShape+'.startTime')
    cmds.connectAttr (bulletSolver+'.outSolverInitialized', constraintShape+'.solverInitialized')

    cmds.connectAttr (objA+'.outRigidBodyData', constraintShape+'.rigidBodyA')
    cmds.connectAttr (objB+'.outRigidBodyData', constraintShape+'.rigidBodyB')

    connections = cmds.getAttr (bulletSolver+'.rigidBodyConstraints', mi=1)
    log.log('', connections)
    if connections != None:
        num = len(connections)+1
    else:
        num = 0

    cmds.connectAttr (constraintShape+'.outConstraintData', bulletSolver+'.rigidBodyConstraints[{}]'.format(str(num)))


    #constraint settings
    setAttrsFromDict(constraintShape, defaultConstraintSettings())
    setAttrsFromDict(constraintShape, defaultConstraintSettings())

    cmds.parent(constraintTransform, objB)

    for ax in ['x','y','z']:
        cmds.setAttr(constraintTransform+'.s'+ax, scale)

def constraintRecursively(object):
    children = cmds.listRelatives(children=True, s=False)
    parent = cmds.listRelatives(parent=True)
    log.log('', parent, children)


    if children != None:
        for child in children:
            if "Shape" not in child:
                constraintObjects (object, child)

        for child in children:
            if "Shape" not in child:
                constraintRecursively(child)

@utils.try_except
def simulateRBDControls(objects, dontRefresh):
    """
    Run simulation for specified CONTROL objects in RBD mode.
    Args:

    Returns:

    """

    log.log (">", "Simulating in RBD mode. ", objects)

    # ERROR CHECK. Initial input values check for errors
    if len(objects) < 1:
        cmds.error ("Not enough objects given for simulateRBDControls command. Need at least 1.")


    # INITIAL VARIABLES
    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)
    frameCount = endFrame - startFrame


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

    cmds.progressBar(gMainProgressBar, e=True, maxValue=(int(frameCount)), pr=0,
                     status="Simulating...")


    # remember old playback and autoKeyframe settings and change to playeveryframe and turn off autoKeyframing
    old_ps, old_mps = cmds.playbackOptions(q=True, ps=True), cmds.playbackOptions(q=True, mps=True)
    cmds.playbackOptions(ps=0.0), cmds.playbackOptions(mps=0.0)
    oldAutoKeyframe = cmds.autoKeyframe(q=True, st=True)
    cmds.autoKeyframe(st=False)

    if dontRefresh:
        cmds.refresh(su=True)

    cmds.currentTime(int(startFrame))

    #Get start time
    startTime = datetime.datetime.now()
    averageTime = None
    remainingTime = None

    bulletSolver = 'bulletSolver1'

    '''
    for i, obj in enumerate(objects):
        matchToObj = connections.getConnectionByName(obj+'.broMatchTo', multi=False)[0]
        shape = None
        shapes = cmds.listRelatives(obj, s=1)
        for potentialShape in shapes:
            if cmds.objectType(potentialShape) == 'bulletRigidBodyShape':
                shape = potentialShape

        if shape != None:
            cmds.cutKey(shape, time=(int(-999999), int(endFrame)), at='bodyType', option='keys')
            cmds.setKeyframe (shape, at='bodyType', v=1, t = [int(startFrame-1])
    '''


    #START FRAME. set start sim frame and reset it. Remember previous.
    nucleusStartFrame = cmds.getAttr (bulletSolver+'.startTime')
    cmds.playbackOptions(min=nucleusStartFrame)
    #cmds.setAttr (bulletSolver+'.startTime', startFrame)
    cmds.currentTime(int(nucleusStartFrame)+1)
    cmds.refresh()
    cmds.currentTime(int(nucleusStartFrame))
    cmds.refresh()

    cmds.currentTime(int(nucleusStartFrame))

    #keyframe positions
    for frame in range(int(nucleusStartFrame), int(endFrame)):
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            message = "Simulation interrupted. Time spent:"
            messageColor = "#FF0000"
            break
        if frame > int(startFrame):
            for i, obj in enumerate(objects):
                matchToObj = connections.getConnectionByName(obj + '.broMatchTo', multi=False)[0]
                matchTransform(obj, matchToObj, True, True, getOffset(obj))
                for a, axis in enumerate(['X', 'Y', 'Z']):
                    #print "Keyframing:", frame, obj, axis, targetPos[a]
                    cmds.setKeyframe (obj, attribute='translate'+axis)
                    cmds.setKeyframe (obj, attribute='rotate'+axis)
                    #cmds.setKeyframe (obj, attribute='translate'+axis, v=targetPos[a], t=[frame])
        else:
            pass

        cmds.currentTime(int(nucleusStartFrame) + frame)

        averageTime = (datetime.datetime.now() - startTime) / (int(frame) + 1)
        remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(frame) + 1))

        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                                     status="Simulating... Time remaining: " + str(remainingTime))

    if dontRefresh:
        cmds.refresh(su=False)



    cmds.playbackOptions(ps=old_ps), cmds.playbackOptions(mps=old_mps)  # restore playback settings
    cmds.autoKeyframe(st=oldAutoKeyframe)
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    cmds.playbackOptions(min=startFrame)
    completionTime = datetime.datetime.now() - startTime
    log.inViewLog(messageColor, message, completionTime)

@utils.try_except
def trackObjectsToConnection(objects, reverse=False, dontRefresh=False):
    log.log (">", "Tracking objects. ", objects)

    # ERROR CHECK. Initial input values check for errors
    if len(objects) < 1:
        cmds.error ("Not enough objects given for trackObjectsToConnection command. Need at least 1.")

    #region P R E

    # INITIAL VARIABLES
    startFrame = cmds.playbackOptions(q=True, min=True)
    endFrame = cmds.playbackOptions(q=True, max=True)
    frameCount = endFrame - startFrame

    # PROGRESSBAR and error messages
    messageColor = '#00FF00'
    message = 'Tracking completed in:'

    gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')

    cmds.progressBar(gMainProgressBar,
                     edit=True,
                     beginProgress=True,
                     isInterruptable=True,
                     status='...',
                     maxValue=5000)

    cmds.progressBar(gMainProgressBar, e=True, maxValue=(int(frameCount)*2+len(objects)), pr=0,
                     status="Simulating...")


    # remember old playback and autoKeyframe settings and change to playeveryframe and turn off autoKeyframing
    old_ps, old_mps = cmds.playbackOptions(q=True, ps=True), cmds.playbackOptions(q=True, mps=True)
    cmds.playbackOptions(ps=0.0), cmds.playbackOptions(mps=0.0)
    oldAutoKeyframe = cmds.autoKeyframe(q=True, st=True)
    cmds.autoKeyframe(st=False)

    if dontRefresh:
        cmds.refresh(su=True)

    cmds.currentTime(int(startFrame))

    #Get start time
    startTime = datetime.datetime.now()
    averageTime = None
    remainingTime = None

    #endregions

    matchToObjects = []
    for obj in objects:
        matchToObjects.append(connections.getConnectionByName(obj + '.broMatchTo', multi=False)[0])

    #matching
    for frame in range(int(startFrame), int(endFrame)):
        if cmds.progressBar(gMainProgressBar, query=True, isCancelled=True):
            message = "Tracking interrupted. Time spent:"
            messageColor = "#FF0000"
            break
        cmds.currentTime(int(frame))
        if frame > int(startFrame):
            if not reverse:
                matchObjects(objects, keyframe=True)
            else:
                matchObjects(matchToObjects, keyframe=True)
        else:
            pass


        averageTime = (datetime.datetime.now() - startTime) / (int(frame) + 1)
        remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(frame) + 1))

        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                                     status="Tracking... Time remaining: " + str(remainingTime))

    #region P O S T

    if dontRefresh:
        cmds.refresh(su=False)

    cmds.playbackOptions(ps=old_ps), cmds.playbackOptions(mps=old_mps)  # restore playback settings
    cmds.autoKeyframe(st=oldAutoKeyframe)
    cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)
    cmds.playbackOptions(min=startFrame)
    completionTime = datetime.datetime.now() - startTime
    log.inViewLog(messageColor, message, completionTime)
    #endregion



#endregion

#region Button functions

def rbdAdd():
    addRBDToSelection(cmds.ls(sl=1))

def rbdRemove():
    removeRBDFromControls(cmds.ls(sl=1,l=1))

def rbdConnect():
    selection = cmds.ls(sl=1, long=1)
    connectCTRLToRBD(selection[0], selection[1])

def rbdRemoveConnection():
    removeRBDConnectionFromCTRLs(cmds.ls(sl=1,l=1))

def rbdMatchSelectedTo():
    matchObjects(cmds.ls(sl=1, l=1))

def rbdMatchToSelected():
    matchToObjects = []
    controls = cmds.ls(sl=1, l=1)

    for ctrl in controls:
        rbdObj = connections.getConnectionByName(ctrl + '.broMatchTo', multi=False)[0]
        matchToObjects.append(rbdObj)

    matchObjects(matchToObjects, keyframe=True)


@utils.try_except
def rbdSetKinematic(objects=None):
    if objects == None:
        objects = cmds.ls(sl=1, l=1)

    for obj in objects:
        bulletShape = None
        if cmds.objectType(obj) == "bulletRigidBodyShape":
            bulletShape = obj
        else:
            shapes = cmds.listRelatives(obj, s=True)
            for shape in shapes:
                if cmds.objectType(shape) == "bulletRigidBodyShape":
                    bulletShape = shape

        if bulletShape != None:
            cmds.setAttr(bulletShape+'.bodyType', 1)
            cmds.setKeyframe(bulletShape, at='bodyType')

        else:
            log.log('warning', "Could not find RigidBodyShape.")

@utils.try_except
def rbdSetDynamic(objects=None):
    if objects == None:
        objects = cmds.ls(sl=1, l=1)

    for obj in objects:
        bulletShape = None
        if cmds.objectType(obj) == "bulletRigidBodyShape":
            bulletShape = obj
        else:
            shapes = cmds.listRelatives(obj, s=True)
            for shape in shapes:
                if cmds.objectType(shape) == "bulletRigidBodyShape":
                    bulletShape = shape

        if bulletShape != None:
            cmds.setAttr(bulletShape+'.bodyType', 2)
            cmds.setKeyframe(bulletShape, at='bodyType')

        else:
            log.log('warning', "Could not find RigidBodyShape.")


def rbdSelectRBDMesh():
    selection = cmds.ls(sl=True)
    cmds.select (cl=True)

    for ctrl in selection:
        matchToObj = connections.getConnectionByName(ctrl + '.broMatchTo', multi=False)[0]
        cmds.select (matchToObj, add=True)

def rbdSelectRBDShape():

    selection = cmds.ls(sl=True)
    cmds.select (cl=True)

    for ctrl in selection:
        matchToObj = connections.getConnectionByName(ctrl + '.broMatchTo', multi=False)[0]
        shape = None
        shapes = cmds.listRelatives(matchToObj, shapes=True)
        for potentialShape in shapes:
            if cmds.objectType(potentialShape) == 'bulletRigidBodyShape':
                shape = potentialShape

        if shape != None:
            cmds.select (shape, add=True)
        else:
            log.log('warning', "Could not find bulletRigidBodyShape for", matchToObj)

def rbdSetupConstraint():
    selection = cmds.ls(sl=1, l=1)
    parent = selection[len(selection)-1]
    selection.remove(parent)
    children = selection

    for child in children:
        constraintObjects (parent, child, scale=100)

def rbdResetCompound():

    startFrame = cmds.getAttr ('bulletSolver1.startTime')
    currentFrame = cmds.currentTime(q=1)

    if currentFrame != startFrame:
        log.inViewLog("#FF0000", "You must be in the first simulation frame to refresh shapes.")

    else:
        selection = cmds.ls(sl=1, l=1)

        for obj in selection:
            shape = None
            shapes = cmds.listRelatives(obj, s=1)
            for potentialShape in shapes:
                if cmds.objectType(potentialShape) == 'bulletRigidBodyShape':
                    shape = potentialShape

            if shape != None:
                cmds.setAttr(shape+'.colliderShapeType', 1)
                cmds.refresh()
                cmds.setAttr(shape+'.colliderShapeType', 8)

# endregion
