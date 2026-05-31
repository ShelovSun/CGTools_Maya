import json

from maya import cmds
from . import signal
from .log import getLogger
from .observableValue import ObservableValue
from .python_compatibility import Object
from .python_compatibility import is_string

log = getLogger("plugin")


class Value(Object):
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def getInt(self):
        try:
            return int(self.get())
        except:
            return 0


class PersistentValue(Value):
    """
    persistent value can store itself into Maya's "option vars" array
    """

    def __init__(self, name, defaultValue=None):
        Value.__init__(self)
        self.name = name
        self.defaultValue = defaultValue
        self.value = loadOption(self.name, self.defaultValue)

    def set(self, value):
        Value.set(self, value)
        saveOption(self.name, self.value)


def loadOption(varName, defaultValue):
    """
    loads value from optionVar
    """

    if cmds.optionVar(exists=varName):
        return cmds.optionVar(q=varName)

    return defaultValue


def saveOption(varName, value):
    """
    saves option via optionVar
    """

    # variable does not exist, attempt to save it
    key = None
    if isinstance(value, float):
        key = 'fv'
    elif isinstance(value, int):
        key = 'iv'
    elif is_string(value):
        key = 'sv'
    else:
        raise ValueError("could not save option %s: invalid value %r" % (varName, value))

    kvargs = {key: (varName, value)}
    log.info("saving optionvar: %r", kvargs)
    cmds.optionVar(**kvargs)


VAR_OPTION_PREFIX = 'ngSkinTools2_'


def deleteCustomOptions():
    for varName in cmds.optionVar(list=True):
        if varName.startswith(VAR_OPTION_PREFIX):
            cmds.optionVar(remove=varName)

    cmds.windowPref('MirrorWeightsWindow', ra=True)


def build_config_property(name, default_value, doc=''):
    return property(lambda self: self.__get_value__(name, default_value), lambda self, val: self.__set_value__(name, val), doc=doc)


class Config(Object):
    """
    Maya-wide settings for ngSkinTools2
    """

    checkForUpdatesAtStartup = build_config_property('checkForUpdatesAtStartup', True)  # type: bool
    mirrorInfluencesDefaults = build_config_property('mirrorInfluencesDefaults', "{}")  # type: string

    def __init__(self):
        self.__storage__ = PersistentValue(VAR_OPTION_PREFIX + "config", "{}")
        self.__state__ = self.load()

    def __get_value__(self, name, default_value):
        result = self.__state__.get(name, default_value)
        log.info("config: return %s=%r", name, result)
        return result

    def __set_value__(self, name, value):
        log.info("config: save %s=%r", name, value)
        self.__state__[name] = value
        self.save()

    def build_observable_value(self, name, default_value):
        """
        builds ObservableValue that is loaded and persisted into config when changed
        :type name: str
        :rtype: ngSkinTools2.observableValue.ObservableValue
        """
        result = ObservableValue(self.__get_value__(name=name, default_value=default_value))

        @signal.on(result.changed)
        def save():
            self.__set_value__(name, result())

        return result

    def load(self):
        # noinspection PyBroadException
        try:
            return json.loads(self.__storage__.get())
        except:
            return {}

    def save(self):
        self.__storage__.set(json.dumps(self.__state__))


config = Config()
