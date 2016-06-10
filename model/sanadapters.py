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

import os


from wok.exception import NotFoundError


FC_HOST_SYS_PATH = '/sys/class/fc_host/%s'

FC_HOST_INFOS = {'wwpn': '/port_name',
                 'wwnn': '/node_name',
                 'max_vports': '/max_npiv_vports',
                 'vports_inuse': '/npiv_vports_inuse',
                 'state': '/port_state',
                 'speed': '/speed',
                 'symbolic_name': '/symbolic_name'}

FC_VIRTUAL_INFOS = {'wwpn': '/port_name',
                    'wwnn': '/node_name',
                    'state': '/port_state',
                    'speed': '/speed',
                    'symbolic_name': '/symbolic_name'}


def get_port_type(name):
    fc_path = FC_HOST_SYS_PATH % name

    if not os.path.isdir(fc_path):
        raise NotFoundError('GINADAP0001E', {'adapter': name})

    max_vports_file = os.path.join(fc_path, 'max_npiv_vports')
    vports_inuse_file = os.path.join(fc_path, 'npiv_vports_inuse')
    if os.path.isfile(max_vports_file) and os.path.isfile(vports_inuse_file):
        return 'physical'

    return 'virtual'


class SanAdaptersModel(object):

    def get_list(self):
        try:
            return os.listdir(FC_HOST_SYS_PATH % '')
        except:
            return []


class SanAdapterModel(object):

    def _read_info(self, fpath):
        try:
            with open(fpath) as f:
                return f.read().strip()
        except:
            return 'Unknown'

    def lookup(self, name):
        if not os.path.isdir(FC_HOST_SYS_PATH % name):
            raise NotFoundError('GINADAP0001E', {'adapter': name})

        info = {}
        info['port_type'] = get_port_type(name)
        fc_host_keys = FC_HOST_INFOS

        if info['port_type'] == 'virtual':
            fc_host_keys = FC_VIRTUAL_INFOS
            info['max_vports'] = 'Not applicable'
            info['vports_inuse'] = 'Not applicable'

        for key in fc_host_keys:
            info[key] = self._read_info(FC_HOST_SYS_PATH % name +
                                        fc_host_keys[key])
        return info
