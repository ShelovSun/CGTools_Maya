import os

realPath = os.path.dirname(os.path.realpath(__file__))
iconPath = os.path.join(realPath, 'images')

import maya.cmds as cmds
from PySide import QtGui, QtCore
from maya import OpenMayaUI as omui
from mayaMixin import *

import log

import struct
import imghdr

def get_image_size(fname):
    '''Determine the image type of fhandle and return its size.
    from draco'''
    with open(fname, 'rb') as fhandle:
        head = fhandle.read(24)
        if len(head) != 24:
            return
        if imghdr.what(fname) == 'png':
            check = struct.unpack('>i', head[4:8])[0]
            if check != 0x0d0a1a0a:
                return
            width, height = struct.unpack('>ii', head[16:24])
        elif imghdr.what(fname) == 'gif':
            width, height = struct.unpack('<HH', head[6:10])
        elif imghdr.what(fname) == 'jpeg':
            try:
                fhandle.seek(0)  # Read 0xff next
                size = 2
                ftype = 0
                while not 0xc0 <= ftype <= 0xcf:
                    fhandle.seek(size, 1)
                    byte = fhandle.read(1)
                    while ord(byte) == 0xff:
                        byte = fhandle.read(1)
                    ftype = ord(byte)
                    size = struct.unpack('>H', fhandle.read(2))[0] - 2
                # We are at a SOFn block
                fhandle.seek(1, 1)  # Skip `precision' byte.
                height, width = struct.unpack('>HH', fhandle.read(4))
            except Exception:  # IGNORE:W0703
                return
        else:
            return
        return width, height



class loaderWindow(QtGui.QMainWindow):
    def __init__(self, rootWidget=None, *args, **kwargs):
        super(loaderWindow, self).__init__(*args, **kwargs)

        # Determine root widget to scan
        if rootWidget != None:
            self.rootWidget = rootWidget
        else:
            mayaMainWindowPtr = omui.MQtUtil.mainWindow()
            self.rootWidget = wrapInstance(long(mayaMainWindowPtr), QtGui.QWidget)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)

        self.parent = self.rootWidget

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")


        #create a widget
        widget = QtGui.QWidget()
        self.setCentralWidget(widget)
        #broRigDancingWindow.setStyleSheet ('background-color:rgb(54,54,54);')

        self.setWindowTitle ("Bro Working...")


        #create layouts
        layout = QtGui.QVBoxLayout(widget)
        #create gif
        moviePath = os.path.join(realPath, 'images', 'loader.gif')
        self.mw, self.mh = get_image_size(moviePath)

        self.logo = QtGui.QLabel ("")
        #self.logo.setMinimumSize (self.mw,self.mh)
        #self.logo.setMaximumSize (self.mw,self.mh)
        self.setMinimumSize (self.mw,self.mh)
        self.setMaximumSize (self.mw,self.mh)
        self.movie = QtGui.QMovie (moviePath)

        self.movie.setScaledSize(QtCore.QSize(5,5))
        self.setWindowOpacity(0)


        self.logo.setMovie(self.movie)
        self.movie.start()
        layout.addWidget(self.logo)
        #self.setWindowOpacity(0.85)

        self.startPosition = self.pos()


        #self.resize(new_widget.size())
        self.show()


    def animateIn(self, value):
        outVal = 0.0 + value
        sizeVal = outVal*(self.mh*0.7)
        self.move(self.pos().x()+outVal, self.pos().y()+outVal)
        self.setWindowOpacity(outVal)

        self.movie.setScaledSize(QtCore.QSize(sizeVal, sizeVal))



    def animateOut(self, value):
        outVal = 1.0 - value
        sizeVal = outVal*(self.mh*0.7)
        self.move(self.pos().x()+outVal, self.pos().y()+outVal)
        self.setWindowOpacity(outVal)
        self.movie.setScaledSize(QtCore.QSize(sizeVal, sizeVal))
        self.resize (outVal, outVal)


    def dockCloseEventTriggered(self):
        log.log("/", "Loader closing.")
        self.close()

    def closeEvent(self, evt):
        '''Hide the QDockWidget and trigger the closeEventTriggered signal
        '''

        if evt.isAccepted():
            self.deleteLater()

    def showMe (self):
        self.show()
        '''
        self.timeline = QtCore.QTimeLine()
        self.timeline.valueChanged.connect(self.animateIn)
        self.timeline.setDuration(333)
        self.timeline.start()'''

    def hide(self):
        self.timeline = QtCore.QTimeLine()
        self.timeline.valueChanged.connect(self.animateOut)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(250)
        self.timeline.start()

    def showEvent(self, event):
        self.timeline = QtCore.QTimeLine()
        self.timeline.valueChanged.connect(self.animateIn)
        self.timeline.setDuration(500)
        self.timeline.start()

        event.accept()


            
            
def initUI():
    global broLoader_WindowName
    broLoader_WindowName = "broLoaderWindow"

    global broLoader_Window

    if cmds.window(broLoader_WindowName, ex=True):
        cmds.deleteUI (broLoader_WindowName, wnd=True)

    broLoader_Window = loaderWindow()
    broLoader_Window.setObjectName("autoIkFkSwitcher_Window")
    broLoader_Window.show()

    log.log (":", "UI initialized.")

