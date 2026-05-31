#coding: gbk

import pymel.core as pm
import maya.cmds as cmds

def create_base():
    Model,Joint,Other=[None,None,None]
    if pm.objExists("Model") or pm.objExists("Joint") or pm.objExists("Other"):
        pm.displayWarning(u"��ǰ�������Ѵ���Model,Joint,Other��")
        return
    else:
        Model=pm.createNode("transform",name="Model")
        Joint=pm.createNode("transform",name="Joint")
        Other=pm.createNode("transform",name="Other")
        OldGrp=pm.createNode("transform",name="OldGrp")
        OldGrp.setAttr("visibility",False)
        Model.setParent(OldGrp)
        Joint.setParent(OldGrp)
        Other.setParent(OldGrp)
    return [Model,Joint,Other]

def Organize_hierarchy():
    Model,Joint,Other=create_base()
    default = [u'persp', u'top', u'front', u'side']
    topNodes=pm.ls(assemblies=1)
    for topNode in topNodes:
        if not topNode in default:
            if topNode.type() == "joint":
                topNode.setParent(Joint)
                jnt_childs=topNode.getChildren(ad=1)
                for jnt_child in jnt_childs:
                    if not jnt_child.type() == "joint":
                        child=get_child_joint(jnt_child)
                        if child:
                            jnt_child.setParent("Other")

            elif topNode.type() == "transform":
                shape=topNode.getShape()
                if shape:
                    if shape.type() == "mesh":
                        shape.getParent().setParent(Model)
                    else:
                        shape.getParent().setParent(Other)
    new_Model = pm.duplicate(Model)[0]
    new_Joint = pm.duplicate(Joint)[0]
    new_Model.setParent(world=1)
    new_Joint.setParent(world=1)
    pm.makeIdentity(new_Joint, apply=True, scale=True)

    locattrs=['tx','ty','tz','rx','ry','rz','sx','sy','sz']
    old_Model=Model.getChildren()
    old_Joint=Joint.getChildren(ad=1)
    dup_Joint=new_Joint.getChildren(ad=1)
    for index,old_jnt in enumerate(old_Joint):
        jnt=pm.rename(old_jnt, old_jnt + "_old")
        if dup_Joint[index].type()=="joint":
            dup_Joint[index].radius.set(0.5)
    for index,mod in enumerate(new_Model.getChildren()):
        for locattr in locattrs:
            mod.setAttr(locattr,lock=False)
        pm.makeIdentity(mod, apply=True, translate=True)
        pm.makeIdentity(mod, apply=True, rotate=True)
        pm.makeIdentity(mod, apply=True, scale=True)
        old_model=pm.rename(old_Model[index],old_Model[index]+"_old")
        skindict=get_influence(old_model)
        for geo in skindict:
            new_geo=str(geo).replace("_old","")
            new_influence=[str(i).replace("_old","") for i in skindict[geo]]
            #cmds.select(new_geo,new_influence)
            #cmds.SmoothBindSkin()
            cmds.skinCluster(new_influence,new_geo)
            pm.copySkinWeights(ss=getSkinCluster(geo),ds=getSkinCluster(new_geo),
                               noMirror=1,surfaceAssociation="closestPoint",
                               influenceAssociation="closestJoint")

def Organize_hierarchy_01():
    if cmds.objExists("|Group|Geometry"):
        Group="|Group"
        Geometry="|Group|Geometry"
        DeformationSystem = "|Group|Main|DeformationSystem"
        cmds.parent("OldGrp",Group)
        for i in cmds.listRelatives("|Model1",c=1):
            cmds.parent(i,Geometry)
        for i in cmds.listRelatives("|Joint1",c=1):
            cmds.parent(i,DeformationSystem)

        cmds.parent("|Group|Main|DeformationSystem|Root_M","|Group|Main|MotionSystem")
        cmds.delete("|Model1","|Joint1")


def __Organize_hierarchy():
    Model,Joint,Other=create_base()
    default = [u'persp', u'top', u'front', u'side']
    topNodes=pm.ls(assemblies=1)
    for topNode in topNodes:
        if not topNode in default:
            if topNode.type() == "joint":
                topNode.setParent(Joint)
                jnt_childs=topNode.getChildren(ad=1)
                for jnt_child in jnt_childs:
                    if not jnt_child.type() == "joint":
                        if jnt_child.type() == "transform":
                            transform=jnt_child
                        else:
                            transform=jnt_child.getParent()
                        if transform:
                            cur_childs=transform.getChildren(ad=1)
                            cur_childs=cur_childs+[transform]
                            for cur_child in cur_childs:
                                if cur_child.type()=="joint":
                                    parent_joint=get_parent_joint(cur_child)
                                    cur_child.setParent(parent_joint)
                                elif cur_child.type()=="transform":
                                    cur_child.setParent(Other)
                        continue
            elif topNode.type() == "transform":
                shape=topNode.getShape()
                if shape:
                    if shape.type() == "mesh":
                        shape.getParent().setParent(Model)
                    else:
                        shape.getParent().setParent(Other)
    new_Model=pm.duplicate(Model)[0]
    new_Joint=pm.duplicate(Joint.getChildren())[0]
    new_Model.setParent(world=1)
    new_Joint.setParent(world=1)
    pm.makeIdentity(new_Joint,apply=True,scale=True)

def get_parent_joint(node):
    parent=node.getParent()
    print parent
    if parent.type()=="joint":
        return parent
    elif not parent:
        return None
    parent=get_parent_joint(parent)
    return parent

def get_child_joint(node):
    children=node.getChildren(ad=1)
    isjoint=False
    for child in children:
        if child.type()=="joint":
            isjoint=False
            return False
        else:
            isjoint=True
    if isjoint:
        return True
            
def hasShape(node):
    if hasattr(node,"getShape"):
        hasshape=node.getShape()
        if hasshape:
            return True
        else:
            return False
    else:
        return False

def getSkinCluster(obj):
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

def get_influence(geo):
    influences={}
    skincluster=getSkinCluster(geo)
    influence=skincluster.getInfluence()
    influences[geo]=influence
    return influences

def AccConvertFbx2Rig_cmd():
    AccConvertFbx2Rig()