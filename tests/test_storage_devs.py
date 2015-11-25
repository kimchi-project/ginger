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

from wok.plugins.ginger.models import utils


class StorageDevsTests(unittest.TestCase):

    def test_ll_parser(self):
        out = """total 0
lrwxrwxrwx. 1 root root 11 Nov 24 10:58 ccw-0X5184 -> ../../dasda
lrwxrwxrwx. 1 root root 12 Nov 23 11:16 ccw-0X5184-part1 -> ../../dasda1
lrwxrwxrwx. 1 root root 11 Nov 24 10:58 ccw-IBM.750000000DX111.0002.84 -> \
../../dasda
lrwxrwxrwx. 1 root root 12 Nov 23 11:16 ccw-IBM.750000000DX111.0002.84-part1 \
-> ../../dasda1
lrwxrwxrwx. 1 root root 10 Nov 24 11:26 dm-name-36005076802810d50480000000000\
2c1e -> ../../dm-5
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d504800000000002\
ede -> ../../dm-0
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d504800000000002\
edf -> ../../dm-1
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d5048000000\
00002edf1 -> ../../dm-3
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d50480000000\
0002ee0 -> ../../dm-2
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d504800000000\
002ee0p1 -> ../../dm-4
lrwxrwxrwx. 1 root root 10 Nov 24 11:26 dm-uuid-mpath-36005076802810d504800\
000000002c1e -> ../../dm-5
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-mpath-36005076802810d5048000\
00000002ede -> ../../dm-0
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-mpath-36005076802810d50480\
0000000002edf -> ../../dm-1
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-mpath-36005076802810d50480\
0000000002ee0 -> ../../dm-2
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-part1-mpath-36005076802810d\
504800000000002edf -> ../../dm-3
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-part1-mpath-36005076802810d50\
4800000000002ee0 -> ../../dm-4
lrwxrwxrwx. 1 root root 10 Nov 24 11:26 lvm-pv-uuid-Pj0OGP-sCHM-KIvP-pdP6-\
4cJI-jNnV-TUdS81 -> ../../dm-5
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d504800000000\
002c1e -> ../../sde
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d5048000000000\
02ede -> ../../sda
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d5048000000000\
02edf -> ../../sdb
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 scsi-36005076802810d50480000000000\
2edf-part1 -> ../../sdb1
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d50480000000000\
2ee0 -> ../../sdc
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 scsi-36005076802810d50480000000000\
2ee0-part1 -> ../../sdc1
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2c1e -> ../../sde
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2ede -> ../../sda
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2edf -> ../../sdb
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2edf-part1 -> ../../sdb1
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2ee0 -> ../../sdc
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2ee0-part1 -> ../../sdc1
"""
        ret_dict, ret_id_dict = utils.parse_ll_out(out)
        self.assertEqual(ret_dict['dasda'], 'ccw-IBM.750000000DX111.0002.84')
        self.assertEqual(ret_dict['sda'], '36005076802810d504800000000002ede')
        self.assertEqual(ret_dict['dm-3'], '36005076802810d504800000000002edf')
        self.assertEqual(
            ret_id_dict['36005076802810d504800000000002edf1'][0],
            'dm-3')
        self.assertEqual(
            len(ret_id_dict['36005076802810d504800000000002edf']), 3)

    def test_parse_lsblk(self):
        out = """NAME="sda" TRAN="iscsi" TYPE="disk" SIZE="5G"
NAME="36005076802810d504800000000002ede" TRAN="" TYPE="mpath" SIZE="5G"
NAME="sdb" TRAN="iscsi" TYPE="disk" SIZE="5G"
NAME="sdb1" TRAN="" TYPE="part" SIZE="5G"
NAME="sdc" TRAN="iscsi" TYPE="disk" SIZE="5G"
NAME="sdc1" TRAN="" TYPE="part" SIZE="10M"
NAME="sdd" TRAN="fc" TYPE="disk" SIZE="20G"
NAME="36005076802810d504800000000002c1e" TRAN="" TYPE="mpath" SIZE="20G"
NAME="sde" TRAN="fc" TYPE="disk" SIZE="20G"
NAME="36005076802810d504800000000002c1e" TRAN="" TYPE="mpath" SIZE="20G"
NAME="dasda" TRAN="" TYPE="disk" SIZE="22.5G"
NAME="dasda1" TRAN="" TYPE="part" SIZE="22.5G"
"""
        ret_dict = utils.parse_lsblk_out(out)
        self.assertEqual(ret_dict['sda']['transport'], 'iscsi')
        self.assertEqual(ret_dict['sde']['transport'], 'fc')
        self.assertEqual(ret_dict['sde']['size'], '20G')

    @mock.patch('wok.plugins.ginger.models.utils.get_lsblk_keypair_out')
    @mock.patch('wok.plugins.ginger.models.utils.get_disks_by_id_out')
    @mock.patch('wok.plugins.ginger.models.utils.os.listdir')
    def test_get_dev_list(self, mock_list_dir, mock_by_id, mock_lsblk_cmd):
        mock_lsblk_cmd.return_value = """NAME="sda" TRAN="iscsi" TYPE="disk" \
        SIZE="5G"
NAME="36005076802810d504800000000002ede" TRAN="" TYPE="mpath" SIZE="5G"
NAME="sdb" TRAN="iscsi" TYPE="disk" SIZE="5G"
NAME="sdb1" TRAN="" TYPE="part" SIZE="5G"
NAME="sdc" TRAN="iscsi" TYPE="disk" SIZE="5G"
NAME="sdc1" TRAN="" TYPE="part" SIZE="10M"
NAME="sdd" TRAN="fc" TYPE="disk" SIZE="20G"
NAME="36005076802810d504800000000002c1e" TRAN="" TYPE="mpath" SIZE="20G"
NAME="sde" TRAN="fc" TYPE="disk" SIZE="20G"
NAME="36005076802810d504800000000002c1e" TRAN="" TYPE="mpath" SIZE="20G"
NAME="dasda" TRAN="" TYPE="disk" SIZE="22.5G"
NAME="dasda1" TRAN="" TYPE="part" SIZE="22.5G"
"""
        mock_by_id.return_value = """total 0
lrwxrwxrwx. 1 root root 11 Nov 24 10:58 ccw-0X5184 -> ../../dasda
lrwxrwxrwx. 1 root root 12 Nov 23 11:16 ccw-0X5184-part1 -> ../../dasda1
lrwxrwxrwx. 1 root root 11 Nov 24 10:58 ccw-IBM.750000000DX111.0002.84\
 -> ../../dasda
lrwxrwxrwx. 1 root root 12 Nov 23 11:16 ccw-IBM.750000000DX111.0002.84\
-part1 -> ../../dasda1
lrwxrwxrwx. 1 root root 10 Nov 24 11:26 dm-name-36005076802810d50480000000\
0002c1e -> ../../dm-5
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d504800000000\
002ede -> ../../dm-0
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d504800000000\
002edf -> ../../dm-1
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d5048000000000\
02edf1 -> ../../dm-3
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d504800000000\
002ee0 -> ../../dm-2
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-name-36005076802810d5048000000000\
02ee0p1 -> ../../dm-4
lrwxrwxrwx. 1 root root 10 Nov 24 11:26 dm-uuid-mpath-36005076802810d5048000\
00000002c1e -> ../../dm-5
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-mpath-36005076802810d5048000\
00000002ede -> ../../dm-0
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-mpath-36005076802810d5048000\
00000002edf -> ../../dm-1
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-mpath-36005076802810d5048000\
00000002ee0 -> ../../dm-2
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-part1-mpath-36005076802810d\
504800000000002edf -> ../../dm-3
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 dm-uuid-part1-mpath-36005076802810d\
504800000000002ee0 -> ../../dm-4
lrwxrwxrwx. 1 root root 10 Nov 24 11:26 lvm-pv-uuid-Pj0OGP-sCHM-KIvP-pdP6\
-4cJI-jNnV-TUdS81 -> ../../dm-5
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d504800000000002c1e\
 -> ../../sde
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d504800000000002ede\
 -> ../../sda
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d504800000000002edf\
 -> ../../sdb
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 scsi-36005076802810d50480000000000\
2edf-part1 -> ../../sdb1
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 scsi-36005076802810d50480000000000\
2ee0 -> ../../sdc
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 scsi-36005076802810d50480000000000\
2ee0-part1 -> ../../sdc1
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2c1e -> ../../sde
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2ede -> ../../sda
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2edf -> ../../sdb
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 wwn-0x6005076802810d504800000000002\
edf-part1 -> ../../sdb1
lrwxrwxrwx. 1 root root  9 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2ee0 -> ../../sdc
lrwxrwxrwx. 1 root root 10 Nov 24 10:58 wwn-0x6005076802810d50480000000000\
2ee0-part1 -> ../../sdc1
"""
        mock_list_dir.return_value = ['sde']
        out_list = utils.get_final_list()
        self.assertEqual(len(out_list), 5)
