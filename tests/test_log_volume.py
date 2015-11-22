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
import wok.plugins.ginger.models.log_volume as log_volume

from wok import config
from wok.exception import MissingParameter
from wok.objectstore import ObjectStore


class LogicalVolumesTests(unittest.TestCase):
    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

    def test_get_lv_list(self):
        lvs = log_volume.LogicalVolumesModel(objstore=self._objstore)
        lvs_list = lvs.get_list()
        self.assertGreaterEqual(len(lvs_list), 0)

    def test_create_lv_missing_vgname(self):
        lvs = log_volume.LogicalVolumesModel(objstore=self._objstore)
        size = ['10M']
        params = {'size': size}
        self.assertRaises(MissingParameter, lvs.create, params)

    def test_create_lv_missing_size(self):
        lvs = log_volume.LogicalVolumesModel(objstore=self._objstore)
        vgname = 'testvg'
        params = {'vg_name': vgname}
        self.assertRaises(MissingParameter, lvs.create, params)

    @mock.patch('wok.plugins.ginger.models.utils._create_lv', autospec=True)
    def test_create_lv(self, mock_create_lv):
        lvs = log_volume.LogicalVolumesModel(objstore=self._objstore)
        vgname = 'testvg'
        size = '10M'
        params = {'vg_name': vgname, 'size': size}
        lvs.create(params)
        mock_create_lv.assert_called_with(vgname, size)

    @mock.patch('wok.plugins.ginger.models.utils._remove_lv',
                autospec=True)
    def test_delete_lv(self, mock_delete_lv):
        lv = log_volume.LogicalVolumeModel(objstore=self._objstore)
        lvname = '/dev/testvg/lvol0'
        lv.delete(lvname)
        mock_delete_lv.assert_called_with(lvname)
