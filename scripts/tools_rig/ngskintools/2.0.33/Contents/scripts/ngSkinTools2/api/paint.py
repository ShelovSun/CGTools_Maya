from ngSkinTools2.api.tools import FloodSettings
from ngSkinTools2.python_compatibility import Object
from PySide2 import QtCore
from maya import cmds
from ngSkinTools2.api import internals, plugin, tools
from ngSkinTools2.log import getLogger
from ngSkinTools2.ui import qt

log = getLogger("api/paint")


class BrushProjectionMode(Object):
    surface = 0
    screen = 1


class PaintMode(Object):
    """
    Constants for paint mode
    """

    replace = 1
    add = 2
    scale = 3
    smooth = 4
    sharpen = 5

    @classmethod
    def all(cls):
        return cls.replace, cls.smooth, cls.add, cls.scale, cls.sharpen


class TabletMode(Object):
    unused = 0
    multiplyIntensity = 1
    multiplyOpacity = 2
    multiplyRadius = 3


class WeightsDisplayMode(Object):
    allInfluences = 0
    currentInfluence = 1
    currentInfluenceColored = 2


class BrushShape(Object):
    solid = 0  # 1.0 for whole brush size
    smooth = 1  # feathered edges
    gaus = 2  # very smooth from center


class PaintTool(Object):
    __paint_context = None

    @classmethod
    def start(cls):
        if cls.__paint_context is None:
            cls.__paint_context = plugin.ngst2PaintContext()
        cmds.setToolTo(cls.__paint_context)

    def flood(self, layer, influence):
        settings = FloodSettings()
        settings.mode = self.paint_mode
        settings.intensity = self.brush_intensity
        settings.iterations = self.brush_iterations
        settings.influences_limit = self.influences_limit
        settings.mirror = self.interactive_mirror
        settings.fixed_influences_per_vertex = self.fixed_influences_per_vertex
        settings.distribute_to_other_influences = self.redistribute_removed_weight
        settings.limit_to_component_selection = self.limit_to_component_selection
        tools.flood_weights(layer, influence, settings)

    brush_projection_mode = internals.make_editable_property('brushProjectionMode')
    paint_mode = internals.make_editable_property('currentPaintMode')

    brush_radius = internals.make_editable_property('brushRadius')
    brush_shape = internals.make_editable_property('brushShape')
    brush_intensity = internals.make_editable_property('brushIntensity')
    brush_iterations = internals.make_editable_property('brushIterations')

    tablet_mode = internals.make_editable_property('tabletMode')

    interactive_mirror = internals.make_editable_property('interactiveMirror')
    influences_limit = internals.make_editable_property('influencesLimit')

    fixed_influences_per_vertex = internals.make_editable_property('fixedInfluencesPerVertex')
    limit_to_component_selection = internals.make_editable_property('limitToComponentSelection')

    weights_display_mode = internals.make_editable_property('weightsDisplayMode')
    display_node_visible = internals.make_editable_property('displayNodeVisible')
    layer_effects_display = internals.make_editable_property('layerEffectsDisplay')
    display_masked = internals.make_editable_property('displayMasked')

    show_selected_verts_only = internals.make_editable_property('showSelectedVertsOnly')

    redistribute_removed_weight = internals.make_editable_property('redistributeRemovedWeight')
    sample_joint_on_stroke_start = internals.make_editable_property('sampleJointOnStrokeStart')

    # noinspection PyMethodMayBeStatic
    def __edit__(self, **kwargs):
        plugin.ngst2PaintSettingsCmd(**kwargs)

    # noinspection PyMethodMayBeStatic
    def __query__(self, **kwargs):
        return plugin.ngst2PaintSettingsCmd(q=True, **kwargs)

    def set_default_options(self):
        self.interactive_mirror = False
        self.weights_display_mode = WeightsDisplayMode.allInfluences
        tabletEventFilter.pressure = 1.0
        self.brush_projection_mode = BrushProjectionMode.surface
        self.fixed_influences_per_vertex = False
        self.limit_to_component_selection = False

        # a copy of CPP side PaintModeSettings.buildDefaultSettings
        for mode in PaintMode.all():
            self.paint_mode = mode
            self.brush_radius = 2
            self.brush_intensity = 1.0
            self.tablet_mode = TabletMode.unused
            self.brush_shape = BrushShape.solid
            self.redistribute_removed_weight = False

            if mode == PaintMode.add:
                self.brush_intensity = 0.1
            if mode == PaintMode.scale:
                self.brush_intensity = 0.95
            if mode == PaintMode.smooth or mode == PaintMode.sharpen:
                self.brush_intensity = 0.2
                self.brush_shape = BrushShape.smooth

        self.paint_mode = PaintMode.replace

    @classmethod
    def is_painting(cls):
        return cmds.contextInfo(cmds.currentCtx(), c=True) == 'ngst2PaintContext'


class Popups(Object):
    def __init__(self):
        self.windows = []

    def add(self, w):
        self.windows.append(w)
        w.destroyed.connect(lambda *args: self.remove(w))

    def remove(self, w):
        self.windows = [i for i in self.windows if i != w]

    def close_all(self):
        for i in self.windows:
            i.close()
        self.windows = []


popups = Popups()


class TabletEventFilter(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self.pressure = 1.0

    def eventFilter(self, obj, event):
        if event.type() in [QtCore.QEvent.TabletPress, QtCore.QEvent.TabletMove]:
            self.pressure = event.pressure()
            # log.info("tablet pressure: %r", self.pressure)

        return QtCore.QObject.eventFilter(self, obj, event)

    def install(self):
        log.info("installing event filter...")
        qt.mainWindow.installEventFilter(self)
        log.info("...done")

    def uninstall(self):
        qt.mainWindow.removeEventFilter(self)
        log.info("event filter uninstalled")


tabletEventFilter = TabletEventFilter()
