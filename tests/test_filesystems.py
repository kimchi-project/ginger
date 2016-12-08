#
# Project Ginger
#
# Copyright IBM Corp, 2015-2016
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

import os
import mock
import unittest

from wok.exception import OperationFailed, MissingParameter, InvalidParameter
from wok.rollbackcontext import RollbackContext
from wok.utils import run_command

import wok.plugins.ginger.model.filesystem as filesystem
from wok.plugins.ginger.model.fs_utils import _parse_df_output


def create_file(self):
    fcmd = ["dd", "if=/dev/zero", "of=/testfile",
            "bs=10M", "count=1"]
    fout, err, rc = run_command(fcmd)
    if rc:
        self.assertRaises(OperationFailed)

    fscmd = ["mkfs.ext4", "/testfile", "-F"]
    fsout, err, rc = run_command(fscmd)
    if rc:
        self.assertRaises(OperationFailed)

    mntpt = '/test'
    if not os.path.exists(mntpt):
        os.makedirs(mntpt)


def delete_file(self):
    fname = "/testfile"
    mntpt = '/test'
    if os.path.exists(fname):
        os.remove(fname)
    if os.path.exists(mntpt):
        os.rmdir(mntpt)


class FileSystemTests(unittest.TestCase):
    def test_get_fs_list(self):
        fs = filesystem.FileSystemsModel()
        fs_list = fs.get_list()
        self.assertGreaterEqual(len(fs_list), 0)

    def test_mount_local_fs(self):
        fs = filesystem.FileSystemsModel()
        fsd = filesystem.FileSystemModel()

        create_file(self)

        fstype = 'local'
        blkdev = '/testfile'
        mntpt = '/test'
        persistent = False

        fs_list = fs.get_list()
        with RollbackContext() as rollback:
            fs.create({'type': fstype, 'blk_dev': blkdev, 'mount_point': mntpt,
                       'persistent': persistent})
            rollback.prependDefer(fsd.delete, mntpt)

            new_fs_list = fs.get_list()
            self.assertEqual(len(new_fs_list), len(fs_list) + 1)

        delete_file(self)

    def test_mount_existing_fs_fails(self):
        fs = filesystem.FileSystemsModel()
        fsd = filesystem.FileSystemModel()

        create_file(self)

        fstype = 'local'
        blkdev = '/testfile'
        mntpt = '/test'
        persistent = False

        with RollbackContext() as rollback:
            fs.create({'type': fstype, 'blk_dev': blkdev, 'mount_point': mntpt,
                       'persistent': persistent})
            rollback.prependDefer(fsd.delete, mntpt)

            with self.assertRaises(OperationFailed):
                fs.create({'type': fstype, 'blk_dev': blkdev,
                           'mount_point': mntpt,
                           'persistent': persistent})

        delete_file(self)

    def test_df_parser(self):
        df_out = """Filesystem Type 1K-blocks Used Available Use% Mounted on
devtmpfs                devtmpfs   3875092        0   3875092   0% /dev
tmpfs                   tmpfs      3886100     1772   3884328   1% /dev/shm
tmpfs                   tmpfs      3886100     1120   3884980   1% /run
tmpfs                 tmpfs      3886100        0   3886100   0% /sys/fs/cgroup
/dev/mapper/fedora-root ext4      51475068 18194240  30643004  38% /
tmpfs                   tmpfs      3886100    25748   3860352   1% /tmp
/dev/sda1               ext4        487652   162811    295145  36% /boot
/dev/mapper/fedora-home ext4     247613436 26170364 208841936  12% /home"""
        parse_out = _parse_df_output(df_out)
        if parse_out[0]['filesystem'] != 'devtmpfs':
            self.fail("Parsing of df failed : filesystem")
        if parse_out[0]['size'] != 3875092:
            self.fail("Parsing of df failed : size")
        if parse_out[0]['used'] != '0':
            self.fail("Parsing of df failed : used")
        if parse_out[0]['avail'] != 3875092:
            self.fail("Parsing of df failed : avail")
        if parse_out[0]['use%'] != '0%':
            self.fail("Parsing of df failed : use%")
        if parse_out[0]['mounted_on'] != '/dev':
            self.fail("Parsing of df failed : mounted on")

    @mock.patch('wok.plugins.ginger.model.fs_utils.nfsmount', autospec=True)
    @mock.patch('wok.plugins.ginger.model.fs_utils.make_persist',
                autospec=True)
    def test_nfs_mount(self, mock_make_persist, mock_nfsmount):
        fs = filesystem.FileSystemsModel()
        fstype = 'nfs'
        server = 'localhost'
        share = '/var/ftp/nfs1'
        mntpt = '/test'
        mntopts = ''

        fs.create({'type': fstype, 'server': server,
                   'share': share, 'mount_point': mntpt,
                   'mount_options': mntopts})

        mock_nfsmount.assert_called_once_with(server, share, mntpt, mntopts)
        mock_make_persist.assert_called_once_with(server + ':' + share,
                                                  mntpt, mntopts)

    def test_nfs_mount_missing_type(self):
        fs = filesystem.FileSystemsModel()
        server = 'localhost'
        share = '/var/ftp/nfs1'
        mntpt = '/test'

        params = {'server': server, 'share': share, 'mount_point': mntpt}

        self.assertRaises(MissingParameter, fs.create, params)

    def test_nfs_mount_invalid_type(self):
        fs = filesystem.FileSystemsModel()
        fstype = 'invalid'
        server = 'localhost'
        share = '/var/ftp/nfs1'
        mntpt = '/test'

        params = {'type': fstype, 'server': server,
                  'share': share, 'mount_point': mntpt}

        self.assertRaises(InvalidParameter, fs.create, params)

    def test_nfs_mount_missing_server(self):
        fs = filesystem.FileSystemsModel()
        fstype = 'nfs'
        share = '/var/ftp/nfs1'
        mntpt = '/test'

        params = {'type': fstype, 'share': share, 'mount_point': mntpt}

        self.assertRaises(MissingParameter, fs.create, params)

    def test_nfs_mount_missing_share(self):
        fs = filesystem.FileSystemsModel()
        fstype = 'nfs'
        server = 'localhost'
        mntpt = '/test'

        params = {'type': fstype, 'server': server, 'mount_point': mntpt}

        self.assertRaises(MissingParameter, fs.create, params)

    def test_nfs_mount_missing_mountpoint(self):
        fs = filesystem.FileSystemsModel()
        fstype = 'nfs'
        server = 'localhost'
        share = '/var/ftp/nfs1'

        params = {'type': fstype, 'server': server, 'share': share}

        self.assertRaises(MissingParameter, fs.create, params)
