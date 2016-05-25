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
    def test_add_anycast_loopback_with_ospf(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Adding Anycast Loopback IP with OSPF")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + "/' anycast-loopback.yaml")
        input_file = glob.glob("anycast-loopback.yaml")
        time.sleep(10)
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-create -f " + input_file[0] + " -P 'ip=3.3.3.3;enable_ospf=true;grid_members=" + Members + "' anycast")
        if GRID_VIP in y:
            time.sleep(90)
        logging.info(out)
        logging.info("Validating Anycast Loopback IP in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if ( x['ipv4_network_setting']['address'] == '3.3.3.3' and x["enable_ospf"] == True ):
                flag = True
            assert flag

    @pytest.mark.run(order=4)
    def test_update_anycast_loopback_ip(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Update Anycast Loopback IP")
        input_file = glob.glob("anycast-loopback.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-update -f " + input_file[0] + " -P 'ip=4.4.4.4;enable_ospf=false;grid_members=" + Members + "' anycast")
        if GRID_VIP in y:
            time.sleep(90)
        logging.info(out)
        logging.info("Validating Updated Anycast Loopback IP in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if ( x['ipv4_network_setting']['address'] == '4.4.4.4' and x["enable_ospf"] == False ):
                flag = True
            assert flag

    @pytest.mark.run(order=5)
    def test_delete_anycast_loopback_ip(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Delete Anycast Loopback IP")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-delete anycast")
        if GRID_VIP in y:
            time.sleep(90)
        logging.info(out)
        logging.info("Validating Anycast Loopback IP is delete on NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"]
            if not x:
                flag = True
            assert flag

    @pytest.mark.run(order=6)
    def test_delete_ospf_config(self):
        logging.info("Delete OSPF Configuration using heat")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + " stack-delete ospf_conf_v4")
        logging.info(out)
        logging.info("Validating Anycast OSPF Configuration delete on NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list']
            if not x:
                flag = True
            assert flag
