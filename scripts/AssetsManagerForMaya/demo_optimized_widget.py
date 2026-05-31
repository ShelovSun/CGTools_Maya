#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
高性能资产列表组件演示
展示如何使用新的优化组件
"""

import sys
import random
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

# 添加路径
import os
scripts_path = os.path.dirname(os.path.abspath(__file__))
if scripts_path not in sys.path:
    sys.path.insert(0, scripts_path)

from widgets.am_items_widget import ItemsWidget
from widgets.am_thumbnail_loader import ThumbnailLoader


class DemoWindow(QtWidgets.QWidget):
    """演示窗口"""

    def __init__(self, parent=None):
        super(DemoWindow, self).__init__(parent)

        self.setWindowTitle("AssetsManager 高性能组件演示")
        self.resize(1200, 800)

        # 主布局
        layout = QtWidgets.QVBoxLayout(self)

        # 控制面板
        control_layout = QtWidgets.QHBoxLayout()

        # 视图模式切换
        self.view_mode_btn = QtWidgets.QPushButton("切换到列表模式")
        self.view_mode_btn.clicked.connect(self.toggleViewMode)
        control_layout.addWidget(self.view_mode_btn)

        # 大小滑块
        control_layout.addWidget(QtWidgets.QLabel("图标大小:"))
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setRange(50, 256)
        self.size_slider.setValue(120)
        self.size_slider.valueChanged.connect(self.onSizeChanged)
        control_layout.addWidget(self.size_slider)

        # 数量显示
        self.count_label = QtWidgets.QLabel("资产数量: 0")
        control_layout.addWidget(self.count_label)

        # 加载按钮
        self.load_btn = QtWidgets.QPushButton("加载测试数据 (1000条)")
        self.load_btn.clicked.connect(self.loadTestData)
        control_layout.addWidget(self.load_btn)

        # 清空按钮
        self.clear_btn = QtWidgets.QPushButton("清空")
        self.clear_btn.clicked.connect(self.clearData)
        control_layout.addWidget(self.clear_btn)

        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 进度条
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QtWidgets.QLabel("就绪")
        layout.addWidget(self.status_label)

        # 高性能 ItemsWidget
        self.items_widget = ItemsWidget(self)
        self.items_widget.itemSelectionChanged.connect(self.onSelectionChanged)
        layout.addWidget(self.items_widget)

        # 测试数据
        self.test_data = []
        self.loaded_count = 0

    def toggleViewMode(self):
        """切换视图模式"""
        if self.items_widget.isList():
            self.items_widget.setIsList(False)
            self.view_mode_btn.setText("切换到列表模式")
            self.status_label.setText("切换到图标模式")
        else:
            self.items_widget.setIsList(True)
            self.view_mode_btn.setText("切换到图标模式")
            self.status_label.setText("切换到列表模式")

    def onSizeChanged(self, value):
        """大小改变"""
        self.items_widget.setItemSize(value)
        self.items_widget.resizeItem()

    def generateTestData(self, count=1000):
        """生成测试数据"""
        data = []
        asset_types = ["Character", "Props", "Environment", "Weapon"]
        status_list = ["已完成", "制作中", "未开始"]
        artists = ["Artist A", "Artist B", "Artist C", "Artist D"]

        for i in range(count):
            asset_type = random.choice(asset_types)
            asset_name = f"{asset_type}_{i:04d}"
            zh_name = f"资产_{i:04d}"

            data.append((
                f"2024{random.randint(1, 12):02d}{random.randint(1, 28):02d}",  # date
                asset_name,  # name
                zh_name,  # zh_name
                random.choice(artists),  # mod_artist
                random.choice(status_list),  # mod_status
                random.choice(artists),  # rig_artist
                random.choice(status_list),  # rig_status
                "",  # icon_path (空表示使用默认图标)
                f"Note for {asset_name}"  # note
            ))

        return data

    def loadTestData(self):
        """加载测试数据"""
        self.status_label.setText("正在生成测试数据...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        # 生成数据
        self.test_data = self.generateTestData(1000)

        # 清空并设置数据
        self.items_widget.clear()
        self.items_widget.setItemsList(self.test_data)

        # 分批加载
        self.loaded_count = 0
        self.total_count = len(self.test_data)

        self.load_timer = QtCore.QTimer(self)
        self.load_timer.timeout.connect(self.loadBatch)
        self.load_timer.start(10)  # 每10ms加载一批

        self.status_label.setText(f"正在加载 {self.total_count} 条数据...")

    def loadBatch(self):
        """分批加载"""
        batch_size = 50
        end = min(self.loaded_count + batch_size, self.total_count)

        for i in range(self.loaded_count, end):
            self.items_widget.addItem(self.test_data[i])

        self.loaded_count = end

        # 更新进度
        progress = int(self.loaded_count / self.total_count * 100)
        self.progress_bar.setValue(progress)
        self.count_label.setText(f"资产数量: {self.loaded_count}")

        if self.loaded_count >= self.total_count:
            self.load_timer.stop()
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"加载完成，共 {self.total_count} 条数据")

    def clearData(self):
        """清空数据"""
        self.items_widget.clear()
        self.test_data = []
        self.loaded_count = 0
        self.count_label.setText("资产数量: 0")
        self.status_label.setText("已清空")

    def onSelectionChanged(self):
        """选择改变"""
        items = self.items_widget.selectedItems()
        if items:
            item_data = items[0].itemData()
            self.status_label.setText(f"选中: {item_data[1]}")

    def closeEvent(self, event):
        """关闭事件"""
        # 清理缩略图缓存
        ThumbnailLoader.clearCache()
        super(DemoWindow, self).closeEvent(event)


def show_demo():
    """显示演示窗口"""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)

    window = DemoWindow()
    window.show()
    return window


if __name__ == "__main__":
    window = show_demo()
    sys.exit(QtWidgets.QApplication.instance().exec_())
