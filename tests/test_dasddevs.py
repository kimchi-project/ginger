#
# Project Ginger
#
# Copyright IBM, Corp. 2015-2016
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

from wok.plugins.ginger.model.dasd_utils import _parse_lsdasd_output


class DASDdevsTests(unittest.TestCase):

    def test_lsdasd_parser(self):
        lsdasd_out = """0.0.5149/dasdgb/94:732
  status:       active
  type:         ECKD
  blksz:        4096
  size:         7043MB
  blocks:       1803060
  use_diag:     0
  readonly:     0
  eer_enabled:  0
  erplog:       0
  uid:          IBM.750000000DX111.0002.49

0.0.5150/dasdc/94:8
  status:       active
  type:         ECKD
  blksz:        4096
  size:         23034MB
  blocks:       5896800
  use_diag:     0
  readonly:     0
  eer_enabled:  0
  erplog:       0
  uid:          IBM.750000000DX111.0002.50"""
        parse_out = _parse_lsdasd_output(lsdasd_out)
        if parse_out[0]['status'] != 'active':
            self.fail("Parsing of lsdasd failed : status")
        if parse_out[0]['blocks'] != '1803060':
            self.fail("Parsing of lsdasd failed : blocks")
        if parse_out[0]['name'] != 'dasdgb':
            self.fail("Parsing of lsdasd failed : name")
        if parse_out[0]['uid'] != 'IBM.750000000DX111.0002.49':
            self.fail("Parsing of lsdasd failed : uid")
        if parse_out[0]['eer_enabled'] != '0':
            self.fail("Parsing of lsdasd failed : eer_enabled")
        if parse_out[0]['erplog'] != '0':
            self.fail("Parsing of lsdasd failed : erplog")
        if parse_out[0]['use_diag'] != '0':
            self.fail("Parsing of lsdasd failed : use_diag")
        if parse_out[0]['readonly'] != '0':
            self.fail("Parsing of lsdasd failed : readonly")
        if parse_out[0]['device'] != '94:732':
            self.fail("Parsing of lsdasd failed : device")
        if parse_out[0]['blksz'] != '4096':
            self.fail("Parsing of lsdasd failed : blksz")
        if parse_out[0]['bus-id'] != '0.0.5149':
            self.fail("Parsing of lsdasd failed : bus-id")
        if parse_out[0]['size'] != '7043MB':
            self.fail("Parsing of lsdasd failed : size")
