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

import wok.plugins.ginger.model.powermanagement as powermanag
from wok.exception import InvalidOperation
from wok.plugins.ginger.model.powermanagement import PowerProfilesModel
from wok.plugins.ginger.model.powermanagement import PowerProfileModel


def mock_powerprofiles_init(self):
    self.error = None


def mock_powerprofile_init(self):
    self.active_powerprofile = 'default'


class PowerManagementTests(unittest.TestCase):

    def setUp(self):
        PowerProfilesModel.__init__ = mock_powerprofiles_init
        self.power_profiles_model = PowerProfilesModel()

        PowerProfileModel.__init__ = mock_powerprofile_init
        self.power_profile_model = PowerProfileModel()

    def test_tunedadm_list_parse(self):
        tuned_list_output = """\
Available profiles:
- balanced                    - General non-specialized tuned profile
- desktop                     - Optmize for the desktop use-case
- latency-performance         - Optimize for deterministic performance\
at the cost of increased power consumption
- network-latency             - Optimize for deterministic performance\
at the cost of increased power consumption, focused on low latency network\
performance
- network-throughput          - Optimize for streaming network throughput.\
  Generally only necessary on older CPUs or 40G+ networks.
- powersave                   - Optimize for low power consumption
- throughput-performance      - Broadly applicable tuning that provides\
 excellent performance across a variety of common server workloads.\
  This is the default profile for RHEL7.
- virtual-guest               - Optimize for running inside a virtual guest.
- virtual-host                - Optimize for running KVM guests
Current active profile: throughput-performance"""
        profiles = powermanag.parse_tunedadm_list(tuned_list_output)
        self.assertEqual(9, len(profiles))
        self.assertIn('balanced', profiles)
        self.assertIn('desktop', profiles)
        self.assertIn('latency-performance', profiles)
        self.assertIn('network-latency', profiles)
        self.assertIn('network-throughput', profiles)
        self.assertIn('powersave', profiles)
        self.assertIn('throughput-performance', profiles)
        self.assertIn('virtual-guest', profiles)
        self.assertIn('virtual-host', profiles)

    def test_old_tunedadm_list_parse(self):
        tuned_list_output = """\
Available profiles:
- balanced
- desktop
- latency-performance
- network-latency
- network-throughput
- powersave
- throughput-performance
- virtual-guest
- virtual-host
Current active profile: throughput-performance"""
        profiles = powermanag.parse_tunedadm_list(tuned_list_output)
        self.assertEqual(9, len(profiles))
        self.assertIn('balanced', profiles)
        self.assertIn('desktop', profiles)
        self.assertIn('latency-performance', profiles)
        self.assertIn('network-latency', profiles)
        self.assertIn('network-throughput', profiles)
        self.assertIn('powersave', profiles)
        self.assertIn('throughput-performance', profiles)
        self.assertIn('virtual-guest', profiles)
        self.assertIn('virtual-host', profiles)

    @mock.patch('wok.plugins.ginger.model.powermanagement.run_command')
    def test_tuned_daemon_offline(self, mock_run_command):
        mock_run_command.return_value = ["", "", 2]
        with self.assertRaisesRegexp(InvalidOperation, 'GINPOWER0002'):
            self.power_profiles_model.get_list()
            mock_run_command.assert_called_once_with(['tuned-adm', 'list'])

    @mock.patch('wok.plugins.ginger.model.powermanagement.run_command')
    def test_powermanagement_get_list(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        self.power_profiles_model.get_list()
        mock_run_command.assert_called_once_with(['tuned-adm', 'list'])

    def test_powermanagement_lookup(self):
        lookup = self.power_profile_model.lookup('test_profile')
        self.assertEqual(lookup, {"name": 'test_profile', "active": False})

    @mock.patch('wok.plugins.ginger.model.powermanagement.run_command')
    def test_powermanagement_update(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]
        self.power_profile_model.update(
            'test_active_profile',
            {'active': True}
        )
        tuned_cmd = ["tuned-adm", "profile", "test_active_profile"]
        mock_run_command.assert_called_once_with(tuned_cmd)

        self.power_profile_model.update('default', {'active': True})
        tuned_cmd = ["tuned-adm", "profile", "default"]
        mock_run_command.assert_called_with(tuned_cmd)
