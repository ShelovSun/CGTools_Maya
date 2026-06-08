#!/usr/bin/env python
# -*- coding: utf-8 -*-
# jsonHelper Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import json
import os


def writeDictToFile(filePath, dataDict):
    result = False
    try:
        # 显式 UTF-8：ensure_ascii=False 会写出中文原字，若用平台默认编码
        # (中文 Windows 为 GBK) 写出 GBK 字节，读取端按 UTF-8 解码就会报错。
        with open(filePath, 'w', encoding='utf-8') as f:
            f.write(json.dumps(dataDict, ensure_ascii=False, indent=4))
        result = True
    except:
        result = False

    return result


def readDictFromFile(filePath):
    if os.path.isfile(filePath):
        with open(filePath, 'rb') as f:
            raw = f.read()
        # 优先 UTF-8(含 BOM)，失败再退回 GBK——兼容历史上被按平台默认编码
        # (中文 Windows=GBK) 写出的旧文件；读到后下次写入即归一化为 UTF-8。
        for enc in ('utf-8-sig', 'gbk'):
            try:
                return json.loads(raw.decode(enc))
            except (UnicodeDecodeError, ValueError):
                continue
        print('read %s data file error: cannot decode as utf-8/gbk!' % filePath)
        return None
    else:
        print("there is not %s" % filePath)
    return None
