import sys
sys.path.append(r"E:\Beam_tools\tools\toolset\tool")

from ..ui.head import *
import maya.OpenMayaUI as OpenMayaUI
#from PyQt4 import QtGui,QtCore
try:
    import shiboken2
except:
    import shiboken

def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    try:
        warp = shiboken2.wrapInstance (long (ptr), QWidget)
    except:
        warp = shiboken.wrapInstance (long (ptr), QWidget)
    return warp

def MayaLoadWindow(step=""):
    for win in QApplication.topLevelWidgets():
        if not hasattr(win,'isWindow'):
            continue
        if not win.isWindow():
            continue
        if win.windowTitle() == "NZTF_check_tool":
            win.setParent(None)
            win.deleteLater()
    maya_win = getMayaWindow()
    beamWindow = ShowWindow(maya_win)
    return beamWindow

def ShowWindow(maya_win,step=""):
    from ..core import check_form as check_form
    reload(check_form)
    beamWindow = check_form.From(maya_win)
    beamWindow.show()
    return beamWindow

if __name__=="__main__":
    app = QApplication(sys.argv)
    ui = ShowWindow()
    sys.exit(app.exec_())