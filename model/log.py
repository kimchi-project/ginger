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

import datetime
import re

from wok.utils import run_command
from wok.exception import OperationFailed

audit_configpath = 'etc/audit/'
auditlog_file = '/var/log/audit/audit.log'


class LogsModel(object):
    def __init__(self, **kargs):
        pass

    def get_list(self, _filter=None):
        try:
            if _filter is None:
                return self.get_unfiltered_log()
            else:
                return self.get_filtered_log(str(_filter))
        except Exception:
            raise OperationFailed('GINAUD0016E')

    def get_filtered_log(self, filter):
        try:
            log_list = []
            search_cmd = ['ausearch']
            options = filter.split(",")
            for item in options:
                each_options = item.split(' ')
                for each in each_options:
                    search_cmd.append(each)
            output, error, rc = run_command(search_cmd)
            if "time->" in output:
                i = 1
                out_list = output.split('----')
                for each in out_list:
                    record_details = dict()
                    record = 'record' + str(i)
                    record_details[record] = each.strip('\n')
                    record_details[record] = {}
                    each = each.split('\n')
                    if each != ['']:
                        each_line = each[2]
                        regex = re.search(r'\w+\S(\w+)\s+\w+\S((\S*\s*)*)',
                                          each_line)
                        time_regex = re.search(
                            r'\w+\S\w+\s+\w+\S\w+\S(\d+\S\d+)((\S+\s*)*)',
                            each_line)
                        timestamp = time_regex.groups()[0]
                        timestamp = float(timestamp)
                        record_details[record]['TYPE'] = regex.groups()[0]
                        record_details[record]['MSG'] = regex.groups()[1]
                        record_details[record]['Date and Time'] = \
                            datetime.datetime.fromtimestamp(
                                timestamp).strftime('%Y-%m-%d %H:%M:%S')
                        i += 1
                        log_list.append(record_details)
            else:
                out_list = output.split('----')
                i = 1
                for each_line in out_list:
                    record_details = dict()
                    record = 'record' + str(i)
                    record_details[record] = each_line.strip('\n')
                    record_details[record] = {}
                    if each_line != "":
                        regex = re.search(r'\w+\S(\w+)\s+((\w+\S+\s*)*\S'
                                          r'(\s\S+)*)',
                                          each_line)
                        time_regex = re.search(r'\w+\S\w+\s+\w+\S\w+\S'
                                               r'(\d+\S\d+\S\d+'
                                               r'\s+\d+\S\d+\S\d+)',
                                               each_line)
                        record_details[record]['TYPE'] = regex.groups()[0]
                        record_details[record]['MSG'] = regex.groups()[1]
                        record_details[record]['Date and Time'] = \
                            time_regex.groups()[0]
                        i += 1
                        log_list.append(record_details)
            return log_list
        except Exception:
            raise OperationFailed('GINAUD0014E')

    def get_unfiltered_log(self):
        try:
            with open(auditlog_file, "r") as log_file:
                log_list = []
                i = 1
                for each_line in log_file:
                    record_details = dict()
                    record = 'record' + str(i)
                    record_details[record] = {}
                    i += 1
                    regex = re.search(r'\w+\S(\w+)\s+((\w+\S+\s*)*)',
                                      each_line)
                    time_regex = re.search(
                        r'\w+\S\w+\s+\w+\S\w+\S(\d+\S\d+)((\S+\s*)*)',
                        each_line)
                    timestamp = time_regex.groups()[0]
                    timestamp = float(timestamp)
                    record_details[record]['TYPE'] = regex.groups()[0]
                    record_details[record]['MSG'] = regex.groups()[1]
                    record_details[record]['Date and Time'] = \
                        datetime.datetime.fromtimestamp(
                            timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    log_list.append(record_details)
                return log_list
        except Exception:
            raise OperationFailed('GINAUD0015E')
