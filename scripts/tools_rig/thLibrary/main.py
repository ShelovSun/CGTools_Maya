#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from .data import font
from .data import rig
from .data import rigLogo
# import sys,codecs
# sys.stdout = codecs.getwriter("utf-8")

class ThShowWin(object):
    fontPath = None
    imagePath = None

    def __init__(self):
        if self.fontPath is None:
            print (u'字型档案路径错误!')
        else:
            ifAddFont = font.addFont(self.fontPath)
            # if ifAddFont == -1:
            #     print(u"字型加载失败")
            # else:
            #     print(u"字型加载成功")
        return

    def logoShowF(self):
        """logo show"""
        if self.imagePath:
            if 'thLogoShowWin' in dir(self):
                del self.thLogoShowWin
            self.thLogoShowWin = rigLogo.ThLogoShow(self.imagePath)


class ThShowDDWin(ThShowWin):

    def __init__(self):
        super(ThShowDDWin, self).__init__()
        # from .data import dd
        self.ddToolsWin = dd.DDToolsQtWin()
        self.logoShowF()


class ThShowRigWin(ThShowWin):

    def __init__(self):
        super(ThShowRigWin, self).__init__()
        # from .data import rig
        self.thRigToolsWin = rig.ThRigToolsQtWin()
        self.logoShowF()


if __name__ == '__main__':
    pass
else:
    openPath = os.path.dirname(__file__)
    fontPath = os.path.join(openPath, 'data/resource/font/Microsoft JhengHei.ttf')
    fontPath = fontPath.replace('\\', '/')
    # fontPath = fontPath.decode('big5')
    setattr(ThShowWin, 'fontPath', fontPath)
    rigImagePath = os.path.join(openPath, 'data/resource/icons/logoShow.gif')
    rigImagePath = rigImagePath.replace('\\', '/')
    # rigImagePath = rigImagePath.decode('big5')
    setattr(ThShowRigWin, 'imagePath', rigImagePath)
    # ddImagePath = os.path.join(openPath, 'data/resource/icons/ddLogoShow.gif')
    # ddImagePath = ddImagePath.replace('\\', '/')
    # ddImagePath = ddImagePath.decode('big5')
    # setattr(ThShowDDWin, 'imagePath', ddImagePath)