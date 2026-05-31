"""

## Event handling brainstorm

# Usecase: when selection changes, handlers need to update to this.

Handlers are interested in same data (what's the selected mesh, are layers available, etc). When even is received
by handler, all data to handle the even is there. Data is mostly pre-fetched (assuming that someone will eventually
need it anyway), but for some events lazy-loading might be needed.

# Usecase: event handlers need to respond only when data actually changes (state goes from "layers available"
to "layers unavailable")

Even handlers store that information on heir side. Signal has no way of knowing prevous state of the handler.

# Usecase: event can be fired as a source of multiple other events (layer availability changed: could come from
data transformation or undo/redo event)

Events have their own hierarchy, "layers availability changed" signal stores information tools_about it's previous state
and emits if state changes.




## Events hierarchy complexity

Whenever possible, keep event tree localized in single place for easier refactoring.
"""
from ngSkinTools2.api import target_info
from ngSkinTools2.python_compatibility import Object
from maya import cmds
from ngSkinTools2 import api
from ngSkinTools2.log import getLogger
from ngSkinTools2 import cleanup, signal
from ngSkinTools2.signal import Signal

log = getLogger("events")


class ConditionalEmit(Object):
    def __init__(self, name, check):
        self.signal = Signal(name)
        self.check = check

    def emitIfChanged(self):
        if self.check():
            self.signal.emit()

    def addHandler(self, handler, **kwargs):
        self.signal.addHandler(handler, **kwargs)

    def removeHandler(self, handler):
        self.signal.removeHandler(handler)


def scriptJob(*args, **kwargs):
    """
    a proxy on top of cmds.scriptJob for scriptJob creation;
    will register an automatic cleanup procedure to kill the job
    """
    job = cmds.scriptJob(*args, **kwargs)

    def kill():
        # noinspection PyBroadException
        try:
            cmds.scriptJob(kill=job)
        except:
            # should be no issue if we cannot kill the job anymore (e.g., killing from the
            # import traceback; traceback.print_exc()
            pass

    cleanup.registerCleanupHandler(kill)

    return job


class Events(Object):
    """
    root tree of events signaling each other
    """

    def __init__(self, state):
        """

        :type state: ngSkinTools2.ui.session.State
        """

        def scriptJobSignal(name):
            result = Signal(name + "_scriptJob")
            scriptJob(e=[name, result.emit])
            return result

        self.mayaDeleteAll = scriptJobSignal('deleteAll')

        self.nodeSelectionChanged = scriptJobSignal('SelectionChanged')

        self.undoExecuted = scriptJobSignal('Undo')
        self.redoExecuted = scriptJobSignal('Redo')
        self.undoRedoExecuted = Signal('undoRedoExecuted')
        self.undoExecuted.addHandler(self.undoRedoExecuted.emit)
        self.redoExecuted.addHandler(self.undoRedoExecuted.emit)

        self.toolChanged = scriptJobSignal('ToolChanged')
        self.quitApplication = scriptJobSignal('quitApplication')

        self.tool_settings_changed = Signal('tool_settings_changed')

        def checkTargetChanged():
            """
            verify that currently selected mesh is changed, and this means a change in LayersManager.
            """
            selection = cmds.ls(selection=True, objectsOnly=True) or []
            selectedSkinCluster = None if not selection else target_info.get_related_skin_cluster(selection[-1])

            if selectedSkinCluster is not None:
                layersAvailable = api.get_layers_enabled(selectedSkinCluster)
            else:
                layersAvailable = False

            if state.selectedSkinCluster == selectedSkinCluster and state.layersAvailable == layersAvailable:
                return False

            state.selection = selection
            state.set_skin_cluster(selectedSkinCluster)
            state.skin_cluster_dq_channel_used = False if selectedSkinCluster is None else cmds.getAttr(selectedSkinCluster + ".skinningMethod") == 2
            state.layersAvailable = layersAvailable
            state.all_layers = []  # reset when target has actually changed
            log.info("target changed, layers available: %s", state.layersAvailable)

            return True

        self.targetChanged = event = ConditionalEmit("targetChanged", checkTargetChanged)

        for source in [self.mayaDeleteAll, self.undoRedoExecuted, self.nodeSelectionChanged]:
            source.addHandler(event.emitIfChanged)

        def checkLayersListChanged():
            state.all_layers = [] if not state.layersAvailable else api.Layers(state.selectedSkinCluster).list()
            return True

        self.layerListChanged = ConditionalEmit("layerListChanged", checkLayersListChanged)
        signal.on(self.targetChanged, self.undoRedoExecuted)(self.layerListChanged.emitIfChanged)

        def checkCurrentLayerChanged():
            # current layer changed if current mesh changed,
            # or id within the mesh changed
            currentLayer = None
            if state.selectedSkinCluster is not None and state.layersAvailable:
                currentLayer = api.Layers(state.selectedSkinCluster).current_layer()

            if state.selectedSkinCluster == state.currentLayer.selectedSkinCluster and state.currentLayer.layer == currentLayer:
                return False

            state.currentLayer.selectedSkinCluster = state.selectedSkinCluster
            state.currentLayer.layer = currentLayer
            return True

        self.currentLayerChanged = event = ConditionalEmit("currentLayerChanged", checkCurrentLayerChanged)
        self.targetChanged.addHandler(event.emitIfChanged)
        self.undoRedoExecuted.addHandler(event.emitIfChanged)

        def checkCurrentPaintTargetChanged():
            skinCluster = state.selectedSkinCluster
            newLayer = state.currentLayer.layer
            newTarget = None
            if newLayer is not None:
                newTarget = newLayer.paint_target

            log.info("checking current influence changed to %s %s %s", skinCluster, newLayer, newTarget)
            if (
                skinCluster == state.currentInfluence.skinCluster
                and newLayer == state.currentInfluence.layer
                and newTarget == state.currentInfluence.target
            ):
                return False

            log.info("current influence changed to %s %s %s", skinCluster, newLayer, newTarget)

            state.currentInfluence.skinCluster = skinCluster
            state.currentInfluence.layer = newLayer
            state.currentInfluence.target = newTarget
            return True

        self.currentInfluenceChanged = event = ConditionalEmit("currentInfluenceChanged", checkCurrentPaintTargetChanged)
        self.currentLayerChanged.addHandler(event.emitIfChanged)

        self.influencesListUpdated = Signal("influencesListUpdated")

        # now get initial state
        self.targetChanged.emitIfChanged()
