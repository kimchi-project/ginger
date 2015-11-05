#
# Project Ginger
#
# Copyright IBM, Corp. 2015
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

from plugins.ginger.models.interfaces import InterfaceModel
from wok.exception import OperationFailed


class InterfacesTests(unittest.TestCase):

    @mock.patch('plugins.ginger.models.interfaces.run_command')
    def test_activate(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        interface = "test_eth0"
        cmd = ['ifup', '%s' % interface]
        InterfaceModel().activate(interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('plugins.ginger.models.interfaces.run_command')
    def test_activate_fail(self, mock_run_command):
        mock_run_command.return_value = ["", "Unable to activate", 1]
        interface = "test_eth0"
        cmd = ['ifup', '%s' % interface]
        self.assertRaises(OperationFailed, InterfaceModel().activate,
                          interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('plugins.ginger.models.interfaces.run_command')
    def test_deactivate(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        interface = "test_eth0"
        cmd = ['ifdown', '%s' % interface]
        InterfaceModel().deactivate(interface)
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('plugins.ginger.models.interfaces.run_command')
    def test_deactivate_fail(self, mock_run_command):
        mock_run_command.return_value = ["", "Unable to deactivate", 1]
        interface = "test_eth0"
        cmd = ['ifdown', '%s' % interface]
        self.assertRaises(OperationFailed, InterfaceModel().deactivate,
                          interface)
        mock_run_command.assert_called_once_with(cmd)
