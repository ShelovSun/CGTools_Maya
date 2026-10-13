#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""资产文件仍在 Assets 下，动作库单独存放在同项目的 Animations 下。"""

import posixpath


def action_library_path(asset_path, settings=None):
    """从资产目录、Rig 或 FBX 文件路径解析动作库目录，解析失败返回空字符串。

    例如 ``.../GOF/Assets/Characters/BaSiTeV4/FBX/BaSiTeV4.fbx`` 对应
    ``.../GOF/Animations/Characters/BaSiTeV4/Action``。
    保留源路径的盘符/网络共享及项目目录，只替换 assetFolder 所在的目录层级。
    旧版共享配置没有 animationFolder 时，也按新规范使用 Animations。
    """
    if not asset_path:
        return ""

    settings = settings or {}
    asset_folder = settings.get("assetFolder") or "Assets"
    animation_folder = settings.get("animationFolder") or "Animations"
    action_folder = settings.get("actionFolder") or "Action"
    path = posixpath.normpath(asset_path.replace("\\", "/"))
    parts = path.split("/")
    try:
        index = [part.lower() for part in parts].index(asset_folder.lower())
    except ValueError:
        return ""
    if len(parts) < index + 3:
        return ""

    parts[index] = animation_folder
    return "/".join(parts[:index + 3] + [action_folder])
