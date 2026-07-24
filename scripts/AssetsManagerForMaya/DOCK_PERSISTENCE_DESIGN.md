# AssetsManager 窗口「浮动/停靠状态」持久化 —— 方案讨论文档

> 目的：把逻辑梳理清楚，对着这份文档讨论、定方向。**本文只描述设计，不代表已实现。**

---

## 1. 需求（你要的效果）

1. 面板**浮动和停靠都要好用**（不能像之前那样浮动白屏）。
2. 面板要**记住我上次的状态**，下次打开**完全还原**：
   - 上次是**浮动**，且在某位置/某大小 → 下次打开还是浮动，回到那个位置和大小。
   - 上次是**停靠**，且停靠在某个位置 → 下次打开还是停靠，回到那个停靠位置。
3. 因此需要记录三件事：
   - **是浮动还是停靠**；
   - 浮动时的**具体位置 + 大小**；
   - 停靠时的**具体停靠位置**（哪一边 / 和谁并排 / 大小）。
4. 生效范围：不仅同一次 Maya 内关掉再开，**重启 Maya 后也要还原**。

---

## 2. 背景：Maya 里这种可停靠窗口是怎么工作的

AssetsManager 用的是 `MayaQWidgetDockableMixin`。窗口显示时，Maya 会建一个 **`workspaceControl`**（停靠系统的容器），我们的界面挂在它里面。「浮动/停靠/在哪一边/多大」这些状态，**由 workspaceControl 承载**。

要让这些状态**跨重启**保留，Maya 只有两条路：

- **路线甲：自己用 QSettings 存，打开时用 `show()` 参数手动摆。**
  我们自己判断上次是浮动还是停靠、存进配置；下次打开时按配置调 `show(dockable=True, floating=.., area=..)`。
- **路线乙：用 Maya 原生的 workspace 持久化（`uiScript`）。**
  创建 workspaceControl 时给一段 `uiScript`（重建界面的代码）。Maya 会把这个控件的完整布局（浮动/停靠/哪一边/大小/tab 分组）**存进工作区配置**，重启后自动还原布局，并执行 `uiScript` 把界面内容重新填进去。Maya 自带面板、ngSkinTools2 都是这么做的。

### 一个关键约束：白屏

我们之前试过路线乙，结果**浮动时白屏**。根因是：`AssetsManagerUI` 是一个 **`QMainWindow`**，`uiScript` 恢复时把这个 QMainWindow 整个 reparent 进 workspaceControl，Qt 底层画不出来 → 白屏。
而 StudioLibrary、ngSkinTools2 用的是**普通 `QWidget` + 布局**，界面内容是**建进 workspaceControl 自己的 widget 里**（不 reparent 一个顶层 QMainWindow），所以它们用路线乙不白屏、且能精确记住停靠。

**结论：白屏不是 `uiScript` 的错，是「QMainWindow 被 reparent」的错。**

---

## 3. 现状（路线甲）与它的天花板

目前代码走的是路线甲（QSettings + `show()` 参数）。逐条对照需求：

| 能力 | 路线甲能否做到 | 说明 |
|------|--------------|------|
| 浮动 → 还原浮动 + 位置 + 大小 | ✅ 可以 | 存 `pos/size`，打开时 `show(dockable=True)` + 恢复几何。已验证 OK。 |
| 停靠 → 还原成「停靠」状态 | ⚠️ 勉强 | `show(dockable=True, floating=False, area=..)` 能让它停靠。 |
| 停靠 → 还原到**具体哪一边** | ❌ 不可靠 | Maya **没有查询停靠区域的命令**；我用 Qt `dockWidgetArea` 兜底，但 workspaceControl 的父子结构下大概率查不到 → 只能回默认边。 |
| 停靠 → 还原**精确布局**（和谁并排/大小） | ❌ 做不到 | `show` 参数只能粗粒度指定一条边。 |
| 退出瞬间正确判断「浮动还是停靠」 | ⚠️ 有隐患 | 退出 Maya 时控件可能正在销毁，`isFloating()` 会落到兜底值 `True`，可能把停靠**误存成浮动**。 |

**天花板：路线甲能把「浮动」记得很准，但「停靠的精确位置」本质上做不到。** 它满足不了你需求里的「停靠也要精确还原」。

---

## 4. 推荐方案（路线乙）：QWidget 重构 + uiScript 原生持久化

要**同时精确还原浮动和停靠**，正解是回到 Maya 原生持久化（路线乙），并且**消除白屏的根因**——把窗口从 `QMainWindow` 改成普通 `QWidget`。

### 4.1 为什么这样能满足全部需求
- 停靠/浮动、哪一边、大小、tab 分组，全部由 **Maya workspace 原生保存**，重启自动还原 —— 精度就是 Maya 自带面板的水平。
- 不再 reparent 顶层 QMainWindow（改为把内容建进 workspaceControl 的 widget），**不白屏**。
- 浮动位置可选择性地再用 QSettings 兜底（双保险）。

### 4.2 需要改的地方（评估，非最终）
1. **`AssetsManagerUI` 基类**：`QMainWindow` → `QtWidgets.QWidget`。
2. **界面挂载方式**：`setCentralWidget(centralwidget)` → 在 `self` 上放一个布局 `QVBoxLayout(self).addWidget(centralwidget)`。
   - 好消息：角标按钮（登录/设置/收缩）现在是加在 **`tabWidget` 的 cornerWidget** 上的（`QTabWidget` 的能力），**不依赖 QMainWindow**，基本不用改。
   - `shrinkWin()`（主界面 ↔ mini 切换）里的 `setCentralWidget/centralWidget()` 改成往布局里换子控件。
3. **显示入口改用 workspaceControl + uiScript**（对齐 ngSkinTools2 [ui/mainwindow.py:195-248]）：
   - `showWindow()`：控件不存在就 `cmds.workspaceControl(WORKSPACE_CONTROL, uiScript='…build()')` 创建，存在就 `restore`。
   - `build()`（uiScript 调用）：`findControl` 拿到 workspaceControl 的 widget → 新建/取用 `AssetsManagerUI` 内容 → `addWidget` 进去。
4. **保存**：浮动几何仍可存 QSettings 兜底；停靠状态交给 Maya 原生，不再自己存 `dockArea`。
5. 清理掉路线甲里为停靠恢复加的临时逻辑（`_currentDockArea`、`showWindow` 里的 `floating/area` 分支等）。

### 4.3 代价与风险（必须诚实说明）
- 属于**主窗口架构级重构**，改动比之前几次都大，可能触及 mini 模式、角标、tab 懒加载等细节。
- `uiScript` 相关行为**我无法在本机验证**，必须在你的 Maya 2022 里逐项测试；历史上这块踩过白屏坑，需要小步验证。
- `uiScript` 里的重建函数要能独立把界面搭起来（登录态、tab 等），比 ngSkinTools2 的简单界面工程量大一些。

---

## 5. 两个方案对比

| 维度 | 方案A：现状(QSettings手动) | 方案B：QWidget+uiScript(推荐) |
|------|--------------------------|------------------------------|
| 浮动还原位置/大小 | ✅ 精确 | ✅ 精确 |
| 停靠还原「哪一边」 | ❌ 多半回默认边 | ✅ 精确（Maya 原生） |
| 停靠还原精确布局 | ❌ | ✅ |
| 浮动白屏 | ✅ 已解决 | ✅ 不会（不 reparent QMainWindow） |
| 改动量 / 风险 | 小 | 大（架构重构 + 需在 Maya 反复验证） |
| 满足你的完整需求 | ❌ 停靠做不到精确 | ✅ 全满足 |

---

## 6. 验证计划（选定方案后，在 Maya 内逐项测）
1. 浮动某位置/大小 → 退出重启 → 打开：位置/大小一致。
2. 停靠某一侧（并调大小）→ 退出重启 → 打开：停靠边/大小一致。
3. 浮动↔停靠反复拖动：不白屏、内容完整。
4. 同一次 Maya 内关掉再开：保持上次状态。
5. mini 模式切换正常。

---

## 7. 待你拍板的点

1. **确认精度要求**：停靠是否必须「精确还原到上次那一侧/布局」？
   - 是 → 走**方案B**（重构，一劳永逸，但工程量/验证成本高）。
   - 「只要还停靠着、位置差不多」就行 → 可以先用**方案A**把隐患补稳，成本低。
2. 若走方案B，是否接受「较大重构 + 需要你在 Maya 里配合分步验证」？
3. mini 模式在方案B下是否也要保留同样的持久化行为？
