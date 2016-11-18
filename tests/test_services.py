# -*- coding: utf-8 -*-
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

from wok.exception import NotFoundError

import wok.plugins.ginger.model.services as services
from wok.plugins.ginger.model.services import ServiceModel
from wok.plugins.ginger.model.services import ServicesModel


class ServicesTests(unittest.TestCase):

    def get_systemlist_output(self):
        return """\
UNIT FILE                                   STATE
timedatex.service                           enabled
tuned.service                               enabled
udisks2.service                             disabled
unbound-anchor.service                      static
upower.service                              disabled
usbmuxd.service                             static
user@.service                               static
vgauthd.service                             enabled
virtlockd.service                           indirect
virtlogd.service                            indirect
vmtoolsd.service                            enabled
wacom-inputattach@.service                  static
wokd.service                                enabled
wpa_supplicant.service                      disabled
wst-schedule.service                        disabled
yum-makecache.service                       static
zram.service                                static

263 unit files listed."""

    def get_systemctl_show_output(self):
        return """\
ControlGroup=/system.slice/wokd.service
Description=Wok - Webserver Originated from Kimchi
LoadState=loaded
ActiveState=active
SubState=running
UnitFileState=disabled\n"""

    def get_systemdcgls_output(self):
        return """\
/system.slice/wokd.service:
`-25775 python2 /usr/bin/wokd
`-26011 nginx: master process nginx -c /etc/nginx/...
`-26012 nginx: worker process\n"""

    def test_systemd_cgls_output(self):
        systemdcgls_output = self.get_systemdcgls_output()

        output_dict = services.parse_systemd_cgls_output(
            systemdcgls_output
        )
        self.assertEqual(output_dict['name'], '/system.slice/wokd.service')
        self.assertEqual(len(output_dict.get('processes')), 3)

        procs = {
            '25775': 'python2 /usr/bin/wokd',
            '26011': 'nginx: master process nginx -c /etc/nginx/...',
            '26012': 'nginx: worker process'
        }

        self.assertEqual(procs, output_dict.get('processes'))

    def test_systemctl_show_output(self):
        systemctlshow_output = self.get_systemctl_show_output()

        output_dict = services.parse_systemctlshow_output(systemctlshow_output)
        self.assertEqual(
            output_dict.get('cgroup'), '/system.slice/wokd.service'
        )
        self.assertEqual(
            output_dict.get('desc'), 'Wok - Webserver Originated from Kimchi'
        )
        self.assertEqual(output_dict.get('load'), 'loaded')
        self.assertEqual(output_dict.get('active'), 'active')
        self.assertEqual(output_dict.get('sub'), 'running')
        self.assertEqual(output_dict.get('autostart'), False)

    def test_systemctl_list_output(self):
        output = self.get_systemlist_output()
        expected_output = [
            'timedatex.service', 'tuned.service',
            'udisks2.service', 'unbound-anchor.service', 'upower.service',
            'usbmuxd.service', 'vgauthd.service', 'virtlockd.service',
            'virtlogd.service', 'vmtoolsd.service', 'wokd.service',
            'wpa_supplicant.service', 'wst-schedule.service',
            'yum-makecache.service', 'zram.service']

        output_array = \
            services.parse_systemctllist_output(output)

        self.assertEqual(len(expected_output), len(output_array))

        for service in expected_output:
            self.assertIn(service, output_array)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_services_get_list(self, mock_run_cmd):
        mock_run_cmd.return_value = [self.get_systemlist_output(), '', 0]

        services_list = ServicesModel().get_list()
        mock_run_cmd.assert_called_once_with(
            ['systemctl', 'list-unit-files', '--no-pager', '--type=service']
        )

        expected_output = [
            'timedatex.service', 'tuned.service',
            'udisks2.service', 'unbound-anchor.service', 'upower.service',
            'usbmuxd.service', 'vgauthd.service', 'virtlockd.service',
            'virtlogd.service', 'vmtoolsd.service', 'wokd.service',
            'wpa_supplicant.service', 'wst-schedule.service',
            'yum-makecache.service', 'zram.service']

        for service in expected_output:
            self.assertIn(service, services_list)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_interface_add_already_exists(self, mock_run_cmd):
        service_exists = [
            'systemctl', 'show', 'unknown.service', '--property=LoadError'
        ]
        not_found_output = \
            'LoadError=org.freedesktop.DBus.Error.FileNotFound '\
            '"No such file or directory"'
        mock_run_cmd.return_value = [not_found_output, '', 0]

        expected_error_msg = "GINSERV00002E"
        with self.assertRaisesRegexp(NotFoundError, expected_error_msg):
            ServiceModel().lookup('unknown.service')
            mock_run_cmd.assert_called_once_with(service_exists)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_service_lookup(self, mock_run_cmd):
        call_service_exists = [
            'systemctl', 'show', 'wokd.service', '--property=LoadError'
        ]
        service_exists_return = ['LoadError=""', '', 0]

        call_systemctl_show = [
            'systemctl', 'show', 'wokd.service',
            '--property=LoadState,ActiveState,'
            'SubState,Description,UnitFileState,ControlGroup'
        ]
        systemctl_show_return = [self.get_systemctl_show_output(), '', 0]

        call_systemd_cgls = ['systemd-cgls', '--no-pager',
                             '/system.slice/wokd.service']
        systemd_cgls_return = [self.get_systemdcgls_output(), '', 0]

        mock_run_cmd_calls = [
            call(call_service_exists),
            call(call_systemctl_show),
            call(call_systemd_cgls)
        ]
        mock_run_cmd.side_effect = [
            service_exists_return,
            systemctl_show_return,
            systemd_cgls_return
        ]

        lookup_dict = ServiceModel().lookup('wokd.service')
        mock_run_cmd.assert_has_calls(mock_run_cmd_calls)

        self.assertEqual(
            lookup_dict.get('desc'), 'Wok - Webserver Originated from Kimchi'
        )
        self.assertEqual(lookup_dict.get('name'), 'wokd.service')
        self.assertEqual(lookup_dict.get('load'), 'loaded')
        self.assertEqual(lookup_dict.get('active'), 'active')
        self.assertEqual(lookup_dict.get('sub'), 'running')
        self.assertEqual(lookup_dict.get('autostart'), False)

        cgroup_dict = {
            'name': '/system.slice/wokd.service',
            'processes': {
                '25775': 'python2 /usr/bin/wokd',
                '26011': 'nginx: master process nginx -c '
                         '/etc/nginx/...',
                '26012': 'nginx: worker process'
            }
        }

        self.assertEqual(lookup_dict.get('cgroup'), cgroup_dict)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_service_enable(self, mock_run_cmd):
        cmd = ['systemctl', 'enable', 'wokd.service']
        mock_run_cmd.return_value = ['', '', 0]
        ServiceModel().enable('wokd.service')
        mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_service_disable(self, mock_run_cmd):
        cmd = ['systemctl', 'disable', 'wokd.service']
        mock_run_cmd.return_value = ['', '', 0]
        ServiceModel().disable('wokd.service')
        mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_service_start(self, mock_run_cmd):
        cmd = ['systemctl', 'start', 'wokd.service']
        mock_run_cmd.return_value = ['', '', 0]
        ServiceModel().start('wokd.service')
        mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_service_stop(self, mock_run_cmd):
        cmd = ['systemctl', 'stop', 'wokd.service']
        mock_run_cmd.return_value = ['', '', 0]
        ServiceModel().stop('wokd.service')
        mock_run_cmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.services.run_command')
    def test_service_restart(self, mock_run_cmd):
        cmd = ['systemctl', 'restart', 'wokd.service']
        mock_run_cmd.return_value = ['', '', 0]
        ServiceModel().restart('wokd.service')
        mock_run_cmd.assert_called_once_with(cmd)
