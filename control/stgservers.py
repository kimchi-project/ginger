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

from wok.control.base import Collection, Resource, SimpleCollection
from wok.control.utils import UrlSubNode


@UrlSubNode('stgserver', True)
class StgServers(Collection):
    def __init__(self, model):
        super(StgServers, self).__init__(model)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.resource = StgServer


class StgServer(Resource):
    def __init__(self, model, ident):
        super(StgServer, self).__init__(model, ident)
        self.admin_methods = ['GET', 'POST', 'DELETE']
        self.uri_fmt = "/stgserver/%s"
        self.nfsshares = NFSShares(self.model, ident)
        self.iscsitargets = ISCSITargets(self.model, ident)

    @property
    def data(self):
        return self.info


class ISCSITargets(SimpleCollection):

    def __init__(self, model, server):
        super(ISCSITargets, self).__init__(model)
        self.admin_methods = ['GET']
        self.server = server
        self.resource_args = [self.server, ]
        self.model_args = [self.server, ]


class NFSShares(SimpleCollection):
    def __init__(self, model, server):
        super(NFSShares, self).__init__(model)
        self.admin_methods = ['GET']
        self.server = server
        self.resource_args = [self.server, ]
        self.model_args = [self.server, ]
