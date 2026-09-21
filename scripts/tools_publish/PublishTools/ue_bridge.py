#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CGTools Maya -> Unreal Editor 动作发布通知客户端。

这个模块只负责一件事：当 Maya 成功导出动作 FBX 后，把动作信息发送给本机正在
运行的 Unreal Editor。UE 端负责监听、弹出“是否导入”窗口，以及真正执行 FBX
动画导入。

为什么由 Maya 主动连接 UE
==========================

Maya 已经准确知道哪个 FBX 刚刚发布成功，因此不应该让 UE 持续扫描动作目录，
尤其不应该扫描 ``Y:`` 网络盘。UE 插件应当在 localhost 上使用阻塞式 Socket
等待；空闲时监听线程由操作系统挂起，不占用 UE 主线程，也不需要 Tick 或目录轮询。

传输协议（UE C++ 插件必须按此实现）
====================================

1. 传输层：TCP，只用于同一台工作站上的进程通信。
2. UE 服务端必须绑定 ``127.0.0.1:19821``，不要绑定 ``0.0.0.0``，避免把没有
   身份认证的导入接口暴露到局域网。
   当前约定一台工作站只运行一个 UE Bridge 服务端；第二个 UE 实例端口绑定失败
   时应只记录提示，不要影响 UE 启动。
3. 每条消息是一个“长度头 + JSON 正文”的二进制帧：

   - 前 4 字节：无符号 32 位整数，网络字节序（big-endian），表示 JSON 正文的
     UTF-8 字节数；对应 Python ``struct.pack("!I", length)``。
   - 后续 N 字节：UTF-8 编码的 JSON；不是 wchar/TCHAR 字节，也不以 ``\\0``
     或换行结尾。
   - TCP 不保留消息边界。UE 端必须循环 ``Recv``，先收满 4 字节，再按长度循环
     收满 N 字节，不能假设一次 ``Recv`` 就拿到完整消息。
   - 当前最大正文为 1 MiB。超过限制应拒绝，避免错误长度造成异常内存分配。

4. Maya 请求正文示例：

   {
     "protocol": "cgtools-ue-bridge",
     "protocol_version": 1,
     "message_type": "action_published",
     "event_id": "4c0f...-uuid",
     "sent_at_utc": "2026-09-14T08:30:00.123Z",
     "source": {
       "application": "Autodesk Maya",
       "maya_version": "2022",
       "publish_tool_version": "2.0.2",
       "host_name": "ANIM-PC-01",
       "process_id": 1234
     },
     "project_names": ["GOF"],
     "action_count": 1,
     "actions": [
       {
         "project_name": "GOF",
         "asset_type": "Characters",
         "asset_name": "Nujian",
         "action_name": "Run",
         "fbx_path": "Y:/.../Nujian_Run.fbx",
         "maya_file_path": "Y:/.../Nujian_Run.ma",
         "reference_node": "Nujian_hi_rigRN",
         "reference_path": "Y:/.../Nujian_hi_rig.ma",
         "namespace": "Nujian_hi_rig",
         "start_frame": 1,
         "end_frame": 100
       }
     ]
   }

5. UE 收到并验证消息、且成功放入自己的主线程待处理队列后，应立即回复 ACK。
   ACK 只表示“UE 已接收并准备弹窗”，不表示用户已经点了“是”，也不表示导入
   已经完成。不要等用户操作后才回复，否则 Maya 会在 ACK 超时前短暂等待。

   {
     "protocol": "cgtools-ue-bridge",
     "protocol_version": 1,
     "message_type": "ack",
     "reply_to_event_id": "请求中的 event_id",
     "accepted": true,
     "message": "queued"
   }

6. ACK 也必须使用同样的 4 字节长度头。若消息无效，UE 可以回复
   ``accepted: false`` 并在 ``message`` 中解释原因。
   一条 TCP 连接只承载“一条 action_published 请求 + 一条 ACK”；Maya 收到 ACK
   或超时后会关闭连接。UE 服务端随后继续 ``Accept`` 下一次发布连接。
7. UE 应以 ``event_id`` 去重。Maya 当前不会自动重试，但去重可以防止未来增加
   重试机制或人为重复发送时连续弹出相同窗口。
8. UE Socket 线程不得直接调用 Slate、AssetTools 或 Python/Editor API。验证并 ACK
   后，应把消息投递到 Game Thread，再在 Game Thread 弹窗和导入资产。

兼容性与失败策略
================

- 本模块仅使用 Python 3.7 标准库，兼容 Maya 2022 自带的 CPython 3.7.7。
- UE 未启动、插件未启用、端口不同或 ACK 超时，都不能让动作发布失败。
- 调用是同步的，但只连接 localhost，并使用很短的连接/ACK 超时；最坏情况下只
  会给发布收尾增加不到一秒的等待，不会出现长期卡住 Maya 的情况。
- 当前协议不包含 UE Skeleton 和 Content Browser 目标目录。这两项应由 UE 插件
  根据 ``project_name + asset_type + asset_name`` 的项目配置解析，不应由 Maya
  猜测。
- 同一轮发布多个动作时只发送一条批量消息，UE 应只弹一次窗口。
"""

from __future__ import absolute_import

import datetime
import json
import os
import socket
import struct
import uuid


PROTOCOL_NAME = "cgtools-ue-bridge"
PROTOCOL_VERSION = 1
MESSAGE_TYPE_ACTION_PUBLISHED = "action_published"
MESSAGE_TYPE_ACK = "ack"
VALID_ACTION_ASSET_TYPES = ("Characters", "Props")

# 端口是 Maya 与 UE 插件之间的协议常量。若工作站确实发生端口冲突，可以同时给
# Maya 和 UE 进程设置 CGTOOLS_UE_BRIDGE_PORT；两端必须使用相同值。
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 19821
PORT_ENV_NAME = "CGTOOLS_UE_BRIDGE_PORT"

# 连接只走本机回环地址。正常情况下 UE 未监听会立刻返回 ConnectionRefused；
# 这里仍设置上限，确保任何异常网络状态都不会长时间阻塞 Maya UI。
CONNECT_TIMEOUT_SECONDS = 0.20
ACK_TIMEOUT_SECONDS = 0.35
MAX_JSON_BYTES = 1024 * 1024


def _configured_port():
    """读取可选端口环境变量；无效值安全回退到协议默认端口。"""
    value = os.environ.get(PORT_ENV_NAME)
    if not value:
        return DEFAULT_PORT
    try:
        port = int(value)
    except (TypeError, ValueError):
        return DEFAULT_PORT
    return port if 1 <= port <= 65535 else DEFAULT_PORT


def _utc_timestamp():
    """返回固定为 UTC、带毫秒和 Z 后缀的 ISO-8601 时间。"""
    return datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"


def _forward_slashes(path):
    """让 Windows 路径在 JSON 和 UE 日志中保持统一；不改变盘符或 UNC 含义。"""
    return path.replace("\\", "/") if path else ""


def _json_frame(message):
    """把字典编码为协议帧：4 字节 big-endian 长度 + UTF-8 JSON。"""
    body = json.dumps(
        message,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    if len(body) > MAX_JSON_BYTES:
        raise ValueError("UE bridge JSON is larger than {0} bytes".format(MAX_JSON_BYTES))
    return struct.pack("!I", len(body)) + body


def _recv_exact(connection, byte_count):
    """从 TCP 流精确读取 byte_count 字节；连接提前关闭时抛出 IOError。"""
    chunks = []
    remaining = byte_count
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise IOError("UE bridge connection closed before a complete frame was received")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def _recv_json_frame(connection):
    """读取并解析一条 ACK 帧。UE C++ 端读取请求时应使用完全相同的步骤。"""
    header = _recv_exact(connection, 4)
    body_size = struct.unpack("!I", header)[0]
    if body_size <= 0 or body_size > MAX_JSON_BYTES:
        raise ValueError("Invalid UE bridge frame length: {0}".format(body_size))
    body = _recv_exact(connection, body_size)
    return json.loads(body.decode("utf-8"))


def _normalize_action(action):
    """复制并规范化一个动作记录，避免修改发布工具持有的原字典。"""
    normalized = dict(action)
    for key in ("fbx_path", "maya_file_path", "reference_path"):
        normalized[key] = _forward_slashes(normalized.get(key))
    return normalized


def build_action_published_message(actions, source_context=None, event_id=None):
    """构造 ``action_published`` 消息，但不进行网络通信。

    该函数保持独立，方便在 Maya 外做协议测试，也方便 UE 插件开发者用固定 JSON
    样本验证 C++ 反序列化。每个动作必须包含 ``asset_type``、``asset_name``、
    ``action_name`` 和 ``fbx_path``；当前由 PublishTool 在调用前保证 FBX 已成功
    导出，且 ``asset_type`` 只能是 ``Characters`` 或 ``Props``。
    """
    normalized_actions = [_normalize_action(action) for action in actions]
    if not normalized_actions:
        raise ValueError("At least one published action is required")

    for action in normalized_actions:
        asset_type = action.get("asset_type")
        if asset_type not in VALID_ACTION_ASSET_TYPES:
            raise ValueError(
                "action asset_type must be Characters or Props, got: {0}".format(asset_type)
            )
        for required_field in ("asset_name", "action_name", "fbx_path"):
            if not action.get(required_field):
                raise ValueError("action is missing required field: {0}".format(required_field))

    source = {
        "application": "Autodesk Maya",
        "host_name": socket.gethostname(),
        "process_id": os.getpid(),
    }
    if source_context:
        source.update(source_context)

    project_names = sorted(set(
        action.get("project_name")
        for action in normalized_actions
        if action.get("project_name")
    ))

    return {
        "protocol": PROTOCOL_NAME,
        "protocol_version": PROTOCOL_VERSION,
        "message_type": MESSAGE_TYPE_ACTION_PUBLISHED,
        "event_id": event_id or str(uuid.uuid4()),
        "sent_at_utc": _utc_timestamp(),
        "source": source,
        "project_names": project_names,
        "action_count": len(normalized_actions),
        "actions": normalized_actions,
    }


def _new_result(message, host, port):
    """所有通知结果使用稳定字段，PublishTool 不需要根据异常类型做判断。"""
    return {
        "status": "error",
        "sent": False,
        "acknowledged": False,
        "accepted": None,
        "event_id": message.get("event_id"),
        "host": host,
        "port": port,
        "message": "",
    }


def notify_actions_published(actions, source_context=None, host=None, port=None):
    """向 UE 发送一批已成功发布的动作，并短暂等待接收 ACK。

    返回值是普通字典，关键 ``status`` 值如下：

    - ``acknowledged``：UE 已接收并接受消息；接下来应在 UE 主线程弹窗。
    - ``rejected``：UE 收到消息但拒绝处理，原因位于 ``message``。
    - ``sent``：请求已经发出，但在短超时内没有收到合法 ACK。UE 仍可能已收到。
    - ``offline``：localhost 端口没有 UE 服务端监听。
    - ``error``：编码、协议或其它 Socket 错误。

    函数不会抛出 Socket 异常，也不会重试。尤其不要在这里等待用户完成 UE 弹窗；
    UE 应在消息入队后立即 ACK，让 Maya 发布流程及时结束。
    """
    host = host or DEFAULT_HOST
    port = port if port is not None else _configured_port()

    try:
        message = build_action_published_message(actions, source_context=source_context)
    except Exception as error:
        return {
            "status": "error",
            "sent": False,
            "acknowledged": False,
            "accepted": None,
            "event_id": None,
            "host": host,
            "port": port,
            "message": "Cannot build UE bridge message: {0}".format(error),
        }

    result = _new_result(message, host, port)
    connection = None
    try:
        connection = socket.create_connection((host, port), CONNECT_TIMEOUT_SECONDS)
        connection.settimeout(ACK_TIMEOUT_SECONDS)
        connection.sendall(_json_frame(message))
        result["sent"] = True

        try:
            acknowledgement = _recv_json_frame(connection)
        except socket.timeout:
            # 请求已经 sendall 成功。ACK 超时不能断言 UE 没收到，所以状态与 offline
            # 分开；同时不自动重试，避免 UE 已入队时产生重复弹窗。
            result["status"] = "sent"
            result["message"] = "Notification sent, but UE acknowledgement timed out"
            return result

        if acknowledgement.get("protocol") != PROTOCOL_NAME:
            raise ValueError("ACK protocol name does not match")
        if acknowledgement.get("protocol_version") != PROTOCOL_VERSION:
            raise ValueError("ACK protocol version does not match")
        if acknowledgement.get("message_type") != MESSAGE_TYPE_ACK:
            raise ValueError("Response is not an ACK message")
        if acknowledgement.get("reply_to_event_id") != message["event_id"]:
            raise ValueError("ACK event_id does not match the request")

        result["acknowledged"] = True
        result["accepted"] = bool(acknowledgement.get("accepted"))
        result["message"] = acknowledgement.get("message") or ""
        result["status"] = "acknowledged" if result["accepted"] else "rejected"
        return result

    except (ConnectionRefusedError, ConnectionResetError):
        result["status"] = "offline"
        result["message"] = "No Unreal Editor bridge is listening on {0}:{1}".format(host, port)
        return result
    except socket.timeout:
        # connect() 阶段超时说明没有可及时响应的 UE 服务；sendall 后的 ACK 超时已经
        # 在上面单独处理，因此这里按 offline 报告。
        result["status"] = "offline"
        result["message"] = "Unreal Editor bridge connection timed out"
        return result
    except OSError as error:
        result["status"] = "offline" if not result["sent"] else "error"
        result["message"] = "UE bridge socket error: {0}".format(error)
        return result
    except Exception as error:
        result["status"] = "error"
        result["message"] = "UE bridge protocol error: {0}".format(error)
        return result
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
