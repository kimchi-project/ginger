#
# Project Ginger
#
# Copyright IBM Corp, 2016
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

import atexit
import augeas
import ethtool
import os
import platform
import re
import shutil
import threading

from netaddr import IPAddress

from wok.exception import InvalidParameter, MissingParameter, OperationFailed
from wok.stringutils import decode_value, encode_value
from wok.utils import run_command, wok_log

from wok.plugins.gingerbase import netinfo


gingerNetworkLock = threading.RLock()
parser = augeas.Augeas("/")


@atexit.register
def augeas_cleanup():
    global parser
    del parser

ifcfg_filename_format = 'ifcfg-%s'
route_format = 'route-%s'
route6_format = 'route6-%s'
# cfgfile keys
BASIC_INFO = "BASIC_INFO"
NAME = 'NAME'
DEVICE = 'DEVICE'
ONBOOT = 'ONBOOT'
TYPE = 'TYPE'
MACADDR = 'MACADDR'
HWADDR = 'HWADDR'
UUID = 'UUID'
MTU = 'MTU'
ZONE = 'ZONE'
COLON = ':'
# z parameters
SUBCHANNELS = 'SUBCHANNELS'
NETTYPE = 'NETTYPE'
PORTNAME = 'PORTNAME'
OPTIONS = 'OPTIONS'
SLAVE = 'SLAVE'
MASTER = 'MASTER'
# interface types
IFACE_ETHERNET = 'nic'
IFACE_BOND = 'bonding'
IFACE_VLAN = 'vlan'

# Architecture type
ARCH_S390 = 's390x'

# Vlan parameters
VLANINFO = 'VLANINFO'
REORDER_HDR = 'REORDER_HDR'
VLAN = 'VLAN'
VLAN_ID = 'VLAN_ID'
PHYSDEV = 'PHYSDEV'
DOT = "."
VLANSTRING = "vlan"
FAIL_OVER_MAC = '/sys/class/net/%s/bonding/fail_over_mac'

# Bond parameters
BONDING_OPTS = 'BONDING_OPTS'
BONDING_MASTER = 'BONDING_MASTER'
BONDINFO = 'BONDINFO'
SLAVES = 'SLAVES'
BONDING_OPTS_LIST = ["ad_select", "arp_interval", "arp_ip_target",
                     "arp_validate", "downdelay", "fail_over_mac",
                     "lacp_rate", "miimon", "mode", "primary",
                     "primary_reselect", "resend_igmp", "updelay",
                     "use_carrier", "xmit_hash_policy"]

STATE_DOWN = "down"
CFGMAP_QUOTES = ["BONDING_OPTS"]

# ipv4 parameters
IPV4_ID = "IPV4_INFO"
BOOTPROTO = 'BOOTPROTO'

DHCP = 'dhcp'
AUTOIP = 'autoip'
MANUAL = 'none'
STATIC = "static"
BOOTPROTO_OPTIONS = [DHCP, AUTOIP, MANUAL]

# Use this connection only for resources on its network
DEFROUTE = 'DEFROUTE'
DNS = 'DNS'
DNSAddresses = 'DNSAddresses'
PEERROUTES = 'PEERROUTES'
IPV4_FAILURE_FATAL = 'IPV4_FAILURE_FATAL'
PEERDNS = 'PEERDNS'
IPADDR = 'IPADDR'
NETMASK = 'NETMASK'
PREFIX = 'PREFIX'
GATEWAY = 'GATEWAY'
IPV4INIT = 'IPV4INIT'
IPV4Addresses = "IPV4Addresses"
ROUTES = 'ROUTES'

# ipv6 parameters
IPV6_ID = "IPV6_INFO"
IPV6INIT = 'IPV6INIT'
IPV6_AUTOCONF = 'IPV6_AUTOCONF'
IPV6_DEFROUTE = 'IPV6_DEFROUTE'
IPV6_PEERDNS = 'IPV6_PEERDNS'
IPV6_PEERROUTES = 'IPV6_PEERROUTES'
IPV6_FAILURE_FATAL = 'IPV6_FAILURE_FATAL'
DHCPV6C = 'DHCPV6C'
IPV6ADDR = 'IPV6ADDR'
IPV6ADDR_SECONDARIES = 'IPV6ADDR_SECONDARIES'
IPV6_DEFAULTGW = 'IPV6_DEFAULTGW'
IPV6_PRIVACY = 'IPV6_PRIVACY'
IPV6Addresses = "IPV6Addresses"

# Routes related attributes
metric = "metric"
ADDRESS = "ADDRESS"
METRIC = "METRIC"
VIA = "via"

# other constants
CONST_YES = 'yes'
CONST_NO = 'no'
CONST_SPACE = ' '

# Assign variables based on distribution
if "SUSE" in platform.linux_distribution()[0]:
    network_configpath = 'etc/sysconfig/network/'
    DEVICE = 'NAME'
    ONBOOT = 'STARTMODE'
    PREFIX = 'PREFIXLEN'
else:
    network_configpath = 'etc/sysconfig/network-scripts/'


class CfgInterfacesHelper(object):
    """
    Class to help the cfginterfaces perform some operations using augeas.
    """

    def get_interface_list(self):
        nics = [nic for nic in ethtool.get_devices()]
        # skip nics other than ethernet,bond and type
        nics = self.filter_nics(nics)
        nics_with_cfgfiles = (self.get_bond_vlan_interfaces())
        # To ensure that comparision are done in same type.
        return set(map(encode_value, nics) +
                   map(encode_value, nics_with_cfgfiles))

    def filter_nics(self, interfaces):
        """
        This method will filter and return interfaces which are of type
        bond , ethernet and vlan
        :param interfaces:
        :return:
        """
        nics = []
        for nic in interfaces:
            if netinfo.get_interface_type(nic) in \
                    [IFACE_ETHERNET, IFACE_BOND,
                     IFACE_VLAN]:
                nics.append(nic)
        return nics

    def get_bond_vlan_interfaces(self):
        """
        This will return nics which are bond/vlan and are inactive with ifcfg
        files present. Scan for type in ifcfg files with bond/vlan value.
        If present, return name of the nic from the DEVICE attribute in file.
        :return: nics
        """
        nics = []
        try:
            gingerNetworkLock.acquire()
            pattern = network_configpath + '*/TYPE'
            parser.load()
            listout = parser.match(decode_value(pattern))
            for input in listout:
                interface_type = parser.get(decode_value(input))
                # Fix for ginger issue #70
                interface_type = self.trim_quotes(interface_type)
                if interface_type in [IFACE_BOND, IFACE_VLAN]:
                    cfg_file = input.rsplit('/', 1)[0]
                    try:
                        cfg_device = parser.get(decode_value(cfg_file +
                                                             '/DEVICE'))
                        # Fix for ginger issue #70
                        cfg_device = self.trim_quotes(cfg_device)
                        if (self.is_cfgfileexist(cfg_device)):
                            nics.append(cfg_device)
                        else:
                            wok_log.warn("no ifcfg file found,skipping" +
                                         cfg_device)
                    except Exception, e:
                        wok_log.warn("no device name found,skipping",
                                     e.message)
        finally:
            gingerNetworkLock.release()
        return nics

    def is_cfgfileexist(self, iface):
        """
        check if cfg file exists for interface .
        :param iface: interface name
        :return:True if file exist.
        """
        filename = ifcfg_filename_format % iface
        fileexist = os.path.isfile(os.sep + network_configpath + filename)
        if (not fileexist):
            return False
        else:
            return True

    def get_device(self, iface):
        """
        :param iface: interface name
        :return:DEVICE value in ifcfg file
        """
        return self.getValue(iface, DEVICE)

    def get_type(self, iface):
        """
        :param iface: interface name
        :return:TYPE value in ifcfg file
        """
        return self.getValue(iface, TYPE)

    def getValue(self, iface, key):
        """
        This method returns value of attribute in ifcfg file
        :param iface: interface name
        :param key: attribute/key to be checked in ifcfg file
        :return:value of key in ifcfgfile
        """
        key_val = ""
        try:
            gingerNetworkLock.acquire()
            if self.is_cfgfileexist(iface):
                file = network_configpath + ifcfg_filename_format % iface
                if self.token_exist(file, encode_value(key)):
                    key_val = parser.get(decode_value(file + "/" +
                                                      encode_value(key)))
                    # Fix for ginger issue #70
                    key_val = self.trim_quotes(key_val)
                    return encode_value(key_val)
        finally:
            gingerNetworkLock.release()
        return key_val

    def token_exist(self, ifcfg_file, key):
        """
        check if key exists in ifcfg file
        :param ifcfg_file:filepath patthern
        :param key: key to be checked/
        :return:True if key found
        """
        is_token_exist = False
        try:
            gingerNetworkLock.acquire()
            parser.load()
            l = parser.match(decode_value(ifcfg_file + os.sep + key))
            if len(l) == 1:
                is_token_exist = True
        finally:
            gingerNetworkLock.release()
        return is_token_exist

    # Fix for ginger issue #70
    def trim_quotes(self, param):
        """
           The function checks for single and double
           quotes in the param and trims the same
           is available and returns the trimmed
           param.
        """
        if (param[0] == param[-1]) \
           and param.startswith(("'", '"')) and ' ' not in param:
            param = param[1:-1]
        return param

    def validate_device_name(self, device_name):
        if device_name == "":
            raise MissingParameter("GINNET0025E")
        if len(device_name) > 15:
            raise InvalidParameter("GINNET0067E")
        if ' ' in device_name:
            raise InvalidParameter("GINNET0068E")

    def validate_minimal_info(self, params):
        cfg_map = {}
        if BASIC_INFO not in params:
            raise MissingParameter("GINNET0024E")
        if DEVICE not in params[BASIC_INFO]:
            raise MissingParameter("GINNET0025E")
        else:
            self.validate_device_name(params[BASIC_INFO][DEVICE])
            cfg_map[DEVICE] = params[BASIC_INFO][DEVICE]
            # Check for all the available interfaces to avoid
            # recreation of the same interface
            # ensure comparision are in same type.
            if decode_value(cfg_map[DEVICE]) in map(decode_value,
                                                    self.get_interface_list()):
                raise InvalidParameter('GINNET0072E', {'iface': cfg_map[
                    DEVICE]})
        if TYPE not in params[BASIC_INFO]:
            raise MissingParameter("GINNET0038E")
        else:
            cfg_map[TYPE] = params[BASIC_INFO][TYPE]
        return cfg_map

    def validate_info_for_vlan(self, params):
        if VLANINFO not in params[BASIC_INFO]:
            raise MissingParameter("GINNET0042E")
        if PHYSDEV not in params[BASIC_INFO][VLANINFO]:
            raise MissingParameter("GINNET0045E")

    def validate_vlan_driver(self):
        cmd = ['modprobe', '8021q']
        out, error, returncode = run_command(cmd)
        if returncode != 0:
            raise OperationFailed('GINNET0048E')

    def validate_dict_bond_for_vlan(self, cfgdata):
        if BASIC_INFO not in cfgdata:
            raise MissingParameter("GINNET0024E")
        if BONDINFO not in cfgdata[BASIC_INFO]:
            raise MissingParameter("GINNET0032E")
        if SLAVES not in cfgdata[BASIC_INFO][BONDINFO]:
            raise MissingParameter("GINNET0036E")

    def validate_interface(self, name):
        if encode_value(name) not in ethtool.get_devices():
            raise InvalidParameter('GINNET0014E', {'name': name})

    def read_ifcfg_file(self, interface_name):
        cfgmap = {}
        wok_log.info('Reading ifcfg file for interface ' + interface_name)
        filename = ifcfg_filename_format % interface_name
        # TODO file pattern to be changed to parse the device name inside
        # files rather than filename
        ifcfg_file_pattern = network_configpath + filename + '/*'
        fileexist = os.path.isfile(os.sep + network_configpath + filename)
        if (not fileexist):
            wok_log.info('ifcfg file not exist for'
                         ' interface :' + interface_name)
            return cfgmap
        # load everytime to reflect the current configuration in folder
        try:
            gingerNetworkLock.acquire()
            parser.load()
            listout = parser.match(decode_value(ifcfg_file_pattern))
            if not listout:
                wok_log.info('No attributes present in ifcfg file for '
                             'interface :' + interface_name)
                return cfgmap
            for single in listout:
                single = decode_value(single)
                labelVal = parser.get(single)
                labelVal = self.trim_quotes(labelVal)
                cfgmap[parser.label(single)] = labelVal
        except Exception, e:
            # typical error message e='Error during match procedure!',
            # u'etc/sysconfig/network-scripts/ifcfg-virbr0
            wok_log.error('Augeas parser throw run time exception', e.message)
            raise OperationFailed('GINNET0015E', {'error': e.message})
        finally:
            gingerNetworkLock.release()
        return cfgmap

    def get_master(self, cfgmap):
        master_bond = ''
        try:
            gingerNetworkLock.acquire()
            if MASTER in cfgmap:
                master_bond = cfgmap[MASTER]
                pattern = network_configpath + '*/DEVICE'
                parser.load()
                listout = parser.match(decode_value(pattern))
                master_found = False
                for device in listout:
                    if master_bond == self.trim_quotes(parser.get(
                                                       decode_value(device))):
                        master_found = True
                        master_bond = self.trim_quotes(parser.get(
                                                       decode_value(device)))
                        return master_bond
                if not master_found:
                    wok_log.info('No master found for slave:')
                    # TODO write logic to get master bond in case MASTER
                    #  = UUID//NMsupport
        finally:
            gingerNetworkLock.release()
        return master_bond

    def get_slaves(self, cfgmap):
        slaves = []
        try:
            gingerNetworkLock.acquire()
            master_device = cfgmap[DEVICE]
            pattern = network_configpath + '*/MASTER'
            parser.load()
            listout = parser.match(decode_value(pattern))
            slave_found = False
            for a_slave in listout:
                if master_device == self.trim_quotes(parser.get(
                                                     decode_value(a_slave))):
                    slave_found = True
                    slave_cfg_file = a_slave.rsplit('/', 1)[0]
                    slave_name = self.trim_quotes(parser.get(
                                                  decode_value(slave_cfg_file +
                                                               '/DEVICE')))
                    slaves.append(slave_name)
            if not slave_found:
                wok_log.info('No slaves found for master:' + master_device)
        finally:
            gingerNetworkLock.release()
        return slaves

    def validate_ipv4_address(self, ip):
        try:
            match = re.match(
                "^(\d{0,3})\.(\d{0,3})\.(\d{0,3})\.(\d{0,3})$", ip)
            if match:
                ip = IPAddress(ip)
                if ip.version == 4:
                    return
            raise Exception("Not an ipv4 address")
        except Exception, e:
            raise InvalidParameter('GINNET0018E', {'ip': ip,
                                                   'error': e.message})

    def validate_macaddress(self, macaddress):
        pattern = '^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if not re.match(pattern, macaddress):
            raise InvalidParameter('GINNET0092E', {'mac': macaddress})

    def delete_token_from_cfg(self, name, token):
        filename = self.get_iface_cfg_fullpath(name)
        try:
            gingerNetworkLock.acquire()
            parser.remove(decode_value(filename + os.sep + token))
            parser.save()
        except Exception, e:
            wok_log.error("Augeas parser throw run time exception ",
                          encode_value(e.message))
            raise OperationFailed("GINNET0058E", {'error': e.message})
        finally:
            gingerNetworkLock.release()

    def write_attributes_to_cfg(self, interface_name, cfgmap):
        try:
            gingerNetworkLock.acquire()
            filename = ifcfg_filename_format % interface_name
            parser.load()
            ifcfg_file_pattern = network_configpath + filename + '/'
            for key, value in cfgmap.iteritems():
                path = ifcfg_file_pattern + key
                parser.set(path, decode_value(value))
            parser.save()
        except Exception:
            raise InvalidParameter('GINNET0074E')
        finally:
            gingerNetworkLock.release()

    def get_iface_identifier(self, cfgmap):
        if DEVICE in cfgmap:
            return cfgmap[DEVICE]
        else:
            return None

    def validate_ipv6_address(self, ip):
        """
        Check if ip provided is valid ipv6 address
        :param ip: ipv6 address
        :return:
        """
        try:
            ip = IPAddress(ip)
            if ip.version == 6:
                return
            raise Exception("Not an ipv6 address")
        except Exception, e:
            raise InvalidParameter('GINNET0028E', {'ip': ip,
                                                   'error': e.message})

    def validateipinfo(self, ipaddrinfo):
        """
        validate ipv6 addresses info provided by user
        :param ipaddrinfo:
        :return:
        """
        if IPADDR in ipaddrinfo:
            self.validate_ipv6_address(ipaddrinfo[IPADDR])
        else:
            wok_log.error(("No ip address provided"))
        if PREFIX in ipaddrinfo:
            try:
                if COLON in ipaddrinfo[PREFIX]:
                    self.validate_ipv6_address(ipaddrinfo[PREFIX])
                    ipaddrinfo[PREFIX] = self.get_ipv6_prefix(
                        ipaddrinfo[PREFIX])
                else:
                    if int(ipaddrinfo[PREFIX]) >= 1\
                            and int(ipaddrinfo[PREFIX]) <= 128:
                        ipaddrinfo[PREFIX] = int(ipaddrinfo[PREFIX])
                    else:
                        raise InvalidParameter('GINNET0065E', {
                            'PREFIX': ipaddrinfo[PREFIX]})
            except Exception, e:
                raise InvalidParameter(
                    'GINNET0019E', {'PREFIX': ipaddrinfo[PREFIX],
                                    'error': e.message})
        else:
            raise MissingParameter('GINNET0021E')
        return ipaddrinfo

    def get_ipv6_prefix(self, ip):
        """
        get netmask from ipv6 address
        :param ip: ipv6 subnet provided bu user
        :return:
        """
        try:
            ip = IPAddress(ip)
            return ip.netmask_bits()
        except Exception, e:
            raise InvalidParameter('GINNET0019E', {'PREFIX': ip,
                                                   'error': e.message})

    def get_ipv4_prefix(self, ip):
        try:
            ip = IPAddress(ip)
            val = ip.is_netmask()
            if val:
                return ip.netmask_bits()
            else:
                raise Exception('')
        except:
            raise InvalidParameter('GINNET0071E', {'PREFIX': ip})

    def validate_populate_ipv4_routes(self, routes_input):
        modified_routes = []
        for routes in routes_input:
            route_info = routes
            if ADDRESS in routes:
                self.validate_ipv4_address(routes[ADDRESS])
            else:
                raise MissingParameter('GINNET0061E')
            if NETMASK in routes:
                match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})"
                                 "\.(\d{0,3})$", routes[NETMASK])
                if match:
                    self.validate_ipv4_address(routes[NETMASK])
                    route_info[NETMASK] = self.\
                        get_ipv4_prefix(routes[NETMASK])
                else:
                    if not int(routes[NETMASK]) >= 1 \
                            and int(routes[NETMASK]) <= 32:
                        raise InvalidParameter('GINNET0062E', {
                            'PREFIX': routes[NETMASK]})
            else:
                raise MissingParameter('GINNET0021E')
            if GATEWAY in routes:
                self.validate_ipv4_address(routes[GATEWAY])
            else:
                raise MissingParameter('GINNET0070E')
            modified_routes.append(route_info)
        return modified_routes

    def get_type_from_cfg(self, name):
        params = self.read_ifcfg_file(name)
        if params:
            if TYPE in params and params[TYPE] is not None:
                return params[TYPE]
            else:
                raise OperationFailed("GINNET0056E")
        else:
            return "n/a"

    def get_iface_cfg_fullpath(self, name):
        filename = ifcfg_filename_format % name
        ifcfg_file = network_configpath + filename
        return ifcfg_file

    def clean_slave_tokens(self, slave):
        wok_log.info("Removing slave information from slave " + slave)
        # TODO restart an interface or leave it as it is based on
        # investigation
        token_to_del = [MASTER, SLAVE]
        for each_token in token_to_del:
            self.delete_token_from_cfg(slave, each_token)

    # adding method to support multiple ipv4 in lookup listing
    def get_ipv4_addresses(self, cfgmap):
        ipv4addresses = []
        index = 0
        while True:
            dict = {}
            if index == 0:
                postfix = ''
            else:
                postfix = str(index)
            if IPADDR + postfix in cfgmap:
                dict.update(IPADDR=cfgmap[IPADDR + postfix])
            else:
                break
            if NETMASK + postfix in cfgmap:
                dict.update(PREFIX=cfgmap[NETMASK + postfix])
            if PREFIX + postfix in cfgmap:
                dict.update(PREFIX=cfgmap[PREFIX + postfix])
            if GATEWAY + postfix in cfgmap:
                dict.update(GATEWAY=cfgmap[GATEWAY + postfix])
            index += 1
            ipv4addresses.append(dict)
        return ipv4addresses

    def parse_ipv6prefix(self, ipv6_with_prefix):
        dict = {}
        splitout = ipv6_with_prefix.split('/')
        dict.update(IPADDR=splitout[0])
        dict.update(PREFIX=splitout[1])
        return dict

    def get_ipv6_address(self, cfgmap):
        ipv6addresses = []
        if IPV6ADDR in cfgmap:
            ipv6addresses.append(self.parse_ipv6prefix(cfgmap[IPV6ADDR]))
        if IPV6ADDR_SECONDARIES in cfgmap:
            split_with_space_result = \
                cfgmap[IPV6ADDR_SECONDARIES].split(CONST_SPACE)
            for eachsecondaryipv6 in split_with_space_result:
                ipv6addresses.append(self.parse_ipv6prefix(eachsecondaryipv6))
        return ipv6addresses

    def get_dnsv4_info(self, cfgmap):
        dnsaddresses = []
        index = 1
        if DNS in cfgmap:
            ip = IPAddress(cfgmap[DNS])
            if ip.version == 4:
                dnsaddresses.append(cfgmap[DNS])
        else:
            while True:
                postfix = str(index)
                if DNS + postfix in cfgmap:
                    ip = IPAddress(cfgmap[DNS + postfix])
                    if ip.version == 4:
                        dnsaddresses.append(cfgmap[DNS + postfix])
                else:
                    break
                index += 1
        return dnsaddresses

    def get_dnsv6_info(self, cfgmap):
        wok_log.debug('Begin get_dns_info')
        dnsaddresses = []
        if DNS in cfgmap:
            ip = IPAddress(cfgmap[DNS])
            if ip.version == 6:
                dnsaddresses.append(cfgmap[DNS])
        else:
            flag = 0
            dnscount = 1
            dnsincrmnt = DNS + str(dnscount)
            while flag == 0:
                if dnsincrmnt in cfgmap:
                    ip = IPAddress(cfgmap[dnsincrmnt])
                    if ip.version == 6:
                        dnsaddresses.append(cfgmap[dnsincrmnt])
                    dnscount = dnscount + 1
                    dnsincrmnt = DNS + str(dnscount)
                else:
                    flag = 1
        wok_log.debug('End get_dns_info')
        return dnsaddresses

    def get_architecture_specific_info(self, info, cfgmap):
        wok_log.debug('Begin get_architecture_specific_info')
        if platform.machine() == ARCH_S390:
            basic_info_keys = [SUBCHANNELS, NETTYPE, PORTNAME, OPTIONS]
            for key in basic_info_keys:
                if key in cfgmap:
                    info[BASIC_INFO][key] = cfgmap[key]
                if key == OPTIONS and key in cfgmap:
                    option_list = cfgmap[key].split(" ")
                    options_dict = dict()
                    for each in option_list:
                        if "=" in each:
                            each = each.replace("'", "")
                            each = each.replace('"', "")
                            each = each.split("=")
                            options_dict[each[0]] = each[1]
                            options_dict.update(options_dict)
                    info[BASIC_INFO][key] = options_dict
        wok_log.debug('End get_architecture_specific_info')
        return info

    def get_vlan_info(self, info, cfgmap):
        wok_log.debug('Begin get_vlan_info')
        info[BASIC_INFO][VLANINFO] = {}
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            vlan_info_keys = [VLAN_ID, VLAN, REORDER_HDR, PHYSDEV]
            for key in vlan_info_keys:
                if key in cfgmap:
                    info[BASIC_INFO][VLANINFO][key] = cfgmap[key]
        wok_log.debug('End get_vlan_info')
        return info

    def get_bond_info(self, info, cfgmap):
        wok_log.debug('Begin get_bond_info')
        info[BASIC_INFO][BONDINFO] = {}
        info[BASIC_INFO][BONDINFO][BONDING_OPTS] = {}
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            if BONDING_MASTER in cfgmap:
                info[BASIC_INFO][BONDINFO][BONDING_MASTER] = cfgmap[
                    BONDING_MASTER]
            if BONDING_OPTS in cfgmap:
                bonding_opts_str = cfgmap[BONDING_OPTS]
                bonding_opts_str = bonding_opts_str[1:-1]
                bonding_opts_str = bonding_opts_str.strip()
                bonding_opts_str = re.sub(' +', ' ', bonding_opts_str)
                bonding_opts_dict = dict(
                    x.split('=') for x in bonding_opts_str.split(' '))
                info[BASIC_INFO][BONDINFO][BONDING_OPTS] = bonding_opts_dict
            info[BASIC_INFO][BONDINFO][SLAVES] = self.get_slaves(cfgmap)
        wok_log.debug('End get_bond_info')
        return info

    def validate_and_get_vlanid(self, params, vlan_info, device):
        vlanid_range = range(0, 4096)
        vlanid_fromdevice = ''
        if DOT not in device and device.startswith(VLANSTRING):
            vlanid_fromdevice = self.convert_to_int_ifvalid(device[4:])
        elif device.count(DOT) == 1:
            vlanid_fromdevice = self.convert_to_int_ifvalid(device.split(
                DOT)[1])
        elif VLAN_ID not in params[BASIC_INFO][VLANINFO]:
            raise MissingParameter("GINNET0044E")
        if vlanid_fromdevice:
            if vlanid_fromdevice not in vlanid_range:
                raise InvalidParameter("GINNET0050E")
        if VLAN_ID in params[BASIC_INFO][VLANINFO]:
            vlan_id = params[BASIC_INFO][VLANINFO][VLAN_ID]
            if int(vlan_id) not in vlanid_range:
                raise InvalidParameter("GINNET0050E")
            vlan_info[VLAN_ID] = params[BASIC_INFO][VLANINFO][VLAN_ID]
        return vlan_info

    def convert_to_int_ifvalid(self, value):
        try:
            int_value = int(value)
        except ValueError, e:
            raise InvalidParameter("GINNET0066E", {'error': e.message})
        return int_value

    def clean_routes(self, interface_name, version):
        """
        This method will delete the route file for interface provided.
        :param interface_name:
        :param version: 4 for ipv4 and 6 for ipv6
        :return:
        """
        if version == 6:
            route_filename = route6_format % interface_name
        else:
            route_filename = route_format % interface_name
        route_filepath = '/' + network_configpath + route_filename
        if (os.path.isfile(route_filepath)):
            os.remove(route_filepath)

    def clean_slaves(self, cfgmap, params):
        existing_slaves = self.get_slaves(cfgmap)
        # Check for atleast one slave is required for a bond
        # interface.
        bondinfo = params[BASIC_INFO][BONDINFO]
        if SLAVES not in bondinfo:
            raise MissingParameter("GINNET0075E")
        new_slaves = bondinfo[SLAVES]
        common_slaves = list(set(existing_slaves).intersection(
            set(new_slaves)))
        slaves_to_be_deleted = list(set(existing_slaves) - set(common_slaves))
        if slaves_to_be_deleted:
            for each_slave in slaves_to_be_deleted:
                self.clean_slave_tokens(each_slave)

    def clean_DNS_attributes(self, cfgmap):
        """
        remove all DNS attributes present in cfgmap
        :param cfgmap:
        :return:
        """
        delattributes = []
        for key in cfgmap:
            if key.startswith(DNS):
                delattributes.append(key)
        for key in delattributes:
            if key in cfgmap:
                del cfgmap[key]
        return cfgmap

    def cleanup_ipv4attributes(self, cfgmap):
        """
        Remove all ipv4 related attributes in cfgmap.
        :param cfgmap:
        :return:
        """
        SINGLE_ATTRIBUTES = [IPV4_FAILURE_FATAL, PEERDNS, PEERROUTES,
                             BOOTPROTO, DEFROUTE]
        MULITPLE_ATTRIBUTES = [IPADDR, PREFIX, GATEWAY, DNS, NETMASK]
        delattributes = []
        for attr in SINGLE_ATTRIBUTES:
            if attr in cfgmap:
                delattributes.append(attr)
        for attr in MULITPLE_ATTRIBUTES:
            for key in cfgmap:
                if key.startswith(attr):
                    delattributes.append(key)
        for key in delattributes:
            if key in cfgmap:
                del cfgmap[key]
        return cfgmap

    def validate_bond_opts(self, bondopts, params):
        def validate_string(opt_value, possible_values):
            if opt_value not in possible_values:
                raise InvalidParameter("GINNET0040E")

        def validate_integer(opt_value):
            try:
                value = int(opt_value)
                if value < 0:
                    raise InvalidParameter("GINNET0040E")
            except ValueError:
                raise InvalidParameter("GINNET0040E")

        def validate_ad_select(opt_value):
            possible_values = ["stable", "bandwidth", "count", "0", "1", "2"]
            validate_string(opt_value, possible_values)

        def validate_arp_interval(opt_value):
            validate_integer(opt_value)

        def validate_arp_ip_target(opt_value):
            if type(opt_value) is list:
                if len(bond_opt_value) <= 16:
                    for key in bond_opt_value:
                        self.validate_ipv4_address(key)
                else:
                    raise InvalidParameter("GINNET0040E")
            else:
                self.validate_ipv4_address(bond_opt_value)

        def validate_arp_validate(opt_value):
            possible_values = ["none", "active", "backup", "all", "filter",
                               "filter_active", "filter_backup", "0", "1",
                               "2", "3", "4", "5"]
            validate_string(opt_value, possible_values)

        def validate_downdelay(opt_value):
            validate_integer(opt_value)

        def validate_fail_over_mac(opt_value):
            possible_values = ["none", "active", "follow", "0", "1", "2"]
            validate_string(opt_value, possible_values)

        def validate_lacp_rate(opt_value):
            possible_values = ["slow", "fast", "0", "1"]
            validate_string(opt_value, possible_values)

        def validate_miimon(opt_value):
            validate_integer(opt_value)

        def validate_mode(opt_value):
            possible_values = ["balance-rr", "active-backup", "balance-xor",
                               "broadcast", "802.3ad", "balance-tlb",
                               "balance-alb", "0", "1", "2", "3", "4", "5",
                               "6"]
            validate_string(opt_value, possible_values)

        def validate_primary(opt_value):
            self.validate_interface(opt_value)

        def validate_primary_reselect(opt_value):
            possible_values = ["always", "better", "failure", "0", "1", "2"]
            validate_string(opt_value, possible_values)

        def validate_resend_igmp(opt_value):
            try:
                value = int(opt_value)
                if value < 0 and value > 255:
                    raise InvalidParameter("GINNET0040E")
            except ValueError:
                raise InvalidParameter("GINNET0040E")

        def validate_updelay(opt_value):
            validate_integer(opt_value)

        def validate_use_carrier(opt_value):
            possible_values = ["0", "1"]
            validate_string(opt_value, possible_values)

        def validate_xmit_hash_policy(opt_value):
            possible_values = ["layer2", "layer2+3", "layer3+4", "encap2+3",
                               "encap3+4"]
            validate_string(opt_value, possible_values)

        bond_validate = \
            dict(ad_select=validate_ad_select,
                 arp_interval=validate_arp_interval,
                 arp_ip_target=validate_arp_ip_target,
                 arp_validate=validate_arp_validate,
                 downdelay=validate_downdelay,
                 fail_over_mac=validate_fail_over_mac,
                 lacp_rate=validate_lacp_rate, miimon=validate_miimon,
                 mode=validate_mode, primary=validate_primary,
                 primary_reselect=validate_primary_reselect,
                 resend_igmp=validate_resend_igmp, updelay=validate_updelay,
                 use_carrier=validate_use_carrier,
                 xmit_hash_policy=validate_xmit_hash_policy)
        for bond_opt_key in BONDING_OPTS_LIST:
            bondopts = params[BASIC_INFO][BONDINFO][BONDING_OPTS]
            if bond_opt_key in bondopts:
                bond_opt_value = bondopts[bond_opt_key]
                bond_validate[bond_opt_key](bond_opt_value)
        return True

    def write_cfgroutes(self, routes_map, interface_name, ipversion=4):
        """
        Route information will be written in ip format to the route file.
        Ex:-10.10.10.0/24 via 192.168.0.10 dev eth0
        :param routes_map: List of dictionaries containing route information
        :param interface_name: interface for which route info needs to be
        written
        :return:
        """
        route_filename = 4
        if ipversion == 4:
            route_filename = route_format % interface_name
        elif ipversion == 6:
            route_filename = route6_format % interface_name
        route_filepath = '/' + network_configpath + route_filename
        output_file = open(route_filepath, "w")
        for routes in routes_map:
            if ADDRESS in routes and NETMASK in routes and GATEWAY in routes:
                if METRIC in routes and routes[METRIC] != "":
                    format_routes = '{}/{} via {} metric {}'.format(
                        routes[ADDRESS],
                        routes[NETMASK],
                        routes[GATEWAY],
                        routes[METRIC])
                else:
                    format_routes = '{}/{} via {}'.format(routes[ADDRESS],
                                                          routes[NETMASK],
                                                          routes[GATEWAY])
                output_file.write(format_routes)
                output_file.write("\n")
        output_file.close()

    def assign_ipv4_address(self, cfgmap, params):
        if IPV4Addresses in params:
            index = 0
            for ipaddrinfo in params[IPV4Addresses]:
                if index == 0:
                    postfix = ''
                else:
                    postfix = str(index)
                if IPADDR in ipaddrinfo:
                    self.validate_ipv4_address(ipaddrinfo[IPADDR])
                    cfgmap[IPADDR + postfix] = ipaddrinfo[IPADDR]
                else:
                    raise MissingParameter('GINNET0020E')
                # Fix for issue 169
                if PREFIX in ipaddrinfo:
                    match = re.match("^(\d{0,3})\.(\d{0,3})\.(\d{0,3})"
                                     "\.(\d{0,3})$", ipaddrinfo[PREFIX])
                    if match:
                        self.validate_ipv4_address(ipaddrinfo[PREFIX])
                        # Below it will validate if valid prefix.
                        # If prefix is valid,then subnet can be assigned safe
                        self.get_ipv4_prefix(ipaddrinfo[PREFIX])
                        cfgmap[NETMASK + postfix] = ipaddrinfo[PREFIX]
                    else:
                        try:
                            if int(ipaddrinfo[PREFIX]) >= 1 and int(
                                    ipaddrinfo[PREFIX]) <= 32:
                                cfgmap[PREFIX + postfix] = \
                                    int(ipaddrinfo[PREFIX])
                            else:
                                raise InvalidParameter(
                                    'GINNET0062E',
                                    {'PREFIX': ipaddrinfo[PREFIX]})
                        except ValueError:
                                raise InvalidParameter(
                                    'GINNET0071E', {'PREFIX': ipaddrinfo[
                                        PREFIX]})
                else:
                    raise MissingParameter('GINNET0021E')
                if GATEWAY in ipaddrinfo:
                    self.validate_ipv4_address(ipaddrinfo[GATEWAY])
                    cfgmap[GATEWAY + postfix] = ipaddrinfo[GATEWAY]
                index += 1
        # Fix for issue 169
        else:
            raise MissingParameter('GINNET0061E')
        return cfgmap

    def assign_ipv6_address(self, cfgmap, params):
        """
        assign ipv6 addresses to network directives
        :param cfgmap: map containing the data from ifcfg files
        :param params:  input provided by user
        :return:
        """
        if IPV6Addresses in params:
            primary = True
            for ipaddrinfo in params[IPV6Addresses]:
                if (primary):
                    ipaddrinfo = self.validateipinfo(ipaddrinfo)
                    cfgmap[IPV6ADDR] = ipaddrinfo[IPADDR] + '/' + \
                        encode_value(ipaddrinfo[PREFIX])
                    primary = False
                else:
                    ipaddrinfo = self.validateipinfo(ipaddrinfo)
                    if IPV6ADDR_SECONDARIES in cfgmap:
                        cfgmap[IPV6ADDR_SECONDARIES] = \
                            cfgmap[IPV6ADDR_SECONDARIES] + CONST_SPACE + \
                            ipaddrinfo[IPADDR] + '/' + ipaddrinfo[PREFIX]
                    else:
                        cfgmap[IPV6ADDR_SECONDARIES] = \
                            ipaddrinfo[IPADDR] + '/' + ipaddrinfo[PREFIX]
        else:
            raise MissingParameter('GINNET0029E')
        return cfgmap

    def update_dnsv6_info(self, cfgmap, params):
        """
        Construct cfgmap with dns addresses information. If DNS={IPV61,IPV62}
        cfgmap will be updated with DNS1=IPV61, DNS2=IPV62 if no ipv4DNS is
        present in cfgmap. If ipv4 dns is present,the DNS increment
        will be after DNSv4 addresses For ex :- DNS=ipv41, then cfgmap will
        have DNS1=ipv41,DNS2=IPV61, DNS3=IPV62
        :param cfgmap:
        :param params:
        :return:
        """
        if DNSAddresses in params[IPV6_ID]:
            # initialize this feild based on ipv4 dns
            dnsstartindexcount = 0
            if DNS in cfgmap:
                dnsstartindexcount += 1
                cfgmap[DNS + str(dnsstartindexcount)] = cfgmap[DNS]
                del cfgmap[DNS]
                dnsstartindexcount += 1
            else:
                dnsstartindexcount += 1
                flag = 0
                while flag == 0:
                    dnsincrmnt = DNS + str(dnsstartindexcount)
                    if dnsincrmnt in cfgmap:
                        dnsstartindexcount += 1
                    else:
                        flag = 1

            list_dns_addresses = params[IPV6_ID][DNSAddresses]
            for addr in list_dns_addresses:
                cfgmap[DNS + str(dnsstartindexcount)] = addr
                dnsstartindexcount += 1
        return cfgmap

    def update_ipv6(self, cfgmap, params):
        """
        update ipv6 information in cfgmap read from ifcfg files
        :param cfgmap: map containing the data from ifcfg files
        :param params: input provided by user
        :return:
        """
        if IPV6INIT in params[IPV6_ID] and params[IPV6_ID][IPV6INIT] == \
                'yes':
            cfgmap[IPV6INIT] = params[IPV6_ID][IPV6INIT]
            if IPV6_FAILURE_FATAL in params[IPV6_ID]:
                cfgmap[IPV6_FAILURE_FATAL] = \
                    params[IPV6_ID][IPV6_FAILURE_FATAL]
            if IPV6_PEERDNS in params[IPV6_ID]:
                cfgmap[IPV6_PEERDNS] = params[IPV6_ID][IPV6_PEERDNS]
            if IPV6_PEERROUTES in params[IPV6_ID]:
                cfgmap[IPV6_PEERROUTES] = params[IPV6_ID][IPV6_PEERROUTES]
            cfgmap = self.update_ipv6_bootproto(cfgmap, params)
            cfgmap = self.update_dnsv6_info(cfgmap, params)
            if ROUTES in params[IPV6_ID]:
                self.write_cfgroutes(params[IPV6_ID][ROUTES],
                                     params[BASIC_INFO][DEVICE], 6)
            else:
                self.clean_routes(cfgmap[DEVICE], 6)
                # Fix ginger issue #42
        elif IPV6INIT in params[IPV6_ID] and params[IPV6_ID][IPV6INIT] == \
                'no':
            cfgmap[IPV6INIT] = params[IPV6_ID][IPV6INIT]
        else:
            raise MissingParameter('GINNET0027E')
        return cfgmap

    def update_ipv6_bootproto(self, cfgmap, params):
        """
        updated information based on boot protocol
        :param cfgmap: map containing the data from ifcfg files
        :param params:  input provided by user
        :return:
        """
        if IPV6_AUTOCONF in params[IPV6_ID]:
            if params[IPV6_ID][IPV6_AUTOCONF] == 'yes':
                cfgmap[IPV6_AUTOCONF] = CONST_YES
            elif params[IPV6_ID][IPV6_AUTOCONF] == 'no':
                cfgmap[IPV6_AUTOCONF] = CONST_NO
                if DHCPV6C in params[IPV6_ID]:
                    if params[IPV6_ID][DHCPV6C] == 'yes':
                        cfgmap[DHCPV6C] = CONST_YES
                else:
                    # Expecting manual mode values here
                    self.assign_ipv6_address(cfgmap, params[IPV6_ID])
        else:
            wok_log.error(("IPV6_AUTOCONF not provided:"))
            raise MissingParameter('GINNET0064E')
        if IPV6_DEFROUTE in params[IPV6_ID]:
            cfgmap[IPV6_DEFROUTE] = params[IPV6_ID][IPV6_DEFROUTE]
        if IPV6_DEFAULTGW in params[IPV6_ID]:
            self.validate_ipv6_address(params[IPV6_ID][IPV6_DEFAULTGW])
            cfgmap[IPV6_DEFAULTGW] = params[IPV6_ID][IPV6_DEFAULTGW]
        return cfgmap

    def update_cfgfile(self, cfgmap, params):
        iface_id = self.get_iface_identifier(cfgmap)
        p_file = os.sep + self.get_iface_cfg_fullpath(iface_id)
        if os.path.isfile(p_file):
            backupfile = p_file + "bak"
            try:
                shutil.copy(p_file, backupfile)
                self.delete_persist_file(os.sep + p_file)
                if IPV4_ID in params and IPV4INIT in params[IPV4_ID] \
                        and params[IPV4_ID][IPV4INIT] == CONST_NO:
                    route_filename = route_format % cfgmap[DEVICE]
                    route_filepath = '/' + network_configpath + route_filename
                    if (os.path.isfile(route_filepath)):
                        os.remove(route_filepath)
                self.write_attributes_to_cfg(
                    self.get_iface_identifier(cfgmap), cfgmap)
            except Exception, e:
                wok_log.error('Exception occured while updating the'
                              ' cfg information' + encode_value(e.message))
                if os.path.isfile(backupfile):
                    shutil.copy(backupfile, p_file)
                raise OperationFailed("GINNET0063E", {'err': e.message})
            finally:
                if os.path.isfile(backupfile):
                    os.remove(backupfile)
        else:
            self.write_attributes_to_cfg(self.get_iface_identifier(cfgmap),
                                         cfgmap)

    def delete_persist_file(self, ifcfg_file):
        wok_log.info('Deleting persist file ' + ifcfg_file)
        try:
            os.remove(ifcfg_file)
        except OSError, e:
            raise OperationFailed("GINNET0049E", {'error': e.message})

    def remove_vlan_persistent(self, name):
        p_file = self.get_iface_cfg_fullpath(name)
        self.delete_persist_file(os.sep + p_file)
        self.clean_routes(name, 4)
        self.clean_routes(name, 6)

    def remove_bond_persistent(self, interface_name):
        params = self.read_ifcfg_file(interface_name)
        if params:
            slave_list = self.get_slaves(params)
            for each_slave in slave_list:
                self.clean_slave_tokens(each_slave)
        p_file = self.get_iface_cfg_fullpath(interface_name)
        self.delete_persist_file(os.sep + p_file)
        self.clean_routes(interface_name, 4)
        self.clean_routes(interface_name, 6)

    def update_ipv4_bootproto(self, cfgmap, params):
        if BOOTPROTO in params[IPV4_ID]:
            if params[IPV4_ID][BOOTPROTO] in BOOTPROTO_OPTIONS:
                if params[IPV4_ID][BOOTPROTO] == DHCP:
                    # do dhcp stuff
                    cfgmap[BOOTPROTO] = DHCP
                    # Fix ginger issue #112
                    if DEFROUTE in params[IPV4_ID]:
                        cfgmap[DEFROUTE] = params[IPV4_ID][DEFROUTE]
                elif params[IPV4_ID][BOOTPROTO] == MANUAL:
                    # do manual stuff
                    cfgmap[BOOTPROTO] = MANUAL
                    if DEFROUTE in params[IPV4_ID]:
                        cfgmap[DEFROUTE] = params[IPV4_ID][DEFROUTE]
                    self.assign_ipv4_address(cfgmap, params[IPV4_ID])
                    # Fix ginger issue #111
                elif params[IPV4_ID][BOOTPROTO] == AUTOIP:
                    # do auto ip stuff
                    cfgmap[BOOTPROTO] = AUTOIP
            else:
                raise AttributeError('GINNET0022E',
                                     {'mode': params[BOOTPROTO]})
        else:
            raise MissingParameter('GINNET0023E')
        return cfgmap

    def update_dnsv4_info(self, cfgmap, params):
        cfgmap = self.clean_DNS_attributes(cfgmap)
        if DNSAddresses in params[IPV4_ID]:
            list_dns_addresses = params[IPV4_ID][DNSAddresses]
            if len(list_dns_addresses) == 1:
                cfgmap[DNS] = list_dns_addresses[0]
            else:
                index = 1
                for addr in list_dns_addresses:
                    cfgmap[DNS + str(index)] = addr
                    index += 1
        return cfgmap

    def update_ipv4(self, cfgmap, params):
        if IPV4INIT in params[IPV4_ID] and params[IPV4_ID][IPV4INIT] == \
                CONST_YES:
            cfgmap = self.cleanup_ipv4attributes(cfgmap)
            if IPV4_FAILURE_FATAL in params[IPV4_ID]:
                cfgmap[IPV4_FAILURE_FATAL] = \
                    params[IPV4_ID][IPV4_FAILURE_FATAL]
            if PEERDNS in params[IPV4_ID]:
                cfgmap[PEERDNS] = params[IPV4_ID][PEERDNS]
            if PEERROUTES in params[IPV4_ID]:
                cfgmap[PEERROUTES] = params[IPV4_ID][PEERROUTES]
            cfgmap = self.update_ipv4_bootproto(cfgmap, params)
            cfgmap = self.update_dnsv4_info(cfgmap, params)
            if ROUTES in params[IPV4_ID]:
                params[IPV4_ID][ROUTES] = \
                    self.validate_populate_ipv4_routes(params[IPV4_ID]
                                                       [ROUTES])
                self.write_cfgroutes(params[IPV4_ID][ROUTES],
                                     params[BASIC_INFO][DEVICE], 4)
            else:
                self.clean_routes(cfgmap[DEVICE], 4)
                # Fix ginger issue #109
        elif IPV4INIT in params[IPV4_ID] and params[IPV4_ID][IPV4INIT] == \
                CONST_NO:
            cfgmap = self.cleanup_ipv4attributes(cfgmap)
            wok_log.info("IPV4INIT value is set to no")
        else:
            raise MissingParameter('GINNET0026E')
        return cfgmap

    def validate_and_get_vlan_info(self, params, cfgmap):
        vlan_info = {}
        wok_log.info('Validating vlan info given for interface')
        if DEVICE not in cfgmap:
            raise MissingParameter("GINNET0025E")
        self.validate_device_name(cfgmap[DEVICE])
        device = cfgmap[DEVICE]
        if VLANINFO not in params[BASIC_INFO]:
            raise MissingParameter("GINNET0042E")
        if VLAN in params[BASIC_INFO][VLANINFO]:
            if not params[BASIC_INFO][VLANINFO][VLAN] == "yes":
                raise MissingParameter("GINNET0041E")
            else:
                vlan_info[VLAN] = params[BASIC_INFO][VLANINFO][VLAN]
        else:
            raise MissingParameter("GINNET0043E")
        vlan_info = self.validate_and_get_vlanid(params, vlan_info, device)
        if PHYSDEV not in params[BASIC_INFO][VLANINFO]:
            raise MissingParameter("GINNET0045E")
        else:
            vlan_info[PHYSDEV] = params[BASIC_INFO][VLANINFO][PHYSDEV]
        vlan_info[TYPE] = params[BASIC_INFO][TYPE]
        return vlan_info

    def get_cfgfile_content(self, interface):
        def get_interface_current_macaddress(interface):
            ip_link_cmd = ['ip', '-o', 'link', 'show', 'dev', interface]
            out, err, rc = run_command(ip_link_cmd)
            if out and rc == 0:
                out_tokens = out.strip().split()
                mac_index = 0
                for i in range(0, len(out_tokens)):
                    if out_tokens[i] == 'link/ether':
                        mac_index = i + 1
                        break
                if mac_index != 0:
                    return out_tokens[mac_index].strip()

            wok_log.error("Unable to get mac address of %s, error %s."
                          % (interface, err))
            return None

        mac_addr = get_interface_current_macaddress(interface)
        if not mac_addr:
            return None

        content = "DEVICE=%(dev)s\nHWADDR=%(mac)s\nONBOOT=yes\n" \
            "BOOTPROTO=none\n" % {'dev': interface, 'mac': mac_addr}

        return content

    def create_interface_cfg_file(self, interface):
        file_path = '/etc/sysconfig/network-scripts/ifcfg-%s' % interface
        if not os.path.isfile(file_path):
            file_content = self.get_cfgfile_content(interface)
            if not file_content:
                raise OperationFailed('GINNET0081E', {'name': interface})

            with open(file_path, 'w') as new_cfg_file:
                new_cfg_file.write(file_content)
