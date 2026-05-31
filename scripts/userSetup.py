# # -*- coding: utf-8 -*-
import os,sys
import maya.cmds as cmds


def __register_CGTools_startup():
    from textwrap import dedent
    cmds.evalDeferred(dedent(
        """
        import menu.startup as s

        s.execute()
        """
    ))


if __name__ == '__main__':

    try:
        print("CGTools startup script has begun")
        __register_CGTools_startup()
        print("CGTools startup script has finished")

    except Exception as e:
        print("CGTools startup script has ended with error")
        # avoidng the "call userSetup.py chain" accidentally stop,
        # all exception must be collapsed
        import traceback
        traceback.print_exc()
