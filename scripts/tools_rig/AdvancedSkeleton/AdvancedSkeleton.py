import pymel.core as pm
import os

class ADV:

    def __init__(self):
        self.cur_path = os.path.dirname(__file__)

    def run_adv(self):
        adv_path=os.path.join(self.cur_path, "AdvancedSkeleton.mel").replace("\\", "/")
        pm.mel.eval("source \"%s\";AdvancedSkeleton;"%(adv_path))

    def run_biped(self):
        adv_path=os.path.join(self.cur_path, "AdvancedSkeletonFiles/Selector/biped.mel").replace("\\", "/")
        pm.mel.eval("source \"%s\";"%(adv_path))

    def run_face(self):
        adv_path=os.path.join(self.cur_path, "AdvancedSkeletonFiles/Selector/face.mel").replace("\\", "/")
        pm.mel.eval("source \"%s\";"%(adv_path))

    def run_picker(self):
        adv_path=os.path.join(self.cur_path, "AdvancedSkeletonFiles/picker/picker.mel").replace("\\", "/")
        pm.mel.eval("source \"%s\";"%(adv_path))

    def run_help(self):
        adv_path=os.path.join(self.cur_path, "AdvancedSkeletonFiles/picker/picker.mel").replace("\\", "/")
        pm.mel.eval("source \"%s\";"%(adv_path))

        help_path = os.path.join(os.path.dirname(__file__), "help")
        doc_path = os.path.join(help_path, "Use documentation.docx")
        os.startfile(doc_path)