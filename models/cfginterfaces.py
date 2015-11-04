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
from wok.exception import InvalidParameter, OperationFailed
from wok.utils import wok_log

parser = augeas.Augeas("/")


@atexit.register
def augeas_cleanup():
    global parser
    del parser


IFCFGPATH = 'etc/sysconfig/network-scripts/'
filenameformat = 'ifcfg-<iname>'
# cfgfile keys
BASIC_INFO = "BASIC_INFO"
NAME = 'NAME'
DEVICE = 'DEVICE'
ONBOOT = 'ONBOOT'
TYPE = 'TYPE'
MACADDR = 'MACADDR'
HWADDR = 'HWADDR'
UUID = 'UUID'
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
BOOTPROTO_DHCP = 'dhcp'
DEFROUTE = 'DEFROUTE'
DNS = 'DNS'
PEERROUTES = 'PEERROUTES'
IPV4_FAILURE_FATAL = 'IPV4_FAILURE_FATAL'
PEERDNS = 'PEERDNS'
IPADDR = 'IPADDR'
NETMASK = 'NETMASK'
PREFIX = 'PREFIX'
GATEWAY = 'GATEWAY'

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
        self.validate_interface(name)
        info = self.get_cfginterface_info(name)
        return info

    def validate_interface(self, name):
        if name not in ethtool.get_devices():
            raise InvalidParameter('GINNET0014E', {'name': name})

    def read_ifcfg_file(self, interface_name):
        cfgmap = {}
        wok_log.info('Reading ifcfg file for interface ' + interface_name)
        filename = filenameformat.replace('<iname>', interface_name)
        # TODO file pattern to be changed to parse the device name inside
        # files rather than filename
        ifcfg_file_pattern = IFCFGPATH + filename + '/*'
        fileexist = os.path.isfile(os.sep + IFCFGPATH + filename)
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
        info.update(self.get_dns_info(info, cfgmap))
        return info

    def get_basic_info(self, cfgmap):
        wok_log.debug('Begin get_basic_info')
        info = {}
        info[BASIC_INFO] = {}
        basic_info_keys = [NAME, DEVICE, ONBOOT, MACADDR, HWADDR, UUID]
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

    # TODO Multiple ipv4 to be supported later.
    def get_ipv4_info(self, info, cfgmap):
        wok_log.debug('Begin get_ipv4_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            info[IPV4_ID] = {}
            ipv4_info_keys = [BOOTPROTO, DEFROUTE, PEERROUTES, PEERDNS,
                              IPV4_FAILURE_FATAL, IPADDR, NETMASK, GATEWAY,
                              PREFIX]
            for key in ipv4_info_keys:
                if key in cfgmap:
                    info[IPV4_ID][key] = cfgmap[key]
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

    def get_dns_info(self, info, cfgmap):
        wok_log.debug('Begin get_dns_info')
        if DNS in cfgmap:
            ip = IPAddress(cfgmap[DNS])
            if ip.version == 4:
                info[IPV4_ID][DNS] = cfgmap[DNS]
            elif ip.version == 6:
                info[IPV6_ID][DNS] = cfgmap[DNS]
        else:
            flag = 0
            dnscount = 1
            dnsincrmnt = DNS + str(dnscount)
            while flag == 0:
                if dnsincrmnt in cfgmap:
                    ip = IPAddress(cfgmap[dnsincrmnt])
                    if ip.version == 4:
                        info[IPV4_ID][dnsincrmnt] = cfgmap[dnsincrmnt]
                    elif ip.version == 6:
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
            pattern = IFCFGPATH + '*/DEVICE'
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
        pattern = IFCFGPATH + '*/MASTER'
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
