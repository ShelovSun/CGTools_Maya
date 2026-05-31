from ngSkinTools2.api.config import Config
from ngSkinTools2.decorators import undoable
from ngSkinTools2.python_compatibility import Object
import json

from maya import mel
from ngSkinTools2.api import internals, plugin, target_info
from ngSkinTools2.api.suspend_updates import suspend_updates
from ngSkinTools2.log import getLogger
from ngSkinTools2.python_compatibility import is_string

logger = getLogger("api/layers")


class NamedPaintTarget(Object):
    MASK = "mask"
    DUAL_QUATERNION = "dq"


class LayerEffects(Object):
    def __init__(self, layer, state=None):
        """
        :type layer: Layer
        """
        self.layer = layer
        if state is not None:
            self.__set_state__(state)

    def __set_state__(self, state):
        self.mirror_mask = state.get("mirrorMask", False)
        self.mirror_weights = state.get("mirrorWeights", False)
        self.mirror_dq = state.get("mirrorDq", False)

    def configure_mirror(self, everything=None, mirror_mask=None, mirror_weights=None, mirror_dq=None):
        if everything is not None:
            mirror_mask = mirror_dq = mirror_weights = everything

        logger.info("configure mirror: layer %s mask %r weights %r dq %r", self.layer.name, mirror_mask, mirror_weights, mirror_dq)

        args = {'mirrorLayerDq': mirror_dq, 'mirrorLayerMask': mirror_mask, 'mirrorLayerWeights': mirror_weights}

        self.layer.__edit__(configureMirrorEffect=True, **{k: v for k, v in list(args.items()) if v is not None})


def build_layer_property(name, doc, editName=None):
    if editName is None:
        editName = name
    return property(lambda self: self.__get_state__(name), lambda self, val: self.__edit__(**{editName: val}), doc=doc)


class Layer(Object):
    """"""

    name = build_layer_property('name', "str: Layer name")  # type: str
    enabled = build_layer_property('enabled', "bool: is layer enabled or disabled")  # type: bool
    opacity = build_layer_property('opacity', "float: value between 1.0 and 0")  # type: float
    paint_target = build_layer_property(
        'paintTarget', "str or int: currently active paint target for this layer (either an influence or one of named targets)"
    )  # type: Union(str, int)
    index = build_layer_property('index', editName='layerIndex', doc="int: layer index in parent's child list; set to reorder")  # type: int

    @classmethod
    def load(cls, mesh, layerId):
        if layerId < 0:
            raise Exception("invalid layer ID: %s" % layerId)
        result = Layer(mesh, layerId)
        result.reload()
        return result

    def __init__(self, mesh, id, state=None):
        self.mesh = mesh
        self.id = id
        self.effects = LayerEffects(self)
        self.__state = None
        if state is not None:
            self.__set_state(state)

    def __get_state__(self, k):
        return self.__state[k]

    def __query__(self, arg, **kwargs):
        keys = " ".join(["-{k} {v}".format(k=k, v=v) for k, v in list(kwargs.items())])
        return mel.eval("ngst2Layers -id {id}  {keys} -q -{arg} {mesh} ".format(id=self.id, mesh=self.mesh, keys=keys, arg=arg))

    def __edit__(self, **kwargs):
        self.__set_state(plugin.ngst2Layers(self.mesh, e=True, id=as_layer_id(self), **kwargs))

    def __set_state(self, state):
        if state is None:
            # some plugin functions still return empty result after edits - nevermind those
            return
        if is_string(state):
            state = json.loads(state)

        self.__state = state

        # logger.info("setting layer state %r: %r", self.id, state)

        self.parent_id = state['parentId']
        self.__parent = None
        self.children_ids = state['children']
        self.__children = []

        self.effects.__set_state__(state['effects'])

    def reload(self):
        """
        Refresh layer data from plugin.
        """
        self.__set_state(self.__query__('layerAttributesJson'))

    def __eq__(self, other):
        if not isinstance(other, Layer):
            return False

        return self.mesh == other.mesh and self.id == other.id and self.__state == other.__state

    def __repr__(self):
        return "[Layer #{id}]".format(id=self.id)

    @property
    def parent(self):
        """
        Layer: layer parent, or None, if layer is at root level.
        """
        if self.__parent is None:
            if self.parent_id is not None:
                self.__parent = Layer.load(self.mesh, self.parent_id)

        return self.__parent

    @parent.setter
    def parent(self, parent):
        if parent is None:
            parent = 0

        self.__edit__(parent=as_layer_id(parent))

    @property
    def num_children(self):
        """
        int: a bit more lightweight method to count number of child layers than len(children()), as it does not
        prefetch children data.
        """
        return len(self.children_ids)

    @property
    def children(self):
        """
        list[Layer]: lazily load children if needed, and return as Layer objects
        """
        if len(self.children_ids) != 0:
            if len(self.__children) == 0:
                self.__children = [Layer.load(self.mesh, i) for i in self.children_ids]

        return self.__children

    def set_current(self):
        """

        Set as "default" layer for other operations.


        .. warning::
            Scheduled for removal. API calls should specify target layer explicitly



        """
        plugin.ngst2Layers(self.mesh, currentLayer=self.id)

    def set_weights(self, influence, weights_list, undo_enabled=True):
        """
        Modify weights in the layer.

        Attributes:
            influence: either index of an influence, or named paint target
            weights_list: weights for each vertex (must match number of vertices in skin cluster)
            undo_enabled: set to False if you don't need undo, for slight performance boost
        """
        self.__edit__(paintTarget=influence, vertexWeights=internals.floatListAsString(weights_list), undoEnabled=undo_enabled)

    def get_weights(self, influence):
        """
        get influence (or named paint target) weights for all vertices
        """
        result = self.__query__('vertexWeights', paintTarget=influence)
        if result is None:
            return []
        return [float(i) for i in result]

    def get_used_influences(self):
        """

        :rtype: list[int]
        """
        result = self.__query__('usedInfluences')
        return result or []


def as_layer_id(layer):
    if isinstance(layer, Layer):
        return layer.id

    return int(layer)


def as_layer_id_list(layers):
    return (as_layer_id(i) for i in layers)


def generate_layer_name(existing_layers, base_name):
    name = base_name
    currentLayerNames = [i.name for i in existing_layers]
    index = 1
    while name in currentLayerNames:
        index += 1
        name = base_name + " ({0})".format(index)

    return name


class Layers(Object):
    """
    Layers manages skinning layers on provided target (skinCluster or a mesh)

        :param target: name of skin cluster node or skinned mesh.
    """

    prune_weights_filter_threshold = internals.make_editable_property('pruneWeightsFilterThreshold')
    influence_limit_per_vertex = internals.make_editable_property('influenceLimitPerVertex')

    def __init__(self, target):
        if not target:
            raise Exception("target must be specified")

        self.__target = target
        self.__cached_data_node = None

    def add(self, name, forceEmpty=False, parent=None):
        """
        creates new layer with given name and returns it's ID; when forceEmpty flag is set to true,
        layer weights will not be populated from skin cluster.
        """
        layerId = plugin.ngst2Layers(self.mesh, name=name, add=True, forceEmpty=forceEmpty)
        result = Layer.load(self.mesh, layerId)
        result.parent = parent
        return result

    def delete(self, layer):
        plugin.ngst2Layers(self.mesh, removeLayer=True, id=as_layer_id(layer))

    def list(self):
        """

        returns all layers as Layer objects.
        """
        data = json.loads(plugin.ngst2Layers(self.mesh, q=True, listLayers=True))
        return [Layer(self.mesh, id=l['id'], state=l) for l in data]

    @undoable
    def clear(self):
        """
        delete all layers
        """
        with suspend_updates(self.data_node):
            for i in self.list():
                if i.parent_id is None:
                    self.delete(i)

    def list_influences(self):
        return target_info.list_influences(self.mesh)

    def current_layer(self):
        """
        get current layer that was previously marked as current with :py:meth:`Layer.set_current`.

        .. warning::
            Scheduled for removal. API calls should specify target layer explicitly

        """
        layerId = plugin.ngst2Layers(self.mesh, q=True, currentLayer=True)
        if layerId < 0:
            return None
        return Layer.load(self.mesh, layerId)

    def __edit__(self, **kwargs):
        plugin.ngst2Layers(self.mesh, e=True, **kwargs)

    def __query__(self, **kwargs):
        return plugin.ngst2Layers(self.mesh, q=True, **kwargs)

    def set_influences_mirror_mapping(self, influencesMapping):
        plugin.ngst2Layers(self.mesh, configureMirrorMapping=True, influencesMapping=internals.influencesMapToList(influencesMapping))

    @property
    def mesh(self):
        return self.__target

    def is_enabled(self):
        """
        returns true if skinning layers are enabled for the given mesh
        :return:
        """
        return get_layers_enabled(self.mesh)

    @property
    def data_node(self):
        if not self.__cached_data_node:
            self.__cached_data_node = target_info.get_related_data_node(self.mesh)
        return self.__cached_data_node

    @property
    def config(self):
        return Config(self.data_node)


def init_layers(target):
    """Attach ngSkinTools data node to given target. Does nothing if layers are already attached.

    Args:
        target (str): skin cluster or mesh node to attach layers to
    Returns:
        Layers: `Layers` instance to further query/modify layers data.
    """
    if not get_layers_enabled(target):
        plugin.ngst2Layers(target, layerDataAttach=True)

    return Layers(target)


def get_layers_enabled(selection):
    """
    return true if layers are enabled on this selection
    """
    return plugin.ngst2Layers(selection, q=True, lda=True)
