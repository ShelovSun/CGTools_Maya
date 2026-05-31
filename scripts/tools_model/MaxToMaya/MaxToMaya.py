import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx

import maya.cmds as cmds
import pymel.core as pm
import os
import xml.etree.ElementTree as ET
import maya.mel as mel
try:
    from importlib import reload
except:
    print("importlib skip")
commandName = 'maxtomaya'

class maxtomayaClass( OpenMayaMPx.MPxCommand ):
    
    def __init__(self):
        ''' Constructor. '''
        OpenMayaMPx.MPxCommand.__init__(self)
    
    def doIt(self, args):
        ''' Command execution. '''     
        import sys
        import os
        from os import path
        import maya.mel as mel
        import maya.cmds as cmds
        scriptPath = ""
        scriptPathPyc = ""
        sysVer = sys.version_info #Get Python Ver
        if sysVer.major == 2:
            scriptPath = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/m2m.py")
            scriptPathPyc = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/m2m.pyc")
        if sysVer.major == 3:
            scriptPath = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/m2m.py")
            scriptPathPyc = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files/m2m_P3.pyc")
        if os.path.exists(scriptPathPyc): scriptPath = scriptPathPyc
        if os.path.exists(scriptPath): scriptPath = scriptPath
        def psource(module):
            file = os.path.basename( module )
            dir = os.path.dirname( module )
            toks = file.split( '.' )
            modname = toks[0]
            if( os.path.exists( dir ) ):
                paths = sys.path
                pathfound = 0
                for path in paths:
                    if(dir == path):
                        pathfound = 1
                if not pathfound:
                    sys.path.append( dir )
            exec(('import ' + modname), globals())

            # try:
            #     importlib.reload(m2m)
            # except:
            #     print("importlib reload - start")
            
            sysVer = sys.version_info #Get Python Ver
            if sysVer.major == 2:
                import m2m
                reload(m2m)
            if sysVer.major == 3:
                import m2m_P3
                reload(m2m_P3)

            # m2m.maxtomayaStartDialog()

            # try:
            #     m2m.maxtomayaStartDialog()
            # except:
            #     print("skip m2m...maxtomayaStart")
            return modname
        def maxtomayastart():
            # When you import a file you must give it the full path
            print("maxtomayaRun: " + scriptPath)
            psource( scriptPath )
        print("executed")
        maxtomayastart()
        #-------------------------------------------------------------------------------------

def cmdCreator():
    ''' Create an instance of our command. '''
    return OpenMayaMPx.asMPxPtr( maxtomayaClass() )

def initializePlugin( mobject ):
    import maya.mel as mel
    import maya.cmds as cmds
    import sys
    import os
    from os import path
    from sys import path as sysPath

    #--------------------- ADD ITEMS IN MENU --------------------------
    scriptPath = os.path.expanduser("~/maya/plug-ins/MaxToMaya_Files")
    sysPath.append(scriptPath)
    import m2mmenu
    m2mmenu.start()
    #--------------------- ADD ITEMS IN MENU // END --------------------------
    
    ''' Initialize the plug-in when Maya loads it. '''
    mplugin = OpenMayaMPx.MFnPlugin( mobject, "3DtoAll", "2.92" )
    try:
        mplugin.registerCommand( commandName, cmdCreator )
    except:
        sys.stderr.write( 'Failed to register command: ' + commandName )

def uninitializePlugin( mobject ):
    ''' Uninitialize the plug-in when Maya un-loads it. '''
    print("Unloaded!")
    import m2mmenu
    m2mmenu.remove() 
    mplugin = OpenMayaMPx.MFnPlugin( mobject )
    try:
        mplugin.deregisterCommand( commandName )
    except:
        sys.stderr.write( 'Failed to unregister command: ' + commandName )