#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json


def am_TempPath():
    path = os.getenv('APPDATA') or os.getenv('HOME')
    TempPath = os.path.join(path, "AssetsManagerTemp")
    if not os.path.exists(TempPath):
        os.mkdir(TempPath)
    return TempPath


def sm_TempPath():
    path = os.getenv('APPDATA') or os.getenv('HOME')
    TempPath = os.path.join(path, "ShotManagerTemp")
    # TEMP = "{}/ShotManagerTemp".format(os.environ.get('APPDATA')) or os.getenv('HOME')
    if not os.path.exists(TempPath):
        os.mkdir(TempPath)
    return TempPath


def projectSetting():
    Json = 'config/projectSetting.json'
    if os.path.exists(Json):
        f = open(Json, 'rb')
        data = f.read()
        f.close()
        try:
            decode_json = json.loads(data)
            return decode_json
        except Exception as e:
            print('read %s data file error:%s!' % (Json, e))
            return None
    else:
        print("there is not %s" % Json)
        return None


