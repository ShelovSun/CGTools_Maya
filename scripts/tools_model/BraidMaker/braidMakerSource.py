# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.6 (tags/v3.8.6:db45529, Sep 23 2020, 15:37:30) [MSC v.1927 32 bit (Intel)]
# Embedded file name: C:/My_Plugins/Products/Braid_Maker/V01/Development/update3\braidMakerSource.py
# Compiled at: 2018-02-20 05:39:41
import sys, maya.OpenMaya as OM, maya.api.OpenMaya as om, maya.OpenMayaMPx as MPx, maya.cmds as cmds, maya.mel as mel, time
from math import *
from functools import partial
import random as rand, pymel.core as pm, colorsys, json
kPluginCmdName = 'braidMaker'

class scriptedCommand(MPx.MPxCommand):

    def __init__(self):
        MPx.MPxCommand.__init__(self)

    def doIt(self, argList):
        braidMaker()


def Func1(mode='cust'):
    networkNodes = cmds.ls(type='network')
    if networkNodes:
        for node in networkNodes:
            if cmds.attributeQuery('isAtrapStripNode', node=node, exists=True):
                if cmds.getAttr(node + '.isAtrapStripNode'):
                    if mode == 'all':
                        trapStripNodes.append(node)
                    elif mode == 'tras':
                        if cmds.attributeQuery('connectedtrasNode', node=node, exists=True):
                            trapStripNodes.append(node)
                    elif not cmds.attributeQuery('connectedtrasNode', node=node, exists=True):
                        trapStripNodes.append(node)


def Func2():
    return 10
    currMSNode = cmds.getAttr('trapGentrasNode.currenttrapStripNode')
    stripMaxCount = cmds.getAttr(currMSNode + '.stripMaxCount')


def tuts(NullField, *args):
    null = cmds.intSliderGrp(NullField, q=1, v=1)
    import webbrowser
    webbrowser.open('https://www.youtube.com/channel/UCoBLDuGOMNZzb2AmLBBRn9w')


def aboutUs(NullField, *args):
    null = cmds.intSliderGrp(NullField, q=1, v=1)
    import webbrowser
    webbrowser.open('https://www.facebook.com/AKAtools/')


def otherProducts(NullField, *args):
    null = cmds.intSliderGrp(NullField, q=1, v=1)
    import webbrowser
    webbrowser.open('https://gumroad.com/akashcgi')


def myBlog(NullField, *args):
    import webbrowser
    webbrowser.open('http://cg-fry.blogspot.in/2017/02/my-python-tools.html')


def loadScalpMesh(*args):
    global meshName
    global meshShape
    sel = cmds.ls(sl=1)
    if len(sel) == 1:
        selShp = cmds.listRelatives(sel, c=1)[0]
        ot = cmds.objectType(selShp)
        if ot != 'mesh':
            cmds.warning('Please select a Mesh Scalp')
        if ot == 'mesh':
            cmds.DeleteHistory()
            cmds.makeIdentity(apply=1, t=1, r=1, s=1, n=0, pn=1)
            meshName = cmds.ls(sl=1)
            meshShape = cmds.listRelatives(meshName, shapes=True)[0]
            cmds.select(cl=1)


def braidCreate(ChkBoxOrient, segsField, sclField, knotsField, *args):
    orient = cmds.checkBox(ChkBoxOrient, q=1, v=1)
    res = cmds.intSliderGrp(segsField, q=1, v=1)
    brPathCU = cmds.ls(sl=1)
    cmds.delete(ch=1)
    cmds.makeIdentity(apply=1, t=1, r=1, s=1, n=0, pn=1)
    for ee in brPathCU:
        try:
            brPathCUShp = cmds.listRelatives(ee, c=1)[0]
            ot = cmds.objectType(brPathCUShp)
            if ot != 'nurbsCurve':
                cmds.warning('Please select a curve')
            if ot == 'nurbsCurve':
                cmds.rebuildCurve(ee, s=res)
                pathLen = cmds.arclen(ee)
                pathLen = pathLen * 0.995
                scl = cmds.floatSliderGrp(sclField, q=1, v=1)
                knots = cmds.intSliderGrp(knotsField, q=1, v=1)
                knots = knots / 3
                brRadius = scl * knots / (knots / 120.0)
                segs = 20
                knotLen = pathLen / knots / 2
                pntA = (0, 0, 0)
                pntB = (pathLen, 0, 0)
                baseCU = cmds.curve(p=(pntA, pntA, pntB, pntB))
                cmds.rebuildCurve(s=res)
                wrapCU = cmds.duplicate(baseCU)
                cmds.select(wrapCU)
                cmds.scale(0.5, 0.5, 0.5)
                cvPoss = [
                 [
                  1.3759512702062637e-17, -0.17703239251857897, -1.0103873205522689],
                 [
                  5.526349367703409e-17, -3.3367604758780204e-18, -1.057870488481239],
                 [
                  9.237768801350403e-17, 0.17703239251857683, -1.0103873205522689],
                 [
                  2.008158652318611e-16, 0.32811336078597036, -0.8915688362168751],
                 [
                  2.084237469358015e-16, 0.4467750365041061, -0.717912281190296],
                 [
                  2.412238367189832e-16, 0.46986648810004256, -0.4848376353189267],
                 [
                  2.1165299285675998e-16, 0.38200536968894155, -0.2802534801016779],
                 [
                  1.8147230489166768e-16, 0.2366424014903311, -0.14915218212118553],
                 [
                  1.3267661207387816e-16, 0.07964057506966105, -0.04664524737291958],
                 [
                  7.783113474029554e-17, -0.0810733825621417, 0.04748943566311135],
                 [
                  1.3340437274008995e-17, -0.23804668256498707, 0.15018390870364576],
                 [
                  -4.703475117787378e-17, -0.38342395653531186, 0.2809871860416585],
                 [
                  -7.04055699634951e-17, -0.470933911213036, 0.48654097011632125],
                 [
                  -5.172758837668081e-17, -0.44473238810305477, 0.7188590722196905],
                 [
                  -1.8414338540221456e-17, -0.3269168311860355, 0.8926473712538584],
                 [
                  2.0547920082194432e-17, -0.17702163152122039, 1.0139077225185094],
                 [
                  6.198802258278497e-17, -5.580494024628159e-16, 1.062910200009657],
                 [
                  9.89644436467075e-17, 0.17702163152121864, 1.0139077225185094],
                 [
                  1.2726407822081798e-16, 0.32691683118603376, 0.8926473712538606],
                 [
                  1.4468655604044425e-16, 0.44473238810305415, 0.7188590722196919],
                 [
                  1.4164410670647327e-16, 0.4709339112130361, 0.48654097011632186],
                 [
                  9.317641695433563e-17, 0.38342395653531364, 0.28098718604165884],
                 [
                  8.306292428216168e-18, 0.2380466825649871, 0.15018390870364592],
                 [
                  -7.210382655517478e-17, 0.08107338256214265, 0.04748943566311169],
                 [
                  -1.2956873632099258e-16, -0.07964057506966048, -0.04664524737291953],
                 [
                  -1.6741837951550943e-16, -0.2366424014903297, -0.1491521821211843],
                 [
                  -1.775537879238015e-16, -0.38200536968894094, -0.2802534801016772],
                 [
                  -1.84003681492103e-16, -0.46986648810004195, -0.48483763531892266],
                 [
                  -1.2922107312665943e-16, -0.4467750365041084, -0.7179122811902956],
                 [
                  -1.054590005266181e-16, -0.3281133607859709, -0.8915688362168731]]
                cmds.circle(r=1, s=30)
                brLoop = cmds.ls(sl=1)
                cmds.delete(ch=1)
                cmds.select(brLoop[0] + '.cv[*]')
                cvs = cmds.ls(sl=1, fl=1)
                for e, f in zip(cvs, cvPoss):
                    cmds.xform(e, t=f, ws=1)

                cmds.select(brLoop)
                cmds.scale(scl, scl, scl, a=1)
                pos = cmds.xform(brLoop, t=1, ws=1, q=1)
                incr = knotLen / segs
                prr = 0
                prrinc = 1.0 / segs
                brCUs = []
                for g in range(3):
                    cuPnts = []
                    for f in range(knots):
                        for e in range(segs):
                            cuPnt = cmds.pointOnCurve(brLoop, top=True, pr=prr, position=True)
                            cuPnts.append(cuPnt)
                            cmds.xform(brLoop, t=(incr, 0, 0), ws=1, r=1)
                            prr += prrinc
                            if prr >= 1:
                                prr = prr - 1

                    prr += 0.333
                    cmds.curve(p=cuPnts, d=3, n='brCU_01')
                    brCU = pm.ls(sl=1)
                    brCUs.append(brCU)
                    cmds.xform(brLoop, t=pos, ws=1)

                brCU = brCUs[0]
                brCU2 = brCUs[1]
                brCU3 = brCUs[2]
                pm.select(brCU3)
                cmds.xform(brLoop, t=pos, ws=1)
                cmds.delete(brLoop)
                pm.select(brCU, brCU2, brCU3)
                mel.eval('Group 0 1 1;')
                brCUGrp1 = cmds.ls(sl=1)
                mel.eval('makeCurvesDynamic 2 { "1", "0", "1", "1", "0"};')
                hsShp = cmds.ls(sl=1)[0]
                pm.select(brCU, brCU2, brCU3)
                cmds.group(n='brd_CUs')
                brCUGrp = cmds.ls(sl=1)
                hsT = cmds.listRelatives(hsShp, p=1)
                hsAll = cmds.listConnections(hsShp)
                cmds.setAttr(hsShp + '.hairWidthScale[0].hairWidthScale_Interp', 1)
                cmds.setAttr(hsShp + '.hairWidthScale[1].hairWidthScale_Interp', 1)
                cmds.setAttr(hsShp + '.clumpWidth', 0.001)
                cmds.setAttr(hsShp + '.simulationMethod', 1)
                mel.eval('assignBrushToHairSystem;')
                pfxShp = cmds.ls(sl=1)[0]
                pfxT = cmds.listRelatives(pfxShp, p=1)
                brsh = cmds.listConnections(pfxShp)[1]
                cmds.setAttr(brsh + '.globalScale', brRadius)
                cmds.select(pfxShp)
                cmds.PaintEffectsToCurve()
                pfxG = cmds.listConnections(pfxShp)
                brCUs3 = (pfxG[2], pfxG[3], pfxG[4])
                delG = cmds.listRelatives(pfxG[2], p=1)
                delG = cmds.listRelatives(delG, p=1)
                cmds.select(brCUs3)
                cmds.parent(w=1)
                brCUsG = cmds.group(n='braidCUs_Grp_01')
                cmds.delete(delG)
                cmds.select(pfxShp)
                mel.eval('doPaintEffectsToPoly( 1,0,0,1,100000);')
                meshA = cmds.ls(sl=1)[0]
                meshB = cmds.listRelatives(meshA, p=1)
                meshC = cmds.listRelatives(meshB, p=1)
                cmds.select(meshB)
                cmds.rename('braidMesh_01')
                meshB = pm.ls(sl=1)
                cmds.setAttr(pfxShp + '.meshQuadOutput', 1)
                cmds.sets(e=1, forceElement='initialShadingGroup')
                pm.select(meshB, brCUs3)
                cmds.scale(2, 1, 1, a=1)
                plTan = cmds.polyPlane(ch=0, sx=2, sy=2)[0]
                pm.select(meshB, brCUs3, plTan)
                latt = cmds.lattice(divisions=(res, 2, 2), objectCentered=1, ldv=(2,
                                                                                  2,
                                                                                  2))
                cmds.select(brCUGrp)
                lattCU = cmds.lattice(divisions=(res, 2, 2), objectCentered=1, ldv=(2,
                                                                                    2,
                                                                                    2))
                latPnts = (lattCU[1] + '.pt[0][0][0]', lattCU[1] + '.pt[0][0][1]', lattCU[1] + '.pt[0][1][0]', lattCU[1] + '.pt[0][1][1]')
                pl = cmds.polyPlane(ch=0, sx=1, sy=1)[0]
                plPnts = (pl + '.vtx[0]', pl + '.vtx[1]', pl + '.vtx[2]', pl + '.vtx[3]')
                for e, f in zip(latPnts, plPnts):
                    xf = cmds.xform(e, q=1, t=1, ws=1)
                    cmds.xform(f, t=xf, ws=1)

                cmds.setAttr(pl + '.rotateZ', 180)
                cmds.xform(pl, s=(2, 2, 2), a=1)
                cmds.makeIdentity(pl, apply=1, t=1, r=1, s=1, n=0, pn=1)
                cmds.delete(pl, ch=1)
                cmds.select(pl)
                cmds.CreateCluster()
                brClstr = cmds.ls(sl=1)[0]
                cmds.hide()
                cmds.select(cl=1)
                polyExtr = cmds.polyExtrudeFacet(pl, ch=1, keepFacesTogether=1, pvx=-0.1636236144, pvy=0.3921607532, pvz=5.33632759, divisions=res, twist=0, taper=1, off=0, thickness=0, smoothingAngle=100, inputCurve=wrapCU[0])
                cmds.select(polyExtr)
                cmds.rename('braid_shape_graph')
                polyExtr = cmds.ls(sl=1)
                cmds.setAttr(polyExtr[0] + '.taperCurve[0].taperCurve_FloatValue', 0.5)
                cmds.setAttr(polyExtr[0] + '.taperCurve[1].taperCurve_Interp', 1)
                cmds.setAttr(polyExtr[0] + '.taperCurve[0].taperCurve_Interp', 1)
                cmds.setAttr(polyExtr[0] + '.offset', -0.05)
                cmds.select(lattCU, pl)
                cmds.CreateWrap()
                plBase = pl + 'Base'
                cmds.setAttr(latt[0] + '.outsideLattice', 1)
                cmds.delete(hsAll[1])
                A = pm.listConnections(brCU)
                B = pm.listRelatives(A)[0]
                C = pm.listConnections(B)[4]
                cu = [
                 baseCU]
                cmds.select(cl=1)
                jnts = res
                crSplIK = 1
                jntRad = 0.1
                for e in cu:
                    shp = cmds.listRelatives(e, s=1)[0]
                    uParam = cmds.getAttr(shp + '.minMaxValue')[0][1] - 0.0001
                    incr = uParam / jnts
                    v = 0
                    ts = []
                    for f in range(jnts + 1):
                        t = cmds.pointOnCurve(e, p=1, pr=v)
                        ts.append(t)
                        v += incr

                    cnt = 0
                    for g in ts:
                        jnt = cmds.joint(p=g)
                        cmds.setAttr(jnt + '.radius', jntRad)
                        if cnt == 0:
                            Fjnt = jnt
                        if cnt == jnts:
                            Ljnt = jnt
                        cnt += 1

                    if crSplIK == 1:
                        cmds.select(Fjnt, Ljnt, e)
                        ik = cmds.ikHandle(sol='ikSplineSolver', ccv=0)[0]
                    cmds.select(cl=1)

                cmds.select(jnt, latt[1])
                cmds.skinCluster()
                bs = cmds.blendShape(ee, baseCU, origin='world', tc=0)[0]
                cmds.setAttr(bs + '.' + ee, 1)
                grpSetup = pm.group(brCUGrp, brCUGrp1, hsT, latt[1], latt[2], pfxT, lattCU[1], lattCU[2], pl, ik, pfxT, Fjnt, plBase, wrapCU, baseCU, brClstr, n='braidSetup_01')
                grpOutput = pm.group(meshB, brCUsG, n='braid_Mesh_Curves')
                grpMain = pm.group(grpSetup, grpOutput, n='braid_Grp_01')
                pm.hide(grpSetup)
                pm.delete(pm.listRelatives(C, p=1))
                cmds.delete(meshC)
                RP = (
                 hsShp, brsh, polyExtr[0], ik, brClstr)
                RP = json.dumps(RP)
                pm.addAttr(meshB[0], ln='RP', dt='string')
                pm.setAttr(meshB[0] + '.RP', l=0)
                pm.setAttr(meshB[0] + '.RP', RP, type='string', l=1)
                posT = cmds.xform(plTan + '.vtx[1]', q=1, t=1, ws=1)
                if orient == 0:
                    pass
                if orient == 1:
                    if len(meshName) == 0:
                        pass
                    if len(meshName) == 1:
                        cmds.select(meshName)
                        meshe2 = cmds.duplicate()
                        cmds.ConvertSelectionToVertices()
                        vtx = cmds.ls(sl=1, fl=1)
                        nn = []
                        x = 0.05
                        for v in vtx:
                            p = x
                            nn.append(p)

                        cmds.moveVertexAlongDirection(n=nn)
                        clsPntNode = cmds.createNode('closestPointOnMesh')
                        cmds.connectAttr(meshShape + '.worldMatrix', clsPntNode + '.inputMatrix')
                        cmds.connectAttr(meshShape + '.worldMesh', clsPntNode + '.inMesh')
                        meshe2Shape = cmds.listRelatives(meshe2, shapes=True)
                        clsPntNode2 = cmds.createNode('closestPointOnMesh')
                        cmds.connectAttr(meshe2Shape[0] + '.worldMatrix', clsPntNode2 + '.inputMatrix')
                        cmds.connectAttr(meshe2Shape[0] + '.worldMesh', clsPntNode2 + '.inMesh')
                        endPos = cmds.xform(ee + '.cv[0]', query=True, worldSpace=True, translation=True)
                        cmds.setAttr(clsPntNode + '.ip', endPos[0], endPos[1], endPos[2], type='double3')
                        posC = cmds.getAttr(clsPntNode + '.p')[0]
                        cmds.setAttr(clsPntNode2 + '.ip', posC[0], posC[1], posC[2], type='double3')
                        posN = cmds.getAttr(clsPntNode2 + '.p')[0]
                        cmds.delete(clsPntNode, clsPntNode2, meshe2, plTan)
                        posNn = [
                         posN[0] - posC[0], posN[1] - posC[1], posN[2] - posC[2]]
                        posTn = [posT[0] - posC[0], posT[1] - posC[1], posT[2] - posC[2]]
                        posCn = [0, 0, 0]
                        posWorld = [0, 1, 0]
                        vNor = om.MVector(posNn).normal()
                        vPos = om.MVector(posCn).normal()
                        vTan = om.MVector(posTn).normal()
                        vWorld = om.MVector(posWorld).normal()
                        dot = vNor * vTan
                        dot2 = vNor * vWorld
                        ang = om.MAngle(acos(dot)).asDegrees()
                        angl = 90 - ang
                        if dot2 > 0:
                            cmds.setAttr(ik + '.roll', angl)
                        if dot2 < 0:
                            cmds.setAttr(ik + '.roll', 180 - angl)
                cmds.delete(plTan)
                pm.select(meshB)
        except:
            pass


def braidBake(*args):
    try:
        meshB = pm.ls(sl=1)
        for ee in meshB:
            brOutput = pm.listRelatives(ee, p=1)
            brGrp = pm.listRelatives(brOutput, p=1)
            name = brGrp[0].split('_')
            if name[0] == 'braid':
                pm.select(brOutput)
                cmds.delete(ch=1)
                cmds.makeIdentity(apply=1, t=1, r=1, s=1, n=0, pn=1)
                cmds.parent(w=1)
                pm.delete(brGrp)
                pm.setAttr(ee + '.RP', l=0)
                pm.deleteAttr(ee + '.RP')

    except:
        pass


def braidEdit(*args):
    global a
    global b
    global c
    global sla
    global slaa
    global slb
    global slbb
    global slc
    global slcc
    global vala
    global valb
    global valc

    def copyGraph(stringo, sele, *args):
        global Fvals
        global Pvals
        global profileNos1
        profiles = cmds.listAttr(sele, m=1, st=stringo)
        profileNos1 = []
        profileNos2 = []
        for e in profiles:
            nm = e.split('[')
            if len(nm) > 1:
                profileNos2.append(e)
                nm2 = e.split(stringo)
                profileNos1.append(nm2[1])

        profileName = profileNos2[0].split('[')[0]
        Fvals = []
        Pvals = []
        for e in profileNos1:
            floatVal = cmds.getAttr(sele + '.' + profileName + e + '.' + profileName + '_FloatValue')
            Fvals.append(floatVal)
            posVal = cmds.getAttr(sele + '.' + profileName + e + '.' + profileName + '_Position')
            Pvals.append(posVal)

    def pasteGraph(stringo2, sele2, x, *args):
        for i in sele2:
            profiles = cmds.listAttr(i[x], m=1, st=stringo2)
            profileNos = []
            for e in profiles:
                nm = e.split('[')
                if len(nm) > 1:
                    profileNos.append(e)

            profileName = profileNos[0].split('[')[0]
            c = 0
            for e in profileNos:
                if c > 0:
                    cmds.removeMultiInstance(i[x] + '.' + e)
                c += 1

            for a, b, c in zip(Pvals, Fvals, profileNos1):
                cmds.setAttr(i[x] + '.' + profileName + c + '.' + profileName + '_FloatValue', b)
                cmds.setAttr(i[x] + '.' + profileName + c + '.' + profileName + '_Position', a)
                cmds.setAttr(i[x] + '.' + profileName + c + '.' + profileName + '_Interp', 1)

    def updateGraphA(*args):
        copyGraph(a, sla)
        pasteGraph(a, slaa, vala)

    def updateGraphB(*args):
        copyGraph(b, slb)
        pasteGraph(b, slbb, valb)

    def updateGraphC(*args):
        copyGraph(c, slc)
        pasteGraph(c, slcc, valc)

    windowID = 'braidEdit'
    if cmds.window(windowID, exists=1):
        cmds.deleteUI(windowID)
    cmds.window(windowID, title='Braid Editor', menuBar=1, h=500, w=400)
    cmds.columnLayout(adjustableColumn=1)
    try:
        mesh = cmds.ls(sl=1)
        RPs = []
        RPs0 = []
        RPs1 = []
        RPs2 = []
        RPs3 = []
        RPs4 = []
        for e in mesh:
            RPattr = cmds.getAttr(e + '.RP')
            RP = json.loads(RPattr)
            RPs.append(RP)
            RPs0.append(RP[0])
            RPs1.append(RP[1])
            RPs2.append(RP[2])
            RPs3.append(RP[3])
            RPs4.append(RP[4])

        RPs0thinning = []
        RPs0clumpWidth = []
        RPs0hairWidthScale = []
        for e in RPs0:
            a = e + '.thinning'
            RPs0thinning.append(a)
            a = e + '.clumpWidth'
            RPs0clumpWidth.append(a)
            a = e + '.hairWidthScale'
            RPs0hairWidthScale.append(a)

        RPs1globalScale = []
        for e in RPs1:
            a = e + '.globalScale'
            RPs1globalScale.append(a)

        RPs2taper = []
        for e in RPs2:
            a = e + '.taper'
            RPs2taper.append(a)

        RPs3roll = []
        RPs3twist = []
        for e in RPs3:
            a = e + '.roll'
            RPs3roll.append(a)
            a = e + '.twist'
            RPs3twist.append(a)

        RPs4Xscl = []
        RPs4Yscl = []
        for e in RPs4:
            a = e + '.scaleZ'
            RPs4Xscl.append(a)
            a = e + '.scaleY'
            RPs4Yscl.append(a)

        cmds.select(cl=1)
        cmds.separator(h=20, w=250)
        cmds.button(label='Edit Selected Braids', command=partial(braidEdit), bgc=(0.45,
                                                                                   0.6,
                                                                                   0.7), w=195)
        cmds.separator(h=20, w=250)
        cmds.text(label='Braid strand width graph')
        a = 'hairWidthScale'
        sla = RP[0]
        slaa = RPs
        vala = 0
        cmds.gradientControl(at='%s.hairWidthScale' % RP[0], w=300, h=100)
        RPs0hairWidthScale
        cmds.popupMenu()
        cmds.menuItem(l='Update Graphs', c=partial(updateGraphA))
        cmds.menuItem(l='Copy Graph', c=partial(copyGraph, a, sla))
        cmds.menuItem(l='Paste Graph', c=partial(pasteGraph, a, slaa, vala))
        cmds.floatSliderGrp('braidStrRadius', label='Braid strand Width', field=1, step=0.01, minValue=1, maxValue=800, v=70, precision=2, w=350)
        cmds.connectControl('braidStrRadius', RPs1globalScale)
        cmds.floatSliderGrp('brThinning', label='Strand length Variation', f=1, step=1, minValue=0, maxValue=1, v=0, precision=2, w=350)
        cmds.connectControl('brThinning', RPs0thinning)
        cmds.separator(h=20, w=250)
        cmds.text(label='Braid bundle width graph')
        b = 'taperCurve'
        slb = RP[2]
        slbb = RPs
        valb = 2
        cmds.gradientControl(at='%s.taperCurve' % RP[2], w=300, h=100)
        cmds.popupMenu()
        cmds.menuItem(l='Update Graphs', c=partial(updateGraphB))
        cmds.menuItem(l='Copy Graph', c=partial(copyGraph, b, slb))
        cmds.menuItem(l='Paste Graph', c=partial(pasteGraph, b, slbb, valb))
        cmds.floatSliderGrp('braidBundleWidth', label='Braid Bundle Width', field=1, step=0.01, minValue=0, maxValue=10, v=0, precision=2, w=350)
        cmds.connectControl('braidBundleWidth', RPs2taper)
        cmds.separator(h=20, w=250)
        cmds.text(label='Braid jitter graph')
        c = 'clumpWidthScale'
        slc = RP[0]
        slcc = RPs
        valc = 0
        cmds.gradientControl(at='%s.clumpWidthScale' % RP[0], w=300, h=100)
        cmds.popupMenu()
        cmds.menuItem(l='Update Graphs', c=partial(updateGraphC))
        cmds.menuItem(l='Copy Graph', c=partial(copyGraph, c, slc))
        cmds.menuItem(l='Paste Graph', c=partial(pasteGraph, c, slcc, valc))
        cmds.floatSliderGrp('clumpWidth', label='Braid jitter radius ', field=1, step=0.01, minValue=0.01, maxValue=1.5, v=0.01, precision=2, w=350)
        cmds.connectControl('clumpWidth', '%s.clumpWidth' % RPs[0][0])
        cmds.connectControl('clumpWidth', RPs0clumpWidth)
        cmds.separator(h=20, w=250)
        cmds.setParent(top=1)
        cmds.floatSliderGrp('brRoll', label='Braid Roll ', f=1, step=1, minValue=-180, maxValue=180, v=0, precision=2, w=350)
        cmds.connectControl('brRoll', RPs3roll)
        cmds.floatSliderGrp('brTwist', label='Braid Twist ', f=1, step=1, minValue=-2000, maxValue=2000, v=0, precision=2, w=350)
        cmds.connectControl('brTwist', RPs3twist)
        cmds.floatSliderGrp('brXscl', label='Braid Scale X', f=1, step=1, minValue=0.1, maxValue=10, v=0, precision=2, w=350)
        cmds.connectControl('brXscl', RPs4Xscl)
        cmds.floatSliderGrp('brYscl', label='Braid Scale Y', f=1, step=1, minValue=0.1, maxValue=10, v=0, precision=2, w=350)
        cmds.connectControl('brYscl', RPs4Yscl)
        cmds.separator(h=20, w=250)
    except:
        cmds.separator(h=50, w=300)
        cmds.text(label='            Please Select a Braid Mesh')
        cmds.separator(h=50, w=300)

    cmds.showWindow(windowID)


def braidMaker():
    windowID = 'braidMake'
    if cmds.window(windowID, exists=1):
        cmds.deleteUI(windowID)
    cmds.window(windowID, title='Braid Maker V 1.0', menuBar=1, h=400, w=450)
    cmds.menu(label=' HELP..!!', tearOff=1)
    NullVal = cmds.intSliderGrp(minValue=0, maxValue=1, value=0, step=1, en=0, vis=0, h=1)
    cmds.menuItem(label='Tutorials', c=partial(tuts, NullVal))
    NullVal = cmds.intSliderGrp(minValue=0, maxValue=1, value=0, step=1, en=0, vis=0, h=1)
    cmds.menuItem(label='About Us', c=partial(aboutUs, NullVal))
    NullVal = cmds.intSliderGrp(minValue=0, maxValue=1, value=0, step=1, en=0, vis=0, h=1)
    cmds.menuItem(label='More Products', c=partial(otherProducts, NullVal))
    NullVal = cmds.intSliderGrp(minValue=0, maxValue=1, value=0, step=1, en=0, vis=0, h=1)
    cmds.menuItem(label='My Blog', c=partial(myBlog, NullVal))
    bg = (0.45, 0.6, 0.7)
    cmds.columnLayout(adjustableColumn=1)
    cmds.text(label=' Tool developed by - AKA Tools    ', bgc=(0.35, 0.4, 0.4), h=25)
    cmds.text(label=' Abhishek Karmakar - aakaashwa@gmail.com    ', bgc=(0.35, 0.4,
                                                                         0.4), h=25)
    cmds.text(label='')
    cmds.setParent('..')
    cmds.frameLayout(label='Create Braid', collapsable=1, collapse=0, bgc=(0.3, 0.4,
                                                                           0.5))
    cmds.columnLayout(adjustableColumn=0)
    cmds.text(label='', w=10)
    cmds.rowColumnLayout(nc=4)
    cmds.text(label='', w=10)
    cmds.button(label='Load Scalp Surface Mesh', command=partial(loadScalpMesh), bgc=bg, w=170)
    cmds.text(label='', w=10)
    ChkBoxOrient = cmds.checkBox(label=' Orient Braids to Scalp Surface ', v=1)
    cmds.setParent('..')
    cmds.text(label='', w=10)
    sclVal = cmds.floatSliderGrp(label='Braid Radius', field=1, minValue=0.1, maxValue=10, precision=2, value=0.4, step=0.1)
    knotsVal = cmds.intSliderGrp(label='Braid Knots', field=1, minValue=6, maxValue=100, value=6, step=1)
    segsVal = cmds.intSliderGrp(label='Deform Resolution', field=1, minValue=10, maxValue=80, value=20, step=1)
    cmds.text(label='', w=10)
    cmds.separator(h=20, w=400)
    cmds.rowColumnLayout(nc=3)
    cmds.button(label='Create Braid', command=partial(braidCreate, ChkBoxOrient, segsVal, sclVal, knotsVal), bgc=bg, w=195)
    cmds.text(label='', w=5)
    cmds.button(label='Edit Braid', command=partial(braidEdit), bgc=bg, w=195)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.button(label='Bake Braid', command=partial(braidBake), bgc=bg, w=395)
    cmds.separator(h=20, w=400)
    cmds.showWindow(windowID)


def cmdCreator():
    return MPx.asMPxPtr(scriptedCommand())