import pymel.core as pm
from ngSkinTools2 import api, signal
from ngSkinTools2.decorators import undoable, preserveSelection
from ngSkinTools2.log import getLogger
from ngSkinTools2.observableValue import ObservableValue
from ngSkinTools2.operations import layers
from ngSkinTools2.python_compatibility import Object
from ngSkinTools2.ui import dialogs
from ngSkinTools2.ui.session import Session

logger = getLogger("operation/tools")


def __create_tool_action__(parent, session, action_name, action_tooltip, exec_handler):
    """
    :type session: Session
    """

    from ngSkinTools2.ui import actions

    def execute():
        if not session.active():
            return

        exec_handler()

    result = actions.define_action(parent, action_name, callback=execute, tooltip=action_tooltip)

    @signal.on(session.events.targetChanged, session.events.currentLayerChanged)
    def update_state():
        result.setEnabled(session.state.layersAvailable and session.state.currentLayer.layer is not None)

    return result


class ClosestJointOptions(Object):
    def __init__(self):
        self.create_new_layer = ObservableValue(False)
        self.all_influences = ObservableValue(True)


def create_action__from_closest_joint(parent, session):
    options = ClosestJointOptions()

    def exec_handler():
        layer = session.state.currentLayer.layer
        influences = None
        if not options.all_influences():
            influences = list(session.context.get_selected_influences())
            if not influences:
                dialogs.info("Select one or more influences in Influences list")
                return

        if options.create_new_layer():
            layer = layers.addLayer()

        api.assign_from_closest_joint(
            session.state.selectedSkinCluster,
            layer,
            influences=influences,
        )
        session.events.currentLayerChanged.emitIfChanged()
        session.events.influencesListUpdated.emit()

        if layer.paint_target is None:
            used_influences = layer.get_used_influences()
            if used_influences:
                layer.paint_target = min(used_influences)

    return (
        __create_tool_action__(
            parent,
            session,
            action_name=u"Assign From Closest Joint",
            action_tooltip="Assign 1.0 weight for closest influence per each vertex in selected layer",
            exec_handler=exec_handler,
        ),
        options,
    )


class UnifyWeightsOptions(Object):
    overall_effect = ObservableValue(1.0)
    single_cluster_mode = ObservableValue(False)


def create_action__unify_weights(parent, session):
    options = UnifyWeightsOptions()

    def exec_handler():
        api.unify_weights(
            session.state.selectedSkinCluster,
            session.state.currentLayer.layer,
            overall_effect=options.overall_effect(),
            single_cluster_mode=options.single_cluster_mode(),
        )

    return (
        __create_tool_action__(
            parent,
            session,
            action_name=u"Unify Weights",
            action_tooltip="For selected vertices, make verts the same for all verts",
            exec_handler=exec_handler,
        ),
        options,
    )


def create_action__merge_layers(parent, session):
    """
    :param parent: UI parent for this action
    :type session: Session
    """

    def exec_handler():
        api.merge_layers(layers=session.context.selected_layers(default=[]))
        session.events.layerListChanged.emitIfChanged()
        session.events.currentLayerChanged.emitIfChanged()

    return __create_tool_action__(
        parent,
        session,
        action_name=u"Merge",
        action_tooltip="Merge contents of this layer into underlying layer. Pre-effects weights will be used for this",
        exec_handler=exec_handler,
    )


def create_action__duplicate_layer(parent, session):
    """
    :param parent: UI parent for this action
    :type session: Session
    """

    @undoable
    def exec_handler():
        with api.suspend_updates(session.state.selectedSkinCluster):
            for source in session.context.selected_layers(default=[]):
                api.duplicate_layer(layer=source)

        session.events.layerListChanged.emitIfChanged()
        session.events.currentLayerChanged.emitIfChanged()

    return __create_tool_action__(
        parent,
        session,
        action_name=u"Duplicate",
        action_tooltip="Duplicate selected layer(s)",
        exec_handler=exec_handler,
    )


def create_action__fill_transparency(parent, session):
    """
    :param parent: UI parent for this action
    :type session: Session
    """

    @undoable
    def exec_handler():
        with api.suspend_updates(session.state.selectedSkinCluster):
            for source in session.context.selected_layers(default=[]):
                api.fill_transparency(layer=source)

    return __create_tool_action__(
        parent,
        session,
        action_name=u"Fill Transparency",
        action_tooltip="All transparent vertices in the selected layer(s) receive weights from their closest non-empty neighbour vertex",
        exec_handler=exec_handler,
    )


def create_action__copy_component_weights(parent, session):
    """
    :param parent: UI parent for this action
    :type session: Session
    """

    def exec_handler():
        for source in session.context.selected_layers(default=[]):
            api.copy_component_weights(layer=source)

    return __create_tool_action__(
        parent,
        session,
        action_name=u"Copy Component Weights",
        action_tooltip="Store components weights in memory for further component-based paste actions",
        exec_handler=exec_handler,
    )


def create_action__paste_average_component_weight(parent, session):
    """
    :param parent: UI parent for this action
    :type session: Session
    """

    def exec_handler():
        for l in session.context.selected_layers(default=[]):
            api.paste_average_component_weights(layer=l)

    return __create_tool_action__(
        parent,
        session,
        action_name=u"Paste Average Component Weight",
        action_tooltip="Compute average of copied component weights and set that value to currently selected components",
        exec_handler=exec_handler,
    )


def create_action__add_influences(parent, session):
    """
    :param parent: UI parent for this action
    :type session: Session
    """

    def exec_handler():
        selection = pm.ls(sl=True)
        if len(selection) < 2:
            logger.info("invalid selection: %s", selection)
            return
        api.add_influences(selection[:-1], selection[-1])
        pm.select(selection[-1])
        session.events.influencesListUpdated.emit()

    return __create_tool_action__(
        parent,
        session,
        action_name=u"Add Influences",
        action_tooltip="Add selected influences to current skin cluster.",
        exec_handler=exec_handler,
    )
