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
GRID_VIP = parser.get('BGP', 'GRID_VIP')
Members = parser.get('BGP', 'Members')
AS = parser.get('BGP', 'AS')
authentication_mode = parser.get('BGP', 'authentication_mode')
bgp_neighbor_pass = parser.get('BGP', 'bgp_neighbor_pass')
comment = parser.get('BGP', 'authentication_mode')
holddown = parser.get('BGP', 'holddown')
interface = parser.get('BGP', 'interface')
keepalive = parser.get('BGP', 'keepalive')
link_detect = parser.get('BGP', 'link_detect')
neighbor_ip = parser.get('BGP', 'neighbor_ip')
remote_as = parser.get('BGP', 'remote_as')
neighbor_ipv6 = parser.get('BGP', 'neighbor_ipv6')
OS_USERNAME = parser.get('BGP', 'OS_USERNAME')
OS_PASSWORD = parser.get('BGP', 'OS_PASSWORD')
OS_TENANT_NAME = parser.get('BGP', 'OS_TENANT_NAME')
OS_AUTH_URL = parser.get('BGP', 'OS_AUTH_URL')


class BgpConfig(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_add_bgp_conf_with_default_values(self):
        logging.info("Adding BGP Configuration Using Heat Template")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' bgp-settings.yaml")
        input_file = glob.glob("bgp-settings.yaml")
        out=commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                               " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                               " stack-create -f " + input_file[0] + " -P 'as=" + AS + ";authentication_mode="\
                               + authentication_mode + ";bgp_neighbor_pass=" + bgp_neighbor_pass + ";comment="\
                               + comment + ";holddown=" + holddown + ";interface=" + interface + ";keepalive="\
                               + keepalive + ";link_detect=" + link_detect + ";neighbor_ip=" + neighbor_ip +\
                               ";remote_as=" + remote_as + ";grid_member=" + Members + "' bgp_conf_v4")
        status = ib_NIOS.wait_for_stack("bgp_conf_v4")
        assert status, "STACK CREATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=2)
    def test_validate_nios_bgp_conf(self):
        logging.info("Validating BGP Configuration in NIOS")
        params = "?host_name=" + Members + "&_return_fields=bgp_as"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        asn = json.loads(response)[0]['bgp_as'][0]['as']
        hd = json.loads(response)[0]['bgp_as'][0]['holddown']
        kl = json.loads(response)[0]['bgp_as'][0]['keepalive']
        ld = json.loads(response)[0]['bgp_as'][0]['link_detect']
        auth_mode = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['authentication_mode']
        iface = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['interface']
        nip = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['neighbor_ip']
        ras = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['remote_as']
        flag = False
        if ( asn == int(AS) and hd == int(holddown) and kl == int(keepalive) and ld == False and \
                         auth_mode == authentication_mode and iface == interface and nip == neighbor_ip and \
                         ras == int(remote_as)):
            flag = True
        assert flag , "Values did not match"

    @pytest.mark.run(order=3)
    def test_update_asn_and_authmode(self):
        logging.info("Updating ASN and authentication mode to MD5")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' bgp-settings.yaml")
        input_file = glob.glob("bgp-settings.yaml")
        new_as = '44'
        new_authmode = 'MD5'
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                                 " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                                 " stack-update -f " + input_file[0] + " -P 'as=" + new_as + ";authentication_mode=" \
                                 + new_authmode + ";bgp_neighbor_pass=" + bgp_neighbor_pass + \
                                 ";neighbor_ip=" + neighbor_ip + ";remote_as=" + remote_as + ";grid_member=" \
                                 + Members + "' bgp_conf_v4")
        status = ib_NIOS.wait_for_stack("bgp_conf_v4")
        assert status, "STACK UPDATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=4)
    def test_validate_asn_and_authmode(self):
        flag = False
        logging.info("Validating ASN and authentication mode")
        params = "?host_name=" + Members + "&_return_fields=bgp_as"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        asn = json.loads(response)[0]['bgp_as'][0]['as']
        auth_mode = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['authentication_mode']
        if asn == 44 and auth_mode == 'MD5':
            flag = True
        assert flag

    @pytest.mark.run(order=5)
    def test_update_neighborip_from_ipv4_to_ipv6_and_remote_as(self):
        logging.info("Updating NeighborIP from IPv4 to IPv6 address")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP + \
                           "/' bgp-settings.yaml")
        input_file = glob.glob("bgp-settings.yaml")
        new_ras = '65534'
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD + \
                                 " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL + \
                                 " stack-update -f " + input_file[0] + " -P 'as=" + AS + ";authentication_mode=" \
                                 + authentication_mode + ";neighbor_ip=" + neighbor_ipv6 + ";remote_as=" + new_ras +\
                                 ";grid_member=" + Members + "' bgp_conf_v4")
        status = ib_NIOS.wait_for_stack("bgp_conf_v4")
        assert status, "STACK UPDATE FAILED"
        logging.info(out)

    @pytest.mark.run(order=6)
    def test_validate_neighborip_and_remote_as(self):
        flag = False
        logging.info("Validating Updated Neighbor IP and Remote AS")
        params = "?host_name=" + Members + "&_return_fields=bgp_as"
        response = ib_NIOS.wapi_request('GET', object_type = "member", params = params)
        nip = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['neighbor_ip']
        ras = json.loads(response)[0]['bgp_as'][0]['neighbors'][0]['remote_as']
        if nip == neighbor_ipv6 and ras == 65534:
            flag = True
        assert flag

    @pytest.mark.run(order=7)
    def test_add_anycast_loopback_with_bgp(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Adding Anycast Loopback IP with BGP")
        commands.getoutput("sed -i -r 's/[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/" + GRID_VIP \
                           + "/' anycast-loopback.yaml")
        input_file = glob.glob("anycast-loopback.yaml")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " + OS_AUTH_URL \
                                 + " stack-create -f " + input_file[0] \
                                 + " -P 'ip=3.3.3.3;enable_bgp=true;grid_members=" + Members + "' anycast")
        logging.info(out)
        status = ib_NIOS.wait_for_stack("anycast")
        assert status, "STACK CREATE FAILED"
        if GRID_VIP in y:
            time.sleep(90)
        logging.info("Validating Anycast Loopback IP in NIOS")
        flag = False
        params = "?host_name=" + Members + "&_return_fields=additional_ip_list"
        response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
        x = json.loads(response)[0]["additional_ip_list"][0]
        if x['ipv4_network_setting']['address'] == '3.3.3.3' and x["enable_bgp"] == True:
            flag = True
        assert flag

    @pytest.mark.run(order=8)
    def test_delete_bgp_config_when_anycast_ip_exist_negative_case(self):
        logging.info("Delete OSPF Configuration using heat when anycast ip exist with BGP enabled")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                                 + OS_AUTH_URL + " stack-delete bgp_conf_v4")
        logging.info(out)
        logging.info("Validating Anycast BGP Configuration should not delete on NIOS")
        flag = False
        params = "?host_name=" + Members + "&_return_fields=bgp_as"
        response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
        x = json.loads(response)[0]['bgp_as']
        if len(x) > 0:
            flag = True
        assert flag

    @pytest.mark.run(order=9)
    def test_delete_anycast_loopback_ip(self):
        v = Members.split(',')
        y = []
        for i in v:
            params = "?host_name=" + i + "&_return_fields=vip_setting"
            response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
            x = json.loads(response)[0]["vip_setting"]["address"]
            y.append(x)
        logging.info("Delete Anycast Loopback IP")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " + OS_PASSWORD \
                                 + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                                 + OS_AUTH_URL + " stack-delete anycast")
        if GRID_VIP in y:
            time.sleep(90)
        time.sleep(10)
        logging.info(out)
        logging.info("Validating Anycast Loopback IP is delete on NIOS")
        flag = False
        params = "?host_name=" + Members + "&_return_fields=additional_ip_list"
        response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
        x = json.loads(response)[0]["additional_ip_list"]
        if not x:
            flag = True
        assert flag

    @pytest.mark.run(order=10)
    def test_delete_bgp_config(self):
        logging.info("Delete BGP Configuration using heat")
        out = commands.getoutput("heat --os-username " + OS_USERNAME + " --os-password " \
                                 + OS_PASSWORD + " --os-tenant-name " + OS_TENANT_NAME + " --os-auth-url " \
                                 + OS_AUTH_URL + " stack-delete bgp_conf_v4")
        logging.info(out)
        logging.info("Validating Anycast BGP Configuration delete on NIOS")
        flag = False
        time.sleep(10)
        params = "?host_name=" + Members + "&_return_fields=ospf_list"
        response = ib_NIOS.wapi_request('GET', object_type="member", params=params)
        x = json.loads(response)[0]['ospf_list']
        if not x:
            flag = True
        assert flag