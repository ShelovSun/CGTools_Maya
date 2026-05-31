#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

import os
# import math
import json
import requests

# import imagesequence
# import maya.cmds as cmds

from utils import jsonHelper, publish
# from my_vendor import six
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

tempPath = "{}/AssetsManagerTemp".format(os.environ.get('APPDATA'))
scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('widgets', '')

__all__ = ["TableItem",
           "TableModArtistItem",
           "TableRigArtistItem",
           "TableStatusItem"]


class TableItem(QtWidgets.QTableWidgetItem):

    def __init__(self, name, tab="Asset", isCombo=False):
        super(TableItem, self).__init__()

        self._tab = tab
        self._isCombo = isCombo
        self._rect = None

        self.dpi = 1
        self.padding = 2

        self._itemData = {}
        self._name = name
        if self._name:
            self.setText(self._name)

        self._isFavor = False
        self._isTag = False

        self._itemsWidget = None

        self._dragEnabled = True

        self.textColor = QtGui.QColor(255, 255, 255, 180)
        self.textSelectedColor = QtGui.QColor(255, 255, 255, 255)

    def setName(self, name):
        self.setText(name)
        self._name = name

    def showArtistMenu(self):
        menu = QtWidgets.QMenu()
        list = ["aaa", "bbb"]
        for i in list:
            menu.addAction(QtWidgets.QAction(i, self._itemsWidget))
        menu.exec_(QtGui.QCursor.pos())

    def showStatusMenu(self):
        menu = QtWidgets.QMenu()
        action_action = QtWidgets.QAction(u'已完成', self._itemsWidget)
        if self._isCombo:
            menu.addAction(action_action)
            menu.exec_(QtGui.QCursor.pos())

    def setItemData(self, data):
        """
        Set the given dictionary as the data for the item.
        :type data: dict
        :rtype: None
        """
        self._itemData = data

    def itemData(self):
        """
        :return: the item data for this item.
        :rtype: dict
        """
        # if self.column() == 0:
        #     return self._itemData
        # else:
        #     return self._itemsWidget.item(self.row(), 0).itemData()
        return self._itemData

    def name(self):
        """
        :return: role_name
        """
        return str(self.itemData()[1])

    def zh_name(self):
        """
        :return: chname
        """
        return self.itemData()[2]

    def setItemsWidget(self, wgt):
        self._itemsWidget = wgt

    def itemsWidget(self):
        """
        Returns the items widget that contains the items.    得到 itemWidget

        :rtype: ItemsWidget
        """
        return self._itemsWidget

    def isFavor(self):
        """
        根据favor list判断是否为喜好
        :return: bool
        """
        # print("=========", self.name(), self.getFavorList())
        if self.name() in self._getFavorList():
            self._isFavor = True
        return self._isFavor

    def _getFavorList(self):
        """
        :return: list of favor
        """
        # print("getFavorList")
        favorList = []
        data = jsonHelper.readDictFromFile('%s/%s_fave.json' % (tempPath, self._tab))
        if data:
            for i in data:
                favorList.append(i.get("role_name"))
        return favorList

    def setFavor(self, value):
        """ 设置喜好，并记录到json """
        self._isFavor = value
        if not os.path.exists(tempPath):
            os.makedirs(tempPath)
        faveJson = r"%s/%s_fave.json" % (tempPath, self._tab)
        if not os.path.isfile(faveJson):  # 如果没有json
            f = open(faveJson, 'w')
            json.dump([self._itemData], f)
            f.close()
        else:  # 如果有就编辑
            data = jsonHelper.readDictFromFile(faveJson)
            data.append(self._itemData)
            f = open(faveJson, 'w')
            json.dump(data, f)
            f.close()

    def isTag(self):
        """ """
        # print(self.getTagList())
        # if self.name() in self.getTagList():
        #     self._isTag = True
        # return self._isTag

    def getTagList(self):
        """ 从json 获取一个有tag的资产列表 """
        # tagList = []
        # data = jsonHelper.readDictFromFile('%s/%s_tag.json' % (tempPath, self._tab))
        # if data:
        #     for i in data.keys():
        #         for n in data[i]:
        #             tagList.append(n[1])
        # return tagList

    def setTag(self, tagText):
        """ 设置标签，并记录到json """
        self._isTag = True

        tagJson = "%s/%s_tag.json" % (tempPath, self._tab)
        if not os.path.isfile(tagJson):
            r = open(tagJson, 'w')
            json.dump({tagText: [self._itemData]}, r)
            r.close()
        else:
            data = jsonHelper.readDictFromFile(tagJson)
            if data.get(tagText):
                data.get(tagText).append(self._itemData)
            else:
                data.update({tagText: [self._itemData]})
            f = open(tagJson, 'w')
            json.dump(data, f)
            f.close()

    def setDragEnabled(self, value):
        """
        Set True if the item can be dragged.
        """
        self._dragEnabled = value

    def dragEnabled(self):
        """
        Return True if the item can be dragged.
        :rtype: bool
        """
        return self._dragEnabled

    # -----------------------------------------------------------------------
    # Support for mouse and key events
    # -----------------------------------------------------------------------

    def mousePressEvent(self, event):
        """
        Reimplement in a subclass to receive mouse press events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if event.button() == QtCore.Qt.RightButton:
            print("========")

    # -----------------------------------------------------------------------
    # Support for custom painting
    # -----------------------------------------------------------------------

    def rect(self):
        """
        Return the rect for the current paint frame.

        :rtype: QtCore.QRect
        """
        return self._rect

    def setRect(self, rect):
        """
        Set the rect for the current paint frame.

        :type rect: QtCore.QRect
        :rtype: None
        """
        self._rect = rect

    def visualRect(self, option):
        """
        Return the visual rect for the item.

        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: QtCore.QRect
        """
        return QtCore.QRect(option.rect)

    def paint(self, painter, option, index):
        """
        Paint performs low-level painting for the item.

        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        :rtype: None
        """
        self.setRect(QtCore.QRect(option.rect))

        painter.save()

        try:
            self.paintBackground(painter, option, index)  # 绘制 item 的背景
            self.paintText(painter, option, index)  # 绘制item 的文字
            if self._isCombo:
                self.paintComboIcon(painter, option)  # 绘制下拉图标
        finally:
            painter.restore()

    def paintBackground(self, painter, option, index):
        """
        Draw the background for the item.
        绘制背景
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        """
        pass
        # isSelected = option.state & QtWidgets.QStyle.State_Selected
        # isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
        # painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
        #
        # visualRect = self.visualRect(option)
        #
        # color = QtGui.QColor(200, 41, 43, 0)
        # if self._name == u"未分配":
        #     color = QtGui.QColor(200, 41, 43, 250)
        #
        # painter.setBrush(QtGui.QBrush(color))
        # painter.drawRect(visualRect)

    def paintText(self, painter, option, index):
        """
        Draw the text for the item.
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        visualRect = self.visualRect(option)
        rect = QtCore.QRect(visualRect)
        align = QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

        isSelected = option.state & QtWidgets.QStyle.State_Selected
        if isSelected:
            color = QtGui.QColor(255, 255, 255, 255)
        else:
            color = QtGui.QColor(200, 200, 200, 255)

        pen = QtGui.QPen(color)
        painter.setPen(pen)

        text = self._name

        painter.drawText(rect, align, text)

    def iconRect(self, option):
        """
        Return the icon rect for the item.

        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: QtCore.QRect
        """
        padding = self.padding
        rect = self.visualRect(option)
        width = rect.width()
        height = rect.height()

        width -= padding
        height -= padding

        rect.setWidth(width)
        rect.setHeight(height)

        x = 0
        x += float(padding) / 2
        x += float((width - rect.width())) / 2

        y = float((height - rect.height())) / 2
        y += float(padding) / 2

        rect.translate(x, y)
        return rect

    def pos(self, option):
        """
        Return the type icon rect.

        :rtype: QtGui.QRect
        """
        padding = 2 * self.dpi
        r = self.iconRect(option)

        x = r.x() + padding
        y = r.y() + padding
        rect = QtCore.QRect(x, y, 13 * self.dpi, 13 * self.dpi)

        return x, y

    def typePixmap(self):
        """
        Return the type pixmap for the plugin.

        :rtype: QtWidgets.QPixmap
        """
        path = self.typeIconPath()
        pixmap = self._TYPE_PIXMAP_CACHE.get(path)

        if not pixmap and path and os.path.exists(path):
            self._TYPE_PIXMAP_CACHE[path] = QtGui.QPixmap(path)

        return self._TYPE_PIXMAP_CACHE.get(path)

    def comboIconRect(self, option):
        """
        Return the type icon rect.

        :rtype: QtGui.QRect
        """
        padding = 2 * self.dpi
        r = self.iconRect(option)

        x = r.x() + 45
        y = r.y() + 6
        rect = QtCore.QRect(x, y, 13 * self.dpi, 13 * self.dpi)

        return rect

    def paintComboIcon(self, painter, option):
        """
        Draw the item type icon at the top left.
        左上角角标
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        rect = self.comboIconRect(option)
        comboPixmap = QtGui.QPixmap("%s/icon/combo.png" % scriptsPath)
        if comboPixmap:
            painter.setOpacity(0.5)
            painter.drawPixmap(rect, comboPixmap)
            painter.setOpacity(1)


class TableModArtistItem(TableItem):
    """ 制作者 控键 """
    clickedSignal = QtCore.Signal()

    def __init__(self, name):
        super().__init__(name, isCombo=True)

    def showMenu(self):
        self.itemsWidget().show_user_menu(self)

    # def paintBackground(self, painter, option, index):
    #     isSelected = option.state & QtWidgets.QStyle.State_Selected
    #     isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
    #     painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
    #
    #     visualRect = self.visualRect(option)
    #
    #     color = QtGui.QColor(38, 41, 43, 200)
    #
    #     painter.setBrush(QtGui.QBrush(color))
    #     painter.drawRoundedRect(visualRect, 3, 3)


class TableRigArtistItem(TableItem):
    """ 制作者 控键 """
    clickedSignal = QtCore.Signal()

    def __init__(self, name):
        super().__init__(name, isCombo=True)
    #
    # def showMenu(self):
    #     self.itemsWidget().show_user_menu(self)

    # def paintBackground(self, painter, option, index):
    #     isSelected = option.state & QtWidgets.QStyle.State_Selected
    #     isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
    #     painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))
    #
    #     visualRect = self.visualRect(option)
    #
    #     # if isSelected:
    #     #     color = QtGui.QColor(250, 65, 150, 255)
    #     # else:
    #     color = QtGui.QColor(38, 41, 43, 200)
    #
    #     painter.setBrush(QtGui.QBrush(color))
    #     painter.drawRoundedRect(visualRect, 3, 3)


class TableStatusItem(TableItem):
    """ 状态控键 """

    def __init__(self, name):
        super().__init__(name, isCombo=True)

    def pos(self):
        """
        Return the type icon rect.

        :rtype: QtGui.QRect
        """
        table_pos = self.itemsWidget().viewport().mapToGlobal(self.itemsWidget().pos())
        rectX = self.itemsWidget().visualItemRect(self).left() + table_pos.x()
        rectY = self.itemsWidget().visualItemRect(self).bottom() + table_pos.y()
        return QtCore.QPoint(rectX, rectY)
    #
    # def showMenu(self):
    #     menu = QtWidgets.QMenu()
    #     action_nodo = QtWidgets.QAction(u'未开始', self._itemsWidget)
    #     action_nodo.triggered.connect(lambda: self.status_changed(action_nodo.text()))
    #     action_doing = QtWidgets.QAction(u'制作中', self._itemsWidget)
    #     action_doing.triggered.connect(lambda: self.status_changed(action_doing.text()))
    #     action_done = QtWidgets.QAction(u'已完成', self._itemsWidget)
    #     action_done.triggered.connect(lambda: self.status_changed(action_done.text()))
    #     if self._isCombo:
    #         menu.addAction(action_nodo)
    #         menu.addAction(action_doing)
    #         menu.addAction(action_done)
    #         menu.exec_(self.pos())
    #
    # def status_changed(self, text):
    #     self.itemsWidget().status_changed(text)

    def paintBackground(self, painter, option, index):
        isSelected = option.state & QtWidgets.QStyle.State_Selected
        isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        visualRect = self.visualRect(option)

        if self._name == u"未开始":
            color = QtGui.QColor(255, 80, 80, 200)
        elif self._name == u"已完成":
            color = QtGui.QColor(135, 135, 135, 200)
        elif self._name == u"制作中":
            color = QtGui.QColor(80, 200, 80, 200)
        else:
            color = QtGui.QColor(53, 56, 60, 200)

        painter.setBrush(QtGui.QBrush(color))
        painter.drawRoundedRect(visualRect, 3, 3)
