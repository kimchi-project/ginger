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
        self.assertEquals('miimon=1 updelay=0 downdelay=0 mode=balance-rr',
                          ethinfo['BASIC_INFO']['BONDING_OPTS'])
        self.assertEquals('yes', ethinfo['BASIC_INFO']['BONDING_MASTER'])

        self.assertEquals(slaves, ethinfo['BASIC_INFO']['SLAVES'])

    def test_get_basic_info_vlan(self):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'VLAN_ID': 10, 'VLAN': 'yes',
                  'REORDER_HDR': 0,
                  'PHYSDEV': 'testpd'}
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals(10,
                          ethinfo['BASIC_INFO']['VLAN_ID'])
        self.assertEquals('Vlan', ethinfo['BASIC_INFO']['TYPE'])
        self.assertEquals(0, ethinfo['BASIC_INFO']['REORDER_HDR'])
        self.assertEquals('testpd', ethinfo['BASIC_INFO']['PHYSDEV'])
