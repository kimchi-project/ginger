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


import ethtool
import os

from wok.exception import InvalidParameter, MissingParameter, OperationFailed
from wok.stringutils import decode_value, encode_value
from wok.utils import wok_log

from wok.plugins.gingerbase import netinfo

from interfaces import InterfaceModel
from nw_interfaces_utils import cfgInterfacesHelper

from nw_cfginterfaces_utils import network_configpath
from nw_cfginterfaces_utils import ifcfg_filename_format
from nw_cfginterfaces_utils import route_format
from nw_cfginterfaces_utils import route6_format
from nw_cfginterfaces_utils import BASIC_INFO
from nw_cfginterfaces_utils import NAME
from nw_cfginterfaces_utils import DEVICE
from nw_cfginterfaces_utils import ONBOOT
from nw_cfginterfaces_utils import TYPE
from nw_cfginterfaces_utils import MACADDR
from nw_cfginterfaces_utils import HWADDR
from nw_cfginterfaces_utils import UUID
from nw_cfginterfaces_utils import MTU
from nw_cfginterfaces_utils import ZONE
from nw_cfginterfaces_utils import SLAVE
from nw_cfginterfaces_utils import MASTER
from nw_cfginterfaces_utils import IFACE_BOND
from nw_cfginterfaces_utils import IFACE_VLAN
from nw_cfginterfaces_utils import VLAN
from nw_cfginterfaces_utils import FAIL_OVER_MAC
from nw_cfginterfaces_utils import BONDING_OPTS
from nw_cfginterfaces_utils import BONDING_MASTER
from nw_cfginterfaces_utils import BONDINFO
from nw_cfginterfaces_utils import SLAVES
from nw_cfginterfaces_utils import BONDING_OPTS_LIST
from nw_cfginterfaces_utils import STATE_DOWN
from nw_cfginterfaces_utils import IPV4_ID
from nw_cfginterfaces_utils import BOOTPROTO
from nw_cfginterfaces_utils import MANUAL
from nw_cfginterfaces_utils import STATIC
from nw_cfginterfaces_utils import DEFROUTE
from nw_cfginterfaces_utils import DNSAddresses
from nw_cfginterfaces_utils import PEERROUTES
from nw_cfginterfaces_utils import IPV4_FAILURE_FATAL
from nw_cfginterfaces_utils import PEERDNS
from nw_cfginterfaces_utils import NETMASK
from nw_cfginterfaces_utils import GATEWAY
from nw_cfginterfaces_utils import IPV4INIT
from nw_cfginterfaces_utils import IPV4Addresses
from nw_cfginterfaces_utils import ROUTES
from nw_cfginterfaces_utils import IPV6_ID
from nw_cfginterfaces_utils import IPV6INIT
from nw_cfginterfaces_utils import IPV6_AUTOCONF
from nw_cfginterfaces_utils import IPV6_DEFROUTE
from nw_cfginterfaces_utils import IPV6_PEERDNS
from nw_cfginterfaces_utils import IPV6_PEERROUTES
from nw_cfginterfaces_utils import IPV6_FAILURE_FATAL
from nw_cfginterfaces_utils import DHCPV6C
from nw_cfginterfaces_utils import IPV6_DEFAULTGW
from nw_cfginterfaces_utils import IPV6_PRIVACY
from nw_cfginterfaces_utils import IPV6Addresses
from nw_cfginterfaces_utils import metric
from nw_cfginterfaces_utils import ADDRESS
from nw_cfginterfaces_utils import METRIC
from nw_cfginterfaces_utils import VIA
from nw_cfginterfaces_utils import CONST_YES
from nw_cfginterfaces_utils import CONST_NO
from nw_cfginterfaces_utils import OPTIONS


class CfginterfacesModel(object):
    def get_list(self):
        nics = cfgInterfacesHelper.get_interface_list()
        # To handle issue https://github.com/kimchi-project/ginger/issues/99
        # cfginterface resource model deals with interface which has config
        # files.remove interface from interface list if ifcfg file not exist.
        nics_with_ifcfgfile = []
        for iface in nics:
            filename = ifcfg_filename_format % iface
            fileexist = os.path.isfile(os.sep + network_configpath + filename)
            if not fileexist:
                wok_log.warn('ifcfg file not exist for'
                             ' interface :' + iface)
            else:
                nics_with_ifcfgfile.append(iface)
        # Ensure comparison are done in same type.
        return sorted(map(decode_value, nics_with_ifcfgfile))
        # return get_interface_list()

    def create(self, params):
        if params[BASIC_INFO][TYPE] == IFACE_BOND \
                or params[BASIC_INFO][TYPE] == IFACE_VLAN:
            cfg_map = cfgInterfacesHelper.validate_minimal_info(params)
            if params[BASIC_INFO][TYPE] == IFACE_VLAN:
                cfgInterfacesHelper.validate_info_for_vlan(params)
                cfgInterfacesHelper.validate_vlan_driver()
            name = params[BASIC_INFO][DEVICE]
            params[BASIC_INFO][NAME] = name
            cfg_map = CfginterfaceModel().populate_ifcfg_atributes(params,
                                                                   cfg_map)
            # Check for any empty key value in cfg_map
            for key in cfg_map:
                if len(cfg_map[key]) == 0:
                    raise InvalidParameter("GINNET0073E", {'key': key})
            cfgInterfacesHelper.write_attributes_to_cfg(
                params[BASIC_INFO][DEVICE], cfg_map)
        else:
            raise InvalidParameter("GINNET0052E")
        return name

    def validate_bond_for_vlan(self, parent_iface):
        """
        method to validate in the case of VLANs over bonds, it is important
        that the bond has slaves and that they are up, and vlan can not be
        configured over bond with the fail_over_mac=follow option.
        :param parent_iface:
        """
        if encode_value(parent_iface) in ethtool.get_devices():
            try:
                with open(FAIL_OVER_MAC % parent_iface) as dev_file:
                    fail_over_mac = dev_file.readline().strip()
            except IOError:
                fail_over_mac = "n/a"
            if fail_over_mac == "follow 2":
                raise OperationFailed("GINNET0046E")
        else:
            """TODO: Need an investigation on, if parent of type bond is not
            active whether we can still create vlan interface or not. If
            'yes', then can include code to validate the fail_over_mac in
            ifcfg persistant file"""
            raise OperationFailed("GINNET0051E")
        cfgdata = CfginterfaceModel().get_cfginterface_info(parent_iface)
        cfgInterfacesHelper.validate_dict_bond_for_vlan(cfgdata)
        slave_list = cfgdata[BASIC_INFO][BONDINFO][SLAVES]
        if len(slave_list) != 0:
            active_slave_found = True
            for slave in slave_list:
                # Fix ginger issue #144
                if netinfo.operstate(slave) == STATE_DOWN:
                    active_slave_found = False
                else:
                    active_slave_found = True
                    wok_log.info("One active slave is found:" + slave)
                    break
            if (not active_slave_found):
                raise OperationFailed("GINNET0047E")
        else:
            raise OperationFailed("GINNET0037E")
        return

    @staticmethod
    def is_feature_available():
        return os.path.isdir(os.sep + network_configpath)


class CfginterfaceModel(object):
    def __init__(self):
        self._rollback_timer = None

    def lookup(self, name):
        # self.validate_interface(name)
        info = self.get_cfginterface_info(name)
        return info

    def delete(self, name):
        self.deactivate_if_itis_active(name)
        iface_type = cfgInterfacesHelper.get_type_from_cfg(name)
        if iface_type == IFACE_BOND:
            cfgInterfacesHelper.remove_bond_persistent(name)
        elif iface_type == IFACE_VLAN:
            cfgInterfacesHelper.remove_vlan_persistent(name)
        elif iface_type == "n/a":
            raise OperationFailed("GINNET0057E", {'name': name})
        else:
            raise OperationFailed("GINNET0055E", {'name': name})

    def deactivate_if_itis_active(self, name):
        type = netinfo.get_interface_type(name)
        allowed_active_types = [IFACE_BOND, IFACE_VLAN]
        if type in allowed_active_types:
            InterfaceModel().deactivate(name)

    def get_cfginterface_info(self, iface):
        ethinfo = {}
        cfgmap = cfgInterfacesHelper.read_ifcfg_file(iface)
        if cfgmap:
            ethinfo.update(self.get_interface_info(cfgmap))
        # When cfgmap is empty or ifcfg file doesn't exist
        else:
            raise OperationFailed("GINNET0080E", {'name': iface})
        return ethinfo

    def get_interface_info(self, cfgmap):
        info = {}
        info.update(self.get_basic_info(cfgmap))
        info.update(self.get_ipv4_info(info, cfgmap))
        info.update(self.get_ipv6_info(info, cfgmap))
        return info

    def get_basic_info(self, cfgmap):
        wok_log.debug('Begin get_basic_info')
        info = {}
        info[BASIC_INFO] = {}
        basic_info_keys = [NAME, DEVICE, ONBOOT, MACADDR,
                           HWADDR, UUID, MTU, ZONE, TYPE]
        for key in basic_info_keys:
            if key in cfgmap:
                info[BASIC_INFO][key] = cfgmap[key]

        if SLAVE in cfgmap and CONST_YES == cfgmap[SLAVE]:
            info[BASIC_INFO][SLAVE] = cfgmap[SLAVE]
            info[BASIC_INFO][MASTER] = cfgInterfacesHelper.get_master(cfgmap)
        interface_type = None
        if TYPE in cfgmap:
            interface_type = cfgmap[TYPE]
        elif VLAN in cfgmap and CONST_YES == cfgmap[VLAN]:
            interface_type = IFACE_VLAN
            # Fix ginger issue #131
        cfgInterfacesHelper.get_architecture_specific_info(info, cfgmap)
        if interface_type is not None:
            info[BASIC_INFO][TYPE] = interface_type
            if interface_type == IFACE_VLAN:
                cfgInterfacesHelper.get_vlan_info(info, cfgmap)
            elif interface_type == IFACE_BOND:
                cfgInterfacesHelper.get_bond_info(info, cfgmap)
        wok_log.debug('end get_basic_info')
        if MTU not in cfgmap:
            info[BASIC_INFO][MTU] = "1500"
        return info

    def get_ipv4_info(self, info, cfgmap):
        wok_log.debug('Begin get_ipv4_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            info[IPV4_ID] = {}
            ipv4_info_keys = [BOOTPROTO, DEFROUTE, PEERROUTES, PEERDNS,
                              IPV4_FAILURE_FATAL]
            for key in ipv4_info_keys:
                if key in cfgmap:
                    info[IPV4_ID][key] = cfgmap[key]
            if BOOTPROTO in cfgmap and (info[IPV4_ID][BOOTPROTO] == MANUAL or
                                        info[IPV4_ID][BOOTPROTO] == STATIC):
                info[IPV4_ID][IPV4Addresses] = \
                    cfgInterfacesHelper.get_ipv4_addresses(cfgmap)
            dnsaddresses = cfgInterfacesHelper.get_dnsv4_info(cfgmap)
            if len(dnsaddresses) > 0:
                info[IPV4_ID][DNSAddresses] = dnsaddresses
            # construct routeinfo.
            if DEVICE in cfgmap:
                routes = self.get_routes_map(cfgmap[DEVICE], 4)
            elif NAME in cfgmap:
                routes = self.get_routes_map(cfgmap[NAME], 4)
            if len(routes) > 0:
                info[IPV4_ID][ROUTES] = routes
            # Fix ginger issue #110
            if len(info[IPV4_ID]) > 0:
                info[IPV4_ID][IPV4INIT] = CONST_YES
            else:
                info[IPV4_ID][IPV4INIT] = CONST_NO
        wok_log.debug('End get_ipv4_info')
        return info

    def get_ipv6_info(self, info, cfgmap):
        wok_log.debug('Begin get_ipv6_info')
        if info.__len__() != 0 and cfgmap.__len__() != 0:
            info[IPV6_ID] = {}
            ipv6_info_keys = [IPV6INIT, IPV6_AUTOCONF, IPV6_DEFROUTE,
                              IPV6_PEERDNS, IPV6_PEERROUTES,
                              IPV6_FAILURE_FATAL, DHCPV6C,
                              IPV6_DEFAULTGW, IPV6_PRIVACY]
            for key in ipv6_info_keys:
                if key in cfgmap:
                    info[IPV6_ID][key] = cfgmap[key]
            ipv6_addresses = cfgInterfacesHelper.get_ipv6_address(cfgmap)
            if len(ipv6_addresses):
                info[IPV6_ID][IPV6Addresses] = ipv6_addresses
        dnsaddresses = cfgInterfacesHelper.get_dnsv6_info(cfgmap)
        if len(dnsaddresses) > 0:
            info[IPV6_ID][DNSAddresses] = dnsaddresses
        # construct routeinfo.
        if DEVICE in cfgmap:
            routes = self.get_routes_map(cfgmap[DEVICE], 6)
        elif NAME in cfgmap:
            routes = self.get_routes_map(cfgmap[NAME], 6)
        if len(routes) > 0:
            info[IPV6_ID][ROUTES] = routes
        wok_log.debug('End get_ipv6_info')
        return info

    def update_basic_info(self, cfgmap, params):
        if DEVICE in params[BASIC_INFO]:
            cfgmap[DEVICE] = params[BASIC_INFO][DEVICE]
        if NAME in params[BASIC_INFO]:
            cfgmap[NAME] = params[BASIC_INFO][NAME]
        if ONBOOT in params[BASIC_INFO]:
            cfgmap[ONBOOT] = params[BASIC_INFO][ONBOOT]
        if MACADDR in params[BASIC_INFO] and params[BASIC_INFO][MACADDR] != '':
            macaddress = params[BASIC_INFO][MACADDR]
            cfgInterfacesHelper.validate_macaddress(macaddress)
            cfgmap[MACADDR] = macaddress
        if MTU in params[BASIC_INFO]:
            cfgmap[MTU] = params[BASIC_INFO][MTU]
        if ZONE in params[BASIC_INFO]:
            cfgmap[ZONE] = params[BASIC_INFO][ZONE]
        if TYPE in params[BASIC_INFO] \
                and params[BASIC_INFO][TYPE] == IFACE_BOND:
            cfgmap.update(self.validate_and_get_bond_info(params, cfgmap))
        if TYPE in params[BASIC_INFO] \
                and params[BASIC_INFO][TYPE] == IFACE_VLAN:
            cfgmap.update(cfgInterfacesHelper.validate_and_get_vlan_info
                          (params, cfgmap))
        if OPTIONS in params[BASIC_INFO]:
            if params[BASIC_INFO][OPTIONS] != {}:
                options_dict = ' '.join('%s=%s' % (k, v)
                                        for k, v in params
                                        [BASIC_INFO][OPTIONS].items())
                cfgmap[OPTIONS] = "'" + options_dict + "'"
            else:
                if OPTIONS in cfgmap:
                    del cfgmap[OPTIONS]
        return cfgmap

    def update(self, name, params):
        cfgmap = cfgInterfacesHelper.read_ifcfg_file(name)
        cfgmap = self.populate_ifcfg_atributes(params, cfgmap)
        cfgInterfacesHelper.update_cfgfile(cfgmap, params)

    def populate_ifcfg_atributes(self, params, cfg_map):
        if BASIC_INFO in params:
            cfg_map = self.update_basic_info(cfg_map, params)
        else:
            raise MissingParameter('GINNET0024E')
        if IPV4_ID in params:
            cfg_map = cfgInterfacesHelper.update_ipv4(cfg_map, params)
        if IPV6_ID in params:
            cfg_map = cfgInterfacesHelper.update_ipv6(cfg_map, params)
        return cfg_map

    def validate_and_get_bond_info(self, params, cfgmap):
        if cfgmap[TYPE] == IFACE_BOND:
            cfgInterfacesHelper.clean_slaves(cfgmap, params)
        bond_info = {}
        wok_log.info('Validating bond info given for interface')
        if DEVICE not in cfgmap:
            raise MissingParameter("GINNET0025E")
        cfgInterfacesHelper.validate_device_name(cfgmap[DEVICE])
        if BONDINFO not in params[BASIC_INFO]:
            raise MissingParameter("GINNET0032E")
        bondinfo = params[BASIC_INFO][BONDINFO]
        if BONDING_MASTER in bondinfo:
            if not bondinfo[BONDING_MASTER] == "yes":
                raise MissingParameter("GINNET0033E")
            else:
                bond_info[BONDING_MASTER] = bondinfo[BONDING_MASTER]
        else:
            raise MissingParameter("GINNET0034E")

        if BONDING_OPTS in params[BASIC_INFO][BONDINFO]:
            bond_opt_value = ""
            bondopts = bondinfo[BONDING_OPTS]
            if cfgInterfacesHelper.validate_bond_opts(bondopts, params):
                for bond_opt_key in BONDING_OPTS_LIST:
                    if bond_opt_key in bondinfo[BONDING_OPTS]:
                        value = bondinfo[BONDING_OPTS][bond_opt_key]
                        if type(value) is not list:
                            bond_opt_value = \
                                bond_opt_value + bond_opt_key + "=" + \
                                encode_value(bondinfo[BONDING_OPTS][
                                    bond_opt_key]) + " "
                        else:
                            values_as_str = map(encode_value, value)
                            values_as_str = encode_value(values_as_str)
                            v = values_as_str.replace(" ", "")
                            bond_opt_value = \
                                bond_opt_value + bond_opt_key + "=" + v + " "
                bond_opt_value = '"' + bond_opt_value + '"'
                bond_info[BONDING_OPTS] = bond_opt_value
        if SLAVES not in bondinfo:
            raise MissingParameter("GINNET0036E")
        if len(bondinfo[SLAVES]) == 0:
            raise MissingParameter("GINNET0037E")
        name = cfgmap[DEVICE]
        self.create_slaves(name, params)
        bond_info[TYPE] = params[BASIC_INFO][TYPE]
        return bond_info

    def create_slaves(self, name, params):
        for slave in params[BASIC_INFO][BONDINFO][SLAVES]:
            slave_info = {SLAVE: "yes", MASTER: name}
            filename = ifcfg_filename_format % slave
            ifcfgFile = os.sep + network_configpath + filename
            fileexist = os.path.isfile(ifcfgFile)
            if fileexist:
                cfgInterfacesHelper.write_attributes_to_cfg(slave, slave_info)
            else:
                raise OperationFailed("GINNET0053E", {'slave': slave})

    # TODO this code can be later made to have strict regex to get the right
    # info(optimize)
    def get_routes_ipformat(self, routecfg_path):
        """
        Constructs a list of route map with key,value information
        for the below format of routes.
        :param: route file which has information in ip format
        :return: list of dictionaries of the key,value information
                 of the routes.
        Ex:
        10.10.10.0/24 via 192.168.0.10 dev eth0
        172.16.1.10/32 via 192.168.0.10 dev eth0
        """
        with open(routecfg_path, "r") as routecfg_file:
            line = routecfg_file.read()
            cfg_map = []
            try:
                each_route = [x for x in (y.split() for y in line.split('\n'))
                              if x]
                for options in each_route:
                    if len(options) >= 3:
                        route_info = {'ADDRESS': options[0].split('/')[0],
                                      'NETMASK': options[0].split('/')[1],
                                      'GATEWAY': options[2]}
                        if metric in options and options[3] == metric:
                            route_info['METRIC'] = options[4]
                        elif metric in options and options[5] == metric:
                            route_info['METRIC'] = options[6]
                        cfg_map.append(route_info)
                    else:
                        wok_log.warn("Skipping the invalid route information" +
                                     encode_value(options))
            except Exception, e:
                raise OperationFailed("GINNET0030E", {'err': e.message})
            return cfg_map

    def get_routes_directiveformat(self, routecfg_path):
        """
        This method reads from routes file and contructs key,value information.
        for the below format.
        :param :route file path which has info in network directives format
        :return: dictionary consisting of route information read from file
        Ex:
        ADDRESS0=10.10.10.13
        NETMASK0=255.255.255.254
        GATEWAY0=10.10.10.15
        METRIC0=1
        """
        with open(routecfg_path, "r") as routecfg_file:
            line = routecfg_file.read()
            cfgroutes_info = {}
            route_input = line.split()
            for elem in route_input:
                try:
                    cfgroutes_info[elem.split('=')[0]] = elem.split('=')[1]
                except Exception, e:
                    raise OperationFailed("GINNET0030E", {'err': e.message})
        route_list = []
        i = 0
        # construct list of dictionaries from the given key=value list.
        while True:
            route_map_dict = {}
            if ADDRESS + str(i) in cfgroutes_info \
                    and NETMASK + str(i) in cfgroutes_info \
                    and GATEWAY + str(i) in cfgroutes_info:
                route_map_dict.update(ADDRESS=cfgroutes_info[ADDRESS + str(i)])
                route_map_dict.update(NETMASK=cfgroutes_info[NETMASK + str(i)])
                route_map_dict.update(GATEWAY=cfgroutes_info[GATEWAY + str(i)])
            else:
                break
            if METRIC + str(i) in cfgroutes_info:
                route_map_dict.update(METRIC=cfgroutes_info[METRIC + str(i)])
            route_list.append(route_map_dict)
            i += 1
        return route_list

    def get_routes_map(self, interface_name, ipversion=4):
        """
        Reads the route information for interface and based on the format of
        the route info key,value inforamation is returned
        :param ipversion:
        :param interface_name: interface name for which routes info is needed
               ipversion :
        :return: list of dictionaries consisting route information
        """
        route_filename = 4
        if ipversion == 4:
            route_filename = route_format % interface_name
        elif ipversion == 6:
            route_filename = route6_format % interface_name
        route_filepath = '/' + network_configpath + route_filename
        fileexist = os.path.isfile(route_filepath)
        if fileexist:
            with open(route_filepath, "r") as route_file:
                line = route_file.read()
                if VIA in line:
                    cfgroutes_list = self.get_routes_ipformat(route_filepath)
                else:
                    cfgroutes_list = self.get_routes_directiveformat(
                        route_filepath)
            return cfgroutes_list
        else:
            return []
