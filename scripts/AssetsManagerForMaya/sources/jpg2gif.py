#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ActionTools Created: 9/5/2021 by Sunxh<175702994@qq.com>
# log: 第一次编写

import sys,os
scriptsPath = os.path.split(os.path.realpath(__file__))[0].replace('\\', '/').replace('sources', '')
sys.path.append('%s/imageio'%scriptsPath.replace("AssetsManagerForMaya","lib"))
import imageio
MYPREFSDIR = os.environ.get('TEMP')

def aaaa():
    path = r'%s\AssetsManagerIconTemp\sequence' % MYPREFSDIR
    # print(path)
    image_list = [path + '\\' + img for img in os.listdir(path)]
    frames = []
    for image in image_list:
        # print(image)
        frames.append(imageio.imread(image))
    imageio.mimsave(r"%s\AssetsManagerIconTemp\thumbnail.gif" % MYPREFSDIR, frames, 'GIF', duration=0.033333333333333)
    # print(u"ActionGif.gif 已转换")

aaaa()