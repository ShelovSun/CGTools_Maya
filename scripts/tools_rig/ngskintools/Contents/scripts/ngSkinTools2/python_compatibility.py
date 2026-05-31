import sys

PY2 = sys.version_info[0] == 2


def is_string(obj):
    if PY2:
        # noinspection PyUnresolvedReferences
        return isinstance(obj, basestring)

    return isinstance(obj, str)


# need to use a new-style class in case of python2, or "normal" class otherwise
if PY2:

    class Object(object):
        pass

else:

    class Object:
        pass


# different ways to import urlopen
if PY2:
    # noinspection PyUnresolvedReferences
    from urllib2 import HTTPError, Request, urlopen
else:
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen

_ = urlopen
_ = Request
_ = HTTPError
