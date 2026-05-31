#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高性能 ItemsWidget 组件
整合 ListView 和 TableWidget，提供统一的接口
参考 StudioLibrary 的 ItemsWidget 实现
"""

import logging
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from widgets.am_list_view import ListView
from widgets.am_list_item_optimized import ListItemOptimized
from widgets.am_thumbnail_loader import ThumbnailLoader

logger = logging.getLogger(__name__)


class TableItemDelegate(QtWidgets.QStyledItemDelegate):
    """表格项委托"""

    def __init__(self, parent=None):
        super(TableItemDelegate, self).__init__(parent)
        self._table_widget = None

    def setTableWidget(self, table_widget):
        self._table_widget = table_widget

    def paint(self, painter, option, index):
        item = self._table_widget.itemFromIndex(index) if self._table_widget else None
        if item and hasattr(item, 'paint'):
            item.paint(painter, option, index)
        else:
            super(TableItemDelegate, self).paint(painter, option, index)


class TableWidget(QtWidgets.QTableWidget):
    """
    高性能表格组件
    """

    itemSelectionChanged = QtCore.Signal()
    dragLeaveSignal = QtCore.Signal()

    table_header = ["创建日期", "资产名", "中文名", "模型制作", "模型状态", "绑定制作", "绑定状态", "备注"]

    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)

        self._items_list = []
        self._items_widget = None

        self.setColumnCount(len(self.table_header))
        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 190)
        self.setColumnWidth(2, 120)
        self.setColumnWidth(3, 60)
        self.setColumnWidth(4, 60)
        self.setColumnWidth(5, 60)
        self.setColumnWidth(6, 60)
        self.setColumnWidth(7, 80)

        # 字体
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        self.setFont(font)

        self.setHorizontalHeaderLabels(self.table_header)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setMinimumHeight(25)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setFont(font)
        self.horizontalHeader().sectionClicked.connect(self.sortByColumn)

        self.verticalHeader().setVisible(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # 延迟加载
        self._load_timer = QtCore.QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(self._loadVisibleItems)

        self.verticalScrollBar().valueChanged.connect(self._onScroll)

    def setItemsWidget(self, widget):
        self._items_widget = widget

    def itemsWidget(self):
        return self._items_widget

    def setItemsList(self, items_list):
        self._items_list = items_list

    def addItem(self, data):
        """添加单个 item"""
        row = self.rowCount()
        self.insertRow(row)

        for col, value in enumerate(data[:8]):  # 只取前8列
            if col < len(self.table_header):
                from widgets import am_tableItem
                if col == 3:
                    item = am_tableItem.TableModArtistItem(str(value))
                elif col == 4:
                    item = am_tableItem.TableStatusItem(str(value))
                elif col == 5:
                    item = am_tableItem.TableRigArtistItem(str(value))
                elif col == 6:
                    item = am_tableItem.TableStatusItem(str(value))
                else:
                    item = am_tableItem.TableItem(str(value))

                item.setItemData(data)
                item.setItemsWidget(self)
                self.setItem(row, col, item)

    def addItems(self, keyword="", add=False):
        """批量添加 items"""
        if not add:
            self.clearContents()
            self.setRowCount(0)

        keyword_lower = keyword.lower() if keyword else ""

        # 过滤数据
        filtered_items = []
        for data in self._items_list:
            if len(data) > 2:
                name = str(data[1]).lower() if data[1] else ""
                zh_name = str(data[2]) if data[2] else ""

                if (not keyword_lower or
                    keyword_lower in name or
                    keyword_lower in zh_name):
                    filtered_items.append(data)

        # 分批添加
        self._pending_items = filtered_items
        self._addBatchItems()

    def _addBatchItems(self):
        """分批添加 items"""
        batch_size = 50

        if not hasattr(self, '_pending_items') or not self._pending_items:
            return

        batch = self._pending_items[:batch_size]
        self._pending_items = self._pending_items[batch_size:]

        for data in batch:
            self.addItem(data)

        if self._pending_items:
            QtCore.QTimer.singleShot(10, self._addBatchItems)
        else:
            self.sortItems(0, QtCore.Qt.DescendingOrder)

    def selectedItems(self):
        """获取选中的 items（每行返回第 0 列的 item，保证带完整 itemData）"""
        items = super(TableWidget, self).selectedItems()
        seen_rows = set()
        unique_items = []
        for item in items:
            row = item.row()
            if row not in seen_rows:
                seen_rows.add(row)
                col0 = self.item(row, 0)
                unique_items.append(col0 if col0 is not None else item)
        return unique_items

    def currentAsset(self):
        """获取当前资产名"""
        items = self.selectedItems()
        if items:
            row = items[0].row()
            name_item = self.item(row, 1)
            if name_item:
                return name_item.text()
        return ""

    def _onScroll(self):
        """滚动时触发"""
        self._load_timer.start(100)

    def _loadVisibleItems(self):
        """加载可见区域的 items（用于延迟加载缩略图等）"""
        pass  # 表格模式不需要特殊处理

    def dragLeaveEvent(self, event):
        self.dragLeaveSignal.emit()
        super(TableWidget, self).dragLeaveEvent(event)


class ItemsWidget(QtWidgets.QWidget):
    """
    高性能 ItemsWidget
    整合 ListView 和 TableWidget
    """

    # 视图模式
    IconMode = "icon"
    TableMode = "table"

    # 信号
    itemSelectionChanged = QtCore.Signal()
    dragLeaveSignal = QtCore.Signal()

    def __init__(self, parent=None, db="FFA", tab="Asset", user="", password=""):
        super(ItemsWidget, self).__init__(parent)

        self._db = db
        self._tab = tab
        self._user = user
        self._password = password

        self._is_list = False
        self._item_size = 120
        self._items_list = []
        self._view_mode = self.IconMode
        self._external_items_widget = None  # 外部控制器引用(AssetToolsUI)

        # 创建子组件
        self._list_view = ListView(self)
        self._list_view.setObjectName("listView")
        self._list_view.itemSelectionChanged.connect(self._onSelectionChanged)
        self._list_view.dragLeaveSignal.connect(self.dragLeaveSignal.emit)

        self._table_widget = TableWidget(self)
        self._table_widget.setObjectName("tableWidget")
        self._table_widget.itemSelectionChanged.connect(self._onSelectionChanged)
        self._table_widget.dragLeaveSignal.connect(self.dragLeaveSignal.emit)

        # 右键菜单：两个子视图都启用自定义右键，并把信号上抛到 ItemsWidget
        # （QListView / QTableWidget 都从 QWidget 继承了 customContextMenuRequested 信号）
        self._list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._list_view.customContextMenuRequested.connect(self.customContextMenuRequested)
        self._table_widget.customContextMenuRequested.connect(self.customContextMenuRequested)

        # 布局
        layout = QtWidgets.QStackedLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list_view)
        layout.addWidget(self._table_widget)
        self.setLayout(layout)

        # 默认显示图标模式
        self.setViewMode(self.IconMode)

    def setViewMode(self, mode):
        """设置视图模式"""
        self._view_mode = mode
        layout = self.layout()

        if mode == self.IconMode:
            layout.setCurrentWidget(self._list_view)
            self._is_list = False
        else:
            layout.setCurrentWidget(self._table_widget)
            self._is_list = True

    def viewMode(self):
        """获取视图模式"""
        return self._view_mode

    def isList(self):
        """是否为列表模式"""
        return self._is_list

    def setIsList(self, value):
        """设置是否为列表模式"""
        self._is_list = value
        self.setViewMode(self.TableMode if value else self.IconMode)

    def currentWidget(self):
        """获取当前显示的 widget"""
        return self.layout().currentWidget()

    def setItemSize(self, size):
        """设置 item 尺寸"""
        self._item_size = size
        self._list_view.setItemSize(size)

    def itemSize(self):
        """获取 item 尺寸"""
        return self._item_size

    def resizeItem(self):
        """调整 item 尺寸"""
        self._list_view.setItemSize(self._item_size)

    def setItemsList(self, items_list):
        """设置数据列表"""
        self._items_list = items_list
        self._list_view.setItemsList(items_list)
        self._table_widget.setItemsList(items_list)

    def itemsList(self):
        """获取数据列表"""
        return self._items_list

    def addItem(self, data):
        """添加单个 item"""
        if self._is_list:
            self._table_widget.addItem(data)
        else:
            self._list_view.addItem(data)

    def addItems(self, keyword="", add=False):
        """批量添加 items"""
        if self._is_list:
            self._table_widget.addItems(keyword, add)
        else:
            self._list_view.addItems(keyword, add)

    def clear(self):
        """清空"""
        self._list_view.clear()
        self._table_widget.clearContents()
        self._table_widget.setRowCount(0)

    def itemCount(self):
        """获取 item 数量"""
        if self._is_list:
            return self._table_widget.rowCount()
        else:
            return self._list_view.itemCount()

    def itemAt(self, point):
        """获取指定位置的 item"""
        if self._is_list:
            return self._table_widget.itemAt(point)
        else:
            return self._list_view.itemAt(point)

    def selectedItems(self):
        """获取选中的 items"""
        if self._is_list:
            return self._table_widget.selectedItems()
        else:
            return self._list_view.selectedItems()

    def currentItem(self):
        """获取当前 item"""
        if self._is_list:
            return self._table_widget.currentItem()
        else:
            return self._list_view.currentItem()

    def currentAsset(self):
        """获取当前资产名"""
        if self._is_list:
            return self._table_widget.currentAsset()
        else:
            items = self._list_view.selectedItems()
            if items:
                return items[0].name()
        return ""

    def _onSelectionChanged(self):
        """选择改变"""
        self.itemSelectionChanged.emit()

    def setItemsWidget(self, widget):
        """保存外部控制器(AssetToolsUI)引用，并转发给支持该接口的子视图（兼容旧接口）。"""
        self._external_items_widget = widget
        for view in (self._list_view, self._table_widget):
            if hasattr(view, "setItemsWidget"):
                view.setItemsWidget(widget)

    def itemsWidget(self):
        """返回外部控制器引用。"""
        return self._external_items_widget

    def setIconMode(self, item_size, keywords=None):
        """设置为图标模式"""
        self._item_size = item_size
        self.setViewMode(self.IconMode)
        self._list_view.setItemSize(item_size)
        keyword = keywords[0] if keywords and len(keywords) > 0 else ""
        self._list_view.addItems(keyword)

    def setListMode(self, keywords=None):
        """设置为列表模式"""
        self.setViewMode(self.TableMode)
        keyword = keywords[0] if keywords and len(keywords) > 0 else ""
        self._table_widget.addItems(keyword)

    def verticalScrollBar(self):
        """获取垂直滚动条"""
        if self._is_list:
            return self._table_widget.verticalScrollBar()
        else:
            return self._list_view.verticalScrollBar()

    def clearSelection(self):
        """清除选择"""
        self._list_view.clearSelection()
        self._table_widget.clearSelection()

    def setFocus(self):
        """设置焦点"""
        self.currentWidget().setFocus()
