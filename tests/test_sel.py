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

import wok.plugins.ginger.model.sel as sel
from wok.exception import NotFoundError, OperationFailed

from wok import config
from wok.objectstore import ObjectStore


class SelTests(unittest.TestCase):

    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present(self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            "5 | 08/08/2016 | 11:46:06 | Event #0x5d | abc | Asserted\n",
            "",
            0]
        sels = sel.SelsModel()
        self.assertGreaterEqual(len(sels.get_list('serverpresent')), 1)

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_cmd_err(self, mock_run_command,
                                        mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["", "error", 1]
        sels = sel.SelsModel()
        self.assertRaises(OperationFailed, sels.get_list, 'serverpresent')

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_cmd_err_lookup(
            self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["", "error", 1]
        selmodel = sel.SelModel()
        self.assertRaises(
            OperationFailed,
            selmodel.lookup,
            'serverpresent',
            '1')

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_lookup(self, mock_run_command,
                                       mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            "5 | 08/08/2016 | 11:46:06 | Event #0x5d | abc | Asserted\n",
            "",
            0]
        sels = sel.SelModel()
        self.assertGreaterEqual(len(sels.lookup('serverpresent', '5')), 0)

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_lookup_error(
            self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            "5 | 08/08/2016 | 11:46:06 | Event #0x5d | abc | Asserted\n",
            "",
            0]
        sels = sel.SelModel()
        expected_error = "GINSEL00003E"
        with self.assertRaisesRegexp(NotFoundError, expected_error):
            sels.lookup('serverpresent', '1')

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_delete_error(
            self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["", "error", 1]
        sels = sel.SelModel()
        self.assertRaises(OperationFailed, sels.delete, 'serverpresent', '1')

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_delete_sucess(
            self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["deleted 5", "", 0]
        sels = sel.SelModel()
        self.assertEqual(None, sels.delete('serverpresent', '5'))

    @mock.patch('wok.plugins.ginger.model.sel.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.sel.run_command', autospec=True)
    def test_sel_server_present_e_parsing_err(
            self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = [
            "5 | 08/08/2016 | 11:46:0Event #0x5dabc | Asserted\n",
            "",
            0]
        sels = sel.SelsModel()
        self.assertRaises(OperationFailed, sels.get_list, 'serverpresent')
