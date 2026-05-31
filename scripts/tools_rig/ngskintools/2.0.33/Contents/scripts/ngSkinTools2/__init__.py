import os

from ngSkinTools2.ui.paintContextCallbacks import definePaintContextCallbacks

DEBUG_MODE = os.getenv("NGSKINTOOLS_DEBUG", 'false') == 'true'


def open_ui():
    """
    opens ngSkinTools2 main UI window. if the window is already open, brings that workspace
    window to front.
    """

    from ngSkinTools2.ui import mainwindow

    mainwindow.open()


def workspace_control_main_window():
    """
    this function is used permanently by Maya's "workspace control", and acts as an alternative top-level entry point to open UI
    """
    from ngSkinTools2.ui import mainwindow

    mainwindow.resume_in_workspace_control()


definePaintContextCallbacks()
