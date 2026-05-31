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


cpdef projectSetting():
    sys.path.append(scriptsPath)
    from utils import jsonHelper
    cdef dict data
    data = jsonHelper.readDictFromFile('%s/config/projectSetting.json' % scriptsPath)  
    return data

cpdef _listItems_CGT(str tab,str project,str type,str asset,str assetmaya,str assetstapy,str assetentity,str assetcnname,unicode keyWords):
    cdef str TW_proj = str(projectSetting()['projectdiction'][project])
    cdef list t_asset_ids = t_tw.info.get_id(TW_proj, asset,[[assetmaya, '=', u"完成"], 'and', [assetstapy, '=', type]])
    cdef list TW_dictionInfo = t_tw.info.get(TW_proj, asset, t_asset_ids, [assetentity,assetcnname])
    cdef dict info
    cdef list list_text = []
    for info in TW_dictionInfo:
        if info[assetentity].lower().find(keyWords.lower()) != -1 or info[assetcnname].find(keyWords) != -1:
            list_text.append(info[assetentity] + '   /   ' + info[assetcnname])
    return list_text

cpdef _listItemsIcon_CGT(str tab,str project,str type,str asset,str assetmaya,str assetstapy,str assetentity,str assetcnname,unicode keyWords):
    # cdef str tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
    cdef str path = ('{0}/{1}/{2}/{3}').format(projectSetting()['rootPath'], project, tab, type)
    cdef str TW_proj = str(projectSetting()['projectdiction'][project])
    cdef list t_asset_ids = t_tw.info.get_id(TW_proj, asset,[[assetmaya, '=', u"完成"], 'and', [assetstapy, '=', type]])
    cdef list TW_dictionInfo = t_tw.info.get(TW_proj, asset, t_asset_ids, [assetentity,assetcnname])
    cdef str icon_path
    cdef dict info
    cdef dict list_dict = {}
    for info in TW_dictionInfo:
        if info[assetentity].lower().find(keyWords.lower()) != -1 or info[assetcnname].find(keyWords) != -1:
            # icon_path = ('{0}/{1}/{2}/{3}/{4}.png').format(tempPath, project, tab, type, info[assetentity])
            # if QtCore.QFileInfo(icon_path).exists() is False:
            icon_path = ('{0}/{1}/{2}/{1}.png').format(path, info[assetentity], projectSetting()['iconFolder'])
            if QtCore.QFileInfo(icon_path).exists() is False:
                icon_path = "%sicon/Default.png" % scriptsPath
            name = info[assetentity] + '   /   ' + info[assetcnname]
            list_dict.update({name:icon_path})
    return list_dict

cpdef _listWidgetAddItems_icon(listWgt, str tab, str project, str type, unicode keyWords):
    cdef dict item_data
    cdef list itemsList
    cdef dict itemsDict
    if tab == 'Assets':
        itemsDict = _listItemsIcon_CGT('Assets', project, type, 'asset', 'asset.maya', 'asset.assetstapy', 'asset.entity', 'asset.cn_name', keyWords)
    else:
        if type != "Map":
            itemsDict = _listItemsIcon_CGT('Scenes', project, type, 'scenes', 'scenes.maya', 'scenes.scenesassetstype', 'scenes.entity', 'scenes.assetsnamecn', keyWords)
        else:
            itemsDict = _listItemsIcon_CGT('Scenes', project, type, 'map', 'map.maya', 'map.type', 'map.entity', 'map.mapnamecn', keyWords)
    itemsList = itemsDict.keys()
    for list in itemsList:
        item_data = {'role_name':list.split(u'   /   ')[0], 'project':project, 'type':type, 'iconpath':itemsDict[list], 'iconloaded':False}
        item = QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.UserRole, item_data)
        item.setText(list.replace('   /   ','\n'))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("%s/icon/blank_ch.png" % scriptsPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        listWgt.addItem(item)

cpdef _listWidgetAddItems_list(listWgt, str tab, str project, str type, unicode keyWords):
    cdef dict item_data
    cdef list itemsList
    cdef dict itemsDict
    if tab == 'Assets':
        itemsDict = _listItemsIcon_CGT('Assets', project, type, 'asset', 'asset.maya', 'asset.assetstapy', 'asset.entity', 'asset.cn_name', keyWords)
    else:
        if type != "Map":
            itemsDict = _listItemsIcon_CGT('Scenes', project, type, 'scenes', 'scenes.maya', 'scenes.scenesassetstype', 'scenes.entity', 'scenes.assetsnamecn', keyWords)
        else:
            itemsDict = _listItemsIcon_CGT('Scenes', project, type, 'map', 'map.maya', 'map.type', 'map.entity', 'map.mapnamecn', keyWords)
    itemsList = itemsDict.keys()
    for list in itemsList:
        item_data = {'role_name': list.split(u'   /   ')[0], 'project': project, 'type': type, 'iconpath':itemsDict[list]}
        item = QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.UserRole, item_data)
        item.setText(list)
        item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        listWgt.addItem(item)

cpdef _update_visibleIcons(listWgt, int showedItemNum, int pointNum):
    cdef int updatedItemNum = 0
    for i in range(showedItemNum, pointNum):
        item = listWgt.item(i)
        itemdata = item.data(QtCore.Qt.UserRole)
        print(itemdata['iconloaded'])
        if itemdata['iconloaded']:
            print("icon is loaded")
            return
        else:
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(itemdata['iconpath']), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            item.setIcon(icon)
            itemdata['iconloaded'] = True
            item.setData(QtCore.Qt.UserRole, itemdata)
            updatedItemNum += 1
            showedItemNum += 1
    return (updatedItemNum, showedItemNum)

cpdef _listWidgetAddItems_CGT(listWgt, str tab, str project, str type, str asset, str assetmaya, str assetstapy, str assetentity, str assetcnname, unicode keyWords, bint isList):
    cdef str tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('TEMP'))
    cdef str TW_proj = str(projectSetting()['projectdiction'][project])
    cdef list t_asset_ids = t_tw.info.get_id(TW_proj, asset,[[assetmaya, '=', u"完成"], 'and', [assetstapy, '=', type]])
    cdef list TW_dictionInfo = t_tw.info.get(TW_proj, asset, t_asset_ids, [assetentity,assetcnname])
    cdef str icon_path
    cdef dict info
    cdef dict item_data
    if isList:
        for info in TW_dictionInfo:
            if info[assetentity].lower().find(keyWords.lower()) != -1 or info[assetcnname].find(keyWords) != -1:
                item_data = {'role_name': info[assetentity],'project': project,'type': type}
                item = QtWidgets.QListWidgetItem()
                item.setText(info[assetentity] + '   /   ' + info[assetcnname]) 
                item.setData(QtCore.Qt.UserRole, item_data)  
                item.setTextAlignment(QtCore.Qt.AlignLeft)
                listWgt.addItem(item)
    else:
        for info in TW_dictionInfo:
            if info[assetentity].lower().find(keyWords.lower()) != -1 or info[assetcnname].find(keyWords) != -1:
                icon_path = ('{0}/{1}/{2}/{3}/{4}.png').format(tempPath, project, tab, type, info[assetentity])
                if QtCore.QFileInfo(icon_path).exists() is False:
                    icon_path = ('{0}/{1}/{2}/{3}/{4}/Icon/{4}.png').format(projectSetting()['rootPath'], project, tab, type, info[assetentity])
                    if QtCore.QFileInfo(icon_path).exists() is False:
                        icon_path = str("%s/icon/Default.png" % scriptsPath)
                item_data = {'role_name': info[assetentity],'project': project,'type': type}
                item = QtWidgets.QListWidgetItem()
                item.setText(info[assetentity] + '\n' + info[assetcnname]) 
                item.setData(QtCore.Qt.UserRole, item_data)  
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap("%s/icon/blank_ch.png" % scriptsPath), QtGui.QIcon.Normal, QtGui.QIcon.Off)
                item.setIcon(icon)
                item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
                listWgt.addItem(item)