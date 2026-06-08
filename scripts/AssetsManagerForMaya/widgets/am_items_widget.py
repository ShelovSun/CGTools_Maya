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
from widgets import user_menu, note_menu

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

    def sizeHint(self, option, index):
        # 自定义 paint 时一并提供 sizeHint，否则行高/绘制偶尔会乱（沿用旧 MainDelegate 的做法）。
        item = self._table_widget.itemFromIndex(index) if self._table_widget else None
        if item is not None:
            hint = item.sizeHint()
            if hint.isValid():
                return hint
        return super(TableItemDelegate, self).sizeHint(option, index)


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

        # ---- 恢复表格交互（迁移到优化路径时遗漏了委托与下拉菜单） ----
        # 1) 安装委托，让 am_tableItem 的自定义 paint() 生效（绘制 isCombo 下拉角标）。
        #    QTableWidgetItem.paint() 不会被 Qt 自动调用，必须由委托转调。
        self._delegate = TableItemDelegate(self)
        self._delegate.setTableWidget(self)
        self.setItemDelegate(self._delegate)

        # 2) 单击单元格右侧 -> 制作人(3/5)/状态(4/6) 菜单；双击中文名(2) -> 编辑框。
        self.clicked.connect(self._on_cell_clicked)
        self.cellDoubleClicked.connect(self.show_edit_menu)
        self.setDragEnabled(True)

        # 3) 制作人选择面板 / 中文名编辑面板（回调 self.artist_changed / self.zh_name_changed）
        self.user_menu = user_menu.UserMenuWidgetNoCheck(self)
        self.user_menu.setItemsWidget(self)
        self.is_user_menu = False

        self.note_menu = note_menu.NoteMenuWidget(self)
        self.note_menu.setItemsWidget(self)
        self.is_note_menu = False

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

        # 列 -> 数据字段映射：第 7 列“备注”取 data[8]；data[7] 是 icon 路径，表格不显示。
        values = list(data[:7])
        values.append(data[8] if len(data) > 8 and data[8] is not None else "")

        for col, value in enumerate(values):
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

    # -----------------------------------------------------------------------
    # 下拉菜单 / 单元格编辑（从旧版 am_tableWidget.MainTableWidget 移植回来）
    # -----------------------------------------------------------------------

    def mousePressEvent(self, event):
        super(TableWidget, self).mousePressEvent(event)
        self.closeMenus()

    def closeMenus(self):
        """关闭弹出的制作人/中文名面板（点击表格或主窗空白处时调用）。"""
        if getattr(self, 'is_user_menu', False):
            self.user_menu.close()
            self.is_user_menu = False
        if getattr(self, 'is_note_menu', False):
            self.note_menu.close()
            self.is_note_menu = False

    def _on_cell_clicked(self, *args):
        """单击单元格右侧 1/3 区域时，按列弹出制作人/状态菜单。"""
        item = self.currentItem()
        if not item:
            return
        table_pos = self.viewport().mapToGlobal(self.pos())
        rect = self.visualItemRect(item)
        rectX = rect.left() + table_pos.x()
        rectX_end = rectX + rect.width() / 3 * 2
        if QtGui.QCursor.pos().x() > rectX_end:
            col = item.column()
            if col in (3, 5):      # 模型制作 / 绑定制作
                self.show_user_menu()
            elif col in (4, 6):    # 模型状态 / 绑定状态
                self.show_status_menu()

    def show_edit_menu(self, *args):
        """双击中文名(第 2 列)弹出编辑框。"""
        item = self.currentItem()
        if not item:
            return
        table_pos = self.viewport().mapToGlobal(self.pos())
        rect = self.visualItemRect(item)
        if item.column() == 2:
            self.note_menu.setUp(item.text())
            self.note_menu.setGeometry(
                rect.left() + table_pos.x(), rect.top() + table_pos.y(),
                rect.width(), rect.height())
            self.is_note_menu = True

    def show_user_menu(self):
        """弹出制作人选择面板。"""
        item = self.currentItem()
        if not item:
            return
        table_pos = self.viewport().mapToGlobal(self.pos())
        rect = self.visualItemRect(item)
        self.user_menu.setUp(exist_name='')
        self.user_menu.setGeometry(
            rect.left() + table_pos.x(), rect.bottom() + table_pos.y(), 200, 300)
        self.is_user_menu = True

    def show_status_menu(self):
        """弹出状态选择菜单。"""
        item = self.currentItem()
        if not item:
            return
        table_pos = self.viewport().mapToGlobal(self.pos())
        rect = self.visualItemRect(item)
        rectX = rect.left() + table_pos.x()
        rectY = rect.bottom() + table_pos.y()
        menu = QtWidgets.QMenu()
        for label in (u'未开始', u'制作中', u'已完成'):
            action = QtWidgets.QAction(label, self)
            action.triggered.connect(lambda checked=False, t=label: self.status_changed(t))
            menu.addAction(action)
        menu.exec_(QtCore.QPoint(rectX, rectY))

    def _current_asset_name(self, row):
        """取某行的资产名(第 1 列)。"""
        name_item = self.item(row, 1)
        return name_item.text() if name_item is not None else None

    def artist_changed(self, text):
        """制作人改变 -> 写库 -> 更新单元格文字。"""
        row, col = self.currentRow(), self.currentColumn()
        asset_name = self._current_asset_name(row)
        if col == 3:        # 模型制作
            self.update_asset(asset_name, "asset.mod_artist", text)
            self.item(row, 3).setName(text)
        elif col == 5:      # 绑定制作
            self.update_asset(asset_name, "asset.rig_artist", text)
            self.item(row, 5).setName(text)

    def status_changed(self, text):
        """状态改变 -> 写库 -> 更新单元格文字。"""
        row, col = self.currentRow(), self.currentColumn()
        asset_name = self._current_asset_name(row)
        if col == 4:        # 模型状态
            self.update_asset(asset_name, "asset.mod_status", text)
            self.item(row, 4).setName(text)
        elif col == 6:      # 绑定状态
            self.update_asset(asset_name, "asset.rig_status", text)
            self.item(row, 6).setName(text)

    def zh_name_changed(self, text):
        """中文名改变 -> 写库 -> 更新单元格文字。"""
        row, col = self.currentRow(), self.currentColumn()
        asset_name = self._current_asset_name(row)
        if col == 2:
            self.update_asset(asset_name, "asset.zh_name", text)
            self.note_menu.close()
            self.is_note_menu = False
            self.item(row, 2).setName(text)

    def update_asset(self, asset_name, key, value):
        """写回数据库。db/user/password/host 取自外部控制器(AssetToolsUI)，随当前项目实时变化。"""
        ctrl = self._items_widget
        if ctrl is None or not asset_name:
            return
        try:
            db = ctrl.currentProject()
            user, password, host = ctrl.user, ctrl.password, ctrl.host
        except AttributeError:
            return

        import psycopg2
        update_script = '''
            UPDATE public.asset SET "%s" = '%s'
            WHERE "asset.name" = '%s';''' % (key, value, asset_name)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=user, password=password, host=host, port="5432")
            cur = conn.cursor()
            cur.execute(update_script)
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()


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

    def closeMenus(self):
        """转发给表格视图，关闭其弹出的制作人/中文名面板。"""
        if hasattr(self._table_widget, "closeMenus"):
            self._table_widget.closeMenus()
