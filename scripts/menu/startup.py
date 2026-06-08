# -*- coding: utf-8 -*-

import os
import sys
import json

import maya.mel as mel
import pymel.core as pm

sm_temp = "{}/ShotManagerTemp".format(os.environ.get('APPDATA'))
SM_SETTING_JSON = "{}/setting.json".format(sm_temp)
scriptsPathIn = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/')
scriptsPath = scriptsPathIn.replace('/menu', '')
scriptsPathOut = scriptsPathIn.replace('/for_Maya/menu', '')
work_paths = [scriptsPath, scriptsPathIn,
              r"%s/Python/Python37/Lib/site-packages" % scriptsPath,
              r"%s/AssetsManagerForMaya" % scriptsPath,
              r"%s/ShotsManagerForMaya" % scriptsPath,
              r"%s/lib/site-packages" % scriptsPathOut,
              r"%s/tools_ani" % scriptsPath,
              r"%s/tools_ani/StudioLibrary" % scriptsPath,
              r"%s/tools_model" % scriptsPath,
              r"%s/tools_scene" % scriptsPath,
              r"%s/tools_render" % scriptsPath,
              r"%s/tools_rig" % scriptsPath,
              r"%s/tools_sim" % scriptsPath,
              r"%s/tools_view" % scriptsPath,
              r"%s/tools_select" % scriptsPath,
              r"%s/tools_windows" % scriptsPath,
              r"%s/tools_publish" % scriptsPath,
              r"%s/tools_rig/shapes/SHAPES/for_Maya" % scriptsPath,
              r"%s/tools_rig/ngskintools/Contents/for_Maya" % scriptsPath,
              r"%s\gen\publish\tools" % scriptsPath]
for work_path in work_paths:
    if work_path not in sys.path:
        sys.path.append(work_path)

# from pyblish_qml import api
#
# api.register_python_executable("{}/Python/Python39/python.exe".format(scriptsPath))
# api.register_pyqt5("{}/Python/Python38-32/Lib/site-packages".format(scriptsPath))

# import pyblishSetup

mel_script = (
    '$s = `getenv "MAYA_SCRIPT_PATH" `;\n        $s = $s + ";{0}/tools_rig/curveUtil/for_Maya";\n        putenv "MAYA_SCRIPT_PATH" $s').format(
    scriptsPath)
mel.eval(mel_script)
# melll = ('$s = `getenv "MAYA_SCRIPT_PATH" `;\n        $s = $s + ";{0}/mod/arnoldAssistant";\n        putenv "MAYA_SCRIPT_PATH" $s').format(scriptsPath)
# mel.eval(melll)
mel.eval('source "%s/tools_model/arnoldAssistant/Arnold.mel";' % scriptsPath)


def menu_setup():
    """
    安装菜单
    :return:True
    """
    # user = readLoginSetting()['user']
    # password = readLoginSetting()['password']
    if pm.menu("CG", exists=True):
        pm.deleteUI("CG")
    CG = pm.menu("CG",
                 parent="MayaWindow",
                 tearOff=True,
                 allowOptionBoxes=True,
                 label=":: CGTools ::")

    pm.menuItem(parent="CG", label="Update Menu", image="{}/icons/menu_update.png".format(scriptsPath),
                command="import startup;import importlib;importlib.reload(startup);startup.menu_setup()")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # =======================================================A&S manager================================================
    pm.menuItem(parent="CG", label="Assets Manager",
                image="{}/icons/assetsManager_menu.png".format(scriptsPathOut),
                command="import AssetsManager_Maya as AM;AM.showWindow()")
    pm.setParent(CG, menu=True)
    pm.menuItem(parent="CG", label="Shots Manager", image="{}/icons/shotsManager_menu.png".format(scriptsPathOut),
                command="import ShotsManager_Maya as SM;SM.ShotsManager_Run()")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # ========================================================model=====================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True,
                label=":::::  model")  # ,image="{}/icons/modeling_shlf.png".format(scriptsPath))
    pm.menuItem(label="发布模型资产", image="{}/icons/publish.png".format(scriptsPathOut),
                command="import PublishTools.PublishTool as PT;PT.showWindow(0)")
    # command="import tools_model.Mod_Publish_Tool.modPublishTool as MP;MP.showWindow()")
    pm.menuItem(label="资产重命名工具",
                command="import renameMat.renameMat as rm;rm.showWindow()")
    pm.menuItem(label="Material Manager",
                command="import tools_model.DW_MaterialManager.UI as UI;UI.UI()")
    pm.menuItem(label="braid Maker",
                command="import tools_model.BraidMaker.startup as MP;MP.braidMaker()")
    pm.menuItem(label="Arnold助手", command="mel.eval('az_UI;')")
    pm.menuItem(label="Max to Maya",
                image="{}/tools_model/MaxToMaya/MaxToMaya_Files/MaxToMaya_icon.png".format(scriptsPath),
                command="import tools_model.MaxToMaya.MaxToMaya_Files.m2m;m2m.guiMain()")
    pm.menuItem(label="Snow Factory",
                command="import tools_model.SnowFactory.SnowFactory as SF;SF.snowFactoryWindow()")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # ========================================================scene=====================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True,
                label=":::::  scene")  # ,image="{}/icons/modeling_shlf.png".format(scriptsPath))
    pm.menuItem(label="发布场景静态资产", image="{}/icons/publish.png".format(scriptsPathOut),
                command="import tools_publish.PublishTools.PublishTool as PT;PT.showWindow(2)")
    # command="import tools_scene.Scene_Publish_Tool.scenePublishTool as SP;SP.showWindow('FFA','Building')")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # =========================================================rig======================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True, label=":::::  rig")
    pm.menuItem(label="发布绑定资产", image="{}/icons/publish.png".format(scriptsPathOut),
                command="import tools_publish.PublishTools.PublishTool as PT;PT.showWindow(1)")
    # command="import tools_rig.Rig_Publish_Tool.rigPublishTool as RP;RP.showWindow()")
    pm.menuItem(label="Check",
                command="import tools_rig.check.main.maya_load_win as maya_load_win;ui=maya_load_win.MayaLoadWindow();ui.show();")
    pm.menuItem(divider=True)
    pm.menuItem(label="Advanced Skeleton",
                image="{}/tools_rig/AdvancedSkeleton/AdvancedSkeletonFiles/icons/asLogo_32.png".format(scriptsPath),
                tearOff=True, subMenu=True)
    pm.menuItem(label="advancedskeleton",
                image="{}/tools_rig/AdvancedSkeleton/AdvancedSkeletonFiles/icons/AS5.png".format(scriptsPath),
                command="import tools_rig.AdvancedSkeleton.AdvancedSkeleton as AdvancedSkeleton;adv=AdvancedSkeleton.ADV();adv.run_adv();")
    pm.menuItem(label="biped",
                image="{}/tools_rig/AdvancedSkeleton/AdvancedSkeletonFiles/icons/asBiped.png".format(scriptsPath),
                command="import tools_rig.AdvancedSkeleton.AdvancedSkeleton as AdvancedSkeleton;adv=AdvancedSkeleton.ADV();adv.run_biped();")
    pm.menuItem(label="face",
                image="{}/tools_rig/AdvancedSkeleton/AdvancedSkeletonFiles/icons/asFace.png".format(scriptsPath),
                command="import tools_rig.AdvancedSkeleton.AdvancedSkeleton as AdvancedSkeleton;adv=AdvancedSkeleton.ADV();adv.run_face();")
    pm.menuItem(label="picker",
                command="import tools_rig.AdvancedSkeleton.AdvancedSkeleton as AdvancedSkeleton;adv=AdvancedSkeleton.ADV();adv.run_picker();")
    pm.menuItem(divider=True)
    pm.menuItem(label="add adv root",
                command="import tools_rig.AdvancedSkeleton.add_root as add_root;adv=add_root.add_adv_root();")
    pm.menuItem(label="add adv global",
                command="import tools_rig.AdvancedSkeleton.add_root as add_root;adv=add_root.adv_add_global_cmd();")
    pm.setParent("..", menu=True)
    pm.menuItem(label="Max To Maya",
                command="import tools_rig.maxtomaya.main.maya_load_win as maya_load_win;ui=maya_load_win.MayaLoadWindow();ui.show();")
    pm.menuItem(divider=True)
    pm.menuItem(label="TH RIG Tools", image="{}/tools_rig/thLibrary/data/resource/icons/icon.png".format(scriptsPath),
                command="import tools_rig.thLibrary.main as th;th.ThShowRigWin()")
    pm.menuItem(label="Copy Weights(ml)",
                command="import tools_ani.ml_tools.ml_copySkin as ml_copySkin;ml_copySkin.ui()")
    pm.menuItem(label="Batch Copy Weights",
                command="import tools_rig.batch_copyskin.main.maya_load_win as maya_load_win;ui=maya_load_win.MayaLoadWindow();ui.show();")
    pm.menuItem(label="Control Maker", command="mel.eval('controlMaker;')")
    pm.menuItem(label="Riggest Controllers", command="mel.eval('Riggest_controllers;')")
    pm.menuItem(label="NgSkinTool",
                image="{}/tools_rig/ngskintools/Contents/icons/ngSkinTools2ShelfIcon.png".format(scriptsPath),
                command="import ngSkinTools2; ngSkinTools2.open_ui()")  # 失败
    pm.menuItem(label="Shapes", command="mel.eval('SHAPES;')")  # 失败
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # ===================================================animation===========================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True, label=":::::  animation")
    pm.menuItem(label="发布动作库资产", image="{}/icons/publish.png".format(scriptsPathOut),
                command="import tools_publish.PublishTools.PublishTool as PT;PT.showWindow(3)")
    # command="import tools_rig.Rig_Publish_Tool.rigPublishTool as RP;RP.showWindow()")
    pm.menuItem(label="动作小工具",
                command="import tools_ani.Ani_smallTools as SmallTools;SmallTools.ShowUI().createUi()")
    pm.menuItem(label="Spring Magic",
                command="import tools_ani.SpringMagic.main as SM;SM.main()")
                #command="exec(open(r'E:/CGTools/for_Maya/tools_ani/SpringMagic/springMagic.py', 'r').read())")
    pm.menuItem(label="Studio Library", image="{}/tools_ani/StudioLibrary/icon/logo.png".format(scriptsPath),
                command="import tools_ani.StudioLibrary.studiolibrary.main as SL;SL.main()")
    pm.menuItem(label="IK/FK Switcher", image="{}/tools_ani/IKFKSwitch/icon/ikfk.png".format(scriptsPath),
                command="import tools_ani.IKFKSwitch.IKFKSwitch as IKFK;IKFK.ikFkSwitch().createUi()")
    pm.menuItem(label="BroDynamics",
                command="import tools_ani.BroTools as BroTools;BroTools.BroDynamics.BroDynamicsUI.initUI()")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # ==================================================sim============================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True, label=":::::  sim")
    pm.menuItem(label="解算助手", command="exec(open(r'{0}\\tools_sim\simTool.py').read())".format(scriptsPath))
    pm.menuItem(label="DynJointTools", command="import tools_sim.DynJointTools.DynJointTool as DJ ;DJ.main()")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # ================================================render===========================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True, label=":::::  render")
    pm.menuItem(label="LGTSetTool", image="{}/icons/light.png".format(scriptsPathOut),
                command="import tools_render.LGTSet_Maya.LGTSetTool as LS;LS.LGTSetToolsUI()")
    pm.menuItem(label="Submit Job To Deadline", image="{}/icons/Submit.png".format(scriptsPathOut),
                command="mel.eval('SubmitJobToDeadline')")
    pm.setParent(CG, menu=True)
    pm.menuItem(divider=True)
    # ===============================================gen================================================================
    pm.menuItem(parent="CG", subMenu=True, tearOff=True, label="xxx")
    # pm.menuItem(label="A v2.0", command="import AssetsManagerUI;AssetsManagerUI.showWindow();")
    # pm.menuItem(divider=True)
    # pm.menuItem("ac_pyblish",label="Pyblish", tearOff=True, subMenu=True)
    # pm.menuItem(divider=True)
    pm.menuItem(label="Publish",
                command="import gen.publish.main.maya_load_win as maya_load_win;ui=maya_load_win.MayaLoadWindow();ui.show();")
    pm.menuItem(divider=True)
    # pm.setParent("..", menu=True)
    pm.menuItem(label="Basic Operation", tearOff=True, subMenu=True)
    pm.menuItem(label="Select Joints",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('joint');")
    pm.menuItem(label="Select NurbsCurves",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('nurbsCurve');")
    pm.menuItem(label="Select NurbsSurface",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('nurbsSurface');")
    pm.menuItem(label="Select ParentConstraint",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('parentConstraint');")
    pm.menuItem(label="Select PointConstraint",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('pointConstraint');")
    pm.menuItem(label="Select OrientConstraint",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('orientConstraint');")
    pm.menuItem(label="Select ScaleConstraint",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('scaleConstraint');")
    pm.menuItem(label="Select Animation NurbsCurves",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_ani_curve();")
    pm.menuItem(label="Select Mesh", command="import gen.generation as gen;g=gen.JT_genaral();g.select_objs('mesh');")
    pm.menuItem(label="Select Reference Objs",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_reference_objs();")
    pm.menuItem(label="Select Influence Objs",
                command="import gen.generation as gen;g=gen.JT_genaral();g.select_inluence();")
    pm.menuItem(divider=True)
    pm.menuItem(label="Add Loc", command="import gen.generation as gen;g=gen.JT_genaral();g.add_loc();")
    pm.menuItem(label="Add Grp", command="import gen.generation as gen;g=gen.JT_genaral();g.add_grp();")
    pm.menuItem(label="Insert Grp", command="import gen.generation as gen;g=gen.JT_genaral();g.insert_grp();")
    pm.menuItem(divider=True)
    pm.menuItem(label="Mirror Pos",
                command="import gen.generation as gen;g=gen.JT_genaral();g.mirror_transform();")
    pm.menuItem(label="Move Pos", command="import gen.generation as gen;g=gen.JT_genaral();g.move_pos();")
    pm.menuItem(label="Constraint Child",
                command="import gen.generation as gen;g=gen.JT_genaral();g.constraint_child();")
    pm.menuItem(label="Joint On Point",
                command="import gen.generation as gen;g=gen.JT_genaral();g.joint_on_point(True);",
                postMenuCommand="import gen.generation as gen;g=gen.JT_genaral();g.joint_on_point(Fasle);")
    pm.menuItem(optionBox=1)
    pm.menuItem(label="Set Zero", command="import gen.generation as gen;g=gen.JT_genaral();g.set_select_zero();")
    pm.setParent("..", menu=True)
    pm.menuItem(label="Jump to current working path",
                command="import gen.Jump_to_current_working_path as jtcwp;")
    # ====================================================help=========================================================
    pm.menuItem(parent="CG", subMenu=False, label="About", image="{}/icons/menu_help.png".format(scriptsPathOut),
                command="import tools_about.info as info;info.showWindow()")
    # command="import webbrowser;webbrowser.open_new_tab('https://space.bilibili.com/475139733')")
    return True


def readLoginSetting():
    """ """
    if os.path.isfile(SM_SETTING_JSON):
        f = open(SM_SETTING_JSON, 'rb')
        setting_data = json.loads(f.read())
        f.close()
    else:
        setting_data = {}
    return setting_data


def spring_magic():
    with open(r'/for_Maya/tools_ani/SpringMagic/springMagic.py', 'r') as f:
        code = f.read()
        exec(code)


def shelf_setup():
    """
    安装工具架
    :return:True
    """
    import shutil
    print("shelf install begun ...")
    # mel.eval('addNewShelfTab "CGTools";shelfTabChange;')
    org_shelf_path = "{}/shelves/shelf_CGTools.mel".format(scriptsPath)
    for i in os.environ['MAYA_SCRIPT_PATH'].split(';'):
        if i.endswith("/prefs/shelves"):
            maya_shelves_path = i
    with open(org_shelf_path) as (f):
        stra = f.read()
        strb = stra.replace('scriptsPath', scriptsPath)
    new_shelf_path = "{}/shelf_CGTools.mel".format(maya_shelves_path)
    if os.path.exists(new_shelf_path):
        try:
            shutil.rmtree(new_shelf_path)
            print("shelf已存在，成功删除")
        except:
            print("shelf已存在，尝试删除失败")
    with open("{}/shelf_CGTools.mel".format(maya_shelves_path), 'w+') as (ff):
        ff.seek(0, 0)
        ff.write(strb)
        ff.truncate()
    melmel = 'loadNewShelf "{0}/shelf_CGTools";shelfTabChange;'.format(maya_shelves_path)
    mel.eval(melmel)
    print("shelf install end ...")
    return True


def execute():
    menu_setup()
    shelf_setup()
