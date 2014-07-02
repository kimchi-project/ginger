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

from collections import namedtuple

import libvirt
from ipaddr import IPv4Network
from threading import Timer

from interfaces import InterfaceModel
from kimchi.exception import OperationFailed
from kimchi.model.libvirtconnection import LibvirtConnection
from kimchi.network import get_dev_netaddr
from kimchi.utils import run_command


RESOLV_CONF = '/etc/resolv.conf'

Route = namedtuple('Route', ['prefix', 'gateway', 'dev'])


class NetworkModel(object):
    _confirm_timeout = 10.0

    def lookup(self, name):
        return {'nameservers': self._get_nameservers(),
                'gateway': self._get_default_gateway()}

    def _get_nameservers(self):
        try:
            with open(RESOLV_CONF) as f:
                return [line.split()[1] for line in f
                        if line.startswith('nameserver')]
        except IOError as e:
            raise OperationFailed('GINNET0001E', {'reason': e.message})

    def _set_nameservers(self, nameservers):
        try:
            with open(RESOLV_CONF, 'w') as f:
                f.write(''.join('nameserver %s\n' % server
                        for server in nameservers))
        except IOError as e:
            raise OperationFailed('GINNET0002E', {'reason': e.message})

    def _get_default_route_entry(self):
        # Default route entry reads like this:
        # default via 9.115.126.1 dev wlp3s0  proto static  metric 1024
        out, err, rc = run_command(['ip', '-4', 'route', 'list',
                                    'match', '0/0'])
        if not rc:
            if out:
                routes = [line.split() for line in out.split('\n')]
                return next(Route(r[0], r[2], r[4]) for r in routes)
            else:
                return None
        else:
            raise OperationFailed('GINNET0009E', {'err': err})

    def _get_default_gateway(self):
        route = self._get_default_route_entry()
        return route.gateway if route is not None else None

    def _set_default_gateway(self, gateway):
        old_route = self._get_default_route_entry()
        if old_route is None:
            old_gateway, old_iface = None, None
        else:
            old_gateway, old_iface = old_route.gateway, old_route.dev

        _, err, rc = run_command(['ip', 'route', 'del', 'default'])
        if rc and not ('No such process' in err):
            raise OperationFailed('GINNET0010E', {'reason': err})
        _, err, rc = run_command(['ip', 'route', 'add', 'default', 'via',
                                  gateway])
        if rc:
            raise OperationFailed('GINNET0011E', {'reason': err})

        self._save_gateway_changes(old_iface, old_gateway)

    def _save_gateway_changes(self, old_iface, old_gateway):
        def save_config(conn, iface, gateway=None):
            n = IPv4Network(get_dev_netaddr(iface))
            net_params = {'ipaddr': str(n.ip), 'netmask': str(n.netmask)}
            if gateway:
                net_params['gateway'] = gateway
            iface_xml = InterfaceModel()._create_iface_xml(iface,
                                                           net_params)
            iface = conn.interfaceDefineXML(iface_xml)

        route = self._get_default_route_entry()
        gateway = route.gateway
        new_iface = route.dev
        conn = LibvirtConnection("qemu:///system").get()
        conn.changeBegin()
        save_config(conn, new_iface, gateway)
        if old_iface and new_iface != old_iface:
            save_config(conn, old_iface)

        self._rollback_timer = Timer(
            self._confirm_timeout, self._rollback_on_failure,
            args=[old_gateway])
        self._rollback_timer.start()

    def update(self, name, params):
        if 'nameservers' in params:
            self._set_nameservers(params['nameservers'])
        if 'gateway' in params:
            self._set_default_gateway(params['gateway'])

    def _rollback_on_failure(self, gateway):
        _, err, rc = run_command(['ip', 'route', 'del', 'default'])
        if rc and not ('No such process' in err):
            raise OperationFailed('GINNET0010E', {'reason': err})
        if gateway:
            _, err, rc = run_command(['ip', 'route', 'add', 'default', 'via',
                                      gateway])
            if rc:
                raise OperationFailed('GINNET0011E', {'reason': err})

        conn = LibvirtConnection("qemu:///system").get()
        try:
            conn.changeRollback()
        except libvirt.libvirtError as e:
            # In case the timeout thread is preempted, and confirm_change() is
            # called before our changeRollback(), we can just ignore the
            # VIR_ERR_OPERATION_INVALID error.
            if e.get_error_code() != libvirt.VIR_ERR_OPERATION_INVALID:
                raise

    def confirm_change(self, _name):
        self._rollback_timer.cancel()
        conn = LibvirtConnection("qemu:///system").get()
        conn.changeCommit()
