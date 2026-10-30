#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mayapy 下验证发布文件备份和 Windows 文件占用；只操作临时目录。"""

import ctypes
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
sys.dont_write_bytecode = True
TOOL_ROOT = Path(__file__).resolve().parents[1]
for path in (
    TOOL_ROOT,
    TOOL_ROOT.parent,
    TOOL_ROOT.parent / 'tools_ani' / 'StudioLibrary',
    TOOL_ROOT.parent / 'Python' / 'Python37' / 'Lib' / 'site-packages',
):
    sys.path.append(str(path))

from utils import publish
from PySide2 import QtWidgets

APP = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
with mock.patch('maya.OpenMayaUI.MQtUtil.mainWindow', return_value=0):
    from tools_publish.PublishTools import PublishTool as publish_tool


class PublishFileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='cgtools_publish_test_')
        self.root = Path(self.temp.name)
        self.rig_dir = self.root / 'Rig'
        self.rig_dir.mkdir()
        self.target = self.rig_dir / 'Asset_all_rig.ma'
        self.original_scene = str(self.root / 'work.mb')
        self.current_scene = self.original_scene
        self.save_error = None
        self.handles = []
        self.publisher = publish.Publish()
        self.cmds_patch = mock.patch.object(publish, 'cmds')
        self.cmds = self.cmds_patch.start()
        self.cmds.file.side_effect = self.maya_file

    def tearDown(self):
        self.cmds_patch.stop()
        for handle in self.handles:
            self.close_handle(handle)
        self.temp.cleanup()

    def maya_file(self, **kwargs):
        if kwargs.get('query'):
            return self.current_scene
        if 'rename' in kwargs:
            self.current_scene = kwargs['rename']
        elif kwargs.get('save'):
            if self.save_error is not None:
                raise self.save_error
            Path(self.current_scene).write_bytes(b'new published scene')

    def save(self, **kwargs):
        return self.publisher.saveToServer(str(self.root), 'Rig', 'Asset', 'all_rig', **kwargs)

    def lock_read_only(self, path):
        """真实 Win32 句柄：允许其他进程读，拒绝写入/删除，模拟网络文件被占用。"""
        from ctypes import wintypes
        create_file = ctypes.windll.kernel32.CreateFileW
        create_file.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE,
        ]
        create_file.restype = wintypes.HANDLE
        handle = create_file(str(path), 0x80000000, 1, None, 3, 0x80, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError()
        self.handles.append(handle)
        return handle

    @staticmethod
    def close_handle(handle):
        if handle is not None:
            close = ctypes.windll.kernel32.CloseHandle
            close.argtypes = [ctypes.c_void_p]
            close.restype = ctypes.c_int
            close(handle)

    def test_backup_only_target_and_leave_original_until_save(self):
        self.target.write_bytes(b'old all rig')
        hi_rig = self.rig_dir / 'Asset_hi_rig.ma'
        hi_rig.write_bytes(b'old hi rig')
        work = self.rig_dir / 'Asset_hi_rig_new.mb'
        work.write_bytes(b'working scene')
        def save_with_check(**kwargs):
            if kwargs.get('save'):
                self.assertEqual(self.target.read_bytes(), b'old all rig')
            return self.maya_file(**kwargs)
        self.cmds.file.side_effect = save_with_check
        self.assertEqual(Path(self.save()), self.target)
        self.assertEqual(self.target.read_bytes(), b'new published scene')
        self.assertEqual(hi_rig.read_bytes(), b'old hi rig')
        self.assertEqual(work.read_bytes(), b'working scene')
        backups = list((self.rig_dir / 'history').rglob('*.*'))
        self.assertEqual([path.name for path in backups], ['Asset_all_rig.ma'])
        self.assertEqual(backups[0].read_bytes(), b'old all rig')

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_locked_unrelated_work_file_does_not_block_publish(self):
        work = self.rig_dir / 'Asset_hi_rig_new.mb'
        work.write_bytes(b'locked work file')
        self.lock_read_only(work)
        self.save()
        self.assertEqual(work.read_bytes(), b'locked work file')
        self.assertEqual(self.target.read_bytes(), b'new published scene')

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_locked_target_retries_and_preserves_files_and_scene_name(self):
        self.target.write_bytes(b'old official file')
        self.lock_read_only(self.target)
        with mock.patch.object(publish.time, 'sleep') as sleep:
            with self.assertRaises(publish.PublishFileInUseError) as caught:
                self.save()
        self.assertEqual(sleep.call_count, 3)
        self.assertEqual(Path(caught.exception.file_path), self.target)
        self.assertEqual(self.target.read_bytes(), b'old official file')
        self.assertFalse((self.rig_dir / 'history').exists())
        self.assertEqual(self.current_scene, self.original_scene)
        self.cmds.file.assert_not_called()

    @unittest.skipUnless(os.name == 'nt', 'Windows sharing semantics')
    def test_transient_lock_release_allows_retry_to_finish(self):
        self.target.write_bytes(b'old official file')
        handle = self.lock_read_only(self.target)
        def unlock(delay):
            self.close_handle(handle)
            self.handles.remove(handle)
        with mock.patch.object(publish.time, 'sleep', side_effect=unlock) as sleep:
            self.save()
        sleep.assert_called_once_with(0.5)
        self.assertEqual(self.target.read_bytes(), b'new published scene')
        backup = next((self.rig_dir / 'history').rglob('Asset_all_rig.ma'))
        self.assertEqual(backup.read_bytes(), b'old official file')

    def test_non_lock_errors_are_not_retried_or_hidden(self):
        error = PermissionError('access denied')
        error.winerror = 5
        operation = mock.Mock(side_effect=error)
        with mock.patch.object(publish.time, 'sleep') as sleep:
            with self.assertRaises(PermissionError):
                self.publisher._retry_file_operation(operation, str(self.target))
        operation.assert_called_once_with()
        sleep.assert_not_called()

    def test_failed_save_keeps_backup_and_restores_original_scene_name(self):
        self.target.write_bytes(b'old official file')
        self.save_error = RuntimeError('Maya save failed')
        with self.assertRaises(RuntimeError) as caught:
            self.save()
        self.assertIn('Maya save failed', str(caught.exception))
        self.assertIn('history', str(caught.exception))
        self.assertEqual(self.current_scene, self.original_scene)
        self.assertEqual(self.target.read_bytes(), b'old official file')
        backup = next((self.rig_dir / 'history').rglob('Asset_all_rig.ma'))
        self.assertEqual(backup.read_bytes(), b'old official file')

    def test_first_publish_and_binary_extension(self):
        result = Path(self.save(mayaformat='mayaBinary'))
        self.assertEqual(result.name, 'Asset_all_rig.mb')
        self.assertTrue(result.is_file())
        self.assertFalse((self.rig_dir / 'history').exists())
        self.assertEqual(Path(self.current_scene), result)
        self.assertEqual(self.cmds.file.call_args[1]['type'], 'mayaBinary')

    def test_hi_rig_has_own_backup_and_does_not_archive_all_rig(self):
        self.target.write_bytes(b'new all rig')
        hi_rig = self.rig_dir / 'Asset_hi_rig.ma'
        hi_rig.write_bytes(b'old hi rig')
        self.publisher.saveToServer(str(self.root), 'Rig', 'Asset', 'hi_rig')
        self.assertEqual(self.target.read_bytes(), b'new all rig')
        self.assertEqual(hi_rig.read_bytes(), b'new published scene')
        backups = list((self.rig_dir / 'history').rglob('*.*'))
        self.assertEqual([path.name for path in backups], ['Asset_hi_rig.ma'])
        self.assertEqual(backups[0].read_bytes(), b'old hi rig')

    def test_hi_rig_failure_stops_pipeline_and_reopens_full_rig(self):
        ui = mock.Mock()
        for name in ('approved_cBox_2', 'icon_cBox_rig', 'xgen_cBox_2', 'textures_cBox_2'):
            getattr(ui, name).isChecked.return_value = False
        ui.info_lineEdit.text.return_value = ''
        ctrl = SimpleNamespace(
            ui=ui, get_publishInfo_rig=lambda: ('S01', 'Asset', 'Asset', 'Props', str(self.root)),
            createRigAssetsForSQL=mock.Mock(return_value=True), logMsg=mock.Mock(),
            selected_surfaces=lambda: [], rigClean=mock.Mock(), rig_fbx_export=mock.Mock(),
            _notify_shotmanager=mock.Mock(),
            projectSetting=lambda: {
                'rigFolder': 'Rig', 'rigFileAll': 'all_rig', 'rigFileHi': 'hi_rig',
            },
        )
        pub = mock.Mock()
        pub.saveToServer.side_effect = [str(self.target), RuntimeError('Target locked')]
        with mock.patch.object(publish_tool.publish, 'Publish', return_value=pub), \
                mock.patch.object(publish_tool, 'cmds') as cmds, \
                mock.patch.object(publish_tool, 'mel'), \
                mock.patch.object(publish_tool, 'action_library_path', return_value='Action'), \
                mock.patch.object(publish_tool.QtWidgets.QMessageBox, 'warning') as warning:
            cmds.listRelatives.return_value = []
            cmds.objExists.return_value = False
            publish_tool.PubToolsUI._rigPublish(ctrl)
            self.assertEqual(pub.saveToServer.call_count, 2)
            self.assertNotIn('createHistory', pub.saveToServer.call_args[1])
            cmds.file.assert_called_once_with(
                str(self.target), open=True, type='mayaAscii', ignoreVersion=True,
                options='v=0', force=True,
            )
            cmds.waitCursor.assert_called_with(state=False)
            warning.assert_called_once()
        ui.log_progressBar.setVisible.assert_called_with(False)
        ctrl.rig_fbx_export.assert_not_called()
        ctrl._notify_shotmanager.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
