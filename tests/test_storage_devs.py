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
import unittest

from wok.plugins.ginger.model import utils


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
            ret_id_dict['36005076802810d504800000000002edf'][0],
            'dm-1')
        self.assertEqual(
            len(ret_id_dict['36005076802810d504800000000002edf']), 3)

    def test_parse_lsblk(self):
        out = """NAME="sda" TYPE="disk" SIZE="5G" TRAN="iscsi"
NAME="36005076802810d504800000000002ede" TYPE="mpath" SIZE="5G" TRAN=""
NAME="sdb" TYPE="disk" SIZE="5G" TRAN="iscsi"
NAME="sdb1" TYPE="part" SIZE="5G" TRAN=""
NAME="sdc" TYPE="disk" SIZE="5G" TRAN="iscsi"
NAME="sdc1" TYPE="part" SIZE="10M" TRAN=""
NAME="sdd" TYPE="disk" SIZE="20G" TRAN="fc"
NAME="36005076802810d504800000000002c1e" TYPE="mpath" SIZE="20G" TRAN=""
NAME="sde" TYPE="disk" SIZE="20G" TRAN="fc"
NAME="36005076802810d504800000000002c1e" TYPE="mpath" SIZE="20G" TRAN=""
NAME="dasda" TYPE="disk" SIZE="22.5G" TRAN=""
NAME="dasda1" TYPE="part" SIZE="22.5G" TRAN=""
"""
        ret_dict = utils.parse_lsblk_out(out)
        self.assertEqual(ret_dict['sda']['transport'], 'iscsi')
        self.assertEqual(ret_dict['sde']['transport'], 'fc')
        self.assertEqual(ret_dict['sde']['size'], '20G')

    @mock.patch('wok.plugins.ginger.model.dasd_utils.get_dasd_devs')
    @mock.patch('wok.plugins.ginger.model.utils.get_fc_path_elements')
    @mock.patch('wok.plugins.ginger.model.utils.get_lsblk_keypair_out')
    @mock.patch('wok.plugins.ginger.model.utils.get_disks_by_id_out')
    @mock.patch('wok.plugins.ginger.model.utils.os.listdir')
    def test_get_dev_list(
            self,
            mock_list_dir,
            mock_by_id,
            mock_lsblk_cmd,
            mock_fc_elems,
            mock_get_dasd_devs):
        mock_get_dasd_devs.return_value = None
        mock_fc_elems.return_value = (
            '0.0.0000',
            '0x0000000000000000',
            '0x1000000000000000')
        mock_lsblk_cmd.return_value = """NAME="sda" TYPE="disk" \
        SIZE="5G" TRAN="iscsi"
NAME="36005076802810d504800000000002ede" TRAN="" TYPE="mpath" SIZE="5G"
NAME="sdb" TYPE="disk" SIZE="5G" TRAN="iscsi"
NAME="sdb1" TYPE="part" SIZE="5G" TRAN=""
NAME="sdc" TYPE="disk" SIZE="5G" TRAN="iscsi"
NAME="sdc1" TYPE="part" SIZE="10M" TRAN=""
NAME="36005076802810d504800000000002c1e" TYPE="mpath" SIZE="20G" TRAN=""
NAME="sdd" TYPE="disk" SIZE="20G" TRAN="fc"
NAME="sde" TYPE="disk" SIZE="20G" TRAN="fc"
NAME="36005076802810d504800000000002c1e" TYPE="mpath" SIZE="20G" TRAN=""
NAME="dasda" TYPE="disk" SIZE="22.5G" TRAN=""
NAME="dasda1" TYPE="part" SIZE="22.5G" TRAN=""
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
        self.assertEqual(len(out_list), 4)


class GetPathsUnitTests(unittest.TestCase):
    """
    unit tests for _get_paths() method
    """
    def test_get_paths_success(self):
        """
        unit test to test for a valid scenario valid chipids
        and binary value of pam to get the installed paths
        """
        chipid = 'fa000000 00000000'
        bin_pam = '10000000'
        installed_paths = ['fa']
        out = utils._get_paths(bin_pam, chipid)
        self.assertEqual(installed_paths, out)

    def test_get_paths_invalid_binaryval(self):
        """
        unit test to test for a invalid scenario for valid chipids
        and invalid binary value of pam to get the installed paths
        """
        chipid = 'fa000000 00000000'
        bin_pam = '11000000'
        out = utils._get_paths(bin_pam, chipid)
        installed_paths = ['fa']
        self.assertNotEqual(installed_paths, out)

    def test_get_paths_invalid_chipid(self):
        """
        unit test to test for a valid scenario for invalid chipids
        and valid binary value of pam to get the installed paths
        """
        chipid = 'ds0000 00000000'
        bin_pam = '10000000'
        out = utils._get_paths(bin_pam, chipid)
        installed_paths = ['fa']
        self.assertNotEqual(installed_paths, out)

    def test_byte_to_binary_success(self):
        """
        unit test to test the conversion of byte in binary value to get the
        valid binary value for the corresponding byte
        """
        val = '\x80'
        binaryval = '10000000'
        out = utils._byte_to_binary(ord(val))
        self.assertEqual(binaryval, out)

    def test_byte_to_binary_failure(self):
        """
        unit test to test the conversion of byte in binary value to get the
        invalid binary value for the corresponding byte
        """
        val = '\x80'
        binaryval = '1230000'
        out = utils._byte_to_binary(ord(val))
        self.assertNotEqual(binaryval, out)

    def test_hex_to_binary_success(self):
        """
        unit test to test the conversion of a hexadecimal value to binary
        for a valid hexadecimal value to fetch the the corresponding binary
        value
        """
        val = '80'
        binaryval = '10000000'
        out = utils._hex_to_binary(val)
        self.assertEqual(binaryval, out)

    def test_hex_to_binary_failure(self):
        """
        unit test to test the conversion of a hexadecimal value to binary
        for a valid hexadecimal value to fetch the the corresponding
        invalid binary value
        """
        val = 'e0'
        binaryval = '10000000'
        out = utils._hex_to_binary(val)
        self.assertNotEqual(binaryval, out)


class FormatLscssUnitTests(unittest.TestCase):
    """
    unit tests for _format_lscss() method
    """
    def test_format_lscss_Noneinput(self):
        """
        unit test to validate _format_lscss() with None input
        _format_lscss() should return None
        """
        device = None
        formated_devices = utils._format_lscss(device)
        self.assertEqual(formated_devices, None)

    def test_format_lscss_emptyjsoninput(self):
        """
        unit test to validate _format_lscss() with empty json i/p
        _format_lscss() should return empty json
        """
        device = {}
        formated_devices = utils._format_lscss(device)
        self.assertEqual(formated_devices, device)

    @mock.patch('wok.plugins.ginger.model.utils.wok_log', autospec=True)
    def test_format_lscss_keyerror(self, mock_log):
        """
        unit test to validate _format_lscss() with wrong keys
        _format_lscss() should raise KeyError
        """
        device = {"Device": "0.0.0200", "Subchan": "0.0.0000",
                  "DevType": "3390/0a", "CU Type": "3390/0a",
                  "Use": "", "PIM": "e0", "PAM": "e0",
                  "POM": "ff", "Invalid Key": "0000"}
        log_msg = 'Issue while formating lscss dictionary output'
        self.assertRaises(KeyError, utils._format_lscss, device)
        mock_log.error.assert_called_with(log_msg)

    def test_format_lscss_use_yes(self):
        """
        unit test to validate _format_lscss() with "Use" as "yes"
        """
        device = {"Device": "0.0.0200", "Subchan": "0.0.0000",
                  "DevType": "3390/0a", "CU Type": "3390/0a",
                  "Use": "yes", "PIM": "e0", "PAM": "e0",
                  "POM": "ff", "CHPIDs": "b0b10d00 00000000"}
        output = {"device": "0.0.0200", "sub_channel": "0.0.0000",
                  "device_type": "3390/0a", "cu_type": "3390/0a",
                  "status": "online", "enabled_chipids":
                  ["b0", "b1", "0d"], "installed_chipids":
                  ["b0", "b1", "0d"]}
        formated_devices = utils._format_lscss(device)
        self.assertEqual(formated_devices, output)

    def test_format_lscss_use_blank(self):
        """
        unit test to validate _format_lscss() with "Use" as "blank"
        and pim mask equal to pam mask
        """
        device = {"Device": "0.0.0200", "Subchan": "0.0.0000",
                  "DevType": "3390/0a", "CU Type": "3390/0a",
                  "Use": "  ", "PIM": "e0", "PAM": "e0",
                  "POM": "ff", "CHPIDs": "b0b10d00 00000000"}
        output = {"device": "0.0.0200", "sub_channel": "0.0.0000",
                  "device_type": "3390/0a", "cu_type": "3390/0a",
                  "status": "offline", "enabled_chipids":
                  ["b0", "b1", "0d"], "installed_chipids":
                  ["b0", "b1", "0d"]}
        formated_devices = utils._format_lscss(device)
        self.assertEqual(formated_devices, output)

    def test_format_lscss_use_pim_notequal_pam(self):
        """
        unit test to validate _format_lscss() with pim mask
        not equal to pam mask
        """
        device = {"Device": "0.0.0200", "Subchan": "0.0.0000",
                  "DevType": "3390/0a", "CU Type": "3390/0a",
                  "Use": "  ", "PIM": "80", "PAM": "e0",
                  "POM": "ff", "CHPIDs": "b0b10d00 00000000"}
        output = {"device": "0.0.0200", "sub_channel": "0.0.0000",
                  "device_type": "3390/0a", "cu_type": "3390/0a",
                  "status": "offline", "enabled_chipids":
                  ["b0", "b1", "0d"], "installed_chipids":
                  ["b0"]}
        formated_devices = utils._format_lscss(device)
        self.assertEqual(formated_devices, output)


class GetDeviceInfoUnitTests(unittest.TestCase):
    """
    unit tests for _get_deviceinfo() method
    """
    @mock.patch('wok.plugins.ginger.model.utils.get_row_data', autospec=True)
    @mock.patch('wok.plugins.ginger.model.utils._format_lscss', autospec=True)
    def test_get_deviceinfo_somedevice(self, mock_format_lscss,
                                       mock_get_row_data):
        """
        unit test to validate _get_deviceinfo() method with
        matching device
        _get_deviceinfo() should return _format_lscss() o/p
        """
        device = "xxx"
        header_pattern = "(Device)\s+(Subchan)\.\s+(DevType)\s+(CU\ Type)\s+" \
                         "(Use)\s+(PIM)\s+(PAM)\s+(POM)\s+(CHPIDs)$"
        device_pattern = "(xxx)\s+(\d\.\d\.[0-9a-fA-F]{4})\s+(\w+\/\w+)" \
                         "\s+(\w+\/\w+)\s(\s{3}|yes)\s+([0-9a-fA-F]{2})\s+" \
                         "([0-9a-fA-F]{2})\s+([0-9a-fA-F]{2})\s+(\w+\s\w+)"
        mock_get_row_data.return_value = {}
        mock_format_lscss.return_value = {}
        deviceinfo = utils._get_deviceinfo('', device)
        mock_get_row_data.assert_called_with('', header_pattern,
                                             device_pattern)
        mock_format_lscss.assert_called_with(mock_get_row_data.
                                             return_value)
        self.assertEqual(deviceinfo, {})

    @mock.patch('wok.plugins.ginger.model.utils', autospec=True)
    @mock.patch('wok.plugins.ginger.model.utils._format_lscss', autospec=True)
    def test_get_deviceinfo_emptydevice(self, mock_format_lscss, mock_utils):
        """
        unit test to validate _get_deviceinfo() with empty device i/p
        _get_deviceinfo() should return device
        """
        device = ""
        deviceinfo = utils._get_deviceinfo('', device)
        self.assertFalse(mock_utils.get_row_data.called,
                         msg='Unexpected call to mock_utils.get_row_data()')
        self.assertFalse(mock_format_lscss.called,
                         msg='Unexpected call to mock_format_lscss()')
        self.assertEqual(deviceinfo, device)
