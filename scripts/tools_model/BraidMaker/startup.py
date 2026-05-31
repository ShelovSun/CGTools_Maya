import sys,os
import maya.mel as mel,maya.cmds as cmds



def braidMaker():
    modScriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
    mel_script = ('$s = `getenv "MAYA_PLUG_IN_PATH" `;\n        $s = $s + ";{0}";\n        putenv "MAYA_PLUG_IN_PATH" $s').format(modScriptsPath)
    mel.eval(mel_script)
    try:
        if not cmds.pluginInfo('braidMaker', q=1, loaded=1):
            cmds.loadPlugin('braidMaker')
        cmds.braidMaker()
    except:
        cmds.warning('Can not load braidMaker!')