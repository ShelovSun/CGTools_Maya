import json
import threading

import maya.utils

defer_func = maya.utils.executeDeferred

try:
    from urllib import urlencode
    from urllib2 import urlopen, Request
except:
    from urllib.request import urlopen, Request
    from urllib.parse import urlencode


def encode_url(base_url, args):
    return base_url + "?" + urlencode(args)


def get_async(url, success_callback, failure_callback):
    def runnerFunc():
        try:
            result = urlopen(url).read()
            defer_func(success_callback, json.loads(result))
        except Exception as err:
            defer_func(failure_callback, str(err))

    t = threading.Thread(target=runnerFunc)
    t.start()
    return t
