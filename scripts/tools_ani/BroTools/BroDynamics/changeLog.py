"""
BroDynamics Changelog and version data file
"""
import base64
import zlib
import urllib2
import os
import log

realPath = os.path.dirname(os.path.realpath(__file__))
offlineFile = os.path.join(realPath, 'info.txt')

currentVersion = '1.6.0'
latestVersion = 'Unknown'

changes = ''
ctag = "===CHANGELOG==="

welcome = ''
wtag = "===WELCOME==="

lic = ''
ltag = "===LICENSE==="

about = ''

def updateAboutText():
    global about
    about = '''<h3>BroDynamics v {0}</h3>
        Latest version: {2}
        <color=#faa300>Michael</color> Davydov <br>http://www.nixes.ru

        <b>CHANGE LOG</b>
        {1}'''.format(currentVersion, changes, latestVersion)

# Try to download actual information from dropbox.
def getInfoFromFile():
    log.log('', "Getting info from file")
    '''
    Get information from file
    '''
    with open(offlineFile, 'r') as file:
        data = file.read()

    parseText(data)
    updateAboutText()
    return data

def getVersion():
    global latestVersion
    try:
        text = ''
        data = urllib2.urlopen("https://dl.dropboxusercontent.com/s/31qqntc0cs15hhj/latestVersion.txt").read(5)  #

    except Exception as e:
        log.log("X", "Unable to connect to get latest version.\n", e, '\n')
        data = "Could not check latest version"

    latestVersion = data
    return data

def downloadInfo():
    '''
    Download information and write it to local file.
    '''
    log.log('', "Downloading information...")
    try:
        compressedData = urllib2.urlopen("https://dl.dropboxusercontent.com/s/vaotysxm90nxdbi/info.txt").read()
        data = zlib.decompress(base64.b64decode(compressedData))

        with open (offlineFile, 'w') as file:
            file.write(data)
        log.log('', "Download successful.")

    except Exception as e:
        log.inViewLog("#FF0000", "BroDynamics: Could not download up-to-date information. License and Changelog and Welcome text may be outdated.")
        log.log("", "BroDynamics: Could not download up-to-date information. License and Changelog and Welcome text may be outdated.", e)
        data = getInfoFromFile()

    getVersion()
    return data

def parseText(text):
    global changes
    global welcome
    global lic
    global about
    text = text.splitlines(True)
    mode = None
    changes = ""
    welcome = ""
    lic = ""
    for line in text:
        if ctag in line or wtag in line or ltag in line:
            if ctag in line:
                mode = ctag
            elif wtag in line:
                mode = wtag
            elif ltag in line:
                mode = ltag
        else:
            if mode == ctag:
                changes += line
            elif mode == wtag:
                welcome += line
            elif mode == ltag:
                lic += line

    updateAboutText()

def updateInfo():
    '''
    Download and update infromation here.
    '''

    parseText(downloadInfo())
    return True

getInfoFromFile()



