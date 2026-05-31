#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 自定义一些QtWidgets

import os
import math
import json
import requests
from widgets import imagesequence

from utils import jsonHelper, publish
from my_vendor import six
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('widgets', '')
tempPath = "{}/AssetsManagerTemp".format(os.environ.get('APPDATA'))   # cmds.internalVar(userTmpDir=True)


def projectSetting():
    data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % scriptsPath)
    return data


class MyThread(QtCore.QThread):
    signal = QtCore.Signal()

    def __init__(self):
        super(MyThread, self).__init__()

    def run(self):
        self.signal.emit()


class GlobalSignals(QtCore.QObject):
    """  """
    sliderChanged = QtCore.Signal(float)


class WorkerSignals(QtCore.QObject):
    """  """
    triggered = QtCore.Signal(object)


class ImageWorker(QtCore.QRunnable):
    """A convenience class for loading an image in a thread."""

    def __init__(self, *args):
        QtCore.QRunnable.__init__(self, *args)

        self._path = None
        self._size = 120
        self.signals = WorkerSignals()

    def setPath(self, path):
        """
        Set the image path to be processed.
        :type path: str
        """
        self._path = path

    def setSize(self, size):
        """
        Set the image size to be processed.
        :type size: int
        """
        self._size = size

    def run(self):
        """The starting point for the thread."""
        try:
            if self._path:
                # image = QtGui.QImage(six.text_type(self._path))
                reader = QtGui.QImageReader(self._path)
                reader.setAutoTransform(True)
                reader.setScaledSize(QtCore.QSize(self._size, self._size))
                image = reader.read()
                self.signals.triggered.emit(image)
        except Exception as error:
            print("Cannot load thumbnail image:%s" % error)


class ListItem(QtWidgets.QListWidgetItem):
    """The Item is used to hold rows of information for an item view."""

    ICON_PATH = None
    TYPE_ICON_PATH = None

    ThreadPool = QtCore.QThreadPool()
    THUMBNAIL_PATH = "%s/icon/blank_ch.png" % scriptsPath

    MAX_ICON_SIZE = 256

    DEFAULT_FONT_SIZE = 12
    DEFAULT_PLAYHEAD_COLOR = QtGui.QColor(255, 255, 255, 220)
    DEFAULT_COLOR = QtGui.QColor(40, 41, 43, 255)
    DEFAULT_TEXT_BG_COLOR = QtGui.QColor(30, 30, 30, 255)
    DEFAULT_HOVER_COLOR = QtGui.QColor(50, 50, 50, 255)
    DEFAULT_SELECTED_COLOR = QtGui.QColor(82, 133, 166, 255)
    DEFAULT_BORDER_SIZE = 1.5

    THUMBNAIL_COLUMN = 0
    ENABLE_THUMBNAIL_THREAD = True
    PAINT_SLIDER = False

    _TYPE_PIXMAP_CACHE = {}

    _globalSignals = GlobalSignals()
    sliderChanged = _globalSignals.sliderChanged

    def __init__(self):
        QtWidgets.QListWidgetItem.__init__(self)

        self._url = None
        self._path = None
        self._size = 120
        self._rect = None
        self._textColumnOrder = []

        self._data = {}
        self._itemData = {}
        self._isLoaded = False

        self._icon = {}
        self._fonts = {}
        self._thread = None
        self._pixmap = {}
        self._pixmapRect = None
        self._pixmapScaled = None

        self._iconPath = None
        self._typePixmap = None

        self._thumbnailIcon = None

        self._isFavor = False
        self._isTag = False
        self._underMouse = False
        self._searchText = None
        self._infoWidget = None

        self._groupItem = None
        self._groupColumn = 0

        self._mimeText = None
        self._itemsWidget = None
        self._stretchToWidget = None

        self._dragEnabled = True

        self.textColor = QtGui.QColor(255, 255, 255, 180)
        self.textSelectedColor = QtGui.QColor(255, 255, 255, 255)

        self._imageSequence = None
        self._imageSequencePath = ""

        self._sliderDown = False
        self._sliderValue = 0.0
        self._sliderPreviousValue = 0.0
        self._sliderPosition = None
        self._sliderEnabled = False

        self._worker = ImageWorker()
        self._worker.setAutoDelete(False)
        self._worker.signals.triggered.connect(self._thumbnailFromImage)
        self._workerStarted = False

    def __eq__(self, other):
        return id(other) == id(self)

    def __ne__(self, other):
        return id(other) != id(self)

    def __hash__(self):
        return hash(id(self))

    def __del__(self):
        """
        Make sure the sequence is stopped when deleted.

        :rtype: None
        """
        self.stop()

    def mimeText(self):
        """
        Return the mime text for drag and drop.
        :rtype: str
        """
        return self._mimeText or self.text(0)

    def setMimeText(self, text):
        """
        Set the mime text for drag and drop.
        :type text: str
        :rtype: None
        """
        self._mimeText = text

    def setLoaded(self):
        """
        是否已加载
        """
        self._isLoaded = True

    def isLoaded(self):
        return self._isLoaded

    # def isFavor(self):
    #     """
    #     根据favor list判断是否为喜好
    #     :return: bool
    #     """
    #     # print("=========", self.name(), self.getFavorList())
    #     if self.name() in self._getFavorList():
    #         self._isFavor = True
    #     return self._isFavor
    #
    # def _getFavorList(self):
    #     """
    #     :return: list of favor
    #     """
    #     # print("getFavorList")
    #     favorList = []
    #     data = jsonHelper.readDictFromFile('%s/%s_fave.json' % (tempPath, self._tab))
    #     if data:
    #         for i in data:
    #             favorList.append(i.get("role_name"))
    #     return favorList
    #
    # def setFavor(self, value):
    #     """ 设置喜好，并记录到json """
    #     self._isFavor = value
    #     if not os.path.exists(tempPath):
    #         os.makedirs(tempPath)
    #     faveJson = r"%s/%s_fave.json" % (tempPath, self._tab)
    #     if not os.path.isfile(faveJson):  # 如果没有json
    #         f = open(faveJson, 'w')
    #         json.dump([self._itemData], f)
    #         f.close()
    #     else:  # 如果有就编辑
    #         data = jsonHelper.readDictFromFile(faveJson)
    #         data.append(self._itemData)
    #         f = open(faveJson, 'w')
    #         json.dump(data, f)
    #         f.close()
    #
    # def isTag(self):
    #     # print(self.getTagList())
    #     if self.name() in self.getTagList():
    #         self._isTag = True
    #     return self._isTag
    #
    # def getTagList(self):
    #     """ 从json 获取一个有tag的资产列表 """
    #     tagList = []
    #     data = jsonHelper.readDictFromFile('%s/%s_tag.json' % (tempPath, self._tab))
    #     if data:
    #         for i in data.keys():
    #             for n in data[i]:
    #                 tagList.append(n.get("role_name"))
    #     return tagList
    #
    # def setTag(self, tagText):
    #     """ 设置标签，并记录到json """
    #     self._isTag = True
    #
    #     tagJson = "%s/%s_tag.json" % (tempPath, self._tab)
    #     if not os.path.isfile(tagJson):
    #         r = open(tagJson, 'w')
    #         json.dump({tagText: [self._itemData]}, r)
    #         r.close()
    #     else:
    #         data = jsonHelper.readDictFromFile(tagJson)
    #         if data.get(tagText):
    #             data.get(tagText).append(self._itemData)
    #         else:
    #             data.update({tagText: [self._itemData]})
    #         f = open(tagJson, 'w')
    #         json.dump(data, f)
    #         f.close()

        # for index, row in subdf.iterrows():
        #     dictText[tagText].append({'LON': row['LON'], 'LAT': row['LAT']})
        #
        # tagJson.write(dictText)
        # tagJson.close()

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

    # def setIcon(self, iconpath):
    #     """
    #     Set the icon to be displayed .
    #     设置icon
    #     """
    #     # Safe guard for when the class is being used without the gui.
    #     isAppRunning = bool(QtWidgets.QApplication.instance())
    #     if not isAppRunning:
    #         return
    #
    #     if isinstance(iconpath, six.string_types):
    #         if not os.path.exists(iconpath):
    #             icon = QtGui.QIcon("%s/icon/Default.png" % scriptsPath)
    #         else:
    #             icon = QtGui.QIcon(iconpath)
    #     else:
    #         icon = iconpath
    #
    #     QtWidgets.QListWidgetItem.setIcon(self, icon)
    #
    #     self.updateIcon()  # 清除 pixmap cache

    def setItemData(self, data):
        """
        Set the given dictionary as the data for the item.
        :type data: dict
        :rtype: None
        """
        self._itemData = data
        self.setImageSequencePath()

    def itemData(self):
        """
        :return: the item data for this item.
        :rtype: dict
        """
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

    def update(self):
        """
        Refresh the visual state of the icon.
        :rtype: None
        """
        self.updateIcon()
        self.updateFrame()

    def updateIcon(self):
        """
        Clear the pixmap cache for the item.
        清除 pixmap cache
        :rtype: None
        """
        self.clearCache()

    def clearCache(self):
        """
        清理 thumbnail cache.
        """
        self._pixmap = {}
        self._pixmapRect = None
        self._pixmapScaled = None
        self._thumbnailIcon = None

    def dpi(self):
        """
        Used for high resolution devices.

        :rtype: int
        """
        return 1

    def selectionChanged(self):
        """
        Triggered when an item has been either selected or deselected.

        :rtype: None
        """
        self.resetSlider()

    def setItemsWidget(self, wgt):
        self._itemsWidget = wgt

    def itemsWidget(self):
        """
        Returns the items widget that contains the items.    得到 itemWidget

        :rtype: ItemsWidget
        """
        return self._itemsWidget

    def searchText(self):
        """
        Return the search string used for finding the item.

        :rtype: str
        """
        if not self._searchText:
            self._searchText = six.text_type(self._data)

        return self._searchText

    def setStretchToWidget(self, widget):
        """
        Set the width of the item to the width of the given widget.

        :type widget: QtWidgets.QWidget
        :rtype: None
        """
        self._stretchToWidget = widget

    def stretchToWidget(self):
        """
        Return the sretchToWidget.

        :rtype: QtWidgets.QWidget
        """
        return self._stretchToWidget

    def setSize(self, size):
        """
        Set the size for the item.
        :type size: Int
        :rtype: None
        """
        self._size = size

    def sizeHint(self):
        """
        Return the current size of the item.
        :rtype: QtCore.QSize
        """
        size = self._itemsWidget.itemSize()
        iconSize = QtCore.QSize(size, size + 40)
        return iconSize

    def thumbnailPath(self):
        """
        Return the thumbnail path on disk. 返回微缩图路径
        :rtype: None or str
        """
        return str(self.itemData()[7])

    def _thumbnailFromImage(self, image):
        """
        Called after the given image object has finished loading.
        当 image 结束 loading 后调用：清理 -> 设置新的 icon
        :type image: QtGui.QImage
        :rtype: None
        """
        self.clearCache()  # 清理pixmap

        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        icon = QtGui.QIcon(pixmap)

        self._thumbnailIcon = icon
        if self.itemsWidget():
            self.itemsWidget().update()

    def defaultThumbnailPath(self):
        """
        Get the default thumbnail path.
        :rtype: str
        """
        return self.THUMBNAIL_PATH

    def defaultThumbnailIcon(self):
        """
        Get the default thumbnail icon.
        :rtype: QtGui.QIcon
        """
        return QtGui.QIcon(self.defaultThumbnailPath())

    def thumbnailIcon(self):
        """
        Return the thumbnail icon.
        返回 self._thumbnailIcon
        :rtype: QtGui.QIcon
        """
        thumbnailPath = self.thumbnailPath()
        # print("thumbnailPath:", thumbnailPath)
        if not self._thumbnailIcon:  # 如果没有 self._thumbnailIcon
            if self.ENABLE_THUMBNAIL_THREAD and not self._workerStarted:  #
                self._workerStarted = True
                self._worker.setPath(thumbnailPath)
                self._worker.setSize(self._size)
                self.ThreadPool.start(self._worker)  # 开始进程池 ImageWorker
                self._thumbnailIcon = self.defaultThumbnailIcon()
            else:
                self._thumbnailIcon = QtGui.QIcon(thumbnailPath)

        return self._thumbnailIcon

    def icon(self):
        """
        Overriding the icon method to add support for the thumbnail icon.
        重写 icon 添加 thumbnail icon 支持
        :type column: int
        :rtype: QtGui.QIcon
        """
        icon = QtWidgets.QListWidgetItem.icon(self)

        if not icon == self.THUMBNAIL_COLUMN:
            icon = self.thumbnailIcon()

        return icon

    def pixmap(self):
        """
        Return the pixmap for the given column.
        :type column: int
        :rtype: QtWidgets.QPixmap
        """
        if not self._pixmap:
            icon = self.icon()
            if icon:
                size = QtCore.QSize(self.MAX_ICON_SIZE, self.MAX_ICON_SIZE)
                iconSize = icon.actualSize(size)
                self._pixmap = icon.pixmap(iconSize)
        return self._pixmap

    def padding(self):
        """
        Return the padding/border size for the item.
        :rtype: int
        """
        return 2

    def textHeight(self):
        """
        Return the height of the text for the item.
        :rtype: int
        """
        return self.itemsWidget().itemTextHeight()

    def textAlignment(self):
        """
        Return the text alignment for the label in the given column.
        :type column: int
        :rtype: QtCore.Qt.AlignmentFlag
        """
        return QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom

    # -----------------------------------------------------------------------
    # Support for mouse and key events
    # -----------------------------------------------------------------------

    def underMouse(self):
        """Return True if the item is under the mouse cursor."""
        return self._underMouse

    def contextMenu(self, menu):
        """
        Return the context menu for the item.

        Reimplement in a subclass to return a custom context menu for the item.

        :rtype: QtWidgets.QMenu
        """
        pass

    def dropEvent(self, event):
        """
        Reimplement in a subclass to receive drop events for the item.

        :type event: QtWidgets.QDropEvent
        :rtype: None
        """

    def mouseLeaveEvent(self, event):
        """
        Reimplement in a subclass to receive mouse leave events for the item.
        鼠标出
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        # print("mouse Leave Event")
        self._underMouse = False  # 鼠标下为假
        self.stop()

    def mouseEnterEvent(self, event):
        """
        Reimplement in a subclass to receive mouse enter events for the item.
        重执行 鼠标进
        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        # print("mouse Enter Event")
        self._underMouse = True  # 鼠标下为真
        self.play()

    def mouseMoveEvent(self, event):
        """
        Reimplement in a subclass to receive mouse move events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        self.sliderEvent(event)
        self.imageSequenceEvent(event)

    def mousePressEvent(self, event):
        """
        Reimplement in a subclass to receive mouse press events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if event.button() == QtCore.Qt.MidButton:
            if self.isSliderEnabled():
                self.setSliderDown(True)
                self._sliderPosition = event.pos()

    def mouseReleaseEvent(self, event):
        """
        Reimplement in a subclass to receive mouse release events for the item.

        :type event: QtWidgets.QMouseEvent
        :rtype: None
        """
        if self.isSliderDown():
            self._sliderPosition = None
            self._sliderPreviousValue = self.sliderValue()

    def keyPressEvent(self, event):
        """
        Reimplement in a subclass to receive key press events for the item.

        :type event: QtWidgets.QKeyEvent
        :rtype: None
        """
        pass

    def keyReleaseEvent(self, event):
        """
        Reimplement in a subclass to receive key release events for the item.

        :type event: QtWidgets.QKeyEvent
        :rtype: None
        """
        pass

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

    def iconPercent(self):
        itemSize = float('%.2f' % (self._itemsWidget.itemSize()))
        return itemSize / (itemSize + 40.00)

    def backgroundColor(self, visualRect):
        linearGradient = QtGui.QLinearGradient(QtCore.QPointF(0, visualRect.y()),
                                               QtCore.QPointF(0, visualRect.y() + visualRect.height()))
        # linearGradient.setColorAt(0, QtGui.QColor(35, 35, 35, 255))
        linearGradient.setColorAt(self.iconPercent(), QtGui.QColor(60, 62, 64, 255))
        linearGradient.setColorAt(self.iconPercent() + 0.01, self.DEFAULT_TEXT_BG_COLOR)
        return linearGradient

    def backgroundHoverColor(self, visualRect):
        linearGradient = QtGui.QLinearGradient(QtCore.QPointF(0, visualRect.y()),
                                               QtCore.QPointF(0, visualRect.y() + visualRect.height()))
        linearGradient.setColorAt(self.iconPercent(), QtGui.QColor(62, 64, 66, 255))
        linearGradient.setColorAt(self.iconPercent() + 0.01, self.DEFAULT_HOVER_COLOR)
        return linearGradient

    def backgroundSelectedColor(self, visualRect):
        linearGradient = QtGui.QLinearGradient(QtCore.QPointF(0, visualRect.y()),
                                               QtCore.QPointF(0, visualRect.y() + visualRect.height()))
        linearGradient.setColorAt(self.iconPercent(), QtGui.QColor(65, 69, 75, 255))
        linearGradient.setColorAt(self.iconPercent() + 0.01, self.DEFAULT_SELECTED_COLOR)
        return linearGradient

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
            # self.drawIconBorder(painter, option)  # 绘制 item 的边框
            self.paintBackground(painter, option, index)  # 绘制 item 的背景
            self.paintIcon(painter, option, index)  # 绘制 item 的 icon

            # if self.imageSequence() and self.sliderValue() != 0:
            #     self.paintSlider(painter, option, index)

            self.paintText(painter, option, index)  # 绘制item 的文字

            self.paintTypeIcon(painter, option)  # 绘制左上角角标

            if self.name().endswith('_GRP'):
                self.paintNum(painter, option)

            if self.imageSequence():
                self.paintPlayhead(painter, option)  # 绘制item 的进度条

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
        isSelected = option.state & QtWidgets.QStyle.State_Selected
        isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        visualRect = self.visualRect(option)
        # visualRect.setX(visualRect.x() - 2)
        # visualRect.setY(visualRect.y() - 2)
        # visualRect.setWidth(visualRect.width() + 2)
        # visualRect.setHeight(visualRect.height() + 2)

        if isSelected:
            color = self.backgroundSelectedColor(visualRect)
        elif isMouseOver:
            color = self.backgroundHoverColor(visualRect)
        else:
            color = self.backgroundColor(visualRect)

        # if not self.itemsWidget().isIconView():
        #     spacing = 1 * self.dpi()
        #     height = visualRect.height() - spacing
        #     visualRect.setHeight(height)
        painter.setBrush(QtGui.QBrush(color))
        painter.drawRect(visualRect)
        # painter.drawRoundedRect(visualRect, 5, 5)

    def paintSlider(self, painter, option, index):
        """
        Draw the virtual slider for the item.
        绘制进度条
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :type index: QtCore.QModelIndex
        """
        if not self.PAINT_SLIDER:
            return

        # if self.itemsWidget().isList():
        #     return

        # Draw slider background
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        rect = self.visualRect(option)

        color = self.itemsWidget().backgroundColor().toRgb()
        color.setAlpha(75)
        painter.setBrush(QtGui.QBrush(color))

        height = rect.height()

        ratio = self.sliderValue()

        if ratio < 0:
            width = 0
        elif ratio > 100:
            width = rect.width()
        else:
            width = rect.width() * (float(ratio) / 100)

        rect.setWidth(width)
        rect.setHeight(height)

        painter.drawRect(rect)

        # Draw slider value
        rect = self.visualRect(option)
        rect.setY(rect.y() + (4 * self.dpi()))

        color = self.itemsWidget().textColor().toRgb()
        color.setAlpha(220)
        pen = QtGui.QPen(color)
        align = QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter

        painter.setPen(pen)
        painter.drawText(rect, align, str(self.sliderValue()) + "%")

    def iconRect(self, option):
        """
        Return the icon rect for the item.

        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: QtCore.QRect
        """
        padding = self.padding()
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

    def scalePixmap(self, pixmap, rect):
        """
        Scale the given pixmap to the give rect size.

        This method will cache the scaled pixmap if called with the same size.

        :type pixmap: QtGui.QPixmap
        :type rect: QtCore.QRect
        :rtype: QtGui.QPixmap
        """
        rectChanged = True

        if self._pixmapRect:
            widthChanged = self._pixmapRect.width() != rect.width()
            heightChanged = self._pixmapRect.height() != rect.height()

            rectChanged = widthChanged or heightChanged

        if not self._pixmapScaled or rectChanged:
            self._pixmapScaled = pixmap.scaled(
                rect.width(),
                rect.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation,
            )

            self._pixmapRect = rect

        return self._pixmapScaled

    def paintIcon(self, painter, option, index, align=None):
        """
        Draw the icon for the item.
        绘制 item 的 icon
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        # icon = self.itemData()[7]
        # pixmap = QtGui.QPixmap()
        # if not icon.startswith("http://"):
        #     pixmap = QtGui.QPixmap(icon)
        # else:
        #     res = requests.get(icon)
        #     pixmap.loadFromData(res.content)
        #
        # if self.imageSequence() and self.underMouse():
        #     pixmap = self.imageSequence().currentPixmap()
        pixmap = self.pixmap()

        if not pixmap:
            return

        rect = self.iconRect(option)  # Return the icon rect for the item.
        pixmap = self.scalePixmap(pixmap, rect)

        pixmapRect = QtCore.QRect(rect)
        pixmapRect.setWidth(pixmap.width())
        pixmapRect.setHeight(pixmap.height())

        x, y = 0, 0
        pixmapRect.translate(x, y)
        painter.drawPixmap(pixmapRect, pixmap)

    def drawIconBorder(self, painter, option):
        """
        Draw a border around the icon.

        :param option:
        :type painter: QtWidgets.QPainter
        :type pixmapRect: QtWidgets.QRect
        :rtype: None
        """
        pixmapRect = QtCore.QRect(option.rect)
        pixmapRect.setX(pixmapRect.x() - self.DEFAULT_BORDER_SIZE)
        pixmapRect.setY(pixmapRect.y() - self.DEFAULT_BORDER_SIZE)
        pixmapRect.setWidth(pixmapRect.width() + self.DEFAULT_BORDER_SIZE)
        pixmapRect.setHeight(pixmapRect.height() + self.DEFAULT_BORDER_SIZE)

        isSelected = option.state & QtWidgets.QStyle.State_Selected
        isMouseOver = option.state & QtWidgets.QStyle.State_MouseOver
        painter.setPen(QtGui.QPen(QtCore.Qt.NoPen))

        if isSelected:
            color = self.DEFAULT_SELECTED_COLOR
        elif isMouseOver:
            color = self.DEFAULT_HOVER_COLOR
        else:
            color = self.DEFAULT_COLOR

        painter.setBrush(QtGui.QBrush(color))
        painter.drawRect(pixmapRect)

    def fontSize(self):
        """
        Return the font size for the item.

        :rtype: int
        """
        return self.DEFAULT_FONT_SIZE

    def font(self, column):
        """
        Return the font for the given column.

        :type column: int
        :rtype: QtWidgets.QFont
        """
        default = QtWidgets.QTreeWidgetItem.font(self, column)

        font = self._fonts.get(column, default)

        font.setPixelSize(self.fontSize() * self.dpi())
        return font

    def setFont(self, column, font):
        """
        Set the font for the given column.

        :type column: int
        :type font: QtWidgets.QFont
        :rtype: Noen
        """
        self._fonts[column] = font

    def paintText(self, painter, option, index):
        """
        Draw the text for the item.
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        visualRect = self.visualRect(option)
        rect = QtCore.QRect(visualRect)
        align = self.textAlignment()

        isSelected = option.state & QtWidgets.QStyle.State_Selected
        if isSelected:
            color = self.textSelectedColor
        else:
            color = self.textColor

        pen = QtGui.QPen(color)
        painter.setPen(pen)
        if self.zh_name():
            zh_name = self.zh_name()
        else:
            zh_name = ""
        text = self.name() + "\n" + zh_name
        painter.drawText(rect, align, text)

    def countGRPNum(self):
        path = self._itemData[7].split("Icon")[0]
        directory = QtCore.QDir("%sMod" % path)
        int_list = directory.entryList(['*.ma'], QtCore.QDir.NoDotAndDotDot | QtCore.QDir.AllEntries,
                                       QtCore.QDir.DirsFirst | QtCore.QDir.IgnoreCase)
        return str(len(int_list) - 1)

    def paintNum(self, painter, option):
        """
        Draw the text for the item.
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        rect = QtCore.QRect(option.rect)
        pen = QtGui.QPen(self.textColor)
        painter.setPen(pen)
        text = self.countGRPNum()
        itemSize = self._itemsWidget.itemSize()
        painter.drawText(rect.x() + itemSize - 15, rect.y() + itemSize - 5, text)

    def textWidth(self, column):
        text = self.text(column)

        font = self.font(column)
        metrics = QtGui.QFontMetricsF(font)
        textWidth = metrics.width(text)
        return textWidth

    # ------------------------------------------------------------------------
    # Support for middle mouse slider
    # ------------------------------------------------------------------------

    def setSliderEnabled(self, enabled):
        """
        Set if middle mouse slider is enabled.

        :type enabled: bool
        """
        self._sliderEnabled = enabled

    def isSliderEnabled(self):
        """
        Return true if middle mouse slider is enabled.

        :rtype: bool
        """
        return self._sliderEnabled

    def sliderEvent(self, event):
        """
        Called when the mouse moves while the middle mouse button is held down.

        :param event: QtGui.QMouseEvent
        """
        if self.isSliderDown():
            value = (event.pos().x() - self.sliderPosition().x()) / 1.5
            value = math.ceil(value) + self.sliderPreviousValue()
            try:
                self.setSliderValue(value)
            except Exception:
                self.setSliderDown(False)

    def resetSlider(self):
        """Reset the slider value to zero."""
        self._sliderValue = 0.0
        self._sliderPreviousValue = 0.0

    def setSliderDown(self, down):
        """Called when the middle mouse button is released."""
        self._sliderDown = down
        if not down:
            self._sliderPosition = None
            self._sliderPreviousValue = self.sliderValue()

    def isSliderDown(self):
        """
        Return True if blending.

        :rtype: bool
        """
        return self._sliderDown

    def setSliderValue(self, value):
        """
        Set the blend value.

        :type value: float
        :rtype: bool
        """
        if self.isSliderEnabled():

            self._sliderValue = value

            if self.PAINT_SLIDER:
                self.update()

            self.sliderChanged.emit(value)

            if self.PAINT_SLIDER:
                self.update()

            print("Blending:" + str(value))

    def sliderValue(self):
        """
        Return the blend value.

        :rtype: float
        """
        return self._sliderValue

    def sliderPreviousValue(self):
        """
        :rtype: float
        """
        return self._sliderPreviousValue

    def sliderPosition(self):
        """
        :rtype: QtGui.QPoint
        """
        return self._sliderPosition

    # ------------------------------------------------------------------------
    # Support animated image sequence
    # ------------------------------------------------------------------------

    def imageSequenceEvent(self, event):  # 被 鼠标移动事件调用
        """
        :type event: QtCore.QEvent
        :rtype: None
        """
        if self.imageSequence():
            if self.rect():
                x = event.pos().x() - self.rect().x()
                width = self.rect().width()
                percent = 1.0 - (float(width - x) / float(width))
                frame = int(self.imageSequence().frameCount() * percent)
                self.imageSequence().jumpToFrame(frame)
                self.updateFrame()

    def resetImageSequence(self):
        self._imageSequence = None

    def imageSequence(self):
        """
        :rtype: studioqt.ImageSequence
        """
        return self._imageSequence

    def setImageSequence(self, value):
        """
        :type value: studioqt.ImageSequence  设置了 ImageSequence
        """
        self._imageSequence = value

    def setImageSequencePath(self):
        """
        :type path: str
        """
        # print(self.itemData())
        self._imageSequencePath = self.itemData()[7].replace('thumbnail.jpg', 'sequence')

    def imageSequencePath(self):
        """
        :rtype: str
        """
        return self._imageSequencePath

    def stop(self):
        """Stop playing the image sequence movie."""
        if self.imageSequence():
            self.imageSequence().stop()

    def play(self):
        """Start playing the image sequence movie."""
        # print("Play Animation")
        self.resetImageSequence()
        path = self.imageSequencePath() or self.thumbnailPath()
        # print(path)

        movie = None

        if os.path.isfile(path) and path.lower().endswith(".gif"):
            movie = QtGui.QMovie(path)
            movie.setCacheMode(QtGui.QMovie.CacheAll)
            movie.frameChanged.connect(self.updateFrame)

        elif os.path.isdir(path):
            if not self.imageSequence():
                movie = imagesequence.ImageSequence(path)
                movie.frameChanged.connect(self.updateFrame)

        if movie:
            self.setImageSequence(movie)
            self.imageSequence().start()

    def updateFrame(self):
        """
        Triggered when the movie object updates the current frame.
        """
        if self.imageSequence():
            itemSize = self._itemsWidget.itemSize()
            pixmap = self.imageSequence().currentPixmap()
            # pixmap.scaled(5, 5)
            self.setIcon(QtGui.QIcon(pixmap))
            # self.setSizeHint(QtCore.QSize(itemSize, itemSize + 40))
            # self._itemsWidget._setViewMode() # 不整理一下item会乱掉，没解决

    def playheadColor(self):
        """
        Return the playhead color.
        :rtype: QtGui.Color
        """
        return self.DEFAULT_PLAYHEAD_COLOR

    def paintPlayhead(self, painter, option):
        """
        Paint the playhead if the item has an image sequence.
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        imageSequence = self.imageSequence()

        if imageSequence and self.underMouse():  # 如果有图片序列 和 鼠标下

            count = imageSequence.frameCount()
            current = imageSequence.currentFrameNumber()

            if count > 0:
                percent = float((count + current) + 1) / count - 1
            else:
                percent = 0

            r = self.iconRect(option)
            c = self.playheadColor()

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(c))

            if percent <= 0:
                width = 0
            elif percent >= 1:
                width = r.width()
            else:
                width = (percent * r.width()) - 1

            height = 3
            y = r.y() + r.width() - (height - 1)

            painter.drawRect(r.x(), y, width, height)

    def typeIconPath(self):
        """
        Return the type icon path on disc.

        :rtype: path or None
        """
        if self.TYPE_ICON_PATH is None:
            return self.ICON_PATH

        return self.TYPE_ICON_PATH

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

    def typeIconRect(self, option):
        """
        Return the type icon rect.

        :rtype: QtGui.QRect
        """
        padding = 2 * self.dpi()
        r = self.iconRect(option)

        x = r.x() + padding
        y = r.y() + padding
        rect = QtCore.QRect(x, y, 13 * self.dpi(), 13 * self.dpi())

        return rect

    def paintTypeIcon(self, painter, option):
        """
        Draw the item type icon at the top left.
        左上角角标
        :type painter: QtWidgets.QPainter
        :type option: QtWidgets.QStyleOptionViewItem
        :rtype: None
        """
        rect = self.typeIconRect(option)
        typePixmap = self.typePixmap()
        if typePixmap:
            painter.setOpacity(0.5)
            painter.drawPixmap(rect, typePixmap)
            painter.setOpacity(1)
