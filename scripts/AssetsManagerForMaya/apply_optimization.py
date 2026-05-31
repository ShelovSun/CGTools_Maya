#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AssetsManager_Maya 性能优化一键切换脚本
使用方法:
    1. 备份原有文件
    2. 应用优化版本
    3. 或恢复原有版本
"""

import os
import shutil
import sys


def backup_file(src_path, backup_suffix=".backup"):
    """备份文件"""
    backup_path = src_path + backup_suffix
    if os.path.exists(src_path):
        if not os.path.exists(backup_path):
            shutil.copy2(src_path, backup_path)
            print(f"[备份] {src_path} -> {backup_path}")
            return True
    return False


def restore_file(src_path, backup_suffix=".backup"):
    """从备份恢复文件"""
    backup_path = src_path + backup_suffix
    if os.path.exists(backup_path):
        shutil.copy2(backup_path, src_path)
        print(f"[恢复] {backup_path} -> {src_path}")
        return True
    else:
        print(f"[错误] 备份文件不存在: {backup_path}")
        return False


def apply_optimization():
    """应用优化版本"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    sources_path = os.path.join(base_path, "sources")

    # 备份原有文件
    original_file = os.path.join(sources_path, "assetTools.py")
    backup_file(original_file)

    # 替换为优化版本
    optimized_file = os.path.join(sources_path, "assetTools_optimized.py")
    if os.path.exists(optimized_file):
        # 读取优化版本内容
        with open(optimized_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 修改类名以匹配原文件
        content = content.replace('class AssetToolsUI', 'class AssetToolsUIOptimized')

        # 写入原文件位置
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print("[应用] 优化版本已应用到 assetTools.py")
        print("[提示] 请重启 Maya 使更改生效")
        return True
    else:
        print(f"[错误] 优化文件不存在: {optimized_file}")
        return False


def restore_original():
    """恢复原始版本"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    sources_path = os.path.join(base_path, "sources")

    original_file = os.path.join(sources_path, "assetTools.py")
    if restore_file(original_file):
        print("[恢复] 原始版本已恢复")
        print("[提示] 请重启 Maya 使更改生效")
        return True
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
        "sources/assetTools_optimized.py",
    ]

    print("\n[状态检查]")
    print("-" * 50)

    all_exist = True
    for component in new_components:
        full_path = os.path.join(base_path, component)
        exists = os.path.exists(full_path)
        status = "✓" if exists else "✗"
        print(f"{status} {component}")
        if not exists:
            all_exist = False

    print("-" * 50)

    if all_exist:
        print("[状态] 所有优化组件已安装")
    else:
        print("[状态] 部分组件缺失，请检查安装")

    # 检查备份
    backup_file = os.path.join(base_path, "sources", "assetTools.py.backup")
    if os.path.exists(backup_file):
        print("[状态] 原始文件已备份")
    else:
        print("[状态] 原始文件未备份")

    return all_exist


def main():
    """主函数"""
    print("=" * 60)
    print("AssetsManager_Maya 性能优化工具")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\n使用方法:")
        print("  python apply_optimization.py status  - 检查状态")
        print("  python apply_optimization.py apply   - 应用优化")
        print("  python apply_optimization.py restore - 恢复原始版本")
        print("\n注意: 应用优化前会自动备份原始文件")
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

    elif command == "restore":
        print("\n[操作] 恢复原始版本...")
        restore_original()

    else:
        print(f"[错误] 未知命令: {command}")
        print("可用命令: status, apply, restore")


if __name__ == "__main__":
    main()
