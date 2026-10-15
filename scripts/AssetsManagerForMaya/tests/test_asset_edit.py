#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""使用 mayapy + 真实 Qt 控件验证编辑流程；数据库连接全部替换为内存 mock。"""

import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.dont_write_bytecode = True
TOOL_ROOT = Path(__file__).resolve().parents[1]
for path in (
    TOOL_ROOT,
    TOOL_ROOT.parent,
    TOOL_ROOT.parent / "tools_ani" / "StudioLibrary",
    TOOL_ROOT.parent / "Python" / "Python37" / "Lib" / "site-packages",
):
    sys.path.append(str(path))

from PySide2 import QtCore, QtGui, QtTest, QtWidgets
from sources.assetTools import AssetToolsUI
from widgets.am_main_optimized import MainStackedWidget

APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])


def make_row(folder, name="SameName", zh_name="旧中文名"):
    return (
        20261015, name, zh_name, "Artist", "未开始", "Artist", "未开始",
        "C:/__cgtools_edit_test__/GOF/{0}/Building/{1}/Icon/{1}.png".format(folder, name),
        "Note",
    )


class AssetEditTests(unittest.TestCase):
    def setUp(self):
        self.widget = MainStackedWidget()
        self.items = self.widget.itemsWidget()
        self.table = self.items._table_widget
        self.ctrl = SimpleNamespace(
            currentProject=lambda: "GOF", user="test_user", password="test_password",
            host="smnas.diandian.info", tab="All", _asset_cache=[],
            ui_main_wgt=self.widget, preview=mock.Mock(),
        )
        self.widget.setItemsWidget(self.ctrl)
        self.widget.rowDataChanged.connect(
            lambda old, new: AssetToolsUI._onItemDataChanged(self.ctrl, old, new)
        )
        self.connection = mock.MagicMock()
        self.cursor = self.connection.cursor.return_value
        self.cursor.rowcount = 1
        self.connect_patch = mock.patch("psycopg2.connect", return_value=self.connection)
        self.connect = self.connect_patch.start()
        self.warning_patch = mock.patch.object(QtWidgets.QMessageBox, "warning")
        self.warning = self.warning_patch.start()

    def tearDown(self):
        self.widget.clear()
        self.widget.close()
        self.widget.deleteLater()
        APP.processEvents()
        self.warning_patch.stop()
        self.connect_patch.stop()

    def load(self, rows):
        self.ctrl._asset_cache = list(rows)
        self.widget.setItemsList(rows)
        self.widget.setListMode()

    def select(self, folder, column=2):
        for row in range(self.table.rowCount()):
            if "/{}/".format(folder) in self.table.item(row, 0).itemData()[7]:
                self.table.setCurrentCell(row, column)
                return self.table.item(row, column)
        self.fail("Missing row: " + folder)

    def assert_query(self, table, field, value, name="SameName"):
        self.cursor.execute.assert_called_once_with(
            'UPDATE public.{0} SET "{1}" = %s WHERE "{0}.name" = %s'.format(table, field),
            (value, name),
        )
        self.connection.commit.assert_called_once_with()
        self.connection.rollback.assert_not_called()
        self.connect.assert_called_once_with(
            database="GOF", user="test_user", password="test_password",
            host="smnas.diandian.info", port="5432", connect_timeout=5,
        )
        self.cursor.close.assert_called_once_with()
        self.connection.close.assert_called_once_with()
        self.warning.assert_not_called()

    def open_editor(self, folder="Scenes"):
        item = self.select(folder)
        self.widget.resize(1000, 400)
        self.widget.show()
        APP.processEvents()
        self.table.show_edit_menu()
        APP.processEvents()
        self.assertTrue(self.table.note_menu.isVisible())
        return item, self.table.note_menu.line

    def test_scene_name_writes_scene_with_same_named_asset_present(self):
        self.load([make_row("Assets"), make_row("Scenes")])
        item = self.select("Scenes")
        value = "亭子（新）"
        self.assertTrue(self.table.zh_name_changed(value))
        self.assert_query("scene", "scene.zh_name", value)
        self.assertEqual(item.text(), value)
        self.assertEqual(self.select("Assets").text(), "旧中文名")

    def test_asset_unicode_and_quotes_are_sql_parameters(self):
        name = "O'Brien"
        self.load([make_row("Assets", name=name)])
        self.select("Assets")
        value = "新中文名 '测试'"
        self.assertTrue(self.table.zh_name_changed(value))
        self.assert_query("asset", "asset.zh_name", value, name)

    def test_return_commits_once_and_disables_unbound_native_editor(self):
        self.load([make_row("Scenes")])
        item, line = self.open_editor()
        self.assertEqual(self.table.editTriggers(), QtWidgets.QAbstractItemView.NoEditTriggers)
        QtTest.QTest.keyClicks(line, "NewName")
        QtTest.QTest.keyClick(line, QtCore.Qt.Key_Return)
        APP.processEvents()
        self.assertEqual(item.text(), "NewName")
        self.assertFalse(self.table.note_menu.isVisible())
        self.assert_query("scene", "scene.zh_name", "NewName")

    def test_double_click_opens_only_the_saving_editor(self):
        self.load([make_row("Scenes")])
        item = self.select("Scenes")
        self.widget.resize(1000, 400)
        self.widget.show()
        APP.processEvents()
        point = self.table.visualItemRect(item).center()
        QtTest.QTest.mouseClick(self.table.viewport(), QtCore.Qt.LeftButton, pos=point)
        QtTest.QTest.mouseDClick(self.table.viewport(), QtCore.Qt.LeftButton, pos=point)
        APP.processEvents()
        self.assertTrue(self.table.note_menu.isVisible())
        self.assertEqual(self.table.viewport().findChildren(QtWidgets.QLineEdit), [])
        QtTest.QTest.keyClicks(self.table.note_menu.line, "DoubleClicked")
        QtTest.QTest.keyClick(self.table.note_menu.line, QtCore.Qt.Key_Return)
        self.assertEqual(item.text(), "DoubleClicked")
        self.assert_query("scene", "scene.zh_name", "DoubleClicked")

    def test_focus_out_saves_and_escape_cancels(self):
        self.load([make_row("Scenes")])
        item, line = self.open_editor()
        QtTest.QTest.keyClicks(line, "SavedOnFocusOut")
        APP.sendEvent(line, QtGui.QFocusEvent(QtCore.QEvent.FocusOut))
        self.assertEqual(item.text(), "SavedOnFocusOut")
        self.assert_query("scene", "scene.zh_name", "SavedOnFocusOut")
        self.cursor.execute.reset_mock()
        self.connection.commit.reset_mock()
        item, line = self.open_editor()
        QtTest.QTest.keyClicks(line, "Cancelled")
        QtTest.QTest.keyClick(line, QtCore.Qt.Key_Escape)
        APP.processEvents()
        self.assertFalse(self.table.note_menu.isVisible())
        self.assertEqual(item.text(), "SavedOnFocusOut")
        self.cursor.execute.assert_not_called()

    def test_edit_target_survives_selection_change(self):
        self.load([make_row("Assets"), make_row("Scenes")])
        scene, line = self.open_editor()
        self.select("Assets", 1)
        line.setText("OriginalTarget")
        self.assertTrue(self.table.note_menu.note_edit_finished())
        self.assertEqual(scene.text(), "OriginalTarget")
        self.assertEqual(self.select("Assets").text(), "旧中文名")
        self.assert_query("scene", "scene.zh_name", "OriginalTarget")

    def test_success_updates_all_caches_sorting_and_view_switches(self):
        rows = [make_row("Scenes", "One", "A"), make_row("Assets", "Two", "M")]
        self.load(rows)
        self.widget.setIconMode(120)
        self.widget.setListMode()
        self.widget.sortItems(2, False)
        item = self.select("Scenes")
        self.assertTrue(self.table.zh_name_changed("Z"))
        expected = tuple("Z" if index == 2 else value for index, value in enumerate(rows[0]))
        self.assertIn(expected, self.widget.itemsList())
        self.assertIn(expected, self.ctrl._asset_cache)
        self.assertEqual(item.row(), 1)
        for column in range(self.table.columnCount()):
            self.assertEqual(self.table.item(item.row(), column).itemData(), expected)
        self.widget.setIconMode(120)
        view = self.items._list_view
        self.assertEqual(view.itemFromIndex(view.model().index(1, 0)).itemData(), expected)
        self.widget.setListMode()
        self.assertEqual(self.select("Scenes").text(), "Z")

    def test_failed_write_keeps_old_text_and_caches(self):
        for failure in ("no_rows", "multiple_rows", "execute_error", "commit_error"):
            with self.subTest(failure=failure):
                rows = [make_row("Scenes")]
                self.load(rows)
                item = self.select("Scenes")
                self.cursor.rowcount = {"no_rows": 0, "multiple_rows": 2}.get(failure, 1)
                self.cursor.execute.side_effect = RuntimeError("Write failed") if failure == "execute_error" else None
                self.connection.commit.side_effect = RuntimeError("Commit failed") if failure == "commit_error" else None
                self.assertFalse(self.table.zh_name_changed("NotSaved"))
                self.assertEqual(item.text(), "旧中文名")
                self.assertEqual(self.widget.itemsList(), rows)
                self.assertEqual(self.ctrl._asset_cache, rows)
                self.connection.rollback.assert_called()
                self.warning.assert_called()
                self.connection.reset_mock()
                self.warning.reset_mock()

    def test_scene_status_and_artist_use_shared_scene_fields(self):
        for column, value, field, mirror in (
            (3, "NewArtist", "scene.artist", 5),
            (5, "NewRigger", "scene.artist", 3),
            (4, "UE", "scene.status", 6),
            (6, "已完成", "scene.status", 4),
        ):
            with self.subTest(column=column):
                self.load([make_row("Scenes")])
                item = self.select("Scenes", column)
                if column in (3, 5):
                    self.table.artist_changed(value)
                else:
                    self.table.status_changed(value)
                self.assert_query("scene", field, value)
                self.assertEqual(item.text(), value)
                self.assertEqual(self.table.item(item.row(), mirror).text(), value)
                self.connection.reset_mock()
                self.connect.reset_mock()

    def test_asset_status_and_artist_keep_independent_columns(self):
        for column, value, field, other_column in (
            (3, "NewArtist", "asset.mod_artist", 5),
            (5, "NewRigger", "asset.rig_artist", 3),
            (4, "UE", "asset.mod_status", 6),
            (6, "已完成", "asset.rig_status", 4),
        ):
            with self.subTest(column=column):
                row = make_row("Assets")
                self.load([row])
                item = self.select("Assets", column)
                if column in (3, 5):
                    self.table.artist_changed(value)
                else:
                    self.table.status_changed(value)
                self.assert_query("asset", field, value)
                self.assertEqual(item.text(), value)
                self.assertEqual(self.table.item(item.row(), other_column).text(), row[other_column])
                self.connection.reset_mock()
                self.connect.reset_mock()

    def test_refresh_cancels_stale_editor(self):
        self.load([make_row("Scenes")])
        item, line = self.open_editor()
        line.setText("DiscardOnRefresh")
        self.widget.clear()
        self.assertFalse(self.table.note_menu.isVisible())
        self.table.note_menu.note_edit_finished()
        self.cursor.execute.assert_not_called()


if __name__ == "__main__":
    unittest.main(verbosity=2)
