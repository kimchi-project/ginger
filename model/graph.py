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

import subprocess

mkgraph = '/usr/lib/python2.7/site-packages/wok/plugins/ginger/mkgraph.sh'


class GraphsModel(object):
    def __init__(self, **kargs):
        pass

    def get_list(self, _filter):
        filter = str(_filter)
        params = filter.split(',')
        report = []
        cmd = "cat /var/log/wok/audit_summary_report.txt | awk '/^[0-9]/ { " \
              "printf \"%s %s\\n\", $" + params[1] + ", $" + params[2] + \
              "}'| sort | uniq | " \
              "/usr/lib/python2.7" \
              "/site-packages/wok/plugins/ginger/mkgraph.sh " + params[0]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, shell=True)
        out = p.communicate()
        str(out).split('\n')
        report_dict = dict()
        report_dict['Graph:'] = "/var/log/wok/" + params[0] + ".svg"
        report.append(report_dict)
        return report
