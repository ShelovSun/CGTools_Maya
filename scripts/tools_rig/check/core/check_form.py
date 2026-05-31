# -*- coding: utf-8 -*-

import os
import sys
from functools import partial
import pymel.core as pm
import rig.check
reload(rig.check)
from rig.check.ui.head import *
from rig.check.ui.ui_main_window import ui_main_window


def item(text):
    widget=QWidget()
    layout=QVBoxLayout()
    item_layout=QHBoxLayout()
    button=QPushButton()
    check_button=QPushButton(u"repair")
    info_button=QPushButton(u"?")
    spacer=QSpacerItem(10,10)
    item_layout.addWidget(button)
    item_layout.insertSpacerItem(1,spacer)
    item_layout.addWidget(info_button)
    item_layout.addWidget(check_button)
    item_layout.setStretch(0,1)
    layout.addLayout(item_layout)
    widget.setLayout(layout)
    button.setText(text)
    return [widget,button,check_button,info_button]

class From(QMainWindow):

    def __init__(self,parent = None):
        super(From,self).__init__(parent)

        self.check_classes=[]

        self.setWindowTitle ("rig_check_tool")
        self.setupUI()
        self.getElems()
        self.connections()
        self.get_items()

    def setupUI (self):
        self.ui_main_window=ui_main_window()
        self.setCentralWidget(self.ui_main_window)

    def getElems(self):
        self.check_layout = self.ui_main_window.ui_check_widget.main_Widget.check_layout
        self.check_pushButton=self.ui_main_window.ui_check_widget.main_Widget.check_pushButton

    def connections(self):
        self.check_pushButton.clicked.connect(self.check_all)

    def check_all(self):
        for check_class in self.check_classes:
            self.run_item(*check_class)

    def get_items(self):
        compDir=rig.check.getComponentDirectories()
        trackLoadItem=[]
        for path,comps in compDir.items():
            for item_name in comps:
                index=0
                comp_name=item_name.split(".")[0]
                if comp_name in trackLoadItem:
                    pm.displayWarning("%s already in default"%(comp_name))
                    continue
                else:
                    trackLoadItem.append(comp_name)
                if comp_name=="__init__":
                    continue
                module=rig.check.importComponentGuide(comp_name)
                reload(module)
                check_class=self.get_items_class(comp_name)

                widgets=item(comp_name)
                widget=widgets[0]
                button=widgets[1]
                check_button=widgets[2]
                info_button=widgets[3]
                self.check_layout.insertWidget(index,widget)
                index+=1
                button.clicked.connect(partial(self.run_item,check_class,comp_name,"check",button))
                check_button.clicked.connect(partial(self.run_item,check_class,comp_name,"run"))
                info_button.clicked.connect(partial(self.run_item, check_class, comp_name, "info"))

                check_item_list=[check_class,comp_name,"check",button]
                self.check_classes.append(check_item_list)

    def get_items_class(self,com_type):
        module=rig.check.importComponentGuide(com_type)
        check_class=getattr(module,"NZTF_Check")
        return check_class()

    def run_item(self,check_class,item_type,type="check",button=None):
        if type=="check":
            check_class.check()
            if not check_class.iscolor:
                button.setStyleSheet("color: rgb(255,0,0)")
            else:
                button.setStyleSheet("color: rgb(55,255,0)")
        if type=="run":
            check_class.run()
        if type=="info":
            info=check_class.info
            QMessageBox.information(self,u"说明",info)

if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    ui = From()
    ui.showWinodow()
    sys.exit(app.exec_())