<img src="./scripts/icons/CGTools.png" width="100" height="100"/>

# CGTools for Maya

CGTools 是一套基于 **Python / PySide2** 的 Autodesk Maya 插件套件，用于影视动画流程中的资产管理、镜头管理，以及覆盖建模、绑定、动画、解算、渲染等全环节的辅助工具。

> 这是一个面向工作室生产环境的 Maya 模块（`.mod`），并非独立应用。所有代码均在 Maya 内部运行。

---

## 支持版本

| Maya 版本 | Python 版本 | 状态 |
|-----------|-------------|------|
| 2014–2020 | 2.7 | 兼容 |
| 2022      | 3.7.7 | **主要目标版本** |
| 2022.3+   | 3.9 | 需自行验证 |

> UI 界面与注释主要使用中文，代码文件头保留 `# -*- coding: utf-8 -*-`。

---

## 核心功能模块

| 模块 | 路径 | 说明 |
|------|------|------|
| **Assets Manager** | `scripts/AssetsManagerForMaya` | 资产（角色 / 道具 / 场景）发布、版本管理与缩略图浏览 |
| **Shots Manager** | `scripts/ShotsManagerForMaya` | 镜头信息管理、场次与环节状态跟踪 |
| **Modeling Tools** | `scripts/tools_model` | 模型发布、材质管理、Arnold 助手、MaxToMaya 等 |
| **Rigging Tools** | `scripts/tools_rig` | 绑定发布、AdvancedSkeleton、NgSkinTool、SHAPES 等 |
| **Animation Tools** | `scripts/tools_ani` | 动作库发布、StudioLibrary、IK/FK 切换、BroDynamics 等 |
| **Simulation Tools** | `scripts/tools_sim` | 解算辅助、DynJointTools |
| **Rendering Tools** | `scripts/tools_render` | 灯光集工具、Deadline 提交 |
| **General Tools** | `scripts/tools_publish`, `scripts/tools_scene`, `scripts/tools_select`, `scripts/tools_view`, `scripts/tools_windows` | 通用发布、选择、视图、窗口工具 |

---

## 安装方法

### 方法一：自动安装（推荐）

在 Maya 中执行以下 MEL 命令：

```mel
source "E:/CGTools_for_Maya/001_CGTools_for_Maya2022_install.mel";
```

脚本会自动：
1. 将 `CGTools.mod` 写入第一个可用的 `MAYA_MODULE_PATH` 目录；
2. 把 `<PATH>` 替换为当前工程路径；
3. 加载模块并执行 `scripts/userSetup.py` 完成菜单与工具架初始化。

### 方法二：手动安装

1. 复制 `CGTools.mod` 到任意一个 `MAYA_MODULE_PATH` 目录（如 `~/Documents/maya/modules`）；
2. 用文本编辑器打开 `.mod` 文件，将 `<PATH>` 替换为工程根目录的绝对路径（使用正斜杠 `/`）；
3. 重启 Maya，菜单 `:: CGTools ::` 与工具架 `CGTools` 将自动加载。

---

## 项目结构

```
CGTools_for_Maya/
├── CGTools.mod                          # Maya 模块描述文件
├── 001_CGTools_for_Maya2022_install.mel # 自动安装脚本
├── README.md
├── scripts/
│   ├── userSetup.py                     # Maya 启动入口
│   ├── menu/
│   │   └── startup.py                   # 菜单 / 工具架构建、sys.path 初始化
│   ├── AssetsManagerForMaya/            # 资产管理主模块
│   │   ├── AssetsManager_Maya.py        # 主窗口入口
│   │   ├── sources/                     # 各 Tab 控制器
│   │   ├── widgets/                     # Qt UI 层（含优化版虚拟滚动缩略图）
│   │   ├── utils/                       # Maya/IO 辅助函数
│   │   └── config/                      # 项目配置读取
│   ├── ShotsManagerForMaya/             # 镜头管理主模块
│   ├── tools_model/                     # 建模工具
│   ├── tools_rig/                       # 绑定工具
│   ├── tools_ani/                       # 动画工具
│   ├── tools_sim/                       # 解算工具
│   ├── tools_render/                    # 渲染工具
│   ├── tools_publish/                   # 通用发布工具
│   ├── Python/
│   │   └── Python37/Lib/site-packages/  # 捆绑的第三方 Python 包
│   └── my_vendor/                       # 轻量兼容层（Qt.py, six.py）
└── shelves/                             # 工具架定义
```

> 因为 `menu/startup.py` 将各工具目录直接加入 `sys.path`，代码中使用的是**扁平根相对导入**，如 `from config import ...`、`import AssetsManager_Maya`。新增代码时请遵循此约定。

---

## 依赖说明

### Maya 自带（无需额外安装）

- `PySide2` / `shiboken2`（Maya 2017+）
- `maya.cmds`、`pymel.core`
- `json`、`os`、`sys` 等标准库

### 项目已捆绑（位于 `scripts/Python/Python37/Lib/site-packages`）

迁移工程时，**请确保以下目录一并复制**，否则会出现 `ModuleNotFoundError`：

| 包名 | 用途 | 对应目录 |
|------|------|----------|
| `psycopg2` | PostgreSQL 数据库连接 | `psycopg2/`, `psycopg2-2.9.5.dist-info/` |
| `requests` | HTTP 请求（缩略图 / 网络资源下载） | `requests/`, `requests-2.28.1.dist-info/` |
| `urllib3` | `requests` 的底层依赖 | `urllib3/`, `urllib3-1.26.13.dist-info/` |
| `certifi` | SSL 证书验证 | `certifi/`, `certifi-2022.12.7.dist-info/` |
| `charset_normalizer` | 编码自动检测 | `charset_normalizer/`, `charset_normalizer-2.1.1.dist-info/` |
| `idna` | 国际化域名处理 | `idna/`, `idna-3.4.dist-info/` |

### 项目自带兼容层

- `Qt.py`（`scripts/my_vendor/`）：兼容 PySide2 / PyQt5 的抽象层
- `six.py`（`scripts/my_vendor/`）：Python 2/3 兼容工具

### 外部基础设施

- **PostgreSQL 数据库**：默认连接 `10.0.203.34:5432`，资产与镜头数据存储于服务端。运行工具前需确保网络可达。

### 如需手动补充依赖

若捆绑目录缺失，可使用 Maya 自带的 Python 安装：

```bash
"C:/Program Files/Autodesk/Maya2022/bin/mayapy.exe" -m pip install requests psycopg2-binary -t "E:/CGTools_for_Maya/scripts/Python/Python37/Lib/site-packages"
```

> 若 `mayapy` 没有 `pip`，先执行 `mayapy -m ensurepip`。

---

## 配置

### 项目设置

`config/projectSetting.json` 是流程契约文件，定义了：

- `rootPath`：项目根路径
- `projects`：项目列表
- `user_list`：用户列表
- 各资产类型的文件夹与文件命名规范（`assetFolder`、`rigFileHi`、`actionFolder`、`assembly` 等）

**修改磁盘目录结构时，只需改此 JSON，无需改代码。**

### 运行时配置

首次运行后，配置会被拷贝到用户临时目录：

- `%APPDATA%/AssetsManagerTemp` —— 资产模块运行时配置
- `%APPDATA%/ShotManagerTemp` —— 镜头模块运行时配置
- Qt `QSettings` —— 窗口几何与登录信息持久化

---

## 开发与调试

### VS Code 配置

本项目包含 VS Code 调试配置：

- **Maya 2022: Attach Debugger**：通过 `debugpy` 附加到运行在 `localhost:5678` 的 Maya 进程。
- **mayapy Launch**：直接启动 Maya 的 Python 解释器进行离线测试。

> 任何触及 `maya.cmds`、`pymel` 或捆绑 site-packages 的代码，请使用 **mayapy** 而非系统 Python 运行。

### 代码风格

- 格式化工具：**Black**，行宽 `100`（见 `.vscode/settings.json`）。
- 文件编码：**UTF-8**，保留 `# -*- coding: utf-8 -*-` 文件头。

### Cython 模块

部分性能敏感模块（`sources/common_pyd/`、`sources/list_items_pyd/`）使用 Cython 编译为 `.pyd`。如需重新编译：

```bash
cd scripts/AssetsManagerForMaya/sources/common_pyd
mayapy setup.py build_ext --inplace
```

---

## 注意事项

1. **无自动化测试/CI**：验证方式为在 Maya 中手动加载并运行工具。
2. **无 `requirements.txt`**：第三方依赖全部以 vendor 形式置于 `scripts/Python/...` 和 `scripts/my_vendor/` 中。
3. **换电脑迁移时**，请务必连同 `scripts/Python/` 和 `scripts/my_vendor/` 一起复制，否则会出现 `ModuleNotFoundError`。

---

## 许可证

MIT
