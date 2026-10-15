#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用 Maya 2022 mayapy 运行；只用内存数据，不查询数据库或修改 Maya 场景。"""

import sys
import time
import unittest
from unittest import mock
from pathlib import Path

sys.dont_write_bytecode = True
TOOL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = TOOL_ROOT.parent
for path in (
    TOOL_ROOT,
    SCRIPTS_ROOT,
    SCRIPTS_ROOT / "tools_ani" / "StudioLibrary",
    SCRIPTS_ROOT / "Python" / "Python37" / "Lib" / "site-packages",
):
    sys.path.append(str(path))

from PySide2 import QtCore, QtWidgets

APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

from sources.assetTools import AssetToolsUI
from widgets.am_main_optimized import MainStackedWidget
from widgets.am_sort import asset_sort_key


def make_rows(count=123):
    """超过两批的数据；日期混合整数/字符串/空值，备注顺序刻意不同于图标路径。"""
    dates = (2, "10", None, "invalid", 30)
    return [
        (
            dates[index % len(dates)],
            "Asset_{:03d}".format(index),
            "中文{:03d}".format(count - index),
            ("zArtist", "Alpha", None)[index % 3],
            ("已完成", "未开始", "制作中")[index % 3],
            (None, "Beta", "aArtist")[index % 3],
            ("制作中", "已完成", None)[index % 3],
            "C:/__cgtools_sort_test__/Icon/{:03d}.png".format(index),
            "Note_{:03d}".format(count - index),
        )
        for index in range(count)
    ]


class AssetSortTests(unittest.TestCase):
    def setUp(self):
        self.widget = MainStackedWidget()
        self.items = self.widget.itemsWidget()
        self.rows = make_rows()

    def tearDown(self):
        self.widget.clear()
        self.widget.deleteLater()
        APP.processEvents()

    def drain_batches(self):
        deadline = time.monotonic() + 3
        while self.items._list_view._pending_items or self.items._table_widget._pending_items:
            self.assertLess(time.monotonic(), deadline, "分批添加未结束")
            APP.processEvents()
            time.sleep(0.005)

    def visible_rows(self):
        if self.widget.isList():
            table = self.items._table_widget
            return [table.item(row, 0).itemData() for row in range(table.rowCount())]
        view = self.items._list_view
        return [view.itemFromIndex(view.model().index(row, 0)).itemData()
                for row in range(view.itemCount())]

    def assert_sorted(self, column, descending, expected_rows=None):
        visible = self.visible_rows()
        expected_rows = self.rows if expected_rows is None else expected_rows
        self.assertCountEqual([row[1] for row in visible], [row[1] for row in expected_rows])
        keys = [asset_sort_key(row, column) for row in visible]
        self.assertEqual(keys, sorted(keys, reverse=descending))
        if self.widget.isList():
            table = self.items._table_widget
            for row_index, data in enumerate(visible):
                for column_index in range(table.columnCount()):
                    self.assertEqual(table.item(row_index, column_index).itemData(), data)

    def load_rows(self, table=False, rows=None):
        self.widget.setItemsList(self.rows if rows is None else rows)
        if table:
            self.widget.setListMode()
        else:
            self.widget.setIconMode(120)
        self.drain_batches()

    def test_numeric_dates_and_note_field(self):
        self.assertLess(asset_sort_key((2,), 0), asset_sort_key(("10",), 0))
        self.assertEqual(asset_sort_key((None,), 0), 0)
        self.assertEqual(asset_sort_key(("invalid",), 0), 0)
        self.assertEqual(asset_sort_key((1, "name"), 7), "")
        row = self.rows[0]
        self.assertEqual(asset_sort_key(row, 7), row[8].lower())

    def test_all_fields_both_directions_in_both_views(self):
        for table in (False, True):
            self.load_rows(table)
            for column in range(8):
                for descending in (False, True):
                    with self.subTest(table=table, column=column, descending=descending):
                        self.widget.sortItems(column, descending)
                        self.assert_sorted(column, descending)

    def test_view_switch_filter_and_reload_keep_sort(self):
        self.load_rows()
        self.widget.sortItems(7, False)
        self.widget.setListMode()
        self.drain_batches()
        self.assert_sorted(7, False)
        self.widget.setIconMode(120, ["Asset_01"])
        self.drain_batches()
        expected = [row for row in self.rows if "Asset_01" in row[1]]
        self.assert_sorted(7, False, expected)
        replacement = make_rows(57)
        self.widget.clear()
        self.widget.setItemsList(replacement)
        self.widget.addItems()
        self.drain_batches()
        self.assert_sorted(7, False, replacement)

    def test_sort_changes_during_pending_batches(self):
        for table in (False, True):
            self.widget.setItemsList(self.rows)
            if table:
                self.widget.setListMode()
            else:
                self.widget.setIconMode(120)
            self.widget.sortItems(7, False)
            self.drain_batches()
            self.assert_sorted(7, False)

    def test_clear_cancels_pending_rows(self):
        for table in (False, True):
            self.widget.setItemsList(self.rows)
            if table:
                self.widget.setListMode()
            else:
                self.widget.setIconMode(120)
            self.widget.clear()
            self.widget.setItemsList([])
            for _ in range(5):
                APP.processEvents()
                time.sleep(0.01)
            self.assertEqual(self.widget.itemCount(), 0)

    def test_streamed_batches_keep_selected_sort_and_complete_rows(self):
        for table in (False, True):
            self.widget.clear()
            self.widget.setIsList(table)
            self.widget.sortItems(3, False)
            for start in range(0, len(self.rows), 50):
                end = min(start + 50, len(self.rows))
                for row in self.rows[start:end]:
                    self.widget.addItem(row)
                self.widget.setItemsList(self.rows[:end])
                self.widget.sortItems(3, False)
                self.assert_sorted(3, False, self.rows[:end])

    def test_sort_preserves_current_selection(self):
        for table in (False, True):
            self.load_rows(table)
            view = self.items.currentWidget()
            if table:
                view.selectRow(3)
            else:
                view.selectionModel().select(
                    view.model().index(3, 0), QtCore.QItemSelectionModel.Select)
            selected_names = [item.itemData()[1] for item in self.widget.selectedItems()]
            self.widget.sortItems(7, False)
            self.assertEqual(
                [item.itemData()[1] for item in self.widget.selectedItems()], selected_names)

    def test_header_and_menu_use_same_toggle_without_query(self):
        self.load_rows(table=True)
        # 不调用控制器构造函数，避免启动其数据库查询和三维预览。
        class Controller:
            _do_sort = AssetToolsUI._do_sort

        controller = Controller()
        controller._current_sort = (0, True)
        controller.ui_main_wgt = self.widget
        self.widget.sortRequested.connect(controller._do_sort)
        header = self.items._table_widget.horizontalHeader()
        for column, expected in ((1, (1, False)), (1, (1, True)), (7, (7, False))):
            header.sectionClicked.emit(column)
            self.assertEqual(controller._current_sort, expected)
            self.assert_sorted(*expected)
            self.assertEqual(header.sortIndicatorSection(), column)
            self.assertEqual(header.sortIndicatorOrder(),
                             QtCore.Qt.DescendingOrder if expected[1] else QtCore.Qt.AscendingOrder)

    def test_menu_fields_icons_and_action_binding(self):
        self.load_rows()
        controller = QtWidgets.QWidget()
        controller._current_sort = (0, True)
        controller.scriptsPath = AssetToolsUI.scriptsPath
        controller.sort_bttn = QtWidgets.QToolButton(controller)
        controller.ui_main_wgt = self.widget
        controller._do_sort = lambda column: AssetToolsUI._do_sort(controller, column)
        labels = [
            "按日期排序", "按资产名排序", "按中文名排序", "按模型制作排序",
            "按模型状态排序", "按绑定制作排序", "按绑定状态排序", "按备注排序",
        ]

        def choose_note(menu, position):
            actions = menu.actions()
            self.assertEqual([action.text() for action in actions], labels)
            self.assertFalse(actions[controller._current_sort[0]].icon().isNull())
            actions[7].trigger()

        class InspectMenu(QtWidgets.QMenu):
            exec_ = choose_note

        # 拦截弹出操作，检查真实菜单和 QAction 回调，不显示窗口。
        with mock.patch.object(QtWidgets, "QMenu", InspectMenu):
            AssetToolsUI.sort_asset_ui(controller)
        self.assertEqual(controller._current_sort, (7, False))
        self.assert_sorted(7, False)
        controller.deleteLater()


if __name__ == "__main__":
    unittest.main(verbosity=2)
