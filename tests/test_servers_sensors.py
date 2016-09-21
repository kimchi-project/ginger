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

from wok.exception import OperationFailed
from wok import config
from wok.objectstore import ObjectStore
import wok.plugins.ginger.model.servers_sensors as sdr


class SdrsTests(unittest.TestCase):

    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    def test_sdr_failure(self, mock_get_config):
        mock_get_config.return_value = []
        sdrs = sdr.ServerSensorsModel()
        self.assertRaises(OperationFailed, sdrs.get_list, 'server1')

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers_sensors.run_command',
                autospec=True)
    @mock.patch('os.path.isfile', autospec=True)
    def test_sdr_server_present_cache_absent(self, mock_os, mock_run_command,
                                             mock_get_config):
        mock_os.return_value = False
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        if(mock_run_command.call_count == 1):
            mock_run_command.return_value = [
                "",
                "",
                0]
        else:
            mock_run_command.return_value = [
                " Fan1 Speed Front | 36h | ok  | 29.1 | 2700 RPM\n",
                "",
                0]
        sdrs = sdr.ServerSensorsModel()
        self.assertGreaterEqual(len(sdrs.get_list('serverpresent')), 1)
        assert mock_run_command.call_count == 2

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers_sensors.run_command',
                autospec=True)
    @mock.patch('os.path.isfile', autospec=True)
    def test_sdr_server_present_cache_present(self, mock_os, mock_run_command,
                                              mock_get_config):
        mock_os.return_value = True
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            " Fan1 Speed Front | 36h | ok  | 29.1 | 2700 RPM\n",
            "",
            0]
        sdrs = sdr.ServerSensorsModel()
        self.assertGreaterEqual(len(sdrs.get_list('serverpresent')), 1)

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers_sensors.run_command',
                autospec=True)
    @mock.patch('os.path.isfile', autospec=True)
    def test_sdr_server_present_cmd_err(self, mock_os, mock_run_command,
                                        mock_get_config):
        mock_os.return_value = True
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["", "error", 1]
        sdrs = sdr.ServerSensorsModel()
        self.assertRaises(OperationFailed, sdrs.get_list, 'serverpresent')

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers_sensors.run_command',
                autospec=True)
    @mock.patch('os.path.isfile', autospec=True)
    def test_sdr_with_query_param(self, mock_os, mock_run_command,
                                  mock_get_config):
        mock_os.return_value = True
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            " Fan1 Speed Front | 36h | ok  | 29.1 | 2700 RPM\n",
            "",
            0]
        sdrs = sdr.ServerSensorsModel()
        self.assertGreaterEqual(len(sdrs.get_list('serverpresent', 'Fan')), 1)

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers_sensors.run_command',
                autospec=True)
    @mock.patch('os.path.isfile', autospec=True)
    def test_sdr_with_query_param_failure(self, mock_os, mock_run_command,
                                          mock_get_config):
        mock_os.return_value = True
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            " Fan1 Speed Front | 36h | ok  | 29.1 | 2700 RPM\n",
            "",
            0]
        sdrs = sdr.ServerSensorsModel()
        self.assertRaises(
            OperationFailed,
            sdrs.get_list,
            'serverpresent',
            'invalidqueryparam')

    @mock.patch('wok.plugins.ginger.model.servers_sensors.get_config',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.servers_sensors.run_command',
                autospec=True)
    @mock.patch('os.path.isfile', autospec=True)
    def test_sdr_parsing_error(self, mock_os, mock_run_command,
                               mock_get_config):
        mock_os.return_value = True
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            " Fan1 Speed Front |||| 36h | ok  | 29.1 | 2700 RPM\n",
            "",
            0]
        sdrs = sdr.ServerSensorsModel()
        self.assertRaises(
            OperationFailed,
            sdrs.get_list,
            'serverpresent',
            'invalidqueryparam')
