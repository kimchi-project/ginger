import ethtool
import netinfo
import os
import time
import nw_cfginterfaces_utils

from nw_cfginterfaces_utils import CfgInterfacesHelper
from wok.utils import wok_log, run_command
from wok.exception import OperationFailed


cfgInterfacesHelper = CfgInterfacesHelper()


class InterfacesHelper(object):
    """
    Class to help the interfaces perform some operations.
    """

    def activate_iface(self, ifacename):
        wok_log.info('Bring up an interface ' + ifacename)
        iface_type = netinfo.get_interface_type(ifacename)
        if iface_type == "Ethernet":
            cmd_ipup = ['ip', 'link', 'set', '%s' % ifacename, 'up']
            out, error, returncode = run_command(cmd_ipup)
            if returncode != 0:
                wok_log.error(
                    'Unable to bring up the interface on ' + ifacename +
                    ', ' + error)
                raise OperationFailed('GINNET0059E', {'name': ifacename,
                                                      'error': error})
            # Some times based on system load, it takes few seconds to
            # reflect the  /sys/class/net files upon execution of 'ip link
            # set' command.  Following snippet is to wait util files get
            # reflect.
            timeout = self.wait_time(ifacename)
            if timeout == 5:
                wok_log.warn("Time-out has happened upon execution of 'ip "
                             "link set <interface> up', hence behavior of "
                             "activating an interface may not as expected.")
            else:
                wok_log.info('Successfully brought up the interface ' +
                             ifacename)
        wok_log.info('Activating an interface ' + ifacename)
        cmd_ifup = ['ifup', '%s' % ifacename]
        out, error, returncode = run_command(cmd_ifup)
        if returncode != 0:
            wok_log.error(
                'Unable to activate the interface on ' + ifacename +
                ', ' + error)
            raise OperationFailed('GINNET0016E',
                                  {'name': ifacename, 'error': error})
        wok_log.info(
            'Connection successfully activated for the interface ' + ifacename)

    def deactivate_iface(self, ifacename):
        wok_log.info('Deactivating an interface ' + ifacename)
        cmd_ifdown = ['ifdown', '%s' % ifacename]
        out, error, returncode = run_command(cmd_ifdown)
        if returncode != 0:
            wok_log.error(
                'Unable to deactivate the interface on ' + ifacename +
                ', ' + error)
            raise OperationFailed('GINNET0017E',
                                  {'name': ifacename, 'error': error})
        wok_log.info(
            'Connection successfully deactivated for the interface ' +
            ifacename)

        wok_log.info('Bringing down an interface ' + ifacename)
        iface_type = netinfo.get_interface_type(ifacename)
        if iface_type == "Ethernet":
            cmd_ipdown = ['ip', 'link', 'set', '%s' % ifacename, 'down']
            out, error, returncode = run_command(cmd_ipdown)
            if returncode != 0:
                wok_log.error(
                    'Unable to bring down the interface on ' + ifacename +
                    ', ' + error)
                raise OperationFailed('GINNET0060E', {'name': ifacename,
                                                      'error': error})
            # Some times based on system load, it takes few seconds to
            # reflect the  /sys/class/net files upon execution of 'ip link
            # set' command. Following snippet is to wait util files get
            # reflect.
            timeout = self.wait_time(ifacename)
            if timeout == 5:
                wok_log.warn("Time-out has happened upon execution of 'ip "
                             "link set <interface> down', hence behavior of "
                             "activating an interface may not as expected.")
            else:
                wok_log.info('Successfully brought down the interface ' +
                             ifacename)
        vlan_or_bond = [nw_cfginterfaces_utils.IFACE_BOND,
                        nw_cfginterfaces_utils.IFACE_VLAN]
        if iface_type in vlan_or_bond:
            if ifacename in ethtool.get_devices():
                cmd_ip_link_del = ['ip', 'link', 'delete', '%s' % ifacename]
                out, error, returncode = run_command(cmd_ip_link_del)
                if returncode != 0 and ifacename in ethtool.get_devices():
                    wok_log.error('Unable to delete the interface ' +
                                  ifacename + ', ' + error)
                raise OperationFailed('GINNET0017E', {'name': ifacename,
                                                      'error': error})

    def wait_time(self, ifacename):
        timeout = 0
        while timeout < 5:
            pathtocheck = "/sys/class/net/%s/operstate"
            if os.path.exists(pathtocheck % ifacename):
                break
            else:
                timeout += 0.5
                time.sleep(0.5)
        return timeout
