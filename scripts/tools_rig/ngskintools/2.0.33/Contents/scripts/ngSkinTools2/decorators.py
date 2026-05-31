from functools import wraps

from maya import cmds
from ngSkinTools2.log import getLogger
from ngSkinTools2.python_compatibility import Object

log = getLogger("decorators")


def preserveSelection(function):
    """
    decorator for function;
    saves selection prior to execution and restores it
    after function finishes
    """

    @wraps(function)
    def undoableWrapper(*args, **kargs):
        selection = cmds.ls(sl=True, fl=True)
        highlight = cmds.ls(hl=True, fl=True)
        try:
            return function(*args, **kargs)
        finally:
            if selection:
                cmds.select(selection)
            else:
                cmds.select(clear=True)
            if highlight:
                cmds.hilite(highlight)

    return undoableWrapper


def undoable(function):
    """
    groups function contents into one undo block
    """

    @wraps(function)
    def result(*args, **kargs):
        with Undo():
            return function(*args, **kargs)

    return result


class Undo(Object):
    """
    an undo context for use "with Undo():"
    """

    def __enter__(self):
        log.debug("UNDO chunk: start")
        cmds.undoInfo(openChunk=True)
        return self

    def __exit__(self, _type, value, traceback):
        log.debug("UNDO chunk: end")
        cmds.undoInfo(closeChunk=True)


def traceException(function):
    @wraps(function)
    def result(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except:
            import sys
            import traceback

            traceback.print_exc(file=sys.__stderr__)
            raise

    return result
