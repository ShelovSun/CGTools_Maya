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
from widgets.am_sort import asset_sort_key
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
    sortRequested = QtCore.Signal(int)
    rowDataChanged = QtCore.Signal(object, object)

    table_header = ["创建日期", "资产名", "中文名", "模型制作", "模型状态", "绑定制作", "绑定状态", "备注"]

    def __init__(self, parent=None):
        super(TableWidget, self).__init__(parent)

        self._items_list = []
        self._items_widget = None
        self._pending_items = []
        self._sort_column = 0
        self._sort_descending = True
        self._zh_name_item = None

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
        self.setSortingEnabled(False)  # 一整行填完后统一排序，避免逐单元格插入时错行。
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setSortIndicator(0, QtCore.Qt.DescendingOrder)
        self.horizontalHeader().sectionClicked.connect(self.sortRequested.emit)

        self.verticalHeader().setVisible(True)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # 只使用接入数据库的自定义编辑框，避免 Qt 默认编辑器仅改变显示文字。
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

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

        self.note_menu = note_menu.NoteMenuWidget(self, commit_on_focus_out=True)
        self.note_menu.setItemsWidget(self)
        self.is_note_menu = False

    def setItemsWidget(self, widget):
        self._items_widget = widget

    def itemsWidget(self):
        return self._items_widget

    def setItemsList(self, items_list):
        self._items_list = items_list

    def setSort(self, column, descending):
        self._sort_column = column
        self._sort_descending = descending
        order = QtCore.Qt.DescendingOrder if descending else QtCore.Qt.AscendingOrder
        self.horizontalHeader().setSortIndicator(column, order)
        self.sortItems(column, order)

    def clearItems(self):
        """同时取消尚未添加的旧批次，避免刷新后混入上次查询的条目。"""
        self.note_menu.cancel()
        self.is_note_menu = False
        self._zh_name_item = None
        self._pending_items = []
        self.clearContents()
        self.setRowCount(0)

    def addItem(self, data):
        """添加单个 item"""
        row = self.rowCount()
        self.insertRow(row)

        # 列 -> 数据字段映射：第 7 列“备注”取 data[8]；data[7] 是 icon 路径，表格不显示。
        values = list(data[:7])
        values.append(data[8] if len(data) > 8 and data[8] is not None else "")

        for col, value in enumerate(values):
            if col < len(self.table_header):
                value = "" if value is None else str(value)
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
            self.clearItems()

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

        self.setSort(self._sort_column, self._sort_descending)
        if self._pending_items:
            QtCore.QTimer.singleShot(10, self._addBatchItems)

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
            if self.note_menu.note_edit_finished() is False:
                return
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
            self._zh_name_item = item
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
        labels = [u'未开始', u'制作中', u'已完成']
        if item.column() == 4:  # UE 仅用于模型状态。
            labels.append(u'UE')
        for label in labels:
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
        col = self.currentColumn()
        if col == 3:        # 模型制作
            self._commit_item_change(self.currentItem(), "asset.mod_artist", text)
        elif col == 5:      # 绑定制作
            self._commit_item_change(self.currentItem(), "asset.rig_artist", text)

    def status_changed(self, text):
        """状态改变 -> 写库 -> 更新单元格文字。"""
        col = self.currentColumn()
        if col == 4:        # 模型状态
            self._commit_item_change(self.currentItem(), "asset.mod_status", text)
        elif col == 6:      # 绑定状态
            self._commit_item_change(self.currentItem(), "asset.rig_status", text)

    def zh_name_changed(self, text):
        """中文名改变 -> 写库 -> 更新单元格文字。"""
        item = self._zh_name_item
        if item is None:
            item = self.currentItem()
        if item is None or item.column() != 2:
            return False
        if not self._commit_item_change(item, "asset.zh_name", text):
            return False
        self._zh_name_item = None
        self.note_menu.close()
        self.is_note_menu = False
        return True

    def _record_table(self, item):
        """优先按当前行的路径区分 asset/scene，支持全部目录混排及同名条目。"""
        data = item.itemData()
        icon = str(data[7]).replace("\\", "/").lower() if len(data) > 7 else ""
        if "/scenes/" in icon:
            return "scene"
        if "/assets/" in icon:
            return "asset"
        ctrl = self._items_widget
        if hasattr(ctrl, "_row_table_of_selected"):
            tab = ctrl._row_table_of_selected(item)
        else:
            tab = getattr(ctrl, "tab", "Assets")
        if tab in ("Scene", "Scenes"):
            return "scene"
        if tab in ("Asset", "Assets"):
            return "asset"
        raise ValueError(u"无法确定条目属于资产还是场景，请刷新后重试。")

    def _commit_item_change(self, item, key, text):
        """写库成功后再更新整行数据及视图缓存。"""
        if item.text() == text:
            return True
        asset_name = self._current_asset_name(item.row())
        if not self.update_asset(asset_name, key, text, item=item):
            return False
        old_data = item.itemData()
        new_data = list(old_data)
        columns = (item.column(),)
        if self._record_table(item) == "scene":
            # scene 查询将 artist/status 同时投影到模型列和绑定列。
            if item.column() in (3, 5):
                columns = (3, 5)
            elif item.column() in (4, 6):
                columns = (4, 6)
        for column in columns:
            new_data[column] = text
            self.item(item.row(), column).setName(text)
        new_data = tuple(new_data)
        for column in range(self.columnCount()):
            cell = self.item(item.row(), column)
            if cell is not None:
                cell.setItemData(new_data)
        self.rowDataChanged.emit(old_data, new_data)
        self.viewport().update()
        return True

    def update_asset(self, asset_name, key, value, item=None):
        """写回当前行所属表；只在唯一记录确实提交后返回成功。"""
        ctrl = self._items_widget
        import psycopg2
        conn = None
        cur = None
        try:
            if ctrl is None or not asset_name:
                raise ValueError(u"缺少项目连接信息或条目名称，请刷新后重试。")
            table = self._record_table(item if item is not None else self.currentItem())
            fields = {
                "asset": {
                    "asset.zh_name": "asset.zh_name",
                    "asset.mod_artist": "asset.mod_artist",
                    "asset.rig_artist": "asset.rig_artist",
                    "asset.mod_status": "asset.mod_status",
                    "asset.rig_status": "asset.rig_status",
                },
                "scene": {
                    "asset.zh_name": "scene.zh_name",
                    "asset.mod_artist": "scene.artist",
                    "asset.rig_artist": "scene.artist",
                    "asset.mod_status": "scene.status",
                    "asset.rig_status": "scene.status",
                },
            }
            # 标识符只取固定映射；用户输入的中文名/条目名通过参数传递。
            update_script = 'UPDATE public.{0} SET "{1}" = %s WHERE "{0}.name" = %s'.format(
                table, fields[table][key]
            )
            conn = psycopg2.connect(
                database=ctrl.currentProject(), user=ctrl.user, password=ctrl.password,
                host=ctrl.host, port="5432", connect_timeout=5
            )
            cur = conn.cursor()
            cur.execute(update_script, (value, asset_name))
            if cur.rowcount != 1:
                raise ValueError(u"保存应更新 1 条记录，实际匹配 %s 条，请刷新后重试。" % cur.rowcount)
            conn.commit()
            return True
        except Exception as e:
            if conn is not None:
                try:
                    conn.rollback()
                except Exception:
                    pass
            QtWidgets.QMessageBox.warning(self, u"保存失败", str(e))
            return False
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
    sortRequested = QtCore.Signal(int)
    rowDataChanged = QtCore.Signal(object, object)

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
        self._sort_column = 0
        self._sort_descending = True

        # 创建子组件
        self._list_view = ListView(self)
        self._list_view.setObjectName("listView")
        self._list_view.itemSelectionChanged.connect(self._onSelectionChanged)
        self._list_view.dragLeaveSignal.connect(self.dragLeaveSignal.emit)

        self._table_widget = TableWidget(self)
        self._table_widget.setObjectName("tableWidget")
        self._table_widget.itemSelectionChanged.connect(self._onSelectionChanged)
        self._table_widget.dragLeaveSignal.connect(self.dragLeaveSignal.emit)
        self._table_widget.sortRequested.connect(self.sortRequested.emit)
        self._table_widget.rowDataChanged.connect(self._onRowDataChanged)

        # 子视图的右键位置是 viewport 坐标，上抛前转换到 ItemsWidget 坐标。
        self._list_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._table_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self._list_view.customContextMenuRequested.connect(
            lambda point: self._forwardContextMenu(self._list_view, point)
        )
        self._table_widget.customContextMenuRequested.connect(
            lambda point: self._forwardContextMenu(self._table_widget, point)
        )

        # 布局
        layout = QtWidgets.QStackedLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list_view)
        layout.addWidget(self._table_widget)
        self.setLayout(layout)

        # 默认显示图标模式
        self.setViewMode(self.IconMode)

    def _forwardContextMenu(self, view, point):
        """将子视图的 viewport 坐标转换为本控件坐标后发出右键信号。"""
        self.customContextMenuRequested.emit(view.viewport().mapTo(self, point))

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
        """缓存当前顺序，切换视图或重新过滤时继续使用相同的排序。"""
        self._items_list = sorted(
            items_list or [],
            key=lambda data: asset_sort_key(data, self._sort_column),
            reverse=self._sort_descending,
        )
        self._list_view.setItemsList(self._items_list)
        self._table_widget.setItemsList(self._items_list)

    def _onRowDataChanged(self, old_data, new_data):
        """编辑结果同步到两种视图及待添加批次，避免重建视图时恢复旧值。"""
        self.setItemsList([new_data if row == old_data else row for row in self._items_list])
        for view in (self._list_view, self._table_widget):
            view._pending_items = [
                new_data if row == old_data else row for row in view._pending_items
            ]
        model = self._list_view.model()
        for row in range(model.rowCount()):
            standard_item = model.item(row)
            item = standard_item.data(QtCore.Qt.UserRole)
            if item.itemData() == old_data:
                item.setItemData(new_data)
                standard_item.setData(
                    asset_sort_key(new_data, self._sort_column), self._list_view._sort_role
                )
        self._list_view.sortItems(self._sort_column, self._sort_descending)
        self._table_widget.setSort(self._sort_column, self._sort_descending)
        self._list_view.viewport().update()
        self.rowDataChanged.emit(old_data, new_data)

    def sortItems(self, column, descending):
        """菜单和表头共用的排序入口，不重建条目或重新查询数据库。"""
        changed = (column, descending) != (self._sort_column, self._sort_descending)
        self._sort_column = column
        self._sort_descending = descending
        if changed:
            self.setItemsList(self._items_list)
        self._list_view.sortItems(column, descending)
        self._table_widget.setSort(column, descending)

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
        self._table_widget.clearItems()

    def itemCount(self):
        """获取 item 数量"""
        if self._is_list:
            return self._table_widget.rowCount()
        else:
            return self._list_view.itemCount()

    def itemAt(self, point):
        """获取本控件坐标下的 item，与右键信号使用同一坐标系。"""
        view = self.currentWidget()
        if view is None:
            return None
        return view.itemAt(view.viewport().mapFrom(self, point))

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
