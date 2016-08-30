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

from wok.plugins.ginger.model.report import ReportsModel


class ReportTests(unittest.TestCase):

    @mock.patch('wok.plugins.ginger.model.report.run_command')
    def test_get_report_without_filter(self, mock_runcmd):
        """
        Unittest for list of unfiltered report.
         :param mock_runcmd:
         :return:
        """
        out_cmd = """Summary Report
                ======================
                Range of time in logs: 07/22/2016 07:17:49.499 -
                08/09/2016 15:17:20.488
                Selected time for report: 07/22/2016 07:17:49 -
                08/09/2016 15:17:20.488
                Number of changes in configuration: 3297
                Number of changes to accounts, groups, or roles: 99
                Number of logins: 6
                Number of failed logins: 173
                Number of authentications: 417
                Number of failed authentications: 225
                Number of users: 3
                Number of terminals: 16
                Number of host names: 1
                Number of executables: 17
                Number of commands: 15
                Number of files: 580
                Number of AVC's: 2842
                Number of MAC events: 17
                Number of failed syscalls: 0
                Number of anomaly events: 20
                Number of responses to anomaly events: 0
                Number of crypto events: 0
                Number of integrity events: 0
                Number of virt events: 0
                Number of keys: 8
                Number of process IDs: 978
                Number of events: 9836
                """
        cmd = ['aureport']
        mock_runcmd.return_value = [out_cmd, '', 0]
        Reportmodel = ReportsModel()
        Reportmodel.get_list()
        mock_runcmd.assert_called_once_with(cmd)

    @mock.patch('wok.plugins.ginger.model.report.run_command')
    def test_get_report_with_filter(self, mock_runcmd):
        """
        Unittest for list of filtered report.
        :param mock_runcmd:
        :return:
        """
        filter = "--start 04/08/2016 00:00:00 --end 04/11/2016 00:00:00"
        out_runcmd = """

Summary Report
======================
Range of time in logs: 01/01/1970 05:30:00.000 - 01/01/1970 05:30:00.000
Selected time for report: 04/08/2016 00:00:00 - 04/11/2016 00:00:00
Number of changes in configuration: 0
Number of changes to accounts, groups, or roles: 0
Number of logins: 0
Number of failed logins: 0
Number of authentications: 0
Number of failed authentications: 0
Number of users: 0
Number of terminals: 0
Number of host names: 0
Number of executables: 0
Number of commands: 0
Number of files: 0
Number of AVC's: 0
Number of MAC events: 0
Number of failed syscalls: 0
Number of anomaly events: 0
Number of responses to anomaly events: 0
Number of crypto events: 0
Number of integrity events: 0
Number of virt events: 0
Number of keys: 0
Number of process IDs: 0
Number of events: 0

        """
        cmd = ['aureport', '--start', '04/08/2016', '00:00:00', '--end',
               '04/11/2016', '00:00:00']
        mock_runcmd.return_value = [out_runcmd, '', 0]
        Reportmodel = ReportsModel()
        Reportmodel.get_list(filter)
        mock_runcmd.assert_called_once_with(cmd)
