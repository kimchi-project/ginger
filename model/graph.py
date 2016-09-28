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

import os
import subprocess

from mkgraph import create_graph, DOT_CMD
from wok.config import get_log_download_path
from wok.exception import OperationFailed, InvalidParameter, InvalidOperation

audit_summary_report = \
    "%s/audit_summary_report.txt" % get_log_download_path()


class GraphsModel(object):
    def __init__(self, **kargs):
        pass

    @staticmethod
    def is_feature_available():
        return os.path.exists(DOT_CMD)

    def get_list(self, _filter):
        try:
            filter = str(_filter)
            params = filter.split(',')
            if len(params) != 4:
                raise InvalidParameter('GINAUD0029E')
            report = []
            cmd = "cat " + audit_summary_report + " |" \
                  " awk '/^[0-9]/ { " \
                  "printf \"%s %s\\n\", $" + params[1] + ", $" + params[2] + \
                  "}'| sort | uniq"
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, shell=True)
            out = p.communicate()
            str(out).split('\n')
            create_graph(out, params[0], params[3])
            report_dict = dict()
            report_dict['Graph:'] = "/data/logs/" + params[0] + "." + \
                                    params[3]
            report.append(report_dict)
            return report
        except InvalidOperation:
            raise
        except Exception, e:
            raise OperationFailed('GINAUD0028E', {'error': e.message})
