__author__ = 'Michael'

import BroDynamics
import datetime
import os
import maya.cmds as cmds

realPath = os.path.dirname(os.path.realpath(__file__))

def log(type='', *args):
    time = str(datetime.datetime.now())
    prefix = type*3
    text = ''
    for item in args:
        text += ' '
        text += str(item)
    print(prefix, time+":", text)

def checkRunTimeCmds():
    '''
    Ensure the RedRuntime Command plugin is loaded.
    '''
    try:
        if not cmds.pluginInfo('SnapRuntime.py', query=True, loaded=True):
            try:
                cmds.loadPlugin('SnapRuntime.py')
            except:
                raise StandardError('SnapRuntime Plug-in could not be loaded')
    except:
        raise StandardError('SnapRuntime Plug-in not found')


def addPluginPath(path=None):
    '''
    Make sure the plugin path has been added. If run as a module
    this will have already been added
    '''
    if not path:
        path=os.path.join(realPath, 'plug-ins')
    plugPaths=os.environ.get('MAYA_PLUG_IN_PATH')
    if os.path.exists(path) and not path in plugPaths:
        log('Adding BroDynamics Plug-ins to Plugin Paths : %s' % path)
        os.environ['MAYA_PLUG_IN_PATH']+='%s%s' % (os.pathsep,path)
    else:
        log('BroDynamics Plug-in Path already setup')

print("\n=====================================================\n")
log ("", "Initializing BroTools...")
addPluginPath()
checkRunTimeCmds()

