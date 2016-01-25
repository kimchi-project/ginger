#
# Project Ginger
#
# Copyright IBM, Corp. 2016
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

from wok.plugins.ginger.model.ibm_sep import SepModel, SubscribersModel
from wok.plugins.ginger.model.ibm_sep import SubscriptionModel


class IBMSepTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_sep_lookup(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]

        lookup = SepModel().lookup(None)

        cmd = ['systemctl', 'status', 'sepctl']
        mock_run_command.assert_called_once_with(cmd)

        self.assertEqual(lookup, {"status": "running"})

    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_sep_start(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]

        SepModel().start()

        cmd = ['systemctl', 'start', 'sepctl']
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_sep_stop(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]

        SepModel().stop()

        cmd = ['systemctl', 'stop', 'sepctl']
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_subscribers_get_list(self, mock_run_command):
        cmd_output = "Subscriber_1: hostname=localhost,port=1,community=com\n"
        mock_run_command.return_value = [cmd_output, "", 0]

        sub_list = SubscribersModel().get_list()

        cmd = ['/opt/ibm/seprovider/bin/getSubscriber']
        mock_run_command.assert_called_once_with(cmd)

        self.assertEqual(sub_list, ['localhost'])

    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_subscribers_create(self, mock_run_command):
        mock_run_command.return_value = ["", "", 0]

        params = {
            'hostname': 'fake_hostname',
            'port': 12345,
            'community': 'ginger'
        }
        added = SubscribersModel().create(params)

        cmd = ['/opt/ibm/seprovider/bin/subscribe', '-h', 'fake_hostname',
               '-p', '12345', '-c', 'ginger']
        mock_run_command.assert_called_once_with(cmd)

        self.assertEqual(added, 'fake_hostname')

    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_subscription_lookup(self, mock_run_command):
        cmd_output = "Subscriber_1: hostname=localhost,port=1,community=com\n"
        mock_run_command.return_value = [cmd_output, "", 0]

        lookup = SubscriptionModel().lookup('localhost')

        cmd = ['/opt/ibm/seprovider/bin/getSubscriber']
        mock_run_command.assert_called_once_with(cmd)

        self.assertEqual(
            lookup,
            {'hostname': 'localhost', 'port': '1', 'community': 'com'}
        )

    @mock.patch('wok.plugins.ginger.model.ibm_sep.SubscriptionModel.lookup')
    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_subscription_delete(self, mock_run_command, mock_lookup):
        mock_run_command.return_value = ["", "", 0]
        mock_lookup.return_value = {'hostname': 'fake_hostname'}

        SubscriptionModel().delete('fake_hostname')

        mock_lookup.assert_called_once_with('fake_hostname')

        cmd = ['/opt/ibm/seprovider/bin/unsubscribe', '-h', 'fake_hostname']
        mock_run_command.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.ibm_sep.SubscriptionModel.delete')
    @mock.patch('wok.plugins.ginger.model.ibm_sep.SubscriptionModel.lookup')
    @mock.patch('wok.plugins.ginger.model.ibm_sep.run_command')
    def test_subscription_update(self, mock_run_command, mock_lookup,
                                 mock_delete):

        mock_run_command.return_value = ["", "", 0]
        mock_lookup.return_value = {'hostname': 'fake_hostname'}

        params = {
            'hostname': 'fake_hostname2',
            'port': 67890,
            'community': 'ginger2'
        }
        SubscriptionModel().update('fake_hostname', params)

        mock_lookup.assert_called_once_with('fake_hostname')
        mock_delete.assert_called_once_with('fake_hostname')

        cmd = ['/opt/ibm/seprovider/bin/subscribe', '-h', 'fake_hostname2',
               '-p', '67890', '-c', 'ginger2']
        mock_run_command.assert_called_once_with(cmd)
