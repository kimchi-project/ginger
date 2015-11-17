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

import wok.plugins.ginger.models.swaps as swaps

from wok import config
from wok.exception import InvalidParameter
from wok.objectstore import ObjectStore
from wok.plugins.ginger.models import utils


class SwapTests(unittest.TestCase):
    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

    @mock.patch('wok.plugins.ginger.models.swaps.wok_log')
    @mock.patch('wok.plugins.ginger.models.swaps.add_task')
    @mock.patch('wok.plugins.ginger.models.swaps.TaskModel')
    def test_create_swap_missing_file_loc(self, mock_task_model,
                                          mock_add_task, mock_wok_log):
        """
        Test case to raise exception in case of
        missing file location in parameters
        """
        taskid = 1
        mock_add_task.return_value = taskid
        mock_task_model.lookup.return_value = "test_task"

        params = {}

        params['type'] = 'file'
        params['size'] = '10M'

        swap_model = swaps.SwapsModel(objstore=self._objstore)
        self.assertRaises(InvalidParameter, swap_model.create, params)
        self.assertFalse(mock_add_task.called,
                         msg='Unexpected call to mock_add_task()')
        msg = "File location required for creating a swap device."
        mock_wok_log.error.assert_called_once_with(msg)

    @mock.patch('wok.plugins.ginger.models.swaps.wok_log')
    @mock.patch('wok.plugins.ginger.models.swaps.add_task')
    @mock.patch('wok.plugins.ginger.models.swaps.TaskModel')
    def test_create_swap_missing_type(self, mock_task_model,
                                      mock_add_task, mock_wok_log):
        """
        Test case to raise exception in case of missing type in parameters
        """
        taskid = 1
        mock_add_task.return_value = taskid
        mock_task_model.lookup.return_value = "test_task"

        params = {}

        params['file_loc'] = '/myswap'
        params['size'] = '10M'

        swap_model = swaps.SwapsModel(objstore=self._objstore)
        self.assertRaises(InvalidParameter, swap_model.create, params)
        self.assertFalse(mock_add_task.called,
                         msg='Unexpected call to mock_add_task()')
        msg = "Type required for creating a swap device."
        mock_wok_log.error.assert_called_once_with(msg)

    @mock.patch('wok.plugins.ginger.models.swaps.wok_log')
    @mock.patch('wok.plugins.ginger.models.swaps.add_task')
    @mock.patch('wok.plugins.ginger.models.swaps.TaskModel')
    def test_create_swap_missing_size(self, mock_task_model,
                                      mock_add_task, mock_wok_log):
        """
        Test case to raise exception in case of
        missing size in parameters for type 'file'
        """
        taskid = 1
        mock_add_task.return_value = taskid
        mock_task_model.lookup.return_value = "test_task"

        params = {}

        params['file_loc'] = '/myswap'
        params['type'] = 'file'

        swap_model = swaps.SwapsModel(objstore=self._objstore)
        self.assertRaises(InvalidParameter, swap_model.create, params)
        self.assertFalse(mock_add_task.called,
                         msg='Unexpected call to mock_add_task()')
        msg = "Size is required file type swap device."
        mock_wok_log.error.assert_called_once_with(msg)

    @mock.patch('wok.plugins.ginger.models.swaps.wok_log')
    @mock.patch('wok.plugins.ginger.models.swaps.add_task')
    @mock.patch('wok.plugins.ginger.models.swaps.TaskModel')
    def test_create_swap_wrong_type(self, mock_task_model,
                                    mock_add_task, mock_wok_log):
        """
        Test case to raise exception in case of wrong type
        """
        taskid = 1
        mock_add_task.return_value = taskid
        mock_task_model.lookup.return_value = "test_task"

        params = {}

        params['file_loc'] = '/myswap'
        params['type'] = 'funny'
        params['size'] = '10M'

        swap_model = swaps.SwapsModel(objstore=self._objstore)
        self.assertRaises(InvalidParameter, swap_model.create, params)
        self.assertFalse(mock_add_task.called,
                         msg='Unexpected call to mock_add_task()')
        msg = "Incorrect swap type."
        mock_wok_log.error.assert_called_once_with(msg)

    def test_swap_parser(self):
        """
        Test case for parsing individual swap devices
        from /proc/swaps. Used by 'lookup' method of the SwapModel.
        """
        input_text = '/myswap          file		10236	72	-1'

        output_dict = utils._parse_swapon_output(input_text)
        self.assertEqual(output_dict['priority'], '-1')
        self.assertEqual(output_dict['size'], '10236')
        self.assertEqual(output_dict['type'], 'file')
        self.assertEqual(output_dict['used'], '72')
        self.assertEqual(output_dict['filename'], '/myswap')

    def test_swap_dev_list_parser(self):
        """
        Test case for parsing /proc/swaps.
        This parser is used by 'get_list' of the SwapsModel.
        """
        input_text = """Filename				Type		Size	Used	Priority
/myswap                                 file		10236	72	-1
"""
        dev_list = utils._get_swapdev_list_parser(input_text)
        self.assertEqual(dev_list[0], '/myswap')
