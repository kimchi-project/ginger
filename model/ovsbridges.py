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

from wok.exception import InvalidParameter, NotFoundError, OperationFailed
from wok.utils import run_command, wok_log


def parse_generic_one_item_per_line_output(output):
    """
    Sample generic output:

elem1
elem2
elem3
    """
    items = output.strip().split('\n')
    if len(items) == 1 and items[0] == '':
        items = []
    return items


def parse_listbr_output(listbr_output):
    return parse_generic_one_item_per_line_output(listbr_output)


def parse_listports_output(listports_output):
    return parse_generic_one_item_per_line_output(listports_output)


def parse_listport_output(output):
    """
    Sample output of ' ovs-vsctl list Port <port>'

_uuid               : 8ed84b43-20d7-4e14-a636-8b3b4c77f6b8
bond_active_slave   : []
bond_downdelay      : 0
bond_fake_iface     : false
bond_mode           : []
bond_updelay        : 0
external_ids        : {}
fake_bridge         : false
interfaces          : [cf3143d6-719c-4467-ae14-f31d950cf48c]
lacp                : []
mac                 : []
name                : "dummy0"
other_config        : {}
qos                 : []
rstp_statistics     : {}
rstp_status         : {}
statistics          : {}
status              : {}
tag                 : []
trunks              : []
vlan_mode           : []
    """
    lines = output.strip().split('\n')
    port = {}
    for line in lines:
        tokens = line.split(':', 1)
        if len(tokens) != 2:
            continue
        key = tokens[0].strip()
        value = tokens[1].strip()
        if key == 'name':
            port['name'] = value.strip('"')
        elif key == 'interfaces':
            ifaces = []
            ifaces_str = value.strip('[]')
            for iface in ifaces_str.split(','):
                ifaces.append(iface.strip())
            port['interfaces'] = ifaces

    return port


def parse_listinterface_output(output):
    """
    Sample output of 'ovs-vsctl list Interface <iface>'

_uuid               : cf3143d6-719c-4467-ae14-f31d950cf48c
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
ifindex             : 15
ingress_policing_burst: 0
ingress_policing_rate: 0
lacp_current        : []
link_resets         : 0
link_speed          : []
link_state          : down
lldp                : {}
mac                 : []
mac_in_use          : "ca:6f:1c:5d:6d:a4"
mtu                 : 1500
name                : "dummy0"
ofport              : 1
ofport_request      : []
options             : {}
other_config        : {}
statistics          : {collisions=0, rx_bytes=0, rx_crc_err=0, \
rx_dropped=0, rx_errors=0, rx_frame_err=0, rx_over_err=0, rx_packets=0, \
tx_bytes=0, tx_dropped=0, tx_errors=0, tx_packets=0}
status              : {driver_name=dummy, driver_version="1.0", \
firmware_version=""}
type                : ""
    """
    def get_stats_dict(statistics_str):
        stats = {}
        statistics_str = statistics_str.strip('{}')
        for key_values in statistics_str.split(','):
            key, value = key_values.split('=')
            key = key.strip()
            value = value.strip()
            stats[key] = value
        return stats

    lines = output.strip().split('\n')
    interface = {}
    for line in lines:
        tokens = line.split(':', 1)
        if len(tokens) != 2:
            continue
        key = tokens[0].strip()
        value = tokens[1].strip()
        if key in ['name', 'mac_in_use']:
            interface[key] = value.strip('"')
        elif key in ['admin_state', 'link_state']:
            interface[key] = value
        elif key == 'statistics':
            interface[key] = get_stats_dict(value)

    return interface


def run_ovsvsctl_command(cmd):
    out, err, returncode = run_command(cmd)
    if returncode != 0:
        if 'database connection failed' in err:
            wok_log.info(
                'Database connection error when executing an ovs-vsctl '
                'command. Is openvswitch service running?'
            )
            raise OperationFailed('GINOVS00001E')

    return out, err, returncode


def ovsbridge_exists(ovsbridge):
    cmd = ['ovs-vsctl', 'br-exists', ovsbridge]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode not in [0, 2]:
        wok_log.error('Error executing ovs-vsctl br-exists: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})
    else:
        return returncode == 0


def get_ovsbridges_list():
    cmd = ['ovs-vsctl', 'list-br']
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl list-br: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})
    else:
        return parse_listbr_output(out)


def create_ovsbridge(ovsbridge):
    if ovsbridge_exists(ovsbridge):
        wok_log.error(
            'Error creating ovsbridge %s. OVSbridge already '
            'exists.' % ovsbridge
        )
        raise InvalidParameter('GINOVS00003E', {'name': ovsbridge})

    cmd = ['ovs-vsctl', 'add-br', ovsbridge]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl add-br: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})


def delete_ovsbridge(ovsbridge):
    cmd = ['ovs-vsctl', 'del-br', ovsbridge]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl del-br: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})


def get_bridge_ports(ovsbridge):
    cmd = ['ovs-vsctl', 'list-ports', ovsbridge]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl list-ports: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})
    else:
        return parse_listports_output(out)


def get_interface_info(uuid):
    cmd = ['ovs-vsctl', 'list', 'Interface', uuid]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl list Interface : %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})
    else:
        info = parse_listinterface_output(out)
        info['type'] = 'interface'
        return info


def get_port_info(port):
    cmd = ['ovs-vsctl', 'list', 'Port', port]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl list Port : %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})

    else:
        port_info = parse_listport_output(out)
        interfaces = port_info['interfaces']
        if len(interfaces) == 1:
            iface_uuid = interfaces[0]
            port_info = get_interface_info(iface_uuid)
        elif len(interfaces) > 1:
            port_info['type'] = 'bond'
            bond_ifaces = []
            for iface_uuid in interfaces:
                bond_ifaces.append(get_interface_info(iface_uuid))
            port_info['interfaces'] = bond_ifaces

        return port_info


def add_interface_to_ovsbridge(ovsbridge, interface):
    if not ovsbridge_exists(ovsbridge):
        wok_log.error(
            'Error adding interface %s for ovsbridge %s. OVSbridge '
            'does not exist.' % (interface, ovsbridge)
        )
        raise NotFoundError('GINOVS00004E', {'name': ovsbridge})

    cmd = ['ovs-vsctl', 'add-port', ovsbridge, interface]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl add-port: %s ' % err)
        port_exists_err = 'port named %s already exists on ' \
            'bridge %s' % (interface, ovsbridge)
        if port_exists_err in err:
            raise InvalidParameter(
                'GINOVS00005E',
                {'name': ovsbridge, 'port': interface}
            )
        else:
            raise OperationFailed('GINOVS00002E', {'err': err})


def del_port_from_ovsbridge(ovsbridge, port):
    cmd = ['ovs-vsctl', 'del-port', ovsbridge, port]
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl del-port: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})


def add_bond_to_ovsbridge(ovsbridge, bond, bond_ifaces):
    if not ovsbridge_exists(ovsbridge):
        wok_log.error(
            'Error creating bond %s for ovsbridge %s. OVSbridge does not '
            'exist.' % (bond, ovsbridge)
        )
        raise NotFoundError('GINOVS00003E', {'name': ovsbridge})

    if len(bond_ifaces) < 2:
        raise InvalidParameter('GINOVS00006E')

    cmd = ['ovs-vsctl', 'add-bond', ovsbridge, bond] + bond_ifaces
    out, err, returncode = run_ovsvsctl_command(cmd)
    if returncode != 0:
        wok_log.error('Error executing ovs-vsctl add-bond: %s ' % err)
        raise OperationFailed('GINOVS00002E', {'err': err})


def change_bond_configuration(ovsbridge, bond, iface_del, iface_add):

    def bond_exists_in_ovsbridge(ovsbridge, bond):
        if not ovsbridge_exists(ovsbridge):
            return False

        ports = get_bridge_ports(ovsbridge)
        if bond not in ports:
            return False

        bond_info = get_port_info(bond)
        if bond_info['type'] != 'bond':
            return False

        return True

    def interface_row_exists(interface):
        cmd = 'ovs-vsctl --id=@%(iface)s get Interface %(iface)s'
        cmd = cmd % {'iface': interface}
        out, err, returncode = run_ovsvsctl_command(cmd.split())
        if returncode != 0:
            return False

        return True

    if not bond_exists_in_ovsbridge(ovsbridge, bond):
        raise InvalidParameter(
            'GINOVS00007E', {'bridge': ovsbridge, 'bond': bond}
        )

    if not interface_row_exists(iface_del):
        raise InvalidParameter('GINOVS00008E', {'iface': iface_del})

    cmd = 'ovs-vsctl --id=@%(iface)s get Interface %(iface)s -- remove ' \
          'Port %(bond)s interfaces @%(iface)s'
    cmd = cmd % {'iface': iface_del, 'bond': bond}
    out, err, returncode = run_ovsvsctl_command(cmd.split())
    if returncode != 0:
        raise OperationFailed('GINOVS00002E', {'err': err})

    cmd = 'ovs-vsctl --id=@%(iface)s create Interface name=%(iface)s ' \
          '-- add Port %(bond)s interfaces @%(iface)s'
    cmd = cmd % {'iface': iface_add, 'bond': bond}
    out, err, returncode = run_ovsvsctl_command(cmd.split())
    if returncode != 0:
        raise OperationFailed('GINOVS00002E', {'err': err})


class OVSBridgesModel(object):

    def is_feature_available(self):
        _, _, returncode = run_command(['ovs-vsctl'])
        if returncode == 127:
            return False
        else:
            return True

    def create(self, params):
        ovsbridge = params['name']
        create_ovsbridge(ovsbridge)
        wok_log.info('OVS bridge %s created.' % ovsbridge)
        return ovsbridge

    def get_list(self):
        return get_ovsbridges_list()


class OVSBridgeModel(object):

    def lookup(self, name):
        if not ovsbridge_exists(name):
            wok_log.error(
                'Error retrieving ovsbridge %s. OVSbridge does not '
                'exist.' % name
            )
            raise NotFoundError('GINOVS00004E', {'name': name})

        br_ports = get_bridge_ports(name)
        ports_array = []
        if br_ports:
            for br_port in br_ports:
                port_info = get_port_info(br_port)
                if port_info:
                    ports_array.append(port_info)

        lookup_dict = {'name': name, 'ports': ports_array}

        return lookup_dict

    def delete(self, name):
        delete_ovsbridge(name)
        wok_log.info('OVS Bridge %s deleted.' % name)

    def add_interface(self, name, interface):
        add_interface_to_ovsbridge(name, interface)

    def del_interface(self, name, interface):
        del_port_from_ovsbridge(name, interface)

    def add_bond(self, name, bond, interfaces):
        add_bond_to_ovsbridge(name, bond, interfaces)

    def del_bond(self, name, bond):
        del_port_from_ovsbridge(name, bond)

    def modify_bond(self, name, bond, iface_del, iface_add):
        change_bond_configuration(name, bond, iface_del, iface_add)
