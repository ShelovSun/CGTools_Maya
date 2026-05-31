# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.6 (tags/v3.8.6:db45529, Sep 23 2020, 15:37:30) [MSC v.1927 32 bit (Intel)]
# Embedded file name: G:\PyCharm\AssetsManager\v1.2.0\utils\jsonHelper.py
# Compiled at: 2016-08-01 15:12:25
import json, shutil, os

def writeDictToFile(filePath, dataDict):
    result = False
    try:
        f = open(filePath, 'w')
        f.write(json.dumps(dataDict, ensure_ascii=False, indent=4))
        f.close()
        result = True
    except:
        result = False

    return result


def readDictFromFile(filePath):
    f = open(filePath, 'r')
    data = f.read()
    f.close()
    decode_json = {}
    try:
        decode_json = json.loads(data)
        return decode_json
    except:
        print ('read json data file error!')
        return

    return