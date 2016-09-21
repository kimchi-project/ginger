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
import wok.plugins.ginger.model.utils as utils


class ISCSITargetsUnitTests(unittest.TestCase):
    """
    Unit tests for iSCSI targets
    """

    def test_iscsi_discovery(self):
        discover_output = \
            """9.193.84.125:3260,1 iqn.2015-06.com.example.test:target1
            9.193.84.125:3260,1 iqn.2015-06.com.example.test:target2"""
        parsed_output = utils.parse_iscsi_discovery(discover_output)
        sample_output = parsed_output[0]
        self.assertEqual(
            sample_output['iqn'],
            "iqn.2015-06.com.example.test:target1")
        self.assertEqual(sample_output['target_ipaddress'], "9.193.84.125")
        self.assertEqual(sample_output['target_port'], "3260")


class ISCSIAuthUnitTests(unittest.TestCase):

    def test_get_iscsi_auth_info(self):
        data = 'node.session.auth.password = pass3\n' \
               'node.session.auth.username = user2\n' \
               'node.session.auth.authmethod = CHAP\n' \
               'discovery.sendtargets.auth.authmethod = CHAP\n' \
               'discovery.sendtargets.auth.username_in = user1\n' \
               'discovery.sendtargets.auth.password_in = pass\n'
        open_mock = mock.mock_open(read_data=data)
        open_mock.return_value.readlines.return_value = data.split('\n')
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            auth_info = utils.get_iscsi_auth_info()
            self.assertEquals(
                'CHAP', auth_info['node.session.auth.authmethod'])
            self.assertEquals(
                'CHAP', auth_info['discovery.sendtargets.auth.authmethod'])
            self.assertEquals('pass3', auth_info['node.session.auth.password'])

    @mock.patch('wok.plugins.ginger.model.utils.os', autospec=True)
    def test_get_iscsi_iqn_auth_info(self, mock_os):
        mock_os.path.exists.return_value = True
        mock_os.listdir.return_value = ['a']
        data = 'node.session.auth.password = pass3\n' \
               'node.session.auth.username = user2\n' \
               'node.session.auth.authmethod = CHAP\n' \
               'discovery.sendtargets.auth.authmethod = CHAP\n' \
               'discovery.sendtargets.auth.username_in = user1\n' \
               'discovery.sendtargets.auth.password_in = pass\n'
        open_mock = mock.mock_open(read_data=data)
        open_mock.return_value.readlines.return_value = data.split('\n')
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            auth_info = utils.get_iscsi_iqn_auth_info('test_iqn')[0]['auth']
            self.assertEquals(
                'CHAP', auth_info['node.session.auth.authmethod'])
            self.assertEquals(
                'CHAP', auth_info['discovery.sendtargets.auth.authmethod'])
            self.assertEquals('pass3', auth_info['node.session.auth.password'])
