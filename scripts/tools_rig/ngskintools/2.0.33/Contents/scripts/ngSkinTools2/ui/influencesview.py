import os

from maya import cmds

from ngSkinTools2.api.influenceMapping import InfluenceInfo
from ngSkinTools2.api.target_info import list_influences
from ngSkinTools2.observableValue import ObservableValue
from ngSkinTools2.python_compatibility import Object
import re

from PySide2 import QtWidgets, QtCore, QtGui
from ngSkinTools2 import signal, options
from ngSkinTools2.log import getLogger
from ngSkinTools2.mllInterface import MllInterface
from ngSkinTools2.signal import Signal
from ngSkinTools2.ui import qt
from ngSkinTools2.ui.layout import scale_multiplier

log = getLogger("influencesView")


class InfluenceNameFilter(Object):
    """
    simple helper object to match against filter strings;
    accepts filter as a string, breaks it down into lowercase tokens, and
    matches values in non-case sensitive way

    e.g. filter "leg arm spines" matches "leg", "left_leg",
    "R_arm", but does not match "spine"

    in a  special case of empty filter, returns true for isMatch
    """

    def __init__(self):
        self.matchers = []
        self.changed = Signal("filter changed")
        self.currentFilterString = ""

    def set_filter_string(self, filterString):
        if self.currentFilterString == filterString:
            # avoid emitting change events if there's no change
            return
        self.currentFilterString = filterString

        def createPattern(expression):
            expression = "".join([char for char in expression if char.lower() in "abcdefghijklmnopqrstuvwxyz0123456789_*"])
            expression = expression.replace("*", ".*")
            return re.compile(expression, re.I)

        self.matchers = [createPattern(i.strip()) for i in filterString.split() if i.strip() != '']
        self.changed.emit()
        return self

    def short_name(self, name):
        try:
            return name[name.rindex("|") + 1 :]
        except Exception as err:
            return name

    def is_match(self, value):
        if len(self.matchers) == 0:
            return True

        value = self.short_name(str(value).lower())
        for pattern in self.matchers:
            if pattern.search(value) is not None:
                return True

        return False


class Config(Object):
    def __init__(self):
        self.used_influences_only = options.config.build_observable_value("influencesViewShowUsedInfluencesOnly", False)


def build_used_influences_action(parent, config):
    """
    :type config: Config
    """
    from ngSkinTools2.ui import actions

    @signal.on(config.used_influences_only.changed)
    def update():
        result.setChecked(config.used_influences_only())

    def toggle():
        config.used_influences_only.set(not config.used_influences_only())

    result = actions.define_action(
        parent,
        "Used Influences Only",
        callback=toggle,
        tooltip="If enabled, influences view will only show influences that have weights on current layer",
    )
    result.setCheckable(True)
    update()
    return result


def buildView(parent, actions, session, filter):
    """
    :type actions: ngSkinTools2.ui.actions.Actions
    :param session: ngSkinTools2.ui.session.Session
    :type filter: InfluenceNameFilter
    """

    config = session.state.influencesViewConfig

    icon_joint = QtGui.QIcon(":/joint.svg")
    icon_joint_disabled = qt.image_icon("joint_disabled.png")
    icon_transform = QtGui.QIcon(":/cube.png")
    icon_transform_disabled = qt.image_icon("cube_disabled.png")
    icon_mask = QtGui.QIcon(":/blendColors.svg")
    icon_dq = QtGui.QIcon(":/rotate_M.png")

    id_role = QtCore.Qt.UserRole + 1
    item_size_hint = QtCore.QSize(25 * scale_multiplier, 25 * scale_multiplier)

    def get_item_id(item):
        if item is None:
            return None
        return item.data(0, id_role)

    tree_items = {}

    def shorten_infl_name(name):
        try:
            return cmds.ls(name)[0]
        except:
            return name

    def build_items(view, items, layer):
        # type: (QtWidgets.QTreeWidget, list[InfluenceInfo], ngSkinTools2.api.layers.Layer) -> None

        used = set([] if layer is None else (layer.get_used_influences() or []))
        for i in items:
            i.used = i.logicalIndex in used

        if config.used_influences_only() and layer is not None:
            items = [i for i in items if i.used]

        log.info("rebuilding influences items")

        def get_icon(influence, is_joint):
            if influence.used:
                return icon_joint if is_joint else icon_transform
            return icon_joint_disabled if is_joint else icon_transform_disabled

        def wanted_tree_items():
            yield "mask", "[Mask]", icon_mask
            if session.state.skin_cluster_dq_channel_used:
                yield "dq", "[DQ Weights]", icon_dq

            for i in items:
                is_joint = i.path is not None
                infl_label = shorten_infl_name(i.path) if is_joint else i.name
                if filter.is_match(infl_label):
                    yield i.logicalIndex, infl_label, get_icon(i, is_joint)

        selected_ids = [get_item_id(item) for item in view.selectedItems()]
        current_id = get_item_id(view.currentItem())

        tree_items.clear()
        tree_root = view.invisibleRootItem()

        item_index = 0
        for itemId, displayName, icon in wanted_tree_items():
            if item_index >= tree_root.childCount():
                item = QtWidgets.QTreeWidgetItem([displayName])
            else:
                item = tree_root.child(item_index)
                item.setText(0, displayName)

            item.setData(0, id_role, itemId)
            item.setIcon(0, icon)
            item.setSizeHint(0, item_size_hint)
            tree_root.addChild(item)

            tree_items[itemId] = item
            if itemId in selected_ids:
                item.setSelected(True)

            item_index += 1

        while item_index < tree_root.childCount():
            tree_root.removeChild(tree_root.child(item_index))

        new_current_item = tree_items.get(current_id, None)
        if new_current_item is None:
            view.setCurrentItem(None, QtCore.QItemSelectionModel.Clear)
        else:
            view.setCurrentItem(new_current_item)
            new_current_item.setSelected(True)

        update_selected_influences()

    view = QtWidgets.QTreeWidget(parent)
    view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    view.setUniformRowHeights(True)
    view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
    view.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    actions.addInfluencesActions(view)
    view.addAction(actions.separator(parent, "View Options"))
    view.addAction(actions.showUsedInfluencesOnly)
    view.setIndentation(10 * scale_multiplier)
    view.header().setStretchLastSection(False)
    view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

    view.setHeaderLabels(["Influences"])

    # view.setHeaderHidden(True)
    def refresh_items():
        build_items(view, list_influences(session.state.currentLayer.selectedSkinCluster), session.state.currentLayer.layer)

    @signal.on(filter.changed, config.used_influences_only.changed, session.events.influencesListUpdated)
    def filter_changed():
        refresh_items()

    @signal.on(session.events.currentLayerChanged, qtParent=view)
    def current_layer_changed():
        if not session.state.currentLayer.layer:
            build_items(view, [], None)
        else:
            log.info("current layer changed to %s", session.state.currentLayer.layer)
            refresh_items()

    @signal.on(session.events.currentInfluenceChanged, qtParent=view)
    def current_influence_changed():
        target = session.state.currentInfluence.target
        log.info("current target changed to %s", target)
        current_item = view.currentItem()
        if target is None and current_item is None:
            return

        prev_influence = None if current_item is None else get_item_id(current_item)

        if prev_influence is None or prev_influence != target:
            item = tree_items.get(target, None)
            if item is not None:
                with qt.signals_blocked(view):
                    log.info("setting current item rofl")
                    view.setCurrentItem(item)
                update_selected_influences()

    @qt.on(view.currentItemChanged)
    def current_item_changed(curr, prev):
        if curr is None:
            return

        if session.state.selectedSkinCluster is None:
            return

        update_selected_influences()

        selected_target = get_item_id(curr)
        if session.state.currentInfluence.target == selected_target:
            return

        if session.state.currentLayer.layer:
            session.state.currentLayer.layer.paint_target = selected_target
        session.events.currentInfluenceChanged.emitIfChanged()

    @qt.on(view.itemSelectionChanged)
    def update_selected_influences():
        ids = {get_item_id(item) for item in [view.currentItem()] + view.selectedItems()}
        selection = [i for i in ids if i is not None]
        log.info("updating selection to %r", selection)

        session.context.selectedInfluences.set(selection)

    current_layer_changed()

    return view
