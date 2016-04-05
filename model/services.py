# -*- coding: utf-8 -*-
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


from wok.exception import NotFoundError, OperationFailed
from wok.utils import run_command, wok_log


def parse_systemd_cgls_output(output):
    """
    Sample output:
<cgroup_name>:
`-PID CMD1
`-PID2 CMD2
`-ID3 CMD3
    """
    items = output.strip().split('\n')
    cgroup_name = items[0][:-1]
    processes_dict = {}
    for proc in items[1:]:
        proc = proc.split('-', 1)[1]
        pid, command = proc.split(' ', 1)
        processes_dict[pid] = command

    cgroup_dict = {
        'name': cgroup_name,
        'processes': processes_dict
    }

    return cgroup_dict


def parse_systemctlshow_output(output):
    """
    Sample output:
ControlGroup=/system.slice/wokd.service
Description=Wok - Webserver Originated from Kimchi
LoadState=loaded
ActiveState=active
SubState=running
UnitFileState=disabled
    """
    items = output.strip().split('\n')
    attr_map = {'ControlGroup': 'cgroup', 'Description': 'desc',
                'LoadState': 'load', 'ActiveState': 'active',
                'SubState': 'sub', 'UnitFileState': 'autostart'}

    service_dict = {}

    for item in items:
        key, val = item.split('=', 1)
        service_key = attr_map.get(key)
        if not service_key:
            continue
        service_dict[service_key] = val

    service_dict['autostart'] = service_dict.get('autostart') == 'enabled'

    return service_dict


def parse_systemctllist_output(output):
    """
    Sample output:
  UNIT                                LOAD      ACTIVE   SUB     DESCRIPTION
  user@1000.service      loaded    active  running  User Manager for UID 1000
  user@42.service        loaded    active  running  User Manager for UID 42
  vgauthd.service   loaded  inactive dead  VGAuth Service for open-vm-tools
  vmtoolsd.service  loaded  inactive dead  Service for virtual machines hosted
  wokd.service      loaded  active running Wok - Webserver Originated from Kim
  wpa_supplicant.service  loaded    active   running WPA supplicant
● xdm.service   not-found inactive dead    xdm.service
● ypbind.service   not-found inactive dead    ypbind.service

LOAD   = Reflects whether the unit definition was properly loaded.
ACTIVE = The high-level unit activation state, i.e. generalization of SUB.
SUB    = The low-level unit activation state, values depend on unit type.

163 loaded units listed.
To show all installed unit files use 'systemctl list-unit-files'
    """
    lines = output.strip().split('\n')
    lines = lines[1:]
    services = []
    for line in lines:
        if line == '' or line.startswith('LOAD'):
            break
        service = line.split()[0]
        if service == '●' or service == '*':
            service = line.split()[1]
        services.append(service)

    return services


def run_systemd_command(command):
    output, err, rc = run_command(command)
    if rc != 0:
        cmd_str = command.join(' ')
        wok_log.error('Error executing systemctl command %s, '
                      'reason: %s' % (cmd_str, err))
        raise OperationFailed(
            'GINSERV00001E', {'cmd': cmd_str, 'err': err}
        )
    return output


def get_services_list():
    cmd = ['systemctl', '--type=service', '--no-pager']
    output = run_systemd_command(cmd)
    return parse_systemctllist_output(output)


def service_exists(service):
    cmd = ['systemctl', 'show', service, '--property=LoadError']
    output = run_systemd_command(cmd)
    return 'No such file or directory' not in output


def get_service_info(service):
    cmd = ['systemctl', 'show', service,
           '--property=LoadState,ActiveState,'
           'SubState,Description,UnitFileState,ControlGroup']
    output = run_systemd_command(cmd)
    return parse_systemctlshow_output(output)


def get_cgroup_info(cgroup):
    cgroup = cgroup.replace('\\x5c', '\\')
    cmd = ['systemd-cgls', '--no-pager', cgroup]
    output = run_systemd_command(cmd)
    return parse_systemd_cgls_output(output)


class ServicesModel(object):

    def get_list(self):
        return get_services_list()


class ServiceModel(object):

    def lookup(self, name):
        if not service_exists(name):
            wok_log.error(
                'Error retrieving service %s. Service does not '
                'exist.' % name
            )
            raise NotFoundError('GINSERV00002E', {'name': name})

        lookup_dict = get_service_info(name)
        lookup_dict['name'] = name
        if lookup_dict.get('cgroup'):
            lookup_dict['cgroup'] = get_cgroup_info(lookup_dict['cgroup'])

        return lookup_dict

    def enable(self, name):
        run_systemd_command(['systemctl', 'enable', name])

    def disable(self, name):
        run_systemd_command(['systemctl', 'disable', name])

    def start(self, name):
        run_systemd_command(['systemctl', 'start', name])

    def stop(self, name):
        run_systemd_command(['systemctl', 'stop', name])

    def restart(self, name):
        run_systemd_command(['systemctl', 'restart', name])
