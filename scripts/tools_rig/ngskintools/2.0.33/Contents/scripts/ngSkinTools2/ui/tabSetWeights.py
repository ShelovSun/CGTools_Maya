from PySide2 import QtWidgets
from ngSkinTools2 import signal
from ngSkinTools2.api.tools import FloodSettings
from ngSkinTools2.log import getLogger
from ngSkinTools2.api import PaintMode, flood_weights
from ngSkinTools2.observableValue import ObservableValue
from ngSkinTools2.python_compatibility import Object
from ngSkinTools2.signal import Signal
from ngSkinTools2.ui import qt, widgets
from ngSkinTools2.ui.layout import createTitledRow, TabSetup
from ngSkinTools2.ui.session import session
from ngSkinTools2.ui.ui_lock import UiLock

log = getLogger("tab set weights")


def make_presets():
    presets = {m: FloodSettings() for m in PaintMode.all()}
    for k, v in presets.items():
        v.mode = k

    presets[PaintMode.smooth].intensity = 0.3
    presets[PaintMode.scale].intensity = 0.3
    presets[PaintMode.add].intensity = 0.1
    presets[PaintMode.scale].intensity = 0.95

    return presets


class Model(Object):
    def __init__(self):
        self.mode_changed = Signal("mode changed")
        self.presets = make_presets()
        self.current_settings = None
        self.set_mode(PaintMode.replace)

    def set_mode(self, mode):
        self.current_settings = self.presets[mode]
        self.mode_changed.emit()

    def apply(self):
        flood_weights(session.state.currentLayer.layer, session.state.currentInfluence.target, self.current_settings)


def build_ui(parent):
    model = Model()
    ui_lock = UiLock()

    def build_mode_settings_group():
        def mode_row():
            row = QtWidgets.QVBoxLayout()

            group = QtWidgets.QActionGroup(parent)

            actions = {}

            def create_mode_button(toolbar, mode, label, tooltip):
                a = QtWidgets.QAction(label, parent)
                a.setToolTip(tooltip)
                a.setCheckable(True)
                actions[mode] = a
                group.addAction(a)

                @qt.on(a.toggled)
                @ui_lock.skip_if_updating
                def toggled(checked):
                    if checked:
                        model.set_mode(mode)
                        update_ui()

                toolbar.addAction(a)

            t = QtWidgets.QToolBar()
            create_mode_button(t, PaintMode.replace, "Replace", "Whatever")
            create_mode_button(t, PaintMode.add, "Add", "")
            create_mode_button(t, PaintMode.scale, "Scale", "")
            row.addWidget(t)

            t = QtWidgets.QToolBar()
            create_mode_button(t, PaintMode.smooth, "Smooth", "")
            create_mode_button(t, PaintMode.sharpen, "Sharpen", "")
            row.addWidget(t)

            actions[model.current_settings.mode].setChecked(True)

            return row

        influences_limit = widgets.NumberSliderGroup(value_type=int, minimum=0, maximum=10)

        @signal.on(influences_limit.valueChanged)
        @ui_lock.skip_if_updating
        def influences_limit_changed():
            for _, v in model.presets.items():
                v.influences_limit = influences_limit.value()
            update_ui()

        intensity = widgets.NumberSliderGroup()

        @signal.on(intensity.valueChanged, qtParent=parent)
        @ui_lock.skip_if_updating
        def intensity_edited():
            model.current_settings.intensity = intensity.value()
            update_ui()

        iterations = widgets.NumberSliderGroup(value_type=int, minimum=1, maximum=100)

        @signal.on(iterations.valueChanged, qtParent=parent)
        @ui_lock.skip_if_updating
        def iterations_edited():
            model.current_settings.iterations = iterations.value()
            update_ui()

        fixed_influences = QtWidgets.QCheckBox("Only adjust existing vertex influences")
        fixed_influences.setToolTip(
            "When this option is enabled, smooth will only adjust existing influences per vertex, "
            "and won't include other influences from nearby vertices"
        )
        limit_to_component_selection = QtWidgets.QCheckBox("Limit to component selection")
        limit_to_component_selection.setToolTip("When this option is enabled, smoothing will only happen between selected components")

        @qt.on(fixed_influences.stateChanged)
        @ui_lock.skip_if_updating
        def fixed_influences_changed():
            model.current_settings.fixed_influences_per_vertex = fixed_influences.isChecked()

        @qt.on(limit_to_component_selection.stateChanged)
        @ui_lock.skip_if_updating
        def limit_to_component_selection_changed():
            model.current_settings.limit_to_component_selection = limit_to_component_selection.isChecked()

        def update_ui():
            with ui_lock:
                widgets.set_paint_expo(intensity, model.current_settings.mode)
                intensity.set_value(model.current_settings.intensity)
                iterations.set_value(model.current_settings.iterations)
                iterations.set_enabled(model.current_settings.mode in [PaintMode.smooth, PaintMode.sharpen])
                fixed_influences.setEnabled(model.current_settings.mode in [PaintMode.smooth])
                fixed_influences.setChecked(model.current_settings.fixed_influences_per_vertex)
                limit_to_component_selection.setChecked(model.current_settings.limit_to_component_selection)
                limit_to_component_selection.setEnabled(fixed_influences.isEnabled())
                influences_limit.set_value(model.current_settings.influences_limit)

        settings_group = QtWidgets.QGroupBox("Mode Settings")
        layout = QtWidgets.QVBoxLayout()

        layout.addLayout(createTitledRow("Mode:", mode_row()))
        layout.addLayout(createTitledRow("Intensity:", intensity.layout()))
        layout.addLayout(createTitledRow("Iterations:", iterations.layout()))
        layout.addLayout(createTitledRow("Influences limit:", influences_limit.layout()))
        layout.addLayout(createTitledRow("Weight bleeding:", fixed_influences))
        layout.addLayout(createTitledRow("Isolation:", limit_to_component_selection))
        settings_group.setLayout(layout)

        update_ui()

        return settings_group

    def common_settings():
        layout = QtWidgets.QVBoxLayout()

        mirror = QtWidgets.QCheckBox("Mirror")
        layout.addLayout(createTitledRow("", mirror))

        @qt.on(mirror.stateChanged)
        def mirror_changed():
            for _, v in model.presets.items():
                v.mirror = mirror.isChecked()

        redistribute_removed_weight = QtWidgets.QCheckBox("Distribute to other influences")
        layout.addLayout(createTitledRow("Removed weight:", redistribute_removed_weight))

        @qt.on(redistribute_removed_weight.stateChanged)
        def redistribute_removed_weight_changed():
            for _, v in model.presets.items():
                v.distribute_to_other_influences = redistribute_removed_weight.isChecked()

        @signal.on(model.mode_changed, qtParent=layout)
        def update_ui():
            mirror.setChecked(model.current_settings.mirror)
            redistribute_removed_weight.setChecked(model.current_settings.distribute_to_other_influences)

        group = QtWidgets.QGroupBox("Common Settings")
        group.setLayout(layout)

        update_ui()

        return group

    def apply_button():
        btn = QtWidgets.QPushButton("Apply")
        btn.setToolTip("Apply selected operation to vertex")

        @qt.on(btn.clicked)
        def clicked():
            model.apply()

        return btn

    tab = TabSetup()
    tab.innerLayout.addWidget(build_mode_settings_group())
    tab.innerLayout.addWidget(common_settings())
    tab.innerLayout.addStretch()

    tab.lowerButtonsRow.addWidget(apply_button())

    @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
    def update_tab_enabled():
        tab.tabContents.setEnabled(session.state.layersAvailable)

    update_tab_enabled()

    return tab.tabContents
