"""
Maya internals dissection, comments are ours. similar example available in "command|hotkey code", see "Here's an example
of how to create runtimeCommand with  a certain hotkey context"


```

// add new hotkey ctx
//  t: Specifies the context type. It's used together with the other flags such as "currentClient", "addClient",
//     "removeClient" and so on.
//  ac: Associates a client to the given hotkey context type. This flag needs to be used with the flag "type" which
//      specifies the context type.
hotkeyCtx -t "Tool" -ac "sculptMeshCache";

// create new runtime command, associate with created context
runTimeCommand -default true
    -annotation (uiRes("m_defaultRunTimeCommands.kModifySizePressAnnot"))
    -category   ("Other items.Brush Tools")
    -command    ("if ( `contextInfo -ex sculptMeshCacheContext`) sculptMeshCacheCtx -e -adjustSize 1 sculptMeshCacheContext;")
    -hotkeyCtx ("sculptMeshCache")
    SculptMeshActivateBrushSize;

// create named command for the runtime command
nameCommand
    -annotation "Start adjust size"
    -command ("SculptMeshActivateBrushSize")
    SculptMeshActivateBrushSizeNameCommand;

// assign hotkey for name command
hotkey -keyShortcut "b" -name ("SculptMeshActivateBrushSizeNameCommand") -releaseName ("SculptMeshDeactivateBrushSizeNameCommand");
```

"""

from maya import cmds
from ngSkinTools2.api import PaintTool
from ngSkinTools2.operations.paint import FloodAction
from ngSkinTools2.python_compatibility import is_string
from ngSkinTools2.ui.action import do_action_hotkey

hotkeySetName = 'ngSkinTools2'
context = 'ngst2PaintContext'


def uninstall_hotkeys():
    if cmds.hotkeySet(hotkeySetName, q=True, exists=True):
        cmds.hotkeySet(hotkeySetName, e=True, delete=True)


def setupNamedCommands():
    # "default" mode will force a read-only behavior for runTimCommands
    # only turn this on for production mode
    import ngSkinTools2

    useDefaultMode = not ngSkinTools2.DEBUG_MODE

    def addCommand(name, annotation, command):
        if not is_string(command):
            command = functionLink(command)

        runtimeCommandName = "ngst2" + name

        # delete (if exists) and recreate runtime command
        if not useDefaultMode and cmds.runTimeCommand(runtimeCommandName, q=True, exists=True):
            cmds.runTimeCommand(runtimeCommandName, e=True, delete=True)

        # we're only deleting commands if we're in default mode (commands can't be edited once they're created)
        if not cmds.runTimeCommand(runtimeCommandName, q=True, exists=True):
            # update command contents - we reserve the right to update annotation and command contents
            cmds.runTimeCommand(
                runtimeCommandName,
                category="Other items.ngSkinTools2",
                hotkeyCtx=context,
                default=useDefaultMode,
                annotation=annotation,
                command=command,
                commandLanguage="python",
            )

            nc = cmds.nameCommand(
                runtimeCommandName + "NameCommand",
                annotation=annotation + "-",
                sourceType="python",
                default=useDefaultMode,
                command=runtimeCommandName,
            )

    def addToggle(name, annotation, commandOn, commandOff):
        addCommand(name + 'On', annotation=annotation, command=commandOn)
        addCommand(name + 'Off', annotation=annotation + "(release)", command=commandOff)

    def pluginHotkey(**kwargs):
        return "from maya import cmds; cmds.ngst2Hotkey(**%r)" % kwargs

    addToggle(
        'BrushSize',
        annotation='Toggle brush size mode',
        commandOn=pluginHotkey(paintContextBrushSize=True),
        commandOff=pluginHotkey(paintContextBrushSize=False),
    )

    addCommand('ToggleHelp', annotation='toggle help', command=pluginHotkey(paintContextToggleHelp=True))
    addCommand('ViewFitInfluence', annotation='fit influence in view', command=pluginHotkey(paintContextViewFit=True))
    addToggle(
        'SampleInfluence',
        annotation='Sample influence',
        commandOn=pluginHotkey(paintContextSampleInfluence=True),
        commandOff=pluginHotkey(paintContextSampleInfluence=False),
    )

    addCommand("SetBrushIntensity", annotation="set brush intensity", command=selectPaintBrushIntensity)

    addCommand("PaintFlood", annotation="apply current brush to all vertices", command=floodPaintTool)


def defineHotkeys():
    setupNamedCommands()

    def nc(nameCommandShortName):
        return "ngst2" + nameCommandShortName + "NameCommand"

    # cmds.hotkey(k="b", name=nc("BrushSizeOn"), releaseName=nc("BrushSizeOff"))
    cmds.hotkey(keyShortcut="b", ctxClient=context, name="ngst2BrushSizeOnNameCommand", releaseName="ngst2BrushSizeOffNameCommand")
    cmds.hotkey(keyShortcut="i", name=nc("SetBrushIntensity"))
    cmds.hotkey(keyShortcut="f", ctrlModifier=True, name=nc("PaintFlood"))
    cmds.hotkey(keyShortcut="f", name=nc("ViewFitInfluence"))
    cmds.hotkey(keyShortcut="h", name=nc("ToggleHelp"))

    cmds.hotkey(keyShortcut="s", name=nc("SampleInfluenceOn"), releaseName=nc("SampleInfluenceOff"))


def installHotkeys():
    uninstall_hotkeys()

    prevHotkeySet = cmds.hotkeySet(q=True, current=True)
    try:
        if cmds.hotkeySet(hotkeySetName, q=True, exists=True):
            cmds.hotkeySet(hotkeySetName, e=True, current=True)
        else:
            cmds.hotkeySet(hotkeySetName, current=True)

        cmds.hotkeyCtx(addClient=context, type='Tool')

        defineHotkeys()
    finally:
        cmds.hotkeySet(prevHotkeySet, e=True, current=True)


def functionLink(fun):
    return "import {module}; {module}.{fn}()".format(module=fun.__module__, fn=fun.__name__)


def selectPaintBrushIntensity():
    from ngSkinTools2.ui.brush_settings_popup import brush_settings_popup

    brush_settings_popup(PaintTool())


def floodPaintTool():
    do_action_hotkey(FloodAction)
