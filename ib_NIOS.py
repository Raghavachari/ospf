import ConfigParser
import logging
import httplib
import json
import time
import ssl
from json import loads
import commands

CONF="config.ini"
parser = ConfigParser.SafeConfigParser()
parser.read(CONF)
GRID_VIP = parser.get('Default', 'GRID_VIP')
USERNAME = "admin"
PASSWORD = "infoblox"
VERSION = "2.3"
PATH = '/wapi/v' + VERSION + '/'
DEFAULT_OBJECT_TYPE = "member"
URLENCODED = 'application/json'
DEFAULT_CONTENT_TYPE = URLENCODED

# WAPI Call methods

def wapi_request(operation, ref='', params='', fields='', \
                    object_type=DEFAULT_OBJECT_TYPE, \
                    content_type=DEFAULT_CONTENT_TYPE):
    '''
    Send an HTTPS request to the NIOS server.
    '''
    # Create connection and request header.
    # This class does not perform any verification of the server`s certificate.
    #conn = httplib.HTTPSConnection(GRID_VIP,context=ssl._create_unverified_context())
    conn = httplib.HTTPSConnection(GRID_VIP)
    auth_header = 'Basic %s' % (':'.join([USERNAME, PASSWORD])
                                .encode('Base64').strip('\r\n'))
    request_header = {'Authorization':auth_header,
                      'Content-Type': content_type}
    if ref:
        url = PATH + ref
    else:
        url = PATH + object_type
    if params:
        url += params
    conn.request(operation, url, fields, request_header)
    response = conn.getresponse();
    if response.status >= 200 and response.status < 300:
        return handle_success(response)
    else:
        return handle_exception(response)

def handle_exception(response):
    '''
    If there was encountered an error while performing requested action,
    print response code and error message.
    '''
    logging.info('Request finished with error, response code: %i %s'\
            % (response.status, response.reason))
    json_object = json.loads(response.read())
    logging.info('Error message: %s' % json_object['Error'])
    raise Exception('WAPI Error message: %s' % json_object['Error'])
    return json_object


def handle_success(response):
    '''
    If the action requested by the client was received, understood, accepted
    and processed successfully, print response code and return response body.
    '''
    logging.info('Request finished successfully with response code: %i %s'\
            % (response.status, response.reason))
    return response.read()

def wait_for_stack(stack):
    status = commands.getoutput("heat stack-show " + stack + " | tr -d ' ' | grep stack_status\| | cut -f3 -d\|")
    flag = False
    count = 0
    while 1:
        if count >= 5:
            break
        if "COMPLETE" in status:
            flag = True
            break
        time.sleep(5)
        status = commands.getoutput("heat stack-show " + stack + " | tr -d ' ' | grep stack_status\| | cut -f3 -d\|")
        count = count + 1
    return flag




