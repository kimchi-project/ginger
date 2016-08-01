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


import unittest
import wok.plugins.ginger.model.utils as utils


class ISCSITargetsUnitTests(unittest.TestCase):
    """
    Unit tests for iSCSI targets
    """

    def test_iscsi_discovery(self):
        discover_output = """9.193.84.125:3260,1 iqn.2015-06.com.example.test:target1
9.193.84.125:3260,1 iqn.2015-06.com.example.test:target2"""
        parsed_output = utils.parse_iscsi_discovery(discover_output)
        sample_output = parsed_output[0]
        self.assertEqual(
            sample_output['iqn'],
            "iqn.2015-06.com.example.test:target1")
        self.assertEqual(sample_output['target_ipaddress'], "9.193.84.125")
        self.assertEqual(sample_output['target_port'], "3260")
