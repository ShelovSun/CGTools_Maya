#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('utils', '')

from .cmds import *
from .decorators import *
from .matchnames import matchNames, groupObjects

from .node import Node
from .attribute import Attribute

from .pose import Pose, savePose, loadPose
from .transferobject import TransferObject
from .animation import Animation, PasteOption, saveAnim, loadAnims

