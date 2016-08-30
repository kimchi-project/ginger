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

import platform
import re


class SyscallModel(object):
    def __init__(self, **kargs):
        pass

    def lookup(self, name):
        return self.get_syscalls_list()

    def get_syscalls_list(self):
        rules_record = {}
        if platform.machine() == 's390x':
            syscalls_file = '/usr/include/asm/unistd.h'
        else:
            syscalls_file = '/usr/include/asm/unistd_64.h'
        with open(syscalls_file, "r") as syscalls_file:
            syscalls_list = []
            for each_line in syscalls_file:
                regex = re.search(r'\S\w+\s+(__NR\S)(\w+) ', each_line)
                if regex is not None:
                    syscalls_list.append(regex.group(2))
        rules_record["syscalls"] = syscalls_list
        return rules_record
