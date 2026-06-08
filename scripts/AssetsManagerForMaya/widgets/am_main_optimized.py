#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
优化后的 MainStackedWidget
整合新的高性能 ItemsWidget
"""

from PySide2 import QtCore
from PySide2 import QtWidgets
from widgets.am_items_widget import ItemsWidget


class MainStackedWidget(QtWidgets.QStackedWidget):
    """
    优化后的主窗切换窗
    使用新的高性能 ItemsWidget
    """

    dragLeaveSignal = QtCore.Signal()
    itemSelectionChanged = QtCore.Signal()

    def __init__(self, db="FFA", tab="Asset", user="", password="", islist=False):
        super(MainStackedWidget, self).__init__()

        self._db = db
        self._tab = tab
        self._user = user
        self._password = password
        self._is_list = islist

        # 创建新的高性能 ItemsWidget
        self._items_widget = ItemsWidget(
            self,
            db=self._db,
            tab=self._tab,
            user=self._user,
            password=self._password
        )

        # 连接信号
        self._items_widget.itemSelectionChanged.connect(self.itemSelectionChanged.emit)
        self._items_widget.dragLeaveSignal.connect(self.dragLeaveSignal.emit)
        # 右键菜单上抛：子视图 -> ItemsWidget -> MainStackedWidget
        # （QStackedWidget 从 QWidget 继承了 customContextMenuRequested 信号）
        self._items_widget.customContextMenuRequested.connect(self.customContextMenuRequested)

        # 设置当前视图模式
        self._items_widget.setIsList(islist)

        # 添加到堆叠布局
        self.addWidget(self._items_widget)

    def setItemsWidget(self, widget):
        """设置外部关联的 items widget（用于兼容旧代码）"""
        self._items_widget.setItemsWidget(widget)

    def itemsWidget(self):
        """获取 items widget"""
        return self._items_widget

    def dragLeaveSignal_connect(self, func):
        """连接拖拽离开信号"""
        self.dragLeaveSignal.connect(func)

    def itemSelectionChanged_connect(self, func):
        """连接选择改变信号"""
        self.itemSelectionChanged.connect(func)

    def clear(self):
        """清空"""
        self._items_widget.clear()

    def itemCount(self):
        """获取 item 数量"""
        return self._items_widget.itemCount()

    def itemAt(self, point):
        """获取指定位置的 item"""
        return self._items_widget.itemAt(point)

    def selectedItems(self):
        """获取选中的 items"""
        return self._items_widget.selectedItems()

    def currentItem(self):
        """获取当前 item"""
        return self._items_widget.currentItem()

    def setIconMode(self, item_size, keywords=None):
        """设置为图标模式"""
        self._is_list = False
        self._items_widget.setIconMode(item_size, keywords)

    def setListMode(self, keywords=None):
        """设置为列表模式"""
        self._is_list = True
        self._items_widget.setListMode(keywords)

    def itemsList(self):
        """获取数据列表"""
        return self._items_widget.itemsList()

    def setItemsList(self, items_list):
        """设置数据列表"""
        self._items_widget.setItemsList(items_list)

    def isList(self):
        """是否为列表模式"""
        return self._is_list

    def setIsList(self, value):
        """设置是否为列表模式"""
        self._is_list = value
        self._items_widget.setIsList(value)

    def itemSize(self):
        """获取 item 尺寸"""
        return self._items_widget.itemSize()

    def setItemSize(self, item_size):
        """设置 item 尺寸"""
        self._items_widget.setItemSize(item_size)

    def resizeItem(self):
        """调整 item 尺寸"""
        self._items_widget.resizeItem()

    def addItem(self, data):
        """添加单个 item"""
        self._items_widget.addItem(data)

    def addItems(self, keywords=None, add=False):
        """批量添加 items"""
        if isinstance(keywords, list):
            keywords = keywords[0] if keywords else ""
        self._items_widget.addItems(keywords, add)

    def currentAsset(self):
        """获取当前资产名"""
        return self._items_widget.currentAsset()

    def clearSelection(self):
        """清除选择"""
        self._items_widget.clearSelection()

    def setFocus(self):
        """设置焦点"""
        self._items_widget.setFocus()

    def closeMenus(self):
        """关闭表格视图弹出的制作人/中文名面板"""
        self._items_widget.closeMenus()
