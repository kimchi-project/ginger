#
# Project Ginger
#
# Copyright IBM Corp, 2016-2017
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

from nw_cfginterfaces_utils import IFACE_BOND
from nw_cfginterfaces_utils import IFACE_VLAN
from nw_interfaces_utils import add_config_to_mlx5_SRIOV_boot_script
from nw_interfaces_utils import cfgInterfacesHelper
from nw_interfaces_utils import InterfacesHelper
from wok.asynctask import AsyncTask
from wok.exception import InvalidOperation, InvalidParameter, NotFoundError
from wok.exception import OperationFailed
from wok.model.tasks import TaskModel
from wok.stringutils import encode_value
from wok.utils import wok_log

from wok.plugins.gingerbase import netinfo


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

    def __init__(self, **kargs):
        self._rollback_timer = None
        self.objstore = kargs['objstore']
        self.task = TaskModel(**kargs)

    def lookup(self, name):
        """
        Populate info using runtime information from /sys/class/net files for
        active interfaces and for inactive bond and vlan interfaces from cfg
        files
        :param name:
        :return:
        """
        try:
            # encode name to ensure comparison are in same type.
            if encode_value(name) in ethtool.get_devices():
                info = netinfo.get_interface_info(name)
            elif cfgInterfacesHelper.is_cfgfileexist(name):
                type = cfgInterfacesHelper.get_type(name).lower()
                if type not in IFACE_BOND + [IFACE_VLAN]:
                    raise ValueError
                device = cfgInterfacesHelper.get_device(name)
                info = {'device': device,
                        'type': cfgInterfacesHelper.get_type(name),
                        'status': "down",
                        'ipaddr': "",
                        'netmask': "",
                        'macaddr': "",
                        'module': netinfo.get_interface_kernel_module(name)}

                if info.get('type') is not 'nic':
                    info['nic_type'] = 'N/A'
                else:
                    info['nic_type'] = netinfo.get_nic_type(device)

            else:
                raise ValueError('unknown interface: %s' % name)

            info['rdma_enabled'] = netinfo.is_rdma_enabled(name)

            return info

        except ValueError:
            raise NotFoundError("GINNET0014E", {'name': name})

    def activate(self, ifacename):
        InterfacesHelper().activate_iface(ifacename)

    def deactivate(self, ifacename):
        InterfacesHelper().deactivate_iface(ifacename)

    def _mlx5_SRIOV_get_max_VF(self, iface):
        max_vf_file = '/sys/class/net/%s/device/sriov_totalvfs' % iface
        max_vf = None

        if os.path.isfile(max_vf_file):
            try:
                with open(max_vf_file, 'r') as vf_file:
                    max_vf = vf_file.read().strip('\n')
            except Exception as e:
                raise OperationFailed("GINNET0085E",
                                      {'file': max_vf_file, 'err': e.message})

        return max_vf

    def _mlx5_SRIOV_get_numvf_config_file(self, iface):
        sriov_files = [
            '/sys/class/net/%s/device/sriov_numvfs' % iface,
            '/sys/class/net/%s/device/mlx5_num_vfs' % iface
        ]
        for sriov_file in sriov_files:
            if os.path.isfile(sriov_file):
                return sriov_file

        raise OperationFailed("GINNET0078E")

    def _mlx5_SRIOV_get_current_VFs(self, iface):
        sriov_file = self._mlx5_SRIOV_get_numvf_config_file(iface)
        try:
            with open(sriov_file, 'r') as vf_file:
                current_vf = vf_file.read().strip('\n')
            return current_vf
        except Exception as e:
            raise OperationFailed("GINNET0085E",
                                  {'file': sriov_file, 'err': e.message})

    def _mlx5_SRIOV_precheck(self, iface, args):
        max_vfs_str = self._mlx5_SRIOV_get_max_VF(iface)
        if not max_vfs_str:
            raise OperationFailed("GINNET0082E", {'name': iface})

        if args is None:
            raise InvalidParameter("GINNET0077E")

        try:
            num_vfs = int(args)
        except ValueError:
            raise InvalidParameter("GINNET0079E")

        max_vfs = int(max_vfs_str)
        if num_vfs > max_vfs:
            raise InvalidParameter(
                "GINNET0083E",
                {'num_vf': num_vfs, 'max_vf': max_vfs, 'name': iface}
            )

        current_vfs_str = self._mlx5_SRIOV_get_current_VFs(iface)
        if num_vfs == int(current_vfs_str):
            if num_vfs == 0:
                raise InvalidParameter("GINNET0093E", {'name': iface})
            else:
                raise InvalidParameter("GINNET0084E",
                                       {'name': iface, 'num_vf': num_vfs})

        return num_vfs

    def enable_sriov(self, name, args):
        kernel_mod = netinfo.get_interface_kernel_module(name)
        if kernel_mod not in ['mlx5_core', 'mlx5-core']:
            raise InvalidOperation("GINNET0076E",
                                   {'name': name, 'module': kernel_mod})

        num_vfs = self._mlx5_SRIOV_precheck(name, args)

        params = {'name': name, 'num_vfs': num_vfs}

        task_id = AsyncTask(
            '/plugins/ginger/network/%s/enable_sriov' % name,
            self._mlx5_SRIOV_enable_task, params
        ).id
        return self.task.lookup(task_id)

    #     When setting the virtual functions, the mlx5_core driver
    # creates each VF as 'eth0' and then rename it to the actual VF
    # interface name.
    #     However, the driver doesn't finish this procedure in the
    # time interval we wait for the 'write' call in its system file
    # to return. This causes at least one 'eth0' interface slipping
    # to the rest of the backend and, when Ginger attempts to use it
    # as a regular interface, the driver most likely renamed it to
    # the right name and the 'eth0' interface is now invalid, causing
    # random backend errors.
    #     This function waits at most 5 seconds until the mlx5_core
    # driver finishes its job. No error will be thrown if the 5 seconds
    # time expires.
    #
    # TODO: erase this function and its call when the mlx5_driver
    # is fixed.
    def _wait_VFs_setup(self, ifaces_without_sriov):
        timeout = 0
        new_ifaces = None
        while timeout < 5:
            current_ifaces = cfgInterfacesHelper.get_interface_list()
            new_ifaces = ifaces_without_sriov ^ current_ifaces

            if 'eth0' in new_ifaces:
                timeout += 0.5
                time.sleep(0.5)
            else:
                break
        if 0 < timeout < 5:
            wok_log.info('Ginger backend waited ' + str(timeout) +
                         ' seconds for the mlx5_core driver to '
                         'complete the SR-IOV setup.')
        elif timeout == 5:
            wok_log.error('Ginger backend waited 5 seconds but the '
                          'mlx5_core driver did not complete the SR-IOV '
                          'setup. Is the mlx5_core driver working '
                          'properly?')
        return new_ifaces

    def _mlx5_SRIOV_enable_task(self, cb, params):
        iface = params.get('name')
        num_vfs = params.get('num_vfs')

        sriov_file = self._mlx5_SRIOV_get_numvf_config_file(iface)

        cb('Setting SR-IOV for %s' % iface)

        try:
            with open(sriov_file, 'w') as f:
                f.write('0\n')

            if num_vfs == 0:
                add_config_to_mlx5_SRIOV_boot_script(iface, num_vfs)
            else:
                ifaces_without_sriov = \
                    cfgInterfacesHelper.get_interface_list()

                with open(sriov_file, 'w') as f:
                    f.write(str(num_vfs) + '\n')

                add_config_to_mlx5_SRIOV_boot_script(iface, num_vfs)

                new_ifaces = self._wait_VFs_setup(ifaces_without_sriov)

                for new_iface in new_ifaces:
                    cfgInterfacesHelper.create_interface_cfg_file(new_iface)

        except Exception as e:
            raise OperationFailed("GINNET0085E", {'err': e.message})

        cb('SR-IOV setup for %s completed' % iface, True)
