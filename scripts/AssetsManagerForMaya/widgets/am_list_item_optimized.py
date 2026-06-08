#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
优化的 ListItem 类
参考 StudioLibrary 的 Item 类实现
支持异步缩略图加载、自定义绘制、图片缓存
"""

import os
import math
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2 import QtWidgets

from widgets.am_thumbnail_loader import ThumbnailLoader, ThumbnailWorker
from utils import jsonHelper

# 收藏/标签的本地存储目录（与 am_tableItem、faverWidget 共用同一份 JSON）
tempPath = "{}/AssetsManagerTemp".format(os.environ.get('APPDATA'))


class ListItemOptimized(QtWidgets.QListWidgetItem):
    """
    优化的列表项类
    - 异步加载缩略图
    - 延迟绘制
    - 图片缓存
    """

    # 类级别的默认缩略图路径
    DEFAULT_THUMBNAIL_PATH = None
    TYPE_ICON_PATH = None
    _type_pixmap_cache = {}

    # 类型图标缓存
    _status_icons = {}

    # 共享的默认缩略图 pixmap，只从磁盘/网络读取一次后全局复用（见 _getDefaultPixmap）
    _default_pixmap = None
    # 文字字体，避免每帧 paint 重建（见 _getTextFont）
    _text_font = None

    def __init__(self, parent=None, tab="Asset"):
        super(ListItemOptimized, self).__init__(parent)

        self._tab = tab
        self._item_data = {}
        self._thumbnail_path = ""
        self._thumbnail_pixmap = None
        self._thumbnail_loaded = False
        self._thumbnail_loading = False
        self._thumbnail_size = 120

        # 缩放结果缓存：滚动时 paint 每帧都会缩放，缓存避免重复 SmoothTransformation。
        # key = (源图 cacheKey, 目标宽, 目标高)，源图或尺寸变了才重新缩放。
        self._pixmap_scaled = None
        self._pixmap_scaled_key = None

        # 背景渐变与边框画笔缓存，避免每帧 paint 重建（见 _backgroundGradient/_borderPen）
        self._gradient_cache = {}
        self._border_pen = None

        self._is_favor = False
        self._is_tag = False
        self._under_mouse = False

        self._items_widget = None
        self._padding = 4
        self._border_size = 1.5

        # 颜色定义
        self._default_color = QtGui.QColor(40, 41, 43, 255)
        self._default_text_bg_color = QtGui.QColor(30, 30, 30, 255)
        self._hover_color = QtGui.QColor(50, 50, 50, 255)
        self._selected_color = QtGui.QColor(82, 133, 166, 255)
        self._text_color = QtGui.QColor(255, 255, 255, 180)
        self._text_selected_color = QtGui.QColor(255, 255, 255, 255)

        # 滑块相关
        self._slider_enabled = False
        self._slider_down = False
        self._slider_value = 0.0
        self._slider_previous_value = 0.0
        self._slider_position = None

        # 图片序列
        self._image_sequence = None
        self._image_sequence_path = ""

        # 当前绘制矩形（paint() 中经 setRect 赋值；预置以防鼠标事件早于首次绘制）
        self._rect = None

        # 缩略图加载器（单例）。
        # 注意：不再让每个 item 都 connect 全局 thumbnailLoaded 信号——
        # 否则 N 个 item 会被 N 次加载各触发一次，形成 O(N^2) 信号风暴；
        # 且 item 是 QListWidgetItem（非 QObject），常驻连接会让其无法回收、跨刷新持续累积。
        # 改为按路径回调（见 loadThumbnail 传入的 callback）。
        self._loader = ThumbnailLoader.instance()

    def __del__(self):
        """析构时停止图片序列"""
        self.stop()

    def setItemsWidget(self, widget):
        """设置所属的 items widget"""
        self._items_widget = widget

    def itemsWidget(self):
        """获取所属的 items widget"""
        return self._items_widget

    def setItemData(self, data):
        """
        设置数据
        data: tuple (date, name, zh_name, mod_artist, mod_status, rig_artist, rig_status, icon_path, note)
        """
        self._item_data = data
        if len(data) > 7:
            self._thumbnail_path = data[7] if data[7] else ""
            self.setText(str(data[1]))  # 设置名称用于排序

    def itemData(self):
        """获取数据"""
        return self._item_data

    def name(self):
        """获取资产名"""
        return str(self._item_data[1]) if len(self._item_data) > 1 else ""

    def zhName(self):
        """获取中文名"""
        return str(self._item_data[2]) if len(self._item_data) > 2 else ""

    def thumbnailPath(self):
        """获取缩略图路径"""
        return self._thumbnail_path

    def setThumbnailSize(self, size):
        """设置缩略图尺寸"""
        self._thumbnail_size = size

    def loadThumbnail(self):
        """异步加载缩略图"""
        if self._thumbnail_loaded or self._thumbnail_loading:
            return

        if not self._thumbnail_path:
            self._thumbnail_path = self._getDefaultThumbnailPath()

        self._thumbnail_loading = True

        # 先检查缓存
        cached = ThumbnailWorker.getCachedPixmap(self._thumbnail_path)
        if cached is not None:
            self._thumbnail_pixmap = cached
            self._thumbnail_loaded = True
            self._thumbnail_loading = False
            self._repaintHost()
        else:
            # 设置默认图标（复用共享 pixmap，不再每个 item 同步读网络文件）
            self._thumbnail_pixmap = self._getDefaultPixmap()
            # 异步加载真实图片，仅通过按路径回调通知本 item（避免全局信号风暴）
            self._loader.loadThumbnail(self._thumbnail_path, self._thumbnail_size,
                                       self._onThumbnailLoaded)

    def _repaintHost(self):
        """触发宿主视图重绘。
        QAbstractItemView 的条目画在 viewport 上，直接对 view 调 update() 不会刷新条目，
        必须刷新 viewport——否则异步缩略图到达后图标不会立即显示，需手动滚动才会重绘。
        """
        w = self._items_widget
        if not w:
            return
        try:
            target = w.viewport() if hasattr(w, "viewport") else w
            target.update()
        except RuntimeError:
            # 视图可能已销毁（窗口关闭后回调晚到），忽略
            pass

    def _onThumbnailLoaded(self, path, pixmap):
        """缩略图加载完成回调（由 ThumbnailLoader 按路径回调，主线程执行）"""
        if path == self._thumbnail_path:
            self._thumbnail_pixmap = pixmap
            self._thumbnail_loaded = True
            self._thumbnail_loading = False
            self._repaintHost()

    def isThumbnailLoaded(self):
        """缩略图是否已加载"""
        return self._thumbnail_loaded

    def isThumbnailLoading(self):
        """缩略图是否正在加载（请求已提交但未完成）。"""
        return self._thumbnail_loading

    def resetThumbnail(self):
        """复位加载状态，使条目可被重新请求。
        用于：之前的请求被 cancelPathsExcept 取消后，滚回该区域时能重新加载。
        """
        self._thumbnail_loaded = False
        self._thumbnail_loading = False

    def setLoaded(self, value):
        """设置加载状态"""
        self._thumbnail_loaded = value

    def isLoaded(self):
        return self._thumbnail_loaded

    def setFavor(self, value):
        """设置收藏状态，并写入本地 Asset_fave.json（与表格条目、收藏面板共用）。"""
        self._is_favor = bool(value)
        self._writeFavor(self._is_favor)

    def isFavor(self):
        """以本地 JSON 为准判断是否已收藏（重开后状态依然正确）。"""
        self._is_favor = self.name() in self._readFavorNames()
        return self._is_favor

    def setTag(self, tag):
        """设置标签，并写入本地 Asset_tag.json（与收藏面板共用）。"""
        self._is_tag = bool(tag)
        if tag:
            self._writeTag(tag)

    def isTag(self):
        """以本地 JSON 为准判断该资产是否被打过任意标签。"""
        data = jsonHelper.readDictFromFile(self._tagJsonPath())
        self._is_tag = False
        if isinstance(data, dict):
            name = self.name()
            for rows in data.values():
                if isinstance(rows, list) and any(
                        isinstance(r, (list, tuple)) and len(r) > 1 and str(r[1]) == name
                        for r in rows):
                    self._is_tag = True
                    break
        return self._is_tag

    # ---- 收藏 / 标签的本地 JSON 持久化（以资产名 itemData[1] 为 key） ----
    def _faveJsonPath(self):
        return '%s/%s_fave.json' % (tempPath, self._tab)

    def _tagJsonPath(self):
        return '%s/%s_tag.json' % (tempPath, self._tab)

    @staticmethod
    def _ensureTempDir():
        # writeDictToFile 不会自建目录，写之前先确保存在
        if not os.path.exists(tempPath):
            os.makedirs(tempPath)

    def _readFavorNames(self):
        """读 Asset_fave.json 里所有收藏资产名；文件不存在/格式不符按空处理。"""
        data = jsonHelper.readDictFromFile(self._faveJsonPath())
        if not isinstance(data, list):
            return []
        return [str(r[1]) for r in data
                if isinstance(r, (list, tuple)) and len(r) > 1]

    def _writeFavor(self, value):
        """value=True 加入收藏（按资产名去重），False 移除。"""
        self._ensureTempDir()
        path = self._faveJsonPath()
        data = jsonHelper.readDictFromFile(path)
        if not isinstance(data, list):
            data = []
        name = self.name()
        data = [r for r in data if not (
            isinstance(r, (list, tuple)) and len(r) > 1 and str(r[1]) == name)]
        if value:
            data.append(list(self._item_data))
        jsonHelper.writeDictToFile(path, data)

    def _writeTag(self, tag):
        """把该资产加入指定标签分组（按资产名去重）。"""
        self._ensureTempDir()
        path = self._tagJsonPath()
        data = jsonHelper.readDictFromFile(path)
        if not isinstance(data, dict):
            data = {}
        name = self.name()
        bucket = data.get(tag)
        if not isinstance(bucket, list):
            bucket = []
        bucket = [r for r in bucket if not (
            isinstance(r, (list, tuple)) and len(r) > 1 and str(r[1]) == name)]
        bucket.append(list(self._item_data))
        data[tag] = bucket
        jsonHelper.writeDictToFile(path, data)

    @classmethod
    def _getDefaultThumbnailPath(cls):
        """获取默认缩略图路径"""
        if cls.DEFAULT_THUMBNAIL_PATH is None:
            scripts_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            cls.DEFAULT_THUMBNAIL_PATH = os.path.join(
                scripts_path, "icon", "blank_ch.png"
            ).replace("\\", "/")
        return cls.DEFAULT_THUMBNAIL_PATH

    @classmethod
    def _getDefaultPixmap(cls):
        """返回共享的默认缩略图 pixmap，只从磁盘/网络读取一次后全局复用。

        之前每个 item 都在 loadThumbnail/_paintIcon 里 QPixmap(path) 各读一次默认图；
        工具放到网络盘后，这会在 UI 线程上对同一张 blank_ch.png 反复发起同步网络读取，
        是滚动卡顿的主因之一。改为类级别只读一次。QPixmap 隐式共享且此处只读不改，
        多个 item 共用同一份安全。
        """
        if cls._default_pixmap is None:
            cls._default_pixmap = QtGui.QPixmap(cls._getDefaultThumbnailPath())
        return cls._default_pixmap

    @classmethod
    def _getTextFont(cls):
        """返回共享的文字字体，避免每帧 paint 重建 QFont。"""
        if cls._text_font is None:
            cls._text_font = QtGui.QFont(u"Microsoft YaHei UI", 10)
        return cls._text_font

    def sizeHint(self):
        """返回 item 尺寸"""
        size = self._thumbnail_size if self._items_widget is None else self._items_widget.itemSize()
        return QtCore.QSize(size + self._padding * 2, size + 40 + self._padding * 2)

    def iconPercent(self):
        """图标(正方形)高度占整个 item 高度的比例。

        图标为边长 = tile 整宽 的正方形(左右铺满)，故比例 = tile宽 / tile高
        = (size+2*padding) / (size+40+2*padding)。渐变背景在此比例处由图标区过渡到
        文字区，恰与图标底边对齐；_paintText 也据此把文字放在图标正下方。
        """
        size = self._thumbnail_size if self._items_widget is None else self._items_widget.itemSize()
        pad = self._padding
        return float(size + pad * 2) / float(size + 40 + pad * 2)

    def paint(self, painter, option, index):
        """
        自定义绘制
        参考 StudioLibrary 的 Item.paint 实现
        """
        self.setRect(QtCore.QRect(option.rect))

        painter.save()
        try:
            self._paintBackground(painter, option)
            self._paintIcon(painter, option)
            self._paintText(painter, option)
            # self._paintStatusIcon(painter, option)
        finally:
            painter.restore()

    def _paintBackground(self, painter, option):
        """绘制背景"""
        is_selected = option.state & QtWidgets.QStyle.State_Selected
        is_mouse_over = option.state & QtWidgets.QStyle.State_MouseOver

        painter.setPen(QtCore.Qt.NoPen)

        rect = self._visualRect(option)

        if is_selected:
            gradient = self._backgroundGradient("selected")
        elif is_mouse_over:
            gradient = self._backgroundGradient("hover")
        else:
            gradient = self._backgroundGradient("normal")

        painter.setBrush(QtGui.QBrush(gradient))
        painter.drawRect(rect)

        # 绘制边框
        if is_selected:
            painter.setPen(self._borderPen())
            painter.setBrush(QtCore.Qt.NoBrush)
            painter.drawRect(rect.adjusted(1, 1, -1, -1))

    def _paintIcon(self, painter, option):
        """绘制图标"""
        if self._thumbnail_pixmap is None or self._thumbnail_pixmap.isNull():
            # 使用默认图标（共享 pixmap，避免在绘制路径同步读网络文件）
            self._thumbnail_pixmap = self._getDefaultPixmap()

        rect = self._iconRect(option)
        pixmap = self._scalePixmap(self._thumbnail_pixmap, rect)

        if pixmap and not pixmap.isNull():
            pixmap_rect = QtCore.QRect(rect)
            pixmap_rect.setWidth(pixmap.width())
            pixmap_rect.setHeight(pixmap.height())

            # 居中
            x = (rect.width() - pixmap.width()) // 2
            y = (rect.height() - pixmap.height()) // 2
            pixmap_rect.translate(x, y)

            painter.drawPixmap(pixmap_rect, pixmap)

    def _paintText(self, painter, option):
        """绘制文字"""
        rect = self._visualRect(option)
        text_rect = QtCore.QRect(rect)

        # 文字区域在图标下方
        icon_percent = self.iconPercent()
        text_y = int(rect.y() + rect.height() * icon_percent)
        text_rect.setY(text_y)
        text_rect.setHeight(rect.height() - (text_y - rect.y()))

        is_selected = option.state & QtWidgets.QStyle.State_Selected
        color = self._text_selected_color if is_selected else self._text_color

        painter.setPen(QtGui.QPen(color))
        # 文字字体与窗体一致，使用微软雅黑（同 UI 的 "Microsoft YaHei UI" 10pt、
        # TableWidget 的字体）。默认 painter 字体随系统/Qt 主题变化，显式指定保持统一。
        # 字体对象共享缓存，避免每帧重建（见 _getTextFont）。
        painter.setFont(self._getTextFont())

        # 绘制名称和中文名
        name = self.name()
        zh_name = self.zhName()

        if zh_name:
            text = f"{name}\n{zh_name}"
        else:
            text = name

        align = QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter
        painter.drawText(text_rect, align, text)

    def _paintStatusIcon(self, painter, option):
        """绘制状态图标（模型和绑定状态）"""
        if len(self._item_data) < 7:
            return

        rect = self._iconRect(option)
        icon_size = 12

        # 模型状态图标
        mod_status = self._item_data[4] if len(self._item_data) > 4 else ""
        rig_status = self._item_data[6] if len(self._item_data) > 6 else ""

        # 状态颜色
        mod_color = self._getStatusColor(mod_status)
        rig_color = self._getStatusColor(rig_status)

        # 绘制状态指示器
        mod_rect = QtCore.QRect(rect.x() + 2, rect.y() + 2, icon_size, icon_size)
        rig_rect = QtCore.QRect(rect.x() + icon_size + 4, rect.y() + 2, icon_size, icon_size)

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(QtGui.QBrush(mod_color))
        painter.drawEllipse(mod_rect)
        painter.setBrush(QtGui.QBrush(rig_color))
        painter.drawEllipse(rig_rect)

    def _getStatusColor(self, status):
        """获取状态颜色"""
        status_map = {
            u"已完成": QtGui.QColor(100, 200, 100, 200),
            u"制作中": QtGui.QColor(200, 200, 100, 200),
            u"未开始": QtGui.QColor(150, 150, 150, 100),
        }
        return status_map.get(status, QtGui.QColor(150, 150, 150, 100))

    def _paintPlayhead(self, painter, option):
        """绘制播放头（用于 GIF 序列）"""
        if self._image_sequence and self._under_mouse:
            count = self._image_sequence.frameCount()
            current = self._image_sequence.currentFrameNumber()

            if count > 0:
                percent = float(current) / count
            else:
                percent = 0

            rect = self._iconRect(option)
            c = QtGui.QColor(255, 255, 255, 220)

            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(QtGui.QBrush(c))

            width = int(percent * rect.width())
            height = 3
            y = rect.y() + rect.height() - height

            painter.drawRect(rect.x(), y, width, height)

    def _backgroundGradient(self, kind):
        """返回按状态(kind)缓存的竖向背景渐变。

        渐变用 ObjectBoundingMode（坐标 0..1 映射到被绘制矩形的包围盒），因此与条目
        当前的 y 坐标无关——滚动时同一个渐变可在任意位置复用，无需每帧按 rect.y() 重建。
        仅当 kind 或 iconPercent（随条目尺寸变化）改变时才重新构造。
        """
        percent = self.iconPercent()
        key = (kind, percent)
        gradient = self._gradient_cache.get(key)
        if gradient is not None:
            return gradient

        gradient = QtGui.QLinearGradient(0, 0, 0, 1)
        gradient.setCoordinateMode(QtGui.QGradient.ObjectBoundingMode)
        if kind == "selected":
            gradient.setColorAt(percent, QtGui.QColor(65, 69, 75, 255))
            gradient.setColorAt(percent + 0.01, self._selected_color)
        elif kind == "hover":
            gradient.setColorAt(percent, QtGui.QColor(62, 64, 66, 255))
            gradient.setColorAt(percent + 0.01, self._hover_color)
        else:  # normal
            gradient.setColorAt(0, QtGui.QColor(35, 35, 35, 255))
            gradient.setColorAt(percent, QtGui.QColor(60, 62, 64, 255))
            gradient.setColorAt(percent + 0.01, self._default_text_bg_color)

        self._gradient_cache[key] = gradient
        return gradient

    def _borderPen(self):
        """返回选中态边框画笔，缓存避免每帧重建。"""
        if self._border_pen is None:
            self._border_pen = QtGui.QPen(self._selected_color, self._border_size)
        return self._border_pen

    def _visualRect(self, option):
        """获取可视矩形"""
        return QtCore.QRect(option.rect)

    def _iconRect(self, option):
        """图标矩形：顶部正方形、铺满 tile 整宽，左右与底部都不留白。

        边长取 tile 整宽，方形缩略图(加载时已被强制缩放为正方形)正好铺满；其下方剩余
        高度(= 文字区高 40)留给文字。不再扣 padding——padding 会在左右/底部留出空隙。
        """
        rect = self._visualRect(option)
        side = rect.width()
        return QtCore.QRect(rect.x(), rect.y(), side, side)

    def _scalePixmap(self, pixmap, rect):
        """缩放图片到指定矩形，缓存缩放结果。

        滚动时 delegate 对每个可见条目每帧都会调用 paint→_scalePixmap，若每次都做
        SmoothTransformation 平滑缩放会明显吃 CPU、造成滚轮/拖动卡顿。这里按
        (源图 cacheKey, 目标宽高) 缓存：源图(默认图→真实图、或 GIF 换帧时 cacheKey 会变)
        或尺寸变化时才重新缩放，否则直接复用，与旧路径 am_listItem.scalePixmap 一致。
        """
        if pixmap.isNull():
            return pixmap

        key = (pixmap.cacheKey(), rect.width(), rect.height())
        if self._pixmap_scaled is None or self._pixmap_scaled_key != key:
            self._pixmap_scaled = pixmap.scaled(
                rect.width(),
                rect.height(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
            self._pixmap_scaled_key = key

        return self._pixmap_scaled

    # 鼠标事件处理
    def mouseEnterEvent(self, event):
        """鼠标进入"""
        self._under_mouse = True
        self.play()

    def mouseLeaveEvent(self, event):
        """鼠标离开"""
        self._under_mouse = False
        self.stop()

    def mouseMoveEvent(self, event):
        """鼠标移动"""
        self._sliderEvent(event)
        self._imageSequenceEvent(event)

    def mousePressEvent(self, event):
        """鼠标按下（由 ListView.mousePressEvent 转发）。滑块启用时记录起点。"""
        if self._slider_enabled:
            self.setSliderDown(True)
            self._slider_position = event.pos()

    def mouseReleaseEvent(self, event):
        """鼠标释放（由 ListView.mouseReleaseEvent 转发）。"""
        if self._slider_enabled:
            self.setSliderDown(False)

    # 图片序列支持
    def setImageSequencePath(self, path):
        """设置图片序列路径"""
        self._image_sequence_path = path

    def imageSequencePath(self):
        """获取图片序列路径"""
        return self._image_sequence_path

    def imageSequence(self):
        """获取图片序列"""
        return self._image_sequence

    def setImageSequence(self, sequence):
        """设置图片序列"""
        self._image_sequence = sequence

    def play(self):
        """播放图片序列"""
        path = self._image_sequence_path or self._thumbnail_path
        if not path:
            return

        # 检查是否是 GIF。先按扩展名短路，避免对非 GIF 的普通缩略图也做 os.path.isfile——
        # 在网络盘上 isfile 是一次同步网络 stat，滚动时条目从光标下经过会逐条触发 hover、
        # 反复 stat，足以造成卡顿。绝大多数缩略图是 jpg/png，扩展名判断会直接短路掉。
        if path.lower().endswith(".gif") and os.path.isfile(path):
            movie = QtGui.QMovie(path)
            movie.setCacheMode(QtGui.QMovie.CacheAll)
            movie.frameChanged.connect(self._updateFrame)
            self._image_sequence = movie
            self._image_sequence.start()

    def stop(self):
        """停止图片序列"""
        if self._image_sequence:
            self._image_sequence.stop()
            self._image_sequence = None

    def _updateFrame(self, frame=None):
        """更新帧"""
        if self._image_sequence:
            pixmap = self._image_sequence.currentPixmap()
            if pixmap and not pixmap.isNull():
                self._thumbnail_pixmap = pixmap
                self._repaintHost()

    def _imageSequenceEvent(self, event):
        """图片序列事件处理"""
        if self._image_sequence and self._rect:
            x = event.pos().x() - self._rect.x()
            width = self._rect.width()
            if width > 0:
                percent = float(x) / width
                if hasattr(self._image_sequence, 'frameCount'):
                    frame = int(self._image_sequence.frameCount() * percent)
                    self._image_sequence.jumpToFrame(frame)
                    self._updateFrame()

    # 滑块支持
    def _sliderEvent(self, event):
        """滑块事件"""
        if self._slider_down and self._slider_enabled:
            value = (event.pos().x() - self._slider_position.x()) / 1.5
            value = math.ceil(value) + self._slider_previous_value
            self.setSliderValue(value)

    def setSliderEnabled(self, enabled):
        """设置滑块启用状态"""
        self._slider_enabled = enabled

    def isSliderEnabled(self):
        return self._slider_enabled

    def setSliderDown(self, down):
        """设置滑块按下状态"""
        self._slider_down = down
        if not down:
            self._slider_position = None
            self._slider_previous_value = self._slider_value

    def isSliderDown(self):
        return self._slider_down

    def setSliderValue(self, value):
        """设置滑块值"""
        if self._slider_enabled:
            self._slider_value = max(0, min(100, value))

    def sliderValue(self):
        return self._slider_value

    def setRect(self, rect):
        """设置矩形区域"""
        self._rect = rect

    def rect(self):
        return self._rect