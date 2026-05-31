#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sceneTools_Maya Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import os
from utils import jsonHelper
import cgtw2
from my_vendor.Qt import QtGui
from my_vendor.Qt import QtCore
from my_vendor.Qt import QtWidgets
from widgets import item, imagesequence

reload(item)

scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')


def projectSetting():
    data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % scriptsPath)
    return data


def getItemsDictFromPath(__tab, __project, __type):
    """
    从路径获取字典
    :return:{role_name:{'role_name': xx,
                        'project': xx,
                        'type': xx,
                        'zh_name': xx,
                        'icon_path': xx}}
    """
    __items_dict = {}
    __path = '{0}/{1}/Assets/{2}'.format(projectSetting()['rootPath'], __project, __type)
    dir = QtCore.QDir(__path)
    for role_name in dir.entryList(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot):
        icon_path = '{0}/{1}/Icon/{1}.png'.format(__path, role_name)
        zn_name = ""
        bbb = {'role_name': role_name, 'project': __project, 'type': __type,
               'zh_name': zn_name, 'icon_path': icon_path}
        __items_dict.update({role_name: bbb})

    return __items_dict


def getItemsDictFromCGTW(__tab, __project, __type):
    """
    从CGTW获取item字典
    :return:{role_name:{'role_name': xx,
                        'project': xx,
                        'type': xx,
                        'zh_name': xx,
                        'icon_path': xx}}
    """
    t_tw = cgtw2.tw()
    __items_dict = {}
    asset, assetmaya, assetstapy, entity, cn_name = get_CGTW_entity(__tab)

    path = '{0}/{1}/{2}/{3}'.format(projectSetting()['rootPath'], __project, __tab, __type)
    TW_proj = str(projectSetting()['projectdiction'][__project])
    t_asset_ids = t_tw.info.get_id(TW_proj, asset, [[assetmaya, '=', u"完成"], 'and', [assetstapy, '=', __type]])
    TW_dictionInfo = t_tw.info.get(TW_proj, asset, t_asset_ids, [entity, cn_name])
    for info in TW_dictionInfo:
        icon_path = '{0}/{1}/Icon/{1}.png'.format(path, info[entity])
        bbb = {'role_name': info[entity], 'project': __project, 'type': __type,
               'zh_name': info[cn_name], 'icon_path': icon_path}
        __items_dict.update({info[entity]: bbb})

    return __items_dict


def get_CGTW_entity(_tab):
    if _tab == 'Assets':
        return 'asset', 'asset.maya', 'asset.assetstapy', 'asset.entity', 'asset.cn_name'
    else:
        if type != "Map":
            return 'scenes', 'scenes.maya', 'scenes.scenesassetstype', 'scenes.entity', 'scenes.assetsnamecn'
        else:
            return 'map', 'map.maya', 'map.type', 'map.entity', 'map.mapnamecn'


def addItemsIcon(listWgt, dict, __type, keyWords=u""):
    """

    :param keyWords:
    :param listWgt:
    :param dict:
    :param __type:
    :return:
    """
    for name in dict[__type].keys():
        item_data = dict[__type][name]
        _item = item.Item()
        if item_data['role_name'].lower().find(keyWords.lower()) != -1 or item_data['chname'].find(keyWords) != -1:
            _item.setData(QtCore.Qt.UserRole, item_data)
            _item.setText(name + "\n" + item_data['chname'])
            # icon = QtGui.QIcon()
            # icon.addPixmap(QtGui.QPixmap("%s/icon/blank_ch.png" % scriptsPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            _item.setIcon("%s/icon/blank_ch.png" % scriptsPath)
            _item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            listWgt.addItem(_item)


def addItemsList(listWgt, dict, __type, keyWords=u""):
    """

    :param keyWords:
    :param listWgt:
    :param dict:
    :param __type:
    :return:
    """
    for name in dict.keys():
        item_data = dict[__type][name]
        _item = item.Item()
        if item_data['role_name'].lower().find(keyWords.lower()) != -1 or item_data['chname'].find(keyWords) != -1:
            _item.setData(QtCore.Qt.UserRole, item_data)
            _item.setText(name + "\n" + item_data['chname'])
            listWgt.addItem(_item)


def countItemsIndexStart(wgt, itemSize, DEF_SPACING):
    width = wgt.width()
    scrollBarY = wgt.verticalScrollBar().value()
    column = width // (itemSize + DEF_SPACING)
    row = scrollBarY / (itemSize + DEF_SPACING + 40)
    return column * row


def countItemsIndexEnd(wgt, itemSize, DEF_SPACING):
    width = wgt.width()
    scrollBarY = wgt.verticalScrollBar().value()
    height = wgt.height() + scrollBarY
    column = width // (itemSize + DEF_SPACING)
    row = height / (itemSize + DEF_SPACING + 40) + 1
    return column * row


def update_visible_icon(wgt, start_index, end_index):
    __updatedNum = 0
    for index in range(start_index, end_index):
        item = wgt.item(index)
        itemdata = item.data(QtCore.Qt.UserRole)
        if item.isload():
            pass
        else:
            print(itemdata['chname'])
            # icon = QtGui.QIcon()
            icon_path = itemdata['iconpath']
            # if QtCore.QFileInfo(icon_path).exists() is False:
            #     icon_path = "%sicon/Default.png" % scriptsPath
            # icon.addPixmap(QtGui.QPixmap(icon_path), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon_path)
            item.setloaded()
            # itemdata['iconloaded'] = True
            # item.setData(QtCore.Qt.UserRole, itemdata)
            __updatedNum += 1
    return __updatedNum
