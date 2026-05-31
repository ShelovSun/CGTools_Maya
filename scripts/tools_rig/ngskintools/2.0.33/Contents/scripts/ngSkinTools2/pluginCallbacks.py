"""
these are methods that are called by plugin when corresponding events happen
"""
from ngSkinTools2.log import getLogger
from ngSkinTools2 import api

from ngSkinTools2.ui.session import session

log = getLogger("plugin callbacks")


def currentPaintTargetChanged():
    # log.info("current paint target changed")
    if session.active():
        if session.state.currentLayer.layer is not None:
            session.state.currentLayer.layer.reload()
        session.events.currentInfluenceChanged.emitIfChanged()


def tool_settings_changed():
    if session.active():
        session.events.tool_settings_changed.emit()


def paintToolStarted():
    api.paint.tabletEventFilter.install()


def paintToolStopped():
    api.paint.tabletEventFilter.uninstall()


def getStylusIntensity():
    return api.paint.tabletEventFilter.pressure


def initializeInfluencesMirrorMapping(mesh):
    """
    gets called by plugin when influences mirror mapping is not set yet
    :return:
    """
    from ngSkinTools2.api.mirror import Mirror
    Mirror(mesh).recalculate_influences_mapping()


def display_node_created(display_node):
    """
    gets called when display node is created

    :param display_node:
    :return:
    """

    from maya import cmds

    # add node to isolated objects if we're currently in isolated mode
    current_view = cmds.paneLayout('viewPanes', q=True, pane1=True)
    is_isolated = cmds.isolateSelect(current_view, q=True, state=True)
    if is_isolated:
        cmds.isolateSelect(current_view, addDagObject=display_node)
