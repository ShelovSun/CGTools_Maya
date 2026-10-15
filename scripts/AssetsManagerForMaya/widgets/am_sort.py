#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""资产/场景的共同排序规则，与 UE 版的字段顺序一致。"""


def sort_value(value, column):
    """日期按整数比较，其他字段忽略大小写，空值使用统一的默认值。"""
    if column == 0:
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0
    return "" if value is None else str(value).lower()


def asset_sort_key(data, column):
    """表格第 7 列是备注(data[8])，data[7] 的缩略图路径不参与排序。"""
    data_index = 8 if column == 7 else column
    try:
        value = data[data_index]
    except (IndexError, TypeError):
        value = None
    return sort_value(value, column)
