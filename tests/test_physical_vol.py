#
# Project Ginger
#
# Copyright IBM, Corp. 2015-2016
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
import wok.plugins.ginger.model.physical_vol as physical_vol

from wok import config
from wok.exception import MissingParameter, NotFoundError, OperationFailed
from wok.objectstore import ObjectStore
from wok.plugins.ginger.model import utils


class PhysicalVolumeTests(unittest.TestCase):
    def setUp(self):
        objstore_loc = config.get_object_store() + '_ginger'
        self._objstore = ObjectStore(objstore_loc)

    def test_get_pv_list(self):
        pvs = physical_vol.PhysicalVolumesModel(objstore=self._objstore)
        pvs_list = pvs.get_list()
        self.assertGreaterEqual(len(pvs_list), 0)

    def test_create_pv_missing_name(self):
        pvs = physical_vol.PhysicalVolumesModel(objstore=self._objstore)
        params = {}
        self.assertRaises(MissingParameter, pvs.create, params)

    @mock.patch('wok.plugins.ginger.model.utils._remove_pv',
                autospec=True)
    def test_delete_pv(self, mock_delete_pv):
        pv = physical_vol.PhysicalVolumeModel(objstore=self._objstore)
        pvname = '/dev/sdb1'
        pv.delete(pvname)
        mock_delete_pv.assert_called_with(pvname)

    def test_pv_list_parser(self):
        input_text = """PV
  /dev/mapper/luks-92ee4956-3fd1-47fa-a603-9b8ad867f66d
  /dev/sdb1"""
        pv_list = utils.parse_pvlist_output(input_text)
        self.assertEqual(pv_list[1], '/dev/sdb1')

    def test_pv_disp_parser(self):
        input_test = """--- NEW Physical volume ---
  PV Name               /dev/sdb1
  VG Name
  PV Size               20.00 MiB
  Allocatable           NO
  PE Size               0
  Total PE              0
  Free PE               0
  Allocated PE          0
  PV UUID               NMLPlg-ozfg-pFuJ-Q0ld-rvqb-KAda-4MywSM"""
        pv_out = utils.parse_pvdisplay_output(input_test)
        self.assertEqual(pv_out['PV Name'], '/dev/sdb1')
        self.assertEqual(pv_out['PV Size'], '20.00 MiB')
        self.assertEqual(pv_out['Allocatable'], 'NO')
        self.assertEqual(pv_out['PV UUID'],
                         'NMLPlg-ozfg-pFuJ-Q0ld-rvqb-KAda-4MywSM')

    @mock.patch('wok.plugins.ginger.model.utils.run_command', autospec=True)
    def test_utils_remove_pv_returns_404_if_vol_not_found(
            self, mock_run_command):

        mock_run_command.return_value = ['', '  Device fake_dev not found', 5]

        expected_error = "GINPV00010E: GINPV00010E"
        with self.assertRaisesRegexp(NotFoundError, expected_error):
            utils._remove_pv('fake_dev')
            mock_run_command.assert_called_once_with(
                ['pvremove', '-f', 'fake_dev']
            )

    @mock.patch('wok.plugins.ginger.model.utils.run_command', autospec=True)
    def test_utils_remove_pv_returns_500_if_unknown_error(
            self, mock_run_command):

        mock_run_command.return_value = ['', '', 1]

        expected_error = "GINPV00009E: GINPV00009E"
        with self.assertRaisesRegexp(OperationFailed, expected_error):
            utils._remove_pv('fake_dev')
            mock_run_command.assert_called_once_with(
                ['pvremove', '-f', 'fake_dev']
            )

    @mock.patch('wok.plugins.ginger.model.utils.run_command', autospec=True)
    def test_utils_pvdisplay_returns_404_if_vol_not_found(
            self, mock_run_command):

        mock_run_command.return_value = [
            '',
            'Failed to find device for physical volume',
            5
        ]

        expected_error = "GINPV00011E: GINPV00011E"
        with self.assertRaisesRegexp(NotFoundError, expected_error):
            utils._pvdisplay_out('fake_dev')
            mock_run_command.assert_called_once_with(
                ['pvdisplay', 'fake_dev']
            )

    @mock.patch('wok.plugins.ginger.model.utils.run_command', autospec=True)
    def test_utils_pvdisplay_returns_500_if_unknown_error(
            self, mock_run_command):

        mock_run_command.return_value = ['', '', 1]

        expected_error = "GINPV00007E: GINPV00007E"
        with self.assertRaisesRegexp(OperationFailed, expected_error):
            utils._pvdisplay_out('fake_dev')
            mock_run_command.assert_called_once_with(
                ['pvdisplay', 'fake_dev']
            )
