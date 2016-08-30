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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301 USA

from wok.utils import run_command
from wok.exception import OperationFailed

audit_configpath = 'etc/audit/'
auditlog_file = '/var/log/audit/audit.log'
report_file = '/var/log/wok/audit_summary_report.txt'


class ReportsModel(object):
    def __init__(self, **kargs):
        pass

    def get_list(self, _filter=None):
        try:
            filter = str(_filter)
            report = []
            summary_cmd = ['aureport']
            if _filter is not None:
                options = filter.split(",")
                for item in options:
                    each_options = item.split(' ')
                    for each in each_options:
                        summary_cmd.append(each)
            out, error, rc = run_command(summary_cmd)
            with open("/var/log/wok/audit_summary_report.txt", "w")\
                    as report_file:
                report_file.write(out)
            out_list = out.split('\n')
            report_dict = dict()
            report_dict['summary'] = out_list
            report.append(report_dict)
            return report
        except Exception:
            raise OperationFailed('GINAUD0017E')
