import sys
from gen.rename.ui.head import *
import maya.cmds as cmds
import maya.OpenMayaUI as apiUI
try:
    import shiboken2
except:
    import shiboken

#get maya windownhange pyqt lib
def getMayaWindow():
      ptr = apiUI.MQtUtil.mainWindow()
      try:
          wrap=shiboken2.wrapInstance(long(ptr), QWidget)
      except:
          wrap = shiboken.wrapInstance(long(ptr), QWidget)

      return wrap

def MayaLoadWindow():
    app = QApplication.instance()
    if not app:
        app=QApplication([])
    for wnd in app.topLevelWidgets():
        # if not hasattr(wnd, 'isWindow'): continue  # if zhe windown is Exist
        # if not wnd.isWindow(): continue
        if wnd.objectName() == 'batch_copyskin':  # if zhe windwon name is you windownn name
            #wnd.setParent(None)
            wnd.close()
            #wnd.deleteLater()
            '''
            wnd.show()#show window 
            wnd.activateWindow()#active windwon 
            '''
    maya_win=getMayaWindow()
    myWindow = ShowWindow(maya_win)  # if do not have windown and creat it
    return myWindow


def ShowWindow(maya_win):
    import rig.batch_copyskin.core.response as response
    reload(response)
    myWindow = response.Response(maya_win)
    myWindow.show()
    return myWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    A = ShowWindow()
    sys.exit(app.exec_())

'''
import sys
sys.path.insert(0, r"E:\git_work\new_ple\rc_publish")
import publish.main.maya_load_win as maya_load_win
reload(maya_load_win)
ui = maya_load_win.MayaLoadWind()
import sys
sys.path.insert(0, r"D:\git_work\rc_publish")
import publish.main.maya_load_win as maya_load_win
reload(maya_load_win)
ui = maya_load_win.MayaLoadWind()

import sys
sys.path.insert(0, r"D:\_hexin\rc_tool\tools\rc_publish")
import publish.main.maya_load_win as maya_load_win
reload(maya_load_win)
ui = maya_load_win.MayaLoadWind('srf')

'''