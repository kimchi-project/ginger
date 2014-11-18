#
# Project Ginger
#
# Copyright IBM, Corp. 2014
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

import ipaddr
import libvirt
import lxml.etree as ET
from lxml.builder import E
from threading import Timer

from kimchi import netinfo
from kimchi.exception import InvalidParameter, NotFoundError, OperationFailed
from kimchi.model.libvirtconnection import LibvirtConnection
from kimchi.utils import run_command
from kimchi.xmlutils.utils import xpath_get_text


class InterfacesModel(object):

    def get_list(self):
        nics = [nic for nic in netinfo.all_interfaces()]
        return sorted(nics)


class InterfaceModel(object):
    _confirm_timout = 10.0  # Second

    def __init__(self):
        self._rollback_timer = None

    def lookup(self, name):
        try:
            info = netinfo.get_interface_info(name)
        except ValueError:
            raise NotFoundError("KCHIFACE0001E", {'name': name})

        info['editable'] = self._is_interface_editable(name)
        return info

    def _is_interface_editable(self, iface):
        return iface in _get_all_libvirt_interfaces()

    def _get_all_libvirt_interfaces(self):
        conn = LibvirtConnection("qemu:///system").get()
        return [iface.name() for iface in conn.listAllInterfaces()]

    def _get_interface_info(self, name):
        try:
            info = netinfo.get_interface_info(name)
        except ValueError:
            raise NotFoundError("KCHIFACE0001E", {'name': name})
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
                               "/interface/protocol[@family='ipv4']"
                               "/ip/@prefix")

            ip_obj = ipaddr.IPv4Network('%s/%s' % (search_ip[0],
                                                   search_prefix[0]))
            return str(ip_obj.ip), str(ip_obj.netmask)

        conn = LibvirtConnection("qemu:///system").get()
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
        conn = LibvirtConnection("qemu:///system").get()
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
        conn = LibvirtConnection("qemu:///system").get()
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

    def confirm_change(self, _name):
        conn = LibvirtConnection("qemu:///system").get()
        self._rollback_timer.cancel()
        conn.changeCommit()
