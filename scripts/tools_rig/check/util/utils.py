"""Utilitie functions"""


import os
import sys
from functools import wraps

from maya import cmds
import pymel.core as pm
from maya import mel

def gatherCustomModuleDirectories(envvarkey,
                                  defaultModulePath,
                                  component=False):
    """returns component directory

    Arguments:
        envvarkey: The environment variable key name, that is searched
        defaultModulePath: The default module path for search in.

    Returns:
        Dict{string: []string}

    """
    results = {}

    # default path
    if not os.path.exists(defaultModulePath):
        message = "= GEAR RIG SYSTEM ====== notify:"
        message += "\n  default module directory is not " \
                   "found at {}".format(defaultModulePath)
        message += "\n\n check your mGear installation"
        message += " or call your system administrator."
        message += "\n"
        log(message, sev_error)
        return {}

    modules = sorted(module for module in os.listdir(defaultModulePath) if module.endswith(".py"))
    results[defaultModulePath] = modules

    # from environment variables
    envvarval = os.environ.get(envvarkey, "")
    for path in envvarval.split(os.pathsep):

        if not path or not os.path.exists(path):
            continue
        if component:
            init_py_path = os.path.join(path, "__init__.py")
            if not os.path.exists(init_py_path):
                message = "= GEAR RIG SYSTEM ====== notify:"
                message += "\n  __init__.py for custom component not " \
                           "found {}".format(init_py_path)
                message += "\n\n check your module definition file or " \
                           "environment variable 'MGEAR_COMPONENTS_PATH'"
                message += " or call your system administrator."
                message += "\n"
                log(message, sev_error)
                continue

        modules = sorted(module for module in os.listdir(defaultModulePath) if module.endswith(".py"))
        modules = [x for x in modules if os.path.isdir(os.path.join(path, x))]

        results[path] = modules

    return results

def getModuleBasePath(directories, moduleName):
    """search component path"""

    for basepath, modules in directories.items():
        if moduleName in modules:
            # moduleBasePath = os.path.basename(basepath)
            moduleBasePath = basepath
            break
    else:
        moduleBasePath = ""
        message = "= GEAR RIG SYSTEM ======"
        message += "component base directory not found " \
                   " for {}".format(moduleName)
        log(message, sev_error)

    return moduleBasePath


def importFromStandardOrCustomDirectories(directories,
                                          defaultFormatter,
                                          customFormatter,
                                          moduleName):
    """Return imported module

    Arguments:
        directories: the directories for search in. this is got by
            gatherCustomModuleDirectories
        defaultFormatter: this represents module structure for default
            module. for example "maya.shifter.component.{}"
        customFormatter:  this represents module structure for custom
            module. for example "{0}.{1}"

    Returns:
        module: imported module

    """
    # Import module and get class
    try:
        module_name = defaultFormatter.format(moduleName)
        module = __import__(module_name, globals(), locals(), ["*"], -1)

    except ImportError:
        moduleBasePath = getModuleBasePath(directories, moduleName)
        module_name = customFormatter.format(moduleName)
        sys.path.append(pm.dirmap(cd=moduleBasePath))
        module = __import__(module_name, globals(), locals(), ["*"], -1)

    return module