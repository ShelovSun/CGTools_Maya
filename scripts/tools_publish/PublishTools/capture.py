# # -*- coding: utf-8 -*-
# import tkinter as tk
# import pyautogui
# from PIL import ImageGrab
# from PIL import ImageTk
# from PIL import Image

# import sys
# from PySide2.QtWidgets import QApplication, QWidget, QRubberBand, QToolButton, QFileDialog, QHBoxLayout
# from PySide2.QtCore import Qt, QRect
# from PySide2.QtGui import QPainter, QColor, QPen, QScreen, QCursor
# from PySide2.QtWidgets import QDesktopWidget
# import os
#
#
# class ScreenCaptureToolBar(QWidget):
#     """截图完成后显示的小工具栏"""
#     def __init__(self, parent, rect, screenshot):
#         super().__init__(parent)
#         self.screenshot = screenshot
#         self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
#         self.setAttribute(Qt.WA_TranslucentBackground)
#
#         layout = QHBoxLayout(self)
#         layout.setContentsMargins(5, 5, 5, 5)
#         layout.setSpacing(8)
#
#         # 保存按钮
#         save_btn = QToolButton()
#         save_btn.setText("💾")
#         save_btn.clicked.connect(self.save_img)
#         layout.addWidget(save_btn)
#
#         # 复制按钮
#         copy_btn = QToolButton()
#         copy_btn.setText("📋")
#         copy_btn.clicked.connect(self.copy_img)
#         layout.addWidget(copy_btn)
#
#         # 取消按钮
#         cancel_btn = QToolButton()
#         cancel_btn.setText("❌")
#         cancel_btn.clicked.connect(self.close_parent)
#         layout.addWidget(cancel_btn)
#
#         # 工具栏位置：矩形框下方
#         geo = rect.translated(parent.geometry().topLeft())
#         self.move(geo.right() - 135, geo.bottom() + 5)
#         self.show()
#
#     def save_img(self):
#         filename, _ = QFileDialog.getSaveFileName(self, "保存截图", "screenshot.png", "PNG Files (*.png)")
#         if filename:
#             self.screenshot.save(filename, "PNG")
#
#     def copy_img(self):
#         QApplication.clipboard().setPixmap(self.screenshot)
#
#     def close_parent(self):
#         self.parent().close()
#
#
# class ScreenCaptureTool(QWidget):
#     """截图工具"""
#     def __init__(self, screen):
#         super().__init__()
#         self.screen = screen
#         self.setWindowTitle('Screen Capture Tool')
#         self.setGeometry(screen.geometry())
#         self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
#         self.origin = None
#         self.rect = None
#         self.setStyleSheet("background-color: rgb(0,0,0);")
#         self.setWindowOpacity(0.3)  # For full transparency
#         self.fullScreen = screen.grabWindow(0)
#         self.toolbar = None
#         self.showFullScreen()
#
#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             self.origin = event.pos()
#             if self.rubberBand.isVisible():
#                 self.rubberBand.hide()
#             self.rubberBand.setGeometry(QRect(self.origin, self.origin))
#             self.rubberBand.show()
#         else:
#             if self.rubberBand.isVisible():
#                 self.close()
#
#     def mouseMoveEvent(self, event):
#         if self.origin is not None:
#             self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
#
#     def mouseReleaseEvent(self, event):
#         if self.rubberBand.isVisible():
#             self.rect = self.rubberBand.geometry()
#             print(self.rect)
#             # self.paint()
#             screenshot = self.fullScreen.copy(self.rect)
#             self.toolbar = ScreenCaptureToolBar(self, self.rect, screenshot)
#
#     def paintEvent(self, event):
#         if self.rect:
#             # Draw transparent rectangle
#             painter = QPainter(self)
#             painter.setRenderHint(QPainter.Antialiasing)
#             painter.setCompositionMode(QPainter.CompositionMode_Clear)
#             painter.fillRect(self.rect, Qt.transparent)
#             painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
#             painter.setPen(QPen(Qt.DashLine))
#             painter.drawRect(self.rect)
#
#             # Draw resize handles
#             handle_size = 10
#             painter.setBrush(QColor(255, 0, 0))
#             # for dx in [0, self.rect.width()]:
#             #     for dy in [0, self.rect.height()]:
#             self.handle_t = painter.drawRect(self.rect.x() + (self.rect.width() * 0.5) - handle_size // 2,
#                                              self.rect.y() - handle_size // 2,
#                                              handle_size, handle_size)
#             self.handle_b = painter.drawRect(self.rect.x() + (self.rect.width() * 0.5) - handle_size // 2,
#                                              self.rect.y() + self.rect.height() - handle_size // 2,
#                                              handle_size, handle_size)
#             self.handle_l = painter.drawRect(self.rect.x() - handle_size // 2,
#                                              self.rect.y() + (self.rect.height() * 0.5) - handle_size // 2,
#                                              handle_size, handle_size)
#             self.handle_r = painter.drawRect(self.rect.x() + self.rect.width() - handle_size // 2,
#                                              self.rect.y() + (self.rect.height() * 0.5) - handle_size // 2,
#                                              handle_size, handle_size)
#             # painter.drawRect(self.rect.x() + dx - handle_size // 2,
#             #                  self.rect.y() + dy - handle_size // 2,
#             #                  handle_size, handle_size)
#
#     def keyPressEvent(self, event):
#         if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
#             self.captureScreen()
#
#     def captureScreen(self):
#         if not self.rect:
#             return
#
#         screen = QApplication.primaryScreen()
#         screenshot = screen.grabWindow(
#             QDesktopWidget().winId(),
#             self.rect.x(), self.rect.y(), self.rect.width(), self.rect.height()
#         )
#
#         # Save screenshot to file
#         file_name = 'screenshot.png'
#         # file_index = 1
#         # while os.path.exists(file_name):
#         #     file_name = f'screenshot_{file_index}.png'
#         #     file_index += 1
#
#         screenshot.save(file_name, 'png')
#         print(f'Screenshot saved as {file_name}')
#
#         # Optionally close the application after saving the screenshot
#         self.close()
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     pos = QCursor.pos()
#     for screen in app.screens():
#         if screen.geometry().contains(pos):
#             target_screen = screen
#             break
#     else:
#         target_screen = app.primaryScreen()
#     tool = ScreenCaptureTool(target_screen)
#     # tool.initUI()
#     sys.exit(app.exec_())


# class Screenshot:
#     def __init__(self):
#         self.root = tk.Tk()
#         self.start_x = None
#         self.start_y = None
#         self.rect = None
#
#         self.set_root()
#         self.create_canvas()
#
#         self.root.mainloop()
#
#     def set_root(self):
#         # 设置全屏
#         self.root.attributes("-fullscreen", True)
#         self.root.attributes("-alpha", 0.3)  # 半透明
#         self.root.bind("<ButtonPress-1>", self.on_button_press)
#         self.root.bind("<B1-Motion>", self.on_mouse_drag)
#         self.root.bind("<ButtonRelease-1>", self.on_button_release)
#         self.root.bind("<Return>", self.on_key_return)
#         self.root.bind("<Escape>", lambda e: root.destroy())
#
#     def create_canvas(self):
#         # 创建一个画布
#         self.canvas = tk.Canvas(root, cursor="cross")
#         # self.canvas.pack(fill=tk.BOTH, expand=True)
#         self.canvas.update()
#
#     def on_button_press(self, event):
#         # 记录鼠标起始位置,初始化虚线框
#         self.canvas.delete("rectangle")
#         self.canvas.delete("handle")
#         self.start_x = self.canvas.canvasx(event.x)
#         self.start_y = self.canvas.canvasy(event.y)
#         self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red',
#                                                  dash=(6, 2), tags="rectangle")
#
#     def on_mouse_drag(self, event):
#         # 动态更新虚线框大小
#         cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
#         self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
#
#     def on_button_release(self, event):
#         # 释放鼠标后启用调节功能
#         self.cur_x, self.cur_y = self.canvas.coords(self.rect)[2:4]#self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
#         x_length = self.cur_x - self.start_x
#         y_length = self.cur_y - self.start_y
#
#         self.handle_t = self.canvas.create_rectangle(self.cur_x - (x_length * 0.5) - 5, self.start_y - 5,
#                                                      self.cur_x - (x_length * 0.5) + 5, self.start_y + 5,
#                                                      fill='black', tags="handle")
#         self.handle_b = self.canvas.create_rectangle(self.cur_x - (x_length * 0.5) - 5, self.cur_y - 5,
#                                                      self.cur_x - (x_length * 0.5) + 5, self.cur_y + 5,
#                                                      fill='black', tags="handle")
#         self.handle_l = self.canvas.create_rectangle(self.start_x - 5, self.cur_y - (y_length * 0.5) - 5,
#                                                      self.start_x + 5, self.cur_y - (y_length * 0.5) + 5,
#                                                      fill='black', tags="handle")
#         self.handle_r = self.canvas.create_rectangle(self.cur_x - 5, self.cur_y - (y_length * 0.5) - 5,
#                                                      self.cur_x + 5, self.cur_y - (y_length * 0.5) + 5,
#                                                      fill='black', tags="handle")
#         # self.canvas.bind("<B1-Motion>", self.on_adjust)
#         self.canvas.tag_bind("handle", "<B1-Motion>", self.on_adjust)
#
#     def on_adjust(self, event):
#         # 更新虚线框大小
#         # cur_x, cur_y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
#         # self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
#         self.cur_x, self.cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
#         self.canvas.coords(self.rect, self.start_x, self.start_y, self.cur_x, self.cur_y)
#         self.canvas.coords(self.handle_t, self.cur_x - 5, self.cur_y - 5, self.cur_x + 5, self.cur_y + 5)
#
#     def on_key_return(self, event):
#         # 获取截取区域坐标
#         x1, y1, x2, y2 = self.canvas.coords(self.rect)
#         # 检查坐标确保是左上角和右下角
#         if x2 < x1:
#             x1, x2 = x2, x1
#         if y2 < y1:
#             y1, y2 = y2, y1
#
#         # 隐藏窗口，进行截图
#         self.root.withdraw()
#         screenshot = ImageGrab.grab(bbox=(x1, y1, x2, y2))
#         # 保存图片
#         screenshot.save("screenshot.png")
#         # 退出程序
#         print("截图已保存为'screenshot.png'")
#         self.root.quit()

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ScreenshotApp(root)
#     root.mainloop()

import os
import sys

from PySide2 import QtWidgets, QtGui, QtCore


class ToolBar(QtWidgets.QWidget):
    def __init__(self, parent, rect, screenshot):
        super().__init__(parent)
        self.screenshot = screenshot
        self.parent = parent
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
        self.tempPath = "{}/AssetsManagerIconTemp".format(os.environ.get('APPDATA'))
        self.localIconPath = os.path.join(self.tempPath, 'snapshot')
        if not os.path.exists(self.localIconPath):
            os.makedirs(self.localIconPath)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(8)

        def make_btn(text, icon, func):
            btn = QtWidgets.QToolButton()
            btn.setToolTip(text)
            btn.setIcon(QtGui.QPixmap(icon))
            btn.clicked.connect(func)
            return btn

        layout.addWidget(make_btn("", '%s/icon/save.png' % self.scriptsPath, self.save_img))
        layout.addWidget(make_btn("", '%s/icon/copy.png' % self.scriptsPath, self.copy_img))
        layout.addWidget(make_btn("", '%s/icon/succeed.png' % self.scriptsPath, self.ok_do_it))
        layout.addWidget(make_btn("", '%s/icon/failed.png' % self.scriptsPath, self.close_parent))

        geo = rect.translated(parent.geometry().topLeft())
        self.move(geo.left(), geo.bottom() + 5)
        self.show()

    def save_img(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存截图", "screenshot.png", "PNG Files (*.png)")
        if filename:
            self.screenshot.save(filename, "PNG")

    def copy_img(self):
        QtWidgets.QApplication.clipboard().setPixmap(self.screenshot)

    def close_parent(self):
        self.close()
        self.parent.close()

    def ok_do_it(self):
        """ 确定截图 """
        filename = os.path.join(self.localIconPath, 'thumbnail.png')
        succeed = self.screenshot.save(filename, "PNG")
        if succeed:
            self.parent.send_back()
            self.close_parent()


class ScreenShot(QtWidgets.QWidget):
    active_instance = None

    def __init__(self, screen, parent):
        super().__init__()
        self.screen = screen
        self.parent = parent
        # print("geometry:", screen.geometry())
        self.setGeometry(screen.geometry())
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.setCursor(QtCore.Qt.CrossCursor)

        self.begin, self.end = QtCore.QPoint(), QtCore.QPoint()
        self.fullscreen = screen.grabWindow(0)
        self.toolbar = None
        self.is_active = False

        self.fixed_rect = None   # 松开后固定矩形
        self.dragging_handle = None  # 当前拖拽的控制点
        self.moving_rect = False     # 是否处于整体移动模式
        self.move_offset = None      # 鼠标按下时相对矩形框的偏移量

    def send_back(self):
        # print("通信到ScreenShot")
        self.parent.set_thumbnail()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawPixmap(0, 0, self.fullscreen)
        painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 120))

        rect = None
        if self.fixed_rect:
            rect = self.fixed_rect
        elif self.is_active and not self.begin.isNull() and not self.end.isNull():
            rect = QtCore.QRect(self.begin, self.end).normalized()

        if rect:
            painter.drawPixmap(rect, self.fullscreen.copy(rect))
            pen = QtGui.QPen(QtCore.Qt.green, 2)
            painter.setPen(pen)
            painter.drawRect(rect)

            # 如果是固定状态，绘制 8 个控制点
            if self.fixed_rect:
                painter.setBrush(QtGui.QBrush(QtCore.Qt.green))
                for pt in self.resize_handles(rect):
                    painter.drawEllipse(pt, 4, 4)

    def resize_handles(self, rect):
        """返回矩形 8 个控制点的 QPoint"""
        return [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
            QtCore.QPoint(rect.center().x(), rect.top()),     # 上中
            QtCore.QPoint(rect.center().x(), rect.bottom()),  # 下中
            QtCore.QPoint(rect.left(), rect.center().y()),    # 左中
            QtCore.QPoint(rect.right(), rect.center().y()),   # 右中
        ]

    def hit_test(self, pos):
        """检测鼠标是否点中某个控制点"""
        if not self.fixed_rect:
            return None
        for i, pt in enumerate(self.resize_handles(self.fixed_rect)):
            handle_rect = QtCore.QRectF(pt.x()-6, pt.y()-6, 12, 12)
            if handle_rect.contains(pos):
                return i
        return None

    def mouseDoubleClickEvent(self, event):
        if not self.is_active:
            return
        if event.button() == QtCore.Qt.LeftButton:
            if self.toolbar:
                self.toolbar.ok_do_it()

    def mousePressEvent(self, event):
        if not self.is_active:
            return
        if event.button() == QtCore.Qt.LeftButton:
            if self.fixed_rect:
                idx = self.hit_test(event.pos())
                if idx is not None:
                    self.dragging_handle = idx
                elif self.fixed_rect.contains(event.pos()):
                    # 进入整体移动模式
                    self.moving_rect = True
                    self.move_offset = event.pos() - self.fixed_rect.topLeft()
                else:
                    self.dragging_handle = None
            else:
                self.begin = event.pos()
                self.end = self.begin
            self.update()
        elif event.button() == QtCore.Qt.RightButton:
            if self.fixed_rect and self.hit_test(event.pos()) is None:
                self.fixed_rect = None
                self.moving_rect = False
                if self.toolbar:
                    self.toolbar.close()
                    self.toolbar = None
                self.update()

    def mouseMoveEvent(self, event):
        if not self.is_active:
            return

        if event.buttons() & QtCore.Qt.LeftButton:
            if self.fixed_rect and self.dragging_handle is not None:
                # 🔹 调整大小
                r = self.fixed_rect
                if self.dragging_handle == 0:
                    r.setTopLeft(event.pos())
                elif self.dragging_handle == 1:
                    r.setTopRight(event.pos())
                elif self.dragging_handle == 2:
                    r.setBottomLeft(event.pos())
                elif self.dragging_handle == 3:
                    r.setBottomRight(event.pos())
                elif self.dragging_handle == 4:
                    r.setTop(event.pos().y())
                elif self.dragging_handle == 5:
                    r.setBottom(event.pos().y())
                elif self.dragging_handle == 6:
                    r.setLeft(event.pos().x())
                elif self.dragging_handle == 7:
                    r.setRight(event.pos().x())
                self.fixed_rect = r.normalized()

            elif self.fixed_rect and self.moving_rect:
                # 🔹 整体移动
                top_left = event.pos() - self.move_offset
                r = QtCore.QRect(top_left, self.fixed_rect.size())
                # 限制在屏幕范围内
                r = r.intersected(self.rect())
                self.fixed_rect = r

            elif not self.fixed_rect:
                self.end = event.pos()

            # 🔹 移动 ToolBar 位置
            if self.toolbar and self.fixed_rect:
                geo = self.fixed_rect.translated(self.geometry().topLeft())
                self.toolbar.move(geo.left(), geo.bottom() + 5)

            self.update()
        else:
            # 🔹 光标变化
            idx = self.hit_test(event.pos())
            if idx is None:
                if self.fixed_rect and self.fixed_rect.contains(event.pos()):
                    self.setCursor(QtCore.Qt.SizeAllCursor)  # 移动模式
                else:
                    self.setCursor(QtCore.Qt.CrossCursor)
            elif idx in (6, 7):
                self.setCursor(QtCore.Qt.SizeHorCursor)
            elif idx in (4, 5):
                self.setCursor(QtCore.Qt.SizeVerCursor)
            elif idx in (0, 3):
                self.setCursor(QtCore.Qt.SizeFDiagCursor)
            elif idx in (1, 2):
                self.setCursor(QtCore.Qt.SizeBDiagCursor)

    def mouseReleaseEvent(self, event):
        if not self.is_active:
            return
        if event.button() == QtCore.Qt.LeftButton:
            if not self.fixed_rect:
                rect = QtCore.QRect(self.begin, self.end).normalized()
                if rect.width() > 5 and rect.height() > 5:
                    self.fixed_rect = rect
                    screenshot = self.fullscreen.copy(rect)
                    if self.toolbar:
                        self.toolbar.close()
                    self.toolbar = ToolBar(self, rect, screenshot)
            self.dragging_handle = None
            self.moving_rect = False
            self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
            self.toolbar.close()
        elif event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self.toolbar:
                self.toolbar.ok_do_it()


def show_capture_screen(parent):

    app = QtWidgets.QApplication.instance()
    owns_app = False
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
        owns_app = True

    screenshots = []  # 解决不了在maya里无法识别双屏幕的问题，待定
    for screen in app.screens():
        print("screen:", screen)
        # screen = QtGui.QGuiApplication.primaryScreen()
        ss = ScreenShot(screen, parent)
        ss.setParent(None)
        screenshots.append(ss)
        ss.show()

    def update_active_screen():
        pos = QtGui.QCursor.pos()
        for s in screenshots:
            if s.geometry().contains(pos):
                if ScreenShot.active_instance != s:
                    if ScreenShot.active_instance:
                        ScreenShot.active_instance.is_active = False
                        ScreenShot.active_instance.update()
                    ScreenShot.active_instance = s
                    s.is_active = True
                    s.update()
                return

    timer = QtCore.QTimer()
    timer.timeout.connect(update_active_screen())
    timer.start(100)

    if owns_app:
        del app
    # return snipper.result_pixmap


class HotkeyApp(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.start_screenshot()

    def start_screenshot(self):
        self.screenshots = []
        for screen in self.screens():
            ss = ScreenShot(screen)
            self.screenshots.append(ss)
            ss.show()

        # 定时器轮询鼠标位置 → 激活屏幕
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_active_screen)
        self.timer.start(100)

    def update_active_screen(self):
        pos = QtGui.QCursor.pos()
        for ss in self.screenshots:
            if ss.geometry().contains(pos):
                if ScreenShot.active_instance != ss:
                    if ScreenShot.active_instance:
                        ScreenShot.active_instance.is_active = False
                        ScreenShot.active_instance.update()
                    ScreenShot.active_instance = ss
                    ss.is_active = True
                    ss.update()
                return

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     pos = QCursor.pos()
#     for screen in app.screens():
#         if screen.geometry().contains(pos):
#             target_screen = screen
#             break
#     else:
#         target_screen = app.primaryScreen()
#     tool = ScreenCaptureTool(target_screen)
#     # tool.initUI()
#     sys.exit(app.exec_())


if __name__ == "__main__":
    app = HotkeyApp(sys.argv)
    sys.exit(app.exec_())


# root = tk.Tk()
# root.wm_attributes('-topmost', 1)

# root.overrideredirect(True)  # 隐藏窗口的标题栏
# root.attributes("-alpha", 0.3)    # 窗口透明度70 %
# root.attributes("-alpha", 0.4)  # 窗口透明度60 %
# root.geometry("300x200+10+10")      # 设置窗口大小与位置
# root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))
# root.configure(bg="blue")

# 当工具条
# canvas = tk.Canvas(root)
# canvas.configure(width=300)
# canvas.configure(height=100)
# canvas.configure(bg="yellow")
# canvas.configure(highlightthickness=0)  # 高亮厚度
# canvas.place(x=(root.winfo_screenwidth() - 500), y=(root.winfo_screenheight() - 300))
# canvas.create_text(150, 50, font='Arial -20 bold', text='ESC退出，假装工具条')

# 再创建1个Canvas用于圈选
# cv = tk.Canvas(root)
# x, y = 0, 0
# xstart, ystart = 0, 0


# def move(event):
#     global x, y, xstart, ystart
#     new_x = (event.x - x) + canvas.winfo_x()
#     new_y = (event.y - y) + canvas.winfo_y()
#     s = "300x200+" + str(new_x) + "+" + str(new_y)
#     canvas.place(x=new_x - xstart, y=new_y - ystart)
#     print("s = ", s)
#     print(root.winfo_x(), root.winfo_y())
#     print(event.x, event.y)


# 鼠标左键按下
# def button_1(event):
#     global x, y, xstart, ystart
#     x, y = event.x, event.y
#     xstart, ystart = event.x, event.y
#     print("event.x, event.y = ", event.x, event.y)
#     xstart, ystart = event.x, event.y
#     cv.configure(height=1)
#     cv.configure(width=1)
#     cv.place(x=event.x, y=event.y)


# 鼠标左键按下并移动
# def b1_Motion(event):
#     global x, y
#     x, y = event.x, event.y
#     print("event.x, event.y = ", event.x, event.y)
#     cv.configure(height=event.y - ystart)
#     cv.configure(width=event.x - xstart)


# 鼠标左键松开
# def buttonRelease_1(event):
#     global x, y, xstart, ystart
#     x, y = event.x, event.y
#     print("event.x, event.y = ", event.x, event.y)
#     Pstart = [0, 0]
#     cv.place_forget()
#     # img = pyautogui.screenshot(region=[xstart, ystart, x - xstart, y - ystart])  # x,y,w,h
#     img = ImageGrab.grab().crop((xstart, ystart, x - xstart, y - ystart))
#     img.save('screenshot.png')


# 退出
# def sys_out(even):
#     root.destroy()
#     func()


# 绑定事件
# canvas.bind("<B1-Motion>", move)
# 绑定事件到Esc键，当按下Esc键就会调用sys_out函数，弹出对话框
# root.bind('<Escape>', sys_out)
# root.bind("<Button-1>", button_1)
# root.bind("<B1-Motion>", b1_Motion)
# root.bind("<ButtonRelease-1>", buttonRelease_1)
# img_png = None


# def func():
#     root1 = tk.Tk()
#     root1.wm_attributes('-topmost', 1)
#     img_open = Image.open("screenshot.png")
#     global img_png
#     img_png = ImageTk.PhotoImage(img_open)
#     label_img = tk.Label(root1, image=img_png)
#     label_img.pack()


# root.mainloop()