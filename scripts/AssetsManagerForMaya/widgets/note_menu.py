#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide2 import QtGui
from PySide2 import QtWidgets


class NoteMenuWidget(QtWidgets.QWidget):
    """ 中文名控键 """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtGui.Qt.Dialog | QtGui.Qt.FramelessWindowHint)
        self._itemsWidget = None
        # self.setVisible(False)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.line = QtWidgets.QLineEdit(self)
        self.line.setMinimumHeight(28)
        self.line.returnPressed.connect(self.note_edit_finished)

        self.layout.addWidget(self.line)

        self.setLayout(self.layout)
        # self.setStyleSheet("background-color: rgb(240, 240, 240)")

    def note_edit_finished(self):
        # print(self.text())
        self.itemsWidget().zh_name_changed(self.line.text())

    def setItemsWidget(self, wgt):
        """
        set the items widget
        """
        self._itemsWidget = wgt

    def itemsWidget(self):
        """
        Returns the items widget that contains the items.    得到 itemWidget
        :rtype: ItemsWidget
        """
        return self._itemsWidget

    def setUp(self, exist_text):
        """ 打开 """
        self.show()
        self.line.setText(exist_text)
        # self.construct_tree(exist_name)


class MovMenuWidget(NoteMenuWidget):
    """ 任务控键 """
    def __init__(self, parent=None):
        super().__init__(parent)

    def note_edit_finished(self):
        # print(self.text())
        self.itemsWidget().update_mov(self.line.text())
