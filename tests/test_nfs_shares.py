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

from wok.exception import NotFoundError

import wok.plugins.ginger.model.nfsshares as nfsshares


class NFSSharesUnitTests(unittest.TestCase):
    """
    Unit tests for NFS shares
    """
    @mock.patch('wok.utils.patch_find_nfs_target', autospec=True)
    def test_list_nfs_targets_for_invalid_server(self, mock_find_nfs_target):
        """
        unittest to validate get_list method with invalid server
        mock_find_nfs_target: mock of patch_find_nfs_target in wok utils
        """
        mock_find_nfs_target.return_value = []
        nfs = nfsshares.NFSSharesModel()
        self.assertRaises(NotFoundError, nfs.get_list, 'abc')

    @mock.patch('wok.plugins.ginger.model.nfsshares.patch_find_nfs_target',
                autospec=True)
    @mock.patch('wok.plugins.ginger.model.fs_utils._get_df_output',
                autospec=True)
    def test_list_nfs_targets(self, mock_df_out, mock_find_nfs_target):
        """
        unittest to validate get_list method
        mock_find_nfs_target: mock of patch_find_nfs_target in wok utils
        """
        mock_find_nfs_target.return_value = [{'type': 'nfsgh',
                                              'target': '/var/ftp/newnfsgh',
                                              'host_name': u'localhost'},
                                             {'type': 'nfs',
                                              'target': '/var/ftp/nfs1',
                                              'host_name': u'localhost'}]
        mock_df_out.return_value = [{'use%': '0%', 'used': '0',
                                     'mounted_on': '/dev', 'avail': 3875092,
                                     'filesystem': 'devtmpfs',
                                     'type': 'devtmpfs', 'size': 3875092},
                                    {'use%': '67%', 'used': '32528200',
                                     'mounted_on': '/', 'avail': 16309044,
                                     'filesystem': '/dev/mapper/fedora-root',
                                     'type': 'ext4', 'size': 51475068},
                                    {'use%': '2%', 'used': '48304',
                                     'mounted_on': '/tmp', 'avail': 3837796,
                                     'filesystem': 'tmpfs', 'type': 'tmpfs',
                                     'size': 3886100},
                                    {'use%': '36%', 'used': '162815',
                                     'mounted_on': '/boot', 'avail': 295141,
                                     'filesystem': '/dev/sda1', 'type': 'ext4',
                                     'size': 487652},
                                    {'use%': '29%', 'used': '67553456',
                                     'mounted_on': '/home',
                                     'avail': 167458844,
                                     'filesystem': '/dev/mapper/fedora-home',
                                     'type': 'ext4', 'size': 247613436},
                                    {'use%': '67%', 'used': '32528384',
                                     'mounted_on':
                                     '/var/lib/kimchi/nfs_mount/testnfs',
                                     'avail': 16309248,
                                     'filesystem': 'localhost:/var/ftp/nfs1',
                                     'type': 'nfs4', 'size': 51475456},
                                    {'use%': '1%', 'used': '24',
                                     'mounted_on': '/run/user/1000',
                                     'avail': 777200,
                                     'filesystem': 'tmpfs',
                                     'type': 'tmpfs', 'size': 777224}]
        server = 'localhost'
        nfs = nfsshares.NFSSharesModel()
        nfs_list = nfs.get_list(server)
        mock_find_nfs_target.assert_called_once_with(server)
        self.assertGreaterEqual(len(nfs_list), 0)
