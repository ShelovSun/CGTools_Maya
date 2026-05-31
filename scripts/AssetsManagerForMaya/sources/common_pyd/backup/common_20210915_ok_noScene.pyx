#coding: utf8
#cython: boundscheck=False, wraparound=False, nonecheck=False

import os, sys,threading
import cython
from PySide2 import  QtWidgets, QtCore, QtGui
sys.path.append('C:\\CgTeamWork_v6.2\\bin\\base')
import cgtw2
t_tw = cgtw2.tw()
from . import scriptsPath


@cython.boundscheck(False)
@cython.wraparound(False)


def test():
    print("Common is working in Cython !")

cpdef projectSetting():
    sys.path.append(scriptsPath)
    from utils import jsonHelper
    cdef dict data
    data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % scriptsPath)  
    return data

cpdef _listWidgetAddItems_CGT(listWgt,int itemSize,str project,str type):
    cdef str tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
    cdef str path = str(('{0}/{1}/{2}/{3}').format(projectSetting()['rootPath'], project, projectSetting()['assetFolder'],type))
    cdef str TW_proj = str(projectSetting()['projectdiction'][project])
    cdef str asset,assetmaya,assetstapy,assetentity,assetcnname
    cdef list t_asset_ids = t_tw.info.get_id(TW_proj, 'asset',[['asset.maya', '=', u"完成"], 'and', ['asset.assetstapy', '=', type]])
    cdef list TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.cn_name'])
    cdef str icon_path
    cdef dict info
    for info in TW_dictionInfo:
        icon_path = ('{0}/{1}/Assets/{2}/{3}.png').format(tempPath, project, type, info['asset.entity'])
        if QtCore.QFileInfo(icon_path).exists() is False:
            icon_path = ('{0}/{1}/{2}/{1}.png').format(path, info['asset.entity'], projectSetting()['iconFolder'])
            if QtCore.QFileInfo(icon_path).exists() is False:
                icon_path = str(projectSetting()['defaultIcon'])
        sub_thread = threading.Thread(target=_addItems_CGT,
                                      args=(listWgt, itemSize, project, type, info['asset.entity'], path, icon_path, info['asset.cn_name']))
        sub_thread.setDaemon(True)
        sub_thread.start()
        sub_thread.join()

def _listWidgetAddItems_CGT_Search(listWgt,int itemSize,str project,str type,unicode keyWords):
    cdef str tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
    cdef str path = ('{0}/{1}/{2}/{3}').format(projectSetting()['rootPath'], project, projectSetting()['assetFolder'],type)
    cdef str TW_proj = str(projectSetting()['projectdiction'][project])
    cdef list t_asset_ids = t_tw.info.get_id(TW_proj, 'asset',[['asset.maya', '=', u"完成"], 'and', ['asset.assetstapy', '=', type]])
    cdef list TW_dictionInfo = t_tw.info.get(TW_proj, 'asset', t_asset_ids, ['asset.entity', 'asset.cn_name'])
    cdef str icon_path
    cdef dict info
    for info in TW_dictionInfo:
        if info['asset.entity'].lower().find(keyWords.lower()) != -1 or info['asset.cn_name'].find(keyWords) != -1:
            icon_path = ('{0}/{1}/Assets/{2}/{3}.png').format(tempPath, project, type, info['asset.entity'])
            if QtCore.QFileInfo(icon_path).exists() is False:
                icon_path = ('{0}/{1}/{2}/{1}.png').format(path, info['asset.entity'],projectSetting()['iconFolder'])
                if QtCore.QFileInfo(icon_path).exists() is False:
                    icon_path = projectSetting()['defaultIcon']
            sub_thread = threading.Thread(target=_addItems_CGT,
                                          args=(listWgt, itemSize, project, type, info['asset.entity'], path, icon_path,info['asset.cn_name']))
            sub_thread.setDaemon(True)
            sub_thread.start()
            sub_thread.join()

cpdef _addItems_CGT(listWgt,int itemSize,str project,str type,unicode role_name,str path,str icon_path,unicode ch_name):
    item_data = _itemDetail(project,type,role_name,path)
    item = QtWidgets.QListWidgetItem()
    item.setText(role_name + '   /   ' + ch_name) 
    item.setData(QtCore.Qt.UserRole, item_data)  
    icon = QtGui.QIcon()
    pixmap = QtGui.QPixmap(icon_path)  
    icon.addPixmap(pixmap, QtGui.QIcon.Normal, QtGui.QIcon.Off)
    item.setIcon(icon)
    listWgt.setIconSize(QtCore.QSize(itemSize, itemSize))
    item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
    listWgt.addItem(item)

cpdef _itemDetail(str project,str type,unicode role_name,str path):
    cdef dict item_data
    item_data = {'role_name': role_name,
                 'project': project,
                 'type': type}
    return (item_data)