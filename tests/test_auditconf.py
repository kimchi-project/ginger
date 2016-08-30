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

from wok.plugins.ginger.model.conf import ConfModel


class ConfTests(unittest.TestCase):

    def test_get_list_of_audit_conf(self):
        data = 'admin_space_left_action = SUSPEND\n' \
               'krb5_principal = auditd\n' \
               'write_logs = yes\n' \
               'disk_full_action = SUSPEND\n' \
               'flush = INCREMENTAL_ASYNC\n' \
               'space_left = 75\n' \
               'max_log_file = 8\n' \
               'disp_qos = lossy\n' \
               'name_format = NONE\n' \
               'tcp_max_per_addr = 1\n' \
               'max_log_file_action = ROTATE\n' \
               'local_events = yes\n' \
               'action_mail_acct = root\n' \
               'admin_space_left = 50\n' \
               'log_group = root\n' \
               'tcp_listen_queue = 5\n' \
               'freq = 50\n' \
               'disk_error_action = SUSPEND\n' \
               'dispatcher = /sbin/audispd\n' \
               'space_left_action = SYSLOG\n' \
               'enable_krb5 = no\n' \
               'priority_boost = 4\n' \
               'tcp_client_max_idle = 0\n' \
               'num_logs = 10\n' \
               'log_format = RAW\n' \
               'log_file = /var/log/audit/audit.log\n' \
               'distribute_network = no\n'
        open_mock = mock.mock_open(read_data=data)
        with mock.patch('wok.plugins.ginger.model.utils.open',
                        open_mock, create=True):
            confmodel = ConfModel()
            confmodel.get_auditd_conf()

    @mock.patch('wok.plugins.ginger.model.conf.'
                'ConfModel.del_lines_of_attribute')
    @mock.patch('wok.plugins.ginger.model.conf.ConfModel.write_to_conf')
    def test_update(self, mock_del, mock_write):
        params = {
                    "admin_space_left_action": "SUSPEND",
                    "krb5_principal": "auditd",
                    "write_logs": "yes",
                    "disk_full_action": "SUSPEND",
                    "flush": "INCREMENTAL_ASYNC",
                    "max_log_file_action": "ROTATE",
                    "freq": "50",
                    "admin_space_left": "50",
                    "name_format": "NONE",
                    "tcp_max_per_addr": "1",
                    "space_left": "75",
                    "local_events": "yes",
                    "action_mail_acct": "root",
                    "disp_qos": "lossy",
                    "log_group": "root",
                    "tcp_listen_queue": "5",
                    "max_log_file": "8",
                    "disk_error_action": "SUSPEND",
                    "dispatcher": "/sbin/audispd",
                    "space_left_action": "SYSLOG",
                    "enable_krb5": "no",
                    "priority_boost": "4",
                    "tcp_client_max_idle": "0",
                    "num_logs": "10",
                    "log_format": "RAW",
                    "log_file": "/var/log/audit/audit.log",
                    "distribute_network": "no"
                }
        name = 'update'
        mock_del.return_value = {}
        mock_write.return_value = {}
        confModel = ConfModel()
        confModel.update(name, params)
