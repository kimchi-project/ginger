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

import mock
import unittest

import wok.plugins.ginger.model.netinfo as netinfo

from wok.exception import OperationFailed
from wok.plugins.ginger.model.interfaces import InterfaceModel


class InterfacesTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.interfaces.run_command')
    def test_activate(self, mock_run_command, mock_get_interface_type):
        mock_run_command.return_value = ["", "", 0]
        mock_get_interface_type.return_value = "Ethernet"
        interface = "test_eth0"
        calls = [(['ip', 'link', 'set', '%s' % interface, 'up'],),
                 (['ifup', '%s' % interface],)]
        InterfaceModel().activate(interface)
        for i in range(0, 1):
            x, y = mock_run_command.call_args_list[i]
            assert x == calls[i]
        assert mock_run_command.call_count == 2

    @mock.patch('wok.plugins.ginger.model.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.interfaces.run_command')
    def test_activate_fail(self, mock_run_command, mock_get_interface_type):
        mock_run_command.return_value = ["", "Unable to activate", 1]
        mock_get_interface_type.return_value = "Ethernet"
        interface = "test_eth0"
        cmd = ['ip', 'link', 'set', '%s' % interface, 'up']
        self.assertRaises(OperationFailed, InterfaceModel().activate,
                          interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.interfaces.run_command')
    def test_deactivate(self, mock_run_command, mock_get_interface_type):
        mock_run_command.return_value = ["", "", 0]
        mock_get_interface_type.return_value = "Ethernet"
        interface = "test_eth0"
        calls = [(['ifdown', '%s' % interface],),
                 (['ip', 'link', 'set', '%s' % interface, 'down'],)]
        InterfaceModel().deactivate(interface)
        for i in range(0, 1):
            x, y = mock_run_command.call_args_list[i]
            assert x == calls[i]
        assert mock_run_command.call_count == 2

    @mock.patch('wok.plugins.ginger.model.netinfo.get_interface_type')
    @mock.patch('wok.plugins.ginger.model.interfaces.run_command')
    def test_deactivate_fail(self, mock_run_command, mock_get_interface_type):
        mock_run_command.return_value = ["", "Unable to deactivate", 1]
        mock_get_interface_type.return_value = "Ethernet"
        interface = "test_eth0"
        cmd = ['ifdown', '%s' % interface]
        self.assertRaises(OperationFailed, InterfaceModel().deactivate,
                          interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.netinfo.get_loaded_modules_list')
    @mock.patch('os.readlink')
    def test_netinfo_interface_module_lookup_success(
        self, mock_readlink, mock_loaded_mod_list
    ):
        mock_loaded_mod_list.return_value = [
            'mod1', 'mod2', 'dummy_net_module', 'mod3', 'mod4'
        ]
        mock_readlink.return_value = '../../../../module/dummy_net_module'

        module = netinfo.get_interface_kernel_module('dummy_iface')
        mock_loaded_mod_list.assert_called_once_with()
        mock_readlink.assert_called_once_with(
           '/sys/class/net/dummy_iface/device/driver/module'
        )

        self.assertEqual(module, 'dummy_net_module')

    @mock.patch('wok.plugins.ginger.model.netinfo.get_loaded_modules_list')
    @mock.patch('os.readlink')
    def test_netinfo_module_lookup_not_loaded_unknown(
        self, mock_readlink, mock_loaded_mod_list
    ):
        mock_loaded_mod_list.return_value = ['mod1', 'mod2', 'mod3', 'mod4']
        mock_readlink.return_value = '../../../../module/dummy_net_module'

        module = netinfo.get_interface_kernel_module('dummy_iface')
        self.assertEqual(module, 'unknown')
        mock_readlink.assert_called_once_with(
           '/sys/class/net/dummy_iface/device/driver/module'
        )
        mock_loaded_mod_list.assert_called_once_with()

    @mock.patch('wok.plugins.ginger.model.netinfo.get_interface_kernel_module')
    @mock.patch('ethtool.get_devices')
    @mock.patch('ethtool.get_ipaddr')
    @mock.patch('ethtool.get_netmask')
    @mock.patch('wok.plugins.ginger.model.netinfo.macaddr')
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
