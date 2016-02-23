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

from mock import call

from wok.exception import InvalidParameter, OperationFailed

import wok.plugins.ginger.model.ovsbridges as ovsbridges
from wok.plugins.ginger.model.ovsbridges import OVSBridgeModel
from wok.plugins.ginger.model.ovsbridges import OVSBridgesModel


class OVSBridgesTests(unittest.TestCase):

    def test_list_bridges_parser(self):
        listbr_output = \
            """
ovsbr
ovsbr2
ovsbr3\n
            """
        output_array = ovsbridges.parse_listbr_output(
            listbr_output
        )
        self.assertEqual(len(output_array), 3)
        self.assertIn('ovsbr', output_array)
        self.assertIn('ovsbr2', output_array)
        self.assertIn('ovsbr3', output_array)

    def test_list_ports_parser(self):
        listports_output = \
            """
interface1
interface2
bond1
bond2\n
            """
        output_array = ovsbridges.parse_listports_output(
            listports_output
        )
        self.assertEqual(len(output_array), 4)
        self.assertIn('interface1', output_array)
        self.assertIn('interface2', output_array)
        self.assertIn('bond1', output_array)
        self.assertIn('bond2', output_array)

    def get_list_port_output(self, port_name, interfaces_array):
        template = """
_uuid               : 32842122-c06f-4faf-8056-4223552b6cef
bond_active_slave   : "00:00:00:00:00:00"
bond_downdelay      : 0
bond_fake_iface     : false
bond_mode           : []
bond_updelay        : 0
external_ids        : {}
fake_bridge         : false
interfaces          : %s
lacp                : []
mac                 : []
name                : "%s"
other_config        : {}
qos                 : []
rstp_statistics     : {}
rstp_status         : {}
statistics          : {}
status              : {}
tag                 : []
trunks              : []
vlan_mode           : []
        """ % (interfaces_array, port_name)

        return template

    def get_list_interfaces_output(
        self, iface_name,
        iface_uuid='047843e4-eb1b-4cdb-8433-4f8f447ff935'
    ):

        template = """
_uuid               : %s
admin_state         : down
bfd                 : {}
bfd_status          : {}
cfm_fault           : []
cfm_fault_status    : []
cfm_flap_count      : []
cfm_health          : []
cfm_mpid            : []
cfm_remote_mpids    : []
cfm_remote_opstate  : []
duplex              : []
error               : []
external_ids        : {}
ifindex             : 16
ingress_policing_burst: 0
ingress_policing_rate: 0
lacp_current        : []
link_resets         : 0
link_speed          : []
link_state          : down
lldp                : {}
mac                 : []
mac_in_use          : "16:bd:8d:f8:aa:f6"
mtu                 : 1500
name                : "%s"
ofport              : 2
ofport_request      : []
options             : {}
other_config        : {}
statistics          : {collisions=0, rx_bytes=0, rx_crc_err=0, \
rx_dropped=0, rx_errors=0, rx_frame_err=0, rx_over_err=0, rx_packets=0, \
tx_bytes=0, tx_dropped=0, tx_errors=0, tx_packets=0}
status              : {driver_name=dummy, driver_version="1.0", \
firmware_version=""}
type                : ""
        """ % (iface_uuid, iface_name)

        return template

    def test_list_port_parser(self):
        port_name = 'bond0'
        interfaces = '[047843e4-eb1b-4cdb-8433-4f8f447ff935, ' \
            '9f0bfa61-b0de-402c-b422-e11fca2b812a]'

        listport_output = self.get_list_port_output(port_name, interfaces)

        output_dict = ovsbridges.parse_listport_output(listport_output)
        self.assertEqual('bond0', output_dict.get('name'))
        self.assertEqual(
            [
                '047843e4-eb1b-4cdb-8433-4f8f447ff935',
                '9f0bfa61-b0de-402c-b422-e11fca2b812a'
            ],
            output_dict.get('interfaces')
        )

    def test_listinterface_parser(self):
        output = self.get_list_interfaces_output('dummy1')

        output_dict = ovsbridges.parse_listinterface_output(output)
        self.assertEqual('dummy1', output_dict.get('name'))
        self.assertEqual('down', output_dict.get('admin_state'))
        self.assertEqual('down', output_dict.get('link_state'))
        self.assertEqual('16:bd:8d:f8:aa:f6', output_dict.get('mac_in_use'))
        self.assertEqual(
            {'collisions': '0', 'rx_bytes': '0', 'rx_crc_err': '0',
             'rx_dropped': '0', 'rx_errors': '0', 'rx_frame_err': '0',
             'rx_over_err': '0', 'rx_packets': '0', 'tx_bytes': '0',
             'tx_dropped': '0', 'tx_errors': '0', 'tx_packets': '0'},
            output_dict.get('statistics')
        )

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_create_fails_if_service_not_running(self, mock_run_cmd):
        mock_run_cmd.return_value = ['', 'database connection failed', 1]

        expected_error_msg = "GINOVS00001E"
        with self.assertRaisesRegexp(OperationFailed, expected_error_msg):
            OVSBridgesModel().create({'name': 'bridge'})
            mock_run_cmd.assert_called_once_with(
                ['ovs-vsctl', 'br-exists', 'bridge']
            )

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_get_list(self, mock_run_cmd):
        ovsbr_list = 'ovsbr1\novsbr2\novsbr3\n'
        mock_run_cmd.return_value = [ovsbr_list, '', 0]

        OVSBridgesModel().get_list()
        mock_run_cmd.assert_called_once_with(['ovs-vsctl', 'list-br'])

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_create_fails_if_bridge_exists(self, mock_run_cmd):
        mock_run_cmd.return_value = ['', '', 0]

        expected_error_msg = "GINOVS00003E"
        with self.assertRaisesRegexp(InvalidParameter, expected_error_msg):
            OVSBridgesModel().create({'name': 'bridge'})
            mock_run_cmd.assert_called_once_with(
                ['ovs-vsctl', 'br-exists', 'bridge']
            )

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_create_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 2]
        call_create_br = ['ovs-vsctl', 'add-br', 'bridge']
        create_br_return = ['', '', 0]
        mock_run_cmd_calls = [call(call_br_exists), call(call_create_br)]
        mock_run_cmd.side_effect = [br_exists_return, create_br_return]

        OVSBridgesModel().create({'name': 'bridge'})
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_lookup_zero_ports_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]
        call_list_ports = ['ovs-vsctl', 'list-ports', 'bridge']
        list_ports_return = ['', '', 0]
        mock_run_cmd_calls = [call(call_br_exists), call(call_list_ports)]
        mock_run_cmd.side_effect = [br_exists_return, list_ports_return]

        lookup_dict = OVSBridgeModel().lookup('bridge')
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

        self.assertEqual('bridge', lookup_dict.get('name'))
        self.assertEqual([], lookup_dict.get('ports'))

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_delete_success(self, mock_run_cmd):
        mock_run_cmd.return_value = ['', '', 0]

        OVSBridgeModel().delete('bridge')
        mock_run_cmd.assert_called_once_with(['ovs-vsctl', 'del-br', 'bridge'])

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_lookup_one_interface_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]

        call_list_ports = ['ovs-vsctl', 'list-ports', 'bridge']
        list_ports_return = ['iface1\n', '', 0]

        call_iface1_lookup = ['ovs-vsctl', 'list', 'Port', 'iface1']
        iface1_lookup_output = \
            self.get_list_port_output('iface1', '[single_uuid]')
        iface1_lookup_return = [iface1_lookup_output, '', 0]

        call_iface1_interface_lookup = ['ovs-vsctl', 'list',
                                        'Interface', 'single_uuid']
        interface_lookup_output = \
            self.get_list_interfaces_output('iface1', iface_uuid='single_uuid')
        interface_lookup_return = [interface_lookup_output, '', 0]

        mock_run_cmd_calls = [
            call(call_br_exists),
            call(call_list_ports),
            call(call_iface1_lookup),
            call(call_iface1_interface_lookup),
        ]
        mock_run_cmd.side_effect = [
            br_exists_return,
            list_ports_return,
            iface1_lookup_return,
            interface_lookup_return
        ]

        lookup_dict = OVSBridgeModel().lookup('bridge')
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)
        self.assertEqual('bridge', lookup_dict.get('name'))
        iface1_dict = {
            'type': 'interface',
            'name': 'iface1',
            'admin_state': 'down',
            'link_state': 'down',
            'mac_in_use': '16:bd:8d:f8:aa:f6',
            'statistics': {
                'collisions': '0', 'rx_bytes': '0', 'rx_crc_err': '0',
                'rx_dropped': '0', 'rx_errors': '0', 'rx_frame_err': '0',
                'rx_over_err': '0', 'rx_packets': '0', 'tx_bytes': '0',
                'tx_dropped': '0', 'tx_errors': '0', 'tx_packets': '0'
            }
        }

        self.assertEqual(1, len(lookup_dict.get('ports')))
        self.assertEqual(iface1_dict, lookup_dict.get('ports')[0])

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_ovsbridge_lookup_bond_two_interfaces_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]

        call_list_ports = ['ovs-vsctl', 'list-ports', 'bridge']
        list_ports_return = ['bond0\n', '', 0]

        call_bond0_lookup = ['ovs-vsctl', 'list', 'Port', 'bond0']
        bond0_lookup_output = \
            self.get_list_port_output('bond0', '[iface1_uuid, iface2_uuid]')
        bond0_lookup_return = [bond0_lookup_output, '', 0]

        call_iface1_interface_lookup = ['ovs-vsctl', 'list',
                                        'Interface', 'iface1_uuid']
        interface1_lookup_output = \
            self.get_list_interfaces_output('iface1', iface_uuid='iface1_uuid')
        interface1_lookup_return = [interface1_lookup_output, '', 0]

        call_iface2_interface_lookup = ['ovs-vsctl', 'list',
                                        'Interface', 'iface2_uuid']
        interface2_lookup_output = \
            self.get_list_interfaces_output('iface2', iface_uuid='iface2_uuid')
        interface2_lookup_return = [interface2_lookup_output, '', 0]

        mock_run_cmd_calls = [
            call(call_br_exists),
            call(call_list_ports),
            call(call_bond0_lookup),
            call(call_iface1_interface_lookup),
            call(call_iface2_interface_lookup)
        ]
        mock_run_cmd.side_effect = [
            br_exists_return,
            list_ports_return,
            bond0_lookup_return,
            interface1_lookup_return,
            interface2_lookup_return
        ]

        lookup_dict = OVSBridgeModel().lookup('bridge')
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

        self.assertEqual('bridge', lookup_dict.get('name'))
        self.assertEqual(1, len(lookup_dict.get('ports')))

        iface1_dict = {
            'type': 'interface',
            'name': 'iface1',
            'admin_state': 'down',
            'link_state': 'down',
            'mac_in_use': '16:bd:8d:f8:aa:f6',
            'statistics': {
                'collisions': '0', 'rx_bytes': '0', 'rx_crc_err': '0',
                'rx_dropped': '0', 'rx_errors': '0', 'rx_frame_err': '0',
                'rx_over_err': '0', 'rx_packets': '0', 'tx_bytes': '0',
                'tx_dropped': '0', 'tx_errors': '0', 'tx_packets': '0'
            }
        }

        iface2_dict = {
            'type': 'interface',
            'name': 'iface2',
            'admin_state': 'down',
            'link_state': 'down',
            'mac_in_use': '16:bd:8d:f8:aa:f6',
            'statistics': {
                'collisions': '0', 'rx_bytes': '0', 'rx_crc_err': '0',
                'rx_dropped': '0', 'rx_errors': '0', 'rx_frame_err': '0',
                'rx_over_err': '0', 'rx_packets': '0', 'tx_bytes': '0',
                'tx_dropped': '0', 'tx_errors': '0', 'tx_packets': '0'
            }
        }

        bond0_info = lookup_dict.get('ports')[0]

        self.assertEqual('bond', bond0_info.get('type'))
        self.assertEqual(2, len(bond0_info.get('interfaces')))

        ifaces_array = bond0_info.get('interfaces')
        self.assertEqual(iface1_dict, ifaces_array[0])
        self.assertEqual(iface2_dict, ifaces_array[1])

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_interface_add_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]
        call_create_port = ['ovs-vsctl', 'add-port', 'bridge', 'dummy1']
        create_port_return = ['', '', 0]
        mock_run_cmd_calls = [call(call_br_exists), call(call_create_port)]
        mock_run_cmd.side_effect = [br_exists_return, create_port_return]

        OVSBridgeModel().add_interface('bridge', 'dummy1')
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_interface_add_already_exists(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]

        call_create_port = \
            ['ovs-vsctl', 'add-port', 'bridge', 'iface']
        error_msg = 'ovs-vsctl: cannot create a port named ' \
            '%(port)s because a port named %(port)s already exists ' \
            'on bridge %(bridge)s' % {'port': 'iface', 'bridge': 'bridge'}
        create_port_return = ['', error_msg, 1]
        mock_run_cmd_calls = [call(call_br_exists), call(call_create_port)]
        mock_run_cmd.side_effect = [br_exists_return, create_port_return]

        expected_error_msg = "GINOVS00005E"
        with self.assertRaisesRegexp(InvalidParameter, expected_error_msg):
            OVSBridgeModel().add_interface('bridge', 'iface')
            mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_interface_del(self, mock_run_cmd):
        cmd = ['ovs-vsctl', 'del-port', 'bridge', 'dummy1']
        mock_run_cmd.return_value = ['', '', 0]

        OVSBridgeModel().del_interface('bridge', 'dummy1')
        mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_bond_add_fails_if_less_than_two_interfaces(self, mock_run_cmd):
        cmd = ['ovs-vsctl', 'br-exists', 'bridge']
        mock_run_cmd.return_value = ['', '', 0]

        expected_error_msg = "GINOVS00006E"
        with self.assertRaisesRegexp(InvalidParameter, expected_error_msg):
            OVSBridgeModel().add_bond('br', 'bond0', ['iface'])
            mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_bond_add_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]

        call_create_bond = [
            'ovs-vsctl', 'add-bond', 'bridge', 'bond0', 'iface1', 'iface2'
        ]
        create_bond_return = ['', '', 0]

        mock_run_cmd_calls = [call(call_br_exists), call(call_create_bond)]
        mock_run_cmd.side_effect = [br_exists_return, create_bond_return]

        OVSBridgeModel().add_bond('bridge', 'bond0', ['iface1', 'iface2'])
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_bond_del(self, mock_run_cmd):
        cmd = ['ovs-vsctl', 'del-port', 'bridge', 'bond0']
        mock_run_cmd.return_value = ['', '', 0]

        OVSBridgeModel().del_bond('bridge', 'bond0')
        mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.ovsbridges.run_command')
    def test_edit_bond_success(self, mock_run_cmd):
        call_br_exists = ['ovs-vsctl', 'br-exists', 'bridge']
        br_exists_return = ['', '', 0]

        call_get_bridge_ports = ['ovs-vsctl', 'list-ports', 'bridge']
        get_bridge_ports_return = ['bond0\n', '', 0]

        call_bond0_lookup = ['ovs-vsctl', 'list', 'Port', 'bond0']
        bond0_lookup_output = \
            self.get_list_port_output('bond0', '[iface1_uuid, iface2_uuid]')
        bond0_lookup_return = [bond0_lookup_output, '', 0]

        call_iface1_interface_lookup = ['ovs-vsctl', 'list',
                                        'Interface', 'iface1_uuid']
        interface1_lookup_output = \
            self.get_list_interfaces_output('iface1', iface_uuid='iface1_uuid')
        interface1_lookup_return = [interface1_lookup_output, '', 0]

        call_iface2_interface_lookup = ['ovs-vsctl', 'list',
                                        'Interface', 'iface2_uuid']
        interface2_lookup_output = \
            self.get_list_interfaces_output('iface2', iface_uuid='iface2_uuid')
        interface2_lookup_return = [interface2_lookup_output, '', 0]

        interface_row_exists = \
            'ovs-vsctl --id=@%(iface)s get ' \
            'Interface %(iface)s' % {'iface': 'iface1'}
        interface_row_exists_cmd = interface_row_exists.split()
        interface_row_exists_return = ['', '', 0]

        del_bond0_iface1 = \
            'ovs-vsctl --id=@%(iface)s get Interface %(iface)s -- remove ' \
            'Port %(bond)s interfaces @%(iface)s'
        del_bond0_iface1 = \
            del_bond0_iface1 % {'iface': 'iface1', 'bond': 'bond0'}
        del_bond0_iface1_cmd = del_bond0_iface1.split()
        del_bond0_iface1_return = ['', '', 0]

        add_bond0_iface3 = \
            'ovs-vsctl --id=@%(iface)s create Interface name=%(iface)s ' \
            '-- add Port %(bond)s interfaces @%(iface)s'
        add_bond0_iface3 = \
            add_bond0_iface3 % {'iface': 'iface3', 'bond': 'bond0'}
        add_bond0_iface3_cmd = add_bond0_iface3.split()
        add_bond0_iface3_return = ['iface3_uuid', '', 0]

        mock_run_cmd_calls = [
            call(call_br_exists),
            call(call_get_bridge_ports),
            call(call_bond0_lookup),
            call(call_iface1_interface_lookup),
            call(call_iface2_interface_lookup),
            call(interface_row_exists_cmd),
            call(del_bond0_iface1_cmd),
            call(add_bond0_iface3_cmd)
        ]

        mock_run_cmd.side_effect = [
            br_exists_return,
            get_bridge_ports_return,
            bond0_lookup_return,
            interface1_lookup_return,
            interface2_lookup_return,
            interface_row_exists_return,
            del_bond0_iface1_return,
            add_bond0_iface3_return
        ]

        OVSBridgeModel().modify_bond('bridge', 'bond0', 'iface1', 'iface3')
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)
