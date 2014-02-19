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
from threading import Timer

from kimchi import netinfo
from kimchi.exception import InvalidParameter, NotFoundError, OperationFailed
from kimchi.model.libvirtconnection import LibvirtConnection


class InterfacesModel(object):

    def get_list(self):
        return netinfo.all_favored_interfaces()


class InterfaceModel(object):
    _confirm_timout = 10.0  # Second

    def __init__(self):
        self._rollback_timer = None

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
            conn.changeRollback()
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
