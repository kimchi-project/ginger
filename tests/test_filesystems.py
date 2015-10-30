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

import os
import unittest

from wok.exception import OperationFailed
from wok.rollbackcontext import RollbackContext
from wok.utils import run_command

import wok.plugins.ginger.models.filesystem as filesystem
from wok.plugins.ginger.models.fs_utils import _parse_df_output


def create_file(self):
    fcmd = ["dd", "if=/dev/zero", "of=/testfile",
            "bs=10M", "count=1"]
    fout, err, rc = run_command(fcmd)
    if rc:
        self.assertRaises(OperationFailed)

    fscmd = ["mkfs.ext4", "/testfile"]
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

    def test_mount_fs(self):
        fs = filesystem.FileSystemsModel()
        fsd = filesystem.FileSystemModel()

        create_file(self)

        blkdev = '/testfile'
        mntpt = '/test'
        persistent = False

        fs_list = fs.get_list()
        with RollbackContext() as rollback:
            fs.create({'blk_dev': blkdev, 'mount_point': mntpt,
                       'persistent': persistent})
            rollback.prependDefer(fsd.delete, mntpt)

            new_fs_list = fs.get_list()
            self.assertEqual(len(new_fs_list), len(fs_list) + 1)

        delete_file(self)

    def test_mount_existing_fs_fails(self):
        fs = filesystem.FileSystemsModel()
        fsd = filesystem.FileSystemModel()

        create_file(self)

        blkdev = '/testfile'
        mntpt = '/test'
        persistent = False

        with RollbackContext() as rollback:
            fs.create({'blk_dev': blkdev, 'mount_point': mntpt,
                       'persistent': persistent})
            rollback.prependDefer(fsd.delete, mntpt)

            with self.assertRaises(OperationFailed):
                fs.create({'blk_dev': blkdev, 'mount_point': mntpt,
                           'persistent': persistent})

        delete_file(self)

    def test_df_parser(self):
        df_out = """Filesystem              Type      Size  Used Avail Use% Mounted on
devtmpfs                devtmpfs  3.7G     0  3.7G   0% /dev
tmpfs                   tmpfs     3.8G  240K  3.8G   1% /dev/shm
tmpfs                   tmpfs     3.8G  1.1M  3.8G   1% /run
tmpfs                   tmpfs     3.8G     0  3.8G   0% /sys/fs/cgroup
/dev/mapper/fedora-root ext4       50G   17G   31G  35% /
tmpfs                   tmpfs     3.8G  520K  3.8G   1% /tmp
/dev/sda1               ext4      477M  159M  289M  36% /boot
/dev/mapper/fedora-home ext4      237G   15G  211G   7% /home
tmpfs                   tmpfs     760M  8.0K  759M   1% /run/user/1000"""
        parse_out = _parse_df_output(df_out)
        if parse_out[0]['filesystem'] != 'devtmpfs':
            self.fail("Parsing of df failed : filesystem")
        if parse_out[0]['size'] != '3.7G':
            self.fail("Parsing of df failed : size")
        if parse_out[0]['used'] != '0':
            self.fail("Parsing of df failed : used")
        if parse_out[0]['avail'] != '3.7G':
            self.fail("Parsing of df failed : avail")
        if parse_out[0]['use%'] != '0%':
            self.fail("Parsing of df failed : use%")
        if parse_out[0]['mounted_on'] != '/dev':
            self.fail("Parsing of df failed : mounted on")
