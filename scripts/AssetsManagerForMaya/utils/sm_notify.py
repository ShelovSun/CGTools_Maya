#!/usr/bin/env python
# -*- coding: utf-8 -*-
# sm_notify —— Maya 端向独立版 ShotManager 发送"资产提交审核"广播消息。
#
# 复用独立版 ShotManager 现成的中心服务器广播通讯系统:
#   服务器 10.0.203.34:12345 (纯 TCP; 与 PostgreSQL 5432 无关)。
#   任何进程连上 -> 发登录帧(用户名) -> 发业务帧, 服务器即原样广播给所有在线客户端。
#   协议: [10 字节左对齐长度头][utf-8 载荷]; 载荷 6 段 code|sender|db|shot|task|link。
#
# 本模块只用标准库 socket (零 PySide2 / psycopg2 依赖), 在后台线程发送、全程静默:
#   连不上 / 超时 / 服务器没起 都不会影响 Maya 发布主流程, 也不弹任何错误框。
#
# 接收端约定见独立版 ShotManager.py 的 ASSET_REVIEW_TAG / split_msg / is_msg_need_to_show:
#   码 1002 且 shot 段 == "资产提交" 时, 定向弹给固定审核人(ShotManager 里的 ASSET_REVIEWER)。

import time
import socket
import threading

# 消息服务器地址 (与独立版 bin/sm_client.py 一致)
IP = "10.0.203.34"
PORT = 12345
HEADER_LENGTH = 10

# 资产提交识别标记 —— 必须与独立版 ShotManager.ASSET_REVIEW_TAG 完全一致!
# 独立版据此把这条 1002 消息识别为"资产审核", 定向弹给 ASSET_REVIEWER。
ASSET_REVIEW_TAG = u"资产提交"

# 资产提交复用的消息码 (独立版 split_msg / is_msg_need_to_show 识别 1002)
ASSET_REVIEW_CODE = "1002"


def _frame(text):
    """ 打一帧: [10 字节左对齐长度头][utf-8 载荷]。 """
    body = text.encode("utf-8")
    header = "{0:<{1}}".format(len(body), HEADER_LENGTH).encode("utf-8")
    return header + body


def _clean(value):
    """ 字段值里的 '|' 会破坏 6 段解析, 统一替换为 '/'。 """
    return str(value).replace("|", "/")


def _send(sender, db, asset, path, timeout):
    """ 同步发送: 连接 -> 登录帧 -> 业务帧 -> 关闭。异常向上抛给 run() 静默处理。 """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((IP, PORT))
        # 登录帧: 服务器把第一帧当用户名(独立版忽略它, 仅供服务器识别连接)
        sock.sendall(_frame(_clean(sender)))
        # 业务帧: 1002|提交者|项目db|资产提交|资产名|真实路径
        payload = "{0}|{1}|{2}|{3}|{4}|{5}".format(
            ASSET_REVIEW_CODE, _clean(sender), _clean(db),
            ASSET_REVIEW_TAG, _clean(asset), _clean(path))
        sock.sendall(_frame(payload))
        # 短暂停留确保数据 flush 后再关闭 (避免 close 竞态吃掉未发出的帧)
        time.sleep(0.2)
    finally:
        try:
            sock.close()
        except Exception:
            pass


def notify_asset_published(sender, db, asset, path, timeout=3.0):
    """ 在后台线程发一条"资产提交审核"广播, 全程静默失败, 立即返回、不阻塞 Maya。

    :param sender: 提交者(显示用), 一般传当前登录美术师名
    :param db:     项目代号(显示用)
    :param asset:  资产名(显示用)
    :param path:   发布真实路径(接收端面板可点击打开)
    :param timeout: socket 超时秒数
    """
    def run():
        try:
            _send(sender, db, asset, path, timeout)
        except Exception as e:
            print("[sm_notify] 通知 ShotManager 失败(已忽略):", e)

    threading.Thread(target=run, name="sm_notify", daemon=True).start()
