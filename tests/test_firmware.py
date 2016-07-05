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
import tempfile
import unittest

from wok import config
from wok.exception import OperationFailed
from wok.objectstore import ObjectStore
from wok.model.tasks import TaskModel

from wok.plugins.ginger.model.firmware import FirmwareModel


class FirmwareTests(unittest.TestCase):

    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        self.task = TaskModel(objstore=self._objstore)

    @mock.patch('wok.plugins.ginger.model.firmware.run_command')
    def test_model_lookup(self, mock_run_command):
        return_output = "0 1 2 3 4 5 6 7 8 9 10 11 12 13"
        mock_run_command.return_value = [return_output, "", 0]
        firmware_lookup = FirmwareModel(objstore=self._objstore).lookup()
        mock_run_command.assert_called_once_with('lsmcode')
        self.assertEquals(
            firmware_lookup,
            {'level': "5 6 7 8 9 10 11 12 13"}
        )

    @mock.patch('wok.plugins.ginger.model.firmware.run_command')
    def test_model_lookup_with_product_in_output(self, mock_run_command):
        return_output = "0 1 2 3 4 Product 6 7 8 9 10 11 12 13"
        mock_run_command.return_value = [return_output, "", 0]
        firmware_lookup = FirmwareModel(objstore=self._objstore).lookup()
        mock_run_command.assert_called_once_with('lsmcode')
        self.assertEquals(firmware_lookup, {'level': '13'})

    @mock.patch('wok.plugins.ginger.model.firmware.detect_live_vm')
    def test_model_update_fails_with_running_vm(self, mock_detect_vm):
        mock_detect_vm.return_value = True
        with self.assertRaises(OperationFailed):
            FirmwareModel(objstore=self._objstore).upgrade(None, None)

    @mock.patch('wok.plugins.ginger.model.firmware.detect_live_vm')
    @mock.patch('wok.plugins.ginger.model.firmware.run_command')
    def test_model_upgrade(self, mock_run_command, mock_detect_vm):
        mock_detect_vm.return_value = False
        mock_run_command.return_value = ["", "", 0]

        temp = tempfile.NamedTemporaryFile()
        task = FirmwareModel(objstore=self._objstore).upgrade(None, temp.name)
        self.task.wait(task['id'])
        self.assertTrue(mock_run_command.called,
                        msg='Expected call to run_command. Not called')

        task_info = self.task.lookup(task['id'])
        self.assertEquals('finished', task_info['status'])
        self.assertEquals('/plugins/ginger/firmware/upgrade',
                          task_info['target_uri'])

    @mock.patch('wok.plugins.ginger.model.firmware.detect_live_vm')
    @mock.patch('wok.plugins.ginger.model.firmware.run_command')
    def test_model_upgrade_overwrite_perm_false(
        self,
        mock_run_command,
        mock_detect_vm
    ):
        mock_detect_vm.return_value = False
        mock_run_command.return_value = ["", "", 0]

        temp = tempfile.NamedTemporaryFile()
        task = FirmwareModel(objstore=self._objstore).upgrade(None, temp.name,
                                                              False)
        self.task.wait(task['id'])
        self.assertTrue(mock_run_command.called,
                        msg='Expected call to run_command. Not called')

        task_info = self.task.lookup(task['id'])
        self.assertEquals('finished', task_info['status'])
        self.assertEquals('/plugins/ginger/firmware/upgrade',
                          task_info['target_uri'])

    @mock.patch('wok.plugins.ginger.model.firmware.run_command')
    def test_model_commit(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        command = ['update_flash', '-c']
        FirmwareModel(objstore=self._objstore).commit(None)
        mock_run_command.assert_called_once_with(command)

    @mock.patch('wok.plugins.ginger.model.firmware.run_command')
    def test_model_reject(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        command = ['update_flash', '-r']
        FirmwareModel(objstore=self._objstore).reject(None)
        mock_run_command.assert_called_once_with(command)
