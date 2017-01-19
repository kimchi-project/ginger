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


DASDPARTITIONS_REQUESTS = {
    'POST': {
        'default': "GINDASDPAR0001L"
    },
}

DASDPARTITION_REQUESTS = {
    'DELETE': {'default': "GINDASDPAR0002L"},
}


@UrlSubNode('dasdpartitions', True)
class DASDPartitions(Collection):
    """
    Collections representing DASD Partitions on the system
    """
    def __init__(self, model):
        super(DASDPartitions, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = DASDPartition

        # set user log messages and make sure all parameters are present
        self.log_map = DASDPARTITIONS_REQUESTS
        self.log_args.update({'dev_name': '', 'size': ''})


class DASDPartition(Resource):
    """
    Resource representing a single DASD Partition
    """
    def __init__(self, model, ident):
        super(DASDPartition, self).__init__(model, ident)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/dasdpartitions/%s"
        self.log_map = DASDPARTITION_REQUESTS

    @property
    def data(self):
        return self.info
