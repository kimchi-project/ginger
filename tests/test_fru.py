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

import wok.plugins.ginger.model.fru as fru
from wok.exception import NotFoundError, OperationFailed

from wok import config
from wok.objectstore import ObjectStore


class FruTests(unittest.TestCase):

    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

    @mock.patch('wok.plugins.ginger.model.fru.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fru.run_command', autospec=True)
    def test_fru_server_present(self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["""FRU Device Description : D (ID 10)
                                        Product Name          : P8DTU-IBM-2

                                        FRU Device Description : CPU 1 (ID 11)
                                        Board Mfg             : IBM
                                        Board Product         : PROCESSOR DULE
                                        Board Serial          : YA1933199124
                                        Board Part Number     : 00UL864
                                        Board Extra           : ECID:019A0077
                                        Board Extra           : EC""", "", 0]
        frus = fru.FrusModel()
        self.assertGreaterEqual(len(frus.get_list('serverpresent')), 1)

    @mock.patch('wok.plugins.ginger.model.fru.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fru.run_command', autospec=True)
    def test_fru_server_absent(self, mock_run_command, mock_get_config):
        e = OperationFailed("exception")
        mock_get_config.side_effect = e
        mock_run_command.return_value = ["""FRU Device Description : D (ID 10)
                                        Product Name          : P8DTU-IBM-2

                                        FRU Device Description : CPU 1 (ID 11)
                                        Board Mfg             : IBM
                                        Board Product         : PROCESR MODULE
                                        Board Serial          : YA1933199124
                                        Board Part Number     : 00UL864
                                        Board Extra           : ECID:00553C82
                                        Board Extra           : EC""", "", 0]
        frus = fru.FrusModel()
        self.assertRaises(OperationFailed, frus.get_list, 'serverabsent')

    @mock.patch('wok.plugins.ginger.model.fru.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fru.run_command', autospec=True)
    def test_fru_cmd_error(self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["""FRU Device Description : D (ID 0)
                                        Product Name          : P8DTU-IBM-2

                                        FRU Device Description : CPU 1 (ID 1)
                                        Board Mfg Date        : Mon  1996
                                        Board Mfg             : IBM
                                        Board Product         : PROCSOR MODULE
                                        Board Serial          : YA1933199124
                                        Board Part Number     : 00UL864
                                        Board Extra           : ECID:00553C82
                                        Board Extra           : EC""", "e", 1]
        frus = fru.FrusModel()
        self.assertRaises(OperationFailed, frus.get_list, 'serverpresent')

    @mock.patch('wok.plugins.ginger.model.fru.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fru.run_command', autospec=True)
    def test_fru_parsing_error(self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["""FRU Device Description : D (ID 0)
                                        Product Name          : P8DTU-IBM-2

                                        FRU Device DescriptionCPU 1 (ID 1)
                                        Board Mfg Date        : Mon  1996
                                        Board Mfg             : IBM
                                        Board Product         : PROCSOR MODULE
                                        Board Serial          : YA1933199124
                                        Board Part Number     : 00UL864
                                        Board Extra           : ECID:00553C82
                                        Board Extra           : EC""", "", 0]
        frus = fru.FrusModel()
        self.assertRaises(OperationFailed, frus.get_list, 'serverpresent')

    @mock.patch('wok.plugins.ginger.model.fru.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fru.run_command', autospec=True)
    def test_fru_lookup_success(self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["""FRU Device Description : D (ID 10)
                                        Product Name          : P8DTU-IBM-2

                                        FRU Device Description : CPU 1 (ID 11)
                                        Board Mfg Date        : Mon 1996
                                        Board Mfg             : IBM
                                        Board Product         : PROCSOR MODULE
                                        Board Serial          : YA1933199124
                                        Board Part Number     : 00UL864
                                        Board Extra           : ECID:00553C82
                                        Board Extra           : EC""", "", 0]
        frus = fru.FruModel()
        self.assertGreaterEqual(len(frus.lookup('serverpresent', '11')), 1)

    @mock.patch('wok.plugins.ginger.model.fru.get_config', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fru.run_command', autospec=True)
    def test_fru_lookup_not_present(self, mock_run_command, mock_get_config):
        mock_get_config.return_value = {
            u'username': u'',
            u'status': u'up',
            u'password': u'WA4M7if4b+9GDqZ0H/ShlA==',
            u'ipaddr': u'127.0.0.0',
            u'name': u'serverpresent',
            u'salt': u'tNqVtx7lQxJGpjOE'}
        mock_run_command.return_value = ["""FRU Device Description : D (ID 10)
                                        Product Name          : P8DTU-IBM-2

                                        FRU Device Description : CPU 1 (ID 11)
                                        Board Mfg Date        : Mon 1996
                                        Board Mfg             : IBM
                                        Board Product         : PROCSOR MODULE
                                        Board Serial          : YA1933199124
                                        Board Part Number     : 00UL864
                                        Board Extra           : ECID:00553C82
                                        Board Extra           : EC""", "", 0]
        frus = fru.FruModel()
        self.assertRaises(NotFoundError, frus.lookup, 'serverpresent', 5)
