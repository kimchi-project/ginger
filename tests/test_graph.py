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

from distutils.spawn import find_executable


from wok.exception import InvalidOperation, OperationFailed
from wok.plugins.ginger.model.graph import GraphsModel


class AuditTests(unittest.TestCase):

    @unittest.skipUnless(find_executable('/usr/bin/dot'), True)
    def test_get_list(self):
        filter = 'abc,2,4,svg'
        report = [{'Graph:': '/data/logs/abc.svg'}]
        graphmodel = GraphsModel()
        exp_out = graphmodel.get_list(filter)
        self.assertEquals(exp_out, report)

    @unittest.skipUnless(find_executable('/usr/bin/dot'), True)
    def test_get_list_failure(self):
        filter = 'abc,6,4,txt'
        report = [{'Graph:': '/var/log/wok/abc.svg'}]
        with self.assertRaisesRegexp(InvalidOperation, 'GINAUD0027E'):
            graphmodel = GraphsModel()
            exp_out = graphmodel.get_list(filter)
            self.assertNotEquals(exp_out, report)

    @unittest.skipUnless(find_executable('/usr/bin/dot'), True)
    def test_get_list_invalid_params(self):
        filter = 'abc,2,4'
        report = [{'Graph:': '/var/lib/wok/logs/abc.svg'}]
        with self.assertRaisesRegexp(OperationFailed, 'GINAUD0028E'):
            graphmodel = GraphsModel()
            exp_out = graphmodel.get_list(filter)
            self.assertNotEquals(exp_out, report)
