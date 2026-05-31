#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide2 import QtGui


class Pixmap(QtGui.QPixmap):
    """ new pixmap can set color"""

    def __init__(self, *args):
        QtGui.QPixmap.__init__(self, *args)
        self._color = None

    def setColor(self, color):
        """
        给pixmap着色
        :type color: QtGui.QColor
        :rtype: None
        """
        if not self.isNull():
            painter = QtGui.QPainter(self)
            painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
            painter.setBrush(color)  # 定义用于填充形状的颜色或图案
            painter.setPen(color)  # 定义用于绘制线条或边界的颜色或点画
            painter.drawRect(self.rect())
            painter.end()


