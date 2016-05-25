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
Area_ID_v6 = parser.get('Default', 'Area_ID_v6')
OS_USERNAME = parser.get('Default', 'OS_USERNAME')
OS_PASSWORD = parser.get('Default', 'OS_PASSWORD')
OS_TENANT_NAME = parser.get('Default', 'OS_TENANT_NAME')
OS_AUTH_URL = parser.get('Default', 'OS_AUTH_URL')


class OspfConfig(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_add_ospf_conf_with_default_values(self):
        logging.info("Adding OSPF Configuration Using Heat Template")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                               " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                               " stack-create -f " + input_file[0] + " -P 'area_id=" + Area_ID + \
                               ";grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        status = ib_NIOS.wait_for_stack("ospf_conf_v4")
        assert status, "STACK CREATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=2)
    def test_validate_nios_ospf_conf(self):
        logging.info("Validating OSPF Configuration in NIOS")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]['area_id']
            assert x == Area_ID , "Area_ID did not match for %s member" % i

    @pytest.mark.run(order=3)
    def test_update_area_type_to_stub_and_authentication_simple(self):
        logging.info("Updating area_type to STUB and authentication to SIMPLE")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                               " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                               " stack-update -f " + input_file[0] + " -P 'area_id=" + Area_ID + \
                               ";area_type=STUB;authentication_type=SIMPLE;authentication_key=test;grid_members=" \
                               + Members + ";is_ipv4=True' ospf_conf_v4")
        status = ib_NIOS.wait_for_stack("ospf_conf_v4")
        assert status, "STACK UPDATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=4)
    def test_validate_area_type_to_stub_and_authentication_simple(self):
        flag = False
        logging.info("Validating area_type and authentication")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]['area_type']
            y = json.loads(response)[0]['ospf_list'][0]['authentication_type']
            if x == 'STUB' and y == 'SIMPLE':
                flag = True
            assert flag

    @pytest.mark.run(order=5)
    def test_update_area_type_to_nssa_and_authentication_md5(self):
        logging.info("Updating area_type to NSSA and authentication to MD5")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                               + " stack-update -f " + input_file[0] + " -P 'area_id=" + Area_ID \
                               + ";area_type=NSSA;authentication_type=MESSAGE_DIGEST;key_id=2;authentication_key=test"\
                                 ";grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        status = ib_NIOS.wait_for_stack("ospf_conf_v4")
        assert status, "STACK UPDATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=6)
    def test_validate_area_type_nssa_and_authentication_md5(self):
        flag = False
        logging.info("Validating area_type and authentication")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]['area_type']
            y = json.loads(response)[0]['ospf_list'][0]['authentication_type']
            z = json.loads(response)[0]['ospf_list'][0]['key_id']
            if x == 'NSSA' and y == 'MESSAGE_DIGEST' and z == 2:
                flag = True
            assert flag

    @pytest.mark.run(order=7)
    def test_update_hellointerval_retransmit_interval_delay(self):
        logging.info("Updating HelloInterval,DeadInterval,RetransmitInterval and Delay")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                               " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                               " stack-update -f " + input_file[0] + " -P 'area_id=" + Area_ID + \
                               ";hello_interval=20;dead_interval=80;retransmit_interval=10;transmit_delay=2"\
                               ";grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        status = ib_NIOS.wait_for_stack("ospf_conf_v4")
        assert status, "STACK UPDATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=8)
    def test_validate_itervals_and_delay(self):
        logging.info("Validating HelloInterval,Dead Interval,RetransmitInterval and Delay")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]
            if x['hello_interval'] == 20 and x['dead_interval'] == 80 \
                    and x['retransmit_interval'] == 10 and x['transmit_delay'] == 2:
                flag = True
            else:
                flag = False
            assert flag

    @pytest.mark.run(order=9)
    def test_add_anycast_loopback_with_ospf(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Adding Anycast Loopback IP with OSPF")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP \
                           + "/' anycast-loopback.yaml")
        input_file = glob.glob("anycast-loopback.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                               + " stack-create -f " + input_file[0] \
                               + " -P 'ip=3.3.3.3;enable_ospf=true;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK CREATE FAILED"
        if GRID_VIP in y:
            time.sleep(90)
        logging.info("Validating Anycast Loopback IP in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if x['ipv4_network_setting']['address'] == '3.3.3.3' and x["enable_ospf"] == True:
                flag = True
            assert flag

    @pytest.mark.run(order=10)
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
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " \
                               + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                               + OS_AUTH_URL + " stack-update -f " + input_file[0] \
                               + " -P 'ip=4.4.4.4;enable_ospf=false;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK UPDATE FAILED"
        if GRID_VIP in y:
            time.sleep(90)
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

    @pytest.mark.run(order=11)
    def test_update_ospf_conf_comment_and_cost(self):
        logging.info("Update OSPF Conf and add comment, disable auto_calc_cost and add cost")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                               " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                               " stack-update -f " + input_file[0] + " -P 'area_id=" + Area_ID + \
                               ";comment=test;auto_calc_cost_enabled=False;cost=10" \
                               ";grid_members=" + Members + ";is_ipv4=True' ospf_conf_v4")
        status = ib_NIOS.wait_for_stack("ospf_conf_v4")
        assert status, "STACK UPDATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=12)
    def test_validate_comment_and_cost_in_ospf_conf(self):
        logging.info("Validating comment, disable auto_calc_cost and cost in OSPF Conf")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list'][0]
            if x['comment'] == "test" and x['auto_calc_cost_enabled'] == False \
                    and x['cost'] == 10:
                flag = True
            else:
                flag = False
            assert flag

    @pytest.mark.run(order=13)
    def test_delete_ospf_config_when_anycast_ip_exist_negative_case(self):
        logging.info("Delete OSPF Configuration using heat when anycast ip exist with OSPF enabled")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                               + OS_AUTH_URL + " stack-delete ospf_conf_v4")
        logging.info(out)
        logging.info("Validating Anycast OSPF Configuration should not delete on NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list']
            if len(x) > 0:
                flag = True
            assert flag

    @pytest.mark.run(order=14)
    def test_delete_anycast_loopback_ip(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Delete Anycast Loopback IP")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                               + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                               + OS_AUTH_URL + " stack-delete anycast")
        if GRID_VIP in y:
            time.sleep(90)
        time.sleep(10)
        logging.info(out)
        logging.info("Validating Anycast Loopback IP is delete on NIOS")
        flag = False
        v = Members.split(',')
        time.sleep(5)
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]["additional_ip_list"]
            if not x:
                flag = True
            assert flag

    @pytest.mark.run(order=15)
    def test_delete_ospf_config(self):
        logging.info("Delete OSPF Configuration using heat")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " \
                               + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                               + OS_AUTH_URL + " stack-delete ospf_conf_v4")
        logging.info(out)
        logging.info("Validating Anycast OSPF Configuration delete on NIOS")
        flag = False
        time.sleep(10)
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
            x = json.loads(response)[0]['ospf_list']
            if not x:
                flag = True
            assert flag

    @pytest.mark.run(order=16)
    def test_add_ospf_conf_v6(self):
        logging.info("Adding OSPF IPv6 Configuration Using Heat Template")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP \
                           + "/' ospf-settings.yaml")
        input_file = glob.glob("ospf-settings.yaml")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                                 + " stack-create -f " + input_file[0] + " -P 'area_id=" + Area_ID_v6 \
                                 + ";grid_members=" + Members + ";is_ipv4=False' ospf_conf_v6")
        status = ib_NIOS.wait_for_stack("ospf_conf_v6")
        assert status, "STACK CREATION FAILED"
        logging.info(out)

    @pytest.mark.run(order=17)
    def test_validate_nios_ospf_conf_v6(self):
        flag = False
        logging.info("Validating OSPF IPv6 Configuration in NIOS")
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]['ospf_list'][0]['area_id']
            assert x == Area_ID_v6, "Area_ID did not match for %s member" % i

    @pytest.mark.run(order=18)
    def test_add_anycast_loopback_ipv6_with_ospf(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Adding Anycast Loopback IPv6 Address with OSPF")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" \
                           + GRID_VIP + "/' anycast-loopback.yaml")
        input_file = glob.glob("anycast-loopback.yaml")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                                 + " stack-create -f " + input_file[0] \
                                 + " -P 'ip=2020::20;enable_ospf=true;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK CREATION FAILED"
        if GRID_VIP in y:
            time.sleep(90)
        time.sleep(10)
        logging.info("Validating Anycast Loopback IPv6 Address in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if (x['ipv6_network_setting']['virtual_ip'] == '2020::20' and x["enable_ospf"] == True):
                flag = True
            assert flag

    @pytest.mark.run(order=19)
    def test_update_anycast_loopback_ipv6_address(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Update Anycast Loopback IPv6 Addtess")
        input_file = glob.glob("anycast-loopback.yaml")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                                 + " stack-update -f " + input_file[0] \
                                 + " -P 'ip=2010::10;enable_ospf=false;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK UPDATE FAILED"
        if GRID_VIP in y:
            time.sleep(90)
        time.sleep(10)
        logging.info("Validating Updated Anycast Loopback IPv6 Address in NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["additional_ip_list"][0]
            if (x['ipv6_network_setting']['virtual_ip'] == '2010::10' and x["enable_ospf"] == False):
                flag = True
            assert flag

    @pytest.mark.run(order=20)
    def test_delete_anycast_loopback_ipv6_address(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Delete Anycast Loopback IPv6 Address")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                                 + OS_AUTH_URL + " stack-delete anycast")
        logging.info(out)
        if GRID_VIP in y:
            time.sleep(90)
        time.sleep(10)
        logging.info("Validating Anycast Loopback IPv6 Address is delete on NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=additional_ip_list"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["additional_ip_list"]
            if not x:
                flag = True
            assert flag

    @pytest.mark.run(order=21)
    def test_delete_ospf_ipv6_config(self):
        logging.info("Delete OSPF IPV6 Configuration using heat")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " \
                                 + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                                 + OS_AUTH_URL + " stack-delete ospf_conf_v6")
        logging.info(out)
        time.sleep(10)
        logging.info("Validating Anycast OSPF IPv6 Configuration delete on NIOS")
        flag = False
        v = Members.split(',')
        for i in v:
            params = "?host_name=" + i + "&_return_fields=ospf_list"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]['ospf_list']
            if not x:
                flag = True
            assert flag
