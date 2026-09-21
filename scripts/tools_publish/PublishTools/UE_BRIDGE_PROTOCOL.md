# CGTools Maya → Unreal Editor 动作发布通知协议

本文档供 UE C++ Editor 插件实现方使用。Maya 客户端的可执行协议实现位于同目录
的 `ue_bridge.py`，动作发布接入点位于 `PublishTool.py` 的
`_notify_unreal_actions()`。如果文档与代码有差异，以相同
`PROTOCOL_VERSION` 下的 `ue_bridge.py` 为准。

## 目标与边界

Maya 成功发布一批动作 FBX 后，主动通知同一台工作站上已经打开的 Unreal
Editor。UE 收到通知后弹出一次确认窗口，用户选择“是”时才执行动画导入。

该协议只负责“发布事件传递”，不负责以下内容：

- Maya 不决定 UE Skeleton；
- Maya 不决定 UE `/Game/...` 目标目录；
- Maya 不等待用户在 UE 中完成导入；
- UE 离线不能导致 Maya 发布失败；
- 当前协议不用于局域网远程控制，因此没有身份认证。

Skeleton 和目标目录应由 UE 插件根据
`project_name + asset_type + asset_name` 查询自己的项目配置。不要在 UE 端只根据
FBX 文件名猜测资产。

## 端点

- 传输：TCP
- 地址：`127.0.0.1`
- 默认端口：`19821`
- Maya 端端口环境变量：`CGTOOLS_UE_BRIDGE_PORT`
- 最大 JSON 正文：1 MiB

UE 插件必须只绑定回环地址 `127.0.0.1`，不要绑定 `0.0.0.0`。如果 UE 插件允许
配置端口，其值必须与 Maya 进程的 `CGTOOLS_UE_BRIDGE_PORT` 相同。

协议 v1 约定一台工作站只有一个活动的 UE Bridge 服务端。第二个 UE 实例无法绑定
同一端口时，应记录清楚的 Editor 日志并禁用该实例的监听，但不能影响 UE 启动。
如果未来必须同时定位多个 UE 实例，需要增加实例发现和端口注册机制，建议作为新
协议版本处理，不要让多个进程竞争读取同一个端口。

## 二进制分帧

TCP 是字节流，没有消息边界。请求和 ACK 都使用以下格式：

```text
+------------------------------+----------------------------------+
| 4-byte uint32, big-endian     | N-byte UTF-8 JSON               |
| JSON 正文字节数 N             | 无 BOM、无结尾 NUL、无结尾换行  |
+------------------------------+----------------------------------+
```

UE C++ 服务端必须：

1. 循环接收，直到收满 4 字节；
2. 按网络字节序解析 `uint32`；
3. 验证 `1 <= N <= 1048576`；
4. 再循环接收，直到收满 N 字节；
5. 按 UTF-8 转换并反序列化 JSON。

不要假设一次 `FSocket::Recv` 能返回完整的头或正文。客户端关闭连接且数据不足时，
应丢弃这一帧。

每个 TCP 连接只包含一条 `action_published` 请求和一条 ACK。Maya 收到 ACK 或等待
超时后会关闭连接；UE 服务端关闭本次 client socket 后，应继续 `Accept` 下一次
发布连接。

## action_published 请求

```json
{
  "protocol": "cgtools-ue-bridge",
  "protocol_version": 1,
  "message_type": "action_published",
  "event_id": "349e9621-a586-4d5c-b960-a9537e692cf9",
  "sent_at_utc": "2026-09-14T08:30:00.123Z",
  "source": {
    "application": "Autodesk Maya",
    "host_name": "ANIM-PC-01",
    "process_id": 1234,
    "maya_version": "2022",
    "publish_tool_version": "2.0.2"
  },
  "project_names": ["GOF"],
  "action_count": 1,
  "actions": [
    {
      "project_name": "GOF",
      "asset_type": "Characters",
      "asset_name": "Nujian",
      "action_name": "Run",
      "fbx_path": "Y:/MCCProject/GOF/Assets/Characters/Nujian/Action/Nujian_Run.fbx",
      "fbx_size_bytes": 1234567,
      "maya_file_path": "Y:/MCCProject/GOF/Assets/Characters/Nujian/Action/Nujian_Run.ma",
      "reference_node": "Nujian_hi_rigRN",
      "reference_path": "Y:/MCCProject/GOF/Assets/Characters/Nujian/Rig/Nujian_hi_rig.ma",
      "namespace": "Nujian_hi_rig",
      "start_frame": 1,
      "end_frame": 100
    }
  ]
}
```

### 顶层字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `protocol` | string | 固定为 `cgtools-ue-bridge` |
| `protocol_version` | number | 当前为 `1`；不支持时应拒绝并解释 |
| `message_type` | string | 当前动作通知固定为 `action_published` |
| `event_id` | string | UUID；UE 必须以此去重 |
| `sent_at_utc` | string | UTC ISO-8601，仅用于日志和过期策略 |
| `source` | object | Maya/发布工具/工作站诊断信息 |
| `project_names` | string[] | 本批动作涉及的 CGTools 项目，可用于过滤 UE 工程 |
| `action_count` | number | 应与 `actions.Num()` 一致 |
| `actions` | object[] | 本轮真实导出成功的 FBX；一批只弹一次窗口 |

### action 字段

| 字段 | 类型 | UE 用途 |
|---|---|---|
| `project_name` | string/null | 选择项目配置；无法解析时可能为 null |
| `asset_type` | string | 必需；只允许 `Characters` 或 `Props` |
| `asset_name` | string | 查找 Skeleton 与目标动画目录 |
| `action_name` | string | 弹窗显示及预期 UE 资产名 |
| `fbx_path` | string | 必需；需要导入的动作 FBX |
| `fbx_size_bytes` | number/null | 诊断字段；Maya 发送前读取的大小 |
| `maya_file_path` | string | 诊断/回溯源文件，不参与 UE 导入 |
| `reference_node` | string | Maya 诊断信息 |
| `reference_path` | string | 原绑定 Reference 路径 |
| `namespace` | string | Maya 导出使用的角色命名空间 |
| `start_frame` | number | 发布起始帧 |
| `end_frame` | number | 发布结束帧 |

协议 v1 中，UE 至少必须验证：

- 协议名、版本、消息类型合法；
- `event_id` 非空；
- `actions` 非空且 `action_count` 一致；
- 每个动作的 `asset_type` 是 `Characters` 或 `Props`；
- 每个动作的 `asset_name`、`action_name` 和 `fbx_path` 非空；
- 当前 UE 工程与 `project_names` 是否匹配；
- 消息是否已经按 `event_id` 处理过。

路径使用正斜杠，以保持 JSON、Windows 和 UE 日志一致。UE 仍需检查本机是否可以访问
对应盘符；若工作站无法看到 Maya 使用的 `Y:` 映射盘，应在 UE 项目配置中转换为
UNC 路径。

## ACK 响应

UE 验证消息并成功放入主线程队列后，应立即发送：

```json
{
  "protocol": "cgtools-ue-bridge",
  "protocol_version": 1,
  "message_type": "ack",
  "reply_to_event_id": "349e9621-a586-4d5c-b960-a9537e692cf9",
  "accepted": true,
  "message": "queued"
}
```

ACK 使用相同的 4 字节长度头。`reply_to_event_id` 必须原样复制请求 `event_id`。

`accepted: true` 只表示 UE 接收并排队成功，不代表：

- 用户已经选择导入；
- FBX 已经导入；
- Skeleton 已成功解析；
- `.uasset` 已经保存。

不要等用户关闭模态窗口再发送 ACK。Maya 只等待约 0.35 秒；延迟 ACK 会让 Maya
显示“已发送但未收到 ACK”，而且为了避免重复弹窗，Maya不会自动重试。

拒绝示例：

```json
{
  "protocol": "cgtools-ue-bridge",
  "protocol_version": 1,
  "message_type": "ack",
  "reply_to_event_id": "349e9621-a586-4d5c-b960-a9537e692cf9",
  "accepted": false,
  "message": "project does not match the current Unreal project"
}
```

## UE 插件线程模型

推荐实现为仅 Editor 加载的 C++ 插件：

```text
Socket 接收线程
    ├─ 阻塞等待 127.0.0.1:19821
    ├─ 读取并验证一条完整帧
    ├─ 按 event_id 去重
    ├─ 放入线程安全队列
    └─ 立即返回 ACK
                    ↓
        AsyncTask(GameThread, ...)
                    ↓
          显示一次 Yes/No 弹窗
                    ↓
         Yes → AssetTools 导入批量动作
         No  → 标记忽略，不导入
```

Socket 线程不得直接调用 `FMessageDialog`、Slate、Asset Registry、AssetTools 或其它
Editor API。可以在接收线程完成纯数据校验和 ACK，然后通过：

```cpp
AsyncTask(ENamedThreads::GameThread, [Message]()
{
    // 弹窗与导入逻辑
});
```

投递到 Game Thread。监听线程使用阻塞式 `Accept/Recv`，不应注册每帧 Tick，也不应
周期性扫描文件系统。

## 去重、批量与生命周期

- 同一条 `event_id` 只能弹一次；重复消息可以 ACK 为 accepted，但不要再次排队。
- 一个请求中的多个 `actions` 应在一个窗口中列出，并只询问一次“是否全部导入”。
- 插件关闭时应先设置停止标记并关闭监听 Socket，以唤醒阻塞的 `Accept/Recv`，然后
  安全等待线程退出，避免 Unreal Editor 退出时残留工作线程。
- PIE 期间可以立即提示，也可以暂存到退出 PIE 后；具体策略属于 UE 插件行为。
- 导入过程失败应在 UE 中报告，不需要通过当前 TCP 连接回传，因为 Maya 在收到
  ACK 后会关闭连接。

## UE 导入配置建议

建议 UE 项目维护显式映射，例如：

```json
{
  "GOF": {
    "Characters": {
      "Nujian": {
        "skeleton": "/Game/Characters/Nujian/Rig/Nujian_Skeleton",
        "animation_path": "/Game/Characters/Nujian/Animations"
      }
    }
  }
}
```

导入动作 FBX 时通常需要配置为：

- Animation 类型；
- `Import Mesh = false`；
- `Import Animations = true`；
- 指定现有 Skeleton；
- 明确同名资源是覆盖、Reimport 还是二次询问；
- 导入完成后按团队规则保存资产。

不同 UE 版本的 AssetTools/FBX Import API 有差异，协议刻意不绑定这些具体 API。

## Maya 端失败语义

Maya 发布界面中的 `send_ue_cBox`（“发布完成通知UE导入”）是通知总开关。只有用户
勾选它时，发布工具才会连接 UE Bridge；未勾选时不会建立 Socket、不会等待 ACK，
也不会产生 UE 离线日志。这个开关只控制通知，不影响 Maya/FBX 发布本身。

Maya 日志会区分：

- `acknowledged`：UE 已接收并接受；
- `rejected`：UE 明确拒绝；
- `sent`：TCP 已发送，但短超时内没有合法 ACK；
- `offline`：端口没有监听或无法及时连接；
- `error`：帧、JSON、ACK 或其它协议错误。

除 Maya 自身 FBX 导出失败外，上述 UE 通信状态都不改变动作发布结果。
