from PySide2 import QtWidgets, QtCore
from ngSkinTools2 import signal
from ngSkinTools2 import api
from ngSkinTools2.log import getLogger
from ngSkinTools2.observableValue import Undefined
from ngSkinTools2.ui import qt, widgets
from ngSkinTools2.ui.layout import createTitledRow, TabSetup
from ngSkinTools2.ui.session import session

log = getLogger("tab layer effects")


def checkStateFromBooleanStates(states):
    """
    for a list of booleans, return checkbox check state - one of Qt.Checked, Qt.Unchecked and Qt.PartiallyChecked

    :type states: list[bool]
    """
    currentState = None
    for i in states:
        if currentState is None:
            currentState = i
            continue

        if i != currentState:
            return QtCore.Qt.PartiallyChecked

    if currentState:
        return QtCore.Qt.Checked

    return QtCore.Qt.Unchecked


def build_ui(parent):
    def list_layers():
        # type: () -> list[api.Layer]
        return [] if not session.state.layersAvailable else session.context.selected_layers(default=[])

    def build_properties():
        layout = QtWidgets.QVBoxLayout()
        opacity = widgets.NumberSliderGroup(tooltip="multiply layer mask to control overall transparency of the layer.")
        opacity.set_value(1.0)
        layout.addLayout(createTitledRow("Opacity:", opacity.layout()))

        def default_selection_opacity(layers):
            if len(layers) > 0:
                return layers[0].opacity
            return 1.0

        @signal.on(session.context.selected_layers.changed, session.events.currentLayerChanged, qtParent=tab.tabContents)
        def update_values():
            layers = list_layers()
            enabled = len(layers) > 0
            opacity.set_enabled(enabled)
            opacity.set_value(default_selection_opacity(layers))

        @signal.on(opacity.valueChanged)
        def opacity_edited():
            layers = list_layers()
            # avoid changing opacity of all selected layers if we just changed slider value based on changed layer selection
            if opacity.value() == default_selection_opacity(layers):
                return
            for i in list_layers():
                i.opacity = opacity.value()

        update_values()

        group = QtWidgets.QGroupBox("Layer properties")
        group.setLayout(layout)

        return group

    def build_mirror_effect():
        def elements():
            result = QtWidgets.QVBoxLayout()

            influences = QtWidgets.QCheckBox("Influence weights")
            mask = QtWidgets.QCheckBox("Layer mask")
            dq = QtWidgets.QCheckBox("Dual quaternion weights")

            for i in [influences, mask, dq]:
                i.setTristate(True)
                result.addWidget(i)

            def configure_behavior(checkbox, state):
                @qt.on(checkbox.stateChanged)
                def update_pref():
                    if checkbox.checkState() == QtCore.Qt.PartiallyChecked:
                        checkbox.setCheckState(QtCore.Qt.Checked)

                    enabled = checkbox.checkState() == QtCore.Qt.Checked
                    for i in list_layers():
                        i.effects.configure_mirror(**{state: enabled})

            configure_behavior(influences, 'mirror_weights')
            configure_behavior(mask, 'mirror_mask')
            configure_behavior(dq, 'mirror_dq')

            @signal.on(session.context.selected_layers.changed, session.events.currentLayerChanged, qtParent=tab.tabContents)
            def update_values():
                layers = list_layers()
                with qt.signals_blocked(influences):
                    influences.setCheckState(checkStateFromBooleanStates([i.effects.mirror_weights for i in layers]))
                with qt.signals_blocked(mask):
                    mask.setCheckState(checkStateFromBooleanStates([i.effects.mirror_mask for i in layers]))
                with qt.signals_blocked(dq):
                    dq.setCheckState(checkStateFromBooleanStates([i.effects.mirror_dq for i in layers]))

            update_values()

            return result

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(createTitledRow("Mirror effect on:", elements()))

        group = QtWidgets.QGroupBox("Mirror")
        group.setLayout(layout)
        return group

    def build_skin_properties():

        use_max_influences = QtWidgets.QCheckBox("Limit max influences per vertex")
        max_influences = widgets.NumberSliderGroup(minimum=1, maximum=5, tooltip="", value_type=int)
        use_prune_weight = QtWidgets.QCheckBox("Prune small weights before writing to skin cluster")
        prune_weight = widgets.NumberSliderGroup(maximum=0.05, tooltip="")
        prune_weight.set_expo("start", 3)

        update_guard = qt.updateGuard()

        @signal.on(session.events.targetChanged)
        def update_ui():
            group.setEnabled(session.state.layersAvailable)

            with update_guard:
                prune_weight.set_enabled(session.state.layersAvailable)
                if session.state.layersAvailable:
                    use_max_influences.setChecked(session.state.layers.influence_limit_per_vertex != 0)
                    max_influences.set_value(session.state.layers.influence_limit_per_vertex)
                    use_prune_weight.setChecked(session.state.layers.prune_weights_filter_threshold != 0)
                    prune_weight.set_value(session.state.layers.prune_weights_filter_threshold)

                update_ui_enabled()

        def update_ui_enabled():
            max_influences.set_enabled(use_max_influences.isChecked())
            prune_weight.set_enabled(use_prune_weight.isChecked())

        @qt.on(use_max_influences.stateChanged, use_prune_weight.stateChanged)
        @signal.on(max_influences.valueChanged, prune_weight.valueChanged)
        def update_values():
            if update_guard.updating:
                return

            if session.state.layersAvailable:
                session.state.layers.influence_limit_per_vertex = max_influences.value() if use_max_influences.isChecked() else 0
                session.state.layers.prune_weights_filter_threshold = prune_weight.value() if use_prune_weight.isChecked() else 0

            update_ui_enabled()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(use_max_influences)
        layout.addLayout(createTitledRow("Max influences:", max_influences.layout()))
        layout.addWidget(use_prune_weight)
        layout.addLayout(createTitledRow("Prune below:", prune_weight.layout()))

        group = QtWidgets.QGroupBox("Skin Properties")
        group.setLayout(layout)

        update_ui()

        return group

    tab = TabSetup()
    tab.innerLayout.addWidget(build_properties())
    tab.innerLayout.addWidget(build_mirror_effect())
    tab.innerLayout.addWidget(build_skin_properties())
    tab.innerLayout.addStretch()

    @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
    def updateTabEnabled():
        tab.tabContents.setEnabled(session.state.layersAvailable)

    updateTabEnabled()

    return tab.tabContents
