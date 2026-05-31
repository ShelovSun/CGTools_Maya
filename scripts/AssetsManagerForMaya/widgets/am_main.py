#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

from PySide2 import QtCore
from PySide2 import QtWidgets
from widgets import am_listWidget
from widgets import am_tableWidget

# import importlib
# importlib.reload(listWidget)
# importlib.reload(tableWidget)


class MainStackedWidget(QtWidgets.QStackedWidget):
    """ 主窗切换窗  """
    dragLeaveSignal = QtCore.Signal()
    itemSelectionChanged = QtCore.Signal()

    def __init__(self, db="FFA", tab="Asset", user="", password="", islist=False):
        super(MainStackedWidget, self).__init__()
        self.db = db
        self._tab = tab
        self.user = user
        self.password = password
        self._isList = islist

        self._list_wgt = am_listWidget.MainListWidget(db=self.db, tab=self._tab, user=self.user, password=self.password)
        self._list_wgt.setDragEnabled(False)
        self._table_wgt = am_tableWidget.MainTableWidget(db=self.db, tab=self._tab, user=self.user, password=self.password)
        self._table_wgt.setItemsWidget(self)

        self._itemsList = []
        self._itemsWidget = None
        self._itemSize = 120
        self._currentItem = None
        # layout = QtWidgets.QHBoxLayout(self)
        # layout.setContentsMargins(0, 0, 0, 0)
        self.addWidget(self._list_wgt)
        self.addWidget(self._table_wgt)
        # self.setLayout(layout)
        if not self._isList:
            self.setCurrentWidget(self._list_wgt)
        else:
            self.setCurrentWidget(self._table_wgt)

    def setItemsWidget(self, wgt):
        """
        set the items widget
        """
        self._itemsWidget = wgt

    def itemsWidget(self):
        """
        Returns the items widget that contains the items. 得到 itemWidget
        :rtype: ItemsWidget
        """
        return self._itemsWidget

    def dragLeaveSignal_connect(self, fanc):
        self._list_wgt.dragLeaveSignal.connect(fanc)
        self._table_wgt.dragLeaveSignal.connect(fanc)

    def itemSelectionChanged_connect(self, fanc):
        self._list_wgt.itemSelectionChanged.connect(fanc)
        self._table_wgt.itemSelectionChanged.connect(fanc)

    def clear(self):
        print("clear")
        self._list_wgt.clear()
        self._table_wgt.clearContents()
        self._table_wgt.setRowCount(0)

    def itemCount(self):
        if self.currentWidget() == self._list_wgt:
            return self._list_wgt.count()
        else:
            return self._table_wgt.rowCount()

    def itemAt(self, point):
        if self.currentWidget() == self._list_wgt:
            return self._list_wgt.itemAt(point)
        else:
            print(self._table_wgt.itemAt(point))   # point有问题
            return self._table_wgt.itemAt(point)

    def selectedItems(self):
        if self.currentWidget() == self._list_wgt:
            return self._list_wgt.selectedItems()
        else:
            return self._table_wgt.selectedItems()

    def currentItem(self):
        if self.currentWidget() == self._list_wgt:
            return self._list_wgt.currentItem()
        else:
            return self._table_wgt.currentItem()

    def setIconMode(self, itemSize, keyWords=[]):
        self.setCurrentWidget(self._list_wgt)
        self._list_wgt.setItemList(self._itemsList)
        self._list_wgt.addItems(keyWords[0])
        self._list_wgt.setItemSize(itemSize)
        self._list_wgt.resizeItem()
        # if len(keyWords) == 1:
        #     self._list_wgt.addItems(keyWords[0])
        # else:
        #     for key in keyWords:
        #         self._list_wgt.addItems(key, add=True)

    def setListMode(self, keyWords=[]):
        self.setCurrentWidget(self._table_wgt)
        self._table_wgt.setItemList(self._itemsList)
        if len(keyWords) == 1:
            self._table_wgt.addItems(keyWords[0])
        else:
            for key in keyWords:
                self._table_wgt.addItems(key, add=True)

    def itemsList(self):
        return self._itemsList

    def setItemsList(self, _list):
        self._itemsList = _list

    def isList(self):
        return self._isList

    def setIsList(self, value):
        self._isList = value
        # self._list_wgt.setIsList(value)

    def itemSize(self):
        return self._list_wgt.itemSize()

    def setItemSize(self, itemSize):
        if not self._isList:
            self._list_wgt.setItemSize(itemSize)

    def resizeItem(self):
        if not self._isList:
            self._list_wgt.resizeItem()

    def addItem(self, data):
        if not self._isList:
            self._list_wgt.add_item(data)
        else:
            self._table_wgt.add_item(data)

    def addItems(self, keyWords=u"", add=False):
        """
        Add the given items to this widget.
        :param add: bool
        :param keyWords:str
        """
        if not self._isList:
            self._list_wgt.setItemList(self._itemsList)
            self._list_wgt.addItems(keyWords, add)
        else:
            self._table_wgt.setItemList(self._itemsList)
            self._table_wgt.addItems(keyWords, add)

    def currentAsset(self):
        if self._isList:
            return self._table_wgt.item(self._table_wgt.row(self._table_wgt.selectedItems()[0]), 1).text()
        else:
            return self._list_wgt.selectedItems()[0].text()
