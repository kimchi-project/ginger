#
# Project Ginger
#
# Copyright IBM Corp, 2016-2017
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
from wok.control.utils import model_fn, UrlSubNode


PARTITIONS_REQUESTS = {
    'POST': {
        'default': "GINPART0001L"
    },
}

PARTITION_REQUESTS = {
    'DELETE': {'default': "GINPART0002L"},
    'POST': {
        'change_type': "GINPART0003L",
        'format': "GINPART0004L",
    },
}


@UrlSubNode('partitions', True)
class Partitions(Collection):
    """
    Collection representing the partitions/disks of the system
    """

    def __init__(self, model):
        super(Partitions, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = Partition

        # set user log messages and make sure all parameters are present
        self.log_map = PARTITIONS_REQUESTS
        self.log_args.update({'devname': '', 'partsize': ''})

    def _get_resources(self, flag_filter):
        """
        Overriden this method, here get_list should return list dict
        which will be set to the resource, this way we avoid calling lookup
        again for each device.
        :param flag_filter:
        :return: list of resources.
        """
        try:
            get_list = getattr(self.model, model_fn(self, 'get_list'))
            idents = get_list(*self.model_args, **flag_filter)
            res_list = []
            for ident in idents:
                # internal text, get_list changes ident to unicode for sorted
                args = self.resource_args + [ident]
                res = self.resource(self.model, *args)
                res.info = ident
                # Excluding devices with mpath_member
                if res.info['fstype'] == 'mpath_member':
                    continue
                else:
                    res_list.append(res)
            return res_list
        except AttributeError:
            return []


class Partition(Resource):
    """
    Resource representing a single partition/disk
    """

    def __init__(self, model, id):
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = '/partitions/%s'
        self.format = self.generate_action_handler_task('format', ['fstype'])
        self.change_type = self.generate_action_handler('change_type',
                                                        ['type'])
        super(Partition, self).__init__(model, id)

        # set user log messages and make sure all parameters are present
        self.log_map = PARTITION_REQUESTS
        self.log_args.update({'type': '', 'fstype': ''})

    @property
    def data(self):
        return {
            'available': str(
                self.info['available']),
            'maj:min': self.info['maj:min'],
            'vgname': self.info['vgname'],
            'name': self.info['name'],
            'pkname': self.info['pkname'],
            'fstype': self.info['fstype'],
            'path': self.info['path'],
            'mountpoint': self.info['mountpoint'] if
            self.info['mountpoint'] else "None",
            'type': self.info['type'],
            'size': self.info['size']}
