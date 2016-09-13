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

from distutils.spawn import find_executable

from wok.exception import InvalidOperation
from wok.config import get_log_download_path
from wok.utils import run_command

DOT_CMD = "/usr/bin/dot"


def create_graph(out, graph_name, extension):
    if not find_executable(DOT_CMD):
        raise InvalidOperation('GINAUD0030E')
    DOT_FILE = "/var/log/wok/%s.dot" % graph_name
    f = open(DOT_FILE, 'w')
    f.write('digraph G {\n')
    str_out = out[0]
    out_list = str_out.split('\n')
    for each in out_list:
        each_list = each.split(' ')
        if len(each_list) == 2:
            f.write('\t' + '"' + each_list[0] + '"' + ' -> ' + '"' +
                    each_list[1] + '"' + ';\n')
    f.write('}')
    f.close()
    dot_format = "-T" + extension
    graph_file = \
        os.path.join(get_log_download_path(), graph_name + '.' + extension)
    cmd = [DOT_CMD, dot_format, '-o', graph_file, DOT_FILE]
    output, error, rc = run_command(cmd)
    if rc:
        raise InvalidOperation('GINAUD0027E')
    os.remove(DOT_FILE)
