#
# Project Ginger
#
# Copyright IBM, Corp. 2015
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

from netaddr import IPAddress
from wok.exception import InvalidParameter, MissingParameter, OperationFailed
from wok.utils import wok_log

parser = augeas.Augeas("/")


@atexit.register
def augeas_cleanup():
    global parser
    del parser


network_configpath = 'etc/sysconfig/network-scripts/'
ifcfg_filename_format = 'ifcfg-%s'
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
# z parameters
SUBCHANNELS = 'SUBCHANNELS'
NETTYPE = 'NETTYPE'
PORTNAME = 'PORTNAME'
OPTIONS = 'OPTIONS'
SLAVE = 'SLAVE'
MASTER = 'MASTER'
# interface types
IFACE_ETHERNET = 'Ethernet'
IFACE_BOND = 'Bond'
IFACE_VLAN = 'Vlan'

# Architecture type
ARCH_S390 = 's390x'

# Vlan parameters
REORDER_HDR = 'REORDER_HDR'
VLAN = 'VLAN'
VLANID = 'VLAN_ID'
PHYSDEV = 'PHYSDEV'

# Bond parameters
BONDING_OPTS = 'BONDING_OPTS'
BONDING_MASTER = 'BONDING_MASTER'
SLAVES = 'SLAVES'

# ipv4 parameters
IPV4_ID = "IPV4_INFO"
BOOTPROTO = 'BOOTPROTO'

DHCP = 'dhcp'
AUTOIP = 'autoip'
MANUAL = 'none'
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
IPV6_DEFAULTGW = 'IPV6_DEFAULTGW'
IPV6_PRIVACY = 'IPV6_PRIVACY'


# other constants
CONST_YES = 'yes'
CONST_NO = 'no'


class CfginterfacesModel(object):
    def get_list(self):
        nics = ethtool.get_devices()
        return sorted(nics)


class CfginterfaceModel(object):
    def __init__(self):
        self._rollback_timer = None

    def lookup(self, name):
        # self.validate_interface(name)
        info = self.get_cfginterface_info(name)
        return info

    def validate_interface(self, name):
        if name not in ethtool.get_devices():
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
            parser.load()
            listout = parser.match(ifcfg_file_pattern)
            if not listout:
                wok_log.info('No attributes present in ifcfg file for '
                             'interface :' + interface_name)
                return cfgmap
            for single in listout:
                cfgmap[parser.label(single)] = parser.get(single)
        except Exception, e:
            # typical error message e='Error during match procedure!',
            # u'etc/sysconfig/network-scripts/ifcfg-virbr0
            wok_log.error('Augeas parser throw run time exception', e)
            raise OperationFailed('GINNET0015E', {'error': e})
        wok_log.info('reading finished. Key value :' + str(cfgmap))
        return cfgmap

    def getValue(self, file, token):
        if self.token_exist(file, "/" + str(token)):
            return str(parser.get(file + "/" + str(token)))

    def token_exist(self, ifcfg_file, token):
        l = parser.match(ifcfg_file + token)
        if len(l) == 1:
            return True

    def get_cfginterface_info(self, iface):
        ethinfo = {}
        cfgmap = self.read_ifcfg_file(iface)
        if cfgmap:
            ethinfo.update(self.get_interface_info(cfgmap))
        return ethinfo

    def get_interface_info(self, cfgmap):
        info = {}
        info.update(self.get_basic_info(cfgmap))
        info.update(self.get_ipv4_info(info, cfgmap))
        info.update(self.get_ipv6_info(info, cfgmap))
        info.update(self.get_dnsv6_info(info, cfgmap))
        return info

    def get_basic_info(self, cfgmap):
        wok_log.debug('Begin get_basic_info')
        info = {}
        info[BASIC_INFO] = {}
        basic_info_keys = [NAME, DEVICE, ONBOOT, MACADDR,
                           HWADDR, UUID, MTU, ZONE]
        for key in basic_info_keys:
            if key in cfgmap:
                info[BASIC_INFO][key] = cfgmap[key]

        if SLAVE in cfgmap and CONST_YES == cfgmap[SLAVE]:
            info[BASIC_INFO][SLAVE] = cfgmap[SLAVE]
            info[BASIC_INFO][MASTER] = self.get_master(cfgmap)
        interface_type = None
        if TYPE in cfgmap:
            interface_type = cfgmap[TYPE]
        elif VLAN in cfgmap and CONST_YES == cfgmap[VLAN]:
            interface_type = IFACE_VLAN
        if interface_type is not None:
            info[BASIC_INFO][TYPE] = interface_type
            if interface_type == IFACE_ETHERNET:
                self.get_architecture_specific_info(info, cfgmap)
            elif interface_type == IFACE_VLAN:
                self.get_vlan_info(info, cfgmap)
            elif interface_type == IFACE_BOND:
                self.get_bond_info(info, cfgmap)
        wok_log.debug('end get_basic_info')
        return info

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
            if PREFIX + postfix in cfgmap:
                dict.update(PREFIX=cfgmap[PREFIX + postfix])
            if GATEWAY + postfix in cfgmap:
                dict.update(GATEWAY=cfgmap[GATEWAY + postfix])
            index += 1
            ipv4addresses.append(dict)
        return ipv4addresses

    def get_ipv4_info(self, info, cfgmap):
        wok_log.debug('Begin get_ipv4_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            info[IPV4_ID] = {}
            ipv4_info_keys = [BOOTPROTO, DEFROUTE, PEERROUTES, PEERDNS,
                              IPV4_FAILURE_FATAL]
            for key in ipv4_info_keys:
                if key in cfgmap:
                    info[IPV4_ID][key] = cfgmap[key]
            if BOOTPROTO in cfgmap and info[IPV4_ID][BOOTPROTO] == MANUAL:
                info[IPV4_ID][IPV4Addresses] = self.get_ipv4_addresses(cfgmap)
            dnsaddresses = self.get_dnsv4_info(cfgmap)
            if len(dnsaddresses) > 0:
                info[IPV4_ID][DNSAddresses] = self.get_dnsv4_info(cfgmap)
        wok_log.debug('End get_ipv4_info')
        return info

    # TODO Multiple ipv6 to be supported later.
    def get_ipv6_info(self, info, cfgmap):
        wok_log.debug('Begin get_ipv6_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            info[IPV6_ID] = {}
            ipv6_info_keys = [IPV6INIT, IPV6_AUTOCONF, IPV6_DEFROUTE,
                              IPV6_PEERDNS, IPV6_PEERROUTES,
                              IPV6_FAILURE_FATAL, DHCPV6C, IPV6ADDR,
                              IPV6_DEFAULTGW, IPV6_PRIVACY]
            for key in ipv6_info_keys:
                if key in cfgmap:
                    info[IPV6_ID][key] = cfgmap[key]
        wok_log.debug('End get_ipv6_info')
        return info

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

    def get_dnsv6_info(self, info, cfgmap):
        wok_log.debug('Begin get_dns_info')
        if DNS in cfgmap:
            ip = IPAddress(cfgmap[DNS])
            if ip.version == 6:
                info[IPV6_ID][DNS] = cfgmap[DNS]
        else:
            flag = 0
            dnscount = 1
            dnsincrmnt = DNS + str(dnscount)
            while flag == 0:
                if dnsincrmnt in cfgmap:
                    ip = IPAddress(cfgmap[dnsincrmnt])
                    if ip.version == 6:
                        info[IPV6_ID][dnsincrmnt] = cfgmap[dnsincrmnt]
                    dnscount = dnscount + 1
                    dnsincrmnt = DNS + str(dnscount)
                else:
                    flag = 1
        wok_log.debug('End get_dns_info')
        return info

    def get_architecture_specific_info(self, info, cfgmap):
        wok_log.debug('Begin get_architecture_specific_info')
        if platform.machine() == ARCH_S390:
            basic_info_keys = [SUBCHANNELS, NETTYPE, PORTNAME, OPTIONS]
            for key in basic_info_keys:
                if key in cfgmap:
                    info[BASIC_INFO][key] = cfgmap[key]
        wok_log.debug('End get_architecture_specific_info')
        return info

    def get_vlan_info(self, info, cfgmap):
        wok_log.debug('Begin get_vlan_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            basic_info_keys = [VLANID, VLAN, REORDER_HDR, PHYSDEV]
            for key in basic_info_keys:
                if key in cfgmap:
                    info[BASIC_INFO][key] = cfgmap[key]
        wok_log.debug('End get_vlan_info')
        return info

    def get_bond_info(self, info, cfgmap):
        wok_log.debug('Begin get_bond_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            basic_info_keys = [BONDING_OPTS, BONDING_MASTER]
            for key in basic_info_keys:
                if key in cfgmap:
                    info[BASIC_INFO][key] = cfgmap[key]
            info[BASIC_INFO][SLAVES] = self.get_slaves(cfgmap)
        wok_log.debug('End get_bond_info')
        return info

    def get_master(self, cfgmap):
        if MASTER in cfgmap:
            master_bond = cfgmap[MASTER]
            pattern = network_configpath + '*/DEVICE'
            parser.load()
            listout = parser.match(pattern)
            master_found = False
            for device in listout:
                if master_bond == parser.get(device):
                    master_found = True
                    master_bond = parser.get(device)
                    return master_bond
            if not master_found:
                wok_log.info('No master found for slave:')
                return ''
                # TODO write logic to get master bond in case MASTER
                #  = UUID//NMsupport

    def get_slaves(self, cfgmap):
        master_device = cfgmap[DEVICE]
        pattern = network_configpath + '*/MASTER'
        parser.load()
        listout = parser.match(pattern)
        slave_found = False
        slaves = []
        for a_slave in listout:
            if master_device == parser.get(a_slave):
                slave_found = True
                slave_cfg_file = a_slave.rsplit('/', 1)[0]
                slave_name = parser.get(slave_cfg_file + '/DEVICE')
                slaves.append(slave_name)
        if not slave_found:
            wok_log.info('No slaves found for master:' + master_device)
        return slaves

    def validate_ipv4_address(self, ip):
        try:
            ip = IPAddress(ip)
            if ip.version == 4:
                return
            raise Exception("Not an ipv4 address")
        except Exception, e:
            wok_log.error(("Invalid ipv4 address:" + str(e)))
            raise InvalidParameter('GINNET0018E', {'ip': ip, 'error': e})

    def get_ipv4_prefix(selfself, ip):
        try:
            ip = IPAddress(ip)
            return ip.netmask_bits()
        except Exception, e:
            wok_log.error(("Invalid netmask:" + str(e)))
            raise InvalidParameter('GINNET0019E', {'NETMASK': ip, 'error': e})

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
                    wok_log.error(("No ip address provided"))
                    raise MissingParameter('GINNET0020E')
                if NETMASK in ipaddrinfo:
                    self.validate_ipv4_address(ipaddrinfo[NETMASK])
                    cfgmap[PREFIX + postfix] = self.get_ipv4_prefix(
                        ipaddrinfo[NETMASK])
                elif PREFIX in ipaddrinfo:
                    cfgmap[PREFIX + postfix] = ipaddrinfo[PREFIX]
                else:
                    wok_log.error(("No netmask or prefix provided"))
                    raise MissingParameter('GINNET0021E')
                if GATEWAY in ipaddrinfo:
                    self.validate_ipv4_address(ipaddrinfo[GATEWAY])
                    cfgmap[GATEWAY + postfix] = ipaddrinfo[GATEWAY]
                index += 1
        return cfgmap

    def update_basic_info(self, cfgmap, params):
        if DEVICE in params[BASIC_INFO]:
            cfgmap[DEVICE] = params[BASIC_INFO][DEVICE]
        else:
            wok_log.error(("DEVICE value is mandatory"))
            raise MissingParameter('GINNET0025E')
        if NAME in params[BASIC_INFO]:
            cfgmap[NAME] = params[BASIC_INFO][NAME]
        if ONBOOT in params[BASIC_INFO]:
            cfgmap[ONBOOT] = params[BASIC_INFO][ONBOOT]
        if MTU in params[BASIC_INFO]:
            cfgmap[MTU] = params[BASIC_INFO][MTU]
        if ZONE in params[BASIC_INFO]:
            cfgmap[ZONE] = params[BASIC_INFO][ZONE]
        return cfgmap

    def update_ipv4_bootproto(self, cfgmap, params):
        if BOOTPROTO in params[IPV4_ID]:
            if params[IPV4_ID][BOOTPROTO] in BOOTPROTO_OPTIONS:
                if params[IPV4_ID][BOOTPROTO] == DHCP:
                    # do dhcp stuff
                    cfgmap[BOOTPROTO] = DHCP
                    if DEFROUTE in params[IPV4_ID][DEFROUTE]:
                        cfgmap[DEFROUTE] = params[IPV4_ID][DEFROUTE]
                elif params[IPV4_ID][BOOTPROTO] == MANUAL:
                    # do manual stuff
                    cfgmap[BOOTPROTO] = MANUAL
                    if DEFROUTE in params[IPV4_ID]:
                        cfgmap[DEFROUTE] = params[IPV4_ID][DEFROUTE]
                    self.assign_ipv4_address(cfgmap, params[IPV4_ID])
                elif params[BOOTPROTO] == AUTOIP:
                    # do auto ip stuff
                    cfgmap[BOOTPROTO] = AUTOIP
            else:
                wok_log.error(("Bootprotocol not supported:" +
                               params[BOOTPROTO]))
                raise AttributeError('GINNET0022E',
                                     {'mode': params[BOOTPROTO]})
        else:
            wok_log.error(("Bootprotocol not provided:"))
            raise MissingParameter('GINNET0023E')
        return cfgmap

    def update_dnsv4_info(self, cfgmap, params):
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
                'yes':
            if IPV4_FAILURE_FATAL in params[IPV4_ID]:
                cfgmap[IPV4_FAILURE_FATAL] = \
                    params[IPV4_ID][IPV4_FAILURE_FATAL]
            if PEERDNS in params[IPV4_ID]:
                cfgmap[PEERDNS] = params[IPV4_ID][PEERDNS]
            if PEERROUTES in params[IPV4_ID]:
                cfgmap[PEERROUTES] = params[IPV4_ID][PEERROUTES]
            cfgmap = self.update_ipv4_bootproto(cfgmap, params)
            cfgmap = self.update_dnsv4_info(cfgmap, params)
        else:
            wok_log.error(("IPV4INIT value is mandatory"))
            raise MissingParameter('GINNET0026E')
        return cfgmap

    def update(self, name, params):
        cfgmap = self.read_ifcfg_file(name)
        if BASIC_INFO in params:
            cfgmap = self.update_basic_info(cfgmap, params)
        else:
            wok_log.error(("BASIC_INFO is mandatory"))
            raise MissingParameter('GINNET0024E')
        if IPV4_ID in params:
            cfgmap = self.update_ipv4(cfgmap, params)
        self.write(name, cfgmap)

    def write(self, interface_name, cfgmap):
        filename = ifcfg_filename_format % interface_name
        ifcfgFile = os.sep + network_configpath + filename
        fileexist = os.path.isfile(ifcfgFile)
        if not fileexist:
            open(ifcfgFile, "w").close()
            os.system('chmod 644 ' + ifcfgFile)
        parser.load()
        ifcfg_file_pattern = network_configpath + filename + '/'
        for key, value in cfgmap.iteritems():
            path = ifcfg_file_pattern + key
            parser.set(path, str(value))
        parser.save()
