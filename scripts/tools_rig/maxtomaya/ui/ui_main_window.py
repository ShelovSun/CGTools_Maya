#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ui_maxtomaya_widget
reload(ui_maxtomaya_widget)
from ui_maxtomaya_widget import ui_maxtomaya_widget

class ui_main_window(QWidget):

    def __init__(self,parent = None):
        super(ui_main_window,self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.ui_maxtomaya_widget = ui_maxtomaya_widget()
        QWidgetvboxLayout = QVBoxLayout(self)
        QWidgetvboxLayout.addWidget(self.ui_maxtomaya_widget)
        QWidgetvboxLayout.setContentsMargins(0,0,0,0)

if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    ui = ui_main_window()
    ui.show()
    sys.exit(app.exec_())