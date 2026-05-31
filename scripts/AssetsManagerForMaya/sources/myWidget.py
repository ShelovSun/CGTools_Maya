#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from my_vendor import six
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets


class MyThread(QtCore.QThread):

    _signal = QtCore.Signal()

    def __init__(self):
        super(MyThread, self).__init__()

    def run(self):
        self._signal.emit()


class MyListModel(QtCore.QAbstractListModel):

    def __init__(self, itemsDict={}, allNum = 0, parent = None):
        QtCore.QAbstractListModel.__init__(self, parent)
        self.__allNum = allNum
        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')
        self.__realDict = itemsDict
        self.__newDict = {}
        self.makeNewDict()

    def makeNewDict(self):
        icon_path = "%s/icon/blank_ch.png" % self.scriptsPath
        for k in self.__realDict.keys():
            self.__newDict.update({k:icon_path})
        return self.__newDict

    def rowCount(self, parent):
        return self.__allNum

    def data(self, index, role):

        if role == QtCore.Qt.DisplayRole:
            row = index.row()
            value = self.__realDict.keys()[row].replace('   /   ','\n')
            return value

        if role == QtCore.Qt.DecorationRole:
            row = index.row()
            icon_path = self.__realDict.values()[row]
            pixmap = QtGui.QPixmap(icon_path)
            icon = QtGui.QIcon(pixmap)
            return icon

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def updateRows(self,position,rows):
        pass

    def insertRows(self, position, rows, parent=QtCore.QModelIndex()):
        print("+++++++++++++++insertRows+++++++++")
        self.beginInsertRows(parent, position, position + rows - 1)
        print(self.__newDict)
        for i in range(rows):
            position  += 1
            aaa = self.__newDict.keys()[position-1]
            value = self.__oldDict[aaa]
            print(aaa,value)
            self.__newDict[aaa] = value
            print("******__newDict*******:",self.__newDict)
        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent=QtCore.QModelIndex()):
        print("removeRows", position, rows)
        self.beginRemoveRows(parent, position, position + rows - 1)
        for i in range(rows):
            value = self.__icon[position]
            aaa = self.__tex[position]
            print(aaa, value)
            self.__icon.remove(value)
        self.endRemoveRows()
        return True

    def setData(self, index, value, role=QtCore.Qt.EditRole):
        if role == QtCore.Qt.EditRole:
            self.dataChanged.emit(index, index)  # 告诉其他view这个model改变了
            return True
        return False


class MyDelegate(QtWidgets.QAbstractItemDelegate):

    def __init__(self, wgt, parent=None):
        super().__init__(parent)
        self.__wgt = wgt

    def createEditor(self, parent, option, index):
        '''用于创建数据编辑界面所用的部件'''
        wdgt = self.__wgt
        return wdgt

    def setEditorData(self, editor, index):
        '''用于从模型获取编辑前的原数据，并加载至编辑部件'''
        value = index.model().data(index, QtCore.Qt.DisplayRole)
        editor.setText(str(value))

    def setModelData(self, editor, model, index):
        '''当编辑结束时，调用其实现将修改后的数据更新至数据库。其实，它是通过调用Model中的setData()实现数据的更新'''
        model.setData(index, editor.text())

    def paint(self, painter, option, index):
        pass

class MyQListWiget(QtWidgets.QListWidget):

    _dragSignal = QtCore.Signal()
    _sizeSignal = QtCore.Signal()
    _wheelSignal = QtCore.Signal()

    def __init__(self):
        super(MyQListWiget, self).__init__()

    def dragLeaveEvent(self, e):
        self._dragSignal.emit()

    # def mouseMoveEvent(self, e):
    #     print("hahahhahahah")
    #     if e.type() == QtCore.QEvent.HoverEnter:
    #         item = self.itemAt(e.pos())
    #         if item:
    #             print(item)

    def resizeEvent(self, e):
        super(MyQListWiget, self).resizeEvent(e)
        self._sizeSignal.emit()

    def wheelEvent(self, e):
        super(MyQListWiget, self).wheelEvent(e)
        self._wheelSignal.emit()

    # def eventFilter(self, receiver, event):
    #     self.receiver = receiver
    #     self.mouse_button = QtWidgets.QApplication.mouseButtons()
    #     if event.type() == QtCore.QEvent.Enter:
    #         print("Enter")
            # return True
    #     elif event.type() == QtCore.QEvent.Leave:
    #         print("Leave")
    #         return True
    #     return False

class MyQListView(QtWidgets.QListView):

    _dragSignal = QtCore.Signal()
    _sizeSignal = QtCore.Signal()
    _wheelSignal = QtCore.Signal()

    def __init__(self):
        super(MyQListView, self).__init__()

    def dragLeaveEvent(self, e):
        self._dragSignal.emit()

    # def mouseMoveEvent(self, e):
    #     if e.buttons() == QtCore.Qt.LeftButton:
    #         print("hahahaha")

    def resizeEvent(self, e):
        super(MyQListView, self).resizeEvent(e)
        self._sizeSignal.emit()

    def wheelEvent(self, e):
        super(MyQListView, self).wheelEvent(e)
        self._wheelSignal.emit()

    def itemAt(self):
        pass


class Mylabel(QtWidgets.QLabel):

    def __init__(self, iconPath = ""):
        super(Mylabel, self).__init__()
        self.iconPath = iconPath
        self.pixmap = QtGui.QPixmap(self.iconPath)
        self.setPixmap(self.pixmap)

    def wheelEvent(self, e):
        super(Mylabel, self).resizeEvent(e)
        if self.iconPath == "":
            return


class WorkerSignals(QtCore.QObject):
    triggered = QtCore.Signal(object)


class ImageWorker(QtCore.QRunnable):
    """A convenience class for loading an image in a thread."""

    def __init__(self, *args):
        QtCore.QRunnable.__init__(self, *args)

        self._path = None
        self.signals = WorkerSignals()

    def setPath(self, path):
        """
        Set the image path to be processed.

        :type path: str
        """
        self._path = path

    def run(self):
        """The starting point for the thread."""
        try:
            if self._path:
                image = QtGui.QImage(six.text_type(self._path))
                self.signals.triggered.emit(image)
        except Exception as error:
            print("Cannot load thumbnail image:%s"%error)



class Pixmap(QtGui.QPixmap):

    def __init__(self, *args):
        QtGui.QPixmap.__init__(self, *args)
        self._color = None

    def setColor(self, color):
        """
        给pixmap着色
        :type color: QtGui.QColor
        :rtype: None
        """
        if not self.isNull():
            painter = QtGui.QPainter(self)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
            painter.setBrush(color) # 定义用于填充形状的颜色或图案
            painter.setPen(color) # 定义用于绘制线条或边界的颜色或点画
            painter.drawRect(self.rect())
            painter.end()