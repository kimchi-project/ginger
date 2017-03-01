#
# Project Ginger
#
# Copyright IBM Corp, 2015-2017
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
import wok.plugins.ginger.model.diskparts as diskparts

import tests.utils as utils

from wok import config
from wok.exception import MissingParameter, NotFoundError
from wok.model.tasks import TaskModel
from wok.objectstore import ObjectStore


class PartitionTests(unittest.TestCase):
    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        self.task_model = TaskModel(objstore=self._objstore)

    @unittest.skipUnless(utils.running_as_root(), 'Must be run as root')
    def test_get_part_list(self):
        parts = diskparts.PartitionsModel()
        parts_list = parts.get_list()
        self.assertGreaterEqual(len(parts_list), 0)

    def test_create_part_missing_device(self):
        parts = diskparts.PartitionsModel()
        size = 10
        params = {'partsize': size}
        self.assertRaises(MissingParameter, parts.create, params)

    def test_create_part_missing_size(self):
        parts = diskparts.PartitionsModel()
        dev = '/dev/sdb'
        params = {'devname': dev}
        self.assertRaises(MissingParameter, parts.create, params)

    @mock.patch('wok.plugins.ginger.model.utils.create_disk_part',
                autospec=True)
    def test_create_part(self, mock_create_part):
        parts = diskparts.PartitionsModel()
        dev = '/dev/sdb'
        size = 10
        params = {'devname': dev, 'partsize': size}
        parts.create(params)
        mock_create_part.return_value = 'sdb1'
        mock_create_part.assert_called_with(dev, size)

    @mock.patch('wok.plugins.ginger.model.utils.change_part_type',
                autospec=True)
    def test_change_part_type(self, mock_change_type):
        part = diskparts.PartitionModel(objstore=self._objstore)
        part_name = 'sdb1'
        type = '82'
        mock_change_type.return_value = 'sdb1'
        part.change_type(part_name, type)
        mock_change_type.assert_called_with(part_name, type)

    @mock.patch('wok.plugins.ginger.model.utils.delete_part',
                autospec=True)
    def test_delete_part(self, mock_delete_part):
        part = diskparts.PartitionModel(objstore=self._objstore)
        part_name = 'sdb1'
        part.delete(part_name)
        mock_delete_part.assert_called_with(part_name)

    @mock.patch('wok.plugins.ginger.model.utils._makefs', autospec=True)
    @mock.patch('wok.plugins.ginger.model.utils._is_mntd', autospec=True)
    def test_format_part(self, mock_is_mntd, mock_makefs):
        mock_is_mntd.return_value = False
        part = diskparts.PartitionModel(objstore=self._objstore)
        name = 'a_partition_name'
        fstype = 'ext4'
        task_obj = part.format(name, fstype)
        self.task_model.wait(task_obj.get('id'))
        mock_makefs.assert_called_with(fstype, name)

    @mock.patch('wok.plugins.ginger.model.diskparts.get_partition_details',
                autospec=True)
    def test_lookup_invalid_part_returns_404(self, mock_get_part_details):
        mock_get_part_details.side_effect = iter([NotFoundError])

        part = diskparts.PartitionModel(objstore=self._objstore)

        with self.assertRaises(NotFoundError):
            part.lookup('/a/invalid/partition')
