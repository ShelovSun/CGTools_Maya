from PySide2 import QtGui
from PySide2 import QtWidgets
from ngSkinTools2 import signal
from ngSkinTools2.api.paint import BrushProjectionMode
from ngSkinTools2.log import getLogger
from ngSkinTools2.api import PaintMode, BrushShape, PaintTool
from ngSkinTools2.ui import qt, widgets
from ngSkinTools2.ui.layout import createTitledRow, TabSetup
from ngSkinTools2.ui.qt import bind_action_to_button
from ngSkinTools2.ui.session import session

log = getLogger("tab paint")


# noinspection PyShadowingNames
def build_ui(parent, globalActions):
    paint = PaintTool()

    def build_brush_settings_group():
        def brush_mode_row3():
            row = QtWidgets.QVBoxLayout()

            group = QtWidgets.QActionGroup(parent)

            actions = {}

            # noinspection PyShadowingNames
            def create_brush_mode_button(t, mode, label, tooltip):
                a = QtWidgets.QAction(label, parent)
                a.setToolTip(tooltip)
                a.setCheckable(True)
                actions[mode] = a
                group.addAction(a)

                @qt.on(a.toggled)
                def toggled(checked):
                    if checked and paint.paint_mode != mode:
                        paint.paint_mode = mode
                        session.events.tool_settings_changed.emit()

                t.addAction(a)

            t = QtWidgets.QToolBar()
            create_brush_mode_button(t, PaintMode.replace, "Replace", "Whatever")
            create_brush_mode_button(t, PaintMode.add, "Add", "")
            create_brush_mode_button(t, PaintMode.scale, "Scale", "")
            row.addWidget(t)

            t = QtWidgets.QToolBar()
            create_brush_mode_button(t, PaintMode.smooth, "Smooth", "")
            create_brush_mode_button(t, PaintMode.sharpen, "Sharpen", "")
            row.addWidget(t)

            @signal.on(session.events.tool_settings_changed, qtParent=row)
            def update_current_brush_mode():
                actions[paint.paint_mode].setChecked(True)

            update_current_brush_mode()

            return row

        # noinspection DuplicatedCode
        def brush_shape_row():
            # noinspection PyShadowingNames
            result = QtWidgets.QToolBar()
            group = QtWidgets.QActionGroup(parent)

            def add_brush_shape_action(icon, title, shape, checked=False):
                a = QtWidgets.QAction(title, parent)
                a.setCheckable(True)
                a.setIcon(QtGui.QIcon(icon))
                a.setChecked(checked)
                result.addAction(a)
                group.addAction(a)

                # noinspection PyShadowingNames
                @qt.on(a.toggled)
                def toggled(checked):
                    if checked:
                        paint.brush_shape = shape
                        update_ui()

                @signal.on(session.events.tool_settings_changed, qtParent=a)
                def tool_settings_changed():
                    a.setChecked(paint.brush_shape == shape)

            add_brush_shape_action(':/circleSolid.png', 'Solid', BrushShape.solid, checked=True)
            add_brush_shape_action(':/circlePoly.png', 'Smooth', BrushShape.smooth)
            add_brush_shape_action(':/circleGaus.png', 'Gaus', BrushShape.gaus)

            return result

        # noinspection DuplicatedCode
        def brush_projection_mode_row():
            # noinspection PyShadowingNames
            result = QtWidgets.QToolBar()
            group = QtWidgets.QActionGroup(parent)

            def add(icon, title, mode, checked=False):
                a = QtWidgets.QAction(title, parent)
                a.setCheckable(True)
                a.setIcon(QtGui.QIcon(icon))
                a.setChecked(checked)
                result.addAction(a)
                group.addAction(a)

                # noinspection PyShadowingNames
                @qt.on(a.toggled)
                def toggled(checked):
                    if checked:
                        paint.brush_projection_mode = mode
                        update_ui()

                @signal.on(session.events.tool_settings_changed, qtParent=a)
                def tool_settings_changed():
                    a.setChecked(paint.brush_projection_mode == mode)

            add(None, 'Surface', BrushProjectionMode.surface, checked=True)
            add(None, 'Screen', BrushProjectionMode.screen, checked=False)
            return result

        def stylus_pressure_selection():
            # noinspection PyShadowingNames
            result = QtWidgets.QComboBox()
            result.addItem("Unused")
            result.addItem("Multiply intensity")
            result.addItem("Multiply opacity")
            result.addItem("Multiply radius")
            return result

        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(createTitledRow("Brush projection:", brush_projection_mode_row()))
        layout.addLayout(createTitledRow("Brush mode:", brush_mode_row3()))
        layout.addLayout(createTitledRow("Brush shape:", brush_shape_row()))
        intensity = widgets.NumberSliderGroup()
        radius = widgets.NumberSliderGroup(
            maximum=100, tooltip="You can also set brush radius by just holding <b>B</b> " "and mouse-dragging in the viewport"
        )
        iterations = widgets.NumberSliderGroup(value_type=int, minimum=1, maximum=100)
        layout.addLayout(createTitledRow("Intensity:", intensity.layout()))
        layout.addLayout(createTitledRow("Brush radius:", radius.layout()))
        layout.addLayout(createTitledRow("Brush iterations:", iterations.layout()))

        influences_limit = widgets.NumberSliderGroup(value_type=int, minimum=0, maximum=10)
        layout.addLayout(createTitledRow("Influences limit:", influences_limit.layout()))

        @signal.on(influences_limit.valueChanged)
        def influences_limit_changed():
            paint.influences_limit = influences_limit.value()
            update_ui()

        fixed_influences = QtWidgets.QCheckBox("Only adjust existing vertex influences")
        fixed_influences.setToolTip(
            "When this option is enabled, smooth will only adjust existing influences per vertex, "
            "and won't include other influences from nearby vertices"
        )
        layout.addLayout(createTitledRow("Weight bleeding:", fixed_influences))

        @qt.on(fixed_influences.stateChanged)
        def fixed_influences_changed():
            paint.fixed_influences_per_vertex = fixed_influences.isChecked()

        limit_to_component_selection = QtWidgets.QCheckBox("Limit to component selection")
        limit_to_component_selection.setToolTip("When this option is enabled, smoothing will only happen between selected components")
        layout.addLayout(createTitledRow("Isolation:", limit_to_component_selection))

        @qt.on(limit_to_component_selection.stateChanged)
        def limit_to_component_selection_changed():
            paint.limit_to_component_selection = limit_to_component_selection.isChecked()

        interactive_mirror = QtWidgets.QCheckBox("Interactive mirror")
        layout.addLayout(createTitledRow("", interactive_mirror))

        @qt.on(interactive_mirror.stateChanged)
        def interactive_mirror_changed():
            paint.interactive_mirror = interactive_mirror.isChecked()
            update_ui()

        sample_joint_on_stroke_start = QtWidgets.QCheckBox("Sample current joint on stroke start")
        layout.addLayout(createTitledRow("", sample_joint_on_stroke_start))

        @qt.on(sample_joint_on_stroke_start.stateChanged)
        def interactive_mirror_changed():
            paint.sample_joint_on_stroke_start = sample_joint_on_stroke_start.isChecked()
            update_ui()

        redistribute_removed_weight = QtWidgets.QCheckBox("Distribute to other influences")
        layout.addLayout(createTitledRow("Removed weight:", redistribute_removed_weight))

        @qt.on(redistribute_removed_weight.stateChanged)
        def redistribute_removed_weight_changed():
            paint.redistribute_removed_weight = redistribute_removed_weight.isChecked()
            update_ui()

        stylus = stylus_pressure_selection()
        layout.addLayout(createTitledRow("Stylus pressure:", stylus))

        @signal.on(session.events.tool_settings_changed, qtParent=layout)
        def update_ui():
            log.info("updated paint settings ui")
            intensity.set_value(paint.brush_intensity)
            widgets.set_paint_expo(intensity, paint.paint_mode)
            radius.set_value(paint.brush_radius)
            iterations.set_value(paint.brush_iterations)
            iterations.set_enabled(paint.paint_mode in [PaintMode.smooth, PaintMode.sharpen])
            stylus.setCurrentIndex(paint.tablet_mode)
            interactive_mirror.setChecked(paint.interactive_mirror)
            redistribute_removed_weight.setChecked(paint.redistribute_removed_weight)
            influences_limit.set_value(paint.influences_limit)
            sample_joint_on_stroke_start.setChecked(paint.sample_joint_on_stroke_start)
            fixed_influences.setChecked(paint.fixed_influences_per_vertex)
            fixed_influences.setEnabled(paint.paint_mode == PaintMode.smooth)
            limit_to_component_selection.setChecked(paint.limit_to_component_selection)
            limit_to_component_selection.setEnabled(fixed_influences.isEnabled())

        @signal.on(radius.valueChanged, qtParent=layout)
        def radius_edited():
            log.info("updated brush radius")
            paint.brush_radius = radius.value()
            update_ui()

        @signal.on(intensity.valueChanged, qtParent=layout)
        def intensity_edited():
            paint.brush_intensity = intensity.value()
            update_ui()

        @signal.on(iterations.valueChanged, qtParent=layout)
        def iterations_edited():
            paint.brush_iterations = iterations.value()
            update_ui()

        @qt.on(stylus.currentIndexChanged)
        def stylus_edited():
            paint.tablet_mode = stylus.currentIndex()
            update_ui()

        update_ui()

        result = QtWidgets.QGroupBox("Brush behavior")
        result.setLayout(layout)
        return result

    def build_display_settings():
        result = QtWidgets.QGroupBox("Display settings")
        layout = QtWidgets.QVBoxLayout()

        influences_display = QtWidgets.QComboBox()
        influences_display.addItem("All influences, multiple colors")
        influences_display.addItem("Current influence, grayscale")
        influences_display.addItem("Current influence, colored")
        influences_display.setMinimumWidth(1)
        influences_display.setCurrentIndex(paint.weights_display_mode)

        display_toolbar = QtWidgets.QToolBar()
        display_toolbar.addAction(globalActions.randomizeInfluencesColors)

        @qt.on(influences_display.currentIndexChanged)
        def influences_display_changed():
            paint.weights_display_mode = influences_display.currentIndex()
            update_ui_to_tool()

        display_layout = QtWidgets.QVBoxLayout()
        display_layout.addWidget(influences_display)
        display_layout.addWidget(display_toolbar)
        layout.addLayout(createTitledRow("Influences display:", display_layout))

        show_effects = QtWidgets.QCheckBox("Show layer effects")
        layout.addLayout(createTitledRow("", show_effects))
        show_masked = QtWidgets.QCheckBox("Show masked weights")
        layout.addLayout(createTitledRow("", show_masked))

        show_selected_verts_only = QtWidgets.QCheckBox("Hide unselected vertices")
        layout.addLayout(createTitledRow("", show_selected_verts_only))

        @qt.on(show_effects.stateChanged)
        def show_effects_changed():
            paint.layer_effects_display = show_effects.isChecked()

        @qt.on(show_masked.stateChanged)
        def show_masked_changed():
            paint.display_masked = show_masked.isChecked()

        @qt.on(show_selected_verts_only.stateChanged)
        def show_selected_verts_changed():
            paint.show_selected_verts_only = show_selected_verts_only.isChecked()

        mesh_toolbar = QtWidgets.QToolBar()
        toggle_original_mesh = QtWidgets.QAction("Show Original Mesh", mesh_toolbar)
        toggle_original_mesh.setCheckable(True)

        @qt.on(toggle_original_mesh.triggered)
        def toggle_display_node_visible():
            paint.display_node_visible = not toggle_original_mesh.isChecked()
            update_ui_to_tool()

        mesh_toolbar.addAction(toggle_original_mesh)

        @signal.on(session.events.toolChanged, qtParent=tab.tabContents)
        def update_ui_to_tool():
            toggle_original_mesh.setChecked(paint.is_painting() and not paint.display_node_visible)

            show_effects.setChecked(paint.layer_effects_display)
            show_masked.setChecked(paint.display_masked)
            show_selected_verts_only.setChecked(paint.show_selected_verts_only)
            globalActions.randomizeInfluencesColors.setEnabled(influences_display.currentIndex() == 0)
            display_toolbar.setVisible(globalActions.randomizeInfluencesColors.isEnabled())

        layout.addLayout(createTitledRow("", mesh_toolbar))

        update_ui_to_tool()

        result.setLayout(layout)
        return result

    tab = TabSetup()
    tab.innerLayout.addWidget(build_brush_settings_group())
    tab.innerLayout.addWidget(build_display_settings())
    tab.innerLayout.addStretch()

    tab.lowerButtonsRow.addWidget(bind_action_to_button(globalActions.paint, QtWidgets.QPushButton()))
    tab.lowerButtonsRow.addWidget(bind_action_to_button(globalActions.flood, QtWidgets.QPushButton()))

    @signal.on(session.events.toolChanged, qtParent=tab.tabContents)
    def update_to_tool():
        tab.scrollArea.setEnabled(paint.is_painting())

    @signal.on(session.events.targetChanged, qtParent=tab.tabContents)
    def update_tab_enabled():
        tab.tabContents.setEnabled(session.state.layersAvailable)

    update_to_tool()
    update_tab_enabled()

    return tab.tabContents
