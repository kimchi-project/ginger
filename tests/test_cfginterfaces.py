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

import __builtin__ as builtins
import mock
import unittest

from mock import call, mock_open, patch

from wok.plugins.ginger.model.cfginterfaces import CfginterfaceModel
from wok.plugins.ginger.model.nw_interfaces_utils import cfgInterfacesHelper
from wok.exception import InvalidParameter, MissingParameter, OperationFailed


class CfgInterfacesTests(unittest.TestCase):
    def test_get_basic_info(self):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'TYPE': 'nic',
                  'MACADDR': '02:02:03:ff:ff:ff'}
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals('testiface', ethinfo['BASIC_INFO']['NAME'])
        self.assertEquals('testdevice', ethinfo['BASIC_INFO']['DEVICE'])
        self.assertEquals('Yes', ethinfo['BASIC_INFO']['ONBOOT'])
        self.assertEquals('02:02:03:ff:ff:ff',
                          ethinfo['BASIC_INFO']['MACADDR'])

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.platform')
    def test_get_basic_info_s390Architecture(self, mock_platform):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'TYPE': 'nic',
                  'SUBCHANNELS': '0.0.09a0,0.0.09a1,0.0.09a2',
                  'NETTYPE': 'qeth', 'PORTNAME': 'OSAPORT',
                  'MACADDR': '02:02:03:ff:ff:ff'}
        mock_platform.machine.return_value = 's390x'
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals('0.0.09a0,0.0.09a1,0.0.09a2',
                          ethinfo['BASIC_INFO']['SUBCHANNELS'])
        self.assertEquals('qeth', ethinfo['BASIC_INFO']['NETTYPE'])
        self.assertEquals('OSAPORT', ethinfo['BASIC_INFO']['PORTNAME'])
        self.assertEquals('02:02:03:ff:ff:ff',
                          ethinfo['BASIC_INFO']['MACADDR'])

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.platform')
    def test_get_basic_info_s390Architecture_withoptions(self, mock_platform):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes', 'TYPE': 'nic',
                  'OPTIONS': ' layer2=1 portno=0 buffer_count=128',
                  'SUBCHANNELS': '0.0.09a0,0.0.09a1,0.0.09a2',
                  'NETTYPE': 'qeth', 'PORTNAME': 'OSAPORT',
                  'MACADDR': '02:02:03:ff:ff:ff'}
        mock_platform.machine.return_value = 's390x'
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals('0', ethinfo['BASIC_INFO']['OPTIONS']['portno'])
        self.assertEquals('128',
                          ethinfo['BASIC_INFO']['OPTIONS']['buffer_count'])
        self.assertEquals('1', ethinfo['BASIC_INFO']['OPTIONS']['layer2'])

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.get_slaves')
    def test_get_basic_info_bond(self, mock_slaves):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice', 'ONBOOT': 'Yes',
                  'TYPE': 'bonding',
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
                  'ONBOOT': 'Yes', 'VLAN_ID': 10, 'VLAN': 'yes',
                  'REORDER_HDR': 0,
                  'PHYSDEV': 'testpd'}
        ethinfo = CfginterfaceModel().get_basic_info(cfgmap)
        self.assertEquals(10, ethinfo['BASIC_INFO']['VLANINFO']['VLAN_ID'])
        self.assertEquals('vlan', ethinfo['BASIC_INFO']['TYPE'])
        self.assertEquals(0, ethinfo['BASIC_INFO']['VLANINFO']['REORDER_HDR'])
        self.assertEquals('testpd', ethinfo['BASIC_INFO']['VLANINFO'][
            'PHYSDEV'])

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.read_ifcfg_file')
    @mock.patch('wok.plugins.ginger.model.cfginterfaces.CfginterfaceModel.'
                'update_basic_info')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.write_attributes_to_cfg')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.update_cfgfile')
    def test_update(self, mock_update_cfgfile, mock_write,
                    mock_basic_info, mock_read):
        cfgmap = {'BASIC_INFO': {'NAME': 'test_iface',
                                 'DEVICE': 'testdevice',
                                 'ONBOOT': 'Yes',
                                 'OPTIONS': {
                                     "buffer_count": "128"}}}
        interface_name = "test_iface"
        cfgmap_in_interfacefile = \
            {'BASIC_INFO': {'DEVICE': 'testdevice',
                            'BOOTPROTO': 'dhcp',
                            'OPTIONS': {
                                "buffer_count": "1223"}
                            }}
        mock_update_cfgfile.return_value = ""
        mock_read.return_value = cfgmap_in_interfacefile
        updatedcfgmap = {'BASIC_INFO': {'NAME': 'testiface',
                                        'DEVICE': 'testdevice',
                                        'ONBOOT': 'Yes',
                                        'BOOTPROTO': 'dhcp',
                                        'OPTIONS': {"buffer_count": "1223"}}}
        mock_basic_info.return_value = updatedcfgmap
        CfginterfaceModel().update(interface_name, cfgmap)
        mock_write.asser_called_once_with()
        mock_basic_info.assert_called_once_with(cfgmap_in_interfacefile,
                                                cfgmap)
        mock_read.assert_called_once_with('test_iface')

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.read_ifcfg_file')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.write_attributes_to_cfg')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.update_cfgfile')
    def test_update_fails_invalid_macaddress(self, mock_update_cfgfile,
                                             mock_write, mock_read):

        cfgmap = {'BASIC_INFO': {'NAME': 'test_iface',
                                 'DEVICE': 'testdevice',
                                 'ONBOOT': 'Yes',
                                 'MACADDR': 'invalid_mac'}}
        interface_name = "test_iface"
        cfgmap_in_interfacefile = \
            {'BASIC_INFO': {'DEVICE': 'testdevice',
                            'BOOTPROTO': 'dhcp'}}
        mock_update_cfgfile.return_value = ""
        mock_read.return_value = cfgmap_in_interfacefile

        with self.assertRaisesRegexp(InvalidParameter, 'GINNET0092E'):
            CfginterfaceModel().update(interface_name, cfgmap)
            mock_read.assert_called_once_with('test_iface')
            mock_write.assert_not_called()

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.'
                'CfgInterfacesHelper.read_ifcfg_file')
    def test_update_missingbasic_info(self, mock_read):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes'}
        interface_name = "test_iface"
        cfgmap_in_interfacefile = {'BASIC_INFO': {'DEVICE': 'testdevice',
                                                  'BOOTPROTO': 'dhcp'}}
        mock_read.return_value = cfgmap_in_interfacefile
        self.assertRaises(MissingParameter, CfginterfaceModel().update,
                          interface_name, cfgmap)

    @mock.patch('wok.plugins.ginger.model.cfginterfaces.os')
    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.parser')
    def test_write(self, mock_parser, mock_os):
        cfgmap = {'NAME': 'testiface', 'DEVICE': 'testdevice',
                  'ONBOOT': 'Yes'}
        interface_name = "test_iface"
        mock_os.path.isfile.return_value = True
        cfgInterfacesHelper.write_attributes_to_cfg(interface_name, cfgmap)
        assert mock_parser.set.call_count == 3
        mock_parser.load.assert_called_once_with()
        mock_parser.save.assert_called_once_with()

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.run_command')
    def test_verify_new_cfgfile_content(self, mock_run_cmd):
        interface = 'dummyiface'

        ip_link_cmd = ['ip', '-o', 'link', 'show', 'dev', interface]
        ip_link_return = 'dummyiface: <BROADCAST,MULTICAST,UP,LOWER_UP> '\
            'mtu 1500 qdisc noqueue state UP mode DEFAULT group default '\
            'qlen 1000\    link/ether 52:54:00:e0:95:c0 brd ff:ff:ff:ff:ff:ff'

        mock_run_cmd.return_value = [ip_link_return, 0, 0]

        expected_content = "DEVICE=%(dev)s\nHWADDR=%(mac)s\nONBOOT=yes\n" \
            "BOOTPROTO=none\n" % {'dev': interface, 'mac': '52:54:00:e0:95:c0'}

        cfg_file_content = cfgInterfacesHelper.get_cfgfile_content(interface)
        mock_run_cmd.assert_called_once_with(ip_link_cmd)
        self.assertEquals(cfg_file_content, expected_content)

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.run_command')
    @mock.patch('os.path.isfile')
    def test_create_minimal_config_file(self, mock_isfile, mock_run_cmd):
        interface = 'dummyiface'

        file_path = '/etc/sysconfig/network-scripts/ifcfg-%s' % interface
        mock_isfile.return_value = False

        ip_link_return = 'dummyiface: (...) qlen 1000\    '\
            'link/ether 52:54:00:e0:95:c0 brd ff:ff:ff:ff:ff:ff'

        mock_run_cmd.return_value = [ip_link_return, 0, 0]

        cfg_file_content = cfgInterfacesHelper.get_cfgfile_content(interface)

        open_ = mock_open(read_data='')

        with patch.object(builtins, 'open', open_):
            cfgInterfacesHelper.create_interface_cfg_file('dummyiface')
            mock_isfile.assert_called_once_with(file_path)

        self.assertEqual(open_.call_args_list, [call(file_path, 'w')])
        self.assertEqual(open_().write.mock_calls, [call(cfg_file_content)])

    @mock.patch('wok.plugins.ginger.model.nw_cfginterfaces_utils.run_command')
    @mock.patch('os.path.isfile')
    def test_create_cfg_file_fails_no_mac_address(self, mock_isfile,
                                                  mock_run_cmd):
        interface = 'dummyiface'

        file_path = '/etc/sysconfig/network-scripts/ifcfg-%s' % interface
        mock_isfile.return_value = False

        ip_link_no_macaddr_return = 'dummyiface: there is no mac address here'

        mock_run_cmd.return_value = [ip_link_no_macaddr_return, 0, 0]

        with self.assertRaisesRegexp(OperationFailed, 'GINNET0081E'):
            cfgInterfacesHelper.create_interface_cfg_file('dummyiface')
            mock_isfile.assert_called_once_with(file_path)
