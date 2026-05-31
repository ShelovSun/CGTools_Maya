from ngSkinTools2.api import plugin
from . import transfer
from .influenceMapping import InfluenceMappingConfig


def import_json(
    target, file, vertex_transfer_mode=transfer.VertexTransferMode.closestPoint, influences_mapping_config=InfluenceMappingConfig.transfer_defaults()
):
    """
    Transfer layers from file into provided target mesh. Existing layers, if any, will be preserved

    :param str target: destination mesh or skin cluster node name
    :param str file: file path to load json from
    :param InfluenceMappingConfig influences_mapping_config:
    """

    importer = transfer.LayersTransfer()
    importer.vertex_transfer_mode = vertex_transfer_mode
    importer.influences_mapping.config = influences_mapping_config
    importer.load_source_from_file(file)
    importer.target = target
    importer.execute()


def export_json(target, file):
    """
    Save skinning layers to file in json format, to be later used in `import_json`

    :param str target: source mesh or skin cluster node name
    :param str file: file path to save json to
    """

    plugin.ngst2tools(
        tool="exportJsonFile",
        target=target,
        file=file,
    )
