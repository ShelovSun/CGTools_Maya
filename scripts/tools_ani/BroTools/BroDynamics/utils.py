#!/usr/bin/env python


"""
BroDynamics\utils.py - Utilities module. In BroDynamics used only for error handling. BroRig and other major folders
have their own utils.py files, which all include error handling and other usefull often-used functions.
"""
import sys
import traceback

import maya.mel as mel
from maya import cmds as cmds

import log
import settings


__author__ = "Mikhail Davydov"
__copyright__ = "Copyright 2016"
__version__ = "BroDynamics 1.0.0"
__email__ = "nixesvfx@gmail.com"

class BroRig_Error(Exception):
    pass


def try_except(fn):
    """
    BroRig exception wrapper. Use @try_except above the function to wrap it.
    Args:
        fn: function to wrap

    Returns:
        wrapped: wrapped function
    """

    def wrapped(*args, **kwargs):
        try:
            cmds.undoInfo(openChunk=True)
            result = fn(*args, **kwargs)
            cmds.undoInfo(closeChunk=True)
            return result
        except Exception as e:
            cmds.undoInfo(closeChunk=True)
            gMainProgressBar = mel.eval('$tmp = $gMainProgressBar')
            cmds.progressBar(gMainProgressBar, edit=True, endProgress=True)

            et, ei, tb = sys.exc_info()
            print(settings.errorText, '\n')
            print("ERROR IN:", fn.__name__, "Function.")
            print(e, "\n")
            print(traceback.print_exc(), '\n')
            print("==================  ==HELP======================")
            print(fn.__doc__, '\n')
            print("====================ERROR=====================")
            cmds.inViewMessage(amg='<span style=\"color:#F05A5A;\">Error: </span>' + str(
                e) + ' <span style=\"color:#FAA300;\">More info in script editor.</span>', pos='topCenter', fade=True,
                               fst=2000, dk=True)
            raise BroRig_Error(BroRig_Error(e)).with_traceback(tb)

    return wrapped


def setAttrsFromDict(obj, settings):
    """
    Args:
        RBDShape: Bullet RBD Shape
        settings: DICT attribute:value
    """
    for attr, value in settings.items():
        try:
            cmds.setAttr(obj+'.'+attr, value)
        except Exception as e:
            log.log("!", "Unable to set attr:", attr, value, " Error:", e)



def snapTransform(child, parent, t=True, r=False, offset=[]):
    '''
    Just an alias to matchTransform, because I sometimes forget that I'm using match instead of snap... o.o
    Returns:

    '''
    matchTransform(child, parent, t, r, offset)


@try_except
def matchTransform(child, parent, t=True, r=False, offset=[], forcexform=False, useRotatePivot=False):
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
    if cmds.pluginInfo('SnapRuntime.py', query=True, loaded=True and not forcexform):
        cmds.SnapTransforms(source=parent, destination=child, snapTranslates=t, snapRotates=r)

    else:
        if not forcexform:
            log.log("!", "SnapRuntime.py plugin is not loaded. Using cmds.xform to match transforms, but this may result in incorrect matching.")

        if t:
            if useRotatePivot:
                cmds.xform(child, ws=True, t=cmds.xform(parent, q=True, ws=True, rp=True))
            else:
                cmds.xform(child, ws=True, t=cmds.xform(parent, q=True, ws=True, t=True))
        if r:
            cmds.xform(child, ws=True, ro=cmds.xform(parent, q=True, ws=True, ro=True))
            cmds.xform(child, ws=True, rp=cmds.xform(parent, q=True, ws=True, rp=True))

    if len(offset)>0:
        cmds.xform(child, r=1, ro=offset[1], t=offset[0])


def snap(nodes=None, snapTranslates=True, snapRotates=True, timeEnabled=False):
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
        cmds.SnapTransforms(source=nodes[0], destination=node, snapTranslates=snapTranslates, snapRotates=snapRotates, timeEnabled=timeEnabled)

import uuid


def randomHash(length=6):
    return str(uuid.uuid4().hex[:length].upper())
