import pymel.core as pm
import itertools

from ngSkinTools2.python_compatibility import Object
from ngSkinTools2.api import plugin, influenceMapping, target_info
from ngSkinTools2.api.layers import Layers
from ngSkinTools2.log import getLogger
from ngSkinTools2.options import config

log = getLogger("mirror")


class Mirror(Object):
    """
    query and configure mirror options for provided target
    """

    def __init__(self, target):
        """
        :type target: skin target (skinCluster or mesh)
        """
        self.target = target
        self.__skin_cluster__ = None
        self.__data_node__ = None

    def seam_width(self):
        return plugin.ngst2Layers(self.target, q=True, mirrorWidth=True)

    def set_seam_width(self, seam_width):
        plugin.ngst2Layers(self.target, configureMirrorMapping=True, mirrorWidth=seam_width)

    def vertex_transfer_mode(self):
        return plugin.ngst2Layers(self.target, q=True, vertexTransferMode=True)

    def set_vertex_transfer_mode(self, mode):
        plugin.ngst2Layers(self.target, configureMirrorMapping=True, vertexTransferMode=mode)

    def axis(self):
        # type: () -> str
        """

        :return: 'x', 'y', 'z' if layers available, otherwise None
        """
        return plugin.ngst2Layers(self.target, q=True, mirrorAxis=True)

    def set_axis(self, axis):
        plugin.ngst2Layers(self.target, configureMirrorMapping=True, mirrorAxis=axis)
        self.recalculate_influences_mapping()

    def __mapper_config_attr(self):
        return self.__get_data_node__().attr("influenceMappingOptions")

    def build_influences_mapper(self):
        from maya import cmds

        mapper = influenceMapping.InfluenceMapping()
        layers = Layers(self.target)
        mapper.influences = layers.list_influences()

        mapper.load_config_from_json(self.__mapper_config_attr().get() or config.mirrorInfluencesDefaults)
        mapper.config.mirror_axis = self.axis()

        return mapper

    def save_influences_mapper(self, mapper):
        """
        :type mapper: influenceMapping.InfluenceMapping
        """
        self.__mapper_config_attr().set(mapper.config_as_json())

    def set_influences_mapping(self, mapping):
        """
        :type mapping: map[int] -> int
        """
        log.info("mapping updated: %r", mapping)

        mapping_as_string = ','.join(str(k) + "," + str(v) for (k, v) in list(mapping.items()))
        plugin.ngst2Layers(self.target, configureMirrorMapping=True, influencesMapping=mapping_as_string)

    def recalculate_influences_mapping(self):
        """
        loads current influence mapping settings, and update influences mapping with these values
        """
        m = self.build_influences_mapper().calculate()
        self.set_influences_mapping(influenceMapping.InfluenceMapping.asIntIntMapping(m))

    def mirror(self, options):
        """
        :type options: MirrorOptions
        """
        plugin.ngst2Layers(
            self.target,
            mirrorLayerWeights=options.mirrorWeights,
            mirrorLayerMask=options.mirrorMask,
            mirrorLayerDq=options.mirrorDq,
            mirrorDirection=options.direction,
        )

    def set_reference_mesh(self, mesh_shape):
        dest = self.__get_data_node__().mirrorMesh

        if mesh_shape:
            shape = pm.PyNode(mesh_shape)
            shape.outMesh >> dest
        else:
            pm.disconnectAttr(dest)

    def get_reference_mesh(self):
        existing_inputs = self.__get_data_node__().attr('mirrorMesh').inputs()
        if existing_inputs:
            return existing_inputs[0]
        return None

    def __get_skin_cluster__(self):
        if self.__skin_cluster__ is None:
            self.__skin_cluster__ = pm.PyNode(target_info.get_related_skin_cluster(self.target))
        return self.__skin_cluster__

    def __get_data_node__(self):
        if self.__data_node__ is None:
            self.__data_node__ = pm.PyNode(target_info.get_related_data_node(self.target))
        return self.__data_node__

    # noinspection PyStatementEffect
    def build_reference_mesh(self):
        sc = self.__get_skin_cluster__()
        dn = self.__get_data_node__()

        if sc is None or dn is None:
            return

        existing_ref_mesh = self.get_reference_mesh()
        if existing_ref_mesh:
            pm.select(existing_ref_mesh)
            raise Exception("symmetry mesh already configured for %s: %s" % (str(sc), existing_ref_mesh.longName()))

        g = pm.group(empty=True, name="ngskintools_mirror_mesh_setup")
        result, _ = pm.polyCube()
        pm.parent(result, g)
        result.rename("mirrorSymmetryMesh")

        pm.delete(result, ch=True)
        sc.input[0].inputGeometry >> result.getShape().inMesh
        pm.delete(result, ch=True)

        (mirrored,) = pm.duplicate(result)
        mirrored.rename('flipped_preview')
        mirrored_shape = mirrored.getShape()

        mirrored.sx.set(-1)
        mirrored.overrideEnabled.set(1)
        mirrored.overrideDisplayType.set(2)
        mirrored.overrideShading.set(0)
        mirrored.overrideTexturing.set(1)

        (blend,) = pm.blendShape(result, mirrored_shape)
        blend.weight[0].set(1.0)

        # lock accidental transformations
        for c, t, m in itertools.product('xyz', 'trs', (result, mirrored)):
            m.attr(t + c).lock()

        # shift setup to the right by slightly more than bounding box width
        bb = pm.exactWorldBoundingBox(g)
        pm.move((bb[3] - bb[0]) * 1.2, 0, 0, g, r=True)

        self.set_reference_mesh(str(result))
        pm.select(result)
        return result


class MirrorOptions(Object):
    directionNegativeToPositive = 0
    directionPositiveToNegative = 1
    directionGuess = 2
    directionFlip = 3

    def __init__(self):
        self.mirrorWeights = True
        self.mirrorMask = True
        self.mirrorDq = True
        self.direction = MirrorOptions.directionPositiveToNegative


def set_reference_mesh_from_selection():
    selection = pm.ls(sl=True)

    if len(selection) != 2:
        log.debug("wrong selection size")
        return

    m = Mirror(selection[1].longName())
    m.set_reference_mesh(selection[0].longName())
