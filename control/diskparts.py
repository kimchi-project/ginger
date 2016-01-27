#
# Project Ginger
#
# Copyright IBM, Corp. 2015-2016
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

from wok.control.base import Collection, Resource
from wok.control.utils import UrlSubNode


@UrlSubNode('partitions', True)
class Partitions(Collection):
    """
    Collection representing the partitions/disks of the system
    """
    def __init__(self, model):
        super(Partitions, self).__init__(model)
        self.role_key = 'storage'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = Partition

    # Defining get_resources in order to return list of
    # partitions/disks without mpath_member
    def _get_resources(self, flag_filter):
        res_list = super(Partitions, self)._get_resources(flag_filter)
        res_list = filter(lambda x: x.info['fstype'] != 'mpath_member',
                          res_list)
        return res_list


class Partition(Resource):
    """
    Resource representing a single partition/disk
    """
    def __init__(self, model, id):
        self.role_key = 'storage'
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = '/partitions/%s'
        self.format = self.generate_action_handler_task('format', ['fstype'])
        self.change_type = self.generate_action_handler('change_type',
                                                        ['type'])
        super(Partition, self).__init__(model, id)

    @property
    def data(self):
        return {'name': self.info['name'],
                'fstype': self.info['fstype'],
                'path': self.info['path'],
                'mountpoint': self.info['mountpoint'],
                'type': self.info['type'],
                'size': self.info['size']}
