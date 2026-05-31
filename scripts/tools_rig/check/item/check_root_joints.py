#coding: utf-8

import maya.cmds as cmds
import pymel.core as pm

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查蒙皮的骨骼是否在根骨骼DeformationSystem下"
        self.iscolor=True
        self.results=[]

    def getSkinCluster(self,obj):
        skinCluster = None

        if isinstance(obj, str):
            obj = pm.PyNode(obj)
        try:
            if (pm.nodeType(obj.getShape())
                    in ["mesh", "nurbsSurface", "nurbsCurve"]):

                for shape in obj.getShapes():
                    try:
                        for skC in pm.listHistory(shape, type="skinCluster"):
                            try:
                                if skC.getGeometry()[0] == shape:
                                    skinCluster = skC
                            except Exception:
                                pass
                    except Exception:
                        pass
        except Exception:
            pm.displayWarning("%s: is not supported." % obj.name())

        return skinCluster

    def get_root_joints(self):
        res=[]
        Root = pm.ls("DeformationSystem")
        Model=pm.ls("Group|Geometry")

        if len(Model) == 1:
            if Root:
                Root=Root[0]
            Model = pm.PyNode(Model[0])
            all_mesh = list(set([i.getParent() for i in Model.getChildren(ad=1) if pm.nodeType(i) == "mesh"]))
            for mesh in all_mesh:
                skin = self.getSkinCluster(mesh)
                if skin:
                    infs = skin.getInfluence()
                    for inf in infs:
                        if not inf.isChildOf(Root):
                            if inf == Root:
                                continue
                            res.append(inf)
        return res

    def check(self):
        res=self.get_root_joints()
        if res:
            self.results.extend(res)
            self.iscolor=False
            pm.select(res)
        else:
            self.results=[]
            self.iscolor = True

    def run(self):
        if self.results:
            pm.select(self.results)