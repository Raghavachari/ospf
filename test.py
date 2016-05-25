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
    def test_add_ospf_conf_with_default_values(self):
        logging.info("Adding OSPF Configuration Using Heat Template")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-create -f " + input_file[0] + " -P 'area_id=" + Area_ID + ";grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        time.sleep(10)
        logging.info(out)
	
    @pytest.mark.run(order=2)
    def test_validate_nios_ospf_conf(self):
        flag = False
        logging.info("Validating OSPF Configuration in NIOS")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]['area_id']
            assert x == Area_ID , "Area_ID did not match for %s member" % i
		
    @pytest.mark.run(order=3)
    def test_update_area_type_and_authentication(self):
        logging.info("Updating area_type to STUB and authentication to SIMPLE")
	commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + "/' ospf-settings.yaml")
	input_file = glob.glob("ospf-settings.yaml")
	out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-update -f " + input_file[0] + " -P 'area_id=" + Area_ID + ";area_type=STUB;authentication_type=SIMPLE;authentication_key=test;grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        time.sleep(5)
        logging.info(out)
		
    @pytest.mark.run(order=4)
    def test_validate_area_type_and_authentication(self):
	flag = False
	logging.info("Validating area_type and authentication")
	params = "?host_name=" + Members + "&_return_fields=ospf_list"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        x = json.loads(response)[0]['ospf_list'][0]['area_type']
	y = json.loads(response)[0]['ospf_list'][0]['authentication_type']
        if ( x == 'STUB' and y == 'SIMPLE' ):
            flag = True
        assert flag

    @pytest.mark.run(order=5)
    def test_update_area_type_to_nssa_and_authentication_md5(self):
        logging.info("Updating area_type to NSSA and authentication to MD5")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-update -f " + input_file[0] + " -P 'area_id=" + Area_ID + ";area_type=NSSA;authentication_type=MESSAGE_DIGEST;key_id=2;authentication_key=test;grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        time.sleep(5)
        logging.info(out)

    @pytest.mark.run(order=6)
    def test_validate_area_typei_nssa_and_authentication_md5(self):
        flag = False
        logging.info("Validating area_type and authentication")
        params = "?host_name=" + Members + "&_return_fields=ospf_list"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        x = json.loads(response)[0]['ospf_list'][0]['area_type']
        y = json.loads(response)[0]['ospf_list'][0]['authentication_type']
        z = json.loads(response)[0]['ospf_list'][0]['key_id']
        if ( x == 'NSSA' and y == 'MESSAGE_DIGEST' and z == 2):
            flag = True
        assert flag

    @pytest.mark.run(order=7)
        logging.info("Updating ")
