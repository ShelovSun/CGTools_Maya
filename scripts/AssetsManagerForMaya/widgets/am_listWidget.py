#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

# import os
# import math
# import json
# import requests
# import imagesequence

from widgets.am_delegate import MainDelegate
from widgets import am_listItem
# from utils import jsonHelper, publish
# from my_vendor import six
# from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

# import importlib
# importlib.reload(listItem)


class MainListWidget(QtWidgets.QListWidget):
    """ 主窗微缩图显示 """
    dragLeaveSignal = QtCore.Signal()

    DEF_SPACING = 8

    def __init__(self, db="FFA", tab="Asset", user="", password=""):
        super(MainListWidget, self).__init__()
        # self.host = projectSetting()["host"]
        # self.db = db
        # self._tab = tab
        # self.user = user
        # self.password = password
        self._itemsList = []
        self._itemSize = 120
        self._currentItem = None
        self.setDragEnabled(False)  # ? 不起作用
        # self.setAcceptDrops()
        self.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setSortingEnabled(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ContiguousSelection)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setTextElideMode(QtCore.Qt.ElideNone)
        self.setMouseTracking(True)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setWordWrap(True)

        self._delegate = MainDelegate()
        self._delegate.setItemsWidget(self)
        self.setItemDelegate(self._delegate)

    def setItemList(self, _list):
        self._itemsList = _list

    def dragLeaveEvent(self, e):
        print("drag Leave")
        self.dragLeaveSignal.emit()

    def mouseMoveEvent(self, e):
        # print("mouseMoveEvent")
        super(MainListWidget, self).mouseMoveEvent(e)
        item = self.itemAt(e.pos())
        # if self.isList():
        #     return
        # else:
        self.itemUpdateEvent(item, e)

    def leaveEvent(self, event):
        if self._currentItem:
            self.itemMouseLeaveEvent(self._currentItem, event)
            self._currentItem = None

    def itemUpdateEvent(self, item, event):
        """
        Triggered on user key press events for the current viewport.
        :type item: studioqt.Item
        :type event: QtCore.QKeyEvent
        :rtype: None
        """
        if id(self._currentItem) != id(item):
            if self._currentItem:
                self.itemMouseLeaveEvent(self._currentItem, event)
                self._currentItem = None
            if item and not self._currentItem:
                self._currentItem = item
                self.itemMouseEnterEvent(item, event)
        # if self._currentItem:
        #     self.itemMouseMoveEvent(item, event)

    @staticmethod
    def itemMouseEnterEvent(item, event):
        """
        Triggered when the mouse enters the given item.
        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        """
        item.mouseEnterEvent(event)

    @staticmethod
    def itemMouseLeaveEvent(item, event):
        """
        Triggered when the mouse leaves the given item.
        :type item: QtWidgets.QTreeWidgetItem
        :type event: QtWidgets.QMouseEvent
        """
        item.mouseLeaveEvent(event)

    # def resizeEvent(self, e):
    #     super(MyQListWiget, self).resizeEvent(e)
    #     self.updateIcons()
    #
    # def wheelEvent(self, e):
    #     super(MyQListWiget, self).wheelEvent(e)
    #     self.updateIcons()

    # @staticmethod
    # def getItemsDictFromPath(__root, __tab, __project, __type):
    #     """
    #     从路径获取字典
    #     :return: [{'role_name': xx, 'project': xx, 'type': xx, 'zh_name': xx, 'icon_path': xx}]
    #     """
    #     # print("getItemsDictFromPath")
    #     __items_dict = []
    #     __path = '{0}/{1}/{2}/{3}'.format(__root, __project, __tab, __type)
    #     dir = QtCore.QDir(__path)
    #     for role_name in dir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot):
    #         icon_path = '{0}/{1}/Icon/{1}.png'.format(__path, role_name)
    #         zn_name = ""
    #         bbb = {'role_name': role_name, 'project': __project, 'type': __type,
    #                'zh_name': zn_name, 'icon_path': icon_path}
    #         __items_dict.append(bbb)
    #
    #     return __items_dict
    #
    # def getItemsDictFromCGTW(self, __tab, __project, __type):
    #     """
    #     从CGTW获取item字典
    #     :return: [{'role_name': xx, 'project': xx, 'type': xx, 'zh_name': xx, 'icon_path': xx}]
    #     """
    #     import cgtw2
    #     t_tw = cgtw2.tw()
    #     token = t_tw.login.token()
    #     __items_dict = []
    #     asset, assetmaya, assetstapy, entity, cn_name, image = self.get_CGTW_entity(__tab, __type)
    #
    #     path = '{0}/{1}/{2}/{3}'.format(projectSetting()['rootPath'], __project, __tab, __type)
    #     TW_proj = str(projectSetting()['projectdiction'][__project])
    #     t_asset_ids = t_tw.info.get_id(TW_proj, asset, [[assetmaya, '=', u"完成"], 'and', [assetstapy, '=', __type]])
    #     TW_dictionInfo = t_tw.info.get(TW_proj, asset, t_asset_ids, [entity, cn_name, image])
    #     for info in TW_dictionInfo:
    #         icon_path = '{0}/{1}/Icon/{1}.png'.format(path, info[entity])
    #         # if info[image] != "":
    #         #     icon_url = 'http://10.0.203.40%s?token=%s' % (json.loads(info[image])[0].get("max"), token)
    #         # else:
    #         #     icon_url = ""
    #         bbb = {'role_name': info[entity], 'project': __project, 'type': __type,
    #                'zh_name': info[cn_name], 'icon_path': icon_path}
    #         __items_dict.append(bbb)
    #
    #     return __items_dict
    #
    # @staticmethod
    # def get_CGTW_entity(_tab, _type):
    #     if _tab == 'Assets':
    #         return 'asset', 'asset.maya', 'asset.assetstapy', 'asset.entity', 'asset.cn_name', 'asset.image'
    #     elif _tab == 'Scenes':
    #         if _type != "Map":
    #             return 'scenes', 'scenes.maya', 'scenes.scenesassetstype', 'scenes.entity', 'scenes.assetsnamecn', 'scenes.image'
    #         else:
    #             return 'map', 'map.maya', 'map.type', 'map.entity', 'map.mapnamecn', 'map.image'
    #
    # def itemsdict(self):
    #     return self._itemsDict
    #
    # def setItemsdict(self, dict):
    #     self._itemsDict = dict

    def itemSize(self):
        return self._itemSize

    def setItemSize(self, itemSize):
        # print("itemSize:", itemSize)
        self._itemSize = itemSize

    # def setListMode(self):
    #     """
    #     列表显示
    #     """
    #     # print("_viewList")
    #     self.setViewMode(QtWidgets.QListView.ListMode)
    #     self.setGridSize(QtCore.QSize(2000, 25))
    #     self.setSpacing(1)
    #     self.setAlternatingRowColors(True)
    #
    # def setIconMode(self):
    #     """
    #     缩略图显示
    #     """
    #     # print("_viewThumb", self._itemSize)
    #     self.setViewMode(QtWidgets.QListView.IconMode)
    #     self.setIconSize(QtCore.QSize(self._itemSize, self._itemSize))
    #     self.setGridSize(QtCore.QSize(self._itemSize + self.DEF_SPACING, self._itemSize + self.DEF_SPACING + 40))
    #     self.setSpacing(2)  # 不起作用
    #     self.setWordWrap(True)
    #     self.setAlternatingRowColors(False)
    #     # self.setStyleSheet(self._thumbStyleSheet())

    def resizeItem(self):
        """
        整理下
        """
        self.setIconSize(QtCore.QSize(self._itemSize, self._itemSize))
        self.setGridSize(QtCore.QSize(self._itemSize + self.DEF_SPACING, self._itemSize + self.DEF_SPACING + 40))
        self.setSpacing(2)  # 不起作用

    def _thumbStyleSheet(self):
        """   """
        itemSize = float('%.2f' % self._itemSize)
        icon_percent = itemSize / (itemSize + 40.00)
        icon_down_percent = icon_percent + 0.01

        hoverStyle = "QListWidget:item:hover{background-color:qlineargradient(spread:pad, y1:0, y2:1, stop:%s rgb(62, " \
                     "64, 66), stop:%s rgb(40, 40, 40));border: 1.5px solid #666666;}" % (str(icon_percent),
                                                                                          str(icon_down_percent))
        selectedStyle = "QListWidget:item:selected{background-color:qlineargradient(spread:pad, y1:0, y2:1, " \
                        "stop:%s rgb(65, 69, 75), stop:%s rgb(82, 133, 166));border: 1.5px solid rgb(82, 133, " \
                        "166);}" % (str(icon_percent),
                                    str(icon_down_percent))
        style = "QListWidget:item{border-radius: 8px;background-color:qlineargradient(spread:pad, y1:0, y2:1, " \
                "stop:0 rgb(35, 35, 35), stop:%s rgb(60, 62, 64), stop:%s rgb(30, 30, 30));border: 1.5px solid " \
                "#1e1e1e;}" % (str(icon_percent),
                               str(icon_down_percent))
        return hoverStyle + selectedStyle + style

    def add_item(self, data):
        _item = am_listItem.ListItem()
        _item.setItemsWidget(self)
        # _item.setSize(self.ui.itemSize_Slider.value())
        _item.setItemData(data)
        self.addItem(_item)

    def addItems(self, keyWords=u"", add=False):
        """
        Add the given items to this widget.
        :param add: bool
        :param keyWords:str
        """
        print("== list addItems")
        if not add:
            self.clear()
        for i in self._itemsList:
            _item = am_listItem.ListItem(tab=self._tab)
            if i[1].lower().find(keyWords.lower()) != -1 or (i[2] and i[2].find(keyWords) != -1):
                _item.setItemData(i)
                _item.setItemsWidget(self)
                _item.setText(i[1])  # 为了有个排序
                self.addItem(_item)

    def countItemsIndexStart(self):
        width = self.width()
        scrollBarY = self.verticalScrollBar().value()
        column = width // (self._itemSize + self.DEF_SPACING)
        row = scrollBarY / (self._itemSize + self.DEF_SPACING + 40)
        return column * row

    def countItemsIndexEnd(self):
        width = self.width()
        scrollBarY = self.verticalScrollBar().value()
        height = self.height() + scrollBarY
        column = width // (self._itemSize + self.DEF_SPACING)
        row = height / (self._itemSize + self.DEF_SPACING + 40) + 1
        return column * row

    def updateIcons(self):
        """   """
        __updatedNum = 0
        start_index = self.countItemsIndexStart()
        end_index = self.countItemsIndexEnd()
        if end_index > self.count():
            end_index = self.count()

        for index in range(start_index, end_index):
            item = self.item(index)
            itemData = item.data(QtCore.Qt.UserRole)
            if item.isloaded():
                pass
            else:
                icon_path = itemData['icon_path']
                item.setIcon(icon_path)
                item.setloaded()
                __updatedNum += 1
        return __updatedNum
