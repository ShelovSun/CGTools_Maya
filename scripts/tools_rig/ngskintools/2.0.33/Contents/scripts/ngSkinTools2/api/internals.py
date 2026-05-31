def make_editable_property(propertyName):
    return property(lambda self: self.__query__(**{propertyName: True}), lambda self, val: self.__edit__(**{propertyName: val}))


def influencesMapToList(influencesMapping):
    return ','.join(str(k) + "," + str(v) for (k, v) in list(influencesMapping.items()))


def floatListAsString(floatList):
    """
    returns empty string for None and []
    otherwise, returns a list of floats, comma delimited
    """
    if not floatList:
        return ""

    return ",".join([str(i) for i in floatList])
