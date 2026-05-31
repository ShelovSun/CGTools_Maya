import ConfigParser
import json
import os

import log
import utils


@utils.try_except
def readJSON(fileName):
    log.log("<", "Reading JSON:", fileName)
    file = open(fileName, 'r')
    data = json.load(file)
    return data


@utils.try_except
def writeJSON(fileName, data):
    log.log("<", "Writing JSON:", fileName)
    file = open(fileName, 'w')
    json.dump(data, file, indent=True)


@utils.try_except
def readConfig(fileName, silent=False):
    """
    reads config file. Use this to access data:
    import ConfigParser
    config = BroTools.common.dataio.readConfig(r'E:\PersonalWork\RiggingTools\BroTools\common\test.cfg')
    print config.get ('section', 'var')
    Args:
        fileName:

    Returns: Config object

    """
    fullFilePath = os.path.abspath(fileName)
    if os.path.exists(fullFilePath):
        if not silent:
            log.log("<", "Reading config file:", fullFilePath)
        config = ConfigParser.RawConfigParser()
        config.optionxform = str
        config.read(fullFilePath)
        return config

    else:
        log.log("!", "Tried Reading config file:", fullFilePath, "but there is no such file.")
        return "No file found"



@utils.try_except
def newConfig():
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    return config


def writeConfig(fileName, config):
    config.write()


@utils.try_except
def writeConfig():
    pass
