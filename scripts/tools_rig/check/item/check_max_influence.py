#coding: utf-8

import maya.cmds as cmds
import pymel.core as pm

class NZTF_Check(object):

    def __init__(self):
        self.info=u"检查蒙皮的点的影响数量是否超过8"
        self.iscolor=True
        self.results=[]
        self.max_value=8

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

    def get_max_value(self):
        res=[]
        Model = pm.ls("Group|Geometry")
        if len(Model) == 1:
            Model = pm.PyNode(Model[0])
            all_mesh = list(set([i.getParent() for i in Model.getChildren(ad=1) if pm.nodeType(i) == "mesh"]))
            for mesh in all_mesh:
                skin = self.getSkinCluster(mesh)
                if skin:
                    shape = mesh.getShape()
                    numvtxs=shape.numVertices()
                    for i in range(numvtxs):
                        vtx='%s.vtx[%s]'%(str(mesh),str(i))
                        weights=pm.skinPercent(skin, vtx, q=1, v=1)
                        weights=[w for w in weights if w > 0.001]
                        if len(weights)>self.max_value:
                            res.append(vtx)

        return res

    def check(self):
        res=self.get_max_value()
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