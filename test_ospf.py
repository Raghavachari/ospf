import pytest
import unittest
import logging
import json
import time
import ConfigParser
import glob
import commands
import ib_NIOS

CONF = "config.ini"
parser = ConfigParser.SafeConfigParser()
parser.read(CONF)
GRID_VIP = parser.get('Default', 'GRID_VIP')
Members = parser.get('Default', 'Members')
Area_ID = parser.get('Default', 'Area_ID')
OS_USERNAME = parser.get('Default', 'OS_USERNAME')
OS_PASSWORD = parser.get('Default', 'OS_PASSWORD')
OS_TENANT_NAME = parser.get('Default', 'OS_TENANT_NAME')
OS_AUTH_URL = parser.get('Default', 'OS_AUTH_URL')

class OSPF_Config(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_add_ospf_conf(self):
        logging.info("Adding OSPF Configuration Using Heat Template")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-create -f " + input_file[0] + " -P 'area_id=" + Area_ID + ";grid_members=" + Members + "' ospf_conf3")
        time.sleep(10)
        logging.info(out)

    @pytest.mark.run(order=2)
    def test_validate_nios_ospf_conf(self):
        flag = False
        logging.info("Validating OSPF Configuration in NIOS")
        params = "?host_name=" + Members + "&_return_fields=ospf_list"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        x = json.loads(response)[0]['ospf_list'][0]['area_id']
        if x == Area_ID:
            flag = True
        assert flag

    @pytest.mark.run(order=3)
    def test_add_anycast_loopback_with_ospf(self):
        logging.info("Adding Anycast Loopback IP with OSPF")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + "/' anycast-loopback.yaml")
        input_file = glob.glob("anycast-loopback.yaml")
        time.sleep(20)
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-create -f " + input_file[0] + " -P 'ip=3.3.3.3;enable_ospf=true;grid_members=" + Members + "' anycast")
        time.sleep(10)
        logging.info(out)
        logging.info("Validating Anycast Loopback IP in NIOS")
        flag = False
        params = "?host_name=" + Members + "&_return_fields=additional_ip_list"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        x = json.loads(response)[0]["additional_ip_list"][0]
        if ( x['ipv4_network_setting']['address'] == '3.3.3.3' and x["enable_ospf"] == True ):
            flag = True
        assert flag
