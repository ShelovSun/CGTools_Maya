# uncompyle6 version 3.7.4
# Python bytecode 2.7 (62211)
# Decompiled from: Python 3.8.6 (tags/v3.8.6:db45529, Sep 23 2020, 15:37:30) [MSC v.1927 32 bit (Intel)]
# Embedded file name: C:/Users/marce/Documents/maya/plug-ins/MaxToMaya_Files\m2m.py
# Compiled at: 2021-05-23 18:25:41
import os, sys, maya.cmds as cmds
from sys import path as sysPath
import maya.mel as mel
from pymel import versions
from uuid import getnode as get_mac
from threading import Timer

try:
    from importlib import reload
except:
    print 'importlib skip'

lastRender = 'Vray222'
tempPath = 'C:\\TEMP3D\\'
m2mSerialWindowName = 'maxtomayaSerial'
m2mMainWindowName = 'maxtomayaWindow'
m2mConfigWindowName = 'maxtomayaConfig'
m2mWaitWindowName = 'maxtomayaWait'
scriptPath = os.path.expanduser('~/maya/plug-ins/MaxToMaya_Files')
m2mlogo = scriptPath + '/' + 'MaxToMaya.jpg'
m2mImageHelp = scriptPath + '/' + 'iconhelpSm.png'
m2mSettingsFile = scriptPath + '/' + 'settings.cfg'
m2mSerialFile = scriptPath + '/' + 'serial.cfg'
m2mSerialConfigFile = scriptPath + '/' + 'maxtomaya_51x56.config'
m2mNoPreview = scriptPath + '/' + 'nopreview.jpg'
m2mDefaultPath = 'C:\\TEMP3D\\'
m2mXMLfile = 'C:\\TEMP3D\\3dm2m.xml'
m2mFbxFile = 'C:\\TEMP3D\\3dm2m.fbx'
m2mThumbFileX = 'C:\\TEMP3D\\3dm2m.jpg'
txtEnterSerial = ''

def getOrSetPath():
    global m2mFbxFile
    global m2mThumbFileX
    global m2mXMLfile
    filesPath = None
    try:
        filesPath = m2mLoadSettings('TempPath').rstrip('\n')
        m2mFbxFile = os.path.join(filesPath, '3dm2m.fbx')
        m2mXMLfile = os.path.join(filesPath, '3dm2m.xml')
        m2mThumbFileX = os.path.join(filesPath, '3dm2m.jpg')
    except:
        pass

    if filesPath == None:
        filesPath = m2mDefaultPath
        m2mFbxFile = os.path.join(filesPath, '3dm2m.fbx')
        m2mXMLfile = os.path.join(filesPath, '3dm2m.xml')
        m2mThumbFileX = os.path.join(filesPath, '3dm2m.jpg')
    return filesPath


def m2mLoadSettings(setting='', settingsFile='settings'):
    fileName = ''
    if settingsFile == 'settings':
        fileName = m2mSettingsFile
    if settingsFile == 'ser':
        fileName = m2mSerialFile
    try:
        with open(fileName, 'r') as (f):
            data = f.readlines()
            for line in data:
                if setting in line:
                    words = line.split('=')
                    return words[1].rstrip('\n')

    except:
        print 'error loading settings'


def m2mSaveSettings(m2mTempPath='', lastRender=''):
    try:
        txtFilesPath = m2mLoadSettings('TempPath').rstrip('\n')
    except:
        pass

    try:
        txtLastPass = m2mLoadSettings('TempPath').rstrip('\n')
    except:
        pass

    try:
        with open(m2mSettingsFile, 'w') as (f):
            f.write('TempPath=' + txtFilesPath + '\n')
            f.write('LastRender=' + lastRender + '\n')
            print '- Settings Saved -'
    except:
        print '- Error: Settings Not Saved -'


def m2mCheckSettings():
    if os.path.isfile(m2mSettingsFile):
        m2mLoadSettings('TempPath')
    else:
        print ('ERROR: File path:\n{} does NOT exist. Exiting...').format(filename)
        m2mSaveSettings()


class myTimer:

    def __init__(self, t, hFunction):
        self.t = t
        self.hFunction = hFunction
        self.thread = Timer(self.t, self.handle_function)

    def handle_function(self):
        self.hFunction()
        self.thread = Timer(self.t, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()


def addToClipBoard(text):
    command = 'echo ' + text.strip(' \t\n\r') + '| clip'
    os.system(command)


def chkSrl(srl):
    mac = get_mac()
    mac1 = str(mac)[2:4]
    mac2 = str(mac)[6:8]
    mac3 = str(mac)[1:3]
    srl1 = srl[3:5]
    srl2 = srl[6:8]
    srl3 = srl[10:12]
    str1 = 'xxx'
    str2 = 'x'
    str3 = 'xx'
    validSrl = 'xxx' + mac3 + 'x' + mac1 + 'xx' + mac2
    if srl1 == mac3 and srl2 == mac1 and srl3 == mac2:
        return True
    else:
        return False


def findPlugin(stringToFind):
    plugList = cmds.pluginInfo(query=True, listPlugins=True)
    for p in plugList:
        if stringToFind in p:
            return True


def guiSerial():
    getOrSetPath()

    def codeGen():
        mac = get_mac()
        mac1 = str(mac)[2:4]
        mac2 = str(mac)[6:8]
        mac3 = str(mac)[1:3]
        str1 = 'M2M'
        str2 = 'kUY'
        str3 = '172'
        str4 = '09H'
        generatedCode = str1 + mac1 + str2 + mac2 + str3 + mac3
        return generatedCode

    def codeCopy():
        codeGenerated = cmds.textField('txtFieldCode', query=True, text=True)
        addToClipBoard(codeGenerated)

    def getSerial():
        cmds.launch(web='http://www.3dtoall.com/register')

    def activar():
        srl = cmds.textField(txtEnterSerial, q=True, tx=True)
        srl = srl.replace(' ', '')
        if chkSrl(srl) == True:
            with open(m2mSerialFile, 'w') as (f):
                f.write('Serial=' + srl + '\n')
            with open(m2mSerialConfigFile, 'w') as (f):
                f.write('Serial=' + srl + '\n')
            print '- MaxToMaya Activated -'
            try:
                cmds.deleteUI(m2mSerialWindowName)
            except:
                pass

            guiMain()
        else:
            cmds.confirmDialog(title='MaxToMaya', message='Activation Problem. Please try again or contact support.', button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')

    try:
        caca = cmds.window('maxtomayaSerial', query=True, title=True)
    except:
        pass

    try:
        cmds.deleteUI(mainWindowName)
    except Exception as e:
        pass

    try:
        cmds.deleteUI(m2mSerialWindowName)
    except Exception as e:
        pass

    windowSerial = cmds.window(m2mSerialWindowName, toolbox=True, maximizeButton=False, minimizeButton=False, sizeable=False, title='MaxToMaya', widthHeight=(343,
                                                                                                                                                              310))
    form = cmds.formLayout(numberOfDivisions=100)
    object = cmds.image(image=m2mlogo, backgroundColor=(0.392157, 0.862745, 1), w=343, h=88)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 0), (object, 'left', 0)])
    object = cmds.text(label='Your Code:', w=115, h=21)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 90), (object, 'left', 115)])
    name = cmds.textField('txtFieldCode', tx=codeGen(), font='boldLabelFont', editable=False, width=150)
    cmds.formLayout(form, edit=True, attachForm=[(name, 'top', 115), (name, 'left', 50)])
    btnCopyCode = cmds.button(label='Copy to Clipboard', width=120, c=lambda *args: codeCopy(), height=20)
    cmds.formLayout(form, edit=True, attachForm=[(btnCopyCode, 'top', 115), (btnCopyCode, 'left', 175)])
    btnRegister = cmds.button(label='Get Activation Serial', width=260, c=lambda *args: getSerial(), height=25)
    cmds.formLayout(form, edit=True, attachForm=[(btnRegister, 'top', 142), (btnRegister, 'left', 45)])
    object = cmds.separator(style='in', w=325, h=6)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 175), (object, 'left', 10)])
    labelEnterCode = cmds.text(label='Enter your MaxToMaya serial here:')
    cmds.formLayout(form, edit=True, attachForm=[(labelEnterCode, 'top', 188), (labelEnterCode, 'left', 85)])
    txtEnterSerial = cmds.textField('txtFieldSerialEnter', tx='', width=210)
    cmds.formLayout(form, edit=True, attachForm=[(txtEnterSerial, 'top', 206), (txtEnterSerial, 'left', 70)])
    btnActivate = cmds.button(label='ACTIVATE', command=lambda *args: activar(), height=40, width=210)
    cmds.formLayout(form, edit=True, attachForm=[(btnActivate, 'top', 232), (btnActivate, 'left', 70)])
    object = cmds.separator(style='in', w=325, h=6)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 280), (object, 'left', 10)])
    txtCopyright = cmds.text(label='(c) 2021 3DtoAll. All Rights Reserved.')
    cmds.formLayout(form, edit=True, attachForm=[(txtCopyright, 'top', 290), (txtCopyright, 'left', 85)])
    cmds.showWindow(windowSerial)
    cmds.window(windowSerial, e=True, width=335, height=312)


def guiConfig():
    filesPath = None
    try:
        filesPath = m2mLoadSettings('TempPath').rstrip('\n')
    except:
        pass

    if filesPath == None:
        filesPath = m2mDefaultPath[:-1]

    def pathRestoreDefault():
        cmds.textField(m2mTxtFieldPath, e=True, tx=m2mDefaultPath[:-1])

    def pathSelect():
        selectedPath = cmds.fileDialog2(dir='path/to/dir', dialogStyle=1, fileMode=3)
        if selectedPath != None:
            cmds.textField(m2mTxtFieldPath, e=True, tx=selectedPath[0])
        return

    def saveSettings():
        lastRender = ''
        try:
            lastRender = m2mLoadSettings('LastRender')
        except Exception as e:
            print e

        if lastRender == None:
            lastRender = 'Standard'
        with open(m2mSettingsFile, 'w') as (f):
            path = cmds.textField(m2mTxtFieldPath, q=True, tx=True)
            f.write('TempPath=' + path + '\n')
            f.write('LastRender=' + lastRender + '\n')
            print '- Settings Saved -'
        try:
            cmds.deleteUI(m2mConfigWindowName)
            cmds.deleteUI(m2mMainWindowName)
        except Exception as e:
            pass

        getOrSetPath()
        guiMain()
        return

    try:
        caca = cmds.window('maxtomayaConfig', query=True, title=True)
    except:
        pass

    try:
        cmds.deleteUI(m2mConfigWindowName)
    except Exception as e:
        pass

    windowSerial = cmds.window(m2mConfigWindowName, title='MaxToMaya', toolbox=True, maximizeButton=False, minimizeButton=False, sizeable=False, widthHeight=(343,
                                                                                                                                                              310))
    form = cmds.formLayout(numberOfDivisions=100)
    object = cmds.text(label='Auto-Import from this Path:', align='left', w=300, h=21)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 5), (object, 'left', 15)])
    m2mTxtFieldPath = cmds.textField('m2mTxtFieldPath', tx=filesPath, editable=False, height=25, width=300)
    cmds.formLayout(form, edit=True, attachForm=[(m2mTxtFieldPath, 'top', 25), (m2mTxtFieldPath, 'left', 10)])
    extra0 = 10
    btnCopyCode = cmds.button(label='Change Path...', width=300, c=lambda *args: pathSelect(), height=20)
    cmds.formLayout(form, edit=True, attachForm=[(btnCopyCode, 'top', 45 + extra0), (btnCopyCode, 'left', 10)])
    btnColor = [0.4, 0.4, 0.5]
    btnRestore = cmds.button(label='Restore Default Path', backgroundColor=btnColor, width=300, c=lambda *args: pathRestoreDefault(), height=25)
    cmds.formLayout(form, edit=True, attachForm=[(btnRestore, 'top', 70 + extra0), (btnRestore, 'left', 10)])
    object = cmds.separator(style='in', w=300, h=6)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 102 + extra0), (object, 'left', 10)])
    btnSettingsSave = cmds.button(label='Save', command=lambda *args: saveSettings(), height=30, width=147)
    cmds.formLayout(form, edit=True, attachForm=[(btnSettingsSave, 'top', 115 + extra0), (btnSettingsSave, 'left', 10)])
    btnCancel = cmds.button(label='Cancel', command=lambda *args: cmds.deleteUI(m2mConfigWindowName), height=30, width=144)
    cmds.formLayout(form, edit=True, attachForm=[(btnCancel, 'top', 115 + extra0), (btnCancel, 'left', 165)])
    cmds.showWindow(m2mConfigWindowName)
    cmds.window(m2mConfigWindowName, e=True, width=320, height=165)
    return


def guiWait():
    try:
        cmds.deleteUI(m2mWaitWindowName)
    except:
        pass

    windowWait = cmds.window(m2mWaitWindowName, toolbox=True, maximizeButton=False, minimizeButton=False, sizeable=False, title='MaxToMaya', widthHeight=(343,
                                                                                                                                                          55))
    cmds.columnLayout('columnName01', adjustableColumn=True)
    cmds.separator(height=20, style='in')
    cmds.text(label='Importing please wait...')
    cmds.separator(height=20, style='in')
    cmds.showWindow(windowWait)
    cmds.window(windowWait, e=True, width=320, height=55)


def guiMain():
    global m2mThumbFileX
    try:
        cmds.deleteUI(m2mMainWindowName)
    except Exception as e:
        pass

    windowMain = cmds.window(m2mMainWindowName, title='MaxToMaya v2.92', s=False, tlb=True)
    form = cmds.formLayout(numberOfDivisions=100)
    if os.path.isfile(m2mThumbFileX) == False:
        try:
            m2mThumbFileX = m2mNoPreview
        except:
            print 'Skip preview...'

    object = cmds.image(image=m2mlogo, backgroundColor=(0.392157, 0.862745, 1), w=343, h=88)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 0), (object, 'left', 0)])
    object = cmds.image(backgroundColor=(0.37, 0.37, 0.37), w=195, h=145)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 99), (object, 'left', 20)])
    guiImage = cmds.image(image=m2mThumbFileX, w=180, h=120)
    cmds.formLayout(form, edit=True, attachForm=[(guiImage, 'top', 106), (guiImage, 'left', 27)])
    extra = 45
    object = cmds.separator(style='in', w=325, h=6)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 250 + extra), (object, 'left', 10)])
    extra = 35
    object = cmds.text(label='Convert To:', w=115, h=21)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 94), (object, 'left', 165 + extra)])
    lbl1 = 'Standard'
    lbl2 = 'Vray'
    lbl3 = 'Arnold'
    lbl4 = 'Redshift'
    lbl5 = 'Mental Ray'
    topStart = 110
    space = 25
    group1 = cmds.radioButtonGrp(select=1, numberOfRadioButtons=1, label='', label1=lbl1, w=250, h=34)
    cmds.formLayout(form, edit=True, attachForm=[(group1, 'top', topStart), (group1, 'left', 50 + extra)])
    group2 = cmds.radioButtonGrp(numberOfRadioButtons=1, shareCollection=group1, label='', label1=lbl2, w=250, h=34)
    cmds.formLayout(form, edit=True, attachForm=[(group2, 'top', topStart + space * 1), (group2, 'left', 50 + extra)])
    group3 = cmds.radioButtonGrp(numberOfRadioButtons=1, shareCollection=group1, label='', label1=lbl3, w=250, h=34)
    cmds.formLayout(form, edit=True, attachForm=[(group3, 'top', topStart + space * 2), (group3, 'left', 50 + extra)])
    group4 = cmds.radioButtonGrp(numberOfRadioButtons=1, shareCollection=group1, label='', label1=lbl4, w=250, h=34)
    cmds.formLayout(form, edit=True, attachForm=[(group4, 'top', topStart + space * 3), (group4, 'left', 50 + extra)])
    group5 = cmds.radioButtonGrp(numberOfRadioButtons=1, shareCollection=group1, label='', label1=lbl5, w=250, h=34)
    cmds.formLayout(form, edit=True, attachForm=[(group5, 'top', topStart + space * 4), (group5, 'left', 50 + extra)])
    sysVer = sys.version_info
    if sysVer.major == 3:
        cmds.radioButtonGrp(group5, e=True, enable=False)
    btnRefreshPrev = cmds.button(label='Refresh Preview', w=180, h=20, c=lambda *args: refreshPrev(guiImage))
    cmds.formLayout(form, edit=True, attachForm=[(btnRefreshPrev, 'top', 188 + extra), (btnRefreshPrev, 'left', 27)])
    extra = 51
    btnAutoImport = cmds.button(label='Auto-Import', w=260, h=34, c=lambda *args: autoImport(group1, group2, group3, group4, group5))
    cmds.formLayout(form, edit=True, attachForm=[(btnAutoImport, 'top', 202 + extra), (btnAutoImport, 'left', 60)])
    object = cmds.button(label='. . .', w=34, h=34, c=lambda *args: guiConfig())
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 202 + extra), (object, 'left', 20)])
    extra = 45
    object = cmds.text(label='(c) 2021 3DtoAll. All rights reserved.', w=343, h=30)
    cmds.formLayout(form, edit=True, attachForm=[(object, 'top', 251 + extra), (object, 'left', 0)])
    lastrender = m2mLoadSettings('LastRender')
    if lastrender == 'Standard':
        cmds.radioButtonGrp(group1, e=True, select=True)
    if lastrender == 'Vray':
        cmds.radioButtonGrp(group2, e=True, select=True)
    if lastrender == 'Arnold':
        cmds.radioButtonGrp(group3, e=True, select=True)
    if lastrender == 'Redshift':
        cmds.radioButtonGrp(group4, e=True, select=True)
    if lastrender == 'MentalRay':
        cmds.radioButtonGrp(group5, e=True, select=True)
    cmds.showWindow(windowMain)
    cmds.window(windowMain, e=True, width=343, height=325)


def testXMLstuff():
    print 'test xml stuff!!'
    import m2mST
    m2mST.xmlToStandard().start(m2mXMLfile, m2mFbxFile, True)


def autoImport(group1, group2, group3, group4, group5):
    scaleMenuValue = 'cm'
    if os.path.exists(m2mXMLfile) == False or os.path.exists(m2mFbxFile) == False:
        cmds.confirmDialog(title='MaxToMaya: Files not found', message='Files not found.\nExport from 3ds Max first, using MaxToMaya.\nBe sure to set the same path in the settings.             ')
        return False
    else:
        mel.eval('FBXImportMode -v Add')
        if scaleMenuValue == 'cm':
            mel.eval('FBXImportConvertUnitString cm')
        if scaleMenuValue == 'mm':
            mel.eval('FBXImportConvertUnitString mm')
        if scaleMenuValue == 'dm':
            mel.eval('FBXImportConvertUnitString dm')
        if scaleMenuValue == 'm':
            mel.eval('FBXImportConvertUnitString m')
        renderStandard = cmds.radioButtonGrp(group1, query=True, select=True)
        renderVray = cmds.radioButtonGrp(group2, query=True, select=True)
        renderArnold = cmds.radioButtonGrp(group3, query=True, select=True)
        renderRedshift = cmds.radioButtonGrp(group4, query=True, select=True)
        renderMentalRay = cmds.radioButtonGrp(group5, query=True, select=True)
        if renderVray == 1 and findPlugin('vrayformaya') == None:
            cmds.confirmDialog(title='MaxToMaya', message='Error.\nVray not found. Check if Vray is loaded.', button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
            return
        if renderArnold == 1 and findPlugin('mtoa') == None:
            cmds.confirmDialog(title='MaxToMaya', message='Error.\nArnold not found. Check if Arnold is loaded.', button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
            return
        if renderRedshift == 1 and findPlugin('redshift') == None:
            cmds.confirmDialog(title='MaxToMaya', message='Error.\nRedshift not found. Check if Redshift is loaded.', button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
            return
        if renderMentalRay == 1 and findPlugin('Mayatomr') == None:
            cmds.confirmDialog(title='MaxToMaya', message='Error.\nMental Ray not found. Check if Mental Ray is loaded.', button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
            return
        result = mel.eval('saveChanges("file -f -new")')
        if result == 0:
            return
        cmds.NewScene()
        try:
            guiWait()
        except:
            pass

        print 'MaxToMaya: Importing...'
        cmds.refresh()
        sysPath.append(scriptPath)
        try:
            cmds.deleteUI(m2mMainWindowName)
        except Exception as e:
            pass

        if renderStandard == 1:
            import m2mST
            try:
                reload(m2mST)
            except:
                print 'importlib reload'

            m2mST.xmlToStandard().start(m2mXMLfile, m2mFbxFile)
            m2mSaveSettings('', 'Standard')
            print 'Standard'
        if renderVray == 1:
            import m2mVR
            try:
                reload(m2mVR)
            except:
                print 'importlib reload'

            m2mVR.xmlToVRay().start(m2mXMLfile, m2mFbxFile)
            m2mSaveSettings('', 'Vray')
            print 'Vray'
        if renderArnold == 1:
            import m2mArn
            try:
                reload(m2mArn)
            except:
                print 'importlib reload'

            m2mArn.xmlToArnold().start(m2mXMLfile, m2mFbxFile)
            m2mSaveSettings('', 'Arnold')
            print 'Arnold'
        if renderRedshift == 1:
            import m2mRS
            try:
                reload(m2mRS)
            except:
                print 'importlib reload'

            m2mRS.xmlToRedShift().start(m2mXMLfile, m2mFbxFile)
            m2mSaveSettings('', 'Redshift')
            print 'Redshift'
        if renderMentalRay == 1:
            import m2mMR
            try:
                reload(m2mMR)
            except:
                print 'importlib reload'

            m2mMR.xmlToMentalRay().start(m2mXMLfile, m2mFbxFile)
            m2mSaveSettings('', 'MentalRay')
            print 'MentalRay'
        try:
            cmds.deleteUI(m2mWaitWindowName)
        except:
            pass

        return


def refreshPrev(guiImage):
    cmds.image(guiImage, e=True, image=m2mThumbFileX, w=180, h=120)


srl = None
try:
    srl = m2mLoadSettings('Serial', 'ser').rstrip('\n')
except:
    srl = None
    print 'Serial Load Error'

def versionCheck():
    print 'Version check...'
    mayaversion = str(versions.current())
    print mayaversion
    suppVer = ['2014', '2015', '2016', '2017', '2018', '2019', '2020', '2022']
    for v in suppVer:
        if v in mayaversion:
            print 'MaxToMaya: Supported Version'
            return True

    dialogMsg = 'Maya Version not Supported. Please visit www.3DtoAll.com'
    cmds.confirmDialog(title='MaxToMaya', message=dialogMsg, button=['Ok'], defaultButton='Yes', cancelButton='No', dismissString='No')
    return False


def maxtomayaStartDialog():
    if os.path.exists(m2mSerialConfigFile) == True:
        guiMain()
    else:
        if srl != None and versionCheck() == True:
            if chkSrl(srl) == True:
                guiMain()
            else:
                guiSerial()
        if srl == None or chkSrl == False:
            guiSerial()
    return


# maxtomayaStartDialog()