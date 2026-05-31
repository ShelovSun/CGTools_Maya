import os
import ast
import re
import base64
import json
import platform

import time
from threading import Thread

from maya import cmds, utils as mu
from ngSkinTools2 import cleanup, options, signal
from ngSkinTools2.api import plugin
from ngSkinTools2.log import getLogger
from ngSkinTools2.python_compatibility import Object
from ngSkinTools2.ui.parallel import ParallelTask

log = getLogger("license client")

try:
    from urllib2 import urlopen, Request, HTTPError
except:
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError


# noinspection PyClassHasNoInit
class Status:
    ok = 0
    unknown = 1
    communicationError = 2
    invalidSignature = 100
    invalidHostId = 101

    @classmethod
    def asStr(cls, status):
        return {
            Status.ok: "",
            Status.unknown: "unknown error",
            Status.communicationError: "communication error",
            Status.invalidSignature: "invalid signature",
            Status.invalidHostId: "license is bound to another workstation",
        }[status]


# noinspection PyAttributeOutsideInit
class LicenseServerClient(Object):
    """
    this client helps c++ plugin communicate with the license server.
    this only takes care of transport layer, to keep options a bit more open for future like TLS communication,
    without having to embed a proper HTTP client into plugin
    """

    def __init__(self, timeout=30):
        self.serverUrl = "http://127.0.0.1:9050"
        self.sleepPeriod = 60 * 2  # amount of seconds
        self.timeout = timeout
        # indirectly referencing a function to call main thread to be able to have different behavior in tests
        self.mainThreadFunc = mu.executeInMainThreadWithResult
        self.lastError = None
        self.is_running = False

        self.debug_num_thread_restarts = 0

    def refresh_reservation(self):
        """
        Called periodically to synchronize with license server
        :return:
        """

        req = Request(self.serverUrl + "/seat-reservations")

        def checkout_request():
            return plugin.ngst2License(serverRequest=True, hostName=platform.node())

        def checkin_response(resp):
            return plugin.ngst2License(serverResponse=resp)

        reqContents = self.mainThreadFunc(checkout_request)

        req.data = reqContents.encode()
        req.add_header("content-type", "application/json")

        try:
            resp = urlopen(req, timeout=self.timeout).read()
            self.lastError = None
            self.mainThreadFunc(checkin_response, resp)
        except IOError as err:
            raise Exception("ngSkinTools: error communicating with license server ({0}): {1}".format(self.serverUrl, err))

    def stop(self):
        self.lastError = None
        self.should_stop = True

    def run_license_reservation_thread(self):
        self.should_stop = False

        # only start new thread if previous one finished running, otherwise we just need to tell the currently running one there's no need to stop
        if self.is_running:
            return

        self.is_running = True

        def thread_func():
            log.info("license thread started")
            while not self.should_stop:
                log.info("refreshing reservation...")
                try:
                    self.refresh_reservation()
                    log.info("reservation refreshed")
                except Exception as err:
                    log.error(err)
                    self.lastError = str(err)

                time.sleep(self.sleepPeriod)
            log.info("license thread stopped")
            self.is_running = False

        self.debug_num_thread_restarts += 1
        self.current_thread = Thread(target=thread_func)
        self.current_thread.start()

        cleanup.registerCleanupHandler(self.stop)

    def apply_configuration(self, conf):
        """
        :type conf: Configuration
        """
        if conf.license_server_url:
            server_address = conf.license_server_url.strip()
            if not server_address.lower().startswith('http://') and not server_address.lower().startswith('https://'):
                server_address = 'http://' + server_address

            self.serverUrl = server_address
            self.refresh_reservation()
            self.run_license_reservation_thread()


def parse_license_contents(contents):
    """

    Example valid contents:

    LICENSE ngstkey ngskintools 1 standalone hostid=123-123
        sig=363c8f7f19679efc324b5ec713ffcf8968b3f4741b3b0d64f62436f8de799ec5

    For historical reasons, this is not a JSON.

    :param str contents:
    """

    values = contents.split()
    if len(values) < 6:
        return None

    result = {}
    for index, v in enumerate(['stamp', 'file-type', 'product', 'product-version', 'license-type']):
        result[v] = values[index]

    # check what we have here
    if result['stamp'] != 'LICENSE':
        return None

    # check if license type is ngstkey
    if result['file-type'] != 'ngstkey':
        return None

    if result['product'] != 'ngskintools2':
        return None

    for value in values[5:]:
        k, v = value.split("=", 2)
        result[k] = v

    # signature is required
    if result.get('sig', None) is None:
        return None

    if result.get('hostid', None) is None:
        return None

    return result


class LicenseFileHandler:
    def __init__(self):
        self.licenseServer = 'https://licensing.ngskintools.com/api/projects/ngskintools2/licenses/'

    def get_host_id(self):
        result = plugin.ngst2License(q=True, hostid=True)
        return result

    def __configuration_for_license_file(self, license_file):
        parsed_license_contents = parse_license_contents(license_file)
        if parsed_license_contents is None:
            raise Exception

        conf = Configuration()
        conf.license_files = [parsed_license_contents]
        return conf

    def apply_configuration(self, conf):
        """
        :type conf: Configuration
        """
        if conf.license_files:
            for c in conf.license_files:
                result = plugin.ngst2License(validateLicense=True, hostid=c['hostid'], licenseKey=c['licensekey'], signature=c['sig'])
                if result == 0:
                    conf.active_license_file = c
                    break

    def download_license_file(self, license_key, host_id):
        """
        exchanges licenseKey+hostId for a license file online.
        :type license_key: basestring
        :type host_id: basestring

        """

        host_id = host_id.strip()
        if host_id == "":
            raise Exception("Cannot download license when host ID is empty")

        import json

        try:
            req = Request(
                self.licenseServer + license_key,
                headers={
                    'Accept': 'application/vnd.releasedb.v1.1+json',
                },
            )
            resp = urlopen(req, json.dumps({"hostId": host_id, "licenseFileType": 'ngstKey'}).encode())
            result = json.load(resp)
            return result['licenseFile']
        except HTTPError as err:
            code = err.getcode()

            message = str(err)
            try:
                message = json.load(err)['message']
            except:
                pass

            log.info("received error: %r", message)

            # for client-side errors, just convey the error from the server
            if code == 400:
                raise Exception(message)

            if code == 404:
                raise Exception("invalid license key")

            raise Exception("Failed downloading license information ({0}): {1}".format(err.getcode(), message))
        except Exception as err:
            raise Exception("Failed downloading license information: unknown error ({0})".format(str(err)))

    def create_online_key_download_task(self, license_key):
        """
        :param basestring license_key:
        """
        host_id = self.get_host_id()

        def run(context):
            context.error = ""
            context.license_file = None

            try:
                context.license_file = self.download_license_file(license_key, host_id)
            except Exception as err:
                context.error = err.message

        def done(context):
            context.conf = None
            if context.license_file is not None:
                context.conf = self.__configuration_for_license_file(context.license_file)

        task = ParallelTask()
        task.add_run_handler(run)
        task.add_done_handler(done)

        return task

    def __is_license_key_valid(self, license_key):
        # UUID format:  8-4-4-4-12 hexadecimal strings
        # e.g. 12345678-abcd-ef09-1234-56789abcdef0
        format = '[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        return re.match(format, license_key)

    def generate_activation_code_link(self, license_key):
        # sample key
        if not self.__is_license_key_valid(license_key):
            raise Exception("Invalid license key format")

        return (
            "https://licensing.ngskintools.com/#/self-service/"
            + base64.b64encode(
                json.dumps({'type': 'activationCode', 'product': 'ngskintools2', 'licenseKey': license_key, 'hostId': self.get_host_id()}).encode()
            ).decode()
        )

    def configuration_for_activation_code(self, activation_code):
        try:
            contents = json.loads(base64.b64decode(activation_code))
        except:
            raise Exception("Invalid activation code: could not parse contents")

        return self.__configuration_for_license_file(contents['licenseFile'])


class Configuration:
    CONFIGURATION_VAR = options.VAR_OPTION_PREFIX + 'licenseConfig'
    CONFIGURATION_ENV_VAR = 'NGSKINTOOLS2_LICENSE_CONFIG'
    CONFIGURATION_PATH_ENV_VAR = 'NGSKINTOOLS2_LICENSE_PATH'

    type_host_id = "host-id"

    json_mapping = {
        'license_files': 'license-files',
        'license_server_url': 'license-server-url',
    }

    def __init__(self):
        self.license_files = []
        self.license_server_url = ""
        self.active_license_file = None

        self.is_editable = True

    def __discover_license_files__(self, path):
        """
        given a dir or file path, discover ngstkey license files. only files that look like license files are parsed,
        and only those that match ngstkey file format are used.
        """

        if path is None:
            return []

        if os.path.isfile(path):
            with open(path) as f:
                contents = f.read(7)
                if contents != 'LICENSE':
                    return []
                contents += f.read()

            parsed_contents = parse_license_contents(contents)
            if parsed_contents is None:
                return []

            parsed_contents['source_file'] = path
            return [parsed_contents]

        if os.path.isdir(path):
            result = []
            for i in os.listdir(path):
                file_name = os.path.join(path, i)
                if os.path.isfile(file_name):
                    result.extend(self.__discover_license_files__(file_name))

            return result

        return []

    def load(self):
        config_contents = os.getenv(self.CONFIGURATION_ENV_VAR, None)
        if config_contents:
            self.is_editable = False  # can't edit if configuration comes from environment variable
            self.load_from_string(config_contents)
            return

        # discover valid ngskintools2 licenses
        self.license_files = self.__discover_license_files__(cmds.internalVar(userAppDir=True))
        path = os.getenv(self.CONFIGURATION_PATH_ENV_VAR, None)
        if path:
            self.license_files.extend(self.__discover_license_files__(path))
        if self.license_files:
            self.is_editable = False  # can't edit if configuration comes from license files
            return

        self.load_from_string(options.loadOption(self.CONFIGURATION_VAR, ""))

    def load_from_string(self, s):
        """
        :param basestring s: either a python dictionary literal or a json containing key:value configuration of this object
        """
        s = s.strip()
        if not s:
            return

        log.info("loading config from: '%s'", s)

        if s.startswith("{"):
            try:
                # try loading as json first
                val = json.loads(s)
            except:
                # revert to ast eval (allows single-quotes)
                val = ast.literal_eval(s)
        else:
            # simple key-value, split with spaces
            items = [i.split("=", maxsplit=1) for i in s.split(" ")]
            val = {i[0]: i[1] for i in items if len(i) == 2}

        for k, v in self.json_mapping.items():
            if v in val:
                setattr(self, k, val[v])

        literal_license_file = {k: val[k] for k in ['hostid', 'licensekey', 'sig'] if k in val}
        if literal_license_file:
            self.license_files.append(literal_license_file)

    def save_to_string(self):
        """
        :return: json serialization of this object, suitable for load_from_string later
        """
        import json

        return json.dumps({v: getattr(self, k) for k, v in self.json_mapping.items()})

    def save(self):
        if self.is_editable:
            options.saveOption(self.CONFIGURATION_VAR, self.save_to_string())


class LicenseData:
    def __init__(self):
        self.active = False
        self.status_description = ""
        self.licensed_to = ''


class LicenseClient:
    def __init__(self):
        self.serverClient = LicenseServerClient()
        self.licenseFileHandler = LicenseFileHandler()
        self.statusChanged = signal.Signal("license status changed")
        self.conf = Configuration()
        self.errors = []

    def load(self):
        cfg = Configuration()
        cfg.load()
        self.__apply_configuration(cfg)

    def load_deferred(self):
        mu.executeDeferred(self.load)

    def __apply_configuration(self, conf):
        """
        :param Configuration conf:
        """
        self.__reset_errors()

        log.info("applying configuration: %s", json.dumps(conf.__dict__, indent=4))
        self.conf = conf
        try:
            self.licenseFileHandler.apply_configuration(conf)
            self.serverClient.apply_configuration(conf)
        except Exception as err:
            self.errors.append(str(err))
        self.statusChanged.emit()

    def __apply_and_save_configuration(self, conf):
        self.__apply_configuration(conf)
        log.info("saving configuration")
        conf.save()

    def __reset_errors(self):
        self.errors = []

    def current_status(self):
        data = LicenseData()
        status_code = plugin.ngst2License(q=True, licenseStatus=True)
        data.active = status_code == 0
        data.licensed_to = plugin.ngst2License(q=True, licensedTo=True)

        errors = self.errors[:]
        if self.serverClient.lastError is not None:
            errors.append(self.serverClient.lastError)
        data.status_description = None if not errors else "\n".join(errors)
        return data

    def current_configuration(self):
        return self.conf

    def activate_with_license_key(self, license_key):
        task = self.licenseFileHandler.create_online_key_download_task(license_key=license_key)
        self.__reset_errors()

        def done(context):

            if context.error:
                self.errors.append(context.error)
            if context.conf is not None:
                self.__apply_and_save_configuration(context.conf)
            self.statusChanged.emit()

        task.add_done_handler(done)
        return task

    def clear_configuration(self):
        plugin.ngst2License(reset=True)
        self.__apply_and_save_configuration(Configuration())

    def generate_acivation_code_link(self, license_key):
        return self.licenseFileHandler.generate_activation_code_link(license_key)

    def accept_activation_code(self, activation_code):
        self.__apply_and_save_configuration(self.licenseFileHandler.configuration_for_activation_code(activation_code))

    def accept_license_server_url(self, server_address):
        """
        :type server_address: basestring
        """
        conf = Configuration()
        conf.license_server_url = server_address

        self.__apply_and_save_configuration(conf)
