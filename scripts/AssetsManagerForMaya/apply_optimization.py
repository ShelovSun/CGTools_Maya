#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AssetsManager_Maya 性能优化状态检查脚本。

优化版已正式合并为 sources/assetTools.py，不再维护并行的优化副本。
保留本脚本是为了兼容旧的 status/apply 调用。
"""

import os
import sys


def apply_optimization():
    """兼容旧命令：现在只确认正式 assetTools.py 存在，不再复制/改写文件。"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    final_file = os.path.join(base_path, "sources", "assetTools.py")
    if os.path.exists(final_file):
        print("[状态] 优化版已内置到 sources/assetTools.py，无需切换")
        return True
    print(f"[错误] 正式文件不存在: {final_file}")
    return False


def check_optimization_status():
    """检查当前优化状态"""
    base_path = os.path.dirname(os.path.abspath(__file__))

    # 检查新组件是否存在
    new_components = [
        "widgets/am_thumbnail_loader.py",
        "widgets/am_list_item_optimized.py",
        "widgets/am_list_view.py",
        "widgets/am_items_widget.py",
        "widgets/am_main_optimized.py",
        "utils/am_database.py",
        "sources/assetTools.py",
    ]

    print("\n[状态检查]")
    print("-" * 50)

    all_exist = True
    for component in new_components:
        full_path = os.path.join(base_path, component)
        exists = os.path.exists(full_path)
        # 纯 ASCII 标记可兼容 Maya 在中文 Windows 下默认使用的 GBK 控制台，
        # 避免状态检查本身因无法编码 Unicode 对勾/叉号而中断。
        status = "[OK]" if exists else "[MISSING]"
        print(f"{status} {component}")
        if not exists:
            all_exist = False

    print("-" * 50)

    if all_exist:
        print("[状态] 所有优化组件已安装")
    else:
        print("[状态] 部分组件缺失，请检查安装")

    print("[状态] sources/assetTools.py 是唯一正式入口")

    return all_exist


def main():
    """主函数"""
    print("=" * 60)
    print("AssetsManager_Maya 性能优化工具")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python apply_optimization.py status  - 检查状态")
        print("  python apply_optimization.py apply   - 确认优化已内置")
        return

    command = sys.argv[1].lower()

    if command == "status":
        check_optimization_status()

    elif command == "apply":
        print("\n[操作] 应用优化版本...")
        if check_optimization_status():
            apply_optimization()
        else:
            print("[错误] 优化组件不完整，无法应用")

    else:
        print(f"[错误] 未知命令: {command}")
        print("可用命令: status, apply")


if __name__ == "__main__":
    main()
