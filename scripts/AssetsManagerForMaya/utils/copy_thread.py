#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from PySide2.QtCore import QThread, Signal


class CopyThread(QThread):
    step_signal = Signal(int)
    file_signal = Signal(str)

    def __init__(self, src, dst):
        super(CopyThread, self).__init__()
        self.src = src
        self.dst = dst
        self.total_files = 0
        self.copied_files = 0

    def run(self):
        self.total_files = self.count_files(self.src)
        self.copytree(self.src, self.dst)

    def count_files(self, path):
        count = 0
        for root, dirs, files in os.walk(path):
            count += len(files)
        return count

    def copytree(self, src, dst, symlinks=False, ignore=None):
        if not os.path.exists(dst):
            os.makedirs(dst)
            shutil.copystat(src, dst)

        lst = os.listdir(src)
        if ignore:
            excl = ignore(src, lst)
            lst = [x for x in lst if x not in excl]

        for item in lst:
            # self.file_signal.emit(f"installing {item} ...")
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if symlinks and os.path.islink(s):
                if os.path.lexists(d):
                    self.file_signal.emit(f"removing {d} ...")
                    os.remove(d)
                os.symlink(os.readlink(s), d)
                try:
                    st = os.lstat(s)
                    mode = stat.S_IMODE(st.st_mode)
                    os.lchmod(d, mode)
                except:
                    pass  # lchmod not available

            if os.path.isdir(s):
                self.file_signal.emit(f"installing {s} ...")
                self.copytree(s, d, symlinks, ignore)
            else:
                self.file_signal.emit(f"installing {s} ...")
                shutil.copy2(s, d)
                self.copied_files += 1
                percent = int((self.copied_files / self.total_files) * 100)
                self.step_signal.emit(percent)

            # if self.step < 99:
            #     self.step += 1
            #     # self.step = round(self.step)
            #     self.step_signal.emit(self.step)

