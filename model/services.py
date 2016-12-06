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
"""A module to manipulate SystemD services

This module contains functions that allow Ginger to fetch
information from SystemD about the services running in
the host.

It also contains the ServicesModel and ServiceModel classes
that uses these module functions.

"""

import re

from wok.exception import NotFoundError, OperationFailed
from wok.utils import run_command


def parse_systemd_cgls_output(output):
    """Function that parses the output of the systemd-cgls command.

    Args:
        output (str): output of the systemd-cgls command with
            the following format:

            <cgroup_name>:
            `-PID CMD1
            `-PID2 CMD2
            `-ID3 CMD3

    Returns:
        dic: A dictionary that represents the cgroup name and processes.
            Format:
            {
                'name': (str),
                'processes': (dict)
            }
            processes format: { pid(str): command(str) }

    """
    re_pattern = '^[^0-9]+(?P<pid>[0-9]+) (?P<command>.*)'
    matcher = re.compile(re_pattern)

    items = output.strip().split('\n')
    cgroup_name = items[0][:-1]
    processes_dict = {}
    for proc in items[1:]:
        match = matcher.search(proc)
        pid = match.group('pid')
        command = match.group('command')
        processes_dict[pid] = command

    cgroup_dict = {
        'name': cgroup_name,
        'processes': processes_dict
    }

    return cgroup_dict


def parse_systemctlshow_output(output):
    """Function that parses systemctl show output.

    Args:
        output (str): output of the command
            with the following format:

            ControlGroup=<string>
            Description=<string>
            LoadState=<string>
            ActiveState=<string>
            SubState=<string>
            UnitFileState=<string>

    Returns:
        dic: A dictionary that represents the state of the service.
            Format:
            {
                'cgroup': (str),
                'desc': (str),
                'load': (str),
                'active': (str),
                'sub': (str),
                'autostart': (bool)
            }

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
    """Parses the output of 'systemctl list-unit-files --no-pager --type=service'.

    Returns:
        List[str]: list of services.

    """
    lines = output.splitlines()[1:-2]
    services = []
    for line in lines:
        if "@" not in line:
            services.append(line.split()[0])

    return services


def run_systemd_command(command):
    """Function that runs systemd commands.

    Runs a systemd command specified in the argument, throwing
    a specific error if something goes wrong.

    Args:
        command (List[str]): the systemd command to be executed.

    Returns:
        str: Output of the command.

    Raises:
        OperationFailed if the return code of the command is not 0.

    """
    output, err, rcode = run_command(command)
    if rcode != 0:
        cmd_str = ' '.join(command)
        raise OperationFailed(
            'GINSERV00001E', {'cmd': cmd_str, 'err': err}
        )
    return output


def get_services_list():
    """Function that returns the services running in the host.

    Returns:
        List[str]: a list of services.

    """
    cmd = ['systemctl', 'list-unit-files', '--no-pager', '--type=service']
    output = run_systemd_command(cmd)
    return parse_systemctllist_output(output)


def service_exists(service):
    """Function that checks if a service exists in the host.

    Returns:
        bool: True if exists, False otherwise.

    """
    cmd = ['systemctl', 'show', service, '--property=LoadError']
    output = run_systemd_command(cmd)
    return 'No such file or directory' not in output


def get_service_info(service):
    """Retrieves information about an existing service.

    Args:
        service (str): an existing service from the host.

    Returns:
        dic: A dictionary that represents the state of the service.
            Format:
            {
                'cgroup': (str),
                'desc': (str),
                'load': (str),
                'active': (str),
                'sub': (str),
                'autostart': (bool)
            }

    """
    cmd = ['systemctl', 'show', service,
           '--property=LoadState,ActiveState,'
           'SubState,Description,UnitFileState,ControlGroup']
    output = run_systemd_command(cmd)
    return parse_systemctlshow_output(output)


def get_cgroup_info(cgroup):
    """Retrieves cgroup PID information.

    Args:
        cgroup (str): name of the cgroup

    Returns:
        dic: A dictionary that represents the cgroup name and processes.
            Format:
            {
                'name': (str),
                'processes': (dict)
            }
            processes format: { pid(str): command(str) }

    """
    cgroup = cgroup.replace('\\x5c', '\\')
    cmd = ['systemd-cgls', '--no-pager', cgroup]
    output = run_systemd_command(cmd)
    return parse_systemd_cgls_output(output)


class ServicesModel(object):
    """Collection model class for services."""

    @staticmethod
    def get_list():
        """Method that retrieves the service list.

        Returns:
            List[str]: a list of services.

        """
        return get_services_list()


class ServiceModel(object):
    """Resource model class for a service."""

    @staticmethod
    def lookup(name):
        """Method that retrieves information about a service.

        Returns:
            dic: A dictionary that represents the state of the service.
                Format:
                {
                    'cgroup': (str),
                    'desc': (str),
                    'load': (str),
                    'active': (str),
                    'sub': (str),
                    'autostart': (bool)
                }

        Raises:
            NotFoundError if the service does not exist.

        """
        if not service_exists(name):
            raise NotFoundError('GINSERV00002E', {'name': name})

        lookup_dict = get_service_info(name)
        lookup_dict['name'] = name
        if lookup_dict.get('cgroup'):
            lookup_dict['cgroup'] = get_cgroup_info(lookup_dict['cgroup'])

        return lookup_dict

    @staticmethod
    def enable(name):
        """Method that enables a service.

        Args:
            name (str): name of the service.

        """
        run_systemd_command(['systemctl', 'enable', name])

    @staticmethod
    def disable(name):
        """Method that disables a service.

        Args:
            name (str): name of the service.

        """
        run_systemd_command(['systemctl', 'disable', name])

    @staticmethod
    def start(name):
        """Method that starts a service.

        Args:
            name (str): name of the service.

        """
        run_systemd_command(['systemctl', 'start', name])

    @staticmethod
    def stop(name):
        """Method that stops a service.

        Args:
            name (str): name of the service.

        """
        run_systemd_command(['systemctl', 'stop', name])

    @staticmethod
    def restart(name):
        """Method that restarts a service.

        Args:
            name (str): name of the service.

        """
        run_systemd_command(['systemctl', 'restart', name])
