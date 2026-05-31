from PySide2 import QtCore, QtWidgets, QtGui
from ngSkinTools2 import signal, api
from ngSkinTools2.log import getLogger

from ngSkinTools2.ui import qt
from ngSkinTools2.ui.layout import scale_multiplier
from ngSkinTools2.ui.session import session

log = getLogger("layersView")


def buildView(parent, actions):
    from ngSkinTools2.operations import layers

    icon_layer = QtGui.QIcon(":/layeredTexture.svg")
    icon_layer_disabled = QtGui.QIcon(":/layerEditor.png")
    icon_visible = qt.image_icon("eye-fill.svg")
    icon_hidden = qt.image_icon("eye-slash-fill.svg")

    layerDataRole = QtCore.Qt.UserRole + 1
    itemSizeHint = QtCore.QSize(1 * scale_multiplier, 25 * scale_multiplier)

    def getLayerFromTreeItem(item):
        if item is None:
            return None
        return item.data(0, layerDataRole)

    def syncLayerParentsToWidgetItems(view):
        """
        after drag/drop tree reordering, just brute-force check
        that rearranged items match layers parents
        :return:
        """

        layers = api.Layers(session.state.selectedSkinCluster)

        def syncItem(treeItem, parent_layer_id):
            for i in range(treeItem.childCount()):
                child = treeItem.child(i)
                rebuild_buttons(child)

                childLayer = getLayerFromTreeItem(child)  # type: api.Layer

                if childLayer.parent_id != parent_layer_id:
                    log.info("changing layer parent: %r->%r (was %r)", parent_layer_id, childLayer, childLayer.parent_id)
                    childLayer.parent = parent_layer_id

                newIndex = treeItem.childCount() - i - 1
                if childLayer.index != newIndex:
                    log.info("changing layer index: %r->%r (was %r)", childLayer, newIndex, childLayer.index)
                    childLayer.index = newIndex

                syncItem(child, childLayer.id)

        with qt.signals_blocked(view):
            syncItem(view.invisibleRootItem(), None)

    class LayersWidget(QtWidgets.QTreeWidget):
        def dropEvent(self, event):
            QtWidgets.QTreeWidget.dropEvent(self, event)
            syncLayerParentsToWidgetItems(self)

    view = LayersWidget(parent)
    view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
    view.setUniformRowHeights(True)
    view.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    # enable drag/drop
    view.setDragEnabled(True)
    view.viewport().setAcceptDrops(True)
    view.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
    view.setDropIndicatorShown(True)

    # add context menu
    view.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
    actions.addLayersActions(view)

    view.setHeaderLabels(["Layers", ""])
    # view.setHeaderHidden(True)
    view.header().setMinimumSectionSize(1)
    view.header().setStretchLastSection(False)
    view.header().swapSections(0, 1)
    view.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
    view.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
    view.setColumnWidth(1, 25 * scale_multiplier)
    view.setIndentation(15 * scale_multiplier)
    view.setIconSize(QtCore.QSize(20 * scale_multiplier, 20 * scale_multiplier))

    treeItems = {}

    def rebuild_buttons(item):
        l = getLayerFromTreeItem(item)
        bar = QtWidgets.QToolBar(parent=parent)
        bar.setMovable(False)
        bar.setIconSize(QtCore.QSize(13 * scale_multiplier, 13 * scale_multiplier))
        a = bar.addAction(icon_visible if l is None or l.enabled else icon_hidden, "Toggle enabled/disabled")

        @qt.on(a.triggered)
        def handler():
            l.enabled = not l.enabled
            session.events.layerListChanged.emitIfChanged()

        view.setItemWidget(item, 1, bar)

    def buildItems(view, layerInfos):
        """
        sync items in view with provided layer values, trying to delete as little items on the view as possible
        :type layerInfos: list[api.Layer]
        """

        # build map "parent id->list of children "

        log.info("syncing items...")

        # save selected layers IDs to restore item selection later
        selected_layer_ids = {getLayerFromTreeItem(item).id for item in view.selectedItems()}
        current_item_id = None if view.currentItem() is None else getLayerFromTreeItem(view.currentItem()).id

        hierarchy = {}
        for child in layerInfos:
            if child.parent_id not in hierarchy:
                hierarchy[child.parent_id] = []
            hierarchy[child.parent_id].append(child)

        def sync(parentTreeItem, childrenList):
            while parentTreeItem.childCount() > len(childrenList):
                parentTreeItem.removeChild(parentTreeItem.child(len(childrenList)))

            for index, child in enumerate(reversed(childrenList)):
                if index >= parentTreeItem.childCount():
                    item = QtWidgets.QTreeWidgetItem()
                    # item.setSizeHint(0, itemSizeHint)
                    item.setSizeHint(1, QtCore.QSize(1 * scale_multiplier, 25 * scale_multiplier))
                    item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
                    parentTreeItem.addChild(item)
                else:
                    item = parentTreeItem.child(index)

                treeItems[child.id] = item

                item.setData(0, layerDataRole, child)
                item.setText(0, child.name)
                item.setIcon(0, icon_layer if child.enabled else icon_layer_disabled)
                rebuild_buttons(item)
                item.setSelected(child.id in selected_layer_ids)
                if child.id == current_item_id:
                    view.setCurrentItem(item)

                sync(item, hierarchy.get(child.id, []))

        with qt.signals_blocked(view):
            treeItems.clear()
            sync(view.invisibleRootItem(), hierarchy.get(None, []))

    @signal.on(session.events.layerListChanged, qtParent=view)
    def refreshLayerList():
        log.info("event handler for layer list changed")
        if not session.state.layersAvailable:
            buildItems(view, [])
        else:
            buildItems(view, session.state.all_layers)

        update_selected_items()

    @signal.on(session.events.currentLayerChanged, qtParent=view)
    def currentLayerChanged():
        log.info("event handler for currentLayerChanged")
        layer = session.state.currentLayer.layer
        current_item = view.currentItem()
        if layer is None:
            view.setCurrentItem(None)
            return

        prevLayer = None if current_item is None else getLayerFromTreeItem(current_item)

        if prevLayer is None or prevLayer.id != layer.id:
            item = treeItems.get(layer.id, None)
            if item is not None:
                log.info("setting current item to " + item.text(0))
                view.setCurrentItem(item, 0, QtCore.QItemSelectionModel.SelectCurrent | QtCore.QItemSelectionModel.ClearAndSelect)

                item.setSelected(True)

    @qt.on(view.currentItemChanged)
    def currentItemChanged(curr, prev):
        if curr is None:
            return

        selectedLayer = getLayerFromTreeItem(curr)

        if layers.getCurrentLayer() == selectedLayer:
            return

        layers.setCurrentLayer(selectedLayer)

    @qt.on(view.itemChanged)
    def itemChanged(item, column):
        log.info("item changed")
        layers.renameLayer(getLayerFromTreeItem(item), item.text(column))

    @qt.on(view.itemSelectionChanged)
    def update_selected_items():
        selection = [getLayerFromTreeItem(item) for item in view.selectedItems()]
        if selection != session.context.selected_layers(default=[]):
            log.info("new selected layers: %r", selection)
            session.context.selected_layers.set(selection)

    refreshLayerList()

    return view
