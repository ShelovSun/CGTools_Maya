from ngSkinTools2.api import plugin, Layers
from ngSkinTools2.api import layers as api_layers, Layer
from ngSkinTools2.api.layers import generate_layer_name
from ngSkinTools2.api.target_info import list_influences
from ngSkinTools2.decorators import undoable
from ngSkinTools2.log import getLogger
from ngSkinTools2.python_compatibility import Object

log = getLogger("tools")


def assign_from_closest_joint(target, layer, influences=None):
    # type: (str, Layer, List[int]) -> None

    if influences is None:
        influences = [i.logicalIndex for i in list_influences(target)]

    if len(influences) == 0:
        # nothing to do?
        return

    plugin.ngst2tools(
        tool="closestJoint",
        target=target,
        layer=api_layers.as_layer_id(layer),
        influences=[int(i) for i in influences],
    )


def unify_weights(target, layer, overall_effect, single_cluster_mode):
    plugin.ngst2tools(
        tool="unifyWeights",
        target=target,
        layer=api_layers.as_layer_id(layer),
        overallEffect=overall_effect,
        singleClusterMode=single_cluster_mode,
    )


class FloodSettings(Object):
    def __init__(self):
        from ngSkinTools2.api import paint

        self.mode = paint.PaintMode.replace
        self.intensity = 1.0
        self.iterations = 1
        self.influences_limit = 0
        self.mirror = False
        self.fixed_influences_per_vertex = False
        self.distribute_to_other_influences = False
        self.limit_to_component_selection = False


def flood_weights(layer, influence=None, settings=None):
    """
    :type layer: Layer
    :type settings: FloodSettings
    """

    if settings is None:
        settings = FloodSettings()  # just use default settings

    plugin.ngst2tools(
        tool="floodWeights",
        target=layer.mesh,
        influence=influence,
        layer=api_layers.as_layer_id(layer),
        mode=settings.mode,
        intensity=settings.intensity,
        iterations=int(settings.iterations),
        influencesLimit=int(settings.influences_limit),
        mirror=bool(settings.mirror),
        distributeRemovedWeight=settings.distribute_to_other_influences,
        limitToComponentSelection=settings.limit_to_component_selection,
        fixedInfluencesPerVertex=bool(settings.fixed_influences_per_vertex),
    )


@undoable
def merge_layers(layers):
    """
    :type layers: list[Layer]
    :rtype: Layer
    """
    if len(layers) > 1:
        # verify that all layers are from the same parent
        for i, j in zip(layers[:-1], layers[1:]):
            if i.mesh != j.mesh:
                raise Exception("layers are not from the same mesh")

    result = plugin.ngst2tools(
        tool="mergeLayers",
        target=layers[0].mesh,
        layers=[api_layers.as_layer_id(i) for i in layers],
    )

    target_layer = Layer.load(layers[0].mesh, result['layerId'])
    target_layer.set_current()

    return target_layer


@undoable
def duplicate_layer(layer):
    """

    :type layer: Layer
    :rtype: Layer
    """

    result = plugin.ngst2tools(
        tool="duplicateLayer",
        target=layer.mesh,
        sourceLayer=layer.id,
    )

    target_layer = Layer.load(layer.mesh, result['layerId'])

    import re

    base_name = re.sub(r"( \(copy\))?( \(\d+\))*", "", layer.name)
    other_layers = [l for l in Layers(target_layer.mesh).list() if l.id != target_layer.id]
    target_layer.name = generate_layer_name(other_layers, base_name + " (copy)")

    target_layer.set_current()

    return target_layer


@undoable
def fill_transparency(layer):
    """

    :type layer: Layer
    """

    plugin.ngst2tools(
        tool="fillLayerTransparency",
        target=layer.mesh,
        layer=layer.id,
    )


def copy_component_weights(layer):
    """
    :type layer: Layer
    """

    plugin.ngst2tools(
        tool="copyComponentWeights",
        target=layer.mesh,
        layer=layer.id,
    )


def paste_average_component_weights(layer):
    """
    :type layer: Layer
    """

    plugin.ngst2tools(
        tool="pasteAverageComponentWeights",
        target=layer.mesh,
        layer=layer.id,
    )


def refresh_screen(target):
    plugin.ngst2tools(
        tool="refreshScreen",
        target=target,
    )
