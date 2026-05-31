#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ui_batch_copyskin_widget
reload(ui_batch_copyskin_widget)
from ui_batch_copyskin_widget import ui_batch_copyskin_widget

class ui_main_window(QWidget):

    def __init__(self,parent = None):
        super(ui_main_window,self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.ui_batch_copyskin_widget = ui_batch_copyskin_widget()
        QWidgetvboxLayout = QVBoxLayout(self)
        QWidgetvboxLayout.addWidget(self.ui_batch_copyskin_widget)
        QWidgetvboxLayout.setContentsMargins(0,0,0,0)

if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    ui = ui_main_window()
    ui.show()
    sys.exit(app.exec_())