# -*- coding: utf-8 -*-

import os
from utils import jsonHelper


# 原有组件
from .am_listWidget import MainListWidget
from .am_main import MainStackedWidget
from .am_tableWidget import MainTableWidget
from .am_listItem import ListItem
from .am_tableItem import TableItem
from .am_delegate import MainDelegate

# 新增高性能组件
from .am_thumbnail_loader import ThumbnailLoader, ThumbnailWorker, ThumbnailLoaderSignals
from .am_list_item_optimized import ListItemOptimized
from .am_list_view import ListView, ItemDelegate
from .am_items_widget import ItemsWidget, TableWidget
from .am_main_optimized import MainStackedWidget as MainStackedWidgetOptimized


scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('widgets', '')
tempPath = "{}/AssetsManagerTemp".format(os.environ.get('APPDATA'))


def projectSetting():
    data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % scriptsPath)
    return data