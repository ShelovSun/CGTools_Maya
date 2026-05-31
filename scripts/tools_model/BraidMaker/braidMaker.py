
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as MPx
import sys

import braidMakerSource as scf


def initializePlugin(mobject):
	mplugin = MPx.MFnPlugin(mobject, "Abhishek Karmakar", "2.0", "Any")
	try:
		mplugin.registerCommand( scf.kPluginCmdName, scf.cmdCreator )
	except:
		sys.stderr.write( "Failed to register command: %s\n" % scf.kPluginCmdName )
		raise

def uninitializePlugin(mobject):
	mplugin = MPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterCommand( scf.kPluginCmdName )
	except:
		sys.stderr.write( "Failed to unregister command: %s\n" % scf.kPluginCmdName )
		raise