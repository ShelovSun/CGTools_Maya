#!/usr/bin/env python


"""
BroDynamics\settings.py - Settings module. Contains colors and error texts and side arrays.

This module is the same for all major folders but still has to be copied to separately-released tools like BroDynamics.
"""

__author__ = "Mikhail Davydov"
__copyright__ = "Copyright 2016"
__version__ = "1.0.0"
__email__ = "nixesvfx@gmail.com"

colorsRGB = {"_Orange": [0.92, 0.73, 0], "_Cyan": [0.0, 0.76, 0.92], "_Green": [1.0, 1.0, 0.2],
             "_Grey": [0.3, 0.3, 0.3], "_Red": [0.9, 0.1, 0.1]}
sidesLeft = ['L', 'l', 'left', 'Left', 'LEFT']
sidesRight = ['r', 'R', 'right', 'Right', 'RIGHT']
sidesCenter = ['c', 'C', 'center', 'Center', 'CENTER']

doneText1 = \
    ' _____   ____  _   _ ______ _ _ _ \n' \
    '|  __ \ / __ \| \ | |  ____| | | | \n' \
    '| |  | | |  | |  \| | |__  | | | | \n' \
    '| |  | | |  | | . ` |  __| | | | | \n' \
    '| |__| | |__| | |\  | |____|_|_|_| \n' \
    '|_____/ \____/|_| \_|______(_|_|_) \n'

errorText = "\n=========== What's wrong, Bro? ============"

maClrIDs = {'grey': 0, 'black': 1, 'darkGrey': 2, 'lightGrey': 3, 'cherry': 4, 'darkBlue': 5, 'blue': 6, 'darkGreen': 7,
            'violet': 8, 'pink': 9, 'brown': 10,
            'darkBrown': 11, 'brick': 12, 'red': 13, 'green': 14, 'blueish': 15, 'white': 16, 'yellow': 17,
            'orange': 18, 'cyan': 19, 'lightPink': 20, 'skin': 21, 'lightYellow': 22,
            'lightGreen': 23, 'lightBrown': 24, 'lightSnort': 25, 'greenSnort': 26, 'cuamSnort': 27, '1': 28, '2': 29,
            '3': 30}


def errorText1(action='doing something'):
    return "\n=========== What's wrong, Bro? ============\nERROR while {}:\n".format(action)
