import itertools

from maya import cmds

from ngSkinTools2.api import PaintTool
from ngSkinTools2.api.session import Session
from ngSkinTools2.decorators import undoable
from ngSkinTools2.mllInterface import MllInterface


def asList(arg):
    return [] if arg is None else arg


customNodeTypes = ['ngst2MeshDisplay', 'ngst2SkinLayerData']


def listCustomNodes():
    """
    list all custom nodes in the scene
    """

    result = []
    for nodeType in customNodeTypes:
        result.extend(asList(cmds.ls(type=nodeType)))
    return result


def listCustomNodesForMesh(mesh=None):
    """
    list custom nodes only related to provided mesh. None means current selection
    """

    skinCluster = MllInterface(mesh=mesh).getTargetInfo()
    if skinCluster is None:
        return []

    # delete any ngSkinTools deformers from the history, and find upstream stuff from given skinCluster.
    hist = asList(cmds.listHistory(skinCluster, future=True, levels=1))
    return [i for i in hist if cmds.nodeType(i) in customNodeTypes]


def listCustomNodesForMeshes(meshes):
    return list(itertools.chain.from_iterable([listCustomNodesForMesh(i) for i in meshes]))


message_scene_noCustomNodes = 'Scene does not contain any custom ngSkinTools nodes.'
message_selection_noCustomNodes = 'Selection does not contain any custom ngSkinTools nodes.'
message_scene_warning = (
    'This command deletes all custom ngSkinTools nodes. Skin weights ' 'will be preserved, but all layer data will be lost. Do you want to continue?'
)
message_selection_warning = (
    'This command deletes custom ngSkinTools nodes for selection. Skin weights '
    'will be preserved, but all layer data will be lost. Do you want to continue?'
)


@undoable
def removeCustomNodes(interactive=False, session=None, meshes=[]):
    """
    Removes custom ngSkinTools2 nodes from the scene or selection.

    :type meshes: list[str]
    :param meshes: list of node names; if empty, operation will be scene-wide.
    :type session: Session
    :param session: optional; if specified, will fire events for current session tools_about changed status of selected mesh
    :type interactive: bool
    :param interactive: if True, user warnings will be emited
    """
    from ngSkinTools2.ui import dialogs

    isSelectionMode = len(meshes) > 0

    customNodes = listCustomNodes() if not isSelectionMode else listCustomNodesForMeshes(meshes)

    if not customNodes:
        if interactive:
            dialogs.info(message_selection_noCustomNodes if isSelectionMode else message_scene_noCustomNodes)
        return

    deleteConfirmed = True
    if interactive:
        deleteConfirmed = dialogs.yesNo(message_selection_warning if isSelectionMode else message_scene_warning)

    if deleteConfirmed:
        cmds.delete(customNodes)

    paint = PaintTool()
    if paint.is_painting():
        # make sure that painting is canceled to restore mesh display etc
        cmds.setToolTo("Move")

    if session is not None:
        session.events.targetChanged.emitIfChanged()


@undoable
def removeCustomNodesFromSelection(interactive=False, session=None):
    selection = cmds.ls(sl=True)
    removeCustomNodes(interactive=interactive, session=session, meshes=asList(selection))
