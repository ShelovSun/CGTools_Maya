#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide2 import QtGui

def addFont(fontPath):
    global _installFont
    if '_installFont' not in globals():
        _installFont = QtGui.QFontDatabase.addApplicationFont(fontPath)
    return _installFont


if __name__ == '__main__':
    pass