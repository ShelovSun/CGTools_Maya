'''
import datetime

import maya.cmds as cmds
import maya.mel as mel

import log
import utils
import BroSimulationCore as bsc


@utils.try_except
def createLiveNParticles(objects, skipFrames=1, goalWeight=0.9, goalSmoothness=3, dontRefresh=False, collide=True,
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
    log.log(">", "Creating live in single object mode. ", goalWeight, goalSmoothness, objects)

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
        obj, partName = bsc.createNParticle(obj, '_part_' + str(i), goalWeight, goalSmoothness, collide=collide,
                                        selfCollide=selfCollide, collideWidthScale=collideWidthScale, bounce=bounce,
                                        friction=friction, stickiness=stickiness, drag=drag, damp=damp)
        particles.append(partName)
        averageTime = (datetime.datetime.now() - startTime) / (int(i) + 1)
        remainingTime = (averageTime * int(frameCount)) - (averageTime * (int(i) + 1))
        cmds.progressBar(gMainProgressBar, edit=True, step=1,
                         status="Generating particles... Time remaining: " + str(remainingTime))

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
                 nucleusOldStartFrame)  # in case nucleus1 existed before simulation, return it's start frame to original.
    for nukeNode in nucleusNodes:
        print nukeNode, nucleusNodes
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
                bsc.setWSPosition(obj, targetPos)
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

'''