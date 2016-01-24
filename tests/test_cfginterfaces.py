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

from plugins.ginger.models.cfginterfaces import CfginterfaceModel
from wok.exception import MissingParameter


class CfgInterfacesTests(unittest.TestCase):
    def test_get_basic_info(self):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'TYPE': 'Ethernet'}
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals('testiface', ethinfo['BASIC_INFO']['NAME'])
        self.assertEquals('testdevice', ethinfo['BASIC_INFO']['DEVICE'])
        self.assertEquals('Yes', ethinfo['BASIC_INFO']['ONBOOT'])

    @mock.patch('plugins.ginger.models.cfginterfaces.platform')
    def test_get_basic_info_s390Architecture(self, mock_platform):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'TYPE': 'Ethernet',
                  'SUBCHANNELS': '0.0.09a0,0.0.09a1,0.0.09a2',
                  'NETTYPE': 'qeth', 'PORTNAME': 'OSAPORT'}
        mock_platform.machine.return_value = 's390x'
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals('0.0.09a0,0.0.09a1,0.0.09a2',
                          ethinfo['BASIC_INFO']['SUBCHANNELS'])
        self.assertEquals('qeth', ethinfo['BASIC_INFO']['NETTYPE'])
        self.assertEquals('OSAPORT', ethinfo['BASIC_INFO']['PORTNAME'])

    @mock.patch('plugins.ginger.models.cfginterfaces.CfginterfaceModel.'
                'get_slaves')
    def test_get_basic_info_bond(self, mock_slaves):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice', 'ONBOOT': 'Yes',
                  'TYPE': 'Bond',
                  'BONDING_OPTS':
                      'miimon=1 updelay=0 downdelay=0 mode=balance-rr',
                  'BONDING_MASTER': 'yes'}
        slaves = ['slave1', 'slave2']
        mock_slaves.return_value = slaves
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals({'downdelay': '0', 'iimon': '1', 'mode': 'balance-r',
                           'updelay': '0'},
                          ethinfo['BASIC_INFO']['BONDINFO']['BONDING_OPTS'])
        self.assertEquals('yes', ethinfo['BASIC_INFO']['BONDINFO'][
            'BONDING_MASTER'])

        self.assertEquals(slaves, ethinfo['BASIC_INFO']['BONDINFO']['SLAVES'])

    def test_get_basic_info_vlan(self):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'VLANID': 10, 'VLAN': 'yes',
                  'REORDER_HDR': 0,
                  'PHYSDEV': 'testpd'}
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals(10, ethinfo['BASIC_INFO']['VLANINFO']['VLANID'])
        self.assertEquals('Vlan', ethinfo['BASIC_INFO']['TYPE'])
        self.assertEquals(0, ethinfo['BASIC_INFO']['VLANINFO']['REORDER_HDR'])
        self.assertEquals('testpd', ethinfo['BASIC_INFO']['VLANINFO'][
            'PHYSDEV'])

    @mock.patch('plugins.ginger.models.cfginterfaces.CfginterfaceModel.'
                'read_ifcfg_file')
    @mock.patch('plugins.ginger.models.cfginterfaces.CfginterfaceModel.'
                'update_basic_info')
    @mock.patch('plugins.ginger.models.cfginterfaces.CfginterfaceModel.'
                'write_attributes_to_cfg')
    @mock.patch('plugins.ginger.models.cfginterfaces.CfginterfaceModel.'
                'update_cfgfile')
    def test_update(self, mock_update_cfgfile, mock_write,
                    mock_basic_info, mock_read):
        cfgmap = {'BASIC_INFO': {'NAME': 'test_iface',
                                 'DEVICE': 'testdevice',
                                 'ONBOOT': 'Yes'}}
        interface_name = "test_iface"
        cfgmap_in_interfacefile = \
            {'BASIC_INFO': {'DEVICE': 'testdevice',
                            'BOOTPROTO': 'dhcp'}}
        mock_update_cfgfile.return_value = ""
        mock_read.return_value = cfgmap_in_interfacefile
        updatedcfgmap = {'BASIC_INFO': {'NAME': 'testiface',
                                        'DEVICE': 'testdevice',
                                        'ONBOOT': 'Yes',
                                        'BOOTPROTO': 'dhcp'}}
        mock_basic_info.return_value = updatedcfgmap
        CfginterfaceModel().update(interface_name, cfgmap)
        mock_write.asser_called_once_with()
        mock_basic_info.assert_called_once_with(cfgmap_in_interfacefile,
                                                cfgmap)
        mock_read.assert_called_once_with('test_iface')

    @mock.patch('plugins.ginger.models.cfginterfaces.CfginterfaceModel'
                '.read_ifcfg_file')
    def test_update_missingbasic_info(self, mock_read):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes'}
        interface_name = "test_iface"
        cfgmap_in_interfacefile = {'BASIC_INFO': {'DEVICE': 'testdevice',
                                                  'BOOTPROTO': 'dhcp'}}
        mock_read.return_value = cfgmap_in_interfacefile
        self.assertRaises(MissingParameter, CfginterfaceModel().update,
                          interface_name, cfgmap)

    @mock.patch('plugins.ginger.models.cfginterfaces.os')
    @mock.patch('plugins.ginger.models.cfginterfaces.parser')
    def test_write(self, mock_parser, mock_os):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes'}
        interface_name = "test_iface"
        mock_os.path.isfile.return_value = True
        CfginterfaceModel().write_attributes_to_cfg(interface_name, cfgmap)
        assert mock_parser.set.call_count == 3
        mock_parser.load.assert_called_once_with()
        mock_parser.save.assert_called_once_with()

    @mock.patch('plugins.ginger.models.cfginterfaces.os')
    @mock.patch('plugins.ginger.models.cfginterfaces.parser')
    @mock.patch('plugins.ginger.models.cfginterfaces.open')
    def test_write_create_interfacefile(self, mock_open, mock_parser,
                                        mock_os):
        """Write attributes to interface file. This method tests
        creation of interface file which does not exist"""
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes'}
        interface_name = "test_iface"
        mock_os.path.isfile.return_value = False
        CfginterfaceModel().write_attributes_to_cfg(interface_name, cfgmap)
        assert mock_parser.set.call_count == 3
        mock_open.close.asser_called_once_with()
        mock_parser.load.assert_called_once_with()
        mock_parser.save.assert_called_once_with()
