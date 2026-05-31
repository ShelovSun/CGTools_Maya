#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

import os
import requests
from widgets import imagesequence
from utils import sequenceplayer

from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('widgets', '')


class PreviewWidget(QtWidgets.QWidget):

    def __init__(self, isPlayer=True):
        super(PreviewWidget, self).__init__()

        self.isPlayer = isPlayer

        vLayout = QtWidgets.QVBoxLayout(self)
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)
        font = QtGui.QFont(u"Microsoft YaHei UI", 10)
        self.play_tBtn = QtWidgets.QToolButton(self)
        self.play_tBtn.setAutoRaise(True)
        self.firstFrame_tBtn = QtWidgets.QToolButton(self)
        self.firstFrame_tBtn.setAutoRaise(True)
        self.prevFrame_tBtn = QtWidgets.QToolButton(self)
        self.prevFrame_tBtn.setAutoRaise(True)
        self.nextFrame_tBtn = QtWidgets.QToolButton(self)
        self.nextFrame_tBtn.setAutoRaise(True)
        self.lastFrame_tBtn = QtWidgets.QToolButton(self)
        self.lastFrame_tBtn.setAutoRaise(True)
        self.frames_lineEdit = QtWidgets.QLineEdit(self)
        self.label = PreviewLabel(self.frames_lineEdit)
        self.title_label = QtWidgets.QLabel(self)
        self.title_label.setStyleSheet("color: rgb(150, 150, 150);background-color: rgb(29, 29, 29);")
        self.title_label.setFixedHeight(45)
        self.title_label.setFont(font)
        hLayout = QtWidgets.QHBoxLayout(self)
        hLayout.setContentsMargins(0, 0, 3, 0)
        hLayout.setSpacing(3)
        hLayout.addWidget(self.play_tBtn)
        hLayout.addWidget(self.firstFrame_tBtn)
        hLayout.addWidget(self.prevFrame_tBtn)
        hLayout.addWidget(self.nextFrame_tBtn)
        hLayout.addWidget(self.lastFrame_tBtn)
        hLayout.addWidget(self.frames_lineEdit)
        vLayout.addWidget(self.label)
        vLayout.addWidget(self.title_label)
        if self.isPlayer:
            vLayout.addLayout(hLayout)
            self.playerSet()

    def resizeEvent(self, e):
        if not self.isPlayer:
            self.setMaximumHeight(self.width() + 45)
        else:
            self.setMaximumHeight(self.width() + 85)

    def setTitle(self, name, zh_name):
        if zh_name is not None:
            self.title_label.setText(u"Name： " + name + u"\n中文名： " + zh_name)
        else:
            self.title_label.setText(u"Name： " + name + u"\n中文名： ")

    def playerSet(self):
        """播放器设置"""
        player = sequenceplayer.Player()
        player.setPlayButtonState(self.play_tBtn)
        '''播放'''
        self.play_tBtn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaPause))
        self.play_tBtn.clicked.connect(lambda: player.play(100, self.play_tBtn))
        '''起始帧'''
        self.firstFrame_tBtn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipBackward))
        self.firstFrame_tBtn.clicked.connect(player.firstFrame)
        '''上一帧'''
        self.prevFrame_tBtn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekBackward))
        self.prevFrame_tBtn.clicked.connect(player.prevFrame)
        '''下一帧'''
        self.nextFrame_tBtn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSeekForward))
        self.nextFrame_tBtn.clicked.connect(player.nextFrame)
        '''结束帧'''
        self.lastFrame_tBtn.setIcon(QtWidgets.QApplication.style().standardIcon(QtWidgets.QStyle.SP_MediaSkipForward))
        self.lastFrame_tBtn.clicked.connect(player.lastFrame)

    def playerEnabled(self, value):
        self.play_tBtn.setEnabled(value)
        self.firstFrame_tBtn.setEnabled(value)
        self.prevFrame_tBtn.setEnabled(value)
        self.nextFrame_tBtn.setEnabled(value)
        self.lastFrame_tBtn.setEnabled(value)

    def clear(self):
        self.label.clear()
        self.title_label.clear()

    def setPreviewPixmap(self, path, _type=None):
        self.label.setPreviewPixmap(path, _type=None)


class PreviewLabel(QtWidgets.QLabel):
    """ 预览窗口 """

    # _enterSignal = QtCore.Signal()
    # _leaveSignal = QtCore.Signal()

    def __init__(self, framsWgt=None):
        super(PreviewLabel, self).__init__()
        self.iconPath = ""

        self.__isAnim = False
        self._imageSequence = None
        self.framsWgt = framsWgt
        self.pixmap = None
        self.typePixmap = None
        self._isMoveing = False
        # self.setScaledContents(True)# 图片自适应label
        self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignHCenter)
        # self.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        self.setStyleSheet("background-color: qradialgradient(spread:pad, cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, "
                           "stop:0 rgba(35, 36, 39, 100),  stop:1 rgba(35, 36, 39, 255));")

    def sizeHint(self):
        labelSize = QtCore.QSize(10, 10)
        return labelSize

    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self.mouse_start_pos = e.pos()
            self._isMoveing = True

    def mouseReleaseEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            self._isMoveing = False

    def mouseMoveEvent(self, e):
        print("mouse move")
        if self._isMoveing:
            point = e.pos() - self.mouse_start_pos
            print(point)
            self.setGeometry(QtCore.QRect(point.x(), point.y(), self.width(), self.height()))
            # transform = QtGui.QTransform()
            # transform.translate(point.x(), point.y())
            # self.pixmap = self.pixmap.transformed(transform)
            # self.setPixmap(self.pixmap)

    def mouseDoubleClickEvent(self, e):
        t = QtGui.QTransform()
        t.translate(5.1, 5.1)
        self.pixmap = self.pixmap.transformed(t)
        self.setPixmap(self.pixmap)

    def wheelEvent(self, e):
        print("wheel")
        super(PreviewLabel, self).wheelEvent(e)
        if self.iconPath == "":
            return
        else:
            angle = e.angleDelta() / 8
            angleY = angle.y()
            transform = QtGui.QTransform()
            if angleY > 0:
                # transform.scale(1.1, 1.1)
                new_w = self.width() + 15
                new_h = self.height() + 15
                new_x = e.x() - (self.width() * (e.x() - self.x())) / (self.width())
                new_y = e.y() - (self.height() * (e.y() - self.y())) / (self.height())
            else:
                # transform.scale(0.9, 0.9)
                new_w = self.width() - 15
                new_h = self.height() - 15
                new_x = e.x() - (self.width() * (e.x() - self.x())) / (self.width())
                new_y = e.y() - (self.height() * (e.y() - self.y())) / (self.height())
            self.setGeometry(QtCore.QRect(new_x, new_y, new_w, new_h))
            # self.pixmap = self.pixmap.transformed(transform)
            # self.setPixmap(self.pixmap)
            # self.adjustSize()
            # self.update()

    def resizeEvent(self, e):
        """"""
        # print("resize event")
        self.setMaximumHeight(self.width())
        self.setMinimumHeight(self.width())
    #     if self.pixmap:
    #         print(self.pixmap)
    #         self.pixmap = self.pixmap.scaled(self.rect().width(),
    #                                self.rect().height(),
    #                                QtCore.Qt.KeepAspectRatio,
    #                                QtCore.Qt.SmoothTransformation)
    #         self.setPixmap(self.pixmap)

    def clear(self):
        super(PreviewLabel, self).clear()
        self.iconPath = ""
        self.pixmap = None
        self.__isAnim = False
        self._imageSequence = None

    def setPreviewPixmap(self, path, _type=None):
        """
        new setpixmap, add typePixmap and paint
        :param path:
        :param _type:
        :return:
        """
        self.iconPath = path

        self.pixmap = QtGui.QPixmap()
        if path.startswith("http://"):  # 如果是url
            res = requests.get(path)
            self.pixmap.loadFromData(res.content)
        else:
            self.pixmap = QtGui.QPixmap(path)

        self.pixmap = self.pixmap.scaled(self.rect().width(),
                                         self.rect().height(),
                                         QtCore.Qt.KeepAspectRatio,
                                         QtCore.Qt.SmoothTransformation)
        # self.pixmap.setDevicePixelRatio(0.5) # 1:1比例设置

        if _type is not None and os.path.isfile("%s/icon/%s.png" % (scriptsPath, _type)):
            self.typePixmap = QtGui.QPixmap("%s/icon/%s.png" % (scriptsPath, _type))

        self.paintTypeIcon()
        self.setPixmap(self.pixmap)

    def isAnim(self):
        return self.__isAnim

    def setAnim(self, path, _type=None):
        self.setPreviewPixmap(path, _type)
        self.__isAnim = True

    def enterEvent(self, e):
        # print("enter")
        if self.__isAnim:
            seq_path = self.iconPath.replace('thumbnail.jpg', 'sequence')
            self._play(seq_path)

    def leaveEvent(self, e):
        # print("leave")
        if self._imageSequence is not None:
            self._imageSequence.stop()

    def _play(self, path):
        """Start playing the movie."""
        movie = None
        if os.path.isfile(path) and path.lower().endswith(".gif"):
            movie = QtGui.QMovie(path)
            self.setMovie(movie)
        elif os.path.isdir(path):
            movie = imagesequence.ImageSequence(path)
            movie.frameChanged.connect(self.__frameChanged)
            self._imageSequence = movie
        if movie:
            movie.start()

    def __frameChanged(self, frame=None):
        """ Triggered when the movie object updates to the given frame. """
        isAppRunning = bool(QtWidgets.QApplication.instance())
        if not isAppRunning:
            return
        if self._imageSequence is not None:
            self.pixmap = self._imageSequence.currentPixmap()
            self.pixmap = self.pixmap.scaled(self.rect().width(),
                                             self.rect().height(),
                                             QtCore.Qt.KeepAspectRatio,
                                             QtCore.Qt.SmoothTransformation)
            fn = self._imageSequence.currentFrameNumber()
            fc = self._imageSequence.frameCount()
            try:
                self.paintTypeIcon()
                self.paintPlayhead()
                self.setPixmap(self.pixmap)
                self.framsWgt.setText(str(fn) + " / " + str(fc))
            except Exception as e:
                print(e)

    def paintTypeIcon(self):
        painter = QtGui.QPainter(self.pixmap)
        typePixmap = self.typePixmap
        if typePixmap:
            painter.drawPixmap(3, 3, typePixmap)
            painter.setPen(QtCore.Qt.NoPen)

    def paintPlayhead(self):
        """
        Paint the playhead if the item has an image sequence.
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        painter = QtGui.QPainter(self.pixmap)

        if self._imageSequence and self.underMouse():  # 如果有图片序列 和 鼠标下

            count = self._imageSequence.frameCount()
            current = self._imageSequence.currentFrameNumber()

            if count > 0:
                percent = float((count + current) + 1) / count - 1
            else:
                percent = 0

            r = self.rect()
            color = QtGui.QColor(255, 255, 255, 220)

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(color))

            if percent <= 0:
                width = 0
            elif percent >= 1:
                width = r.width()
            else:
                width = (percent * r.width()) - 1

            height = 3
            if r.height() > r.width():
                y = r.y() + r.height() - (height - 1) - (r.height() - r.width())
            else:
                y = r.y() + r.height() - (height - 1)

            painter.drawRect(r.x(), y, width, height)
