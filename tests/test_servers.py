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

import mock
import unittest

import wok.plugins.ginger.model.servers as servers

from wok.exception import OperationFailed, MissingParameter, InvalidParameter


class ServerOperationTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_add_server_without_username(self, mock_run_command):
        server = servers.ServersModel()
        rc = 0
        mock_run_command.return_value = [
            "System Power : off\nPower Overload : false\n",
            "",
            rc]
        params = {
            u'password': u'baremetal',
            u'ipaddr': u'127.0.0.2',
            u'name': u'def'}
        resp = server.create(params)
        self.assertEquals('def', resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_add_server(self, mock_run_command):
        server = servers.ServersModel()
        rc = 0
        mock_run_command.return_value = [
            "System Power : off\nPower Overload : false\n",
            "",
            rc]
        params = {
            u'username': u'Interns',
            u'password': u'baremetal',
            u'ipaddr': u'127.0.0.1',
            u'name': u'abc'}
        resp = server.create(params)
        self.assertEquals('abc', resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_add_server_failed(self, mock_run_command):
        server = servers.ServersModel()
        mock_run_command.return_value = [
            "",
            "Error sending Chassis Status command",
            "1"]
        params = {
            u'username': u'Interns',
            u'password': u'wrong_pass',
            u'ipaddr': u'127.0.0.1',
            u'name': u'abc'}
        self.assertRaises(OperationFailed, server.create, params)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_lookup_server(self, mock_run_command):
        server = servers.ServerModel()
        rc = 0
        mock_run_command.return_value = [
            "System Power : off\nPower Overload : false\n",
            "",
            rc]
        resp = server.lookup('abc')
        info = {
            'name': 'abc',
            'ipaddr': '127.0.0.1',
            'status': 'off',
        }
        self.assertEquals(info, resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_server_power_on(self, mock_run_command):
        rc = 0
        server = servers.ServerModel()
        if(mock_run_command.call_count == 1):
            mock_run_command.return_value = [
                "System Power : off\nPower Overload : false\n",
                "",
                rc]
        else:
            mock_run_command.return_value = [
                "System Power : on\nPower Overload : false\n",
                "",
                rc]
        resp = server.poweron('abc')
        self.assertEquals(None, resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_server_power_off(self, mock_run_command):
        server = servers.ServerModel()
        rc = 0
        if(mock_run_command.call_count == 1):
            mock_run_command.return_value = [
                "System Power : on\nPower Overload : false\n",
                "",
                rc]
        else:
            mock_run_command.return_value = [
                "System Power : off\nPower Overload : false\n",
                "",
                rc]
        resp = server.poweroff('abc')
        self.assertEquals(None, resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_server_power_on_failure(self, mock_run_command):
        rc = 0
        server = servers.ServerModel()
        if(mock_run_command.call_count == 1):
            mock_run_command.return_value = [
                "System Power : off\nPower Overload : false\n",
                "",
                rc]
        else:
            rc = 1
            mock_run_command.return_value = [
                "System Power : on\nPower Overload : false\n",
                "",
                rc]
        self.assertRaises(OperationFailed, server.poweron, 'abc')

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    def test_server_power_off_failure(self, mock_run_command):
        server = servers.ServerModel()
        rc = 0
        if(mock_run_command.call_count == 1):
            mock_run_command.return_value = [
                "System Power : on\nPower Overload : false\n",
                "",
                rc]
        else:
            rc = 1
            mock_run_command.return_value = [
                "System Power : off\nPower Overload : false\n",
                "",
                rc]
        self.assertRaises(OperationFailed, server.poweroff, 'abc')

    def test_server_remove(self):
        server1 = servers.ServerModel()
        resp = server1.delete('abc')
        self.assertEquals(None, resp)

    def test_server_remove_without_username(self):
        server1 = servers.ServerModel()
        resp = server1.delete('def')
        self.assertEquals(None, resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers.get_config', autospec=True)
    def test_update_server(self, mock_get_config, mock_run_command):
        server = servers.ServerModel()
        rc = 0
        mock_get_config.return_value = {
            u'username': u'Interns',
            u'password': u'baremetal',
            u'ipaddr': u'127.0.0.1',
            u'name': u'abc'}
        mock_run_command.return_value = [
            "System Power : on\nPower Overload : false\n", "", rc]
        params = {
            u'username': u'Interns',
            u'password': u'baremetal'}
        name = 'abc'
        resp = server.update(name, params)
        self.assertEquals('abc', resp)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers.get_config', autospec=True)
    def test_update_server_failure(self, mock_get_config, mock_run_command):
        server = servers.ServerModel()
        rc = 1
        mock_get_config.return_value = {
            u'username': u'Interns',
            u'password': u'baremetal',
            u'ipaddr': u'127.0.0.1',
            u'name': u'abc'}
        mock_run_command.return_value = [
            "System Power : off\nPower Overload : false\n",
            "",
            rc]
        params = {
            u'username': u'Interns',
            u'password': u'wrong_pass'}
        name = 'abc'
        self.assertRaises(OperationFailed, server.update,
                          name, params)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers.get_config', autospec=True)
    def test_update_server_invalidparam(self,
                                        mock_get_config, mock_run_command):
        server = servers.ServerModel()
        rc = 1
        mock_get_config.return_value = {
            u'username': u'Interns',
            u'password': u'baremetal',
            u'ipaddr': u'127.0.0.1',
            u'name': u'abc'}
        mock_run_command.return_value = [
            "System Power : off\nPower Overload : false\n",
            "",
            rc]
        params = {
            u'username': u'Interns',
            u'password': u'wrong_pass',
            u'name': u'abc'}
        name = 'abc'
        self.assertRaises(InvalidParameter, server.update,
                          name, params)

    @mock.patch('wok.plugins.ginger.model.servers.run_command', autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers.get_config', autospec=True)
    def test_update_server_without_pass(self,
                                        mock_get_config, mock_run_command):
        server = servers.ServerModel()
        rc = 1
        mock_get_config.return_value = {
            u'username': u'Interns',
            u'password': u'baremetal',
            u'ipaddr': u'127.0.0.1',
            u'name': u'abc'}
        mock_run_command.return_value = [
            "System Power : off\nPower Overload : false\n",
            "",
            rc]
        params = {
            u'username': u'Interns'}
        name = 'abc'
        self.assertRaises(MissingParameter, server.update,
                          name, params)
