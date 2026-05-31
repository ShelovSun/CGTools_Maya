#!/usr/bin/env python
"""
connections.py - BroTools module containing procedures for handling meta-connections (message-connections) between Maya
nodes. This includes connecting and acquiring connection data.
"""


import maya.cmds as cmds

import log
import utils

__author__ = "Mikhail Davydov"
__copyright__ = "Copyright 2016"
__version__ = "1.0.1"
__email__ = "nixesvfx@gmail.com"


@utils.try_except
def metaConnect(obj, toObj, ln = 'none', multi = True, force=False):
    """
    Connect two objects together using 'message' attribute.
    Args:
        fromObj(str): Object to connect FROM
        toObj(str): Object to connect TO
        ln(str): Name of connection. If left empty or 'none' - turns into fromObj name.
        multi(bool): if true - multiple connections can be made to one attribute.
    """
    if ln == 'none':
        split = obj.split("|")
        ln = split[len(split)-1]

    if not force:
        if cmds.objExists(toObj+'.'+ln):
            cmds.error("metaConnect {0}: Connection already exists.".format(__version__))

    if force:
        if cmds.objExists(toObj+'.'+ln):
            cmds.deleteAttr(toObj, at=ln)

    selection = cmds.ls(sl=True, l=True)
    if cmds.objExists(toObj+'.'+ln) == False:
        #print "No attr, creating"
        cmds.select (toObj, r=True)
        cmds.addAttr (ln=ln, at='message', multi=multi)
    if multi == False:
        #print "multi false"
        cmds.connectAttr (obj+'.message', toObj+'.'+ln)
    elif multi == True:
        connections = cmds.getAttr (toObj+'.'+ln, mi=True)
        #print "CONNECTIONS", connections
        if connections == None:
            newID = '['+str(0)+']'
        else:
            newID = '['+str(len(connections))+']'
        cmds.connectAttr (obj+'.message', toObj+'.'+ln+newID)
    log.log (">", obj, "connected to", toObj)
    cmds.select(selection, r=True)

@utils.try_except
def metaConnectMultiple (ln='none'):
    """
    Connect multiple objects together, using metaConnect. If no name provided - will create
    individual single connections, named after object names. If name is provided - will create a single multi-connection.
    Args:
        ln (str): Name of connection


    """
    print ''
    objects = cmds.ls(sl=True, l=True)
    if len(objects) < 2:
        cmds.error("At least 2 objects must be selected.")
    target = objects.pop(len(objects)-1)
    if ln == 'none':
        multi = False
    else:
        multi = True
    log.log ('>', "Connecting", objects, "to", target)
    for object in objects:
        metaConnect(object, target, ln, multi)

@utils.try_except
def getConnectionByName (n='', multi=True):
    """
    Get metaConnections (messageConnections) of a given object.attribute.
    Args:
        n: "object.attribue" string to get connections from
        multi: if an attribute has multiple connections use this

    Returns: Array of [objects]

    """
    if n == '':
        cmds.error ("No connection name specified for getConnectionByName function.")

    if cmds.objExists (n):
        if multi:
            connections = cmds.getAttr (n, mi=1)
            objects = []
            for i in range(0, len(connections)):
                objects.append(cmds.connectionInfo(n+'[{0}]'.format(i), sourceFromDestination=True).replace('.message', ''))
        else:
            objects = [cmds.connectionInfo(n, sourceFromDestination=True).replace('.message', '')]

        return objects
    else:
        cmds.error ("No such connection: "+str(n))