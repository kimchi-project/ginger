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
