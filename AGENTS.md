# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## What this is

CGTools is a Maya **module** (`.mod`) that bundles a studio CG-production pipeline: a large suite of Python/PySide2 tools for managing assets, shots, modeling, rigging, animation, sim, and rendering. It is not a standalone application — all code runs **inside Autodesk Maya** (targets Maya 2014–2022; primary target is Maya 2022 with its bundled CPython 3.7.7). Most UI text and comments are in Chinese.

The two flagship tools are **AssetsManager** (`scripts/AssetsManagerForMaya`) and **ShotsManager** (`scripts/ShotsManagerForMaya`); the rest live under `scripts/tools_*` (one folder per pipeline stage).

## How it loads (critical to understand before editing)

Loading is a chain, and the `sys.path` setup in step 3 is what makes the flat imports throughout the codebase work:

1. **Install** — In Maya, `source` `Install_CGTools_for_Maya2022.mel` (or `001_CGTools_for_Maya2022_install.mel`). This writes `CGTools.mod` into a `MAYA_MODULE_PATH` dir with `<PATH>` substituted for the repo location, loads the module, and runs `scripts/userSetup.py`.
2. **`scripts/userSetup.py`** — on Maya startup, defers to `menu.startup.execute()`.
3. **`scripts/menu/startup.py`** — the real bootstrap. It appends ~20 tool directories (and the bundled `scripts/Python/Python37/Lib/site-packages`) to `sys.path`, extends `MAYA_SCRIPT_PATH`, sources Arnold MEL, then builds the `:: CGTools ::` Maya menu (`menu_setup`) and the shelf (`shelf_setup`).

Because `startup.py` puts each tool dir directly on `sys.path`, imports are **flat and root-relative**, not package-qualified — e.g. inside AssetsManager you'll see `from config import ...`, `from utils import jsonHelper`, `from sources import assetTools`, `import AssetsManager_Maya`. When adding code, match this convention; do not assume the repo root is a package.

Menu items are wired as inline command strings in `menu_setup()` (e.g. `command="import AssetsManager_Maya as AM;AM.showWindow()"`). Adding a tool to the menu = adding a `pm.menuItem(...)` with such a string.

## AssetsManager architecture

Entry point: `AssetsManager_Maya.showWindow()` → `AssetsManagerUI` (a `MayaQWidgetDockableMixin` QMainWindow). Layering:

- **`AssetsManager_Maya.py`** — top-level window, login/QSettings persistence, tab dispatch. Tabs are lazily constructed in `tabChanged()`; each tab hosts a `*ToolsUI` from `sources/`.
- **`sources/`** — per-tab controllers: `assetTools`, `sceneTools`, `actionTools`, `ShotsManager_Maya`, `rigTools`, etc. (several are commented out / WIP).
- **`widgets/`** — the Qt view layer. Note the **two generations**: original (`am_listWidget`, `am_listItem`, `am_main`) and a StudioLibrary-inspired optimized rewrite (`am_list_view`, `am_list_item_optimized`, `am_thumbnail_loader`, `am_main_optimized`) for async thumbnail loading and virtual scrolling. See `OPTIMIZATION_README.md`. `*_optimized.py` files are the newer path.
- **`utils/`** — Maya/IO helpers (`jsonHelper`, `publish`, `am_database`, `copy_thread`, plus a `gui/` subpackage and several files lifted from StudioLibrary: `mirrortable`, `pose`, `playblast`, `animation`).
- **`config/`** — `config.__init__` exposes `projectSetting()`, `am_Temp()`, `sm_Temp()`, and the `SMConfig` ini-settings class.

**Data backend**: PostgreSQL via `psycopg2` (bundled under `scripts/Python/Python37/Lib/site-packages`), connecting to a studio DB host (default `10.0.203.34`, port 5432); assets/scenes also resolve to network file paths. There is no local DB — running the tools requires the studio environment.

## Configuration & runtime state

- **`config/projectSetting.json`** is the pipeline contract: it defines `rootPath`, `projects`, `user_list`, and the folder/file naming for every asset type (`assetFolder`, `rigFileHi`, `actionFolder`, `assembly`, etc.). Code reads paths through these keys rather than hardcoding — changing the on-disk layout means editing this file, not the Python.
- On first run the JSON is copied to a per-user temp dir; runtime/user settings live in `%APPDATA%/AssetsManagerTemp` and `%APPDATA%/ShotManagerTemp` (`setting.json`, ini files via `SMConfig`), plus Qt `QSettings` for window geometry.

## Cython modules

`sources/common_pyd/` and `sources/list_items_pyd/` ship `.pyx` sources compiled to `.pyd`. To rebuild (must use Maya's Python so the ABI matches, e.g. `mayapy`):

```bash
cd scripts/AssetsManagerForMaya/sources/common_pyd
mayapy setup.py build_ext --inplace
```

The `backup/` folders next to them hold prior `.py`/`.pyx` revisions — reference only, not imported.

## Working in this codebase

- **No automated test/build/lint harness exists.** Verification is manual: load the module in Maya and exercise the tool. There is no CI, no `requirements.txt`, no package manifest — third-party deps are vendored under `scripts/Python/...` and `scripts/my_vendor/` (`Qt.py`, `six.py`).
- **Formatting**: Black, line length 100 (`.vscode/settings.json`). UI strings are Chinese — preserve `# -*- coding: utf-8 -*-` headers and use UTF-8.
- **Debugging in Maya**: VS Code config provides a `debugpy` *attach* on `localhost:5678` ("Maya 2022: Attach Debugger") and a `mayapy` launch config. Use mayapy (not the system Python) for anything that touches `maya.cmds`, `pymel`, or the bundled site-packages.
- **Maya version checks** live in `CGTools.mod` (`MAYAVERSION` lines) and the install MEL's `findModuleMatch`; the code itself assumes PySide2 + `shiboken2` (Maya 2017+ Qt5).
