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

from wok.plugins.ginger.model.log import LogsModel


class LogsTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.log.LogsModel.get_unfiltered_log')
    def test_get_list_log_unfiltered(self, mock_log):
        """
        Unittest for list of unfiltered log.
        :param mock_log:
        :return:
        """
        log_list = "[{'record1': {'MSG': 'msg=audit(1469152069.499:1669): " \
                   "op=start ver=2.5.2 format=raw " \
                   "kernel=4.5.5-300.fc24.x86_64 auid=4294967295 " \
                   "pid=1020 subj=system_u:system_r:auditd_t:s0 " \
                   "res=success\n', 'TYPE': 'DAEMON_START'," \
                   " 'Date and Time': '2016-07-22 07:17:49'}}]"
        mock_log.return_value = log_list
        Logsmodel = LogsModel()
        out_log_list = Logsmodel.get_list()
        mock_log.assert_called_with()
        self.assertIn(log_list, out_log_list)

    @mock.patch('wok.plugins.ginger.model.log.LogsModel.get_filtered_log')
    def test_get_list_log_filtered(self, mock_log_filter):
        """
        Unittest for list of filtered log.
        :param mock_log_filter:
        :return:
        """
        filter = "ua 01000 C-as"
        log_list = """[{'record2': "type=USER_LOGIN msg=
                   audit(07/22/2016 07:17:58.940:286) :
                   pid=1650 uid=root auid=unset ses=unset
                   subj=system_u:system_r:xdm_t:s0-s0:c0.c1023
                   msg='uid=mesmriti exe=/usr/libexec/gdm-session-worker
                   hostname=? addr=? terminal=? res=failed' "}]"""
        mock_log_filter.return_value = log_list
        Logsmodel = LogsModel()
        out_log_list = Logsmodel.get_list(filter)
        mock_log_filter.assert_called_with(filter)
        self.assertIn(log_list, out_log_list)

    @mock.patch('wok.plugins.ginger.model.log.LogsModel.get_filtered_log')
    def test_get_list_invalid_filter(self, mock_log_filter):
        """
        Unittest for log with invalid filter.
        :param mock_log_filter:
        :return:
        """
        filter = "-asese"
        log_list = "[{'record1': ''}]"
        mock_log_filter.return_value = log_list
        Logsmodel = LogsModel()
        out_log_list = Logsmodel.get_list(filter)
        self.assertIn(log_list, out_log_list)
