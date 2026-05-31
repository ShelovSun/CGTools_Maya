#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jsonHelper Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import json
import os


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
    if os.path.isfile(filePath):
        f = open(filePath, 'rb')
        data = f.read()
        f.close()
        decode_json = {}
        try:
            decode_json = json.loads(data)
            return decode_json
        except Exception as e:
            print('read %s data file error:%s!' % (filePath, e))
            return None
    else:
        print("there is not %s" % filePath)
    return None
