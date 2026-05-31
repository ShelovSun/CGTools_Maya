import os.path
from rig.check.util import utils
reload(utils)



BEAM_ITEM_ENV_KEY = "BEAM_COMPONENT_PATH"


def getComponentDirectories():
    """Get the item directory"""
    return utils.gatherCustomModuleDirectories(BEAM_ITEM_ENV_KEY, os.path.join(os.path.dirname(__file__), "item"))


def importComponentGuide(comp_type):
    """Import the item guide"""
    dirs = getComponentDirectories()
    defFmt = "rig.check.item.{}"
    customFmt = "{}"

    module = utils.importFromStandardOrCustomDirectories(dirs, defFmt, customFmt, comp_type)
    return module