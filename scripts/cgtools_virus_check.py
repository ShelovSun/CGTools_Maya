# -*- coding: utf-8 -*-
"""各版 Publish.virusCheck 共用的 MayaVirusCleaner v41 场景规则。"""

import re


def virus_check(cmds):
    """清理当前场景的病毒脚本节点；检查或清理失败时抛出 RuntimeError。

    由 Publish.virusCheck 传入 maya.cmds，兼容启动路径中不同版本的 utils。
    只检查当前场景，不执行脚本内容，也不扫描磁盘或修改个人启动脚本。
    """
    bad_names = re.compile(
        r'^(?:maya_secure_system_scriptNode|fuckVirus_gene|breed_gene|vaccine_gene|'
        r'sysytenasdasdfsadfsdaf_dsfsdfaasd|PuTianTongQing|daxunhuan)\d*$',
        re.IGNORECASE,
    )
    bad_content = re.compile(
        r'maya_secure_system|MayaSecureSystem|fuckVirus|vaccine\.phage|'
        r'leukocyte\.antivirus|codeExtractor|codeChunk|quit\s+-f|fuck_All_U|'
        r'uifiguration|petri_dish_path|aW1wb3J0IGJpbm',
        re.IGNORECASE,
    )

    def infected_nodes():
        infected = []
        for node in cmds.ls(type='script', long=True) or []:
            short_name = node.rsplit('|', 1)[-1].rsplit(':', 1)[-1]
            if bad_names.match(short_name) or 'uifiguration' in short_name.lower():
                infected.append(node)
                continue
            try:
                content = '\n'.join(
                    cmds.getAttr(node + '.' + attr) or '' for attr in ('before', 'after')
                )
            except Exception as error:
                raise RuntimeError(u'病毒检查未完成，无法读取脚本节点 %s：\n%s' % (node, error))
            # MayaMelUIConfigurationFile 本身是合法节点名，必须命中脚本内容才删除。
            if bad_content.search(content):
                infected.append(node)
        return infected

    infected = infected_nodes()
    if not infected:
        return []

    referenced = []
    for node in infected:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            source = cmds.referenceQuery(node, filename=True, withoutCopyNumber=True)
            referenced.append(u'%s\n  %s' % (node, source))
    if referenced:
        raise RuntimeError(
            u'发布已中止，引用文件含有病毒脚本节点，请先清理源文件并重新加载引用：\n'
            + '\n'.join(referenced)
        )

    removed = []
    failures = []
    cmds.undoInfo(openChunk=True, chunkName='CGToolsVirusCheck')
    try:
        for node in infected:
            try:
                cmds.lockNode(node, lock=False)
                cmds.delete(node)
                if cmds.objExists(node):
                    raise RuntimeError(u'节点删除后仍然存在')
                removed.append(node)
                print(u'[virusCheck] 已清除病毒脚本节点：%s' % node)
            except Exception as error:
                failures.append(u'%s：%s' % (node, error))
    finally:
        cmds.undoInfo(closeChunk=True)

    remaining = infected_nodes()
    if failures or remaining:
        details = failures + [u'清理后仍检测到：%s' % node for node in remaining]
        raise RuntimeError(u'发布已中止，病毒脚本节点未清理完成：\n' + '\n'.join(details))
    return removed
