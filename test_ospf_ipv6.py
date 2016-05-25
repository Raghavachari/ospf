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
Area_ID_v6 = parser.get('Default', 'Area_ID_v6')
OS_USERNAME = parser.get('Default', 'OS_USERNAME')
OS_PASSWORD = parser.get('Default', 'OS_PASSWORD')
OS_TENANT_NAME = parser.get('Default', 'OS_TENANT_NAME')
OS_AUTH_URL = parser.get('Default', 'OS_AUTH_URL')

class OSPF_IPv6_ConfigSuite(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_add_ospf_conf_v6(self):
        logging.info("Adding OSPF IPv6 Configuration Using Heat Template")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP \
                           + "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                               + " stack-create -f " + input_file[0] + " -P 'area_id=" + Area_ID_v6 \
                               + ";grid_members=" + Members + ";is_ipv4=False' ospf_conf_v6")
        status = ib_NIOS.wait_for_stack("ospf_conf_v6")
        assert status, "STACK CREATION FAILED"
        logging.info(out)

    @pytest.mark.run(order=2)
    def test_validate_nios_ospf_conf_v6(self):
        flag = False
        logging.info("Validating OSPF IPv6 Configuration in NIOS")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]['area_id']
            assert x == Area_ID_v6, "Area_ID did not match for %s member" % i

    @pytest.mark.run(order=3)
    def test_add_anycast_loopback_ipv6_with_ospf(self):
        logging.info("Adding Anycast Loopback IPv6 Address with OSPF")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" \
                           + GRID_VIP + "/' anycast-loopback.yaml")
        input_file = glob.glob("anycast-loopback.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                               + " stack-create -f " + input_file[0] \
                               + " -P 'ip=2020::20;enable_ospf=true;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK CREATION FAILED"
        logging.info("Validating Anycast Loopback IPv6 Address in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if ( x['ipv6_network_setting']['virtual_ip'] == '2020::20' and x["enable_ospf"] == True ):
                flag = True
            assert flag

    @pytest.mark.run(order=4)
    def test_update_anycast_loopback_ipv6_address(self):
        logging.info("Update Anycast Loopback IPv6 Addtess")
        input_file = glob.glob("anycast-loopback.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                               + " stack-update -f " + input_file[0] \
                               + " -P 'ip=2010::10;enable_ospf=false;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK UPDATE FAILED"
        logging.info("Validating Updated Anycast Loopback IPv6 Address in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if ( x['ipv6_network_setting']['virtual_ip'] == '2010::10' and x["enable_ospf"] == False ):
                flag = True
            assert flag

    @pytest.mark.run(order=5)
    def test_delete_anycast_loopback_ipv6_address(self):
        logging.info("Delete Anycast Loopback IPv6 Address")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                               + OS_AUTH_URL + " stack-delete anycast")
        logging.info(out)
        time.sleep(10)
        logging.info("Validating Anycast Loopback IPv6 Address is delete on NIOS")
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
    def test_delete_ospf_ipv6_config(self):
        logging.info("Delete OSPF IPV6 Configuration using heat")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " \
                               + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                               + OS_AUTH_URL + " stack-delete ospf_conf_v6")
        logging.info(out)
        time.sleep(10)
        logging.info("Validating Anycast OSPF IPv6 Configuration delete on NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list']
            if not x:
                flag = True
            assert flag
