#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用 Maya 2022 mayapy 验证动作 FBX 的实际片段范围；只创建临时场景和文件。"""

import os
import shutil
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from types import MethodType, SimpleNamespace
from unittest import mock

sys.dont_write_bytecode = True
MAYA_PREFS = tempfile.mkdtemp(prefix='cgtools_fbx_range_prefs_')
os.environ['MAYA_APP_DIR'] = MAYA_PREFS
os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
TOOL_ROOT = Path(__file__).resolve().parents[1]
for path in (
    TOOL_ROOT,
    TOOL_ROOT.parent,
    TOOL_ROOT.parent / 'tools_ani' / 'StudioLibrary',
    TOOL_ROOT.parent / 'Python' / 'Python37' / 'Lib' / 'site-packages',
):
    sys.path.append(str(path))

import maya.standalone

maya.standalone.initialize(name='python')
import maya.cmds as cmds
import maya.mel as mel
from utils import fbxMesh, publish
from widgets.previewGLWidget import PreviewGLWidget

with mock.patch('maya.OpenMayaUI.MQtUtil.mainWindow', return_value=0):
    from tools_publish.PublishTools import PublishTool


class ActionFbxRangeTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.loadPlugin('fbxmaya', quiet=True)
        cmds.currentUnit(time='ntsc')
        cmds.namespace(add='RangeTest')
        self.group = cmds.group(empty=True, name='RangeTest:DeformationSystem')
        self.joint = cmds.joint(name='RangeTest:root')
        self.control = cmds.createNode('transform', name='RangeTest:control')
        self.temp = tempfile.TemporaryDirectory(prefix='cgtools_action_fbx_test_')
        self.publisher = SimpleNamespace(Pub=publish.Publish())

    def tearDown(self):
        cmds.file(new=True, force=True)
        self.temp.cleanup()

    def setup_animation(self, constrained=False, selected=True, modified=False):
        animated = self.control if constrained else self.joint
        for time, value in ((500, 0), (520, 20), (748, 100)):
            cmds.setKeyframe(animated, attribute='rotateY', time=time, value=value)
        if constrained:
            cmds.parentConstraint(self.control, self.joint, maintainOffset=False)
        cmds.playbackOptions(
            minTime=500, maxTime=748, animationStartTime=450, animationEndTime=800
        )
        cmds.currentTime(710)
        cmds.select(self.control) if selected else cmds.select(clear=True)
        mel.eval(
            'FBXResetExport; '
            'FBXExportSplitAnimationIntoTakes -clear; '
            'FBXExportSplitAnimationIntoTakes -v "Existing Clip" 10 20; '
            'FBXExportSplitAnimationIntoTakes -v "Other Clip" 30 40; '
            'FBXExportDeleteOriginalTakeOnSplitAnimation -v false;'
        )
        cmds.file(modified=modified)
        self.animated = animated
        self.original = self.scene_state()

    def scene_state(self):
        return {
            'range': [cmds.playbackOptions(query=True, **{flag: True}) for flag in (
                'minTime', 'maxTime', 'animationStartTime', 'animationEndTime')],
            'time': cmds.currentTime(query=True),
            'selection': cmds.ls(selection=True, long=True) or [],
            'modified': cmds.file(query=True, modified=True),
            'takes': mel.eval('FBXExportSplitAnimationIntoTakes -q;'),
            'delete_original': mel.eval('FBXExportDeleteOriginalTakeOnSplitAnimation -q;'),
            'key_times': cmds.keyframe(self.animated, query=True, timeChange=True),
            'key_values': cmds.keyframe(self.animated, query=True, valueChange=True),
        }

    def export(self, start, end):
        path = Path(self.temp.name) / ('action_%s_%s.fbx' % (start, end))
        PublishTool.PubToolsUI.ani_fbx_export(
            self.publisher, path.as_posix(), start, end, namespace='RangeTest'
        )
        self.assertEqual(self.scene_state(), self.original)
        return path

    def assert_fbx_range(self, path, start, end):
        root, objects = fbxMesh._load_tree(str(path))
        action = fbxMesh.build_action(root, objects)
        self.assertIsNotNone(action)
        to_frame = lambda ticks: ticks / float(fbxMesh._FBX_TIME_UNIT) * action.fps
        self.assertAlmostEqual(to_frame(action.t0), start)
        self.assertAlmostEqual(to_frame(action.t1), end)
        self.assertEqual(sum(node.name == 'AnimationStack' for node in objects.children), 1)
        settings = root.first('GlobalSettings')
        self.assertAlmostEqual(to_frame(fbxMesh._p70(settings, 'TimeSpanStart')[0]), start)
        self.assertAlmostEqual(to_frame(fbxMesh._p70(settings, 'TimeSpanStop')[0]), end)
        curves = fbxMesh._parse_anim_curves(objects)
        times = [time for key_times, _values in curves.values() for time in key_times]
        self.assertTrue(times)
        self.assertAlmostEqual(to_frame(min(times)), start)
        self.assertAlmostEqual(to_frame(max(times)), end)

    def test_custom_range_crops_direct_keys_and_restores_scene(self):
        self.setup_animation()
        self.assert_fbx_range(self.export(500, 520), 500, 520)

    def test_custom_range_bakes_constrained_joints(self):
        self.setup_animation(constrained=True, selected=False, modified=True)
        self.assert_fbx_range(self.export(500, 520), 500, 520)

    def test_consecutive_ranges_do_not_reuse_previous_take(self):
        self.setup_animation()
        for start, end in ((500, 520), (600, 620), (500, 748)):
            self.assert_fbx_range(self.export(start, end), start, end)

    def test_failed_export_restores_range_selection_and_take_settings(self):
        self.setup_animation()
        with mock.patch.object(
            self.publisher.Pub, 'exportFBX', side_effect=RuntimeError('export failed')
        ):
            with self.assertRaisesRegex(RuntimeError, 'export failed'):
                self.export(500, 520)
        self.assertEqual(self.scene_state(), self.original)


class ActionPreviewCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cgtools_action_cache_test_')
        self.rig = Path(self.temp.name) / 'rig.fbx'
        self.action = Path(self.temp.name) / 'action.fbx'
        self.rig.touch()
        self.action.touch()
        self.rig_path, self.action_path = self.rig.as_posix(), self.action.as_posix()
        # standalone 没有 OpenGL 窗口，只调用真实的缓存/播放调度方法。
        self.preview = SimpleNamespace(
            _CACHE_CAP=8, _PAGE_GL=1, _PAGE_LOADING=2,
            _current_fbx=self.rig_path, _current_action=None, _current_action_stamp=None,
            _anim_cache={}, _anim_order=[], _skin_cache={}, _skin_lock=threading.Lock(),
            _gl_view=mock.Mock(), _gl_failed=False, _pool=mock.Mock(), _csignals=mock.Mock(),
            _load_timer=mock.Mock(), _showPageForCurrentMode=mock.Mock(),
            _rigStaticMd=mock.Mock(return_value=None), _showRigStatic=mock.Mock(),
            _animFileStamp=PreviewGLWidget._animFileStamp,
        )
        self.preview._load_timer.isActive.return_value = False
        for name in ('playAction', '_animCacheGet', '_animCachePut'):
            setattr(self.preview, name, MethodType(getattr(PreviewGLWidget, name), self.preview))
        self.anim, self.images = object(), {}

    def tearDown(self):
        self.temp.cleanup()

    def cache_animation(self):
        self.preview._animCachePut(self.rig_path, self.action_path, self.anim, self.images)
        self.preview.playAction(self.action_path)

    def test_unchanged_animation_reuses_cache(self):
        self.cache_animation()
        self.preview.playAction(self.action_path)
        self.preview._pool.start.assert_not_called()
        self.preview._gl_view.showResult.assert_called_once_with(None, self.anim, self.images)

    def test_republished_action_or_rig_reloads_current_animation(self):
        for path in (self.action, self.rig):
            with self.subTest(updated=path.name):
                self.cache_animation()
                stamp = path.stat()
                os.utime(str(path), ns=(stamp.st_atime_ns, stamp.st_mtime_ns + 2000000000))
                self.assertIsNone(self.preview._animCacheGet(self.rig_path, self.action_path))
                self.preview._pool.start.reset_mock()
                self.preview.playAction(self.action_path)
                self.preview._pool.start.assert_called_once()
                task = self.preview._pool.start.call_args[0][0]
                self.assertEqual((task._rig, task._action), (self.rig_path, self.action_path))

    def test_deleted_action_cannot_reuse_cache(self):
        self.cache_animation()
        self.action.unlink()
        self.assertIsNone(self.preview._animCacheGet(self.rig_path, self.action_path))


if __name__ == '__main__':
    try:
        unittest.main()
    finally:
        maya.standalone.uninitialize()
        # mayaLog 在 Windows 中会保持占用到进程退出，允许留下该临时日志。
        shutil.rmtree(MAYA_PREFS, ignore_errors=True)
