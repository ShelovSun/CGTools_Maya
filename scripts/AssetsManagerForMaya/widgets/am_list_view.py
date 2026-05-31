#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高性能 ListView 组件
参考 StudioLibrary 的 ListView 实现
支持虚拟滚动、延迟加载、批量渲染
"""

import logging
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from widgets.am_list_item_optimized import ListItemOptimized
from widgets.am_thumbnail_loader import ThumbnailLoader

logger = logging.getLogger(__name__)


class ItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    自定义 Item 委托
    负责绘制每个 item
    """

    def __init__(self, parent=None):
        super(ItemDelegate, self).__init__(parent)
        self._list_view = None

    def setListView(self, list_view):
        """设置关联的 ListView"""
        self._list_view = list_view

    def paint(self, painter, option, index):
        """绘制 item"""
        item = self._list_view.itemFromIndex(index) if self._list_view else None

        if isinstance(item, ListItemOptimized):
            # 检查是否需要加载缩略图。
            # 注意：不再在此处 setLoaded(True)——那会在真实图到达前就谎称“已加载”，
            # 一旦该请求随后被取消，条目会卡在“已加载但无图”状态、永远显示默认图。
            # 改为只在“未加载且未在加载中”时触发；真正的 loaded 由回调置位。
            if not item.isThumbnailLoaded() and not item.isThumbnailLoading():
                item.loadThumbnail()
            item.paint(painter, option, index)
        else:
            super(ItemDelegate, self).paint(painter, option, index)

    def sizeHint(self, option, index):
        """返回 item 尺寸"""
        item = self._list_view.itemFromIndex(index) if self._list_view else None
        if isinstance(item, ListItemOptimized):
            return item.sizeHint()
        return super(ItemDelegate, self).sizeHint(option, index)


class ListView(QtWidgets.QListView):
    """
    高性能 ListView
    特性:
    - 虚拟滚动
    - 延迟加载可见 items
    - 批量缩略图加载
    - 鼠标悬停检测
    """

    # 信号
    itemClicked = QtCore.Signal(object)
    itemDoubleClicked = QtCore.Signal(object)
    itemSelectionChanged = QtCore.Signal()
    dragLeaveSignal = QtCore.Signal()

    def __init__(self, parent=None):
        super(ListView, self).__init__(parent)

        self._item_size = 120
        self._spacing = 8
        self._items_list = []
        self._current_item = None
        self._loading_batch_size = 20  # 每批加载数量
        self._loading_delay = 50  # 加载延迟(ms)

        # 设置 ListView 属性
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setSpacing(self._spacing)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setMouseTracking(True)
        self.setUniformItemSizes(True)  # 统一 item 尺寸以优化性能
        self.setBatchSize(50)  # 批量绘制

        # 设置自定义委托
        self._delegate = ItemDelegate(self)
        self._delegate.setListView(self)
        self.setItemDelegate(self._delegate)

        # 模型
        self._model = QtGui.QStandardItemModel(self)
        self.setModel(self._model)

        # 定时器用于延迟加载
        self._load_timer = QtCore.QTimer(self)
        self._load_timer.setSingleShot(True)
        self._load_timer.timeout.connect(self._loadVisibleItems)

        # 滚动条值变化时更新可见 items
        self.verticalScrollBar().valueChanged.connect(self._onScroll)

        # 选择模型信号
        self.selectionModel().selectionChanged.connect(self._onSelectionChanged)

        # 缩略图加载器
        self._thumbnail_loader = ThumbnailLoader.instance()

    def setItemSize(self, size):
        """设置 item 尺寸"""
        self._item_size = size
        self.setIconSize(QtCore.QSize(size, size))
        grid_size = size + self._spacing + 40  # 40 for text
        self.setGridSize(QtCore.QSize(grid_size, grid_size))

    def itemSize(self):
        """获取 item 尺寸"""
        return self._item_size

    def setItemsList(self, items_list):
        """设置数据列表"""
        self._items_list = items_list

    def addItem(self, data):
        """添加单个 item"""
        item = ListItemOptimized(tab=self._tab if hasattr(self, '_tab') else "Asset")
        item.setItemData(data)
        item.setThumbnailSize(self._item_size)
        item.setItemsWidget(self)
        item.setText(str(data[1]) if len(data) > 1 else "")

        # 创建标准 item 用于模型
        standard_item = QtGui.QStandardItem()
        standard_item.setData(item, QtCore.Qt.UserRole)

        self._model.appendRow(standard_item)

        # 延迟加载缩略图
        self._scheduleLoad()

    def addItems(self, keyword="", add=False):
        """批量添加 items"""
        if not add:
            self.clear()

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

        # 分批添加以避免阻塞 UI
        self._pending_items = filtered_items
        self._addBatchItems()

    def _addBatchItems(self):
        """分批添加 items"""
        batch_size = 50  # 每批添加数量

        if not hasattr(self, '_pending_items') or not self._pending_items:
            return

        batch = self._pending_items[:batch_size]
        self._pending_items = self._pending_items[batch_size:]

        for data in batch:
            item = ListItemOptimized(tab=self._tab if hasattr(self, '_tab') else "Asset")
            item.setItemData(data)
            item.setThumbnailSize(self._item_size)
            item.setItemsWidget(self)
            item.setText(str(data[1]) if len(data) > 1 else "")

            standard_item = QtGui.QStandardItem()
            standard_item.setData(item, QtCore.Qt.UserRole)
            self._model.appendRow(standard_item)

        # 如果还有更多，使用定时器继续添加
        if self._pending_items:
            QtCore.QTimer.singleShot(10, self._addBatchItems)
        else:
            # 全部添加完成，加载可见 items
            self._scheduleLoad()

    def clear(self):
        """清空列表"""
        self._model.clear()
        self._thumbnail_loader.clearPendingLoads()

    def itemCount(self):
        """获取 item 数量"""
        return self._model.rowCount()

    def itemFromIndex(self, index):
        """从索引获取 item"""
        if not index.isValid():
            return None
        standard_item = self._model.itemFromIndex(index)
        if standard_item:
            return standard_item.data(QtCore.Qt.UserRole)
        return None

    def itemAt(self, pos):
        """从位置获取 item"""
        index = self.indexAt(pos)
        return self.itemFromIndex(index)

    def selectedItems(self):
        """获取选中的 items"""
        items = []
        for index in self.selectedIndexes():
            item = self.itemFromIndex(index)
            if item:
                items.append(item)
        return items

    def currentItem(self):
        """获取当前 item"""
        index = self.currentIndex()
        return self.itemFromIndex(index)

    def _onScroll(self):
        """滚动时触发"""
        self._scheduleLoad()

    def _scheduleLoad(self):
        """安排加载可见 items"""
        self._load_timer.start(self._loading_delay)

    def _visibleRowRange(self):
        """计算当前 viewport 中可见 item 的行号区间 [start, end]（含端点）。

        IconMode 下 indexAt 取角点时，角点常落在 item 之间的 spacing 间隙而返回
        无效索引。**关键约束**：该区间会被 cancelPathsExcept 当作“保留区”，区间外
        的加载请求会被取消——所以宁可多算（多保留几行），绝不能少算，否则真正可见
        的条目会被误取消、永远停在默认图（之前滚到底部只刷出第一行就是这个原因）。

        做法：沿顶边、底边各取多个采样点 indexAt，避开 spacing 间隙；采样全落空时
        用网格尺寸估算一屏的行数做**有界**回退（绝不直接回退到列表末尾，以免又把整
        条尾巴全部入队）。
        """
        row_count = self._model.rowCount()
        if row_count == 0:
            return 0, -1

        vp = self.viewport().rect()
        xs = [vp.left() + 2, vp.center().x(), vp.right() - 2]
        offsets = (2, self._spacing + 4)  # 紧贴边缘的点易落在间隙，再向内采一点

        top_rows = []
        bottom_rows = []
        for x in xs:
            for dy in offsets:
                ti = self.indexAt(QtCore.QPoint(x, vp.top() + dy))
                if ti.isValid():
                    top_rows.append(ti.row())
                bi = self.indexAt(QtCore.QPoint(x, vp.bottom() - dy))
                if bi.isValid():
                    bottom_rows.append(bi.row())

        start = min(top_rows) if top_rows else 0

        if bottom_rows:
            end = max(bottom_rows)
        else:
            # 底边全落空：可能滚到最底或列表没占满一屏。用网格估算一屏行数做有界回退，
            # 而不是跳到 rowCount-1（那会把整条尾巴重新入队，退回老问题）。
            grid = self.gridSize()
            gw = grid.width() if grid.width() > 0 else (self._item_size + self._spacing)
            gh = grid.height() if grid.height() > 0 else (self._item_size + self._spacing + 40)
            cols = max(1, vp.width() // gw)
            rows_per_screen = vp.height() // gh + 2
            end = min(row_count - 1, start + cols * rows_per_screen)

        if end < start:
            start, end = end, start
        return start, end

    def _loadVisibleItems(self):
        """加载可见区域的 items，并取消可见区之外的排队请求。"""
        row_count = self._model.rowCount()
        if row_count == 0:
            return

        start_index, end_index = self._visibleRowRange()

        # 扩展预加载范围（上下各预读半批）
        preload_range = self._loading_batch_size // 2
        start_index = max(0, start_index - preload_range)
        end_index = min(row_count - 1, end_index + preload_range)

        # 收集可见区（含预读）的条目与缩略图路径
        visible_items = []
        keep_paths = set()
        for row in range(start_index, end_index + 1):
            item = self.itemFromIndex(self._model.index(row, 0))
            if isinstance(item, ListItemOptimized):
                visible_items.append(item)
                path = item.thumbnailPath()
                if path:
                    keep_paths.add(path)

        # 取消可见区之外仍在排队的加载，让线程池立刻处理可见区
        # （被取消的 worker 会在 run() 开头即返回，几微秒内腾出线程）。
        self._thumbnail_loader.cancelPathsExcept(keep_paths)

        # 加载可见区条目；对此前被取消、卡在“加载中”状态的条目先复位再请求。
        for item in visible_items:
            if item.isThumbnailLoaded():
                continue
            if item.isThumbnailLoading() and not self._thumbnail_loader.isPending(item.thumbnailPath()):
                item.resetThumbnail()  # 之前的请求已被取消，允许重新加载
            item.loadThumbnail()

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        super(ListView, self).mouseMoveEvent(event)

        # 处理 item 的鼠标进入/离开事件
        item = self.itemAt(event.pos())

        if item != self._current_item:
            if self._current_item:
                self._current_item.mouseLeaveEvent(event)
            if item:
                item.mouseEnterEvent(event)
            self._current_item = item

        if item:
            item.mouseMoveEvent(event)

    def leaveEvent(self, event):
        """鼠标离开事件"""
        if self._current_item:
            self._current_item.mouseLeaveEvent(event)
            self._current_item = None
        super(ListView, self).leaveEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        item = self.itemAt(event.pos())
        if item:
            item.mousePressEvent(event)
        super(ListView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        item = self.itemAt(event.pos())
        if item:
            item.mouseReleaseEvent(event)
        super(ListView, self).mouseReleaseEvent(event)

    def _onSelectionChanged(self, selected, deselected):
        """选择改变事件"""
        self.itemSelectionChanged.emit()

    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.dragLeaveSignal.emit()
        super(ListView, self).dragLeaveEvent(event)

    def resizeEvent(self, event):
        """尺寸改变事件"""
        super(ListView, self).resizeEvent(event)
        self._scheduleLoad()

    def wheelEvent(self, event):
        """滚轮事件"""
        # 支持 Ctrl+滚轮缩放
        if event.modifiers() & QtCore.Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._item_size = min(256, self._item_size + 10)
            else:
                self._item_size = max(50, self._item_size - 10)
            self.setItemSize(self._item_size)
            self.update()
        else:
            super(ListView, self).wheelEvent(event)

    def getVisibleItems(self):
        """获取当前可见的所有 items"""
        visible_items = []
        viewport_rect = self.viewport().rect()

        for row in range(self._model.rowCount()):
            index = self._model.index(row, 0)
            rect = self.visualRect(index)
            if viewport_rect.intersects(rect):
                item = self.itemFromIndex(index)
                if item:
                    visible_items.append(item)

        return visible_items
