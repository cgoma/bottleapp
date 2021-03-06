#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This module creates API for getting reported property from
azure device twin
"""

import json
import threading
import bottle
import time
import sys
import iothub_service_client
import json
from iothub_service_client import IoTHubDeviceTwin, IoTHubError
#from iothub_service_client_args import get_iothub_opt_with_module, OptionError
from bottle import run, route, get, post, request, template, response, \
Bottle,HTTPResponse
app = Bottle(__name__)

CONNECTION_STRING = "HostName=WRDM2-IOTHUB-CHETAB.azure-devices.net;SharedAccessKeyName=iothubowner;SharedAccessKey=G/pvf/JC8KdbN/eN4gtt273CJCl+VuulFS0onzA8RA0="

DEVICE_ID = "WRDM2_IOTDEVICE_CHETAN_2"
MODULE_ID = None

def get_iothub_device_twin(methodname):

    try:
        retVal = 0
        iothub_twin_method = IoTHubDeviceTwin(CONNECTION_STRING)
        # Query for device twin
        twin_info = iothub_twin_method.get_twin(DEVICE_ID)
        payload = json.loads(twin_info)
        if methodname == 'ota':
            retVal = payload["properties"]["reported"]["softwareUpdate"]
        if methodname == 'reboot':
            retVal = payload["properties"]["reported"]["rebootStatus"]
        return retVal

    except IoTHubError as iothub_error:
        print ( "" )
        print ( "Unexpected error {0}" % iothub_error )
        return "error"
    except KeyboardInterrupt:
        print ( "" )
        print ( "IoTHubModuleTwin sample stopped" )

class RestServer():
    """
    This creates rest server using bottle
    """

    def __init__(self):

        self._stop_requested = False
        self._stopped = threading.Event()
        self._stopped.clear()
        self._rest_host = ''
        self._rest_port = '80'
        self._remote_host = '192.168.0.100'
        self._app = Bottle()
        self._is_connected = False
        self._route()
        self._enable_cors()

    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

    def _get_update_status(self):
        self._enable_cors()
        return get_iothub_device_twin('ota')

    def _get_reboot_status(self):
        self._enable_cors()
        return get_iothub_device_twin('reboot')

    def _update_device_twin(self):
        #self._enable_cors()
        UPDATE_JSON = "{\"properties\":{\"desired\":{\"software_version\":\"%s\", \"reboot\":\"%s\", \"url\":\"%s\"}}}"
        try:
            post = json.load(request.body)
            msg_json = UPDATE_JSON % (str(post['software_version']), str(post['reboot']), str(post['url']))
            iothub_twin_method = IoTHubDeviceTwin(CONNECTION_STRING)
            twin_info = iothub_twin_method.update_twin(DEVICE_ID, msg_json)
        except Exception as err:
            return str(err)

        return "200 OK\n"


    def _update_reboot(self):
        UPDATE_JSON = "{\"properties\":{\"desired\":{\"reboot\":\"%s\"}}}"
        try:
            post = json.load(request.body)
            msg_json = UPDATE_JSON % (str(post['reboot']))
            iothub_twin_method = IoTHubDeviceTwin(CONNECTION_STRING)
            twin_info = iothub_twin_method.update_twin(DEVICE_ID, msg_json)
        except Exception as err:
            return str(err)

        return "200 OK\n"


    def _send_ok(self):
        return "200 OK"

    def _route(self):
        ROUTE = '/updatestatus'
        self._app.route(ROUTE, method="GET", callback=self._get_update_status)

        ROUTE = '/getRebootStatus'
        self._app.route(ROUTE, method="GET", callback=self._get_reboot_status)

        ROUTE = '/updatetwin'
        self._app.route(ROUTE, method="POST", callback=self._update_device_twin)

        ROUTE = '/updatereboot'
        self._app.route(ROUTE, method="POST", callback=self._update_reboot)

        ROUTE = '/updatetwin'
        self._app.route(ROUTE, method="OPTIONS", callback=self._send_ok)

    def start(self):
        threading.Thread(target=self._rest_serve).start()


    def _rest_serve(self):
        self._app.run(host=self._rest_host, port=self._rest_port, debug=False)

if __name__ == '__main__':
    print ( "" )
    print ( "Python {0}".format(sys.version) )
    print ( "IoT Hub Service Client for Python" )
    print ( "" )
    """
    try:
        (CONNECTION_STRING, DEVICE_ID, MODULE_ID) = get_iothub_opt_with_module(sys.argv[1:], CONNECTION_STRING, DEVICE_ID, MODULE_ID)
    except OptionError as option_error:
        print ( option_error )
        usage()
        sys.exit(1)

    print ( "Starting the IoT Hub Service Client ModuleTwin Python sample..." )
    print ( "    Connection string = {0}".format(CONNECTION_STRING) )
    print ( "    Device ID         = {0}".format(DEVICE_ID) )
    """
    rest = RestServer()
    rest.start()

