#!/usr/bin/env python
# -*- coding: utf-8 -*-
# common Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 设置Action面板，修改右键菜单

import os, sys,threading
import cython
from PySide2 import  QtWidgets, QtCore, QtGui
sys.path.append('C:\\CgTeamWork_v6.2\\bin\\base')
import cgtw2
t_tw = cgtw2.tw()
from . import scriptsPath


@cython.boundscheck(False)
@cython.wraparound(False)
class Common():
    def __init__(self):
        self.tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))

    def test(self):
        print("Common is working in Cython !")

    def projectSetting(self):
        sys.path.append(scriptsPath)
        from utils import jsonHelper
        data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % scriptsPath)
        return data

    cdef _listWidgetAddItems_CGT(self, listWgt, itemSize,project, type):
        ''' ** 根据type，project，读取CGT资产数据库，icon优先读取本地数据（快速），设置主面板item显示 '''
        cdef char path
        path = ('{0}/{1}/{2}/{3}').format(self.projectSetting()['rootPath'], project, self.projectSetting()['assetFolder'],type)
        TW_proj = self.projectSetting()['projectdiction'][project]
        t_asset_ids = t_tw.info.get_id(TW_proj, 'asset',[['asset.maya', '=', u"完成"], 'and', ['asset.assetstapy', '=', type]])
        TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.cn_name'])
        for info in TW_dictionInfo:
            cdef char icon_path
            icon_path = ('{0}/{1}/Assets/{2}/{3}.png').format(self.tempPath, project, type, info['asset.entity'])
            if QtCore.QFileInfo(icon_path).exists() is False:
                icon_path = ('{0}/{1}/{2}/{1}.png').format(path, info['asset.entity'], self.projectSetting()['iconFolder'])
                if QtCore.QFileInfo(icon_path).exists() is False:
                    icon_path = self.projectSetting()['defaultIcon']
            # self.addItems_CGT(info['asset.entity'], icon_path, info['asset.cn_name']) #非多线程直接设置items
            sub_thread = threading.Thread(target=self._addItems_CGT,
                                          args=(listWgt, itemSize, project, type, info['asset.entity'], path, icon_path, info['asset.cn_name']))
            sub_thread.setDaemon(True)
            sub_thread.start()
            sub_thread.join()

    def _listWidgetAddItems_CGT_Search(self, listWgt, itemSize,project, type, keyWords):
        ''' 根据type，project，读取CGT资产数据库，icon优先读取本地数据（快速），设置主面板item显示 '''
        path = ('{0}/{1}/{2}/{3}').format(self.projectSetting()['rootPath'], project, self.projectSetting()['assetFolder'],type)
        TW_proj = self.projectSetting()['projectdiction'][project]
        t_asset_ids = t_tw.info.get_id(TW_proj, 'asset',
                                       [['asset.maya', '=', u"完成"], 'and', ['asset.assetstapy', '=', type]])
        TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.cn_name'])
        for info in TW_dictionInfo:
            if info['asset.entity'].lower().find(keyWords.lower()) != -1 or info['asset.cn_name'].find(keyWords) != -1:
                icon_path = ('{0}/{1}/Assets/{2}/{3}.png').format(self.tempPath, project, type, info['asset.entity'])
                if QtCore.QFileInfo(icon_path).exists() is False:
                    icon_path = ('{0}/{1}/{2}/{1}.png').format(path, info['asset.entity'],
                                                               self.projectSetting()['iconFolder'])
                    if QtCore.QFileInfo(icon_path).exists() is False:
                        icon_path = self.projectSetting()['defaultIcon']
                # self._addItems_CGT(listWgt,itemSize,project,type,info['asset.entity'], path,icon_path, info['asset.cn_name'])
                sub_thread = threading.Thread(target=self._addItems_CGT,
                                              args=(listWgt, itemSize, project, type, info['asset.entity'], path, icon_path,info['asset.cn_name']))
                sub_thread.setDaemon(True)
                sub_thread.start()
                sub_thread.join()

    def _addItems_CGT(self, listWgt,itemSize,project,type,role_name, path,icon_path, ch_name):
        item_data = self._itemDetail(project,type,role_name,path)
        item = QtWidgets.QListWidgetItem()
        item.setText(role_name + '   /   ' + ch_name)  # 设置文字
        item.setData(QtCore.Qt.UserRole, item_data)  # 设置信息
        icon = QtGui.QIcon()
        pixmap = QtGui.QPixmap(icon_path)  # 设置icon
        icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        listWgt.setIconSize(QtCore.QSize(itemSize, itemSize))
        item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
        listWgt.addItem(item)

    def _itemDetail(self, project,type,role_name,path):
        '''设置item信息'''
        item_data = {'hi_rig': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['rigFolder'], role_name, self.projectSetting()['rigFileHi'], self.projectSetting()['mayaFormat']),
                     'all_rig': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['rigFolder'], role_name, self.projectSetting()['rigFileAll'], self.projectSetting()['mayaFormat']),
                     'low_rig': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['rigFolder'], role_name, self.projectSetting()['rigFileLow'], self.projectSetting()['mayaFormat']),
                     'render': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['renderFolder'], role_name, self.projectSetting()['renderFile'], self.projectSetting()['mayaFormat']),
                     'mod': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['modelFolder'], role_name, self.projectSetting()['modelFile'], self.projectSetting()['mayaFormat']),
                     'xgen': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['xgenFileFolder'], role_name, self.projectSetting()['xgenFile'], self.projectSetting()['mayaFormat']),
                     'icon': ('{0}/{1}/{2}/{3}.{4}').format(path, role_name, self.projectSetting()['iconFolder'], role_name, self.projectSetting()['iconFormat']),
                     'AD': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['assembly'], role_name, self.projectSetting()['assemblyFile'], self.projectSetting()['mayaFormat']),
                     'OAT': ('{0}/{1}/{2}/{3}_{4}.{5}').format(path, role_name, self.projectSetting()['rigFolder'], role_name, 'OAT', self.projectSetting()['mayaFormat']),
                     'role_name': role_name,
                     'project': project,
                     'type': type}
        return (item_data)