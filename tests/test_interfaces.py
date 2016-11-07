#
# Project Ginger
#
# Copyright IBM Corp, 2015-2016
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

import __builtin__ as builtins
import mock
import unittest

from mock import call, mock_open, patch

import wok.plugins.ginger.model.nw_interfaces_utils as ifaces_utils
import wok.plugins.gingerbase.netinfo as netinfo

from wok import config
from wok.exception import InvalidOperation, InvalidParameter, OperationFailed
from wok.model.tasks import TaskModel
from wok.objectstore import ObjectStore
from wok.plugins.ginger.model.interfaces import InterfaceModel


class InterfacesTests(unittest.TestCase):

    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        self.task = TaskModel(objstore=self._objstore)

    @mock.patch('wok.plugins.gingerbase.netinfo.os')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.run_command')
    def test_activate(self, mock_run_command, mock_get_interface_type,
                      mock_os):
        mock_run_command.return_value = ["", "", 0]
        mock_os.path.isfile.return_value = True
        mock_get_interface_type.return_value = "nic"
        interface = "test_eth0"
        cmd = ['ip', 'link', 'set', '%s' % interface, 'up']
        InterfaceModel(objstore=self._objstore).activate(interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.gingerbase.netinfo.os')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.run_command')
    def test_activate_no_config_file(self, mock_run_command,
                                     mock_get_interface_type, mock_os):
        mock_run_command.return_value = ["", "", 0]
        mock_os.path.isfile.return_value = False
        mock_get_interface_type.return_value = "nic"
        interface = "test_eth0"
        calls = [(['ip', 'link', 'set', '%s' % interface, 'up'],),
                 (['ifup', '%s' % interface],)]
        InterfaceModel(objstore=self._objstore).activate(interface)
        for i in range(0, 1):
            x, y = mock_run_command.call_args_list[i]
            assert x == calls[i]
        assert mock_run_command.call_count == 1

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.run_command')
    def test_activate_fail(self, mock_run_command, mock_get_interface_type):
        mock_run_command.return_value = ["", "Unable to activate", 4]
        mock_get_interface_type.return_value = "nic"
        interface = "test_eth0"
        cmd = ['ip', 'link', 'set', '%s' % interface, 'up']
        self.assertRaises(OperationFailed,
                          InterfaceModel(objstore=self._objstore).activate,
                          interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.gingerbase.netinfo.os')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.run_command')
    def test_deactivate(self, mock_run_command, mock_get_interface_type,
                        mock_os):
        mock_run_command.return_value = ["", "", 0]
        mock_os.path.isfile.return_value = True
        mock_get_interface_type.return_value = "nic"
        interface = "test_eth0"
        cmd = ['ip', 'link', 'set', '%s' % interface, 'down']
        InterfaceModel(objstore=self._objstore).deactivate(interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.gingerbase.netinfo.os')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.run_command')
    def test_deactivate_no_config_file(self, mock_run_command,
                                       mock_get_interface_type, mock_os):
        mock_run_command.return_value = ["", "", 0]
        mock_os.path.isfile.return_value = False
        mock_get_interface_type.return_value = "nic"
        interface = "test_eth0"
        calls = [(['ip', 'link', 'set', '%s' % interface, 'down'],),
                 (['ifdown', '%s' % interface],)]
        InterfaceModel(objstore=self._objstore).deactivate(interface)
        for i in range(0, 1):
            x, y = mock_run_command.call_args_list[i]
            assert x == calls[i]
        assert mock_run_command.call_count == 1

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.run_command')
    def test_deactivate_fail(self, mock_run_command, mock_get_interface_type):
        mock_run_command.return_value = ["", "Unable to deactivate", 4]
        mock_get_interface_type.return_value = "nic"
        interface = "test_eth0"
        cmd = ['ip', 'link', 'set', '%s' % interface, 'down']
        self.assertRaises(OperationFailed,
                          InterfaceModel(objstore=self._objstore).deactivate,
                          interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('os.readlink')
    def test_netinfo_interface_module_lookup_success(self, mock_readlink):
        mock_readlink.return_value = '../../../../module/dummy_net_module'

        module = netinfo.get_interface_kernel_module('dummy_iface')
        mock_readlink.assert_called_once_with(
            '/sys/class/net/dummy_iface/device/driver/module')

        self.assertEqual(module, 'dummy_net_module')

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('ethtool.get_devices')
    @mock.patch('ethtool.get_ipaddr')
    @mock.patch('ethtool.get_netmask')
    @mock.patch('wok.plugins.gingerbase.netinfo.macaddr')
    def test_netinfo_get_interface_info(self, mock_macaddr, mock_netmask,
                                        mock_ipaddr, mock_getdevs,
                                        mock_get_module):
        mock_get_module.return_value = 'dummy_net_module'
        mock_getdevs.return_value = ['dev1', 'dummy_iface', 'dev2']
        mock_ipaddr.return_value = '99.99.99.99'
        mock_netmask.return_value = '255.255.255.0'
        mock_macaddr.return_value = 'aa:bb:cc:dd:ee:ff'

        iface_info = netinfo.get_interface_info('dummy_iface')

        mock_macaddr.assert_called_once_with('dummy_iface')
        mock_netmask.assert_called_once_with('dummy_iface')
        mock_ipaddr.assert_called_once_with('dummy_iface')
        mock_getdevs.assert_called_once_with()
        mock_get_module.assert_called_once_with('dummy_iface')

        self.assertEqual(iface_info.get('device'), 'dummy_iface')
        self.assertEqual(iface_info.get('type'), 'unknown')
        self.assertEqual(iface_info.get('status'), 'down')
        self.assertEqual(iface_info.get('ipaddr'), '99.99.99.99')
        self.assertEqual(iface_info.get('netmask'), '255.255.255.0')
        self.assertEqual(iface_info.get('macaddr'), 'aa:bb:cc:dd:ee:ff')
        self.assertEqual(iface_info.get('module'), 'dummy_net_module')

    @mock.patch('ethtool.get_devices')
    @mock.patch('wok.plugins.gingerbase.netinfo.is_rdma_enabled')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_info')
    def test_interface_lookup(self, mock_iface_info, mock_rdma_enabled,
                              mock_getdevs):
        iface_info_return = {
            'device': 'dummy_iface', 'type': 'unknown', 'status': 'down',
            'ipaddr': '99.99.99.99', 'netmask': '255.255.255.0',
            'macaddr': 'aa:bb:cc:dd:ee:ff', 'module': 'dummy_net_module'
        }
        mock_iface_info.return_value = iface_info_return
        mock_rdma_enabled.return_value = True
        mock_getdevs.return_value = ['dev1', 'dummy_iface', 'dev2']

        iface_model = InterfaceModel(objstore=self._objstore)
        iface_info = iface_model.lookup('dummy_iface')
        mock_iface_info.assert_called_once_with('dummy_iface')
        mock_rdma_enabled.assert_called_once_with('dummy_iface')
        mock_getdevs.called_once_with()

        self.assertEqual(iface_info.get('device'), 'dummy_iface')
        self.assertEqual(iface_info.get('type'), 'unknown')
        self.assertEqual(iface_info.get('status'), 'down')
        self.assertEqual(iface_info.get('ipaddr'), '99.99.99.99')
        self.assertEqual(iface_info.get('netmask'), '255.255.255.0')
        self.assertEqual(iface_info.get('macaddr'), 'aa:bb:cc:dd:ee:ff')
        self.assertEqual(iface_info.get('module'), 'dummy_net_module')
        self.assertTrue(iface_info.get('rdma_enabled'))

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    def test_invalid_module_enable_sriov_failure(self, mock_get_module):
        mock_get_module.return_value = 'unknown'

        expected_error_msg = "GINNET0076E"
        with self.assertRaisesRegexp(InvalidOperation, expected_error_msg):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('any_iface_name', {'num_vfs': 4})

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_no_args_failure(self, mock_get_max_VF,
                                        mock_get_module):

        mock_get_max_VF.return_value = '1'
        mock_get_module.return_value = 'mlx5_core'

        expected_error_msg = "GINNET0077E"
        with self.assertRaisesRegexp(InvalidParameter, expected_error_msg):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('any_iface_name', None)

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_argument_failure(self, mock_get_max_VF,
                                         mock_get_module):

        mock_get_max_VF.return_value = '1'
        mock_get_module.return_value = 'mlx5_core'

        expected_error_msg = "GINNET0079E"
        with self.assertRaisesRegexp(InvalidParameter, expected_error_msg):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('any_iface_name', 'not_an_int')

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_no_system_files_failure(self, mock_get_max_VF,
                                                mock_isfile,
                                                mock_get_module):
        mock_get_max_VF.return_value = '8'
        mock_get_module.return_value = 'mlx5_core'

        call_file1_not_exist = \
            '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        call_file2_not_exist = \
            '/sys/class/net/%s/device/mlx5_num_vfs' % 'iface1'

        mock_isfile.side_effect = [False, False]

        mock_isfile_calls = [
            call(call_file1_not_exist),
            call(call_file2_not_exist)
        ]

        expected_error_msg = "GINNET0078E"
        with self.assertRaisesRegexp(OperationFailed, expected_error_msg):
            iface_model = InterfaceModel(objstore=self._objstore)
            task_obj = iface_model.enable_sriov('iface1', 4)
            self.task.wait(task_obj['id'])

            mock_isfile.assert_has_calls(mock_isfile_calls)

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    def test_mlx5_sriov_not_enabled_in_FW(self, mock_isfile, mock_get_module):
        mock_get_module.return_value = 'mlx5_core'

        file1 = '/sys/class/net/%s/device/sriov_totalvfs' % 'iface1'
        mock_isfile.return_value = False

        with self.assertRaisesRegexp(OperationFailed, 'GINNET0082E'):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('iface1', 4)
            mock_isfile.assert_called_once_with(file1)

    @mock.patch('os.path.isfile')
    def test_mlx5_sriov_get_maxVF_value(self, mock_isfile):
        file1 = '/sys/class/net/%s/device/sriov_totalvfs' % 'iface1'
        mock_isfile.return_value = True

        open_ = mock_open(read_data='8\n')

        with patch.object(builtins, 'open', open_):
            iface_model = InterfaceModel(objstore=self._objstore)
            max_vf_str = iface_model._mlx5_SRIOV_get_max_VF('iface1')
            mock_isfile.assert_called_once_with(file1)
            self.assertEqual(max_vf_str, '8')

        self.assertEqual(open_.call_args_list, [call(file1, 'r')])

    @mock.patch('os.path.isfile')
    def test_mlx5_sriov_get_currentVF_value(self, mock_isfile):
        file1 = '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        mock_isfile.return_value = True

        open_ = mock_open(read_data='5\n')

        with patch.object(builtins, 'open', open_):
            iface_model = InterfaceModel(objstore=self._objstore)
            curr_vf_str = iface_model._mlx5_SRIOV_get_current_VFs('iface1')
            mock_isfile.assert_called_once_with(file1)
            self.assertEqual(curr_vf_str, '5')

        self.assertEqual(open_.call_args_list, [call(file1, 'r')])

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_fails_if_VF_greater_max(self, mock_get_max_VF,
                                                mock_isfile, mock_get_module):

        mock_get_max_VF.return_value = '8'
        mock_get_module.return_value = 'mlx5_core'

        file1 = '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        mock_isfile.return_value = True

        with self.assertRaisesRegexp(InvalidParameter, 'GINNET0083E'):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('iface1', 16)
            mock_isfile.assert_called_once_with(file1)

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_current_VFs')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_fails_if_VF_equal_to_current(
        self, mock_get_max_VF, mock_get_current_VF,
        mock_isfile, mock_get_module
    ):

        mock_get_max_VF.return_value = '16'
        mock_get_current_VF.return_value = '8'
        mock_get_module.return_value = 'mlx5_core'

        file1 = '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        mock_isfile.return_value = True

        with self.assertRaisesRegexp(InvalidParameter, 'GINNET0084E'):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('iface1', 8)
            mock_isfile.assert_called_once_with(file1)

    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_current_VFs')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_sriov_fails_if_VF_and_config_value_is_zero(
        self, mock_get_max_VF, mock_get_current_VF,
        mock_isfile, mock_get_module
    ):

        mock_get_max_VF.return_value = '16'
        mock_get_current_VF.return_value = '0'
        mock_get_module.return_value = 'mlx5_core'

        file1 = '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        mock_isfile.return_value = True

        with self.assertRaisesRegexp(InvalidParameter, 'GINNET0093E'):
            iface_model = InterfaceModel(objstore=self._objstore)
            iface_model.enable_sriov('iface1', 0)
            mock_isfile.assert_called_once_with(file1)

    @mock.patch('wok.plugins.ginger.model.interfaces.'
                'add_config_to_mlx5_SRIOV_boot_script')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.create_interface_cfg_file')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.get_interface_list')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_current_VFs')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_success(self, mock_get_max_VF, mock_get_current_VF,
                                mock_isfile, mock_get_module,
                                mock_get_iface_list, mock_create_cfg_file,
                                mock_add_boot_script):

        mock_get_max_VF.return_value = '8'
        mock_get_current_VF.return_value = '2'
        mock_get_module.return_value = 'mlx5_core'

        file1 = '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        mock_isfile.return_value = True

        mock_get_iface_list.side_effect = [
            set(['iface1', 'iface2']),
            set(['iface1', 'sriov1', 'sriov2', 'iface2'])
        ]

        open_ = mock_open(read_data='')

        with patch.object(builtins, 'open', open_):
            iface_model = InterfaceModel(objstore=self._objstore)
            task_obj = iface_model.enable_sriov('iface1', 4)
            self.task.wait(task_obj['id'])

            finished_task = self.task.lookup(task_obj['id'])
            self.assertEquals(finished_task['status'], 'finished')
            mock_isfile.assert_called_once_with(file1)

        self.assertEqual(open_.call_args_list,
                         [call(file1, 'w'), call(file1, 'w')])
        self.assertEqual(open_().write.mock_calls, [call('0\n'), call('4\n')])
        mock_create_cfg_file.assert_has_calls(
            [call('sriov1'), call('sriov2')]
        )
        mock_add_boot_script.assert_called_once_with('iface1', 4)

    @mock.patch('wok.plugins.ginger.model.interfaces.'
                'add_config_to_mlx5_SRIOV_boot_script')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.create_interface_cfg_file')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.get_interface_list')
    @mock.patch('wok.plugins.gingerbase.netinfo.get_interface_kernel_module')
    @mock.patch('os.path.isfile')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_current_VFs')
    @mock.patch('wok.plugins.ginger.model.interfaces.InterfaceModel.'
                '_mlx5_SRIOV_get_max_VF')
    def test_mlx5_sriov_success_zero_VFs(self, mock_get_max_VF,
                                         mock_get_current_VF,
                                         mock_isfile, mock_get_module,
                                         mock_get_iface_list,
                                         mock_create_cfg_file,
                                         mock_add_boot_script):

        mock_get_max_VF.return_value = '8'
        mock_get_current_VF.return_value = '4'
        mock_get_module.return_value = 'mlx5_core'

        file1 = '/sys/class/net/%s/device/sriov_numvfs' % 'iface1'
        mock_isfile.return_value = True

        mock_get_iface_list.side_effect = [
            set(['iface1', 'iface2']),
            set(['iface1', 'sriov1', 'sriov2', 'iface2'])
        ]

        open_ = mock_open(read_data='')

        with patch.object(builtins, 'open', open_):
            iface_model = InterfaceModel(objstore=self._objstore)
            task_obj = iface_model.enable_sriov('iface1', 0)
            self.task.wait(task_obj['id'])

            finished_task = self.task.lookup(task_obj['id'])
            self.assertEquals(finished_task['status'], 'finished')
            mock_isfile.assert_called_once_with(file1)

        self.assertEqual(open_.call_args_list, [call(file1, 'w')])
        self.assertEqual(open_().write.mock_calls, [call('0\n')])
        mock_create_cfg_file.assert_not_called()
        mock_add_boot_script.assert_called_once_with('iface1', 0)

    @mock.patch('os.path.isfile')
    def test_mlx5_sriov_edit_openib_conf(self, mock_isfile):
        openib_conf_file = ifaces_utils.OPENIB_CONF_FILE
        sriov_boot_file = ifaces_utils.MLX5_SRIOV_BOOT_FILE

        conf_file_content = "OPENIBD_PRE_START\nOPENIBD_POST_START\n"\
            "OPENIBD_PRE_STOP\nOPENIBD_POST_STOP\n"

        conf_file_writelines_content = [
            "OPENIBD_PRE_START\n",
            "OPENIBD_POST_START=%s\n" % sriov_boot_file,
            "OPENIBD_PRE_STOP\n",
            "OPENIBD_POST_STOP\n"
        ]

        mock_isfile.return_value = True

        open_ = mock_open(read_data=conf_file_content)

        with patch.object(builtins, 'open', open_):
            ifaces_utils.add_mlx5_SRIOV_boot_script_in_openib_conf()
            mock_isfile.assert_called_once_with(openib_conf_file)

        self.assertEqual(
            open_.call_args_list,
            [call(openib_conf_file, 'r'), call(openib_conf_file, 'w')]
        )
        self.assertEqual(
            open_().writelines.mock_calls,
            [call(conf_file_writelines_content)]
        )

    @mock.patch('os.path.isfile')
    def test_mlx5_sriov_edit_openib_conf_notfound(self, mock_isfile):
        openib_conf_file = ifaces_utils.OPENIB_CONF_FILE

        mock_isfile.return_value = False

        with self.assertRaisesRegexp(OperationFailed, 'GINNET0088E'):
            ifaces_utils.add_mlx5_SRIOV_boot_script_in_openib_conf()
            mock_isfile.assert_called_once_with(openib_conf_file)

    @mock.patch('os.path.isfile')
    def test_mlx5_sriov_openib_conf_variable_notfound(self, mock_isfile):
        openib_conf_file = ifaces_utils.OPENIB_CONF_FILE
        sriov_boot_file = ifaces_utils.MLX5_SRIOV_BOOT_FILE

        conf_file_content = "OPENIBD_PRE_START\n"\
            "OPENIBD_PRE_STOP\nOPENIBD_POST_STOP\n"

        conf_file_write_content = "OPENIBD_POST_START=%s\n" % sriov_boot_file

        mock_isfile.return_value = True

        open_ = mock_open(read_data=conf_file_content)

        with patch.object(builtins, 'open', open_):
            ifaces_utils.add_mlx5_SRIOV_boot_script_in_openib_conf()
            mock_isfile.assert_called_once_with(openib_conf_file)

        self.assertEqual(
            open_.call_args_list,
            [call(openib_conf_file, 'r'), call(openib_conf_file, 'a')]
        )
        self.assertEqual(open_().write.mock_calls,
                         [call(conf_file_write_content)])

    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.'
                'add_mlx5_SRIOV_boot_script_in_openib_conf')
    @mock.patch('os.chmod')
    def test_mlx5_sriov_fresh_boot_script_content(self, mock_chmod,
                                                  mock_add_openib):

        ginger_boot_script = ifaces_utils.MLX5_SRIOV_BOOT_FILE

        template = """#!/bin/sh\n\
# ginger_sriov_start.sh: Connectx-4 SR-IOV init script - created by Ginger\n\
\n# %(iface)s setup\n\
echo 0 > /sys/class/net/%(iface)s/device/sriov_numvfs\n\
echo %(num_vf)s > /sys/class/net/%(iface)s/device/sriov_numvfs\n"""
        interface = 'dummyiface'
        num_vfs = '4'
        template = template % {'iface': interface, 'num_vf': num_vfs}

        open_ = mock_open(read_data='')
        with patch.object(builtins, 'open', open_):
            ifaces_utils.create_initial_mlx5_SRIOV_boot_script(interface,
                                                               num_vfs)

        self.assertEqual(
            open_.call_args_list, [call(ginger_boot_script, 'w+')]
        )
        self.assertEqual(
            open_().write.mock_calls, [call(template)]
        )
        mock_chmod.assert_called_once_with(ginger_boot_script, 0744)
        mock_add_openib.assert_called_once_with()

    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.'
                'add_mlx5_SRIOV_boot_script_in_openib_conf')
    @mock.patch('os.path.isfile')
    def test_update_mlx5_sriov_boot_script_append(self, mock_isfile,
                                                  mock_add_openib):
        ginger_boot_script = ifaces_utils.MLX5_SRIOV_BOOT_FILE
        mock_isfile.return_value = True

        initial_file = """#!/bin/sh\n\
# ginger_sriov_start.sh: Connectx-4 SR-IOV init script - created by Ginger\n\
\n# iface1 setup\n\
echo 0 > /sys/class/net/iface1/device/sriov_numvfs\n\
echo 4 > /sys/class/net/iface1/device/sriov_numvfs\n"""

        expected_writelines = [
            "#!/bin/sh\n",
            "# ginger_sriov_start.sh: Connectx-4 SR-IOV init script - "
            "created by Ginger\n", "\n",
            "# iface1 setup\n",
            "echo 0 > /sys/class/net/iface1/device/sriov_numvfs\n",
            "echo 4 > /sys/class/net/iface1/device/sriov_numvfs\n",
            "# iface2 setup\n",
            "echo 0 > /sys/class/net/iface2/device/sriov_numvfs\n",
            "echo 8 > /sys/class/net/iface2/device/sriov_numvfs\n"
        ]

        open_ = mock_open(read_data=initial_file)
        with patch.object(builtins, 'open', open_):
            ifaces_utils.add_config_to_mlx5_SRIOV_boot_script('iface2',
                                                              8)
            mock_isfile.assert_called_once_with(ginger_boot_script)

        self.assertEqual(
            open_.call_args_list, [call(ginger_boot_script, 'r+')]
        )
        self.assertEqual(
            open_().writelines.mock_calls, [call(expected_writelines)]
        )
        mock_add_openib.assert_called_once_with()

    @mock.patch('wok.plugins.ginger.model.nw_interfaces_utils.'
                'add_mlx5_SRIOV_boot_script_in_openib_conf')
    @mock.patch('os.path.isfile')
    def test_update_mlx5_sriov_script_modify_line(self, mock_isfile,
                                                  mock_add_openib):
        ginger_boot_script = ifaces_utils.MLX5_SRIOV_BOOT_FILE
        mock_isfile.return_value = True

        initial_file = """#!/bin/sh\n\
# ginger_sriov_start.sh: Connectx-4 SR-IOV init script - created by Ginger\n\
\n# iface1 setup\n\
echo 0 > /sys/class/net/iface1/device/sriov_numvfs\n\
echo 4 > /sys/class/net/iface1/device/sriov_numvfs\n\
# iface2 setup\n\
echo 0 > /sys/class/net/iface2/device/sriov_numvfs\n\
echo 6 > /sys/class/net/iface2/device/sriov_numvfs\n\
# iface3 setup\n\
echo 0 > /sys/class/net/iface3/device/sriov_numvfs\n\
echo 8 > /sys/class/net/iface3/device/sriov_numvfs\n\
# iface4 setup\n\
echo 0 > /sys/class/net/iface4/device/sriov_numvfs\n\
echo 10 > /sys/class/net/iface4/device/sriov_numvfs\n\
"""
        expected_writelines = [
            "#!/bin/sh\n",
            "# ginger_sriov_start.sh: Connectx-4 SR-IOV init script - "
            "created by Ginger\n", "\n",
            "# iface1 setup\n",
            "echo 0 > /sys/class/net/iface1/device/sriov_numvfs\n",
            "echo 4 > /sys/class/net/iface1/device/sriov_numvfs\n",
            "# iface2 setup\n",
            "echo 0 > /sys/class/net/iface2/device/sriov_numvfs\n",
            "echo 6 > /sys/class/net/iface2/device/sriov_numvfs\n",
            "# iface3 setup\n",
            "echo 0 > /sys/class/net/iface3/device/sriov_numvfs\n",
            "echo 2 > /sys/class/net/iface3/device/sriov_numvfs\n",
            "# iface4 setup\n",
            "echo 0 > /sys/class/net/iface4/device/sriov_numvfs\n",
            "echo 10 > /sys/class/net/iface4/device/sriov_numvfs\n",
        ]

        open_ = mock_open(read_data=initial_file)
        with patch.object(builtins, 'open', open_):
            ifaces_utils.add_config_to_mlx5_SRIOV_boot_script('iface3',
                                                              2)
            mock_isfile.assert_called_once_with(ginger_boot_script)

        self.assertEqual(
            open_.call_args_list, [call(ginger_boot_script, 'r+')]
        )
        self.assertEqual(
            open_().writelines.mock_calls, [call(expected_writelines)]
        )
        mock_add_openib.assert_called_once_with()
