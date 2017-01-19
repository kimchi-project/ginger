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
from wok.control.utils import UrlSubNode


FILESYSTEMS_REQUESTS = {
    'POST': {'default': "GINFS0001L"},
}

FILESYSTEM_REQUESTS = {
    'DELETE': {'default': "GINFS0002L"},
}


@UrlSubNode('filesystems', True)
class FileSystems(Collection):
    """
    Collections representing the filesystems on the system
    """
    def __init__(self, model):
        super(FileSystems, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = FileSystem

        # set user log messages and make sure all parameters are present
        self.log_map = FILESYSTEMS_REQUESTS
        self.log_args.update({'type': '', 'mountpoint': ''})

    def _get_resources(self, flag_filter):
        res_list = super(FileSystems, self)._get_resources(flag_filter)
        res_list = filter(lambda x: 'tmpfs' not in x.info['type'],
                          res_list)
        return res_list


class FileSystem(Resource):
    """
    Resource representing a single file system
    """
    def __init__(self, model, ident):
        super(FileSystem, self).__init__(model, ident)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/filesystems/%s"
        self.log_map = FILESYSTEM_REQUESTS

    @property
    def data(self):
        return {'filesystem': self.info['filesystem'],
                'type': self.info['type'],
                'size': self.info['size'],
                'used': self.info['used'],
                'avail': self.info['avail'],
                'use%': self.info['use%'],
                'mounted_on': self.info['mounted_on']}
