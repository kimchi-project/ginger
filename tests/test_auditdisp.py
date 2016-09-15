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

from wok.plugins.ginger.model.utils import write_to_conf
from wok.plugins.ginger.model.auditdisp import AuditdispModel


class AuditdispTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.auditdisp.'
                'AuditdispModel.get_auditdisp_conf')
    def test_get_auditdisp_conf(self, mock_conf):
        """
        Unittest to get audit dispatcher conf
        """
        exp_out = {'overflow_action': 'SYSLOG',
                   'priority_boost': '4',
                   'q_depth': '150',
                   'max_restarts': '10',
                   'name_format': 'HOSTNAME'
                   }
        open_mock = mock.mock_open()
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            auditdisp = AuditdispModel()
            mock_conf.return_value = exp_out
            out = auditdisp.get_auditdisp_conf()
            self.assertEqual(out, exp_out)

    @mock.patch('wok.plugins.ginger.model.utils.'
                'write_to_conf')
    def test_write_to_conf(self, mock_write):
        """
        Unit test to write data to audisp conf file.
        """
        data = 'q_depth = 150\n' \
               'overflow_action = SYSLOG\n' \
               'priority_boost = 4\n' \
               'max_restarts = 10\n' \
               'name_format = HOSTNAME\n' \
               '#name = mydomain\n'
        AUDISPD_CONF = '/etc/audisp/abc'
        key = "dummy"
        value = "23"
        open_mock = mock.mock_open(read_data=data)
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            mock_write.return_value = {}
            write_to_conf(key, value, AUDISPD_CONF)

    @mock.patch('wok.plugins.ginger.model.'
                'utils.del_lines_of_attribute')
    @mock.patch('wok.plugins.ginger.model.'
                'utils.write_to_conf')
    def test_update(self, mock_write, mock_del):
        """
        Unit test to update data to audisp conf file.
        """
        params = {"priority_boost": "34",
                  "q_depth": "13"}
        name = "audit"
        mock_del.return_value = {}
        mock_write.return_value = {}
        auditdisp = AuditdispModel()
        auditdisp.update(name, params)
