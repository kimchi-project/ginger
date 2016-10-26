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
import os
import time

import nw_cfginterfaces_utils

from nw_cfginterfaces_utils import CfgInterfacesHelper
from wok.exception import OperationFailed
from wok.stringutils import encode_value
from wok.utils import run_command, wok_log

from wok.plugins.gingerbase import netinfo


cfgInterfacesHelper = CfgInterfacesHelper()
carrier_path = '/sys/class/net/%s/carrier'

MLX5_SRIOV_BOOT_FILE = '/etc/infiniband/ginger_sriov_start.sh'
OPENIB_CONF_FILE = '/etc/infiniband/openib.conf'


def add_mlx5_SRIOV_boot_script_in_openib_conf():
    if not os.path.isfile(OPENIB_CONF_FILE):
        raise OperationFailed("GINNET0088E")

    try:
        script_line = "OPENIBD_POST_START=%s\n" % MLX5_SRIOV_BOOT_FILE
        line_found = False

        with open(OPENIB_CONF_FILE, 'r') as f:
            contents = f.readlines()

        for i in range(0, len(contents)):
            line = contents[i]
            if 'OPENIBD_POST_START' in line:
                line_found = True
                contents[i] = script_line
                break

        if not line_found:
            with open(OPENIB_CONF_FILE, 'a') as f:
                f.write(script_line)
        else:
            with open(OPENIB_CONF_FILE, 'w') as f:
                f.writelines(contents)

    except OperationFailed:
        raise
    except Exception as e:
        raise OperationFailed("GINNET0087E", {'err': e.message})


def create_initial_mlx5_SRIOV_boot_script(iface, num_vfs):
    template = """#!/bin/sh\n\
# ginger_sriov_start.sh: Connectx-4 SR-IOV init script - created by Ginger\n\
\n# %(iface)s setup\n\
echo 0 > /sys/class/net/%(iface)s/device/sriov_numvfs\n\
echo %(num_vf)s > /sys/class/net/%(iface)s/device/sriov_numvfs\n"""
    template = template % {'iface': iface, 'num_vf': num_vfs}

    try:
        with open(MLX5_SRIOV_BOOT_FILE, 'w+') as f:
            f.write(template)
        os.chmod(MLX5_SRIOV_BOOT_FILE, 0744)
    except Exception as e:
        raise OperationFailed("GINNET0086E", {'err': e.message})

    add_mlx5_SRIOV_boot_script_in_openib_conf()


def update_mlx5_SRIOV_script_content(script_content, iface, num_vfs):
    line_template = \
        "echo %(num_vf)s > /sys/class/net/%(iface)s/device/sriov_numvfs\n"
    updated_line = line_template % {'iface': iface, 'num_vf': num_vfs}

    line_found = False
    iface_marker = "# %s setup" % iface

    for i in range(0, len(script_content)):
        line = script_content[i]
        if iface_marker in line:
            line_found = True
            # skip 2 lines due to the 'echo 0'
            i = i + 2
            script_content[i] = updated_line
            break

    if not line_found:
        script_content.append(iface_marker + '\n')
        script_content.append(
            line_template % {'iface': iface, 'num_vf': 0}
        )
        script_content.append(updated_line)

    return script_content


def add_config_to_mlx5_SRIOV_boot_script(iface, num_vfs):
    if not os.path.isfile(MLX5_SRIOV_BOOT_FILE):
        create_initial_mlx5_SRIOV_boot_script(iface, num_vfs)
        return

    try:
        with open(MLX5_SRIOV_BOOT_FILE, 'r+') as f:
            content = update_mlx5_SRIOV_script_content(f.readlines(),
                                                       iface, num_vfs)
            f.seek(0)
            f.writelines(content)

        add_mlx5_SRIOV_boot_script_in_openib_conf()
    except Exception as e:
        raise OperationFailed("GINNET0086E", {'err': e.message})


class InterfacesHelper(object):
    """
    Class to help the interfaces perform some operations.
    """

    def activate_iface(self, ifacename):
        wok_log.info('Bring up an interface ' + ifacename)
        iface_type = netinfo.get_interface_type(ifacename)
        if iface_type == "nic":
            cmd_ipup = ['ip', 'link', 'set', '%s' % ifacename, 'up']
            out, error, returncode = run_command(cmd_ipup)
            if returncode != 0:
                # non-ascii encoded value and unicode value
                # cannot be concatenated, so convert both variable
                # to one format.
                raise OperationFailed('GINNET0059E',
                                      {'name': encode_value(ifacename),
                                       'error': encode_value(error)})
            # Some times based on system load, it takes few seconds to
            # reflect the  /sys/class/net files upon execution of 'ip link
            # set' command.  Following snippet is to wait util files get
            # reflect.
            timeout = self.wait_time(ifacename)
            if timeout == 5:
                wok_log.warn("Time-out has happened upon execution of 'ip "
                             "link set <interface> up', hence behavior of "
                             "activating an interface may not as expected.")
            else:
                wok_log.info('Successfully brought up the interface ' +
                             ifacename)
        wok_log.info('Activating an interface ' + ifacename)
        cmd_ifup = ['ifup', ifacename]
        out, error, returncode = run_command(cmd_ifup)
        if (returncode == 4):
            raise OperationFailed('GINNET0095E', {'name': ifacename})
        # Timeout is used for carrier file
        # since the carrier file needs few seconds approx 5 sec
        # to update the carrier value of an iface from 0 to 1.
        self.wait_time_carrier(ifacename)
        # Check for the carrier value after the device is activated
        if os.path.isfile(carrier_path % ifacename):
            with open(carrier_path % ifacename) as car_file:
                carrier_val = car_file.readline().strip()
            if (carrier_val == '0'):
                if iface_type != "nic":
                    raise OperationFailed('GINNET0094E', {'name': ifacename})
                else:
                    raise OperationFailed('GINNET0090E', {'name': ifacename})
        else:
            raise OperationFailed('GINNET0091E', {'name': ifacename})
        if returncode != 0:
            raise OperationFailed('GINNET0016E',
                                  {'name': encode_value(ifacename),
                                   'error': encode_value(error)})
        wok_log.info(
            'Connection successfully activated for the interface ' + ifacename)

    def deactivate_iface(self, ifacename):
        wok_log.info('Deactivating an interface ' + ifacename)
        cmd_ifdown = ['ifdown', '%s' % ifacename]
        out, error, returncode = run_command(cmd_ifdown)
        if returncode != 0:
            raise OperationFailed('GINNET0017E',
                                  {'name': encode_value(ifacename),
                                   'error': encode_value(error)})
        wok_log.info(
            'Connection successfully deactivated for the interface ' +
            ifacename)

        wok_log.info('Bringing down an interface ' + ifacename)
        iface_type = netinfo.get_interface_type(ifacename)
        if iface_type == "nic":
            cmd_ipdown = ['ip', 'link', 'set', '%s' % ifacename, 'down']
            out, error, returncode = run_command(cmd_ipdown)
            if returncode != 0:
                raise OperationFailed('GINNET0060E',
                                      {'name': encode_value(ifacename),
                                       'error': encode_value(error)})
            # Some times based on system load, it takes few seconds to
            # reflect the  /sys/class/net files upon execution of 'ip link
            # set' command. Following snippet is to wait util files get
            # reflect.
            timeout = self.wait_time(ifacename)
            if timeout == 5:
                wok_log.warn("Time-out has happened upon execution of 'ip "
                             "link set <interface> down', hence behavior of "
                             "activating an interface may not as expected.")
            else:
                wok_log.info('Successfully brought down the interface ' +
                             ifacename)
        vlan_or_bond = [nw_cfginterfaces_utils.IFACE_BOND,
                        nw_cfginterfaces_utils.IFACE_VLAN]
        if iface_type in vlan_or_bond:
            if encode_value(ifacename) in ethtool.get_devices():
                cmd_ip_link_del = ['ip', 'link', 'delete', '%s' % ifacename]
                out, error, returncode = run_command(cmd_ip_link_del)
                if (returncode != 0 and
                   (encode_value(ifacename) in ethtool.get_devices())):
                    raise OperationFailed('GINNET0017E',
                                          {'name': encode_value(ifacename),
                                           'error': encode_value(error)})

    def wait_time(self, ifacename):
        timeout = 0
        while timeout < 5:
            pathtocheck = "/sys/class/net/%s/operstate"
            if os.path.exists(pathtocheck % ifacename):
                break
            else:
                timeout += 0.5
                time.sleep(0.5)
        return timeout

    def wait_time_carrier(self, ifacename):
        timeout = 0
        while timeout < 5:
            if os.path.exists(carrier_path % ifacename):
                timeout += 0.5
                time.sleep(0.5)
            else:
                break
