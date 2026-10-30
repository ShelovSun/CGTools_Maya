#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""用 mayapy 验证当前场景查杀；测试脚本只有注释，不包含可执行的病毒代码。"""

import ast
import importlib.util
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

os.environ['MAYA_SKIP_USERSETUP_PY'] = '1'
os.environ['MAYA_SKIP_USERSETUP_MEL'] = '1'
os.environ['MAYA_NO_PLUGIN_AUTOLOAD'] = '1'
os.environ['MAYA_DISABLE_CIP'] = '1'
os.environ['MAYA_DISABLE_CER'] = '1'
sys.dont_write_bytecode = True
TOOL_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOL_ROOT))
for path in (
    TOOL_ROOT.parent,
    TOOL_ROOT.parent / 'tools_ani' / 'StudioLibrary',
    TOOL_ROOT.parent / 'Python' / 'Python37' / 'Lib' / 'site-packages',
):
    sys.path.append(str(path))

import maya.standalone
maya.standalone.initialize(name='python')

import maya.cmds as cmds
from utils import publish


def publish_implementations():
    """独立加载每个旧版 utils，模拟不同 sys.path 顺序实际选中的实现。"""
    yield publish
    folders = (
        'ShotsManagerForMaya', 'tools_publish/PublishTools', 'tools_model/Mod_Publish_Tool',
        'tools_rig/Rig_Publish_Tool', 'tools_ani/Ani_Publish_Tool',
        'tools_scene/Scene_Publish_Tool',
    )
    for index, folder in enumerate(folders):
        path = TOOL_ROOT.parent / folder / 'utils' / 'publish.py'
        spec = importlib.util.spec_from_file_location('test_legacy_publish_%s' % index, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module


def load_method(path, name, namespace):
    """单独加载 UI 方法，避免旧版 ShotsManager 导入时连接 CGTeamWork 或弹窗。"""
    tree = ast.parse(path.read_text(encoding='utf-8'))
    method = next(
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == name
    )
    method.decorator_list = []
    module = ast.parse('')
    module.body = [method]
    exec(compile(module, str(path), 'exec'), namespace)
    return namespace[name]


class VirusCheckSceneTests(unittest.TestCase):
    def setUp(self):
        cmds.file(new=True, force=True)
        cmds.undoInfo(state=True)
        self.temp = tempfile.TemporaryDirectory(prefix='cgtools_virus_check_')

    def tearDown(self):
        cmds.file(new=True, force=True)
        self.temp.cleanup()

    @staticmethod
    def script(name, before='', after=''):
        node = cmds.createNode('script', name=name)
        cmds.setAttr(node + '.scriptType', 0)
        cmds.setAttr(node + '.before', before, type='string')
        cmds.setAttr(node + '.after', after, type='string')
        return node

    def test_empty_scene(self):
        self.assertEqual(publish.Publish.virusCheck(), [])

    def test_all_known_names_and_duplicate_number(self):
        names = [
            'maya_secure_system_scriptNode', 'fuckVirus_gene', 'breed_gene', 'vaccine_gene',
            'sysytenasdasdfsadfsdaf_dsfsdfaasd', 'PuTianTongQing', 'daxunhuan',
            'vaccine_gene12', 'custom_uifiguration_node', 'VACCINE_GENE',
        ]
        nodes = [self.script(name) for name in names]
        self.assertEqual(set(publish.Publish().virusCheck()), set(nodes))
        self.assertFalse(any(cmds.objExists(node) for node in nodes))
        self.assertEqual(publish.Publish.virusCheck(), [])

    def test_content_rules_in_before_and_after(self):
        markers = [
            'maya_secure_system', 'MayaSecureSystem', 'fuckVirus', 'vaccine.phage',
            'leukocyte.antivirus', 'codeExtractor', 'codeChunk', 'quit -f',
            'fuck_All_U', 'uifiguration', 'petri_dish_path', 'aW1wb3J0IGJpbm',
        ]
        for attr in ('before', 'after'):
            for index, marker in enumerate(markers):
                with self.subTest(attr=attr, marker=marker):
                    node = self.script('renamed_%s_%s' % (attr, index), **{attr: '// ' + marker})
                    self.assertEqual(publish.Publish.virusCheck(), [node])
                    self.assertFalse(cmds.objExists(node))

    def test_normal_scripts_ui_configuration_and_other_node_types_survive(self):
        normal = [
            self.script('MayaMelUIConfigurationFile', '// normal Maya UI configuration'),
            self.script('normal_gene', '// normal studio script'),
            self.script('breed_gene_helper', '// normal helper'),
            self.script('vaccine_gene_notes', '// normal notes'),
        ]
        transform = cmds.createNode('transform', name='vaccine_gene')
        self.assertEqual(publish.Publish.virusCheck(), [])
        self.assertTrue(all(cmds.objExists(node) for node in normal + [transform]))

    def test_ui_configuration_with_bad_content_is_removed(self):
        node = self.script('MayaMelUIConfigurationFile', after='// fuck_All_U')
        self.assertEqual(publish.Publish.virusCheck(), [node])

    def test_namespaces_and_locked_nodes(self):
        cmds.namespace(add='character')
        node = self.script('character:breed_gene2')
        cmds.lockNode(node, lock=True)
        self.assertEqual(publish.Publish.virusCheck(), [node])
        self.assertFalse(cmds.objExists(node))

    def test_cleanup_can_be_undone_as_one_operation(self):
        nodes = [self.script('vaccine_gene'), self.script('breed_gene')]
        publish.Publish.virusCheck()
        cmds.undo()
        self.assertTrue(all(cmds.objExists(node) for node in nodes))

    def test_open_binary_scene_is_cleaned_without_conversion(self):
        self.script('renamed_payload', after='// vaccine.phage')
        path = str(Path(self.temp.name) / 'input.mb')
        cmds.file(rename=path)
        cmds.file(save=True, type='mayaBinary', force=True)
        cmds.file(new=True, force=True)
        cmds.file(path, open=True, force=True, executeScriptNodes=False)
        self.assertEqual(publish.Publish.virusCheck(), ['renamed_payload'])
        self.assertEqual(cmds.file(query=True, sceneName=True), path.replace('\\', '/'))

    def test_infected_reference_reports_source_and_preserves_scene(self):
        self.script('vaccine_gene')
        path = str(Path(self.temp.name) / 'reference.ma')
        cmds.file(rename=path)
        cmds.file(save=True, type='mayaAscii', force=True)
        cmds.file(new=True, force=True)
        cmds.file(path, reference=True, namespace='asset', executeScriptNodes=False)
        local = self.script('breed_gene')
        with self.assertRaises(RuntimeError) as caught:
            publish.Publish.virusCheck()
        self.assertIn('asset:vaccine_gene', str(caught.exception))
        self.assertIn('reference.ma', str(caught.exception))
        self.assertTrue(cmds.objExists('asset:vaccine_gene'))
        self.assertTrue(cmds.objExists(local))

    def test_unreadable_script_blocks_check(self):
        self.script('normal_script')
        with mock.patch.object(publish.cmds, 'getAttr', side_effect=RuntimeError('cannot read')):
            with self.assertRaises(RuntimeError) as caught:
                publish.Publish.virusCheck()
        self.assertIn('normal_script', str(caught.exception))
        self.assertIn('cannot read', str(caught.exception))

    def test_delete_failure_is_reported_and_undo_chunk_is_closed(self):
        node = self.script('vaccine_gene')
        with mock.patch.object(publish.cmds, 'delete', side_effect=RuntimeError('cannot delete')), \
                mock.patch.object(publish.cmds, 'undoInfo', wraps=cmds.undoInfo) as undo:
            with self.assertRaises(RuntimeError) as caught:
                publish.Publish.virusCheck()
            undo.assert_called_with(closeChunk=True)
        self.assertIn('cannot delete', str(caught.exception))
        self.assertTrue(cmds.objExists(node))

    def test_reinfection_after_delete_blocks_check(self):
        node = self.script('vaccine_gene')
        delete = cmds.delete

        def reappear(name):
            delete(name)
            self.script(name)

        with mock.patch.object(publish.cmds, 'delete', side_effect=reappear):
            with self.assertRaises(RuntimeError) as caught:
                publish.Publish.virusCheck()
        self.assertIn(node, str(caught.exception))
        self.assertTrue(cmds.objExists(node))

    def test_all_seven_publish_implementations_use_the_same_rules(self):
        for module in publish_implementations():
            with self.subTest(module=module.__file__):
                self.assertIs(module.virus_check, publish.virus_check)
                node = self.script('renamed_payload', after='// vaccine.phage')
                self.assertEqual(module.Publish().virusCheck(), [node])
                self.assertFalse(cmds.objExists(node))

    def test_save_to_server_writes_a_clean_maya_file(self):
        self.script('renamed_payload', after='// vaccine.phage')
        self.script('normal_script', before='// normal studio script')
        path = publish.Publish().saveToServer(self.temp.name, 'Mod', 'Asset', 'mod')
        cmds.file(new=True, force=True)
        cmds.file(path, open=True, force=True, executeScriptNodes=False)
        self.assertFalse(cmds.objExists('renamed_payload'))
        self.assertTrue(cmds.objExists('normal_script'))


class VirusCheckPublishEntryTests(unittest.TestCase):
    def test_all_save_helpers_stop_before_archiving_or_writing_on_infection(self):
        for module in publish_implementations():
            for method_name in ('saveToServer', 'saveXGenFile'):
                with self.subTest(module=module.__file__, method=method_name):
                    publisher = module.Publish()
                    publisher.virusCheck = mock.Mock(side_effect=RuntimeError('infected reference'))
                    publisher.createHistory = mock.Mock()
                    publisher.makePath = mock.Mock()
                    args = ('unused', 'Rig', 'Asset', 'all_rig', 'mayaAscii')
                    if method_name == 'saveXGenFile':
                        args = ('Asset', 'Project', 'unused', 'XGen', 'xgen', 'ma')
                    with mock.patch.object(module.cmds, 'file') as scene_file:
                        with self.assertRaises(RuntimeError):
                            getattr(publisher, method_name)(*args)
                        scene_file.assert_not_called()
                    publisher.createHistory.assert_not_called()
                    publisher.makePath.assert_not_called()

    def test_direct_publish_and_export_methods_cannot_bypass_check(self):
        main_methods = {
            '_modPublish': (), '_rigPublish': (), '_scenePublish': (),
            '_scenePublish_Map': ('Map',), '_scenePublish_GRP': (['Asset'],),
            '_scenePublish_Single': ('Asset',), '_actionsPublish': (),
            '_publishOneAction': ({},), '_actionPublish': (),
            'export_port_Ai': ('Group', 'Asset'), 'export_port_Rs': ('Group', 'Asset'),
            'export_mod': ('Group', 'Asset'), 'export_AD': ('Group', 'Asset'),
        }
        legacy_scene_methods = {
            name: args for name, args in main_methods.items()
            if name in ('_scenePublish', '_scenePublish_Map', '_scenePublish_GRP')
            or name.startswith('export_')
        }
        legacy_scene_methods['_scenePublish'] = ('Asset',)
        cases = {
            'tools_publish/PublishTools/PublishTool.py': main_methods,
            'tools_model/Mod_Publish_Tool/modPublishTool.py': {'_modPublish': ()},
            'tools_rig/Rig_Publish_Tool/rigPublishTool.py': {'_rigPublish': ()},
            'tools_ani/Ani_Publish_Tool/rigPublishTool.py': {'_rigPublish': ()},
            'tools_scene/Scene_Publish_Tool/scenePublishTool.py': legacy_scene_methods,
            'AssetsManagerForMaya/sources/rigTools.py': {'_rigPublish': ()},
            'AssetsManagerForMaya/sources/ShotsManager_Maya.py': {'saveMaya': ('unused.ma',)},
            'ShotsManagerForMaya/ShotsManager_Maya.py': {'saveMaya': ('unused.ma',)},
            'AssetsManagerForMaya/utils/animation.py': {'save': ('unused',)},
            'ShotsManagerForMaya/utils/animation.py': {'save': ('unused',)},
        }
        for rel, methods in cases.items():
            for name, args in methods.items():
                with self.subTest(path=rel, method=name):
                    scene_cmds = mock.Mock()
                    ctrl = mock.Mock()
                    ctrl.Pub = publish.Publish()
                    method = load_method(
                        TOOL_ROOT.parent / rel, name,
                        {'publish': publish, 'cmds': scene_cmds, 'QtWidgets': mock.Mock()},
                    )
                    with mock.patch.object(
                        publish.Publish, 'virusCheck', side_effect=RuntimeError('infected reference')
                    ):
                        with self.assertRaises(RuntimeError):
                            method(ctrl, *args)
                    self.assertEqual(scene_cmds.mock_calls, [])
                    self.assertEqual(ctrl.mock_calls, [])

    def test_all_four_publish_pages_check_before_dispatch_and_stop_on_failure(self):
        publisher = mock.Mock()
        qt = mock.Mock()
        method = load_method(
            TOOL_ROOT.parent / 'tools_publish' / 'PublishTools' / 'PublishTool.py',
            'yes_bttn_clicked',
            {'publish': SimpleNamespace(Publish=lambda: publisher), 'QtWidgets': qt},
        )
        routes = ('_modPublish', '_rigPublish', '_scenePublish', '_actionsPublish')
        for index, route in enumerate(routes):
            with self.subTest(route=route):
                ctrl = mock.Mock()
                ctrl.ui.Pub_Tab.currentIndex.return_value = index
                publisher.virusCheck.side_effect = RuntimeError('infected reference')
                method(ctrl)
                for name in routes:
                    getattr(ctrl, name).assert_not_called()
                qt.QMessageBox.warning.assert_called_with(
                    ctrl, '发布已中止', 'infected reference'
                )
                publisher.virusCheck.side_effect = None
                method(ctrl)
                getattr(ctrl, route).assert_called_once_with()

    def test_both_shots_publish_checks_stop_on_infection(self):
        paths = [
            TOOL_ROOT / 'sources' / 'ShotsManager_Maya.py',
            TOOL_ROOT.parent / 'ShotsManagerForMaya' / 'ShotsManager_Maya.py',
        ]
        for path in paths:
            with self.subTest(path=str(path)):
                publisher = mock.Mock()
                qt = mock.Mock()
                method = load_method(path, 'check_before_publish', {'QtWidgets': qt})
                ctrl = SimpleNamespace(Pub=publisher)
                publisher.virusCheck.side_effect = RuntimeError('infected reference')
                self.assertIs(method(ctrl), False)
                publisher.pluginInfo.assert_not_called()
                publisher.removeUnknownNodes.assert_not_called()
                qt.QMessageBox.warning.assert_called_once()
                publisher.virusCheck.side_effect = None
                self.assertIs(method(ctrl), True)


if __name__ == '__main__':
    try:
        unittest.main(verbosity=2)
    finally:
        maya.standalone.uninitialize()
