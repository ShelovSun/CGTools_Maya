from PySide2 import QtWidgets
from ngSkinTools2 import api
from ngSkinTools2 import signal


def buildAction_export(session, parent):
    from ngSkinTools2.ui import actions

    def export_callback():

        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(parent, "Export to Json", filter="JSON files(*.json)")
        if not file_name:
            return

        if session.state.layersAvailable:
            api.export_json(session.state.selectedSkinCluster, file_name)

    result = actions.define_action(
        parent,
        "Export Layers to Json...",
        callback=export_callback,
        tooltip="Save layer info to external file, suitable for importing weights to different scene/mesh",
    )

    @signal.on(session.events.targetChanged, qtParent=parent)
    def update_to_target():
        result.setEnabled(session.state.layersAvailable)

    update_to_target()

    return result


def buildAction_import(session, parent, fileDialogFunc=None):
    from ngSkinTools2.ui import actions
    from ngSkinTools2.ui.transferDialog import UiModel, open, LayersTransfer

    def defaultFileDialogFunc():
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(parent, "Import from Json", filter="JSON files(*.json)")
        return file_name

    if fileDialogFunc is None:
        fileDialogFunc = defaultFileDialogFunc

    def transfer_dialog(transfer):
        model = UiModel()
        model.transfer = transfer
        open(parent, model)

    def import_callback():
        if session.state.selectedSkinCluster is None:
            return

        file_name = fileDialogFunc()
        if not file_name:
            return

        t = LayersTransfer()
        t.load_source_from_file(file_name)
        t.target = session.state.selectedSkinCluster
        t.customize_callback = transfer_dialog
        t.execute()

    result = actions.define_action(parent, "Import Layers from Json...", callback=import_callback, tooltip="Load previously exported weights")

    @signal.on(session.events.targetChanged, qtParent=parent)
    def update():
        result.setEnabled(session.state.selectedSkinCluster is not None)

    update()

    return result
