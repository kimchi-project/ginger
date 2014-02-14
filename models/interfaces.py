#
# Project Kimchi
#
# Copyright IBM, Corp. 2013
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

from kimchi import netinfo
from kimchi.exception import InvalidParameter, NotFoundError, OperationFailed
from kimchi.model.libvirtconnection import LibvirtConnection


class InterfacesModel(object):

    def get_list(self):
        return netinfo.all_favored_interfaces()


class InterfaceModel(object):

    def lookup(self, name):
        try:
            return netinfo.get_interface_info(name)
        except ValueError:
            raise NotFoundError("KCHIFACE0001E", {'name': name})

    def update(self, name, params):
        try:
            iface_xml = self._create_iface_xml(name, params)
        except (ipaddr.AddressValueError, ipaddr.NetmaskValueError) as e:
            raise InvalidParameter('GINNET0003E', {'err': e.message})
        self._create_libvirt_network_iface(iface_xml)

    def _create_iface_xml(self, iface, net_params):
        n = ipaddr.IPv4Network('%s/%s' %
                               (net_params['ipaddr'], net_params['netmask']))
        m = E.interface(
            E.start(mode='onboot'),
            E.protocol(
                E.ip(address=str(n.ip), prefix=str(n.prefixlen)),
                family='ipv4'),
            type='ethernet',
            name=iface)
        if 'gateway' in net_params:
            m.find('protocol').append(E.route(gateway=net_params['gateway']))
        return ET.tostring(m)

    def _create_libvirt_network_iface(self, iface_xml):
        conn = LibvirtConnection("qemu:///system").get()
        conn.changeBegin()
        try:
            iface = conn.interfaceDefineXML(iface_xml)
            if iface.isActive():
                iface.destroy()
            iface.create()
        except libvirt.libvirtError as e:
            conn.changeRollback()
            raise OperationFailed('GINNET0004E', {'err': e.message})
        else:
            conn.changeCommit()
