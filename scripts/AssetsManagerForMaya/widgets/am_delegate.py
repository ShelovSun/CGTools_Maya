#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

# import os
# import math
# import json
# import requests
# import imagesequence
# import maya.cmds as cmds
#
# from utils import jsonHelper, publish
# from my_vendor import six
# from PySide2 import QtGui
# from PySide2 import QtCore
from PySide2 import QtWidgets


class MainDelegate(QtWidgets.QStyledItemDelegate):
    """ 主窗委托 """

    def __init__(self):
        QtWidgets.QStyledItemDelegate.__init__(self)
        self._itemsWidget = None

    def paint(self, painter, option, index):
        # print("items paint")
        painter.save()  # ========不污染其他操作
        item = self.itemsWidget().itemFromIndex(index)
        if item:
            item.paint(painter, option, index)
        painter.restore()  # ======不污染其他操作

    def sizeHint(self, option, index):
        """如果设置了paint就需要sizeHint（好像否则有时候paint会乱掉）"""
        item = self.itemsWidget().itemFromIndex(index)
        return item.sizeHint()

    def itemsWidget(self):
        return self._itemsWidget

    def setItemsWidget(self, itemsWidget):
        self._itemsWidget = itemsWidget
