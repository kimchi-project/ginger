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
import wok.plugins.ginger.models.vol_group as vol_group

from wok import config
from wok.exception import MissingParameter
from wok.model.tasks import TaskModel
from wok.objectstore import ObjectStore


class VolumeGroupsTests(unittest.TestCase):
    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)
        self.task_model = TaskModel(objstore=self._objstore)

    def test_get_vg_list(self):
        vgs = vol_group.VolumeGroupsModel(objstore=self._objstore)
        vgs_list = vgs.get_list()
        self.assertGreaterEqual(len(vgs_list), 0)

    def test_create_vg_missing_name(self):
        vgs = vol_group.VolumeGroupsModel(objstore=self._objstore)
        pvpaths = ['/dev/sdb1']
        params = {'pv_paths': pvpaths}
        self.assertRaises(MissingParameter, vgs.create, params)

    def test_create_vg_missing_pvpaths(self):
        vgs = vol_group.VolumeGroupsModel(objstore=self._objstore)
        vgname = 'testvg'
        params = {'vg_name': vgname}
        self.assertRaises(MissingParameter, vgs.create, params)

    @mock.patch('wok.plugins.ginger.models.utils._create_vg', autospec=True)
    def test_create_vg(self, mock_create_vg):
        vgs = vol_group.VolumeGroupsModel(objstore=self._objstore)
        vgname = 'testvg'
        pvpaths = ['/dev/sdb1']
        params = {'vg_name': vgname, 'pv_paths': pvpaths}
        task_obj = vgs.create(params)
        self.task_model.wait(task_obj.get('id'))
        mock_create_vg.assert_called_with(vgname, pvpaths)

    @mock.patch('wok.plugins.ginger.models.utils._extend_vg', autospec=True)
    def test_extend_vg(self, mock_extend_vg):
        vg = vol_group.VolumeGroupModel(objstore=self._objstore)
        vgname = 'testvg'
        pvpaths = ['/dev/sdb2']
        vg.extend(vgname, pvpaths)
        mock_extend_vg.assert_called_with(vgname, pvpaths)

    @mock.patch('wok.plugins.ginger.models.utils._reduce_vg', autospec=True)
    def test_reduce_vg(self, mock_reduce_vg):
        vg = vol_group.VolumeGroupModel(objstore=self._objstore)
        vgname = 'testvg'
        pvpaths = ['/dev/sdb2']
        vg.reduce(vgname, pvpaths)
        mock_reduce_vg.assert_called_with(vgname, pvpaths)

    @mock.patch('wok.plugins.ginger.models.utils._remove_vg',
                autospec=True)
    def test_delete_vg(self, mock_delete_vg):
        vg = vol_group.VolumeGroupModel(objstore=self._objstore)
        vgname = 'testvg'
        vg.delete(vgname)
        mock_delete_vg.assert_called_with(vgname)
