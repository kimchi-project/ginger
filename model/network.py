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

from collections import namedtuple

import atexit
import augeas
import os
import platform
import threading
from threading import Timer

from wok.exception import OperationFailed
from wok.stringutils import decode_value
from wok.utils import run_command
from nw_interfaces_utils import cfgInterfacesHelper

gingerNetworkLock = threading.RLock()
parser = augeas.Augeas("/")


@atexit.register
def augeas_cleanup():
    global parser
    del parser


RESOLV_CONF = '/etc/resolv.conf'
NAMESERVER = 'nameserver'
GATEWAY = 'GATEWAY'
file_format = "/etc/network/interfaces"

Route = namedtuple('Route', ['prefix', 'gateway', 'dev'])


class NetworkModel(object):
    _confirm_timeout = 10.0

    def lookup(self, name):
        return {'nameservers': self._get_nameservers(),
                'gateway': self._get_default_gateway()}

    def _get_nameservers(self):
        if not os.path.isfile(RESOLV_CONF):
            return []
        try:
            with open(RESOLV_CONF) as f:
                return [line.split()[1] for line in f if line.startswith(
                    'nameserver') and len(line.split()) == 2]
        except IOError as e:
            raise OperationFailed('GINNET0001E', {'reason': e.message})

    def _set_nameservers(self, nameservers):
        try:
            with open(RESOLV_CONF, 'a+') as f:
                # read the file contents, delete old name servers
                # add new name servers to the file data and write
                data = f.read().splitlines()
                f.truncate(0)
                new_data = []
                for line in data:
                    if NAMESERVER not in line:
                        new_data.append(line)
                for server in nameservers:
                    if server:
                        new_data.append(NAMESERVER + ' ' + server)
                f.write(''.join('%s\n' % line for line in new_data))
                f.close()
        except Exception, e:
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
            raise OperationFailed('GINNET0011E', {'err': err})

        self._save_gateway_changes(old_iface, old_gateway)

    def _save_gateway_changes(self, old_iface, old_gateway):
        def save_config(iface, gateway=None):
            if gateway:
                gateway_info = {GATEWAY: gateway}
                cfgInterfacesHelper.write_attributes_to_cfg(iface,
                                                            gateway_info)

        def save_config_for_ubuntu(iface, gateway=None):
            if gateway:
                try:
                    gingerNetworkLock.acquire()
                    pattern = "etc/network/interfaces/iface[*]"
                    listout = parser.match(decode_value(pattern))
                    for list_iface in listout:
                        list_iface = decode_value(list_iface)
                        iface_from_match = parser.get(list_iface)
                        if iface_from_match == decode_value(iface):
                            parser.set(list_iface + "/gateway", gateway)
                            parser.save()
                except Exception, e:
                    raise OperationFailed("GINNET0074E", {'error': e})
                finally:
                    gingerNetworkLock.release()

        route = self._get_default_route_entry()
        gateway = route.gateway
        new_iface = route.dev
        try:
            if platform.linux_distribution()[0] == "Ubuntu":
                if os.path.isfile(os.sep + file_format):
                    save_config_for_ubuntu(new_iface, gateway)
            else:
                save_config(new_iface, gateway)
        except Exception:
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
                raise OperationFailed('GINNET0011E', {'err': err})
        raise OperationFailed('GINNET0089W')
