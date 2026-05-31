#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

# import os
import psycopg2
# import json
# import requests
# import imagesequence

from widgets.am_delegate import MainDelegate
# from utils import jsonHelper, publish
# from my_vendor import six
# from tableItem \
from widgets import am_tableItem, user_menu, note_menu

# import importlib
# importlib.reload(tableItem)

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

__all__ = ["MainTableWidget"]


class MainTableWidget(QtWidgets.QTableWidget):
    """ 主窗表格显示 """
    dragLeaveSignal = QtCore.Signal()

    table_header = ["创建日期", "资产名", "中文名", "模型制作", "模型状态", "绑定制作", "绑定状态", "备注"]

    def __init__(self, db="FFA", tab="Asset", user="", password=""):
        super(MainTableWidget, self).__init__()
        # self.host = projectSetting()["host"]
        self.db = db
        self._tab = tab
        self.user = user
        self.password = password
        self._itemsList = []

        self._itemsWidget = None
        self.setColumnCount(len(self.table_header))
        self.setColumnWidth(0, 80)
        self.setColumnWidth(1, 190)
        self.setColumnWidth(2, 120)
        self.setColumnWidth(3, 60)
        self.setColumnWidth(4, 60)
        self.setColumnWidth(5, 60)
        self.setColumnWidth(6, 60)
        self.setColumnWidth(7, 80)

        # self.horizontalHeader().setSectionResizeMode(7, QtWidgets.QHeaderView.Stretch)

        self.font = QtGui.QFont()
        self.font.setFamily(u"Microsoft YaHei UI")
        self.font.setPointSize(10)
        self.setFont(self.font)
        # _item = QtWidgets.QTableWidgetItem()
        # _item.setText("XXX")
        # _item.setIcon(QtGui.QIcon("%s/icon/Default.png" % scriptsPath))
        # self.setHorizontalHeaderItem(2, _item)
        self.setHorizontalHeaderLabels(self.table_header)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setMinimumHeight(25)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setFont(self.font)
        self.horizontalHeader().sectionClicked.connect(self.sortByColumn)

        self.verticalHeader().setVisible(True)

        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        # self.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.clicked.connect(self.cellClicked)
        self.cellDoubleClicked.connect(self.show_edit_menu)
        ''' 附加面板 '''
        # self.filter_menu = filter_menu.FilterMenuWidget(self)
        # self.filter_menu.setItemsWidget(self)
        # self.is_filter_menu = False

        self.user_menu = user_menu.UserMenuWidgetNoCheck(self)
        self.user_menu.setItemsWidget(self)
        self.is_user_menu = False

        self.note_menu = note_menu.NoteMenuWidget(self)
        self.note_menu.setItemsWidget(self)
        self.is_note_menu = False

        self.setDragEnabled(True)

        self._delegate = MainDelegate()
        self._delegate.setItemsWidget(self)
        self.setItemDelegate(self._delegate)

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

    def dragLeaveEvent(self, e):
        print("drag Leave")
        self.dragLeaveSignal.emit()

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # if self.is_filter_menu:
        #     self.filter_menu.close()
        if self.is_user_menu:
            self.user_menu.close()
        if self.is_note_menu:
            self.note_menu.close()

    def cellClicked(self):
        item = self.currentItem()
        table_pos = self.viewport().mapToGlobal(self.pos())
        rectX = self.visualItemRect(item).left() + table_pos.x()
        rectX_end = rectX + self.visualItemRect(item).width() / 3 * 2
        pos = QtGui.QCursor.pos()
        if item and pos.x() > rectX_end:
            if item.column() == 3:  # 模型制作
                self.show_user_menu()
            if item.column() == 4:  # 模型状态
                self.show_status_menu()
            if item.column() == 5:  # 绑定制作
                self.show_user_menu()
            if item.column() == 6:  # 绑定状态
                self.show_status_menu()

    def show_edit_menu(self):
        """ 双击弹出文字编辑菜单 """
        print("开始编辑文字", self.currentItem().column())
        item = self.currentItem()
        table_pos = self.viewport().mapToGlobal(self.pos())
        rectX = self.visualItemRect(item).left() + table_pos.x()
        rectY = self.visualItemRect(item).top() + table_pos.y()
        rectW = self.visualItemRect(item).width()
        rectH = self.visualItemRect(item).height()

        if item.column() == 2:  # 中文名
            self.note_menu.setUp(item.text())
            self.note_menu.setGeometry(rectX, rectY, rectW, rectH)
            self.is_note_menu = True

    def show_user_menu(self):
        """ 弹出制作者选择菜单 """
        # print("展示", self.visualItemRect(pressed_item))
        item = self.currentItem()
        table_pos = self.viewport().mapToGlobal(self.pos())
        rectX = self.visualItemRect(item).left() + table_pos.x()
        rectY = self.visualItemRect(item).bottom() + table_pos.y()
        self.user_menu.setUp(exist_name='')
        self.user_menu.setGeometry(rectX, rectY, 200, 300)
        self.is_user_menu = True

    def show_status_menu(self):
        """ 弹出状态选择菜单 """
        item = self.currentItem()
        table_pos = self.viewport().mapToGlobal(self.pos())
        rectX = self.visualItemRect(item).left() + table_pos.x()
        rectY = self.visualItemRect(item).bottom() + table_pos.y()
        menu = QtWidgets.QMenu()
        action_nodo = QtWidgets.QAction(u'未开始', self)
        action_nodo.triggered.connect(lambda: self.status_changed(action_nodo.text()))
        action_doing = QtWidgets.QAction(u'制作中', self)
        action_doing.triggered.connect(lambda: self.status_changed(action_doing.text()))
        action_done = QtWidgets.QAction(u'已完成', self)
        action_done.triggered.connect(lambda: self.status_changed(action_done.text()))

        menu.addAction(action_nodo)
        menu.addAction(action_doing)
        menu.addAction(action_done)
        menu.exec_(QtCore.QPoint(rectX, rectY))

    def zh_name_changed(self, text):
        """ 中文名改变 -> 数据库改变 -> 刷新 """
        db = self.db
        asset_name = self.get_current_asset()
        if self.currentColumn() == 2:  # 中文名
            self.update_asset(db, asset_name, "asset.zh_name", text)
            self.note_menu.close()
            self.selectedItems()[2].setName(text)

    def artist_changed(self, text):
        """ 制作人改变 -> 数据库改变 -> 刷新 """
        db = self.db
        asset_name = self.get_current_asset()
        if self.currentColumn() == 3:  # 模型制作人
            self.update_asset(db, asset_name, "asset.mod_artist", text)
            self.selectedItems()[3].setName(text)
        elif self.currentColumn() == 5:  # 绑定制作人
            self.update_asset(db, asset_name, "asset.rig_artist", text)
            self.selectedItems()[5].setName(text)

    def status_changed(self, text):
        """ 制作状态/任务状态改变 -> 数据库改变 -> 刷新 """
        db = self.db
        asset_name = self.get_current_asset()

        if self.currentColumn() == 4:  # 模型状态
            self.update_asset(db, asset_name, "asset.mod_status", text)
            self.selectedItems()[4].setName(text)
        elif self.currentColumn() == 6:  # 绑定状态
            self.update_asset(db, asset_name, "asset.rig_status", text)
            self.selectedItems()[6].setName(text)

    def get_current_asset(self):
        """ 获取当前创意名 """
        try:
            shot_name = self.item(self.row(self.selectedItems()[0]), 1).text()
            return shot_name
        except:
            return None

    def setItemList(self, _list):
        self._itemsList = _list

    def show_asset(self):
        """ """
        # data = self.itemsWidget().itemsWidget().getItemsList()
        # self.itemsWidget().itemsWidget().listWidgetAddItems(data)

    def add_item(self, data):
        """ """
        row = self.rowCount()
        self.insertRow(row)
        _item_date = am_tableItem.TableItem(str(data[0]))
        _item_date.setItemData(data)
        _item = am_tableItem.TableItem(data[1])
        _item_zh = am_tableItem.TableItem(data[2])

        _item_mod_artist = am_tableItem.TableModArtistItem(data[3])
        _item_mod_artist.setItemsWidget(self)
        _item_mod_status = am_tableItem.TableStatusItem(str(data[4]))
        _item_mod_status.setItemsWidget(self)

        _item_rig_artist = am_tableItem.TableRigArtistItem(data[5])
        _item_rig_artist.setItemsWidget(self)
        _item_rig_status = am_tableItem.TableStatusItem(str(data[6]))
        _item_rig_status.setItemsWidget(self)

        _item_note = am_tableItem.TableItem(data[8])

        self.setItem(row, 1, _item)
        self.setItem(row, 0, _item_date)
        self.setItem(row, 2, _item_zh)
        self.setItem(row, 3, _item_mod_artist)
        self.setItem(row, 4, _item_mod_status)
        self.setItem(row, 5, _item_rig_artist)
        self.setItem(row, 6, _item_rig_status)
        self.setItem(row, 7, _item_note)

    def addItems(self, keyWords=u"", add=False):
        # (20230215, 'BaiMoRen', '白模人', '孙学鹤', 2, '孙学鹤', 2, None)
        if not add:
            self.clearContents()

        row = 0
        for i in self._itemsList:
            if i[1].lower().find(keyWords.lower()) != -1 or (i[2] and i[2].find(keyWords) != -1):
                self.insertRow(row)
                _item_date = am_tableItem.TableItem(str(i[0]))
                _item_date.setItemData(i)
                _item = am_tableItem.TableItem(i[1])
                _item_zh = am_tableItem.TableItem(i[2])

                _item_mod_artist = am_tableItem.TableModArtistItem(i[3])
                _item_mod_artist.setItemsWidget(self)
                _item_mod_status = am_tableItem.TableStatusItem(str(i[4]))
                _item_mod_status.setItemsWidget(self)

                _item_rig_artist = am_tableItem.TableRigArtistItem(i[5])
                _item_rig_artist.setItemsWidget(self)
                _item_rig_status = am_tableItem.TableStatusItem(str(i[6]))
                _item_rig_status.setItemsWidget(self)

                _item_note = am_tableItem.TableItem(i[8])

                self.setItem(row, 1, _item)
                self.setItem(row, 0, _item_date)
                self.setItem(row, 2, _item_zh)
                self.setItem(row, 3, _item_mod_artist)
                self.setItem(row, 4, _item_mod_status)
                self.setItem(row, 5, _item_rig_artist)
                self.setItem(row, 6, _item_rig_status)
                self.setItem(row, 7, _item_note)
                row += 1

        self.sortItems(0, QtCore.Qt.DescendingOrder)

    # def set_mod_status_color(self):
    #     """ 设置状态颜色 """
    #     for row in range(0, self.rowCount()):
    #         if self.cellWidget(row, 4).currentText() == u"制作中":
    #             combo_StyleSheet = self.combo_StyleSheet_mod_doing
    #         elif self.cellWidget(row, 4).currentText() == u"已完成":
    #             combo_StyleSheet = self.combo_StyleSheet_mod_done
    #         else:
    #             combo_StyleSheet = self.combo_StyleSheet_undo
    #
    #         self.cellWidget(row, 4).setStyleSheet(combo_StyleSheet)
    #
    # def set_rig_status_color(self):
    #     """ 设置状态颜色 """
    #     for row in range(0, self.rowCount()):
    #         if self.cellWidget(row, 6).currentText() == u"制作中":
    #             combo_StyleSheet = self.combo_StyleSheet_rig_doing
    #         elif self.cellWidget(row, 6).currentText() == u"已完成":
    #             combo_StyleSheet = self.combo_StyleSheet_rig_done
    #         else:
    #             combo_StyleSheet = self.combo_StyleSheet_undo
    #
    #         self.cellWidget(row, 6).setStyleSheet(combo_StyleSheet)

    # def get_asset_database(self, _type, keyword=""):
    #     """ 得到数据 """
    #     conn = None
    #     cur = None
    #     get_script = '''
    #          SELECT "asset.date", "asset.name", "asset.zh_name", "asset.mod_artist", "asset.mod_status",
    #          "asset.rig_artist", "asset.rig_status", "asset.icon"
    #          FROM public."asset"
    #          WHERE
    #          "asset.type" = '%s';
    #          ''' % _type
    #     try:
    #         conn = psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host,
    #                                 port="5432")
    #         cur = conn.cursor()
    #         cur.execute(get_script)
    #         data = cur.fetchall()
    #         # print(data)
    #         self._itemsList = data
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         if cur is not None:
    #             cur.close()
    #         if conn is not None:
    #             conn.close()

    # def get_scene_database(self, _type, keyword=""):
    #     """ 得到数据 """
    #     conn = None
    #     cur = None
    #     get_script = '''
    #          SELECT "scene.date", "scene.name", "scene.zh_name", "scene.artist", "scene.status", "scene.icon"
    #          FROM public."scene"
    #          WHERE
    #          "asset.type" = '%s';
    #          ''' % _type
    #     try:
    #         conn = psycopg2.connect(database=self.db, user=self.user, password=self.password, host=self.host,
    #                                 port="5432")
    #         cur = conn.cursor()
    #         cur.execute(get_script)
    #         data = cur.fetchall()
    #         # print(data)
    #         self._itemsList = data
    #     except Exception as e:
    #         print(e)
    #     finally:
    #         if cur is not None:
    #             cur.close()
    #         if conn is not None:
    #             conn.close()

    def update_asset(self, db, asset_name, key, value):
        update_script = ''' 
            UPDATE public.asset SET
            "%s" = '%s' 
            WHERE
            "asset.name" = '%s';''' % (key, value, asset_name)
        print(update_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
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

    def update_scene(self, db, scene_name, key, value):
        update_script = ''' 
            UPDATE public.scene SET
            "%s" = '%s' 
            WHERE
            "scene.name" = '%s';''' % (key, value, scene_name)
        print(update_script)
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(database=db, user=self.user, password=self.password, host=self.host, port="5432")
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
