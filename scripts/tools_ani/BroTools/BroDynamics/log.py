__author__ = 'Michael'

import datetime

import maya.cmds as cmds
import zlib
import base64

debugEnabled = True

def log(type='', *args):
    if debugEnabled and type != 'error' and type != '!':
        time = str(datetime.datetime.now())
        prefix = type * 3
        text = ''
        for item in args:
            text += ' '
            text += str(item)

        if type == 'warning':
            output = 'WARNING: '+time+": "+text
            cmds.warning (output)
        elif type == 'error':
            output = 'ERROR: '+time+": "+text
            cmds.error(output)
        else:
            output = prefix+' '+time+": "+text
            print output


def log2(type='', *args):
    time = str(datetime.datetime.now())
    prefix = type
    text = ''
    for item in args:
        text += ' '
        text += str(item)
    print prefix, time + ":", text

def zp(data):
    try:
        r = base64.b64encode(zlib.compress(data))
        return r
    except:
        return "Err"


def inViewLog(color='', *args):
    text = ''
    for item in args:
        text += ' '
        text += str(item)

    log('', text)
    if color != '':
        text = "<span style=\"color:{0};\">{1}</span>".format(color, text)

    cmds.inViewMessage(amg=text, pos='topCenter', fade=True, fst=1000, dk=True)
