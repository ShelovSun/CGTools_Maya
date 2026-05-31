#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets
from config import projectSetting


class UserMenuWidget(QtWidgets.QWidget):
    """ 选择User的面板 """
    user_list = projectSetting()["user_list"]

    def __init__(self, parent=None):
        super(UserMenuWidget, self).__init__(parent)

        self.exist_name = []
        self._itemsWidget = None
        self.setWindowFlags(QtGui.Qt.Dialog | QtGui.Qt.FramelessWindowHint)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(2, 2, 2, 2)
        self.layout.setSpacing(0)
        self.line = QtWidgets.QLineEdit(self)
        self.line.returnPressed.connect(self.construct_tree)
        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setHeaderHidden(True)
        self.layout.addWidget(self.line)
        self.layout.addWidget(self.tree)
        self.setLayout(self.layout)

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

    def construct_tree(self, exist_name=""):
        """ 构建树状 """

        if exist_name and exist_name != "":
            self.exist_name = exist_name.split(",")

        self.tree.clear()
        _filter = self.line.text()
        items = []
        for pkg_name in self.user_list.keys():
            item = QtWidgets.QTreeWidgetItem(self.tree, [pkg_name])
            flags = item.flags()
            flags ^= QtGui.Qt.ItemIsSelectable
            flags ^= QtGui.Qt.ItemIsDropEnabled
            item.setFlags(flags)
            for child_title in self.user_list[pkg_name]:
                if child_title.find(_filter) != -1:
                    node_item = QtWidgets.QTreeWidgetItem(item, [child_title])
                    # node_item.setData(0, QtGui.Qt.UserRole, self.user_list[pkg_name][node_title])
                    node_item.setFlags(node_item.flags() ^ QtGui.Qt.ItemIsDropEnabled)
                    if child_title in self.exist_name:
                        node_item.setCheckState(0, QtGui.Qt.Checked)
                    else:
                        node_item.setCheckState(0, QtGui.Qt.Unchecked)
            item.setExpanded(True)

    def setUp(self, exist_name):
        """ 打开 """
        self.show()
        self.exist_name = []
        self.construct_tree(exist_name)

    def shoutDown(self):
        """ 关闭 """
        print("user menu close")
        super().close()
        checkedItems = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            for j in range(item.childCount()):
                if item.child(j).checkState(0) == QtCore.Qt.CheckState.Checked:
                    checkedItems.append(item.child(j).text(0))
        return checkedItems


class UserMenuWidgetNoCheck(UserMenuWidget):
    """ 选择User的面板 """

    def __init__(self, parent=None):
        super(UserMenuWidgetNoCheck, self).__init__(parent)
        self.tree.itemClicked.connect(self.handle_item_clicked)

    def construct_tree(self, exist_name=""):
        """ 构建树状 """
        self.tree.clear()
        _filter = self.line.text()
        for pkg_name in self.user_list.keys():
            item = QtWidgets.QTreeWidgetItem(self.tree, [pkg_name])
            flags = item.flags()
            flags ^= QtGui.Qt.ItemIsSelectable
            flags ^= QtGui.Qt.ItemIsDropEnabled
            item.setFlags(flags)
            for child_title in self.user_list[pkg_name]:
                if child_title.find(_filter) != -1:
                    node_item = QtWidgets.QTreeWidgetItem(item, [child_title])
                    # node_item.setData(0, QtGui.Qt.UserRole, self.user_list[pkg_name][node_title])
                    node_item.setFlags(node_item.flags() ^ QtGui.Qt.ItemIsDropEnabled)
            item.setExpanded(True)

    def handle_item_clicked(self, item, column):
        """ 点击触发 """
        if item.childCount() == 0:  # 如果非父级
            # print(item.text(0))
            self.itemsWidget().artist_changed(item.text(0))
            # self.update_asset(item.text(0))
        self.shoutDown()

    # def update_asset(self, text):
    #     """ """
    #     self.itemsWidget().artist_changed(text)

    def shoutDown(self):
        """ 关闭 """
        print("user menu close")
        super().close()


class SponsorMenuWidgetNoCheck(UserMenuWidgetNoCheck):
    """ 选择User的面板 """

    def __init__(self, parent=None):
        super(SponsorMenuWidgetNoCheck, self).__init__(parent)

    def handle_item_clicked(self, item, column):
        """ 点击触发 """
        if item.childCount() == 0: # 如果非父级
            # print(item.text(0))
            self.itemsWidget().sponsor_changed(item.text(0))
            # self.update_asset(item.text(0))
        self.shoutDown()

