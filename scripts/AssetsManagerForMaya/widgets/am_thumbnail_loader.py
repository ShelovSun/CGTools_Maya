#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
异步缩略图加载器
参考 StudioLibrary 的 ImageWorker 实现
使用 QThreadPool + QRunnable 实现异步图片加载
"""

import os
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets


class ThumbnailLoaderSignals(QtCore.QObject):
    """缩略图加载信号"""
    loaded = QtCore.Signal(str, QtGui.QPixmap)  # path, pixmap
    error = QtCore.Signal(str, str)  # path, error message


class ThumbnailWorker(QtCore.QRunnable):
    """
    缩略图加载工作线程
    在后台线程中加载图片，避免阻塞 UI
    """

    _cache = {}  # 类级别的图片缓存
    _cache_lock = QtCore.QMutex()
    _max_cache_size = 500  # 最大缓存数量

    def __init__(self, path, size=120):
        super(ThumbnailWorker, self).__init__()
        self._path = path
        self._size = size
        self.signals = ThumbnailLoaderSignals()
        self._cancelled = False

    def setCancelled(self, value):
        self._cancelled = value

    @classmethod
    def getCachedPixmap(cls, path):
        """从缓存获取图片"""
        with QtCore.QMutexLocker(cls._cache_lock):
            return cls._cache.get(path)

    @classmethod
    def setCachedPixmap(cls, path, pixmap):
        """设置缓存图片"""
        with QtCore.QMutexLocker(cls._cache_lock):
            if len(cls._cache) >= cls._max_cache_size:
                # 清理最早的 20% 缓存
                keys_to_remove = list(cls._cache.keys())[:int(cls._max_cache_size * 0.2)]
                for key in keys_to_remove:
                    del cls._cache[key]
            cls._cache[path] = pixmap

    @classmethod
    def clearCache(cls):
        """清空缓存"""
        with QtCore.QMutexLocker(cls._cache_lock):
            cls._cache.clear()

    def run(self):
        """在线程池中执行"""
        if self._cancelled:
            return

        # 首先检查缓存
        cached = self.getCachedPixmap(self._path)
        if cached is not None:
            self.signals.loaded.emit(self._path, cached)
            return

        try:
            if not os.path.exists(self._path):
                # 如果路径不存在，使用默认图片
                self._loadDefaultIcon()
                return

            # 使用 QImageReader 读取图片，更高效
            reader = QtGui.QImageReader(self._path)
            reader.setAutoTransform(True)

            # 设置缩放大小以提高性能
            if self._size > 0:
                reader.setScaledSize(QtCore.QSize(self._size, self._size))

            image = reader.read()

            if self._cancelled:
                return

            if image.isNull():
                # 如果图片读取失败，使用默认图片
                self._loadDefaultIcon()
                return

            pixmap = QtGui.QPixmap.fromImage(image)

            # 存入缓存
            self.setCachedPixmap(self._path, pixmap)

            if not self._cancelled:
                self.signals.loaded.emit(self._path, pixmap)

        except Exception as e:
            if not self._cancelled:
                self.signals.error.emit(self._path, str(e))

    def _loadDefaultIcon(self):
        """加载默认图标"""
        default_path = self._getDefaultIconPath()
        if default_path and os.path.exists(default_path):
            pixmap = QtGui.QPixmap(default_path)
            self.setCachedPixmap(self._path, pixmap)
            if not self._cancelled:
                self.signals.loaded.emit(self._path, pixmap)

    def _getDefaultIconPath(self):
        """获取默认图标路径"""
        scripts_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(scripts_path, "icon", "blank_ch.png").replace("\\", "/")


class ThumbnailLoader(QtCore.QObject):
    """
    缩略图加载管理器
    管理线程池和加载队列
    """

    # 全局线程池
    _thread_pool = None
    _instance = None

    # 信号
    thumbnailLoaded = QtCore.Signal(str, QtGui.QPixmap)
    thumbnailError = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        super(ThumbnailLoader, self).__init__(parent)
        self._workers = {}
        self._pending_paths = set()
        self._mutex = QtCore.QMutex()

        # 初始化线程池
        if ThumbnailLoader._thread_pool is None:
            ThumbnailLoader._thread_pool = QtCore.QThreadPool()
            ThumbnailLoader._thread_pool.setMaxThreadCount(4)  # 最多4个线程

    @classmethod
    def instance(cls):
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = ThumbnailLoader()
        return cls._instance

    @classmethod
    def getThreadPool(cls):
        """获取线程池"""
        if cls._thread_pool is None:
            cls._thread_pool = QtCore.QThreadPool()
            cls._thread_pool.setMaxThreadCount(4)
        return cls._thread_pool

    def loadThumbnail(self, path, size=120):
        """
        异步加载缩略图
        :param path: 图片路径
        :param size: 目标尺寸
        """
        if not path:
            return

        with QtCore.QMutexLocker(self._mutex):
            if path in self._pending_paths:
                return  # 已经在加载中
            self._pending_paths.add(path)

        # 检查缓存
        cached = ThumbnailWorker.getCachedPixmap(path)
        if cached is not None:
            self.thumbnailLoaded.emit(path, cached)
            with QtCore.QMutexLocker(self._mutex):
                self._pending_paths.discard(path)
            return

        # 创建工作线程
        worker = ThumbnailWorker(path, size)
        worker.signals.loaded.connect(self._onThumbnailLoaded)
        worker.signals.error.connect(self._onThumbnailError)

        with QtCore.QMutexLocker(self._mutex):
            self._workers[path] = worker

        # 提交到线程池
        self.getThreadPool().start(worker)

    def _onThumbnailLoaded(self, path, pixmap):
        """缩略图加载完成"""
        with QtCore.QMutexLocker(self._mutex):
            self._pending_paths.discard(path)
            self._workers.pop(path, None)

        self.thumbnailLoaded.emit(path, pixmap)

    def _onThumbnailError(self, path, error):
        """缩略图加载错误"""
        with QtCore.QMutexLocker(self._mutex):
            self._pending_paths.discard(path)
            self._workers.pop(path, None)

        self.thumbnailError.emit(path, error)

    def cancelLoad(self, path):
        """取消加载指定路径的缩略图"""
        with QtCore.QMutexLocker(self._mutex):
            worker = self._workers.get(path)
            if worker:
                worker.setCancelled(True)
            self._pending_paths.discard(path)
            self._workers.pop(path, None)

    def clearPendingLoads(self):
        """清除所有待加载的缩略图"""
        with QtCore.QMutexLocker(self._mutex):
            for worker in self._workers.values():
                worker.setCancelled(True)
            self._workers.clear()
            self._pending_paths.clear()

    @classmethod
    def clearCache(cls):
        """清空缩略图缓存"""
        ThumbnailWorker.clearCache()