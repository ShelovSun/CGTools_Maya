#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide2 import QtWidgets, QtGui, QtCore

class ThLogoShow(QtWidgets.QDialog):

    def __init__(self, image):
        super(ThLogoShow, self).__init__()
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        layout1 = QtWidgets.QVBoxLayout()
        layout1.setMargin(2)
        layout1.setSpacing(2)
        self.setLayout(layout1)
        movie = QtGui.QMovie(image)
        label = QtWidgets.QLabel(self)
        label.setMovie(movie)
        movie.start()
        layout1.addWidget(label)
        self.show()
        QtWidgets.QApplication.processEvents()
        self.timer = QtCore.QTimer(self)
        self.timer.start(2500)
        self.timer.timeout.connect(self.timeDeleteWin)

    def timeDeleteWin(self):
        self.deleteLater()


if __name__ == '__main__':
    image = 'D:/Google 雲端硬碟/th_tools/Web/logo_web.gif'
    logoShowWin = ThLogoShow(image)