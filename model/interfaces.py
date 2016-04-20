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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301 USA


import ethtool
import ipaddr
import libvirt
import lxml.etree as ET
import os

from lxml.builder import E
from threading import Timer

import netinfo

from nw_interfaces_utils import cfgInterfacesHelper
from nw_interfaces_utils import InterfacesHelper
from wok.exception import InvalidParameter, NotFoundError, OperationFailed
from wok.xmlutils.utils import xpath_get_text

from nw_cfginterfaces_utils import IFACE_BOND
from nw_cfginterfaces_utils import IFACE_VLAN


class InterfacesModel(object):
    def get_list(self):
        """
        Return the active interfaces returned by ethtool.getdevices
        and interfaces that are inactive and are of type of bond and vlan.
        :return:
        """
        return cfgInterfacesHelper.get_interface_list()


class InterfaceModel(object):
    _confirm_timout = 10.0  # Second
    _conn = libvirt.open("qemu:///system")

    def __init__(self):
        self._rollback_timer = None
        self.actions_mod = self.get_actions_per_module()

    def lookup(self, name):
        """
        Populate info using runtime information from /sys/class/net files for
        active interfaces and for inactive bond and vlan interfaces from cfg
        files
        :param name:
        :return:
        """

        def get_actions_info_without_method(kernel_mod):
            info = self.actions_mod.get(kernel_mod, {})
            for action in info.keys():
                action_info = info[action]

                # not all interface has method
                if 'method' in action_info.keys():
                    action_info.pop('method')
                info[action] = action_info
            return info

        try:
            if name in ethtool.get_devices():
                info = netinfo.get_interface_info(name)
            elif cfgInterfacesHelper.is_cfgfileexist(name):
                type = cfgInterfacesHelper.get_type(name).lower()
                if type in [IFACE_BOND, IFACE_VLAN]:
                    raise ValueError
                device = cfgInterfacesHelper.get_device(name)
                info = {'device': device,
                        'type': cfgInterfacesHelper.get_type(name),
                        'status': "down",
                        'ipaddr': "",
                        'netmask': "",
                        'macaddr': "",
                        'module': netinfo.get_interface_kernel_module(name)}
            else:
                raise ValueError('unknown interface: %s' % name)

            info['actions'] = get_actions_info_without_method(info['module'])
            return info

        except ValueError:
            raise NotFoundError("GINNET0014E", {'name': name})

    def _is_interface_editable(self, iface):
        return iface in self._get_all_libvirt_interfaces()

    def _get_all_libvirt_interfaces(self):
        conn = self._conn
        return [iface.name() for iface in conn.listAllInterfaces()]

    def _get_interface_info(self, name):
        try:
            info = netinfo.get_interface_info(name)
        except ValueError:
            raise NotFoundError("GINNET0014E", {'name': name})
        if not info['ipaddr']:
            info['ipaddr'], info['netmask'] = \
                self._get_static_config_interface_address(name)
        return info

    def _get_static_config_interface_address(self, name):
        def _get_ipaddr_info(libvirt_interface_xml):
            search_ip = \
                xpath_get_text(libvirt_interface_xml,
                               "/interface/protocol[@family='ipv4']"
                               "/ip/@address")

            if not len(search_ip):
                return '', ''

            search_prefix = \
                xpath_get_text(libvirt_interface_xml,
                               "/interfac/protocol[@family='ipv4']"
                               "/ip/@prefix")

            ip_obj = ipaddr.IPv4Network('%s/%s' % (search_ip[0],
                                                   search_prefix[0]))
            return str(ip_obj.ip), str(ip_obj.netmask)

        conn = self._conn
        iface_obj = conn.interfaceLookupByName(name)
        iface_libvirt_xml = \
            iface_obj.XMLDesc(libvirt.VIR_INTERFACE_XML_INACTIVE)
        return _get_ipaddr_info(iface_libvirt_xml)

    def update(self, name, params):
        if not self._is_interface_editable(name):
            raise InvalidParameter('GINNET0013E', {'name': name})

        try:
            iface_xml = self._create_iface_xml(name, params)
        except (ipaddr.AddressValueError, ipaddr.NetmaskValueError) as e:
            raise InvalidParameter('GINNET0003E', {'err': e.message})
        self._create_libvirt_network_iface(iface_xml)

    def _create_iface_xml(self, iface, net_params):
        m = E.interface(
            E.start(mode='onboot'),
            type='ethernet',
            name=iface)

        if net_params['ipaddr'] and net_params['netmask']:
            n = ipaddr.IPv4Network('%s/%s' % (net_params['ipaddr'],
                                              net_params['netmask']))
            protocol_elem = E.protocol(E.ip(address=str(n.ip),
                                            prefix=str(n.prefixlen)),
                                       family='ipv4')

            if 'gateway' in net_params:
                protocol_elem.append((E.route(gateway=net_params['gateway'])))
            m.append(protocol_elem)

        elif net_params['ipaddr'] or net_params['netmask']:
            raise InvalidParameter('GINNET0012E')

        return ET.tostring(m)

    def _create_libvirt_network_iface(self, iface_xml):
        conn = self._conn
        # Only one active transaction is allowed in the system level.
        # It implies that we can use changeBegin() as a synchronized point.
        conn.changeBegin()
        try:
            iface = conn.interfaceDefineXML(iface_xml)
            self._rollback_timer = Timer(
                self._confirm_timout, self._rollback_on_failure, args=[iface])
            if iface.isActive():
                iface.destroy()
                iface.create()
            self._rollback_timer.start()
        except Exception as e:
            self._rollback_on_failure(iface)
            raise OperationFailed('GINNET0004E', {'err': e.message})

    def _rollback_on_failure(self, iface):
        ''' Called by the Timer in a new thread to cancel wrong network
        configuration and rollback to previous configuration. '''
        conn = self._conn
        try:
            conn.changeRollback()
            if iface.isActive():
                iface.destroy()
                iface.create()
        except libvirt.libvirtError as e:
            # In case the timeout thread is preempted, and confirm_change() is
            # called before our changeRollback(), we can just ignore the
            # VIR_ERR_OPERATION_INVALID error.
            if e.get_error_code() != libvirt.VIR_ERR_OPERATION_INVALID:
                raise

    def activate(self, ifacename):
        InterfacesHelper().activate_iface(ifacename)

    def deactivate(self, ifacename):
        InterfacesHelper().deactivate_iface(ifacename)

    def confirm_change(self, _name):
        conn = self._conn
        self._rollback_timer.cancel()
        conn.changeCommit()

    def get_actions_per_module(self):
        mlx5_core_SRIOV = {
            'desc': 'SR-IOV: Single Root I/O Virtualization',
            'args': {'num_vfs': 'Number of virtual functions to enable'},
            'method': self._mlx5_SRIOV_enable
        }
        actions_mod = {
            'mlx5-core': {'SR-IOV': mlx5_core_SRIOV},
            'mlx5_core': {'SR-IOV': mlx5_core_SRIOV}
        }
        return actions_mod

    def _mlx5_SRIOV_get_max_VF(self, iface):
        max_vf_file = '/sys/class/net/%s/device/sriov_totalvfs' % iface
        max_vf = None

        if os.path.isfile(max_vf_file):
            with open(max_vf_file, 'r') as vf_file:
                max_vf = vf_file.read().strip('\n')

        return max_vf

    def _mlx5_SRIOV_precheck(self, iface, args):
        max_vfs_str = self._mlx5_SRIOV_get_max_VF(iface)
        if not max_vfs_str:
            raise OperationFailed("GINNET0082E", {'name': iface})

        if not args or 'num_vfs' not in args.keys():
            raise InvalidParameter("GINNET0077E")

        num_vfs = args['num_vfs']
        try:
            num_vfs = int(num_vfs)
        except ValueError:
            raise InvalidParameter("GINNET0079E")

        max_vfs = int(max_vfs_str)
        if num_vfs > max_vfs:
            raise InvalidParameter(
                "GINNET0083E",
                {'num_vf': num_vfs, 'max_vf': max_vfs, 'name': iface}
            )

        return num_vfs

    def _mlx5_SRIOV_enable(self, iface, args):
        num_vfs = self._mlx5_SRIOV_precheck(iface, args)

        sriov_files = [
            '/sys/class/net/%s/device/sriov_numvfs' % iface,
            '/sys/class/net/%s/device/mlx5_num_vfs' % iface
        ]
        any_file_found = False

        for sriov_file in sriov_files:
            if os.path.isfile(sriov_file):
                any_file_found = True
                with open(sriov_file, 'w') as f:
                    f.write(str(num_vfs) + '\n')
                break

        if not any_file_found:
            raise OperationFailed("GINNET0078E")

    def action(self, name, action_name, args):
        kernel_mod = netinfo.get_interface_kernel_module(name)
        actions = self.actions_mod.get(kernel_mod)
        if not actions or not actions.get(action_name):
            raise NotFoundError(
                "GINNET0076E",
                {'name': name, 'module': kernel_mod, 'action': action_name}
            )
        actions[action_name]['method'](name, args)
