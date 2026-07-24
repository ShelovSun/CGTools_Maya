#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
优化的数据库查询模块
使用流式查询和批量处理来提高性能
"""

import psycopg2
from PySide2 import QtCore
from PySide2 import QtWidgets


class DatabaseQueryThread(QtCore.QThread):
    """
    优化的数据库查询线程
    支持流式查询，分批返回数据
    """

    # 信号
    dataReady = QtCore.Signal(list)  # 一批数据准备好
    rowReady = QtCore.Signal(tuple)  # 单行数据准备好
    errorOccurred = QtCore.Signal(str)  # 错误发生
    queryFinished = QtCore.Signal(int)  # 查询完成，返回总数

    def __init__(self, db, user, password, host, port="5432"):
        super(DatabaseQueryThread, self).__init__()

        self._db = db
        self._user = user
        self._password = password
        self._host = host
        self._port = port

        self._query = ""
        self._params = None
        self._batch_size = 50  # 每批返回的数据量
        self._cancelled = False
        self._connection = None
        self._cursor = None

    def setQuery(self, query, params=None):
        """设置查询语句"""
        self._query = query
        self._params = params

    def setBatchSize(self, size):
        """设置批处理大小"""
        self._batch_size = size

    def cancel(self):
        """取消查询"""
        self._cancelled = True
        if self._cursor:
            try:
                self._cursor.close()
            except:
                pass
        if self._connection:
            try:
                self._connection.cancel()
            except:
                pass

    def run(self):
        """执行查询"""
        if not self._query:
            self.errorOccurred.emit("No query set")
            return

        self._cancelled = False
        total_count = 0

        try:
            # 建立连接
            self._connection = psycopg2.connect(
                database=self._db,
                user=self._user,
                password=self._password,
                host=self._host,
                port=self._port
            )

            # 使用服务器端游标（流式查询）
            self._cursor = self._connection.cursor(name='server_cursor')
            self._cursor.itersize = self._batch_size

            # 执行查询
            if self._params:
                self._cursor.execute(self._query, self._params)
            else:
                self._cursor.execute(self._query)

            # 分批获取数据
            batch = []
            for row in self._cursor:
                if self._cancelled:
                    break

                batch.append(row)
                self.rowReady.emit(row)
                total_count += 1

                if len(batch) >= self._batch_size:
                    self.dataReady.emit(batch[:])
                    batch = []
                    # 短暂休眠以允许 UI 更新
                    self.msleep(1)

            # 发送剩余数据
            if batch and not self._cancelled:
                self.dataReady.emit(batch)

            if not self._cancelled:
                self.queryFinished.emit(total_count)

        except Exception as e:
            if not self._cancelled:
                self.errorOccurred.emit(str(e))

        finally:
            if self._cursor:
                try:
                    self._cursor.close()
                except:
                    pass
            if self._connection:
                try:
                    self._connection.close()
                except:
                    pass


class AssetDatabaseManager(QtCore.QObject):
    """
    资产管理数据库管理器
    提供统一的资产查询接口
    """

    # 信号
    assetsReady = QtCore.Signal(list)  # 资产数据准备好
    assetRowReady = QtCore.Signal(tuple)  # 单行资产准备好
    queryError = QtCore.Signal(str)  # 查询错误
    queryFinished = QtCore.Signal(int)  # 查询完成

    def __init__(self, user, password, host, port="5432"):
        super(AssetDatabaseManager, self).__init__()

        self._user = user
        self._password = password
        self._host = host
        self._port = port

        self._current_thread = None

    def queryAssets(self, db, asset_type=None, keywords=None):
        """
        查询资产（public."asset"）
        :param db: 数据库名
        :param asset_type: 资产类型
        :param keywords: 关键词列表
        """
        query = '''
            SELECT "asset.date", "asset.name", "asset.zh_name", "asset.mod_artist",
                   "asset.mod_status", "asset.rig_artist", "asset.rig_status",
                   "asset.icon", "asset.note"
            FROM public."asset"
            WHERE TRUE
        '''
        params = []
        if asset_type:
            query += ' AND "asset.type" = %s'
            params.append(asset_type)
        query += self._keyword_clause("asset", keywords, params)
        query += ' ORDER BY "asset.date" DESC'
        self._run_query(db, query, params)

    def queryScenes(self, db, scene_type=None, keywords=None):
        """
        查询场景（public."scene"）。为与 asset 保持同构 9 列，scene 无独立 rig 列，
        故 artist 同时填第 3/5 列、status 同时填第 4/6 列（与 sceneTools.get_database 一致）。
        :param db: 数据库名
        :param scene_type: 场景类型
        :param keywords: 关键词列表
        """
        query = '''
            SELECT "scene.date", "scene.name", "scene.zh_name", "scene.artist",
                   "scene.status", "scene.artist", "scene.status",
                   "scene.icon", "scene.note"
            FROM public."scene"
            WHERE TRUE
        '''
        params = []
        if scene_type:
            query += ' AND "scene.type" = %s'
            params.append(scene_type)
        query += self._keyword_clause("scene", keywords, params)
        query += ' ORDER BY "scene.date" DESC'
        self._run_query(db, query, params)

    def queryAll(self, db, keywords=None):
        """
        "全部目录"：横跨 asset + scene 两表 UNION ALL，各取同 9 列（别名 c0..c8）。
        只按名称关键词过滤，不套用表专属的高级筛选（两表字段名不同）。
        """
        params = []
        asset_kw = self._keyword_clause("asset", keywords, params)
        scene_kw = self._keyword_clause("scene", keywords, params)
        query = '''
            SELECT * FROM (
              SELECT "asset.date" AS c0, "asset.name" AS c1, "asset.zh_name" AS c2, "asset.mod_artist" AS c3,
                     "asset.mod_status" AS c4, "asset.rig_artist" AS c5, "asset.rig_status" AS c6,
                     "asset.icon" AS c7, "asset.note" AS c8
              FROM public."asset" WHERE TRUE {0}
              UNION ALL
              SELECT "scene.date", "scene.name", "scene.zh_name", "scene.artist",
                     "scene.status", "scene.artist", "scene.status", "scene.icon", "scene.note"
              FROM public."scene" WHERE TRUE {1}
            ) AS combined
            ORDER BY c0 DESC
        '''.format(asset_kw, scene_kw)
        self._run_query(db, query, params)

    @staticmethod
    def _keyword_clause(prefix, keywords, params):
        """按 name/zh_name 关键词拼一段以 AND 开头的参数化 SQL（无关键词返回空串）。
        会把两个 ILIKE 参数追加进 params（就地修改），保证占位符与参数顺序一致。"""
        if keywords and keywords[0]:
            keyword = keywords[0]
            params.extend([f'%{keyword}%', f'%{keyword}%'])
            return ' AND ("{0}.name" ILIKE %s OR "{0}.zh_name" ILIKE %s)'.format(prefix)
        return ""

    def _run_query(self, db, query, params):
        """取消上一次查询 -> 建线程 -> 连信号 -> start（queryAssets/Scenes/All 共用）。"""
        self.cancelQuery()
        self._current_thread = DatabaseQueryThread(
            db, self._user, self._password, self._host, self._port
        )
        self._current_thread.setQuery(query, params if params else None)
        self._current_thread.dataReady.connect(self.assetsReady.emit)
        self._current_thread.rowReady.connect(self.assetRowReady.emit)
        self._current_thread.errorOccurred.connect(self.queryError.emit)
        self._current_thread.queryFinished.connect(self.queryFinished.emit)
        self._current_thread.start()

    def cancelQuery(self):
        """取消当前查询"""
        if self._current_thread and self._current_thread.isRunning():
            self._current_thread.cancel()
            self._current_thread.wait(1000)

    def isQuerying(self):
        """是否正在查询"""
        return self._current_thread is not None and self._current_thread.isRunning()
