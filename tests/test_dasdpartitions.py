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

import mock
import re
import unittest

import wok.plugins.ginger.model.dasdpartitions as partitions
from wok.plugins.gingerbase.disks import _parse_lsblk_output


class DASDPartitionsTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.dasd_utils._create_dasd_part',
                autospec=True)
    def test_create_part(self, mock_create_part):
        parts = partitions.DASDPartitionsModel()
        dev = 'dasdb'
        size = 10
        params = {'dev_name': dev, 'size': size}
        parts.create(params)
        mock_create_part.return_value = 'dasdb'
        mock_create_part.assert_called_with(dev, size)

    @mock.patch('wok.plugins.ginger.model.dasd_utils._delete_dasd_part',
                autospec=True)
    def test_delete_part(self, mock_delete_part):
        part = partitions.DASDPartitionModel()
        part_name = 'dasdb2'
        name_split = re.split('(\D+)', part_name, flags=re.IGNORECASE)
        dev_name = name_split[1]
        part_num = name_split[2]
        part.delete(part_name)
        mock_delete_part.assert_called_with(dev_name, part_num)

    def test_lsblk_parser(self):
        lsblk_out = \
            """NAME="dasda" TYPE="disk" FSTYPE="" MOUNTPOINT=""MAJ:MIN="94:0"
NAME="dasda1" TYPE="part" FSTYPE="ext3" MOUNTPOINT="/" MAJ:MIN="94:1"
NAME="dasdb" TYPE="disk" FSTYPE="" MOUNTPOINT="" MAJ:MIN="94:4"
NAME="dasdb1" TYPE="part" FSTYPE="" MOUNTPOINT="" MAJ:MIN="94:5"
NAME="dasdb2" TYPE="part" FSTYPE="" MOUNTPOINT="" MAJ:MIN="94:6"
NAME="dasdc" TYPE="disk" FSTYPE="" MOUNTPOINT="" MAJ:MIN="94:8"

"""

        keys = ["NAME", "TYPE", "FSTYPE", "MOUNTPOINT", "MAJ:MIN"]
        parse_out = _parse_lsblk_output(lsblk_out, keys)
        if parse_out[0]['name'] != 'dasda':
            self.fail("Parsing of lsblk failed : name")
        if parse_out[0]['type'] != 'disk':
            self.fail("Parsing of lsblk failed : type")
        if parse_out[0]['mountpoint'] != '':
            self.fail("Parsing of lsblk failed : mountpoint")
        if parse_out[0]['fstype'] != '':
            self.fail("Parsing of lsblk failed : fstype")
