import os
import pickle
import json

import pymel.core as pm
import maya.OpenMaya as OpenMaya


def getSkinCluster(obj):
    """Get the skincluster of a given object

    Arguments:
        obj (dagNode): The object to get skincluster

    Returns:
        pyNode: The skin cluster pynode object

    """
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

def skinCopy(sourceMesh=None, targetMesh=None, *args):
    if not sourceMesh or not targetMesh:
        if len(pm.selected()) >= 2:
            sourceMesh = pm.selected()[-1]
            targetMeshes = pm.selected()[:-1]
        else:
            pm.displayWarning("Please select target mesh/meshes and source "
                              "mesh with skinCluster.")
            return
    else:
        targetMeshes = [targetMesh]

        # we check this here, because if not need to check when we work
        # base on selection.
        if isinstance(sourceMesh, str):
            sourceMesh = pm.PyNode(sourceMesh)

    for targetMesh in targetMeshes:
        if isinstance(targetMesh, str):
            sourceMesh = pm.PyNode(targetMesh)

        ss = getSkinCluster(sourceMesh)

        if ss:
            oDef = pm.skinCluster(sourceMesh, query=True, influence=True)
            skinCluster = pm.skinCluster(oDef,
                                         targetMesh,
                                         tsb=True,
                                         nw=1,
                                         n=targetMesh.name() + "_SkinCluster")
            pm.copySkinWeights(ss=ss.stripNamespace(),
                               ds=skinCluster.name(),
                               noMirror=True,
                               ia="oneToOne",
                               sm=True,
                               nr=True)
        else:
            pm.displayError("Source Mesh :" + sourceMesh.name() + " Don't "
                            "have skinCluster")